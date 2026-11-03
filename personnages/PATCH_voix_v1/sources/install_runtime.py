"""Install the recorded R/Soundgen toolchain inside the workspace (Debian13 x86_64).
No sudo, no package-manager database changes, no model weights or paid service.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,tarfile,urllib.request
BANK=Path(__file__).resolve().parents[1]
ROOT=BANK.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fetch(url,path,expected):
 path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists() or sha(path)!=expected:urllib.request.urlretrieve(url,path)
 if sha(path)!=expected:raise ValueError('Download checksum mismatch: '+path.name)
def install(runtime):
 runtime=Path(runtime).resolve();prefix=runtime/'root';src=runtime/'src';rlib=runtime/'rlib'
 for p in [prefix,src,rlib]:p.mkdir(parents=True,exist_ok=True)
 data=json.loads((BANK/'controle/runtime_packages.json').read_text())
 for name,info in data.items():
  target=runtime/'debs'/(name+'.deb');fetch(info['url'],target,info['sha256'])
  subprocess.run(['dpkg-deb','-x',str(target),str(prefix)],check=True)
 rh=prefix/'usr/lib/R'
 for p in (rh/'etc').iterdir():
  if p.is_symlink():
   dest=prefix/str(p.readlink()).lstrip('/');p.unlink()
   if dest.exists():shutil.copy2(dest,p)
   elif p.name=='Renviron':shutil.copy2(rh/'etc/Renviron.ucf',p)
 wrapper=rh/'bin/R';text=wrapper.read_text().replace('R_HOME_DIR=/usr/lib/R','R_HOME_DIR='+str(rh))
 for var,suffix in [('R_SHARE_DIR','share'),('R_INCLUDE_DIR','include'),('R_DOC_DIR','doc')]:
  text=text.replace(var+'=/usr/share/R/'+suffix,var+'='+str(prefix/'usr/share/R'/suffix))
 wrapper.write_text(text)
 fc=prefix/'usr/bin/gfortran'
 if not fc.exists():fc.symlink_to('gfortran-14')
 conf=rh/'etc/Makeconf';text=conf.read_text().replace('FC = gfortran','FC = '+str(fc)).replace('FLIBS =  -lgfortran -lm -lquadmath','FLIBS = -L'+str(prefix/'usr/lib/gcc/x86_64-linux-gnu/14')+' -lgfortran -lm -lquadmath');conf.write_text(text)
 for name in ['libgfortran.so.5','libquadmath.so.0']:
  p=prefix/'usr/lib/x86_64-linux-gnu'/name;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.symlink_to(Path('/usr/lib/x86_64-linux-gnu')/name)
 env=os.environ.copy();env['R_LIBS_USER']=str(rlib);env['R_HOME']=str(rh)
 env['LD_LIBRARY_PATH']=str(rh/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
 packages=json.loads((BANK/'controle/source_packages.json').read_text())
 for name in ['signal','tuneR','phonTools','soundgen']:
  meta=packages[name];target=src/(name+'-pinned.tar.gz');fetch(meta['source_url'],target,meta['pinned_archive_sha256'])
  with tarfile.open(target) as archive:archive.extractall(src,filter='data')
  package=src/(name+'-'+meta['commit'])
  subprocess.run([str(wrapper),'CMD','INSTALL','--no-docs','--no-html','--no-help','--library='+str(rlib),str(package)],env=env,check=True)
 proof=subprocess.run([str(wrapper),'--vanilla','--slave','-e','library(soundgen); cat(R.version.string,"\\n"); cat(as.character(packageVersion("soundgen")),"\\n")'],env=env,check=True,capture_output=True,text=True)
 (runtime/'installation.txt').write_text(proof.stdout+proof.stderr)
 print(proof.stdout)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,default=ROOT/'work/voix_soundgen_runtime');install(p.parse_args().runtime)
