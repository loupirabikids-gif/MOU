"""Independent V26 verification entry point; run only after final sources freeze."""
from pathlib import Path
import importlib.util
import sys
EP=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mou_v26_final_verifier',EP/'sources/verify.py')
verify=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=verify
spec.loader.exec_module(verify)
if __name__=='__main__':verify.main(EP/'controle/audit_revision_v26.json')
