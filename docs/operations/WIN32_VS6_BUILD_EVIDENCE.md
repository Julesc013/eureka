# Win32 VS6 Build Evidence

Win32 build evidence requires a suitable Visual C++ 6.0 style host.

Future manual steps:

- Open `native/win/win32/project/Eureka.dsw`.
- Confirm `Eureka.dsp` references only committed source/resource files.
- Build without package restore or network dependency.
- Launch the app and confirm read-only panes render.
- Record smoke evidence under an explicit audit generated path.

No build outputs, installers, binaries, or logs are committed in C-BUNDLE-02.
