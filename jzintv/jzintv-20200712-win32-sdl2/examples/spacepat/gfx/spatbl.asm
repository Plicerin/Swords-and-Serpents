;;==========================================================================;;
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; MOB Attribute Tables, Buggy Collision Tables                             ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  SPENT:  This macro takes several arguments to construct a sprite        ;;
;;          attribute entry.                                                ;;
;;                                                                          ;;
;;  SPANI:  Same as SPENT, but also specifies animation parameters.         ;;
;;                                                                          ;;
;;      lbl     Label to assign SPAT entry.  Becomes SPATBL.lbl             ;;
;;      intr    MOB interaction:  One of na, intr                           ;;
;;      xsiz    X magnification:  One of na, xsiz                           ;;
;;      xofs    X offset.  Small integer.                                   ;;
;;      yres    Y height.         One of na, yres                           ;;
;;      ysiz    Y magnification:  One of na, siz2, siz4                     ;;
;;      xmir    X mirroring:      One of na, xmir                           ;;
;;      ymir    Y mirroring:      One of na, ymir                           ;;
;;      yofs    Y offset.  Small integer.                                   ;;
;;      color   Color:            One of X_BLK thru X_PUR                   ;;
;;      card    Integer $00 to $FF (GROM), $100 to $13F (GRAM).             ;;
;;      bw      Bounding box width                                          ;;
;;      bh      Bounding box height                                         ;;
;;                                                                          ;;
;;  SPANI only:                                                             ;;
;;      anim    Next SPAT in animation sequence.                            ;;
;;      rate    Animation rate:   One of 60, 30, 15, 0.                     ;;
;;                                                                          ;;
;;                                                                          ;;
;;  SPATBL entries are built primarily around the STIC's X/Y/A register     ;;
;;  structure, with a few extra things thrown in:                           ;;
;;                                                                          ;;
;;                                                                          ;;
;;  X Register:    Offset 0                                                 ;;
;;                                                                          ;;
;;    15   14   13  12  11   10   9    8   7   6   5   4   3   2   1    0   ;;
;;  +----+----+----+---+---+---+----+----+---+---+---+---+---+---+---+---+  ;;
;;  |      Bits 7:3 of     | X |VISB|INTR|        X Coordinate           |  ;;
;;  |    next anim frame   |SIZ|    |    |         (0 to 255)            |  ;;
;;  +----+----+----+---+---+---+----+----+---+---+---+---+---+---+---+---+  ;;
;;                                                                          ;;
;;  Y Register:    Offset 1                                                 ;;
;;                                                                          ;;
;;    15   14   13   12   11  10   9   8   7   6   5   4   3   2   1   0    ;;
;;  +----+----+----------+---+---+---+---+---+---+---+---+---+---+---+---+  ;;
;;  |Bits 2, 0| Bits 3:2 | Y | X | Y | Y | Y |       Y Coordinate        |  ;;
;;  |next anim|of ScorIdx|MIR|MIR|SZ4|SZ2|RES|        (0 to 127)         |  ;;
;;  +----+----+----------+---+---+---+---+---+---+---+---+---+---+---+---+  ;;
;;                                                                          ;;
;;  A Register:    Offset 2                                                 ;;
;;                                                                          ;;
;;    15   14   13   12   11  10   9   8   7   6   5   4   3   2   1   0    ;;
;;  +----+----+----+----+----+---+---+---+---+---+---+---+---+---+---+---+  ;;
;;  |Animation|PRIO| FG |GRAM|  GRAM/GROM Card # (0 to 255)  |  FG Color |  ;;
;;  |  Rate   |    |bit3|GROM| (bits 9, 10 ignored for GRAM) |  Bits 0-2 |  ;;
;;  +----+----+----+----+----+---+---+---+---+---+---+---+---+---+---+---+  ;;
;;                           |ScorIdx|                                      ;;
;;                           |Bit 1:0|                                      ;;
;;                           +-------+                                      ;;
;;                                                                          ;;
;;  Bounding Box:  Offset 3                                                 ;;
;;    15                            8   7                              0    ;;
;;  +---------------------------------+----------------------------------+  ;;
;;  |            Object               |              Object              |  ;;
;;  |            Height               |              Width               |  ;;
;;  +---------------------------------+----------------------------------+  ;;
;;                                                                          ;;
;;                                                                          ;;
;;  The animation rate is encoded as a 2 bit number:                        ;;
;;                                                                          ;;
;;      00      None                                                        ;;
;;      01      8 Hz                                                        ;;
;;      11      15 Hz                                                       ;;
;;      10      30 Hz                                                       ;;
;;                                                                          ;;
;;  The animation frame number refers directly to a SPATBL entry.           ;;
;;                                                                          ;;
;;  The ScorIdx value gives a 4 bit number indicating what score is         ;;
;;  associated with the SPATBL entry if any.  Notice that bits 1:0 of       ;;
;;  the ScorIdx overlap the GRAM/GROM card number.  Most SPATBL entries     ;;
;;  point to GRAM entries, so these bits go unused.  Only three objects     ;;
;;  use GROM entries:  The hut, stalactites and land-mines.  Only           ;;
;;  stalactites have a non-zero score.                                      ;;
;;                                                                          ;;
;;  To make stalactites work, they must use a ScorIdx whose bits 1 and 0    ;;
;;  match bits 7 and 6 of the card number.  Thus stalactites must have a    ;;
;;  ScorIdx of the form xx10.                                               ;;
;;                                                                          ;;
;; ======================================================================== ;;

MACRO spidx(lbl)
    ((%lbl% - SPATBL) + 1)
ENDM

MACRO SPENT lbl,intr,xsiz,xofs,yres,ysiz,xmir,ymir,yofs,color,card,bw,bh,sc
@@_%lbl%:
 DECLE _X.%intr% + _X.visb + _X.%xsiz% + (%xofs%)
 DECLE _Y.%yres% + _Y.%ysiz% + _Y.%ymir% + _Y.%xmir% + (%yofs%)+SCORIDX.hi%sc%
 DECLE X_%color% + 8*%card% + SCORIDX.lo%sc%
 DECLE (%bh%) SHL 8 + %bw%
@@%lbl%     EQU     spidx(@@_%lbl%)
ENDM

MACRO SPANI lbl,intr,xsiz,xofs,yres,ysiz,xmir,ymir,yofs,color,card,bw,bh,sc,an,rate
@@_%lbl%:
 DECLE _X.%intr% + _X.visb + _X.%xsiz% + (%xofs%) + ((spidx(@@_%an%) AND $F8) SHL 8)
 DECLE _Y.%yres% + _Y.%ysiz% + _Y.%ymir% + _Y.%xmir% + (%yofs%)+ ((spidx(@@_%an%) AND $4) SHL 13) + ((spidx(@@_%an%) AND 1) SHL 14)+SCORIDX.hi%sc%
 DECLE X_%color% + 8*%card% + ANI.%rate%+SCORIDX.lo%sc%
 DECLE %bh% * 256 + %bw%
@@%lbl%     EQU     spidx(@@_%lbl%)
ENDM

ANI     PROC
@@30    EQU     2 SHL 14
@@15    EQU     3 SHL 14
@@8     EQU     1 SHL 14
@@0     EQU     0 SHL 14
        ENDP

MACRO   scoridx(l, v)
SCORIDX.lo%l% EQU ((%v%) AND $3) SHL 9
SCORIDX.hi%l% EQU ((%v%) AND $C) SHL 10
ENDM

scoridx(0000, $0)
scoridx(0350, $1)
scoridx(0500, $2)
scoridx(0750, $3)
scoridx(1000, $4)
scoridx(1250, $5)
scoridx(1450, $6)
scoridx(2000, $7)
scoridx(2250, $8)
scoridx(3750, $9)
scoridx(4500, $A)
scoridx(6250, $B)
scoridx(rnd0, $C)   ; 3000/6000/5000/8000   (plant)
scoridx(rnd1, $D)   ; 5000/8000/7500/10000  (follower)
scoridx(stal, $C)   ; 2500/5000/7500/10000  (stalactite) (really $E)
scoridx(rnd3, $F)   ; ?


;; ======================================================================== ;;
;;  SCORTBL -- Lookup table associated with ScorIdx 0000 .. 1011.           ;;
;; ======================================================================== ;;
SCORTBL PROC
        DECLE   pack(Score(   0), Score( 350))
        DECLE   pack(Score( 500), Score( 750))
        DECLE   pack(Score(1000), Score(1250))
        DECLE   pack(Score(1450), Score(2000))
        DECLE   pack(Score(2250), Score(3750))
        DECLE   pack(Score(4500), Score(6250))
        ENDP

;; ======================================================================== ;;
;;  MOVING OBJECT ATTRIBUTE TABLE                                           ;;
;; ======================================================================== ;;
SPATBL  PROC
@@_done EQU     SPATBL-1
@@0     EQU     0

;; Saucers must be at head of table.

;; Crater-making Saucers (must be together in one spot for BGSAUCER).
SPENT wht0, intr,xsiz,-5, na  ,siz4,na  ,na  ,-4,WHT,$123,$0A,$0A,2000
SPENT wht1, intr,xsiz,-8, na  ,siz2,na  ,na  ,+2,GRY,$123,$10,$0A,2000
SPENT wht2, intr,na  , 0, na  ,siz2,na  ,na  ,+4,WHT,$123,$07,$08,2000
SPENT wht3, intr,na  , 0, na  ,siz1,na  ,na  ,+4,CYN,$123,$07,$08,2250

;; Moon Saucers:  Pink, Blue
SPENT pnk0, intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,PNK,$121,$10,$06,1250
SPENT blu0, intr,xsiz,-8, na  ,siz1,na  ,na  ,+4,BLU,$122,$10,$05,1250

;; Mars Saucers:  Cyan, Yellow, Grey
SPANI pnk1, intr,xsiz,-8, na  ,siz1,na  ,na  ,+4,YGR,$121,$10,$08,1250,pnk1b,30
SPANI pnk1b,intr,xsiz,-8, na  ,siz1,na  ,na  ,+4,GRN,$11A,$10,$08,1250,pnk1c,30
SPANI pnk1c,intr,xsiz,-8, na  ,siz1,xmir,na  ,+4,YGR,$11A,$10,$08,1250,pnk1d,30
SPANI pnk1d,intr,xsiz,-8, na  ,siz1,xmir,na  ,+4,GRN,$121,$10,$08,1250,pnk1 ,30
SPENT blu1, intr,xsiz,-8, na  ,siz1,na  ,na  ,+4,YEL,$122,$10,$05,1250
SPENT blu1a,intr,xsiz,-8, na  ,siz1,na  ,na  ,+4,TAN,$122,$10,$05,1250

;; Pluto Saucers
SPANI pnk2 ,intr,na  , 0, na  ,siz1,na  ,na  ,+4,PUR,$121,$08,$08,1250,pnk2b,8
SPANI pnk2b,intr,na  , 0, na  ,siz1,xmir,na  ,+4,PUR,$121,$08,$08,1250,pnk2 ,8
SPANI blu2, intr,na  , 0, na  ,siz1,na  ,na  ,+4,RED,$103,$08,$05,1250,blu2b,30
SPANI blu2b,intr,na  , 0, na  ,siz1,na  ,na  ,+4,RED,$11A,$08,$05,1250,blu2c,30
SPANI blu2c,intr,na  , 0, na  ,siz1,xmir,na  ,+4,RED,$11A,$08,$05,1250,blu2d,30
SPANI blu2d,intr,na  , 0, na  ,siz1,xmir,na  ,+4,RED,$103,$08,$05,1250,blu2 ,30

;; Mercury Saucers
SPANI pnk3, intr,na  , 0, na  ,siz1,na  ,na  ,+4,RED,$121,$08,$06,1450,pnk3b,8
SPANI pnk3b,intr,na  , 0, na  ,siz1,xmir,na  ,+4,RED,$121,$08,$06,1450,pnk3 ,8
SPANI pnk3c,intr,na  , 0, na  ,siz1,na  ,na  ,+4,ORG,$121,$08,$06,1450,pnk3d,8
SPANI pnk3d,intr,na  , 0, na  ,siz1,xmir,na  ,+4,ORG,$121,$08,$06,1450,pnk3c,8
SPENT blu3, intr,na  , 0, na  ,siz1,na  ,na  ,+4,WHT,$11A,$08,$05,1450
SPENT blu3c,intr,na  , 0, na  ,siz1,na  ,na  ,+4,YEL,$11A,$08,$05,1450
S_end   EQU     SPATBL.blu3c    ; Last saucer

;; Turrets
SPENT tur0, intr,na  , 0, na  ,siz2,na  ,na  ,+2,DGR,$120,$08,$08,2000
SPENT tur1, intr,na  , 0, na  ,siz2,na  ,na  ,+2,GRN,$120,$08,$08,2000
SPENT tur2, intr,na  , 0, na  ,siz2,na  ,na  ,+2,BRN,$120,$08,$08,2000
SPENT tur3, intr,na  , 0, na  ,siz2,na  ,na  ,+2,BLK,$120,$08,$08,2250

;; Boulder (four frames)
SPANI bld0a,intr,na  , 0, na  ,siz2,na  ,na  ,+2,BRN,$122,$08,$08,0500,bld0b,8
SPANI bld0b,intr,na  , 0, na  ,siz2,xmir,na  ,+2,BRN,$122,$08,$08,0500,bld0c,8
SPANI bld0c,intr,na  , 0, na  ,siz2,xmir,ymir,+2,BRN,$122,$08,$08,0500,bld0d,8
SPANI bld0d,intr,na  , 0, na  ,siz2,na  ,ymir,+2,BRN,$122,$08,$08,0500,bld0a,8

;; Followers (2 MOBs each)
SPENT fol0a,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,RED,$11E,$10,$08,rnd1
SPENT fol1a,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,BLU,$11E,$10,$08,rnd1
SPENT fol2a,intr,xsiz,-8, na  ,siz2,xmir,na  ,+0,DGR,$11E,$10,$08,rnd1
SPENT fol3a,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,PUR,$11E,$10,$08,rnd1

SPENT fol0b,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,BLU,$11D,$10,$08,0000
SPENT fol1b,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,YEL,$11D,$10,$08,0000
SPENT fol2b,intr,xsiz,-8, na  ,siz2,xmir,na  ,+0,WHT,$11D,$10,$08,0000
SPENT fol3b,intr,xsiz,-8, na  ,siz2,na  ,na  ,+0,BLK,$11D,$10,$08,0000

;; Land Mines
SPENT lmna, intr,xsiz,-1, na  ,siz2,na  ,na  ,+1,WHT,$00E,$04,$02,0000
SPENT lmnb, intr,xsiz,-1, na  ,siz2,na  ,na  ,+1,RED,$00E,$04,$02,0000

;; Space plant
SPENT plta, intr,na  ,+0, na  ,siz2,na  ,na  ,+0,DGR,$101,$08,$07,rnd0
SPENT pltb, intr,na  ,+0, na  ,siz2,na  ,na  ,+0,DGR,$102,$08,$09,rnd0
SPENT pltc, intr,xsiz,-8, na  ,siz4,na  ,na  ,-8,DGR,$101,$10,$0E,rnd0
SPENT pltd, intr,xsiz,-8, na  ,siz4,na  ,na  ,-8,DGR,$102,$10,$12,rnd0

;; Bullets:  Crater, Bomb, Vert tank, Gun turret
SPANI b1,   intr,na  ,+0, na  ,siz2,na  ,na  ,+0,WHT,$124,$03,$03,0350,b1b ,15
SPANI b1b,  intr,na  ,+0, na  ,siz2,na  ,na  ,+0,RED,$124,$03,$03,0350,b1  ,15
SPENT b2,   intr,na  ,+0, na  ,siz2,na  ,na  ,+0,WHT,$126,$05,$05,0000
SPENT b3,   na  ,na  ,+0, na  ,siz2,na  ,na  ,+0,WHT,$125,$00,$00,0000
SPENT b4,   intr,na  ,-2, na  ,na  ,na  ,na  ,+3,BLK,$00D,$0A,$08,0000
SPENT b5,   intr,na  ,+0, na  ,na  ,na  ,na  ,+4,BLK,$00D,$08,$08,0000

;; Explosion frames ... large/medium/small
SPANI x1,   na  ,xsiz,-8, na  ,siz2,na  ,na  ,+0,CYN,$11F,$00,$00,0000,x2  ,15
SPANI x2,   na  ,xsiz,-8, na  ,siz1,na  ,na  ,+2,YGR,$11F,$00,$00,0000,x3  ,15
SPANI x3,   na  ,na  ,-4, na  ,siz1,na  ,na  ,+2,RED,$11F,$00,$00,0000,done,15

;; Stalactites
SPENT stal, intr,na  ,-4, na  ,siz2,na  ,na  ,+0,DGR,$092,$08,$08,stal
SPANI stala,intr,na  ,-3, na  ,siz2,na  ,na  ,+1,DGR,$092,$08,$08,stal,stalb,30
SPANI stalb,intr,na  ,-4, na  ,siz2,na  ,na  ,+1,DGR,$092,$08,$08,stal,stala,30
SPENT stalf,intr,na  ,-4, na  ,siz2,na  ,na  ,+0,DGR+_A.prio,$092,$08,$08,stal

;; Hut
SPENT hut0, na,  na, -$C, na  ,siz2,na  ,na, $48,WHT,$12C,    0,  0,0000
SPENT hut1, na,  na, -$4, na  ,siz2,na  ,na, $48,LBL,$12D,    0,  0,0000
SPENT hut2, na,  na, -$5, na  ,siz2,na  ,na, $48,WHT, 159,    0,  0,0000
SPENT hut3, na,  na, -$A, na  ,siz4,na  ,na, $40,BLK,$12E,    0,  0,0000

;; crat6
SPENT crat6,na,  xsiz, 0, na  ,siz2,na  ,na  , 0,GRN,95, 0, 0,0000
        ENDP


;; ======================================================================== ;;
;;  SPRITE ATTRIBUTES for level marker.                                     ;;
;; ======================================================================== ;;
SPATLM  PROC
        DECLE   _X.visb, _Y.siz2 + GROW_p + 20, X_BLK
        ENDP

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

