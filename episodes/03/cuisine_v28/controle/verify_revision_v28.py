"""V28 independent final-verification entry point."""
from pathlib import Path
import importlib.util
import sys
EP=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mou_v28_independent_verifier',EP/'sources/verify.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
if __name__=='__main__':m.main(EP/'controle/audit_revision_v28.json')
