@echo off

setlocal enabledelayedexpansion

SET ram=4G
SET name=%1
SET jar=%2

title %name%

echo Folder name = %name%
echo Jar file name = %jar%

cd "%name%"
java -Xmx%ram% -Xms%ram% -jar "%jar%" nogui

pause