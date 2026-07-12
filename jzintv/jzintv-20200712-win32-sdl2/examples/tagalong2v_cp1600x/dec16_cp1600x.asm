;* ======================================================================== *;
;*  The routines and data in this file (dec16only.asm) are dedicated to     *;
;*  the public domain via the Creative Commons CC0 v1.0 license by its      *;
;*  author, Joseph Zbiciak.                                                 *;
;*                                                                          *;
;*          https://creativecommons.org/publicdomain/zero/1.0/              *;
;* ======================================================================== *;

;; ======================================================================== ;;
;;  Quick-and-dirty update to use LTO ISA instructions.                     ;;
;;  Not a drop-in replacement.  Redefines meaning of R2 and R3.             ;;
;;                                                                          ;;
;;  DEC16                                                                   ;;
;;      Displays a 16-bit decimal number on the screen with leading blanks  ;;
;;      in a field up to 5 characters wide.  Displays all blanks if the     ;;
;;      number is zero.                                                     ;;
;;                                                                          ;;
;;  DEC16A                                                                  ;;
;;      Same as DEC16, only displays leading zeroes.                        ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;      R0 -- Number to be displayed in decimal.                            ;;
;;      R2 -- Number of digits to suppress (0 .. 5; 5 - field_width)        ;;
;;      R3 -- Color mask / screen format word (Added to digit.)             ;;
;;      R4 -- Screen offset (lower 8-bits)                                  ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- Unmodified                                                    ;;
;;      R1 -- Trashed                                                       ;;
;;      R2 -- Multiplied by 4.                                              ;;
;;      R3 -- Color mask, with bit 15 cleared                               ;;
;;      R4 -- Pointer to character just right of string                     ;;
;;      R5 -- Unmodified                                                    ;;
;;      X0 -- Trashed                                                       ;;
;;      X1 -- Trashed                                                       ;;
;;      X2 -- Zeroed                                                        ;;
;; ======================================================================== ;;
DEC16:  PROC
        ADDR    R3,     R3      ; \_ Set LSB to 1 to indicate leading spaces.
        INCR    R3              ; /
        INCR    R7              ; Skip the ADDR.
DEC16A: ADDR    R3,     R3      ; Set LSB to 0 to indicate leading zeros.

        SUB3    5,  R2, X2      ; X3 is number of digits to display.
        I2BCD   0,  R0, X0      ; BCD decode the number
        SLL     R2,     2       ; \_ Pop off suppressed digits into X1.
        SHLU3   X0, R2, X0      ; /
        AND3    X1, $F, X1      ; Keep only the last one.

@@digit_loop:
        MOVR    R3,     R1
        SARC    R1,     1
        TSTBNZ  X1,     @@non_zero
        BC      @@no_digit
@@non_zero:
        ANDI    #$FFFE, R3
        MPY16   X1, 8,  X1
        ADD     X1,     R1
        ADDI    #$80,   R1
        
@@no_digit:
        MVO@    R1,     R4
        
        SHLU3   X0, 4,  X0      ; Pop next digit into X1
        DECBNZ  X2, @@digit_loop

        SLR     R3,     1       ; Restore R3
        JR      R5
        ENDP
