
@echo off

set here=%~dp0
set user_src=%here%\SublimeText3\User

set user_dest=%userprofile%\AppData\Roaming\Sublime Text 3\Packages\User

IF EXIST "%user_dest%" (
    echo Error: '%user_dest%' already exists
    echo        Remove this directory and rerun this script
) ELSE (
    IF NOT EXIST "%user_dest%\.." (
        echo Making dir "%user_dest%\.."
        MKDIR "%user_dest%\.."
    )
    mklink /D "%user_dest%" %user_src%
)
