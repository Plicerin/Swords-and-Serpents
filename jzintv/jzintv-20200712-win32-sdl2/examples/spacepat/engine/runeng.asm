;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  RUNENG  Run the main game engine.                                       ;;
;;                                                                          ;;
;;  This function has two purposes:  Glue ENGINE1 to ENGINE2, and scan      ;;
;;  for controller inputs.  The hand controller scanner is very simplified  ;;
;;  and focused only on doing what's needed for the game.                   ;;
;; ======================================================================== ;;
RUNENG      PROC

            JSRD    R5,     INITMEM.0
            INIT    DOENG,  0
            INIT    DNENG,  0
            INIT    EBSY,   0
            INIT    SFXQ,   0
            INIT    MOBHIT, 1
            INIT    SDATP,  SDAT
            INIT_DONE

    IF (DEFINED SEEKKEYS) <> 0
            B       @@loop

@@waitnokey CALL    WAITNOKEY
    ENDI

            ;; ------------------------------------------------------------ ;;
            ;;  Main event loop:  Look for ENGINE2 requests and scan ctrls  ;;
            ;; ------------------------------------------------------------ ;;
@@loop:     
            DIS                             ; !!critical section!!
            MVI     DOENG,  R0              ; \
            DECR    R0                      ;  |- See if ENGINE1 ran
            BMI     @@idle                  ; /
            EIS
            MVO     R0,     DOENG           ; \__ Yes: Do engine 2.
            JE      ENGINE2                 ; /
ENGINE2_RET                                 ; ENGINE2 returns here.

@@idle:     EIS
            MVI     DNENG,  R2
            DECR    R2
            BPL     @@done       

@@not_done
            CALL    DEFSCORE            ; update deferred score

    IF 0
            CLRR    R1
            CMP     MPTR,   R1          ; \_ do top-score upd. only if no
            BNEQ    @@skiptss           ; /  mountain updates this frame

            CALL    UPTSS
@@skiptss:
    ENDI
            CALL    DBHC        ; Read debounced hand ctrlrs
            ; R0 = stable value
            ; R1 = delta bits
            ; R2 = suppressed bits

            MVI     EMODE,  R3
            DECR    R3
            BEQ     @@game_hand
;           BMI     @@what_hand

            ;; ------------------------------------------------------------ ;;
            ;;  Title screen:  Just wait for anything.                      ;;
            ;; ------------------------------------------------------------ ;;
@@title_hand:                               ; \
            TSTR    R0                      ;  |
            BNEQ    @@maybe_done            ;  |- Wait for keyup -> keydown
            MVO     R0,     TMP             ;  |
            B       @@loop                  ; /
@@maybe_done
            XOR     TMP,    R2
            BEQ     @@done
            B       @@loop

@@game_hand:
            ;; ------------------------------------------------------------ ;;
            ;;  Look for a pause request.                                   ;;
            ;; ------------------------------------------------------------ ;;
            CMPI    #$A5,   R0
            BEQ     @@pausing

    IF (DEFINED SEEKKEYS) <> 0
            ;; ------------------------------------------------------------ ;;
            ;;  Just during development                                     ;;
            ;; ------------------------------------------------------------ ;;
;           CMPR    R0,     R1
;           BNEQ    @@nodigit

            MVII    #@@waitnokey, R5
            CMPI    #$84,   R0
            BEQ     PRVLVL
            CMPI    #$44,   R0
            BEQ     RSTLVL
            CMPI    #$24,   R0
            BEQ     NXTLVL
            CMPI    #$48,   R0
            BNEQ    @@nodigit

            MVII    #2,     R2
            B       @@done
@@nodigit:
    ENDI


            ;; ------------------------------------------------------------ ;;
            ;;  Game DISC decoding                                          ;;
            ;; ------------------------------------------------------------ ;;
            MOVR    R0,         R3          ; \
            ANDI    #2,         R3          ;  |- Pushing right?
            BNEQ    @@go_fast               ; /

            MOVR    R0,         R3          ; \
            ANDI    #8,         R3          ;  |- Pushing left?
            BNEQ    @@go_slow               ; /

            MVII    #VMED,      R3          ; \
            B       @@set_vel               ;  |
@@go_slow   MVII    #VSLOW,     R3          ;  |- Set buggy velocity
            B       @@set_vel               ;  |
@@go_fast   MVII    #VFAST,     R3          ; /

@@set_vel   MVO     R3,         WANTVL

            ;; ------------------------------------------------------------ ;;
            ;;  Game ACTION decoding.  This is somewhat tricky due to       ;;
            ;;  the challenges of noisy controllers, and the aliasing that  ;;
            ;;  occurs between the three buttons.  ACTTBL contains the      ;;
            ;;  state machine that determines when we will issue jump and   ;;
            ;;  fire events, based on various transitions we might see.     ;;
            ;;                                                              ;;
            ;;  R0 contains the current stablized controller input.         ;;
            ;;  R2 contains the bits that changed since the last stable     ;;
            ;;     sample.                                                  ;;
            ;; ------------------------------------------------------------ ;;
            ANDI    #$E0,       R0          ; \
            ANDI    #$E0,       R2          ;  |_ Look for edges.
            CMPR    R0,         R2          ;  |
            BEQ     @@loop                  ; /  Don't decode if not an edge.
            MVII    #@@loop,    R5

            SLR     R0,         2
            SLR     R0,         2
            SLR     R0,         1
            ADDI    #ACTTBL,    R0          ; Index into ACTTBL based on new
            SLR     R2,         2
            SLR     R2,         2
            ADDI    #SHLTBL,    R2          ; Index into field based on prev

            MOVR    R0,         R1          ; Can't read @R0, so do @R1
            MVI@    R1,         R0          ; Get ACTTBL entry
            MOVR    R0,         R1          ; and duplicate it.

            AND@    R2,         R0          ; Non-zero means fire
            BNEQ    DOFIRE
            INCR    R2
            AND@    R2,         R1          ; Non-zero means jump.
            BNEQ    DOJUMP
            B       @@loop

            ;; ------------------------------------------------------------ ;;
            ;;  Exit out and let the top-level code have a stab.            ;;
            ;; ------------------------------------------------------------ ;;
@@done:     MVI     EMODE,      R0
            DECR    R0
            BNEQ    RUNENG_RET_TITLE
            B       RUNENG_RET_NORMAL

            ;; ------------------------------------------------------------ ;;
            ;;  Handle pausing.                                             ;;
            ;; ------------------------------------------------------------ ;;
@@pausing
            DIS

            SETISR  JRR5
            
            MVI     $1F8,       R1          ; \
            MVI     $0F8,       R3          ;  |
            MVII    #$3F,       R0          ;  |- Mute the music & sfx
            MVO     R0,         $1F8        ;  |
            MVO     R0,         $0F8        ; /

            JSRE    R5,         WAITKEY

            MVO     R1,         $1F8        ; \__ Unmute music, sfx.
            MVO     R3,         $0F8        ; /

            SETISR  ENGINE1

            B       @@loop                  ; Resume game.

            ENDP

MACRO       act(a,b,c,d,e,f,g,h)
            DECLE (ACTTBL.%a% SHL 14) + (ACTTBL.%b% SHL 12) + (ACTTBL.%c% SHL 10) + (ACTTBL.%d% SHL  8) + (ACTTBL.%e% SHL  6) + (ACTTBL.%f% SHL  4) + (ACTTBL.%g% SHL  2) + (ACTTBL.%h% SHL  0)
ENDM



ACTTBL      PROC
@@___       EQU     0
@@__f       EQU     1
@@j__       EQU     2
@@j_f       EQU     3

;;New       Prv 111 110 101 100 011 010 001 000     
@@000       act(___,___,___,___,___,___,___,___)
@@001       act(___,___,___,___,___,___,___,___)
@@010       act(___,___,___,___,___,___,___,___)
@@011       act(___,___,j__,___,___,j__,j__,j__)
@@100       act(___,___,___,___,___,___,___,___)
@@101       act(___,__f,___,__f,___,___,__f,__f)
@@110       act(___,___,j__,___,___,j__,j__,j__)
@@111       act(___,__f,j__,j_f,__f,j_f,j_f,j_f)

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
;*                   Copyright (c) 2007, Joseph Zbiciak                     *;
;* ======================================================================== *;
