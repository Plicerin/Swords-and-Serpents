# Note: SDK-1600 tools must be in your $PATH.
#
CC     = gcc -Wall -Werror -ggdb3

# directories
BDIR   = bin
EXE    = exe
F      = fonts
GA     = genasm
WORLD  = world
CDIR   = c
GFX    = gfx
GS     = gfxsrc

all:	$(BDIR)/sdk1600_spacepat.bin

# lists of files
FONT_ASM  = $(F)/tank.fnt 
FONT_ASM += $(F)/misc.fnt 
FONT_ASM += $(F)/digit.fnt 
FONT_ASM += $(F)/mountain.fnt 

CR_FONTS  = $(F)/creep.fnt
CR_FONTS += $(F)/game.fnt

GENASM  = $(GA)/beg_a_e.asm 
GENASM += $(GA)/beg_f_j.asm 
GENASM += $(GA)/beg_k_o.asm 
GENASM += $(GA)/beg_p_t.asm 
GENASM += $(GA)/beg_u_z.asm 

GENASM += $(GA)/chl_a_e.asm 
GENASM += $(GA)/chl_f_j.asm 
GENASM += $(GA)/chl_k_o.asm 
GENASM += $(GA)/chl_p_t.asm 
GENASM += $(GA)/chl_u_z.asm 

GENASM += $(GA)/mab_a_e.asm 
GENASM += $(GA)/mab_f_j.asm 
GENASM += $(GA)/mab_k_o.asm 
GENASM += $(GA)/mab_p_t.asm 
GENASM += $(GA)/mab_u_z.asm 

GENASM += $(GA)/mac_a_e.asm 
GENASM += $(GA)/mac_f_j.asm 
GENASM += $(GA)/mac_k_o.asm 
GENASM += $(GA)/mac_p_t.asm 
GENASM += $(GA)/mac_u_z.asm 

GENASM += $(GA)/plb_a_e.asm 
GENASM += $(GA)/plb_f_j.asm 
GENASM += $(GA)/plb_k_o.asm 
GENASM += $(GA)/plb_p_t.asm 
GENASM += $(GA)/plb_u_z.asm 

GENASM += $(GA)/plc_a_e.asm 
GENASM += $(GA)/plc_f_j.asm 
GENASM += $(GA)/plc_k_o.asm 
GENASM += $(GA)/plc_p_t.asm 
GENASM += $(GA)/plc_u_z.asm 

GENASM += $(GA)/hgb_a_e.asm 
GENASM += $(GA)/hgb_f_j.asm 
GENASM += $(GA)/hgb_k_o.asm 
GENASM += $(GA)/hgb_p_t.asm 
GENASM += $(GA)/hgb_u_z.asm 

GENASM += $(GA)/hgc_a_e.asm 
GENASM += $(GA)/hgc_f_j.asm 
GENASM += $(GA)/hgc_k_o.asm 
GENASM += $(GA)/hgc_p_t.asm 
GENASM += $(GA)/hgc_u_z.asm 

GENASM += $(GA)/creepfnt.asm
GENASM += $(GA)/creep2.asm
GENASM += $(GA)/creep3.asm
GENASM += $(GA)/creep4.asm
#GENASM += $(GA)/demolvl.asm 
GENASM += $(GA)/font.asm    
GENASM += $(GA)/joefnt.asm  
GENASM += $(GA)/sctbl.asm   

GFXASM  = $(GFX)/title.asm
GFXASM += $(GFX)/hut.asm
GFXASM += $(GFX)/midcity1.asm
GFXASM += $(GFX)/midcity2.asm
GFXASM += $(GFX)/midcity3.asm
GFXASM += $(GFX)/midcity4.asm
GFXASM += $(GFX)/rockbg.asm
GFXASM += $(GFX)/midmount.asm
GFXASM += $(GFX)/rockcrat.asm
GFXASM += $(GFX)/spin1.asm
GFXASM += $(GFX)/spin2.asm
GFXASM += $(GFX)/topmount.asm
GFXASM += $(GFX)/ground.asm
GFXASM += $(GFX)/wheels.asm


## top level
SRCASM  = spacepat.asm
SRCASM += $(BDIR)/bldflags.asm

## os-support type thingys
SRCASM += os/main_os.asm
SRCASM += os/rand.asm
SRCASM += os/wnk.asm
SRCASM += os/setisr.asm
SRCASM += os/debounce.asm

## graphics, sound and core game engines
SRCASM += engine/engine1.asm
SRCASM += engine/engine2.asm
SRCASM += engine/runeng.asm 
SRCASM += engine/sfxeng.asm
SRCASM += engine/ckbgb.asm
SRCASM += engine/ckbgp.asm
SRCASM += engine/ckbrc.asm
SRCASM += engine/ckggb.asm
SRCASM += engine/clrsp.asm
SRCASM += engine/ttlsp.asm
SRCASM += engine/upani.asm
SRCASM += engine/upbgp.asm
SRCASM += engine/upbsp.asm
SRCASM += engine/upcrd.asm
SRCASM += engine/uphbp.asm
SRCASM += engine/upmux.asm
SRCASM += engine/upspa.asm
SRCASM += engine/upspp.asm
SRCASM += engine/twinkle.asm
SRCASM += engine/tracker.asm
SRCASM += engine/tank.asm
SRCASM += engine/tictsk.asm

## bad-guy engines
SRCASM += bg/bgengine.asm
SRCASM += bg/bgsaucer.asm
SRCASM += bg/bgthink.asm
SRCASM += bg/bgmpind.asm
SRCASM += bg/bgfollow.asm

## world data 
SRCASM += world/world.asm
SRCASM += world/spawns.asm

## music and sound effect data
SRCASM += snd/sfx.asm
SRCASM += snd/mp.asm
SRCASM += snd/music.asm

## data for rocks, craters and MOBs
SRCASM += $(GFX)/spatbl.asm
SRCASM += $(GFX)/rcsdata.asm

## other game logic
SRCASM += game/title.asm
SRCASM += game/ckpoint.asm
SRCASM += game/gameover.asm
SRCASM += game/level.asm
SRCASM += game/gameloop.asm
SRCASM += game/menu.asm
SRCASM += game/mission.asm
SRCASM += game/names.asm
SRCASM += game/data.asm
SRCASM += game/score.asm

## misc files
SRCASM += macro/dseg.mac
SRCASM += macro/gfx.mac
SRCASM += macro/initmem.mac
SRCASM += macro/p16.mac
SRCASM += macro/s16.mac
SRCASM += macro/score.mac
SRCASM += macro/stic.mac
SRCASM += macro/tracker.mac
SRCASM += macro/util.mac
SRCASM += util/fillmem.asm
SRCASM += util/hex16.asm
SRCASM += util/p16.asm
SRCASM += util/prnum16.asm
SRCASM += util/prnum32.asm
SRCASM += util/initmem.asm

$(GA)/%.asm: $(WORLD)/%.wr3 $(EXE)/wasm3
	$(EXE)/wasm3 $@ $<

$(EXE)/fixsum: $(CDIR)/fixsum.c $(CDIR)/crc16.c $(CDIR)/icartrom.c
	$(CC) -o $@ -g $(CDIR)/fixsum.c $(CDIR)/crc16.c $(CDIR)/icartrom.c

$(EXE)/%: $(CDIR)/%.c
	$(CC) -o $@ -g $<

$(GA)/sctbl.asm: $(EXE)/sctc $(CDIR)/sctc.c bg/saucer.sct
	$(EXE)/sctc bg/saucer.sct > $(GA)/sctbl.asm

$(GA)/font.asm: $(FONT_ASM) $(EXE)/mkfont16
	$(EXE)/mkfont16 $(FONT_ASM) > $(GA)/font.asm

$(GA)/creepfnt.asm: $(EXE)/mkfont16 $(CR_FONTS)
	$(EXE)/mkfont16 $(CR_FONTS) > $(GA)/creepfnt.asm

$(GA)/joefnt.asm: $(EXE)/mkfont16 $(F)/joe.fnt
	$(EXE)/mkfont16 $(F)/joe.fnt > $(GA)/joefnt.asm

$(GA)/%.asm: $(F)/%.fnt $(EXE)/mkfont16
	$(EXE)/mkfont16 $< > $@

$(GA)/topmount.asm: $(GS)topmount $(EXE)/maketmnt
	$(EXE)/maketmnt < topmount > $(GA)/topmount.asm

$(GA)/rockcrat.asm: $(GS)/rock1 $(GS)/rock2 $(GS)/rock3 $(GS)/crat1 $(GS)/crat2 $(EXE)/makerock
	$(EXE)/makerock > $(GA)/rockcrat.asm

$(BDIR)/sdk1600_spacepat.rom: $(SRCASM) $(GFXASM) $(GENASM) $(EXE)/today $(EXE)/fixsum
	$(EXE)/today > genasm/date.asm
	as1600 -c -i$(BDIR) -o $(BDIR)/sdk1600_spacepat.rom -l $(BDIR)/spacepat.lst -s $(BDIR)/spacepat.sym spacepat.asm
	$(EXE)/fixsum
	@echo ""
	@echo "========================================"
	@grep _.*.end bin/spacepat.sym
	@echo "========================================"
	@echo ""

$(BDIR)/sdk1600_spacepat.bin: $(BDIR)/sdk1600_spacepat.rom dbgmac.cfg
	rom2bin $(BDIR)/sdk1600_spacepat.rom
	cat dbgmac.cfg >> $(BDIR)/sdk1600_spacepat.cfg


$(GFX)/midcity1.asm: $(GS)/midcity1 $(EXE)/makecity
	$(EXE)/makecity MIDCITY1 < $(GS)/midcity1 > $(GFX)/midcity1.asm

$(GFX)/midcity2.asm: $(GS)/midcity2 $(EXE)/makecity
	$(EXE)/makecity MIDCITY2 < $(GS)/midcity2 > $(GFX)/midcity2.asm

$(GFX)/midcity3.asm: $(GS)/midcity3 $(EXE)/makecity
	$(EXE)/makecity MIDCITY3 < $(GS)/midcity3 > $(GFX)/midcity3.asm

$(GFX)/midcity4.asm: $(GS)/midcity4 $(EXE)/makecity
	$(EXE)/makecity MIDCITY4 < $(GS)/midcity4 > $(GFX)/midcity4.asm

$(GFX)/rockbg.asm:   $(GS)/rockbg $(EXE)/makecity
	$(EXE)/makecity ROCKBG   < $(GS)/rockbg > $(GFX)/rockbg.asm

clean:
	rm -f $(BDIR)/sdk1600_spacepat.bin $(BDIR)/sdk1600_spacepat.cfg 
	rm -f $(BDIR)/sdk1600_spacepat.rom
	rm -f $(BDIR)/spacepat.lst $(BDIR)/spacepat.sym
	rm -f $(GENASM) genasm/date.asm
	rm -f $(EXE)/makerock $(EXE)/makemmnt $(EXE)/maketmnt $(EXE)/mkfont16
	rm -f $(EXE)/wasm3 $(EXE)/today $(EXE)/sctc $(EXE)/fixsum $(EXE)/makecity
	rm -rf $(EXE)/*.dSYM
