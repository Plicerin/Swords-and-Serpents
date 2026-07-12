;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  TWINKLE -- Twinkles the stars in the sky.                               ;;
;;==========================================================================;;
TWINKLE     PROC
            PSHR    R5
           
            CALL    RAND
           
            MOVR    R0,     R3
            ANDI    #$FF,   R0
           
            CMPI    #60,    R0
            BGE     @@done
           
            MVII    #$200,  R2
            ADDR    R0,     R2
           
            ANDI    #$700,  R3
            BEQ     @@toggle
            CLRR    R1
            B       @@clear

@@toggle:
            MVI     RSEED,  R0
            ANDI    #3,     R0

            MVII    #@@tbl, R1
            ADDR    R0,     R1
            MVI@    R1,     R1
           
            XOR@    R2,     R1
            MOVR    R1,     R3
            ANDI    #$FF*8, R3
            BNEQ    @@ok
            XOR@    R2,     R1
@@ok:
@@clear:
            MVO@    R1,     R2
           
@@done:     PULR    PC
           
@@tbl:      DECLE   $2B*8 + X_TAN + $800
            DECLE   $2B*8 + X_CYN + $800
            DECLE   $2B*8 + X_YGR + $800
            DECLE   $2B*8 + X_GRY + $800
            ENDP
