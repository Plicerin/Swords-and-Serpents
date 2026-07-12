;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  CLRSP     Clear all the sprites.                                        ;;
;;==========================================================================;;
CLRSP   PROC
        MVII    #SDAT,  R4          ;     Just clear out the SDAT shadow regs
        INCR    PC
@@1:    CLRR    R4                  ;     Alt: Clear out the actual MOB regs

        CLRR    R0                  ;
        MVII    #$18/8, R1          ;
@@lp1:
        MVO@    R0,     R4          ;     \
        MVO@    R0,     R4          ;      |
        MVO@    R0,     R4          ;      |
        MVO@    R0,     R4          ;      |
        DECR    R1                  ;      |-- Just pump the MOBs full of 
        MVO@    R0,     R4          ;      |   zeros.
        MVO@    R0,     R4          ;      |
        MVO@    R0,     R4          ;      |
        MVO@    R0,     R4          ;     / 
        BNEQ    @@lp1               ;

        JR      R5
        ENDP
