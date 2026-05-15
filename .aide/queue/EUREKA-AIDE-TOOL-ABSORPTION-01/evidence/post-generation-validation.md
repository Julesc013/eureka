# Post-Generation Validation

Interpreter used: `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe` (Python 3.12.9).

The sandboxed `py` launcher was inaccessible after the permission-mode change; system `python` is Python 3.8.1 and fails AIDE writer selftests because `Path.write_text(..., newline=...)` requires a newer Python.

- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py doctor`: PASS (exit 0, 16.26s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py validate`: PASS (exit 0, 16.6s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py test`: PASS (exit 0, 29.71s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py selftest`: PASS (exit 0, 21.41s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py verify`: PASS (exit 0, 2.08s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py review-pack`: PASS (exit 0, 2.63s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py tools validate`: PASS (exit 0, 2.32s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py tools status`: PASS (exit 0, 0.84s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py tools capabilities`: PASS (exit 0, 1.2s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py roots status`: PASS (exit 0, 1.25s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py repo validate`: PASS (exit 0, 1.97s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py quality validate`: PASS (exit 0, 5.21s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py intent validate`: PASS (exit 0, 0.8s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py git policy`: PASS (exit 0, 1.07s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`: PASS (exit 0, 0.73s)
- `C:\Program Files\Hybrid\64bit\Vapoursynth\python.exe scripts/check_architecture_boundaries.py`: PASS (exit 0, 11.55s)
- `git diff --check`: PASS (exit 0, 2.58s)
- `git check-ignore -v .aide.local/`: PASS (exit 0, 0.12s)
