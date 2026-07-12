;;==========================================================================;;
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2007, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  Bad guy related code                                                    ;;
;;                                                                          ;;
;;   -- Update bad-guy movement programs.                                   ;;
;;   -- Spawn/kill bad guys.                                                ;;
;;                                                                          ;;
;;  "Love among puppets / And one day I'll pull all the strings"            ;;
;;                                                -- Gary Numan             ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  BGSPAWN -- Spawns a set of bad guys.  Set to spawn is in R3.            ;;
;; ======================================================================== ;;
BGSPAWN PROC
        PSHR    R5

;       PSHR    R3
;       SLL     R3,     1
;       SLL     R3,     2
;       ADDI    #$87,   R3
;       MVO     R3,     $200
;       PULR    R3

        MVII    #SPAWNTBL,R4    ;\
        SLL     R3,     2       ; |-- R5 = 4*R3 + SPAWNTBL
        ADDR    R3,     R4      ;/

        B       @@first

@@sploop:
        CALL    BGMAKE
        ADCR    PC              ;\_ if carry set, we maybe have room for more
        PULR    PC              ;/
@@first:
        MVI@    R4,     R2      ; movement program
        TSTR    R2              ; if bit 15 set, this is last spawn in list
        BPL     @@sploop

        ANDI    #$7FFF, R2      ;\

;       B       BGMAKE.1        ; |- chain return via BGMAKE
        INCR    PC              ;/

        ENDP

;; ======================================================================== ;;
;;  BGMAKE  Make a given bad-guy in first-available slot (if any)           ;;
;;          R2  -- Movement program                                         ;;
;;          R4  -- Pointer to rest of spawn record.                         ;;
;; ======================================================================== ;;
BGMAKE  PROC
        PSHR    R5
@@1:
        ;; ---------------------------------------------------------------- ;;
        ;;  Find first slot in group 1 of the MOBs.                         ;;
        ;; ---------------------------------------------------------------- ;;
        MVII    #SPAT1, R5
        MVII    #5,     R1
        CLRR    R0
@@find:
        CMP@    R5,     R0
        BEQ     @@found
        DECR    R1
        BNEQ    @@find

        CLRC
        PULR    PC                ;; Didn't find one, so leave.

        ;; ---------------------------------------------------------------- ;;
        ;;  Slot is open so copy over the attribute for the new bad-guy.    ;;
        ;; ---------------------------------------------------------------- ;;
@@found:
        MOVR    R5,     R1

        MOVR    R2,     R0
        SWAP    R0
        ANDI    #$7F,   R0

        CMPI    #BGI.plant0, R0
        BNEQ    @@not_plant
        CALL    PLAYSFX
        DECLE   FXPLANT
        B       @@cont
@@not_plant:
        CMPI    #BGI.sauc_lr,R0
        BNEQ    @@cont

        MVI     WAVE,   R0      ; \
        INCR    R0              ;  |- Increment active saucer count
        MVO     R0,     WAVE    ; /

        DECR    R0              ; \
        BNEQ    @@cont          ;  |  Play saucer sound effect at start of
        MVO     R0,     WKILL   ;  |- a new wave, and zero out the kill count
        CALL    PLAYSFX         ;  |
        DECLE   FXSAUC          ; /

@@cont:
        MOVR    R1,     R5

        DECR    R5              ; rewind R5 back to slot in SPAT
        MVI     COURSE, R3      ; \
        ANDI    #6,     R3      ;  |
        SLL     R3,     2       ;  |- Index into BGS table based on
        SLL     R3,     1       ;  |  current course
        ADDI    #BGSTBL*2,R3    ; /
        ADD@    R4,     R3      ; get bad-guy type
        RRC     R3
        MVI@    R3,     R0      ; look up bad guy attributes.
        ADCR    PC              ; \
        SWAP    R0              ;  |- unpack
        MOVR    R0,     R3      ;  |    (R3 holds jump-over score detail)
        ANDI    #$FC,   R0      ; /
        INCR    R0

        CMPI    #SPATBL.stal, R0
        BNEQ    @@notstal           ; \
        MVI     INCITY, R0          ;  |
        CMPI    #2,     R0          ;  |- Only spawn stalactites underground
        BNEQ    @@nospawn           ;  |
        MVII    #SPATBL.stal, R0    ; /
@@notstal:
        MVO@    R0,     R5      ; Store attrs to SPAT.

        ADDI    #JMPSCO-SPAT1-1, R5 ; \
        ANDI    #3,     R3          ;  |- Store the jump-over score info
        MVO@    R3,     R5          ; /

        DECR    R4
        MVI@    R4,     R3

        ADDI    #SPHSCR-JMPSCO-1, R5    ; Index into SPHSCR table
        CLRR    R1              ; \
        CMPI    #8,     R3      ;  |_ Clear SPHSCR for spawns 0-7
        ADCR    R1              ;  |  Set SPHSCR for spawns 8-15
        MVO@    R1,     R5      ; /

        ADDI    #BGEXIT-SPHSCR-1, R5 ; Point into Bad-Guy exit table
        MVO@    R2,     R5      ; Store out "exit programming"
        SWAP    R2              ;

        SUBI    #BGEXIT+1, R5   ; convert R5 back to slot #

        ADDR    R5,     R5
        MOVR    R5,     R3      ; R3 = 2*slot
        ADDR    R5,     R5      ; R5 points into BGMPTBL + 4*slot
        ADDI    #BGMPTBL, R5    ; Now index into program counter tbl
        MVO@    R2,     R5      ; Store motion program indirection
        MVII    #1,     R1      ; Zero out rest of program state.
        MVO@    R1,     R5      ; delay counter -- wait a tick, balance load
        MVI@    R4,     R1
        MVO@    R1,     R5      ; stat byte 1
        SWAP    R1
        MVO@    R1,     R5      ; stat byte 2

        MVII    #SPXYV, R5      ; \__ Now point to this slot's X/Y velocity
        ADDR    R3,     R5      ; /

        CLRR    R2              ; \
        MVO@    R2,     R5      ;  |-- Set X, Y velocity to 0.
        MVO@    R2,     R5      ; /

        ADDI    #SPXYP-SPXYV-2, R5 ; Index back into position table.
        MVI@    R4,     R3      ; Get X/Y coordinates
        MOVR    R3,     R2      ; \
        ANDI    #$00FF, R3      ;  |
        BNEQ    @@notf          ;  |\
        MVI     FXLO,   R3      ;  | |- Pick up follower X posn for the
        XORR    R3,     R2      ;  |/   mine-layer
@@notf: MVO@    R3,     R5      ;  |__ Initialize the position for this
        XORR    R3,     R2      ;  |   bad guy.
        SWAP    R2              ;  |
        MVO@    R2,     R5      ; /

@@nospawn:
        SETC
        PULR    PC

        ENDP

MACRO BGSENT a,W,b,X,c,Y,d,Z
    DECLE (((SPATBL.%a% AND $FC) OR %W%) SHL 8) + ((SPATBL.%b% AND $FC) OR %X%)
    DECLE (((SPATBL.%c% AND $FC) OR %Y%) SHL 8) + ((SPATBL.%d% AND $FC) OR %Z%)
ENDM

BGSTBL  PROC
    ; Moon
    BGSENT  pnk0,  0,      blu0,  0,      wht0,  0,      fol0a, 0
    BGSENT  fol0b, 0,      pnk0,  0,      blu0,  0,      wht0,  0
    BGSENT  tur0,  2,      bld0a, 2,      lmna,  1,      plta,  2
    BGSENT  pltc,  3,      0,     0,      0,     0,      0,     0
                                                                 
    ; Mars                                                       
    BGSENT  pnk1,  0,      blu1,  0,      wht1,  0,      fol1a, 0
    BGSENT  fol1b, 0,      pnk1,  0,      blu1a, 0,      wht1,  0
    BGSENT  tur1,  2,      bld0a, 2,      lmna,  1,      plta,  2
    BGSENT  pltc,  3,      0,     0,      0,     0,      0,     0
                                                                 
    ; Pluto                                                      
    BGSENT  pnk2,  0,      blu2,  0,      wht2,  0,      fol2a, 0
    BGSENT  fol2b, 0,      pnk2,  0,      blu2,  0,      wht2,  0
    BGSENT  tur2,  2,      bld0a, 2,      lmna,  1,      plta,  2
    BGSENT  pltc,  3,      crat6, 2,      0,     0,      0,     0
                                                                 
    ; Mercury                                                    
    BGSENT  pnk3,  0,      blu3,  0,      wht3,  0,      fol3a, 0
    BGSENT  fol3b, 0,      pnk3c, 0,      blu3c, 0,      wht3,  0
    BGSENT  tur3,  2,      bld0a, 2,      lmna,  1,      plta,  2
    BGSENT  pltc,  3,      stal,  0,      0,     0,      0,     0

    ENDP

;; ======================================================================== ;;
;;  BGDOEXIT -- Make a set of bad guys exit.                                ;;
;; ======================================================================== ;;
BGDOEXIT PROC

        SLL     R3,     2       ; \___ Shift our exit cue # to align w/
        SLL     R3,     1       ; /    exit programming in BGEXIT table
        ANDI    #$F8,   R3      ; cull extra bits

        MVII    #BGEXIT,    R4  ; point R4 into Bad Guy Exit Program table
        MVII    #BGMPTBL,   R2  ; point R2 into Bad Guy Motion Program table

        MVII    #5,     R0      ; loop over all five bad guys

@@loop: MVI@    R2,     R1      ; \
        TSTR    R1              ;  |- Skip dead bad guys
        MVI@    R4,     R1
        BEQ     @@nope          ; /
        XORR    R3,     R1      ; lets see if tag is equal
        CMPI    #8,     R1      ; if remainder < 8, it is.
;       BC      @@nope
        ADCR    PC              ; ADCR is a tad cheaper than the branch
        MVO@    R1,     R2      ; force this bad guy into his exit state
@@nope: ADDI    #4,     R2      ; advance to next BGMP record
        DECR    R0
        BNEQ    @@loop          ; loop over all 5 bad guys

        JR      R5
        ENDP

 IF (DEFINED BUILD_DEMO)
;; ======================================================================== ;;
;;  UPDMO    Update demo program                                            ;;
;; ======================================================================== ;;
UPDMO   PROC
        PSHR    R5

        MVI     DIG_CNT,R0
        DECR    R0
        BPL     @@cmd_delaying

        MVI     DIG_PTR,R5
        B       @@cmd_loop

@@next_cmd:
        PULR    R1
        PULR    R5

@@cmd_loop:
        MVI@    R5,     R0      ; Read in command
        MVO     R5,     DIG_PTR

        ;; Commands:
        ;;  <0 Delay  (< 0)
        ;;  0  End demo
        ;;  2  Jump
        ;;  4  Fire
        ;;  6  Set velocity
        ;;  8  Spawn bad-guy grouping

        COMR    R0
        BEQ     @@cmd_loop
        BPL     @@cmd_delaying
        COMR    R0
        MOVR    R0,     R1
        SLR     R1,     2
        SLR     R1,     2

        PSHR    R5
        PSHR    R1

        ANDI    #$E,    R0
        ADDR    R0,     PC
        B       @@cmd_demo_over
        B       @@cmd_jump
        B       @@cmd_fire
        B       @@cmd_setvel
        B       @@cmd_spawn
        B       @@cmd_demo_over
        B       @@cmd_demo_over
        B       @@cmd_demo_over

@@cmd_jump:
        CALL    DOJUMP
        B       @@next_cmd

@@cmd_fire:
        CALL    DOFIRE
        B       @@next_cmd

@@setvel_tbl:
        DECLE   VSLOW,  VMED,   VFAST

@@cmd_setvel:
        ADDI    #@@setvel_tbl, R1
        MVI@    R1,     R1
        MVO     R1,     WANTVL
        B       @@next_cmd

@@cmd_spawn:
        CALL    BGSPAWN
        B       @@next_cmd

@@cmd_delaying:
        MVO     R0,     DIG_CNT
        PULR    PC

@@cmd_demo_over:
        SUBI    #2,     R6      ; discard top two items on stack
        PULR    R5
        B       SCHEDEXIT

        ENDP
        INCLUDE "demo_ingame.asm"
 ENDI

;; ======================================================================== ;;
;;  Interpreter for Bad Guy Motion Programs                                 ;;
;;                                                                          ;;
;;  ARCHITECTURE                                                            ;;
;;                                                                          ;;
;;  Each bad guy has the following 5 bytes of state:                        ;;
;;                                                                          ;;
;;   -- One program indirect pointer (1 byte)                               ;;
;;   -- One delay counter   (1 byte)                                        ;;
;;   -- Two status bytes    (2 bytes)                                       ;;
;;                                                                          ;;
;; ======================================================================== ;;


;; ======================================================================== ;;
;;  UPBGM -- Update Bad Guy Motion.  Called on a 30Hz tick.                 ;;
;; ======================================================================== ;;
UPBGM   PROC

@@0:    PSHR    R5

        MVII    #BGMPTBL, R4
        CLRR    R1
        B       @@first_bgmp    ; skip first INCR R1

@@1:    PSHR    R5

        MVII    #BGMPTBL + 4, R4
        MVII    #1,     R1
        B       @@first_bgmp

        ;; ---------------------------------------------------------------- ;;
        ;;  Iterate through the motion programs.                            ;;
        ;;   R0 -- scratch                                                  ;;
        ;;   R1 -- Slot # for MOB (within group 1)                          ;;
        ;;   R2 -- Program counter for current record.                      ;;
        ;;   R3 -- scratch                                                  ;;
        ;;   R4 -- Pointer to BGMP state tables                             ;;
        ;;   R5 -- scratch                                                  ;;
        ;; ---------------------------------------------------------------- ;;

@@next_bgmp:
        ADDI    #2,     R1      ; next slot #

        CMPI    #5,     R1      ; Is this the end?
        BGE     @@done_bgmp     ; Yes, done.

@@first_bgmp:
        MVI@    R4,     R2      ; Get program counter
        TSTR    R2              ; If it's zero, motion program is inactive
        BNEQ    @@active_bgmp   ; Non-zero, it's active.

        ADDI    #3 + 4, R4      ; Skip rest of record.
        CMPI    #BGMPTBL+20, R4 ; Is this the end?
        BLT     @@next_bgmp     ; No, do the next one.
;       B       @@done_bgmp     ; Yes, done.
@@done_bgmp:
        PULR    PC

@@active_bgmp:

        MOVR    R4,     R3
        MVI@    R4,     R0      ; Get delay counter for this motion program
        ADDI    #2 + 4, R4      ; point to next record
        DECR    R0              ; Count down the delay counter.
        MVO@    R0,     R3      ; Store the updated delay counter

        BPL     @@next_bgmp     ; If not expired, go to the next program.

@@expired:
        INCR    R3              ; Point R3 to first 'status byte' in record
        PSHR    R4
;       MVII    #@@dnR4,R5      ; \    Call the motion program via indirect
        ADDI    #BGMPIND-1,R2   ;  |-- table.  R1=slot #, R3 and R4=state tbl
        MVI@    R2,     PC      ; /    R2, R5 are scratch.

BGT_RET:
@@dnR4: PULR    R4
@@done: DECR    R3              ; Point R3 back to delay counter
        MVO@    R0,     R3      ; Put R0 (return value) into delay counter.

        B       @@next_bgmp     ; Do processing for next motion program

        ENDP

;; ======================================================================== ;;
;;  BGFIRE.  Make bad-guy number in R1 fire a bullet.                       ;;
;;           R0 == Velocity table index in MSB, attr in LSB.                ;;
;; ======================================================================== ;;
BGFIRE  PROC

@@d:    MVII    #pack(@@cc-@@tbl, SPATBL.b5), R0    ; fire left
        B       @@doit

@@c:    MVII    #pack(@@cc-@@tbl, SPATBL.b4), R0    ; fire left
        B       @@doit

@@b:    MVII    #pack(@@bb-@@tbl, SPATBL.b1), R0    ; drop crater maker
        B       @@doit

@@a:    MVII    #pack(@@aa-@@tbl, SPATBL.b2), R0    ; drop the bomb

@@doit:
        PSHR    R5
        PSHR    R4

        MVII    #TMP,   R4

        MVO@    R0,     R4
        SWAP    R0
        MVO@    R0,     R4

        MVO@    R2,     R4
        SWAP    R2
        MVO@    R2,     R4
        CLRR    R2                  ; interruptible

        MVO@    R3,     R4
        CLRR    R3                  ; interruptible


        ; here, R1 == bad guy #.  Now we need to copy the bad-guy's
        ; coordinates to the bullet, set up the bullet velocity,
        ; and bullet type.

        ; find a slot for the bullet
        MVII    #SPAT2, R5
@@slotlp:
        INCR    R2
        CMP@    R5,     R3
        BNEQ    @@slotlp
        DECR    R2

        CMPI    #SPAT2+5,R5
        BC      @@nobgfire      ; Can't fire -- all slots taken

        ;  set up position
        MOVR    R1,     R4      ; R1 == bad guy number
        MOVR    R2,     R5      ; R2 == bullet slot number
        ADDR    R1,     R4      ; R4 == offset to bad guy
        ADDR    R2,     R5      ; R5 == offset to bullet slot
        ADDI    #SPXY1, R4      ; Point to XY of badguy
        ADDI    #SPXY2, R5      ; Point to XY of bullet

        MVII    #$00FF, R0      ;
        MVI@    R4,     R3      ; \
        SUBI    #$003,  R3      ;  |
        ANDR    R0,     R3      ;  |__ Copy over MSB of X and Y.
        MVO@    R3,     R5      ;  |   Offset X left by 3 pixels.
        AND@    R4,     R0      ;  |
        MVO@    R0,     R5      ; /

        ; now, set up velocity & type.  These are passed in via R0 and R3.
        MVII    #SPXYV+5*2, R5  ; \
        ADDR    R2,     R5      ;  |-- Point to xy vel of bullet
        ADDR    R2,     R5      ; /
        ADDI    #SPAT2, R2      ; Point to attr of bullet

        MVI     TMP+1,  R4      ; \__ get ptr to horiz/vert velocity
        ADDI    #@@tbl, R4      ; /
        MVI@    R4,     R0
        MVO@    R0,     R5      ; set horiz velocity of bullet
        MVI@    R4,     R0
        MVO@    R0,     R5      ; set vert velocity of bullet

        MVI     TMP,    R3      ; Get attribute.
        MVO@    R3,     R2      ; Store out attribute
        B       @@done

@@nobgfire:
@@done:
        MVI     TMP+4,  R3
        XORI    #$100,  R3
        MVI     TMP+3,  R2
        SWAP    R2
        MVI     TMP+2,  R2

        PULR    R4
        PULR    PC

@@tbl:
@@cc:   DECLE   $44FE, $0000
@@bb:   DECLE   $4001, $4001
@@aa:   DECLE   $0000, $0001

        ENDP

;; ======================================================================== ;;
;;  BGKILL  Remove a bad guy in a given slot.                               ;;
;;          R1  -- Slot number                                              ;;
;; ======================================================================== ;;
BGKILL  PROC
        PSHR    R5

        ADDI    #BGEXIT,R1          ; \
        CLRR    R0                  ;  |- Cancel BGEXIT tie-in
        MVO@    R0,     R1          ; /

        ADDI    #SPHSCR-BGEXIT,R1   ; \_ Cancel any horiz scrolling this
        MVO@    R0,     R1          ; /  bad guy may have requested.

        SLL     R1,     2
        MVII    #(BGMPTBL - 4*(SPHSCR)) AND $FFFF, R5
        ADDR    R1,     R5

        ;; Kill the movement program connected with this slot
        MVO@    R0,     R5  ; zero out the motion program pointer.
        MVO@    R0,     R5  ; zero out the motion program counter.
        MVO@    R0,     R5  ; zero out loopa
        MVO@    R0,     R5  ; zero out loopb

        PULR    PC
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
