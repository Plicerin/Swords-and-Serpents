;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  CKBRC     Check buggy vs. rocks and craters.                            ;;
;;==========================================================================;;
CKBRC   PROC

        MVI     TXLO,   R1          ;  10 Get x position
        MOVR    R1,     R2          ;   6 \
        SLR     R2,     2           ;   8  |__ Point R2 at card on ground to
        SLR     R2,     1           ;   6  |   check against.
        MOVR    R2,     R4          ;   6 use auto-incr pointer
        MOVR    R2,     R5          ;   6 use auto-incr pointer
        ADDI    #GROW,  R4          ;   8 /
        ADDI    #GROW+20, R5        ;   8 /
                                         
        ANDI    #7,     R1          ;   8
        SUBI    #8,     R1          ;   8
        MVI     PGPHAS, R0          ;  10
        ANDI    #7,     R0          ;   8
        ADDR    R0,     R1          ;   6
        NEGR    R1                  ;   6 offset = -((buggy_x&7-8) + (gphase&7))
        MVII    #3,     R2          ;   8 Check 3 cards
                                    ;----
                                    ; 112
@@i_loop:                                
        MVI@    R4,     R3          ;   8 Get card for maybe-rock
        TSTR    R3                  ;   6 MSB tells us if it's maybe a rock
        BPL     @@buggy_ok          ; 7/9 set == maybe a rock
        ANDI    #$1F8,  R3          ;   8 Extract card number
        BNEQ    @@not_crater        ; 7/9 If != 0, it's not a crater
        MVI@    R5,     R3          ;   8 Get card for maybe-crater
        ANDI    #$1F8,  R3          ;   8 Extract card number
        DECR    R5                  ;   6
@@not_crater                        ;----
                                    ;  43 (worst case)

        SLR     R3,     2           ;   8 \
        SLR     R3,     1           ;   6  |
        SUBI    #RCARD, R3          ;   8  |-- if it's a rock card.  Skip it
        BLT     @@buggy_ok          ; 7/9  |   if it's not a rock.
        CMPI    #12,    R3          ;   8  |
        BGE     @@buggy_ok          ; 7/9 /
                                    ;----
                                    ;  44 (worst case)
                                    ;  43 (carried forward)
                                    ;----
                                    ;  87

                                   
        ; Calculate offset and do the table lookup.
                                   
        ADDI    #MJHIDX,R3          ;   8 Get per-card index
        MVI@    R3,     R3          ;   8 Get index into MinJumpHeight table
        ADDR    R1,     R3          ;   6 Add our buggy_x/gphase offset
        CLRC                        ;   6
        RRC     R3                  ;   6
        MVI@    R3,     R3          ;   8
        ADCR    PC                  ;   7
        SWAP    R3                  ;   6
        ANDI    #$1FE,  R3          ;   8
                                   
        CMP     JHGT,   R3          ;  10
        BLE     @@maybe_score       ; 7/9 Buggy's ok, try to score.
                                    ;----
                                    ;  65 (worst case)
                                    ;  87 (carried forward)
                                    ;----
                                    ; 152

        CLRR    R0                  ;   6 \__ Set the "We Died!" flag
        MVO     R0,     MOBHIT      ;  11 /
        MVO     R0,     DEFSCO      ;  11
        MVO     R0,     LANDED      ;  11
        B       @@leave             ;   9
                                    ; (won't bother counting "died" case)

@@maybe_score
        DECR    R4                  ;   6
        MVI@    R4,     R3          ;   8 \
        MOVR    R3,     R0          ;   6  |
        ANDI    #$0600, R3          ;   8  |  Bits 9/10 hold score for
        BEQ     @@buggy_ok          ; 7/9  |- object.  1 = 500, 2 = 750
        XORR    R3,     R0          ;   6  |  3 = 1000.  Clear to 0 on
        DECR    R4                  ;   6  |  scoring.
        MVO@    R0,     R4          ;   9 /

        SLR     R3                  ;   6 \
        SWAP    R3                  ;   6  |
        INCR    R3                  ;   6  |- Score(250) * (bit[10:9] + 1)
        MOVR    R3,     R0          ;   6  |
        SLL     R3,     2           ;   8 /

        ADD     DEFSCO, R3          ;  10 \ 
        ADDR    R0,     R3          ;   6  |- Add to deferred score
        MVO     R3,     DEFSCO      ;  11 /
                                    ;----
                                    ; 115
                                    ; 152 (carried forward)
                                    ;----
                                    ; 267
@@buggy_ok:                        
        INCR    R5                  ;   6
        ADDI    #8,     R1          ;   8 Move offset by 8
        DECR    R2                  ;   6
        BNEQ    @@i_loop            ; 7/9
                                    ;----
                                    ;  29
                                    ; 267 (carried forward)
                                    ;----
                                    ; 296 per iteration
                                    ;==== x 3 iterations
                                    ; 888
                                    ; 112 (carried forward)
                                    ;----
                                    ;1000
        MVI     LANDED, R0
        SLL     R0,     1
        MVO     R0,     LANDED

                                   
        ;; ---------------------------------------------------------------- ;;
        ;;  Note:  Above cycle analysis is very pessimistic.  The full      ;;
        ;;  code "maybe_score" runs on at most 1 of the 3 iterations.       ;;
        ;;  This shaves 156 cycles.                                         ;;
        ;; ---------------------------------------------------------------- ;;


@@leave:                           
                                   
;       JR      R5                  ;   7
        ENDP

