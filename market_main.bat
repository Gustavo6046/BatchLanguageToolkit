@echo off
echo The Galactic Market
echo        by Gustavo Ramos Rehermann
echo ----
echo.
echo Type the language's name. (lang_*.bat)
set /p "lang=: "

call "lang_%lang%.bat"
rem @echo on
call :gen_name 9
set ore.1.name=%res%ite
call :gen_name 9
set ore.2.name=%res%ite
call :gen_name 9
set ore.3.name=%res%ite
set /a ore.1.kgprice=%RANDOM% %% 20000
set /a ore.2.kgprice=%RANDOM% %% 20000
set /a ore.3.kgprice=%RANDOM% %% 50000
set money=ore.1.kgprice
set /a money+=ore.2.kgprice
set /a money/= 8

set num0=zero
set num1=one
set num2=two
set num3=three
set num4=four
set num5=five
set num6=six
set num7=seven
set num8=eight
set num9=nine
set "dec0="
set "dec1=%rad.ten%%ligation%%rad.fold% "
set "dec2=%rad.hundred%%ligation%%rad.fold% "
set "dec3=%rad.thousand%%ligation%%rad.fold% "
set "dec4=%rad.ten%%ligation%%rad.thousand%%ligation%%rad.fold% "
set "dec5=%rad.hundred%%ligation%%rad.thousand%%ligation%%rad.fold% "

echo.
echo Welcome to the Market!
echo Aliens that speak %langname%
echo sell stuff around here.
echo.
echo Here you see three stands.
echo.
echo The first one sells what its alien
echo owner calls '%rad.red%%ligation%%rad.stone%',
echo which is a bright red, rough ore, that barely
echo shines. A nearby sign announces:
echo - %pronoun.indefinite.pointer.internal% %rad.cost%%conjugation.third.singular%:
call :lang_number %ore.1.kgprice%
echo %res% %rad.money% %rad.unit%%ending.plural%
echo.
echo The second one sells more refined
echo material; '%rad.blue%%ligation%%rad.strength%'.
echo Shiny blue metal bars. The sign aside says:
echo - %pronoun.indefinite.pointer.internal% %rad.cost%%conjugation.third.singular%:
call :lang_number %ore.2.kgprice%
echo %res% %rad.money% %rad.unit%%ending.plural%
echo.
echo The third one sells a clear, cut, white
echo gem. "%rad.white%%ligation%%rad.beauty%%ending.nominal.degree.large%".
echo A futuristic screen reads:
echo - 1KG %rad.of% %rad.white%%ligation%%rad.beauty%%ending.nominal.degree.large% %rad.cost%%conjugation.third.singular%:
call :lang_number %ore.3.kgprice%
echo %res% %rad.money% %rad.unit%%ending.plural%
goto :eof

:lang_number
set "number=%1"
call :strlen %number% nlength
set "res="
set ind=0

:lnum_loop
call set digit=%%number:~%ind%,1%%
set decp=%nlength%
set /a decp-=%ind%
if %digit% EQU 0 GOTO :lnum_continue
call set _num=%%num%digit%%%
call set "res=%res%%%dec%decp%%%%%rad.%_num%%% "

:lnum_continue
set /a ind+=1
if %ind% GTR %nlength% goto :lnum_finish
goto :lnum_loop

:lnum_finish
set "res=%res:~0,-1%"
goto :eof

:gen_name
set vowels=AEIOU
set consonants=BCDFGHJKLMNPQRSTVWXYZ
set dig1=tglpr
set dig2=hln
set isc=yes
set dig=no
set len=%1
set "res="

:gen_loop
set "cn="
set "vw="

if %isc%==yes (
	set /a dig=%RANDOM% %% 7
	if %dig% LSS 2 (set dig=yes) else (set dig=no)
	
	if %dig%==yes (
		set /a "d1=%RANDOM% %% 6"
		set /a "d2=%RANDOM% %% 4"
		set /a d1-=1
		set /a d2-=1
		echo %d1% %d2%
		call set "d1=%%dig1:~%d1%,1%%"
		call set "d2=%%dig2:~%d2%,1%%"
		set "res=%res%%d1%%d2%"
	) else (
		set /a cn=%RANDOM% %% 22
		set /a cn-=1
		call set "cn=%%consonants:~%cn%,1%%"
		set "res=%res%%cn%"
	)
	
	set isc=no
) else (
	set /a vw=%RANDOM% %% 6
	set /a vw-=1
	call set "vw=%%vowels:~%vw%,1%%"
	set "res=%res%%vw%"
	set isc=yes
)

set /a len-=1
if %len% GTR 0 goto :gen_loop
goto :eof

REM Slightly modified version from Stack
REM Overflow.
:strlen
setlocal EnableDelayedExpansion
set "s=%1"
set "len=0"
set "res.strlen="
for %%P in (4096 2048 1024 512 256 128 64 32 16 8 4 2 1) do (
	if "!s:~%%P,1!" NEQ "" (
		set /a "len+=%%P"
		set "s=!s:~%%P!"
	)
)
endlocal & (
	set %2=%len%
)
goto :eof

:eof