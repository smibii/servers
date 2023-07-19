@echo off

setlocal enabledelayedexpansion

SET name=%1
SET jar=%2

title %name%

echo Folder name = %name%
echo Jar file name = %jar%

cd "%name%"
java -Xmx3G -Xms3G -jar "%jar%" nogui

pause