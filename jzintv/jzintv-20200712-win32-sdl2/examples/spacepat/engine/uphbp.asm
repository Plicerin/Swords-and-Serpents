;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPHBP     Do all the horizontal-bullet related updates.                 ;;
;;==========================================================================;;
UPHBP   PROC

        ;;------------------------------------------------------------------;;
        ;;  If we're displaying a horizontal bullet, redisplay it.          ;;
        ;;------------------------------------------------------------------;;
        MVI     HBCOL1, R1          ;  10 Get horizontal bullet column
        SLR     R1,     2           ;   8
        MVO     R1,     HBCOL0      ;  11 
        DECR    R1                  ;   6 Zero means no horizontal bullet
        BMI     @@nohb              ; 7/9 Skip if no bullet
        ADDI    #GROW,  R1          ;   8 Make ptr to screen
        MVI@    R1,     R0          ;   8 Get old data
        ANDI    #$1F8,  R0          ;   8 Can we display here?
        BEQ     @@disphb            ; 7/9 If zero, all's cool.
                                    ;----
                                    ;  73

        ;;------------------------------------------------------------------;;
        ;;  We can't display, so we must've hit something!                  ;;
        ;;------------------------------------------------------------------;;
        MOVR    R1,     R4          ;   6 \
        SLR     R0,     2           ;   8  |
        SLR     R0,     1           ;   6  |
        SUBI    #RCARD, R0          ;   8  |-- Did we hit a rock?
        BLT     @@killhb            ; 7/9  |
        CMPI    #7,     R0          ;   8  |
        BGE     @@killhb            ; 7/9 /
                                   
        SLL     R0,     1           ;   6 \
        ADDR    R0,     PC          ;   7  |
        B       @@rk12a             ;   9  |
        B       @@rk12b             ;      |
        B       @@rk12a             ;      |-- Yes:  Dispatch to handler for
        B       @@rk12b             ;      |   specific rock we hit.
        B       @@rk3a              ;      |
        B       @@rk3b              ;      |
;       B       @@rk3c              ;     /
                                    ;----
                                    ;  72
                                    ;  73 (carried forward)
                                    ;----
                                    ; 145

@@rk3c  DECR    R4                  ;   6
@@rk3b  DECR    R4                  ;   6
        CLRR    R1                  ;   6 kill hb right away
@@rk3a  MVII    #1,     R0          ;   8 Rock 3, first card 
        MVO@    R0,     R4          ;   9 \ 
        MVII    #RCARD2x, R0        ;   8  |__ For Rock 3, demote to Rock 2
        MVO@    R0,     R4          ;   9  |   starting at Rock 3's 2nd card.
        ADDI    #8+RCS1.sc750-$8000,R0 ;8  |
        MVO@    R0,     R4          ;   9 /
        B       @@donerock          ;   9
                                    ;----
                                    ;  78
                                    ; 145 (carried fwd)
                                    ;----
                                    ; 223
                                   
@@rk12b DECR    R4                  ;   6
        CLRR    R1                  ;   6 kill hb right away
@@rk12a MVII    #$1,    R0          ;   8 Rock 1/2, first card 
        MVO@    R0,     R4          ;   9 \_ For rock 1 & 2, just nuke rock.
        MVO@    R0,     R4          ;   9 /
                                    ;----
                                    ;  38
                                    ; 145 (carried fwd)
                                    ;----
                                    ; 183
                                   
@@donerock:                        
        CSTSCO  1000                ;   ? 1000 points per rock segment

;       MOVR    R5,     R0          ;
        CALL    PLAYSFX             ;  75 Yes: Play a sound effect.
        DECLE   FXLGEXP             ;
;       MOVR    R0,     R5          ;

        ; Decide if we're going to let the bullet animate for the rest of
        ; this card.
        TSTR    R1                  ;   6
        BEQ     @@killhb            ; 7/9

        MVI     HBCOL1, R0          ;  10 \
        COMR    R0                  ;   6  |
        ANDI    #3,     R0          ;   8  |- R0:  # frames left in this card
        BEQ     @@killhb            ; 7/9 /

        MVO     R0,     HBCNT       ;  11 \   Yes:  Let it animate to end of
        MVII    #1,     R0          ;   8  |- card, but kill it if UPCRD 
        MVO     R0,     HBKOS       ;  11 /   decides it's time to scroll.
        B       @@disphb            ;   9
                                    ;----
                                    ;  83

@@killhb:                          
        CLRR    R0                  ;   6 \
        MVO     R0, HBKOS           ;  11  |
        MVO     R0, HBDATA          ;  11  |
        MVO     R0, HBCOL1          ;  11  |-- We hit the rock, so nuke the
        INCR    R0                  ;   6  |   bullet too.
        MVO     R0, HBCOL0          ;  11 /   
        B       @@nohb              ;   9
                                    ; (not critical path)
                                   
@@disphb:                          
        MVI@    R1,     R0          ;   8 \
        ANDI    #$8600, R0          ;   8  |__ Display bullet, preserving
        XORI    #HBCARDx, R0        ;   8  |   any flag bits we may have set.
        MVO@    R0,     R1          ;   9 /
                                    ;----
                                    ;  33
                                    ;
        ;;------------------------------------------------------------------;;
        ;;  Update the horizontal bullet position if in flight.             ;;
        ;;------------------------------------------------------------------;;
        MVI     HBCOL1, R0          ;  10 Get bullet column
        INCR    R0                  ;   6 Move by one pixel

        MVI     HBCNT,  R2          ;  10 Decrement our flight counter
        DECR    R2                  ;   6
        BMI     @@hbdie             ; 7/9 Kill the bullet if it dies.
        
        MVO     R2,     HBCNT       ;  11 Store updated flight counter

        MVI     HBDATA, R1          ;  10 \___ Bullet moves right by 2 pixels
        SLR     R1,     2           ;   8 /
        BNEQ    @@hbcok             ; 7/9 If bullet still in card, that's it.

        MVII    #$C0,   R1          ;   8 Put pixels at left of byte.
        B       @@hbcok             ;   9 
                                    ;----
                                    ;  92
                                    ;  33 (carried fwd)
                                    ;  75 (carried fwd)
                                    ;  83 (carried fwd)
                                    ; 223 (carried fwd)
                                    ;----
                                    ; 506

@@hbdie CLRR    R0                  ;     No:  Bullet must die.
        CLRR    R1                  ;
@@hbcok MVO     R0,     HBCOL1      ;  11 Store new column 
        MVO     R1,     HBDATA      ;  11 Store new pixel data.
                                    ;----
                                    ;  22
                                    ; 506 (carried fwd)
                                    ;----
                                    ; 528

@@nohb:
        ;;------------------------------------------------------------------;;
        ;;  Decrement our re-fire counter.  Rate-limits the buggy's firing. ;;
        ;;------------------------------------------------------------------;;
        MVI     FCNT,   R0          ;  10
        DECR    R0                  ;   6
        BMI     @@fcntok            ; 7/9
        MVO     R0,     FCNT        ;  11
@@fcntok

        MVI     HBCNT2, R0          ;  10
        DECR    R0                  ;   6
        BMI     @@hbcnt2ok          ; 7/9
        MVO     R0,     HBCNT2      ;  11
@@hbcnt2ok                          ;----
                                    ;  68
                                    ; 528
                                    ;----
                                    ; 596

                                    ; Note: omits cost of CSTSCO.

;       JR      R5
        ENDP
