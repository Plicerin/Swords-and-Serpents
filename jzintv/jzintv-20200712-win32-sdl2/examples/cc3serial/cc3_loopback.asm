;;==========================================================================;;
;; Joe Zbiciak's Loopy McLoopback for CC3                                   ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;* ======================================================================== *;
;*  TO BUILD IN BIN+CFG FORMAT:                                             *;
;*      as1600 -o cc3_loopback.bin -l cc3_loopback.lst cc3_loopback.asm     *;
;*                                                                          *;
;*  TO BUILD IN ROM FORMAT:                                                 *;
;*      as1600 -o cc3_loopback.rom -l cc3_loopback.lst cc3_loopback.asm     *;
;* ======================================================================== *;

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

        CFGVAR  "name" = "SDK-1600 Loopy McLoopback for CC3"
        CFGVAR  "short_name" = "Loopy McLoopback"
        CFGVAR  "author" = "Joe Zbiciak"
        CFGVAR  "author" = "Chad Schell"
        CFGVAR  "year" = 2006
        CFGVAR  "license" = "GPLv2+"
        CFGVAR  "description" = "Serial loopback tester for CC3 boards"
        CFGVAR  "publisher" = "SDK-1600"

        ROMW    16              ; Use 16-bit ROM width
        ORG     $5000           ; Use default memory map

RX_ERROR    EQU $35B
FRAMING     EQU $35B
PARITY      EQU $35B
OVERRUN     EQU $35C
OK_COUNT    EQU $35D
LAST_LSR    EQU $35E
LAST_RBR    EQU $35F
ROTATE      EQU $103


;------------------------------------------------------------------------------
; Include system information
;------------------------------------------------------------------------------
        INCLUDE "../library/gimini.asm"

;------------------------------------------------------------------------------
; EXEC-friendly ROM header.
;------------------------------------------------------------------------------
ROMHDR: BIDECLE ZERO            ; MOB picture base   (points to NULL list)
        BIDECLE ZERO            ; Process table      (points to NULL list)
        BIDECLE MAIN            ; Program start address
        BIDECLE ZERO            ; Bkgnd picture base (points to NULL list)
        BIDECLE ONES            ; GRAM pictures      (points to NULL list)
        BIDECLE TITLE           ; Cartridge title/date
        DECLE   $03C0           ; No ECS title, run code after title,
                                ; ... no clicks
ZERO:   DECLE   $0000           ; Screen border control
        DECLE   $0000           ; 0 = color stack, 1 = f/b mode
ONES:   DECLE   C_BLU, C_BLU    ; Initial color stack 0 and 1: Blue
        DECLE   C_BLU, C_BLU    ; Initial color stack 2 and 3: Blue
        DECLE   C_BLU           ; Initial border color: Blue
;------------------------------------------------------------------------------


;; ======================================================================== ;;
;;  TITLE  -- Display our modified title screen & copyright date.           ;;
;; ======================================================================== ;;
TITLE:  PROC
        BYTE    106, 'Loopy McLoopback', 0
MAIN:   
        ; Patch the title string to say '=JRMZ=' instead of Mattel.
        CALL    PRINT.FLS       ; Write string (ptr in R5)
        DECLE   C_WHT, $23D     ; White, Point to 'Mattel' in top-left
        STRING  '=JRMZ='        ; Guess who?  :-)
        STRING  ' Productions' 
        BYTE    0

        CALL    PRINT.FLS       ; Write string (ptr in R1)
        DECLE   C_WHT, $2D0     ; White, Point to 'Mattel' in lower-right
        STRING  '2006 =JRMZ='   ; Guess who?  :-)
        BYTE    0

        MVII    #ISR,   R0
        MVO     R0,     $100
        SWAP    R0
        MVO     R0,     $101

        EIS

        CLRR    R0
        MVO     R0,     LAST_LSR
        MVO     R0,     LAST_RBR
        MVO     R0,     OK_COUNT
        MVO     R0,     ROTATE  
        CLRR    R0
        MVO     R0,     RX_ERROR
        MVO     R0,     FRAMING
        MVO     R0,     PARITY
        MVO     R0,     OVERRUN


        CALL    CC3_SERINIT
        MVII    #9600 / 2, R0
        CALL    CC3_SETBAUD
        BC      @@sb_fail
@@loop:
        CALL    CC3_RECV
        TSTR    R1
        BEQ     @@no_error

        MVI     OVERRUN,    R2
        SARC    R1
        ADCR    R2
        MVO     R2,         OVERRUN

        MVI     PARITY,     R2
        SARC    R1
        ADCR    R2
        MVO     R2,         PARITY

        MVI     FRAMING,    R2
        SARC    R1
        ADCR    R2
        MVO     R2,         FRAMING
        
        TSTR    R1
        BNEQ    @@xmit

        MVI     RX_ERROR,   R2
        INCR    R2
        MVO     R2,         RX_ERROR

@@xmit: CALL    CC3_XMIT
        B       @@loop

@@no_error:
        MVI     OK_COUNT,   R2
        INCR    R2
        MVO     R2,     OK_COUNT
        CALL    CC3_XMIT
        B       @@loop


@@sb_fail: CALL    PRINT.FLS
        DECLE   7, $200, "SETBAUD Failed", 0

        ; Done.
        DECR    PC
        ENDP


ISR     PROC 
        MVO     R0,     $20
        MVI     ROTATE, R1
        INCR    R1
        MVO     R1,     ROTATE
        ANDI    #3,     R1
        ADDI    #@@table, R1
        MVI@    R1,     PC
@@table:
        DECLE   @@a, @@b, @@c, @@d;


@@a:    MVI     RX_ERROR, R0
        MVII    #7,     R1
        MVII    #$200,  R4
        CALL    HEX16
        B       $1014

@@b:    MVI     FRAMING,  R0
        MVII    #7,     R1
        MVII    #$205,  R4
        CALL    HEX16
        B       $1014

@@c:    MVI     PARITY,   R0
        MVII    #7,     R1
        MVII    #$20A,  R4
        CALL    HEX16
        B       $1014

@@d:    MVI     OVERRUN, R0
        MVII    #7,     R1
        MVII    #$20F,  R4
        CALL    HEX16
        B       $1014

        ENDP

;; ======================================================================== ;;
;;  LIBRARY INCLUDES                                                        ;;
;; ======================================================================== ;;
        INCLUDE "../library/print.asm"       ; PRINT.xxx routines
        INCLUDE "../library/fillmem.asm"     ; CLRSCR/FILLZERO/FILLMEM
        INCLUDE "../library/hex16.asm"         


    IF 0
        INCLUDE "cc3serial.asm"
    ELSE

;; ======================================================================== ;;
;;  Serial Driver for CC3                                                   ;;
;;  Slavish copy of C code from Chad Schell.                                ;;
;; ======================================================================== ;;


CC3         PROC
@@u0dll     EQU     $0F00
@@u0thr     EQU     $0F00
@@u0rbr     EQU     $0F00
@@u0dlm     EQU     $0F01
@@u0fcr     EQU     $0F02
@@u0lsr     EQU     $0F03
@@u0lcr     EQU     $0F04
@@u0ter     EQU     $0F05
@@PCLK      EQU     15000000/16
            ENDP
;; ======================================================================== ;;
;;  CC3_SERINIT -- Init / reset the serial port.  Sets it to 19200 8-N-1.   ;;
;; ======================================================================== ;;
CC3_SERINIT PROC

    IF 1
            MVII    #$80,       R0          ;\_ enable divisor access
            MVO     R0,         CC3.u0lcr   ;/
            CLRR    R1                      ;\
            MVO     R1,         CC3.u0dlm   ; |_ Set for 19200 baud
            MVII    #$31,       R1          ; |
            MVO     R1,         CC3.u0dll   ;/
            MVII    #$03,       R1          ;\_ 8-N-1 format
            MVO     R1,         CC3.u0lcr   ;/
            MVII    #$C7,       R1          ;\_ Enable, reset FIFOs
            MVO     R1,         CC3.u0fcr   ;/
            MVO     R0,         CC3.u0ter   ; Enable transmitter
            JR      R5
    ELSE
            MVII    #$80,       R0          ;\_ enable divisor access
            MVO     R0,         CC3.u0lcr   ;/
            CLRR    R1                      ;\
            MVO     R1,         CC3.u0dlm   ; |_ Set for 4800 baud
            MVII    #$C4,       R1          ; |
            MVO     R1,         CC3.u0dll   ;/
            MVII    #$03,       R1          ;\_ 8-N-1 format
            MVO     R1,         CC3.u0lcr   ;/
            MVII    #$C7,       R1          ;\_ Enable, reset FIFOs
            MVO     R1,         CC3.u0fcr   ;/
            MVO     R0,         CC3.u0ter   ; Enable transmitter
            JR      R5
    ENDI

            ENDP


;; ======================================================================== ;;
;;  CC3_XMIT    -- Send byte in R0                                          ;;
;; ======================================================================== ;;
CC3_XMIT    PROC
            PSHR    R5

@@wait_tx:
;           MVI     CC3.u0lsr,  R5
;           ANDI    #$20,       R5
;           BEQ     @@wait_tx

            MVO     R0,         CC3.u0thr
            PULR    PC
            ENDP


;; ======================================================================== ;;
;;  CC3_RECV    -- Receive byte in R0.  Status in R1.                       ;;
;; ======================================================================== ;;
CC3_RECV    PROC
@@recv_loop MVI     CC3.u0lsr,  R1          ;\
            SARC    R1                      ; |- Wait for LSB to be 1
            BNC     @@recv_loop             ;/

            MVO     R1,         LAST_LSR

            MVI     CC3.u0rbr,  R0          ; Read data
            ANDI    #$47,       R1          ; Leave only error status in R1

            MVO     R0,         LAST_RBR

            JR      R5
            ENDP




;; ------------------------------------------------------------------------ ;;
;;  Baud rates                                                              ;;
;; ------------------------------------------------------------------------ ;;
MACRO           cc3_baud x 
                DECLE   %x% / 2, ((CC3.PCLK + (%x%/2)) / %x%)
ENDM
CC3_BAUD        PROC
                cc3_baud    115200
                cc3_baud    57600
                cc3_baud    38400
                cc3_baud    19200
                cc3_baud    9600
                cc3_baud    4800
                cc3_baud    2400
                cc3_baud    1200
                cc3_baud    600
                cc3_baud    300
                cc3_baud    110

@@rates         EQU         ($ - CC3_BAUD) / 2
                ENDP

;; ======================================================================== ;;
;;  CC3_SETBAUD  -- Set the baud rate for the serial port.                  ;;
;;                  R0 is desired baud rate divided by 2, up to 115200.     ;;
;;                  C=1 if baud rate is unsupported.                        ;;
;; ======================================================================== ;;
CC3_SETBAUD     PROC
                MVII    #CC3_BAUD,       R4
                MVII    #CC3_BAUD.rates, R1
               
@@loop:         CMP@    R4,         R0
                BEQ     @@got_it
                INCR    R4
                DECR    R1
                BNEQ    @@loop
               
                ;; Didn't find it.  Report error with C=1
                SETC
                JR      R5
@@got_it:      
                MVII    #$80,       R0          ;\_ enable divisor access
                MVO     R0,         CC3.u0lcr   ;/
                MVI@    R4,         R1          ; get baud rate from table
                MVO     R1,         CC3.u0dll   ;\
                SWAP    R1                      ; |- Set desired baud rate
                MVO     R1,         CC3.u0dlm   ;/
                MVII    #$03,       R1          ;\_ 8-N-1 format
                MVO     R1,         CC3.u0lcr   ;/
                MVII    #$07,       R1          ;\_ Enable, reset FIFOs
                MVO     R1,         CC3.u0fcr   ;/
                MVO     R0,         CC3.u0ter   ; Enable transmitter
               
                CLRC
                JR      R5
                ENDP
    ENDI
