;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  TTLSP     Display sprites for title screen.                             ;;
;;==========================================================================;;
TTLSP   PROC
        PSHR    R5

        ;;------------------------------------------------------------------;;
        ;;  Arrange for the title screen graphic to display.                ;;
        ;;------------------------------------------------------------------;;
        MVII    #LMPTITLE, R0       ;     \___ Abuse the rock/crat copyover
        MVO     R0,     RPTR        ;     /    to pull in title graphic. :-)

        MVII    #TITLESP,  R4       ;     \
        MVII    #SDAT + 2,  R5      ;      |-- Copy over the fixed title
        MVII    #3,     R1          ;     /    5-MOB pattern. 
@@tsplp
        MVI@    R4,     R0          ;     \
        MVO@    R0,     R5          ;      |
        MVI@    R4,     R0          ;      |
        MVO@    R0,     R5          ;      |
        MVI@    R4,     R0          ;      |
        MVO@    R0,     R5          ;      |__ Copy over 5 MOB per iter
        MVI@    R4,     R0          ;      |   for each of the three regs.
        MVO@    R0,     R5          ;      |   
        MVI@    R4,     R0          ;      |
        MVO@    R0,     R5          ;      |
        ADDI    #3,     R5          ;      |
        DECR    R1                  ;      |
        BNEQ    @@tsplp             ;     /
        

        ;;------------------------------------------------------------------;;
        ;;  Now do the little message fader.  We use MOB #7 for the 'comb'  ;;
        ;;  that fades messages in and out.                                 ;;
        ;;------------------------------------------------------------------;;
        MVI     SDAT + 7, R1        ;     \
        ADDI    #2,     R1          ;      |-- Move the "comb" right 2 pixels
        ANDI    #$FF,   R1          ;     /
        MOVR    R1,     R4          ;     Copy the X position 
        CMPI    #160,   R4          ;     Are we at the right of the screen?
        BNEQ    @@same_msg          ;     No:  Don't increment message number
        MVI     TMADDR, R5          ;     \
        INCR    R5                  ;      |-- Otherwise, advance to the next
        MVO     R5,     TMADDR      ;     /    message in our message ring.
@@same_msg

        ADDI    #_X.visb+_X.xsiz,R4 ;     \___ Store updated X register for
        MVO     R4,   SDAT + 7      ;     /    "comb" graphic.


;       MVI     SDAT + 15,  R4
;       ANDI    #_Y.ymir,   R4
;       XORI    #56 + _Y.yres + _Y.ymir, R4   
        MVII    #56 + _Y.yres + _Y.ymir, R4   
                                    ;     \    Store values for Y and A 
        MVO     R4,     SDAT + 15   ;      |-- registers for "comb" graphic
        MVI     COURSE,     R4
        ANDI    #$E,        R4
        ADDI    #CSTKCLR-8, R4
        MVI@    R4,         R2
        SLR     R2,         2
        SLR     R2,         2
        ANDI    #$F,        R2
        ADDI    #$FF8,      R2
        ANDI    #$1007,     R2
        ADDI    #LMPCARDx + 10*8 - X_TITL, R2
        MVO     R2,     SDAT + 23   ;     /

        CMPI    #160,   R1          ;     Are we off right side?
        BGE     @@offright          ;     Yes:  Do nothing for now.

        MOVR    R1,     R4          ;     \ 
        ANDI    #$7,    R4          ;      |-- If we're not at a card 
        CMPI    #6,     R4
        BNEQ    @@done              ;     /    boundary, then that's it!

        SLR     R1,     2           ;     \__  Convert X coord to card #
        SLR     R1,     1           ;     /    within row.
        MVI     TMADDR, R4          ;     Get our message number
        ADDI    #TMTBL, R4          ;     Index into the message table
        MVI@    R4,     R5          ;     Get the message pointer
        TSTR    R5                  ;     If it's null, time to reset pointer.
        BNEQ    @@tmok              ;     Otherwise, go to the message update.
        MVO     R5,     TMADDR      ;     Reset the message pointer
        MVI     TMTBL,  R5          ;     Get first message's message address
@@tmok
         
        MOVR    R1,     R0
        SARC    R0                  ;
        ADDR    R0,     R5          ;     Index into the message.

        ADDI    #$200+6*20, R1      ;     Point to appropriate place onscreen
        MVI@    R5,     R0          ;     Get a character from the message
        MOVR    R1,     R2          ;     \
        SARC    R2                  ;      |_ Pick odd/even half
        BNC     @@nos               ;      |
        SWAP    R0                  ;     /
@@nos   ANDI    #$7F8,  R0          ;     \
        XOR     TMCLR,  R0          ;      |
        MVI@    R1,     R2          ;      |_ Display it onscreen
        ANDI    #$2000, R2          ;      |
        XORR    R2,     R0          ;      |
        MVO@    R0,     R1          ;     /

@@done  PULR    R5                  ;
        B       UPBSP               ;     Update moon-buggy sprites

@@offright:
        CMPI    #$FE,   R1
        BNEQ    @@done

        MVII    #SCORE, R4
        MVI@    R4,     R0
        ADD@    R4,     R0
        ADD@    R4,     R0
        ADD@    R4,     R0
        BEQ     @@done

        MVI     TMADDR, R0
        SARC    R0
        BNC     @@final

        CALL    DISPPEAK
        DECLE   disp_ptr(11,0)
        B       @@done
@@final      
        CALL    DISPFINAL
        DECLE   disp_ptr(11,0)
        B       @@done

        ENDP

