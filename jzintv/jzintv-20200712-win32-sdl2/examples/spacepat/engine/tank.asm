;; ======================================================================== ;;
;;  Miscellaneous tank-related stuff.                                       ;;
;; ======================================================================== ;;

;;==========================================================================;;
;;  DOJUMP -- Event handler for jump key.                                   ;;
;;==========================================================================;;
DOJUMP      PROC
            PSHR    R5
            MVI     JHGT,   R0
            TSTR    R0
            BNEQ    @@nojump
            MVII    #VJUMP, R0
            MVO     R0,     JVEL
            MVII    #2,     R1

            MVII    #FXJUMP2,R1
            CALL    DOPLAYSFX

            MVII    #FXJUMP,R1
            PULR    R5
            B       DOPLAYSFX

@@nojump:   PULR    PC
            ENDP

;;==========================================================================;;
;;  DOFIRE -- Event handler for fire button.                                ;;
;;==========================================================================;;
DOFIRE      PROC
            PSHR    R5

            ; Don't let user fire too often
            MVI     FCNT,   R0
            TSTR    R0
            BNEQ    @@noupb
            MVII    #10,    R0
            MVO     R0,     FCNT


            ; See if we have a bullet we can fire.  We get 2.
            CLRR    R0
            CLRR    R1
            MVII    #SPAT2 + 5, R5
            CMP@    R5,     R0      ; Check first bullet slot.
            BEQ     @@do_fire_up    ; if attr==0, bullet is available
            CMP@    R5,     R0      ; Check second bullet slot.
            BNEQ    @@noupb         ; if second bullet not available, leave
            MVII    #2,     R1

@@do_fire_up:   ; Fire the bullet!

            MOVR    R1,     R4
            ADDI    #SPXY2 +  5*2, R4   ; R4 points to XY position
            ADDI    #SPXYV + 10*2, R1   ; R1 points to XY velocity


            CLRR    R3
            MVO@    R3,     R1      ; set X velocity to 0
            INCR    R1
            MVII    #$00FE, R3
            MVO@    R3,     R1      ; set Y velocity to -$80

            MVI     SDAT,   R3      ; get buggy's X position
            SUBI    #6,     R3      ; Offset slightly
            ANDI    #$FF,   R3      ; mask to 8 bits

            MVO@    R3,     R4      ; MSB derived from tank position

            MVI     SDAT+8, R3      ; get buggy's Y position
            SUBI    #4,     R3      ; Offset slightly
            ANDI    #$7F,   R3      ; mask to 7 bits
            MVO@    R3,     R4      ; MSB derived from tank position

            DECR    R5              ;
            MVII    #SPATBL.b3, R3  ; Get the buggy's bullet
            MVO@    R3,     R5      ; Activate the bullet

            MVII    #FXBFIRE,R1
            CALL    DOPLAYSFX       ; Make a bip...

@@noupb:


            ;; Can we fire a horizontal bullet?

            MVI     HBCNT2, R0
            TSTR    R0
            BNEQ    @@leave

            MVI     HBCOL0, R0      ; Get current displayed horiz bullet column
            DECR    R0              ; If zero, we can fire.
            BPL     @@leave         ; Non-zero, don't fire.

            MVI     JHGT,   R2      ; Are we jumping?
            CMPI    #32*4,  R2      ;
            BGE     @@leave         ; Yes:  Don't fire.


            MVI     SDAT,   R3      ; get buggy's X position
            ADDI    #16,    R3      ; Offset slightly
            ANDI    #$FF,   R3      ; keep 8 bits

            SLR     R3,     1       ; \
            MOVR    R3,     R4      ;  |__ Pick an initial bullet graphic.
            ANDI    #3,     R4      ;  |
            ADDI    #@@tbl, R4      ; /

            SLR     R2,     2       ; \
            SLR     R2,     2       ;  |-- Calculate horizontal bullet row
            SLR     R2,     1       ; /
            MVII    #20,    R1      ; End 5.5 cards away
            MVI@    R4,     R0      ; Starting position in pattern depends on
                                    ; buggy position

            MVO     R0,     HBDATA  ; \
            MVO     R1,     HBCNT   ;  |__ "Ensign, fire at Will!"
            MVO     R2,     HBROW   ;  |
            MVO     R3,     HBCOL1  ; /
            MVII    #28,    R1
            MVO     R1,     HBCNT2  ;
            CLRR    R0
            MVO     R0,     HBKOS


            MVII    #FXBFIRE,R1
            CALL    DOPLAYSFX       ; Make a bip...

@@leave:    PULR    PC

@@tbl:      DATA    $C0, $30, $0C, $03
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
