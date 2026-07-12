Everything below the line is a historical README file written during
development of Space Patrol (back when it was named LunarMP).  I'm keeping
it here for historical purposes.

And for the record, LunarMP stood for Lunar Military Police.

--JZ

_______________________________________________________________________________

Currently defined keys:


[0]  Exit
[1]  Draw crater scene
[3]  Draw city scene
[4]  Flash red caution
[5]  Flash green caution
[6]  Flash pink caution
[7]  Back one checkpoint
[8]  Restart current checkpoint
[9]  Next checkpoint

Upper Action:  Fire
Lower Action:  Jump

DISC:  Speed up / slow down.


Here's a map to what's in LunarMP:

.
|-- README.txt          This file
|
|-- Makefile            Linux Makefile to build LunarMP
|-- build.bat           DOS batch file to build LunarMP
|-- dbgmac.cfg          Debug helpers for INTVPC
|
|-- lunar_mp.asm
|
|-- bin                 Where the generated binaries go
|   |-- lunar_mp.bin
|   |-- lunar_mp.cfg
|   |-- lunar_mp.lst
|   |-- lunar_mp.rom
|   `-- lunar_mp.sym
|
|-- engine              Various engines:  Graphics, world, sound, bad guy 
|   |-- engine1.asm     Very time-sensitive graphics engine
|   |-- engine2.asm     Less time-sensitive world engine
|   `-- soundeng.asm    Sound / music engine
|
|-- bg                  Bad Guys!
|   |
|   |-- bgmpind.asm     Indirect lookup table for Bad Guy Motion Programs
|   |-- bgthink.asm     Bad Guy thinker routines, except for saucers
|   |-- bgsaucer.asm    Saucer AI (reads saucer control tables)
|   `-- bgengine.asm    Bad Guy engine top-level
|
|-- bgmp                Bad Guy Motion Programs (Saucer Control Tables)
|   `-- test.sct        Current test saucer control tables
|
|-- game                Additional game logic
|   `-- ckpoint.asm     Checkpoint display screen (not currently used)
|
|-- gfx                 Graphics-related data
|   |-- mobattr.asm     MOB attributes for all MOBs
|   |-- rcsdata.asm     Metadata for rocks and craters
|   |-- rockcrat.asm    Graphics for rocks and craters
|   |-- spin.asm        Graphics for white spinner
|   |-- lmptitle.asm    Graphics for title badge
|   |-- midcity.asm     Graphics for middle section:  City scene
|   |-- midmount.asm    Graphics for middle section:  Mountain/crater scene
|   `-- topmount.asm    Graphics for top section
|
|-- macro               Handy macros
|   |-- gfx.mac
|   |-- print.mac
|   `-- stic.mac
|
|-- os                  RTOS-like functionality
|   |-- main_os.asm     Main scheduler
|   |-- scanhand.asm    Hand controller scanner
|   |-- taskq.asm       Async task queue and idle loop
|   `-- rand.asm        Random number generator
|
|-- snd                 Sound/Music files
|   |-- lmp_sfx.asm     Sound effects and top level registry for music
|   |-- music.asm       Top level wrapper for music
|   `-- mp.asm          Moon Patrol main theme
|
|-- util                Utility functions (same as SDK-1600 equiv)
|   |-- fillmem.asm
|   |-- hex16.asm
|   |-- print.asm
|   |-- prnum16.asm
|   `-- prnum32.asm
|
|-- misc                Dumping ground for anything else
|   `-- sega.asm        Inty title animation
|
|-- gfxsrc              Source files for generating many of the graphics
|   |-- crat1           Small crater
|   |-- crat2           Large crater
|   |-- rock1           Small rock
|   |-- rock2           Medium rock
|   |-- rock3           Large rock
|   |-- midcity         Middle-section graphic: City 
|   |-- midmount        Middle-section graphic: Crater/mountain
|   `-- topmount        Top section graphic:  Mountains
|
|-- fonts               Fonts / graphic pictures
|   |-- creep.fnt
|   |-- digit.fnt
|   |-- game.fnt
|   |-- joe.fnt
|   |-- misc.fnt
|   |-- mountain.fnt
|   |-- sega.fnt
|   `-- tank.fnt
|
|-- world               World data and related tables.
|   |
|   |                   The world-data files have a very simple format.
|   |                   See "c/wasm3.c" for the format.
|   |
|   |-- beg_a_e.wr3     Beginner's Course, A-E
|   |-- beg_f_j.wr3     Beginner's Course, F-J
|   |-- beg_k_o.wr3     Beginner's Course, K-O
|   |-- beg_p_t.wr3     Beginner's Course, P-T
|   |-- beg_u_z.wr3     Beginner's Course, U-Z
|   |-- demolvl.wr3     Extra, for testing plants
|   |
|   |-- chl_a_e.wr3     Challenge Course, A-E
|   |-- chl_f_j.wr3     Challenge Course, F-J
|   |-- chl_k_o.wr3     Challenge Course, K-O
|   |-- chl_p_t.wr3     Challenge Course, P-T
|   |-- chl_u_z.wr3     Challenge Course, U-Z
|   |
|   |-- spawns.asm      Spawn tables describing types of spawns
|   `-- world.asm       Top level world wrapper
|
|-- musicsrc
|   |-- chicken.txt     Chicken Dance
|   |-- moonptrl.txt    Moon Patrol theme
|   `-- patrol.rgn
|
|-- genasm              Generated assembly, generated from .fnt, .wr3, etc.
|   |-- beg_a_e.asm
|   |-- beg_f_j.asm
|   |-- beg_k_o.asm
|   |-- beg_p_t.asm
|   |-- beg_u_z.asm
|   |-- creepfnt.asm
|   |-- demolvl.asm
|   |-- font.asm
|   |-- joefnt.asm
|   |-- sctbl.asm
|   `-- spawns.asm
|
|-- exe                 DOS/Linux executables for helper utilities
|   |-- fixcfg.exe
|   |-- makemmnt.exe
|   |-- makerock.exe
|   |-- maketmnt.exe
|   |-- mkfont16
|   |-- mkfont16.exe
|   |-- pm16.exe
|   |-- profile.exe
|   |-- rom2bin.exe
|   |-- sctc
|   |-- sctc.exe
|   `-- wasm3.exe
|
|-- c                   C source for little helper utilities
|   |-- config.h
|   |-- crc16.c
|   |-- crc16.h
|   |-- fixcfg.c
|   |-- icartrom.c
|   |-- icartrom.h
|   |-- jumprock.c
|   |-- makecity.c
|   |-- makemmnt.c
|   |-- makerock.c
|   |-- maketmnt.c
|   |-- mkfont16.c
|   |-- pm16.c
|   |-- profile.c
|   |-- rom2bin.c
|   |-- sctc.c
|   `-- wasm3.c
|
`-- _exrc               Preferred editor settings for VIM



