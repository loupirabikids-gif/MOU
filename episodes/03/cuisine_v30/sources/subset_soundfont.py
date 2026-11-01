"""Create a small, reproducible FluidR3 nylon-guitar and acoustic-bass subset from the official SF2.

The sample data and loops are copied intact. Instrument zones outside the
documented score ranges are omitted; retained SF2 tables are fully reindexed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

PRESETS={(0,24):set(range(48,78)),(0,32):set(range(33,58))}
FMT={'phdr':'<20sHHHIII','pbag':'<HH','pmod':'<HHhHH','pgen':'<HH',
     'inst':'<20sH','ibag':'<HH','imod':'<HHhHH','igen':'<HH','shdr':'<20sIIIIIBbHH'}


def chunks(data,start=0):
    result=[];position=start
    while position+8<=len(data):
        kind=data[position:position+4];size=struct.unpack_from('<I',data,position+4)[0]
        assert position+8+size<=len(data)
        result.append((kind,data[position+8:position+8+size]));position+=8+size+(size%2)
    return result


def chunk(kind,data):
    return kind+struct.pack('<I',len(data))+data+(b'\0' if len(data)%2 else b'')


def pack_table(name,rows):return b''.join(struct.pack(FMT[name],*row) for row in rows)


def build(source,destination):
    raw=source.read_bytes();assert raw[:4]==b'RIFF' and raw[8:12]==b'sfbk'
    groups={d[:4]:dict(chunks(d,4)) for k,d in chunks(raw,12) if k==b'LIST'}
    tables={name:list(struct.iter_unpack(fmt,groups[b'pdta'][name.encode()])) for name,fmt in FMT.items()}
    ph,pb,pg,pm=(tables[x] for x in ('phdr','pbag','pgen','pmod'))
    inst,ib,ig,im,sh=(tables[x] for x in ('inst','ibag','igen','imod','shdr'))
    selected=[i for i,r in enumerate(ph[:-1]) if (r[2],r[1]) in PRESETS]
    assert len(selected)==len(PRESETS)
    notes_by_instrument={}
    for i in selected:
        notes=PRESETS[(ph[i][2],ph[i][1])]
        for bag in range(ph[i][3],ph[i+1][3]):
            for op,value in pg[pb[bag][0]:pb[bag+1][0]]:
                if op==41:notes_by_instrument.setdefault(value,set()).update(notes)
    zones_by_instrument={};sampleids=set()
    for index,notes in notes_by_instrument.items():
        zones=[];has_sample=False
        for bag in range(inst[index][1],inst[index+1][1]):
            generators=ig[ib[bag][0]:ib[bag+1][0]]
            keys=next(((v&255,v>>8) for op,v in generators if op==43),(0,127))
            samples=[v for op,v in generators if op==53]
            if not samples or any(keys[0]<=n<=keys[1] for n in notes):
                zones.append(bag);sampleids.update(samples);has_sample|=bool(samples)
        if has_sample:zones_by_instrument[index]=zones
    # Stereo samples must retain their linked counterpart even when a zone
    # directly references only one side.
    todo=list(sampleids)
    while todo:
        i=todo.pop();link=sh[i][8];kind=sh[i][9]&32767
        if kind in (2,4,8) and link not in sampleids:
            sampleids.add(link);todo.append(link)
    instrument_map={old:new for new,old in enumerate(sorted(zones_by_instrument))}
    sample_map={old:new for new,old in enumerate(sorted(sampleids))}
    new_sh=[];sample_data=bytearray();sample_metadata=[]
    for old,new in sample_map.items():
        name,start,end,loop_start,loop_end,rate,pitch,correction,link,kind=sh[old]
        assert 0<=start<end<=len(groups[b'sdta'][b'smpl'])//2
        new_start=len(sample_data)//2;length=end-start
        sample_data.extend(groups[b'sdta'][b'smpl'][start*2:end*2]);sample_data.extend(b'\0'*92)
        new_sh.append((name,new_start,new_start+length,new_start+loop_start-start,
                       new_start+loop_end-start,rate,pitch,correction,
                       sample_map.get(link,0) if (kind&32767) in (2,4,8) else 0,kind))
        sample_metadata.append({'name':name.rstrip(b'\0').decode(errors='replace'),'frames':length,'sample_rate':rate})
    terminal=len(sample_data)//2
    new_sh.append((b'EOS',terminal,terminal,terminal,terminal,0,0,0,0,1))
    new_inst=[];new_ib=[];new_ig=[];new_im=[]
    for old in instrument_map:
        new_inst.append((inst[old][0],len(new_ib)))
        for bag in zones_by_instrument[old]:
            new_ib.append((len(new_ig),len(new_im)))
            new_ig.extend((op,sample_map[v] if op==53 else v) for op,v in ig[ib[bag][0]:ib[bag+1][0]])
            new_im.extend(im[ib[bag][1]:ib[bag+1][1]])
    new_inst.append((b'EOI',len(new_ib)));new_ib.append((len(new_ig),len(new_im)))
    new_ig.append((0,0));new_im.append((0,0,0,0,0))
    new_ph=[];new_pb=[];new_pg=[];new_pm=[];preset_metadata=[]
    for old in selected:
        name,program,bank,first,library,genre,morphology=ph[old]
        new_ph.append((name,program,bank,len(new_pb),library,genre,morphology))
        kept=0
        for bag in range(first,ph[old+1][3]):
            gens=pg[pb[bag][0]:pb[bag+1][0]]
            indices=[v for op,v in gens if op==41]
            if indices and indices[0] not in instrument_map:continue
            new_pb.append((len(new_pg),len(new_pm)));kept+=1
            new_pg.extend((op,instrument_map[v] if op==41 else v) for op,v in gens)
            new_pm.extend(pm[pb[bag][1]:pb[bag+1][1]])
        preset_metadata.append({'name':name.rstrip(b'\0').decode(),'bank':bank,'program':program,'preset_zones':kept,'notes':sorted(PRESETS[(bank,program)])})
    new_ph.append((b'EOP',0,0,len(new_pb),0,0,0));new_pb.append((len(new_pg),len(new_pm)))
    new_pg.append((0,0));new_pm.append((0,0,0,0,0))
    new_tables=dict(phdr=new_ph,pbag=new_pb,pmod=new_pm,pgen=new_pg,inst=new_inst,
                    ibag=new_ib,imod=new_im,igen=new_ig,shdr=new_sh)
    info=dict(groups[b'INFO']);info[b'INAM']=b'MOU Bossa - FluidR3 subset\0\0'
    payload=b'sfbk'+chunk(b'LIST',b'INFO'+b''.join(chunk(k,v) for k,v in info.items()))
    payload+=chunk(b'LIST',b'sdta'+chunk(b'smpl',bytes(sample_data)))
    payload+=chunk(b'LIST',b'pdta'+b''.join(chunk(name.encode(),pack_table(name,new_tables[name])) for name in FMT))
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(chunk(b'RIFF',payload))
    result={'source_sha256':hashlib.sha256(raw).hexdigest(),'subset_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'bank_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'source_bytes':len(raw),'subset_bytes':destination.stat().st_size,'presets':preset_metadata,
            'instrument_count':len(instrument_map),'sample_count':len(sample_map),'sample_frames':len(sample_data)//2,
            'method':'Original PCM and sample loops copied intact; zone key ranges filtered to documented score notes, stereo sample links and all bags/generators/modulators reindexed.',
            'samples':sample_metadata}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('destination',type=Path);args=parser.parse_args()
    result=build(args.source,args.destination)
    report=args.destination.with_suffix('.json');report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},ensure_ascii=False))


if __name__=='__main__':main()
