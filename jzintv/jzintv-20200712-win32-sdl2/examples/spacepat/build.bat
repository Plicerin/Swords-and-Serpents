set bdir=%1
if "%1" == "" set bdir=bin
@REM perl exe\spasm.pl < bgmp\spawns > genasm\spawns.asm
@REM if errorlevel 1 goto err
exe\sctc bg/saucer.sct > genasm\sctbl.asm
@call world.bat demolvl .
@if errorlevel 1 goto err
@call world.bat beg_a_e beg_f_j beg_k_o beg_p_t beg_u_z .
@if errorlevel 1 goto err
@call world.bat chl_a_e chl_f_j chl_k_o chl_p_t chl_u_z .
@if errorlevel 1 goto err
@call world.bat mab_a_e mab_f_j mab_k_o mab_p_t mab_u_z .
@if errorlevel 1 goto err
@call world.bat mac_a_e mac_f_j mac_k_o mac_p_t mac_u_z .
@if errorlevel 1 goto err
@call world.bat plb_a_e plb_f_j plb_k_o plb_p_t plb_u_z .
@if errorlevel 1 goto err
@call world.bat plc_a_e plc_f_j plc_k_o plc_p_t plc_u_z .
@if errorlevel 1 goto err
@call world.bat hgb_a_e hgb_f_j hgb_k_o hgb_p_t hgb_u_z .
@if errorlevel 1 goto err
@call world.bat hgc_a_e hgc_f_j hgc_k_o hgc_p_t hgc_u_z .
@if errorlevel 1 goto err
exe\mkfont16 fonts/tank.fnt fonts/misc.fnt fonts/digit.fnt fonts/mountain.fnt > genasm\font.asm
@if errorlevel 1 goto err
exe\mkfont16 fonts/joe.fnt > genasm\joefnt.asm
@if errorlevel 1 goto err
exe\mkfont16 fonts/creep.fnt fonts/game.fnt > genasm\creepfnt.asm
@if errorlevel 1 goto err
exe\mkfont16 fonts/creep2.fnt > genasm\creep2.asm
@if errorlevel 1 goto err
exe\mkfont16 fonts/creep3.fnt > genasm\creep3.asm
@if errorlevel 1 goto err
exe\mkfont16 fonts/creep4.fnt > genasm\creep4.asm
@if errorlevel 1 goto err
exe\today > genasm\date.asm
as1600 -o %bdir%/spacepat -l %bdir%/spacepat.lst -s %bdir%/spacepat.sym -i%bdir% spacepat.asm
exe\fixsum
exe\rom2bin %bdir%/spacepat.rom
@REM @if errorlevel 1 goto err
@REM exe\fixcfg 
@REM @if errorlevel 1 goto err
@REM move /y bin\new.cfg bin\spacepat.cfg
@REM @if errorlevel 1 goto err
@goto end
:err
@echo BUILD ABORTED DUE TO ERRORS
:end
