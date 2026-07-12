
; Author: Carl Mueller, Jr.
; Tweaked by:  Joe Zbiciak

JDIV        PROC

            ; Descr:   Signed integer divide. For a "fast" integer divide for
            ;          numbers less than $8000, use the "Fast" entry point.

            ; Input:   R1  = Dividend (Numerator)
            ;          R2  = Divisor  (Denominator)

            ; Output:  R0  = Quotient
            ;          R1  = Remainder
            ;          R2  = Divisor  (2's complement if Divisor negative)

            ; Notes:   - Quotient = 0 if you pass in a Divisor of 0 (undefined).
            ;          - Signed entry point handles values of -32,768 correctly.
            ;          - Register and space compatible with EXEC's signed
            ;            division routine at $1DFB.

            ; Costs:   40 locations

            MOVR    R1, R1              ; Dividend signed ?
            BPL     @@NumPlus           ; no,  so now check Divisor's sign

            NEGR    R1                  ; yes, so get 2's complement first

            MVO@    R5, R6              ; save RetAddr

            MVII    #@@Negate, R5       ; make Quotient negative on exit
@@NumPlus:  MOVR    R2, R0              ; Divisor ..
            BPL     @@DenPlus           ; .15 == 0 ? if yes, already positive

            NEGR    R2                  ; .15 == 1 ? if yes, make positive

            MVO@    R5, R6              ; save RetAddr

            MVII    #@@Negate, R5       ; make Quotient negative on exit

            BMI     @@DenMinus          ; == 32,768 ? if yes, special handling
@@Fast:     MOVR    R2, R0              ; Divisor ..
@@DenPlus:  BZE     @@DenZero           ; == 0 ? if yes, undefined -- return 0

            MVII    #$FFFF, R0          ; Count = 0
            CLRC
@@Count:    RRC     R0, 1               ; Count++
            SLL     R2, 1               ; Denominator <<= 1

            CMPR    R2, R1              ; Divisor * 2^X .. Dividend ?
            BC      @@Count             ; < ?  if yes, check next multiple
;           BNZE    @@Divide            ; > ?  if yes, past highest multiple

;           CLRR    R1                  ; Remainder = 0
;           INCR    R0                  ; Quotient.X = 1
@@Divide:;  COMR    R0
@@Iter:     SLR     R2, 1               ; Denominator >>= 1

@@DenMinus: SUBR    R2, R1              ; Remainder >= Divisor * 2^X ?
            ADCR    R7                  ; no,  so set Quotient.X = 0
            ADDR    R2, R1              ; yes, so set Quotient.X = 1
@@B0:       RLC     R0, 1               ; --Count == 0 ? (Quotient.X <- C)
            BC      @@Iter              ; no, so get more bits for Quotient
            COMR    R0
@@DenZero:
            JR      R5                  ; return to caller
@@Negate:
            NEGR    R0                  ; make Quotient negative (or positive)

            MVI@    R6, R7              ; return to caller (or Negate)

            ENDP

