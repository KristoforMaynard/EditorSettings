
@echo off

set here=%~dp0
set user_src=%here%\VSCode\User

set user_dest=%userprofile%\AppData\Roaming\Code\User
set ext_dest=%userprofile%\.vscode\extensions

IF EXIST %user_dest% (
    echo Error: '%user_dest%' already exists
    echo        Remove this directory and rerun this script
) ELSE (
    IF NOT EXIST %user_dest%\.. (
        MKDIR %user_dest%\..
    )
    mklink /D %user_dest% %user_src%
)

FOR %%E IN (xkod) DO (
    IF EXIST %ext_dest%\%%E (
        RMDIR /Q %ext_dest%\%%E
    )
    mklink /D %ext_dest%\%%E %user_src%\%%E
)
