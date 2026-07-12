;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2007, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;


;; ======================================================================== ;;
;;  SCROLL ENGINE                                                           ;;
;;                                                                          ;;
;;  ENGINE1                                                                 ;;
;;  Every tick we do the following prior to end of VBL period:              ;;
;;   -- Unconditionally update the sprites.                                 ;;
;;   -- Unconditionally update the ground, rock and crater GRAM entries.    ;;
;;   -- Unconditionally update the buggy wheel GRAM entries.                ;;
;;   -- Conditionally update the "middle" or "top" mountains.  Never do     ;;
;;      both, and round-robin if needed.                                    ;;
;;                                                                          ;;
;;  ENGINE2                                                                 ;;
;;  After that, we do the following (less time critical, but must happen    ;;
;;  well within 1/60th second frame time -- listed in order of criticality) ;;
;;   -- Move cards for ground, rocks, craters, bullets.                     ;;
;;   -- Update sfx                                                          ;;
;;   -- Update mountain position information for next frame.                ;;
;;   -- Update sprite positions for next frame.                             ;;
;;   -- Do "world calculations" for next frame.                             ;;
;;                                                                          ;;
;;  VARIABLES AND SYMBOLS                                                   ;;
;;   RPTR     -- Rock/Crater gfx data pointer                               ;;
;;   MPTR     -- Mountain gfx data pointer (zero if no update)              ;;
;;   GGRAM    -- GRAM address for ground data (constant).                   ;;
;;   RGRAM    -- GRAM address for rock/crater data (constant).              ;;
;;   MGRAM    -- GRAM address for mountain data (variable).                 ;;
;;   SDAT     -- Array of "shadow registers" for sprite data in 16-bit RAM  ;;
;;                                                                          ;;
;; ======================================================================== ;;

;;==========================================================================;;
;;  ENGINE2 -- This is somewhat less time-critical stuff.  Here, we first   ;;
;;             move background cards as necessary, and then calculate our   ;;
;;             state for the next frame.                                    ;;
;;==========================================================================;;
ENGINE2;PROC
        CLRR    R0                  ;   6
        MVO     R0,     EBSY        ;  10

    IF (DEFINED DODEAD) = 0
        MVI     MOBHIT, R0
        TSTR    R0
        BEQ     E2.died
    ENDI
        ;;------------------------------------------------------------------;;
        ;;  Calculate the next frame's "state of the world."                ;;
        ;;------------------------------------------------------------------;;
        ICALL   upbgp               ; 943 Update buggy vel and ground phase

        ;;------------------------------------------------------------------;;
        ;;  Update sound effects and music                                  ;;
        ;;------------------------------------------------------------------;;
        CALL    UPSND               ;   ?

        MVI     EMODE,  R0          ;  10 \
        MVII    #E2.spdone,  R5     ;   8  |   If EMODE==0, don't display 
        DECR    R0                  ;   6  |__ sprites.  Return to spdone.
        BMI     CLRSP               ; 7/9  |   If EMODE==2 do the title-screen
        MVII    #E2.bgdone,  R5     ;   8  |   specific stuff.  Return to
        BNEQ    TTLSP               ; 7/9 /    E2.bgdone.
                                    ;----
                                    ;  38 (fall thru)
                                    ;  16 (carried forward)
                                    ; 943 (carried forward)
                                    ;----
                                    ; 997
        CALL    UPBSP               ; 246 Update moon-buggy sprites
        ICALL   upspp               ;1207 Update sprite positions
        CALL    UPSPA               ; 379 Update gp1/gp2 allocations.
                                    ;----
                                    ;2829
E2.muxonly:
        CLRR    R0                  ;   6
        CMP     MUXOK,  R0          ;  10
        BEQ     E2.spdone           ; 7/9
        MVO     R0,     MUXOK       ;  11
                                    ;----
                                    ;  34
        CALL    UPMUX               ;1329 Update sprite->MOB multiplexing
                                    ;2829 (carried forward)
                                    ;----
                                    ;4158
                                    ; 
E2.spdone:
        ;; ---------------------------------------------------------------- ;;
        ;;  In order to reduce peak loading, we always do cues two pixel    ;;
        ;;  scrolls after a card boundary.  This is because card boundaries ;;
        ;;  represent a burst of activity (two calls to COPYROW aren't      ;;
        ;;  exactly cheap).                                                 ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     PPGPHA, R3
        ANDI    #$7,    R3
        CMPI    #$2,    R3 
        BNEQ    @@nocue     

        MVI     CUENUM, R3
        DECR    R3
        BMI     @@nocue

        CMPI    #$80,   R3
        BC      @@doexit

        MVII    #@@donecue, R5
        B       BGSPAWN
@@doexit:
        CALL    BGDOEXIT
@@donecue:
        CLRR    R3
        MVO     R3,     CUENUM
@@nocue:

    IF (DEFINED DODEAD) = 0
        MVI     MOBHIT, R0
        TSTR    R0
        BEQ     E2.died
    ENDI

        ;; ---------------------------------------------------------------- ;;
        ;;  Now execute either the even or odd frame activities.  On even   ;;
        ;;  frames, we update bad-guy programs 0, 2, 4.  We also check for  ;;
        ;;  bad guys that have moved off-screen and update the timer clock. ;;
        ;;  On odd frames, we update bad-guy programs 1 and 3, and also     ;;
        ;;  check the good-guy and bad guy bullets.                         ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     BGFLAG, R0
        XORI    #1,     R0
        MVO     R0,     BGFLAG
        SARC    R0
        BNC     @@even

@@odd   
        ICALL   ckggb           ; Check good guys' bullets.
        ICALL   ckbgb           ; Check bad guys' bullets.
        MVII    #E2.bgdone, R5
        B       UPBGM.1         ; update odd bad-guys' motion programs
@@even
        CALL    TICTSK
        ICALL   upani           ; update animations (moved here from eng 2)
        CALL    UPBGM.0         ; update even bad-guys' motion programs
        ICALL   ckbgp           ; cull bad guys that have left the screen

E2.bgdone:



        ;;------------------------------------------------------------------;;
        ;;  Twinkle, twinkle little star, how I wonder what you are...      ;;
        ;;------------------------------------------------------------------;;
        MVI     DOENG,  R0
        TSTR    R0
        BNEQ    ENGINE2_RET     ; get outta here extra fast
;       MVI     EMODE,  R0
;       TSTR    R0
;       BEQ     E2.notwinkle
        MVI     INCITY, R0
        CMPI    #2,     R0
        BGE     E2.notwinkle

        MVII    #ENGINE2_RET, R5
        B       TWINKLE

E2.notwinkle
        MVII    #ENGINE2_RET, R5
        B       RAND
E2.died
        MVII    #1,     R0
        MVO     R0,     DNENG
        B       ENGINE2_RET

;       ENDP
        

;;==========================================================================;;
;;  RSGGB     Reset Good Guy's bullets.                                     ;;
;;==========================================================================;;
RSGGB   PROC
        PSHR    R0
        CLRR    R0                  ; \
        MVO     R0,     SPAT2+5     ;  |- Disable Sprites for GGBs 1 & 2
        MVO     R0,     SPAT2+6     ; /
        MVO     R0,     HBDATA      ;
        MVO     R0,     HBCOL1      ; \
        INCR    R0                  ;  |_ Disable horizontal bullet
        MVO     R0,     HBCNT       ;  |
        MVO     R0,     HBCNT2      ; /
        MVII    #$6060, R0          ; \
        MVO     R0,     GGB0        ;  |_ Move GGBs off screen.
        MVO     R0,     GGB1        ;  |
        MVO     R0,     GGB2        ; /
        PULR    R0
        JR      R5
        ENDP

MACRO   jhp(a, b)
        (((%a% SHL 8) AND $FE00) OR (%b% AND $1FE) OR (%a% SHR 8))
ENDM

MACRO   jhr(a, b, c, d, e, f, g, h)
        jhp(%a%, %b%), jhp(%c%, %d%), jhp(%e%, %f%), jhp(%g%, %h%)
ENDM

;;==========================================================================;;
;;  MJHTBL   Minimum Jump Height Table.                                     ;;
;;==========================================================================;;
MJHTBL  PROC
        ;; Rock #1
        DECLE   jhp(  0,   0)                               ; Padding
        DECLE   jhr(  0,   0,   0,   0,   0,   0,   0,   0)  ; Padding
        DECLE   jhr(  0,  32,  64,  96, 128, 128, 160, 192)  ;  -8 thru -1
@@rock1 DECLE   jhr(192, 160, 160, 192, 192, 160, 160, 192)  ;   0 thru  7
        DECLE   jhr(192, 160, 128, 128,  96,  96,  96,  64)  ;   8 thru 15
        DECLE   jhr(  0,   0,   0,   0,   0,   0,   0,   0)  ;  16 thru 19
        ;; Rock #2
        DECLE   jhp(  0,   0)                               ; Padding
        DECLE   jhr(  0,  32,  96, 160, 192, 192, 224, 256)  ;  -8 thru -1
@@rock2 DECLE   jhr(256, 224, 224, 256, 256, 224, 224, 256)  ;   0 thru  7
        DECLE   jhr(256, 224, 192, 192, 160, 160, 160, 128)  ;   8 thru 15
        DECLE   jhr( 96,  32,   0,   0,   0,   0,   0,   0)  ;  16 thru 19
        ;; Rock #3
        DECLE   jhp(  0,   0)                               ; Padding
        DECLE   jhr(  0,  32,  96, 160, 192, 192, 224, 256)  ; -16 thru -9
        DECLE   jhr(256, 224, 224, 256, 256, 224, 224, 256)  ;  -8 thru -1
@@rock3 DECLE   jhr(256, 224, 192, 192, 192, 160, 160, 192)  ;   0 thru  7
        DECLE   jhr(192, 160, 128, 128,  96,  96,  96,  64)  ;   8 thru 15
        DECLE   jhr(  0,   0,   0,   0,   0,   0,   0,   0)  ;  16 thru 19
        ;; Crat #1
        DECLE   jhp(  0,   0)                               ; Padding
        DECLE   jhr(  0,   0,   0,   0,   4,   4,   4,   4)  ;  -8 thru -1
@@crat1 DECLE   jhr(  4,   4,   4,   4,   4,   4,   4,   4)  ;   0 thru  7
        DECLE   jhr(  4,   4,   4,   4,   4,   0,   0,   0)  ;   8 thru 15
        DECLE   jhr(  0,   0,   0,   0,   0,   0,   0,   0)  ;  16 thru 19
        ;; Crat #2
        DECLE   jhp(  0,   0)                               ; Padding
        DECLE   jhr(  0,   0,   0,   0,   4,   4,   4,   4)  ; -16 thru -9
        DECLE   jhr(  4,   4,   4,   4,   4,   4,   4,   4)  ;  -8 thru -1
@@crat2 DECLE   jhr(  4,   4,   4,   4,   4,   4,   4,   4)  ;   0 thru  7
        DECLE   jhr(  4,   4,   4,   4,   4,   0,   0,   0)  ;   8 thru 15
        DECLE   jhr(  0,   0,   0,   0,   0,   0,   0,   0)  ;  16 thru 19
        DECLE   jhp(  0,   0)                               ; Padding
        ENDP

MJHIDX  PROC
        DECLE   2*MJHTBL.rock1, 2*MJHTBL.rock1 - 8
        DECLE   2*MJHTBL.rock2, 2*MJHTBL.rock2 - 8
        DECLE   2*MJHTBL.rock3, 2*MJHTBL.rock3 - 8, 2*MJHTBL.rock3 - 16
        DECLE   2*MJHTBL.crat1, 2*MJHTBL.crat1 - 8
        DECLE   2*MJHTBL.crat2, 2*MJHTBL.crat2 - 8, 2*MJHTBL.crat2 - 16
        ENDP


;;==========================================================================;;
;;  HALTENGINE -- Utility function to shut things down.                     ;;
;;==========================================================================;;
HALTENGINE  PROC
            ;; ------------------------------------------------------------ ;;
            ;;  Halt all the MOBs.                                          ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #3,         R0          ;\__ Halt all updates in engine2
            MVO     R0,         EMODE       ;/   except sprite->MOB muxing.

;           B       SPINIT
            ENDP

;; ======================================================================== ;;
;;  SPINIT  -- Initialize the MOB data structures so things don't blow up.  ;;
;; ======================================================================== ;;
SPINIT      PROC
            MOVR    R5,     R2

            MVII    #.SPSTART8,             R4
            MVII    #.SPSTOP8 - .SPSTART8,  R1
            CALL    FILLZERO

            MVII    #.SPSTART16,             R4
            MVII    #.SPSTOP16 - .SPSTART16, R1
            MOVR    R2,     R5
            B       FILLZERO

            ENDP

;; ======================================================================== ;;
;;  ENGDONE                                                                 ;;
;;                                                                          ;;
;;  Cleanup "engine" ISR which disables all the MOBs and then switches to   ;;
;;  the miscellaneous ISR as the main ISR afterwards.  This is called to    ;;
;;  clean up after the main game engine ISR.                                ;;
;;                                                                          ;;
;; ======================================================================== ;;
ENGDONE     PROC
            MVO     R0,     $20
            CALL    CLRSP.1
            CALL    CLRSP

            SETISR  MISCISR

            B       MISCISR.1
            ENDP


;       INCLUDE "engine/ckbgb.asm"  ; Check bad-guy bullets
;       INCLUDE "engine/ckggb.asm"  ; Check good-guy bullets
;       INCLUDE "engine/ckbrc.asm"  ; Check buggy-rock collision
;       INCLUDE "engine/ckbgp.asm"  ; Check bad-guy position (culling)
;       INCLUDE "engine/upcrd.asm"  ; Update cards
        INCLUDE "engine/upmux.asm"  ; Update MOB muxing
        INCLUDE "engine/upspa.asm"  ; Update sprite allocations
;       INCLUDE "engine/upspp.asm"  ; Update sprite positions
        INCLUDE "engine/upbsp.asm"  ; Update buggy sprite 
;       INCLUDE "engine/upbgp.asm"  ; Update buggy/ground position
;       INCLUDE "engine/uphbp.asm"  ; Update horiz bullet position
;       INCLUDE "engine/upani.asm"  ; Update animation
        INCLUDE "engine/ttlsp.asm"  ; Title sprite updates
        INCLUDE "engine/clrsp.asm"  ; Clear sprites and update
        INCLUDE "engine/twinkle.asm"; Twinkle stars in the sky

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
;*                   Copyright (c) 2007, Joseph Zbiciak                     *;
;* ======================================================================== *;
