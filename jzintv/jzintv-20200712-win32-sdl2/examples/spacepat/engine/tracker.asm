;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Music engine copyright 2006, Arnauld Chevallier                          ;;
;;==========================================================================;;

;;==========================================================================;;
;;  Constants                                                               ;;
;;==========================================================================;;
RFRSH2POS   EQU     (POS_A - RFRSH_A) AND $FFFF
POS2NOTE    EQU     (POS_A - NOTE_A)  AND $FFFF
COUNT2PER   EQU     ($01F0 - COUNT_A) AND $FFFF
PER2VOL     EQU     (VOL_A - $01F4)   AND $FFFF
VOL2VOL     EQU     ($01FB - VOL_A)   AND $FFFF

;;==========================================================================;;
;;  WAIT_SONG                                                               ;;
;;  Wait for end of current song                                            ;;
;;==========================================================================;;
WAIT_SONG   PROC

@@spin: MVI     SONG,   R0
        TSTR    R0
        BNEQ    @@spin
        
        JR      R5
        ENDP

WAIT_SONG1  PROC
        MVI@    R5,     R0
        MVO     R0,     WTIMER

        PSHR    R5

@@spin: MVI     DOENG,  R0
        DECR    R0
        BMI     @@nope
        MVO     R0,     DOENG
        CALL    UPSND
        CLRR    R0
        MVO     R0,     EBSY

@@nope: CLRR    R0
        CMP     WTIMER, R0
        BEQ     @@done

        CMP     SONG,   R0
        BNEQ    @@spin
        
@@done  MVO     R0,     WTIMER
        PULR    PC
        ENDP

;;==========================================================================;;
;;  INIT_SONG                                                               ;;
;;  Initialize a new song                                                   ;;
;;==========================================================================;;
PLAY.mus    MVI@    R5, R4
INIT_SONG   PROC
        PSHR    R5

        MVO     R4,     SONG        ; save song address

        INCR    R4                  ; read flags
        MVI@    R4,     R0
        MVO     R0,     MUS_FLAGS   ; and save them

        CALL    FILLZERO.lp         ; clear most variables
        DECLE   PAT-RFRSH_M+1
        DECLE   RFRSH_M

;       COMR    R0                  ; initialize counters
;       MVO     R0,     COUNT_A
;       MVO     R0,     COUNT_B
;       MVO     R0,     COUNT_C

        CALL    INITMEM.0
        INIT    COUNT_A,    $FF
        INIT    COUNT_B,    $FF
        INIT    COUNT_C,    $FF
        INIT    PSG0 + 8,   $38     ; set channel enables to "Tone Only"
        INIT    PSG1 + 8,   $31     ; on second PSG, have noise on channel A
        INIT    PSG1 + 9,   $3      ; Noise period of 3
        INIT    PSG1 + 11,  $0      ; Volume off
        INIT_DONE

        PULR    R5
        ENDP

;;==========================================================================;;
;;  INIT_PAT                                                                ;;
;;  Initialize next pattern                                                 ;;
;;==========================================================================;;
INIT_PAT    PROC

        MVI     SONG,   R4
        ADDI    #2,     R4
        MVI@    R4,     R2          ; R2 = address of 1st pattern
        MVI     PAT,    R0          ; R0 = position in patterns order table
        ADDR    R0,     R4

        MVI@    R4,     R1          ; R1 = pattern number
        TSTR    R1
        BPL     @@pat_ok            ; end of sequence ?

        CMPI    #$8000, R1          ; restart ? ...
        BNEQ    @@restart

        CLRR    R0                  ; ... no : clear SONG and quit
        MVO     R0,     SONG
        JR      R5

@@restart:
        ADDR    R1,     R0          ; ... yes : jump to restart position ...
        ADDR    R1,     R4
        DECR    R4
        MVI@    R4,     R1          ; ... and read again

@@pat_ok:
        INCR    R0                  ; increment position
        MVO     R0,     PAT         ; in patterns order table

        SLL     R1,     2           ; R4 = R1 * 4 + R2
        MOVR    R1,     R4          ; (beginning of pattern's detail)
        ADDR    R2,     R4

        MVI@    R4,     R0          ; init. pattern counter
        MVO     R0,     COUNT_P

    IF 0
        MVI@    R4,     R0          ; init. position for each channel
        MVO     R0,     POS_A
        MVI@    R4,     R0
        MVO     R0,     POS_B
        MVI@    R4,     R0
        MVO     R0,     POS_C
    ELSE
        MVI@    R4,     R0
        MVI@    R4,     R1
        MVI@    R4,     R2
        MVII    #POS_A, R4
        MVO@    R0,     R4
        MVO@    R1,     R4
        MVO@    R2,     R4
    ENDI

        JR      R5
        ENDP

;;==========================================================================;;
;;  PLAY_SONG                                                               ;;
;;  Update the current song                                                 ;;
;;==========================================================================;;
PLAY_SONG   PROC
        PSHR    R5

        MVI     SONG,   R4          ; is a song playing ?
        TSTR    R4
        BEQ     @@done

        MVI     COUNT_M,R0          ; global music counter
        INCR    R0
        MVO     R0,     COUNT_M

        MVI     RFRSH_M,R0          ; refresh notes ?
        DECR    R0
        BPL     @@notes_ok

        MVI@    R4,     R0          ; ... yes : read speed
        MVO     R0,     RFRSH_M

        CALL    UPD_CH              ; refresh note for each channel
        DECLE   RFRSH_A
        
        MVI     MUS_FLAGS,R0        ; 3-channel tune ? ...
        ANDI    #M_3CH, R0
        BEQ     @@tick
        
        CALL    UPD_CH              ; ... yes
        DECLE   RFRSH_B
        CALL    UPD_CH
        DECLE   RFRSH_C

@@tick:
        MVI     MUS_FLAGS,R0        ; ticks enabled ? ...
        ANDI    #M_TICK,R0
        BEQ     @@cnt

        MVII    #$0E,   R0          ; ... yes : initialize new tick
        MVO     R0,     PSG1+11

@@cnt:  MVI     COUNT_P,R0          ; pattern counter
        DECR    R0
        MVO     R0,     COUNT_P
        BNEQ    @@upd_psg           ; jump to next pattern ?

        CALL    INIT_PAT            ; ... yes
        B       @@upd_psg

@@notes_ok:
        MVO     R0,     RFRSH_M

@@upd_psg:
        CALL    UPD_PSG             ; update PSG for each channel
        DECLE   NOTE_A
        
        MVI     MUS_FLAGS,R0        ; 3-channel tune? ...
        ANDI    #M_3CH, R0
        BEQ     @@upd_tick
        
        CALL    UPD_PSG             ; ... yes
        DECLE   NOTE_B
        CALL    UPD_PSG
        DECLE   NOTE_C

@@upd_tick:
        MVI     PSG1+11,R1          ; update tick
        ANDI    #$0F,   R1
        SUBI    #4,     R1
        BPL     @@tick_ok
        CLRR    R1
@@tick_ok:
        MVO     R1,     PSG1+11

@@done:
        PULR    PC
        ENDP

;;==========================================================================;;
;;  UPD_CH                                                                  ;;
;;  Update a channel                                                        ;;
;;==========================================================================;;
UPD_CH  PROC
        MVI@    R5,     R3
        PSHR    R5

        MVI@    R3,     R0          ; (R3 = RFRSH_x)
        SUBI    #$10,   R0
        BMI     @@ch_new

        MVO@    R0,     R3
        PULR    PC

@@ch_new:
        ADDI    #RFRSH2POS,R3       ; read pos
        MVI@    R3,     R4
        MVI@    R4,     R0          ; read data

        MOVR    R0,     R1          ; disable ticks ? ...
        BPL     @@data_ok

        MVI     MUS_FLAGS,R2        ; ... yes
        ANDI    #($FFFF XOR M_TICK),R2
        MVO     R2,MUS_FLAGS

@@data_ok:
        MVO@    R4,     R3          ; update pos

        SWAP    R0                  ; save note
        SUBI    #POS2NOTE,R3
        ANDI    #$7F,   R0
        BEQ     @@skip_sav

        MVO@    R0,     R3

@@skip_sav:
        ADDI    #3,     R3          ; new refresh value (R3 = RFRSH_x)
        MVO@    R1,     R3

        ANDI    #$F,    R1          ; new volume
        ADDI    #3,     R3          ; (R3 = VOL_x)
        MVO@    R1,     R3

        TSTR    R0                  ; if note = 0,
        BEQ     @@ch_ok             ; don't reset counter

        ADDI    #6,     R3          ; (R3 = COUNT_x)
        CLRR    R0                  ; reset counter
        MVO@    R0,     R3

@@ch_ok:
        PULR    PC
        ENDP

;;==========================================================================;;
;;  UPD_PSG                                                                 ;;
;;  Update the PSG                                                          ;;
;;==========================================================================;;
UPD_PSG PROC
        MVI@    R5,     R3
        MVI@    R3,     R1          ; read note
        
        ADDI    #12,    R3          ; (R3 = COUNT_x)
        MVI@    R3,     R2          ; read channel counter -> R2
        CMPI    #$FF,   R2          ; prevents loop after $FF
        BEQ     @@cnt_ok

        INCR    R2                  ; increment counter
        MVO@    R2,     R3
        DECR    R2

@@cnt_ok:
        ADDI    #(PER_TBL-1),R1     ; read period from notes table
        MVI@    R1,     R0          ; R0 = period

        ADDI    #COUNT2PER,R3       ; write period
        MVO@    R0,     R3          ; (low)
        SWAP    R0
        ADDI    #4,     R3
        MVO@    R0,     R3          ; (high)

        MVI     MUS_FLAGS,R1        ; duplicate on channels B/C ? ...
        ANDI    #M_DUP, R1
        BEQ     @@env
        
        SWAP    R0                  ; ... yes
        MOVR    R0,     R1
        SUBI    #2,     R0          ; R0 = note tuned slightly sharp
        SLR     R1                  ; R1 = note + 1 octaves

        SUBI    #3,     R3          ; write period
        MVO@    R0,     R3          ; (low / channel B)
        INCR    R3
        MVO@    R1,     R3          ; (low / channel C)
        SWAP    R0
        SWAP    R1
        ADDI    #3,     R3
        MVO@    R0,     R3          ; (high / channel B)
        INCR    R3
        MVO@    R1,     R3          ; (high / channel C)
        SUBI    #2,     R3
        
@@env:
        MVII    #ENV.01, R4         ; R4 = pointer to envelope
        SLR     R2                  ; R2 = channel counter / 2

        MOVR    R2,     R1          ; get volume from envelope
        SLR     R2,     2
        ADDR    R2,     R4
        MVI@    R4,     R0

        SARC    R1,     2           ; 2 LSBs say which of four nibbles to use
        BC      @@env_X1            ;    C==1 means nibble 1 or 3
        SLR     R0,     2           ; \_ C==0 means nibble 0 or 2
        SLR     R0,     2           ; /
@@env_X1            
        BOV     @@env_1X            ;    V==1 means nibble 2 or 3
        SWAP    R0                  ;    V==0 means nibble 0 or 1
@@env_1X                            ; (nibbles numbered left-to-right)

        ANDI    #$F,    R0


        ADDI    #PER2VOL,R3         ; (R3 = VOL_x)
        SUB@    R3,     R0          ; get volume from song
        BPL     @@upd_vol
        CLRR    R0
@@upd_vol:
        ADDI    #VOL2VOL,R3         ; apply new volume
        MVO@    R0,     R3

        MVI     MUS_FLAGS,R1        ; duplicate on channels B/C ? ...
        ANDI    #M_DUP, R1
        BEQ     @@done
        
        INCR    R3                  ; ... yes : same value
        MVO@    R0,     R3
        INCR    R3
        MVO@    R0,     R3
@@done:
        JR      R5
        ENDP

;;==========================================================================;;
;;  PER_TBL                                                                 ;;
;;  Periods of the 50 defined notes                                         ;;
;;==========================================================================;;
PER_TBL PROC
        DECLE   $054D, $0501, $04B9, $0475, $0435, $03F9, $03C0, $038A
        DECLE   $0357, $0327, $02FA, $02CF, $02A7, $0281, $025D, $023B
        DECLE   $021B, $01FC, $01E0, $01C5, $01AC, $0194, $017D, $0168
        DECLE   $0153, $0140, $012E, $011D, $010D, $00FE, $00F0, $00E2
        DECLE   $00D6, $00CA, $00BE, $00B4, $00AA, $00A0, $0097, $008F
        DECLE   $0087, $007F, $0078, $0071, $006B, $0065, $005F, $005A
        DECLE   $0055, $0050
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
