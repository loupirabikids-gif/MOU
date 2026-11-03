"""Execute the recorded local Soundgen/R backend; optionally package the bank."""
from pathlib import Path
import argparse,json,os,subprocess,hashlib,sys
BANK=Path(__file__).resolve().parents[1]
ROOT=BANK.parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,default=ROOT/'work/voix_soundgen_runtime');p.add_argument('--raw-only',action='store_true');a=p.parse_args()
 runtime=a.runtime.resolve();rh=runtime/'root/usr/lib/R';out=ROOT/'work/voix_squeaky/generated';out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['R_HOME']=str(rh);env['R_LIBS_USER']=str(runtime/'rlib');env['LD_LIBRARY_PATH']=str(rh/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
 command=[str(rh/'bin/R'),'--vanilla','--slave','-f',str(BANK/'sources/generate.R'),'--args',str(out)]
 r=subprocess.run(command,env=env,check=True,text=True,capture_output=True)
 (ROOT/'work/voix_squeaky/generation.log').write_text(r.stdout+r.stderr)
 if not a.raw_only:subprocess.run([sys.executable,str(BANK/'sources/finish_bank.py'),str(out)],check=True)
 print('Soundgen generated12raw takes:',out)
if __name__=='__main__':main()
