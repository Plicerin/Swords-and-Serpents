;;==========================================================================;;
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;


;; ------------------------------------------------------------------------ ;;
;;                                                                          ;;
;;  "But this has taken us far afield from interface, which is not          ;;
;;   a bad place to be, since I particularly want to move ahead to          ;;
;;   the kludge.  Why do people have so much trouble understanding          ;;
;;   the kludge?  What is a kludge, after all, but not enough Ks,           ;;
;;   not enough ROMs, not enough RAMs, poor quality interface and too       ;;
;;   few bytes to go around?  Have I explained yet about the bytes?"        ;;
;;                                              -- UNIX Fortune File        ;;
;;                                                                          ;;
;; ------------------------------------------------------------------------ ;;

 CFGVAR  "name" = "SDK-1600 Space Patrol"
 CFGVAR  "short_name" = "Space Patrol"
 CFGVAR  "author" = "Joe Zbiciak"
 CFGVAR  "sfx_by" = "Joe Zbiciak"
 CFGVAR  "game_art_by" = "Joe Zbiciak"
 CFGVAR  "box_art_by" = "Teresa Zbiciak"
 CFGVAR  "music_by" = "Arnauld Chevallier"
 CFGVAR  "author" = "Arnauld Chevallier"
 CFGVAR  "author" = "David Harley"
 CFGVAR  "year" = 2006
 CFGVAR  "license" = "GPLv2+"
 CFGVAR  "description" = "The SDK-1600 build of Space Patrol (no LTO branding)."
 CFGVAR  "publisher" = "SDK-1600"
 CFGVAR  "ecs_compat" = 2    ; Enhanced by ECS

        INCLUDE "bldflags.asm"  ; should be in whatever our builddir is

        ROMW    16              ; This makes life mucho easier.

;; ------------------------------------------------------------------------ ;;
;;  Magic Constants                                                         ;;
;; ------------------------------------------------------------------------ ;;
COPYR   EQU     $13A            ; Character # for Copyright circle-C
JZB     EQU     $121            ; Starting character # for my name...

C_BLK   EQU     $0              ; Black
C_BLU   EQU     $1              ; Blue
C_RED   EQU     $2              ; Red
C_TAN   EQU     $3              ; Tan
C_DGR   EQU     $4              ; Dark Green
C_GRN   EQU     $5              ; Green
C_YEL   EQU     $6              ; Yellow
C_WHT   EQU     $7              ; White
C_GRY   EQU     $8              ; Grey
C_CYN   EQU     $9              ; Cyan
C_ORG   EQU     $A              ; Orange
C_BRN   EQU     $B              ; Brown
C_PNK   EQU     $C              ; Pink
C_LBL   EQU     $D              ; Light Blue
C_YGR   EQU     $E              ; Yellow-Green
C_PUR   EQU     $F              ; Purple

X_BLK   EQU     $0              ; Black
X_BLU   EQU     $1              ; Blue
X_RED   EQU     $2              ; Red
X_TAN   EQU     $3              ; Tan
X_DGR   EQU     $4              ; Dark Green
X_GRN   EQU     $5              ; Green
X_YEL   EQU     $6              ; Yellow
X_WHT   EQU     $7              ; White
X_GRY   EQU     $1000           ; Grey
X_CYN   EQU     $1001           ; Cyan
X_ORG   EQU     $1002           ; Orange
X_BRN   EQU     $1003           ; Brown
X_PNK   EQU     $1004           ; Pink
X_LBL   EQU     $1005           ; Light Blue
X_YGR   EQU     $1006           ; Yellow-Green
X_PUR   EQU     $1007           ; Purple

; STIC MOB attribute bits
_X      PROC                    ; bits in the MOB's X register
@@na    EQU     $0000
@@xsiz  EQU     $0400           ; Doubles width
@@visb  EQU     $0200           ; Visible vs. Invisible
@@intr  EQU     $0100           ; Object interacts w/ others
        ENDP
_Y      PROC                    ; bits in the MOB's Y register
@@na    EQU     $0000
@@yres  EQU     $0080           ; 16-lines
@@siz1  EQU     $0000           ; 1x height
@@siz2  EQU     $0100           ; 2x height
@@siz4  EQU     $0200           ; 4x height
@@siz8  EQU     $0300           ; 8x height
@@xmir  EQU     $0400           ; Mirror horizontally
@@ymir  EQU     $0800           ; Mirror vertically
        ENDP
_A      PROC                    ; bits in the MOB's A register
@@na    EQU     $0000
@@grom  EQU     $0000           ; MOB's card is in GROM
@@gram  EQU     $0800           ; MOB's card is in GRAM
@@prio  EQU     $2000           ; MOB is behind background
        ENDP

VFAST   EQU     $FF
VMED    EQU     $BF
VSLOW   EQU     $6F
VJUMP   EQU     $1B
;VBIAS   EQU     $80

MAXGP1  EQU     5               ; Max sprites in group 1 is 5
MAXGP2  EQU     7               ; Max sprites in group 2 is 7
MAXSPR  EQU     MAXGP1+MAXGP2   ; Max total sprites is 12.
                                ; We mux these onto 6 MOBs.

X_TITL  EQU     X_PUR           ; \_ Title screen color scheme
C_TITL  EQU     C_PUR           ; /
C_STAT  EQU     C_GRY           ; Status bar color
X_GRND  EQU     X_ORG           ; \_ Ground color
C_GRND  EQU     C_ORG           ; /
X_ROCK  EQU     X_BRN           ; \_ Rock color
C_ROCK  EQU     C_BRN           ; /

TSKQM   EQU     $7              ; 7 task queue

M_DUP   EQU     $1              ; music flag : 'duplicate on channels B/C'
M_3CH   EQU     $2              ; music flag : '3-channel tune'
M_TICK  EQU     $4              ; music flag : 'ticks enabled'

;; ======================================================================== ;;
;;  Magic memory locations                                                  ;;
;; ======================================================================== ;;
VBLANK      EQU     $20         ; Vertical-blank Handshake
COLSTK      EQU     $21         ; Color-stack/FGBG switch
CS0         EQU     $28         ; Color Stack 0
CS1         EQU     $29         ; Color Stack 1
CS2         EQU     $2A         ; Color Stack 2
CS3         EQU     $2B         ; Color Stack 3
CB          EQU     $2C         ; Color for border

EC_LOC      EQU     $CF00
EC_MAG      EQU     $69
EC_POLL     EQU     $CF01

;; ======================================================================== ;;
;;  MACROS                                                                  ;;
;; ======================================================================== ;;
            INCLUDE "macro/util.mac"
            INCLUDE "macro/stic.mac"
            INCLUDE "macro/tracker.mac"
            INCLUDE "macro/dseg.mac"
            INCLUDE "macro/gfx.mac"
            INCLUDE "macro/initmem.mac"
            INCLUDE "macro/s16.mac"
            INCLUDE "macro/p16.mac"
            INCLUDE "macro/score.mac"


ISRVEC      EQU     $100 ;-$101 ; ISR jump vector

;; ======================================================================== ;;
;;  SCRATCH (8-bit) MEMORY                                                  ;;
;; ======================================================================== ;;
TICK        SCRATCH 1           ; Global clock tick
PTPHAS      SCRATCH 1           ; Previous top-mountain phase
PMPHAS      SCRATCH 1           ; Previous mid-mountain phase
PGPHAS      SCRATCH 1           ; Previous ground phase
PPGPHA      SCRATCH 1           ; Previous ground phase
MOFS        SCRATCH 1           ; Previous ground card offset
PGCARD      SCRATCH 1           ; Previous ground card offset
MIDGFX      SCRATCH 1           ; City or mountain for mid gfx.
MIDMSK      SCRATCH 1           ; mask for CITY vs. MOUNTAIN ($3FFF/$1FFF)
TSKIP       SCRATCH 1           ; Top vs. Mid mountain priority flag
INCITY      SCRATCH 1           ; Zero if not in CITY.
CRATCNT     SCRATCH 1           ; Counter until we can make new crater
GDATA       SCRATCH 1           ; Ground pixel pattern
HBDATA      SCRATCH 1           ; Horizontal bullet pixel pattern
HBCOL0      SCRATCH 1           ; Horizontal bullet column (old)
HBCOL1      SCRATCH 1           ; Horizontal bullet column (new)
HBCNT       SCRATCH 1           ; Horizontal bullet lifetime counter
HBCNT2      SCRATCH 1           ; Horizontal bullet fire-to-fire counter
HBROW       SCRATCH 1           ; Horizontal bullet row
HBKOS       SCRATCH 1           ; Horizontal bullet kill-on-scroll
TMCLR       SCRATCH 1           ; Title message color 
TMADDR      SCRATCH 1           ; Title message address


;SKIPRC      SCRATCH 1           ; XXX -- Skip decoding of rocks/craters
;EXITOK      SCRATCH 1           ; XXX -- schedexit trigger, to reuse for pause
;STCNT       SCRATCH 1           ; XXX -- Stats div-by-16 counter
;IDLE        SCRATCH 1           ; Number of idle ticks

FDROP       SCRATCH 1           ; Number of frames droped (if any)
EMODE       SCRATCH 1           ; Operating mode for engine
CUENUM      SCRATCH 1           ; Deferred bad-guy CUE
BGFLAG      SCRATCH 1           ; Flag:  Bad-guy engine even/odd frame toggle
BGMPTBL     SCRATCH 20          ; Bad-guy motion program table.
BGEXIT      SCRATCH 5           ; BGMP Exit program table.
MOBHIT      SCRATCH 1           ; LSB set if buggy collides w/ other MOBs
CAUTFL      SCRATCH 1

CONTS       SCRATCH 1           ; Continues left
LIVES       SCRATCH 1           ; Lives left
POINT       SCRATCH 1           ; Last passed checkpoint
COURSE      SCRATCH 1           ; Course number (0..7)

DEFSCO      SCRATCH 1           ; Deferred score (waiting for buggy to land)
CURBON      SCRATCH 1           ; Current bonus threshold
WAVE        SCRATCH 1           ; Number of currently active saucers
WKILL       SCRATCH 1           ; Number of saucers killed in this wave
DOSCO       SCRATCH 1           ; Flag:  Do score update

.SPSTART8   SET     .SCRMEM
SPAT        SCRATCH 12          ; Attributes for 12 sprites
SPAT1       EQU     SPAT        ; Offset into SPAT table for Group 1
SPAT2       EQU     SPAT  + 5   ; Offset into SPAT table for Group 2

JMPSCO      SCRATCH 5           ; Jumpable-object scoring info fpr SP #0-4
SPHSCR      SCRATCH 5           ; Horizontal-scroll flags for SP #0-4
LANDED      SCRATCH 1           ; Flag:  Just landed safely

GP1MOB      SCRATCH 1           ; Number of MOBs alloc'd to group 1
GP1ACT      SCRATCH 1           ; Number of active sprites in group 1
GP1CNT      SCRATCH 1           ; Multiplex counter for group 1
GP2MOB      SCRATCH 1           ; Number of MOBs alloc'd to group 2
GP2ACT      SCRATCH 1           ; Number of active sprites in group 2
GP2CNT      SCRATCH 1           ; Multiplex counter for group 2
.SPSTOP8    SET     .SCRMEM

TXLO        SCRATCH 1           ; Pixel column of back end of tank
FXLO        SCRATCH 1           ; Pixel column of follower (minelayer)
FHCNT       SCRATCH 1           ; Follower fast-hover count

RCCNT       SCRATCH 1
RCPIC       SCRATCH 1
RCNXT       SCRATCH 2           ; RCIDX for next level
RCLVL       SCRATCH 2           ; RCIDX for current level
LMCNT       SCRATCH 1           ; Level marker counter
LMCHAR      SCRATCH 1           ; Level 'character'

TIMSEC      SCRATCH 1
TIMTIC      SCRATCH 1
CKTOG       SCRATCH 1           ; Toggle checking bad guy/good-guy bullets
FCNT        SCRATCH 1           ; Counter:  Rate-limit bullet firing.
EBSY        SCRATCH 1           ; Engine Busy flag (in case we drop frames)
SPINCNT     SCRATCH 1           ; Spinner frame counter
SPINB       SCRATCH 1           ; Spinner bullet in the air
WTIMER      SCRATCH 1           ; Countdown timer for WAIT

GRATE       SCRATCH 1           ; Ground scrolling rate
WANTVL      SCRATCH 1           ; desired velocity
JVEL        SCRATCH 1           ; Current jump velocity (0 == not moving)
DOENG       SCRATCH 1
DNENG       SCRATCH 1

DBOUT       SCRATCH 1           ; Debounced hand controller values
DBCM        SCRATCH 1           ; Debounce counter MSB
DBCL        SCRATCH 1           ; Debounce counter LSB

TMP         SCRATCH 5           ; Temp storage for whoever needs it
SCROLL      EQU     TMP

RFRSH_M     SCRATCH 1           ; Generic counter for music refresh
NOTE_A      SCRATCH 1           ; Current note on channel A
NOTE_B      SCRATCH 1           ; Current note on channel B
NOTE_C      SCRATCH 1           ; Current note on channel C
RFRSH_A     SCRATCH 1           ; Counter for refresh on channel A
RFRSH_B     SCRATCH 1           ; Counter for refresh on channel B
RFRSH_C     SCRATCH 1           ; Counter for refresh on channel C
VOL_A       SCRATCH 1           ; Current volume on channel A
VOL_B       SCRATCH 1           ; Current volume on channel B
VOL_C       SCRATCH 1           ; Current volume on channel C
_INSTR_A    SCRATCH 1           ; ** available **
_INSTR_B    SCRATCH 1           ; ** available **
_INSTR_C    SCRATCH 1           ; ** available **
COUNT_A     SCRATCH 1           ; Note counter on channel A
COUNT_B     SCRATCH 1           ; Note counter on channel B
COUNT_C     SCRATCH 1           ; Note counter on channel C
COUNT_M     SCRATCH 1           ; Generic counter for music
COUNT_P     SCRATCH 1           ; Pattern counter
PAT         SCRATCH 1           ; Current pattern
MUS_FLAGS   SCRATCH 1           ; Music flags

SFXTBL      SCRATCH 8
SFXQ        SCRATCH 1
SFXBSY      SCRATCH 1
SFXSTMP     SCRATCH 1           ; extra state for saucer slide-whistle SFX

MUXOK       SCRATCH 1           ; Flag:  Ok to run UPMUX in ENGINE2

SCORE       SCRATCH 2           ; 16-bit score
PSCOR       SCRATCH 2           ; Peak score this game
TOPSCO      SCRATCH 16          ; Top scores for all 8 courses.

PSG0        EQU     $1F0 ;-$1FD ; PSG base address (master component)
PSG1        EQU     $0F0 ;-$0FD ; PSG base address (ECS)
CTRL0       EQU     $1FE        ; Right hand controller
CTRL1       EQU     $1FF        ; Left hand controller

;; ======================================================================== ;;
;;  SYSTEM (16-bit) MEMORY                                                  ;;
;; ======================================================================== ;;
.SPSTART16  SET     .SYSMEM
SDAT        SYSTEM  24          ; Shadow copy of STIC regs
SPXYV       SYSTEM  24          ; X/Y velocity for 12 sprites
SPXYP       SYSTEM  24          ; Sprite X/Y position, 8Q8
.SPSTOP16   SET     .SYSMEM

SPXY1       EQU     SPXYP       ; Offset into SPXYP table for Group 1
SPXY2       EQU     SPXYP + 5*2 ; Offset into SPXYP table for Group 2

RCIDX       SYSTEM  1           ; Rock/crater/spawn index

GGB0        SYSTEM  1           ; good-guy bullet 0
GGB1        SYSTEM  1           ; good-guy bullet 1
GGB2        SYSTEM  1           ; good-guy bullet 2
MGOFS       SYSTEM  1           ; Mid-ground graphics offset in GRAM
GPHASE      SYSTEM  1           ; ground scroll phase
MPHASE      SYSTEM  1           ; midmntn scroll phase
TPHASE      SYSTEM  1           ; topmntn scroll phase
MPTR        SYSTEM  1           ; mountain gfx ROM pointer
WPTR        SYSTEM  1           ; wheel gfx ROM pointer
RPTR        SYSTEM  1           ; rock/crater gfx ROM pointer
JHGT        SYSTEM  1           ; Current jump height (0 == on ground)
MGRAM       SYSTEM  1           ; GRAM address for mountain data

SONG        SYSTEM  1           ; Tracker variables
POS_A       SYSTEM  1
POS_B       SYSTEM  1
POS_C       SYSTEM  1

SDATP       SYSTEM  1

STACK       SYSTEM  20

BGTTMP      EQU     $35E        ; Temporary variable used by BGT routines
RSEED       EQU     $35F

GROM        EQU     $3000
GRAM        EQU     $3800
ISRRET      EQU     $1014


;; ------------------------------------------------------------------------ ;;
;;  Magic memory locations in ECS                                           ;;
;; ------------------------------------------------------------------------ ;;
ECSOK       EQU     $4040       ; flag saying whether extra features exist.

;; ------------------------------------------------------------------------ ;;
;;  GRAM layout in-game                                                     ;;
;;      00              Space character                                     ;;
;;      01 - 07         "Joseph Zbiciak" graphic                            ;;
;;      03 - 04         "Time" graphic                                      ;;
;;      05 - 07         "Caution" graphic                                   ;;
;;      08 - 0F         Middle "mountain" graphics (8 cards)                ;;
;;      10 - 19         Numeric digits (10 cards)                           ;;
;;      1A              Circle-C copyright symbol                           ;;
;;      1A              "Pt" graphic                                        ;;
;;      1B              Ground terrain (1 cards)                            ;;
;;      21              Creep #1 (orange ship)                              ;;
;;      22              Creep #2 (blue ship)                                ;;
;;      23              Creep #3 (white spinner)                            ;;
;;      24              Creep missle                                        ;;
;;      25              Buggy vert missle                                   ;;
;;      26              Buggy horiz missle                                  ;;
;;      27              Buggy body                                          ;;
;;      28 - 29         Buggy wheels/guns (2 cards)                         ;;
;;      2A              Solid ground-piece                                  ;;
;;      2B              Creep crater-blaster missle                         ;;
;;      2C - 37         Rock / Crater graphics (12 cards)                   ;;
;;      38 - 3F         Top "mountain" graphics (8 cards)                   ;;
;; ------------------------------------------------------------------------ ;;
TCARD       EQU     $38
CCARD       EQU     $08
MCARD       EQU     $08
RCARD       EQU     $2C
GCARD       EQU     $1B
HBCARD      EQU     $1C
BCARD       EQU     $27
WCARD       EQU     $28
SCARD       EQU     $23
TMCARD      EQU     $04
PTCARD      EQU     $1A

TOPGR       EQU     GRAM + TCARD * 8        ; Top mountains
MIDGR       EQU     GRAM + MCARD * 8        ; Middle mountains
RGRAM       EQU     GRAM + RCARD * 8        ; Rock / Crater
GGRAM       EQU     GRAM + GCARD * 8        ; Ground terrain
BGRAM       EQU     GRAM + BCARD * 8        ; Buggy body
WGRAM       EQU     GRAM + WCARD * 8 + 5    ; Buggy wheels
HBGRAM      EQU     GRAM + HBCARD* 8 + 3    ; Horizontal bullet
SGRAM       EQU     GRAM + SCARD * 8        ; Spinner

TMCARDx     EQU     $800 + TMCARD * 8       ; "Time" graphic
PTCARDx     EQU     $800 + PTCARD * 8       ; "Pt" graphic
HBCARDx     EQU     HBCARD*8 + X_BLK + $0800
LMPCARDx    EQU     RCARD*8 + X_TITL + $0800
RCARDx      EQU     RCARD*8 + X_ROCK + $0800 + $8000
RCARD2x     EQU     (RCARD + 2)*8 + X_ROCK + $0800 + $8000
GCARDx      EQU     GCARD*8       + X_GRND + $0800

TROW_n      EQU     3
CROW_n      EQU     6
MROW_n      EQU     7
GROW_n      EQU     8
TROW_p      EQU     TROW_n * 8
CROW_p      EQU     CROW_n * 8
MROW_p      EQU     MROW_n * 8
GROW_p      EQU     GROW_n * 8
TROW        EQU     $200 + TROW_n*20
CROW        EQU     $200 + CROW_n*20
MROW        EQU     $200 + MROW_n*20
GROW        EQU     $200 + GROW_n*20

STROW1      EQU     0*20 + $200
STROW2      EQU     7*20 + $200
RKROW       EQU     1*20 + $200


;; ======================================================================== ;;
;;  FONT AND DATA                                                           ;;
;; ======================================================================== ;;

    IF 0
            ; Temporary scratch memory
            ORG     $C100, $C100, "+RW"
SNDSTRM     RMB     8           ; Sound stream table
;STACK       RMB     128         ; For now, for debugging purposes
STKDEEP     RMB     1
    ENDI

    IF (DEFINED DOIDLEHST) <> 0
            ORG     $CE00, $CE00, "+RW"
IDLEHST     RMB     256
    ENDI

            ORG     $D000
_SPATBL     EQU $
            INCLUDE "gfx/spatbl.asm"
_SPATBL.size EQU $ - _SPATBL


_SPAWN      EQU $
            INCLUDE "bg/bgmpind.asm"
            INCLUDE "world/spawns.asm"
_SPAWN.size EQU $ - _SPAWN

            INCLUDE "gfx/rcsdata.asm"

_WORLD      EQU $
            INCLUDE "world/world.asm"
_WORLD.size EQU $ - _WORLD

_OS2        EQU $
            INCLUDE "util/initmem.asm"
_OS2.size   EQU $ - _OS2

CKSUM       DECLE   0                   ; checksum

        IF ($ < $D000) OR ($ > $E000)
            ERR     "D000 overflow"
        ENDI

_D000.end   EQU     $

            LISTING "off"
            REPEAT  $E000 - $
            DECLE   $FFFF
            ENDR
            LISTING "prev"

            ORG     $F000

_GFX        EQU $
            INCLUDE "gfx/topmount.asm"
            INCLUDE "gfx/midmount.asm"
            INCLUDE "gfx/midcity1.asm"
            INCLUDE "gfx/midcity2.asm"
            INCLUDE "gfx/midcity3.asm"
            INCLUDE "gfx/midcity4.asm"
            INCLUDE "gfx/rockbg.asm"
            INCLUDE "gfx/rockcrat.asm"
            INCLUDE "gfx/spin1.asm"     ; \_ must be adjacent
            INCLUDE "gfx/spin2.asm"     ; /
            INCLUDE "gfx/title.asm"
            INCLUDE "gfx/hut.asm"
            INCLUDE "gfx/ground.asm"
            INCLUDE "gfx/wheels.asm"
_GFX.size   EQU $ - _GFX

_FONT       EQU $
            INCLUDE "genasm/font.asm"
            INCLUDE "genasm/joefnt.asm"
            INCLUDE "genasm/creepfnt.asm"
            INCLUDE "genasm/creep2.asm"
            INCLUDE "genasm/creep3.asm"
            INCLUDE "genasm/creep4.asm"
_FONT.size  EQU $ - _FONT



_SFX        EQU $
            INCLUDE "snd/sfx.asm"
            INCLUDE "snd/music.asm"
_SFX.size   EQU $ - _SFX

_SCTBL      EQU $
            INCLUDE "genasm/sctbl.asm"
_SCTBL.size EQU $ - _SCTBL

_POW10      EQU $
            INCLUDE "util/pow10.asm"
_POW10.size EQU $ - _POW10


        IF ($ < $F000) OR ($ > $10000)
            ERR     "F000 overflow"
        ENDI

_F000.end   EQU     $

            LISTING "off"
            REPEAT  $10000 - $
            DECLE   $FFFF
            ENDR
            LISTING "prev"

;; ======================================================================== ;;
;;  ROM HEADER                                                              ;;
;; ======================================================================== ;;
            ORG     $5000       ; Standard Mattel cartridge memory map
_TOPLEV     EQU $
;; ------------------------------------------------------------------------ ;;
ROMHDR:     WORD    $0000       ; RTAB (ignored)
            DECLE   $01,$00     ; Movable object data (ignored)
            WORD    START       ; Program start address (ignored)
            WORD    $0000       ; Background graphics
            WORD    ROMHDR + 2  ; Card table -- stored above in header. :-)
            WORD    TITLE       ; Title string.

            DECLE   $3C0        ; run title code, clicks off, INTY2 on, no ECS
;           DECLE   $00         ; -> to STIC $32
;           DECLE   $00         ; 0 = color stack, 1 = f/b mode
;           DECLE   0, 0, 0, 0  ; color stack elements 1 - 4
;           DECLE   $00         ; border color
;; ------------------------------------------------------------------------ ;;
_TOPLEV.size EQU $ - _TOPLEV


;;==========================================================================;;
;;  MAJOR SUBSYSTEMS AND SUPPORT CODE                                       ;;
;;==========================================================================;;

_BGMP       EQU $
            INCLUDE "bg/bgthink.asm"
            INCLUDE "bg/bgsaucer.asm"
            INCLUDE "bg/bgfollow.asm"
_BGMP.size  EQU $ - _BGMP

_ENG1       EQU     $
            INCLUDE "engine/engine1.asm"
_ENG1.size  EQU     $ - _ENG1

_ENG2       EQU     $
            INCLUDE "engine/engine2.asm"
            INCLUDE "engine/runeng.asm"
            INCLUDE "engine/tictsk.asm"
            INCLUDE "engine/tank.asm"
_ENG2.size  EQU     $ - _ENG2

_BGENG      EQU     $
            INCLUDE "bg/bgengine.asm"
_BGENG.size EQU     $ - _BGENG

_GAME       EQU     $
            INCLUDE "game/names.asm"
            INCLUDE "game/data.asm"
    IF (DEFINED OLDMENU) = 0
            INCLUDE "game/mission.asm"
    ELSE
            INCLUDE "game/menu.asm"
    ENDI
            INCLUDE "game/ckpoint.asm"
            INCLUDE "game/gameloop.asm"
            INCLUDE "game/level.asm"
;           INCLUDE "game/title.asm"
            INCLUDE "game/gameover.asm"
            INCLUDE "game/score.asm"
_GAME.size  EQU     $ - _GAME

_SENG       EQU     $
            INCLUDE "engine/sfxeng.asm"
            INCLUDE "engine/tracker.asm"
_SENG.size  EQU     $ - _SENG

_OS         EQU     $
            INCLUDE "os/main_os.asm"
            INCLUDE "os/rand.asm"
            INCLUDE "os/setisr.asm"
            INCLUDE "os/wnk.asm"
            INCLUDE "util/p16.asm"
;           INCLUDE "util/prnum32.asm"
            INCLUDE "util/prnum16.asm"
            INCLUDE "util/fillmem.asm"
;           INCLUDE "util/hex16.asm"
            INCLUDE "util/menuinp.asm"
            INCLUDE "misc/shltbl.asm"
            INCLUDE "os/debounce.asm"

            EMIT_CST8
            EMIT_CST16
_OS.size    EQU     $ - _OS

_5000.end   EQU     $

        IF ($ < $5000) OR ($ > $7000)
            ERR     "5000 overflow"
        ENDI

            LISTING "off"
            REPEAT  $7000 - $
            DECLE   $FFFF
            ENDR
            LISTING "prev"

;* ======================================================================== *;
;*  This program is free software; you can redistribute it and/or modify    *;
;*  it under the terms of the GNU General Public License as published by    *;
;*  the Free Software Foundation; either version 2 of the License, or       *;
;*  (at your option) any later version.                                     *;
;*                                                                          *;
;*  This program is distributed in the hope that it will be useful,         *;
;*  but WITHOUT ANY WARRANTY; without even the implied warranty of          *;
;*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       *;
;*  General Public License for more details.                                *;
;*                                                                          *;
;*  You should have received a copy of the GNU General Public License       *;
;*  along with this program; if not, write to the Free Software             *;
;*  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.               *;
;* ======================================================================== *;
;*                   Copyright (c) 2006, Joseph Zbiciak                     *;
;* ======================================================================== *;
