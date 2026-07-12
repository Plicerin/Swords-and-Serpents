;; ======================================================================== ;;
;;  Integer Square Root function                        Carl Mueller, Jr.   ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      R1  Radicand (value to take square root of), eg. distance squared   ;;
;;                                                                          ;;
;;  OUTPUTS                                                                 ;;
;;      R0  Constant:  $0080                                                ;;
;;      R1  Unmodified                                                      ;;
;;      R2  sqrt( R1 )                                                      ;;
;;                                                                          ;;
;;  DESCRIPTION                                                             ;;
;;      Returns the integer square root of R1 in R2.  That is, R2 will      ;;
;;      contain the largest non-negative integer whose square is less       ;;
;;      than or equal to R1.                                                ;;
;;                                                                          ;;
;;      The code runs between 451 and 571 cycles, depending on the exact    ;;
;;      input.                                                              ;;
;;                                                                          ;;
;;  IMPLEMENTATION DETAILS                                                  ;;
;;      This implementation relies on a couple tricks to achieve its        ;;
;;      compact size and fast running time.  The algorithm guesses bits     ;;
;;      of the square root starting at the MSB of the result, working       ;;
;;      toward the LSB.                                                     ;;
;;                                                                          ;;
;;      Register usage:                                                     ;;
;;                                                                          ;;
;;      R0 serves a dual purpose in the code.  Its primary role is to       ;;
;;      hold the square of the next "guess" bit.  It also doubles as        ;;
;;      a loop counter, limiting the loop to 8 iterations.                  ;;
;;                                                                          ;;
;;      R2 initially just holds the radicand.  As the algorithm runs,       ;;
;;      it also accumulates bits of the square root in its LSBs.            ;;
;;                                                                          ;;
;;      R5 contains (Guess + NewBit) squared, minus 1.  This value          ;;
;;      represents how much "guess squared" will change by if we set        ;;
;;      the next bit in the square.                                         ;;
;;                                                                          ;;
;;      For the full description of how this algorithm works, please see    ;;
;;      the accompanying documentation.                                     ;;
;;                                                                          ;;
;;  EXEC COMPARISON                                                         ;;
;;      This routine is nearly an exact drop-in replacement for the         ;;
;;      EXEC's square root routine at $1E23.  It occupies exactly the       ;;
;;      same number of words (21 words total), and provides the same        ;;
;;      register interface in R1 and R2.  R0 differs however -- this        ;;
;;      code returns $0080 in R0 where the EXEC returns 0 or 1.             ;;
;;                                                                          ;;
;;      Unlike the EXEC's square root routine, this routine is entirely     ;;
;;      self contained, computing the square root directly without calls    ;;
;;      to outside code.  The EXEC's code performs repeated divides to      ;;
;;      refine its guesses.  As a result, this code is significantly        ;;
;;      faster, and uses less stack space.                                  ;;
;;                                                                          ;;
;;  PURISTS NOTE (10-bit ROM)                                               ;;
;;      The two 16-bit MVII instructions below can be replaced with short   ;;
;;      two-instruction sequences, to allow the routine to fit in a GI      ;;
;;      10-bit ROM, such as the ROM that holds the EXEC.                    ;;
;;                                                                          ;;
;;                  MVII    $8000, R0  ->  SUBR    R0, R0                   ;;
;;                  ..                     RRC     R0, 1                    ;;
;;                  MVII    $FFFF, R5  ->  CLRR    R5                       ;;
;;                  ..                     DECR    R5                       ;;
;;                                                                          ;;
;;      This change does not affect the size of the code, and would only    ;;
;;      slow the entire function by 8 cycles total (approximately 2%).      ;;
;;                                                                          ;;
;;  CREDITS                                                                 ;;
;;      Code by Carl Mueller, Jr.                                           ;;
;;      Documentation by Joe Zbiciak.                                       ;;
;;      Inspired by ideas from Mark Borgerding, Paul Hsieh and Joe Zbiciak. ;;
;;                                                                          ;;
;; ======================================================================== ;;

ISQRT       PROC
            PSHR    R5              ;   9   save return address

            MVII    $8000,  R0      ;   8   SquareBit = 1/2 * Bit^2, Count = 8
            MOVR    R1,     R2      ;   6   Radicand or distance-squared in R2 
            MVII    $FFFF,  R5      ;   8   Update = (Guess + Bit)^2 - 1
                                    ;----
                                    ;  33
                                          
@@Cont:     SUBR    R0,     R5      ;   6   Update -= 1/4 * Bit^2
                                          
            SLLC    R2,     1       ;   6   Was Remainder's MSB set ?
            ADCR    PC              ;   7   If yes, skip CMPR & fall into "B1"
                                          
            CMPR    R2,     R5      ;   6   Update <= Remainder ?
            BC      @@B0            ; 9/7   No, so set Result's current LSB = 0
                                          
@@B1:       SUBR    R5,     R2      ;   6   Remainder -= ( Update - 1 )
            ADDR    R0,     R5      ;   6   -.
            ADDR    R0,     R5      ;   6   -' Update += Bit^2
                                          
@@B0:       SLR     R0,     1       ;   6   SquareBit >>= 1
            BPL     @@Cont          ; 7/9   if --Count == 0, handled final LSB
                                    ;----
                                    ; 518 = 65*8-2  
                                    ;       (Worst case path: 
                                    ;        ADCR not taken, BC not taken)
                                    ;+ 33   carried forward
                                    ;----
                                    ; 551   worst case
                                          
                                    ; ... or ...
                                    ;
                                    ; 398 = 50*8-2  
                                    ;       (Best case path: 
                                    ;        ADCR not taken, BC taken)
                                    ;+ 33   carried forward
                                    ;----
                                    ; 431   best case

            ANDI    $00FF,  R2      ;   8   isolate Result in bits 0-7
            PULR    PC              ;  12   Return to isqrt's caller
                                    ;----
                                    ;  20
                                    ; 551  (worst case)
                                    ;----
                                    ; 571  (worst case)

                                    ; ... or ...
                                    ;  20
                                    ; 431  (best case)
                                    ;----
                                    ; 451  (best case)

            ENDP
