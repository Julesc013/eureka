# Microsoft Developer Studio Project File - Name="Eureka" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# Build-unverified skeleton for C-BUNDLE-02.

# TARGTYPE "Win32 (x86) Application" 0x0101

CFG=Eureka - Win32 Debug
!MESSAGE This project is a read-only fixture skeleton.
!MESSAGE It does not download, install, execute payloads, or mutate indexes.

!IF "$(CFG)" == "Eureka - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# ADD BASE CPP /nologo /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /YX /FD /c
# ADD CPP /nologo /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "EUREKA_READONLY" /YX /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x409 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 user32.lib gdi32.lib /nologo /subsystem:windows /machine:I386
# ADD LINK32 user32.lib gdi32.lib /nologo /subsystem:windows /machine:I386

!ELSEIF "$(CFG)" == "Eureka - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# ADD BASE CPP /nologo /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /YX /FD /c
# ADD CPP /nologo /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "EUREKA_READONLY" /YX /FD /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "_DEBUG"
# ADD RSC /l 0x409 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 user32.lib gdi32.lib /nologo /subsystem:windows /debug /machine:I386
# ADD LINK32 user32.lib gdi32.lib /nologo /subsystem:windows /debug /machine:I386

!ENDIF

# Begin Target

# Name "Eureka - Win32 Release"
# Name "Eureka - Win32 Debug"

# Begin Group "Source Files"
# Begin Source File
SOURCE=..\src\app\main.c
# End Source File
# Begin Source File
SOURCE=..\src\app\eu_win32_app.c
# End Source File
# Begin Source File
SOURCE=..\src\ui\eu_win32_main_window.c
# End Source File
# Begin Source File
SOURCE=..\src\ui\eu_win32_dialogs.c
# End Source File
# Begin Source File
SOURCE=..\src\contract\eu_win32_snapshot_adapter.c
# End Source File
# Begin Source File
SOURCE=..\src\contract\eu_win32_relay_adapter.c
# End Source File
# End Group

# Begin Group "Header Files"
# Begin Source File
SOURCE=..\src\app\eu_win32_app.h
# End Source File
# Begin Source File
SOURCE=..\src\ui\eu_win32_main_window.h
# End Source File
# Begin Source File
SOURCE=..\src\ui\eu_win32_dialogs.h
# End Source File
# Begin Source File
SOURCE=..\src\contract\eu_win32_snapshot_adapter.h
# End Source File
# Begin Source File
SOURCE=..\src\contract\eu_win32_relay_adapter.h
# End Source File
# End Group

# Begin Group "Resource Files"
# Begin Source File
SOURCE=..\res\Eureka.rc
# End Source File
# Begin Source File
SOURCE=..\res\resource.h
# End Source File
# End Group

# End Target
