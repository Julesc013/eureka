from __future__ import annotations

EUREKA_SCRIPT_COMPAT_WRAPPER = True

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
_TARGET = Path(__file__).resolve().parents[1] / 'tools/generators/run_h12_retro_community_live_probe.py'
_TARGET_PARENT = str(_TARGET.parent)
if _TARGET_PARENT not in sys.path:
    sys.path.insert(0, _TARGET_PARENT)
_SPEC = spec_from_file_location(f"_eureka_tool_{Path(__file__).stem}", _TARGET)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load tool implementation: {_TARGET}")
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

for _name, _value in vars(_MODULE).items():
    if _name not in {"__name__", "__loader__", "__package__", "__spec__"}:
        globals()[_name] = _value
if __name__ != "__main__":
    sys.modules[__name__] = _MODULE
else:
    sys.argv[0] = str(_TARGET)
    if hasattr(_MODULE, "main"):
        raise SystemExit(_MODULE.main())
    runpy.run_path(str(_TARGET), run_name="__main__")