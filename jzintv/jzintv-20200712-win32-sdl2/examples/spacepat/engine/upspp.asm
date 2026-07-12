;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPSPP     Updates sprite positions based on velocities                  ;;
;;==========================================================================;;
UPSPP   PROC
;       PSHR    R5                  ;

        
        ;;------------------------------------------------------------------;;
        ;;  Determine if the display scrolled horizontally by 1 pixel       ;;
        ;;------------------------------------------------------------------;;
        MVI     PGPHAS, R0          ;  10 \
        CMP     PPGPHA, R0          ;  10  |- See if screen moved
        MVO     R0,     PPGPHA      ;  11 /
        BEQ     @@no_hscroll        ; 7/9
                                    ;----
                                    ;  38 (fallthru)

        ;;------------------------------------------------------------------;;
        ;;  When horiz-scrolling, update the level marker if it's active.   ;;
        ;;------------------------------------------------------------------;;
@@lmscroll:
        MVI     LMCNT,  R1          ;  10 Get current level marker posn
        MVO     R1,     SDAT+7      ;  11 Funky MOB 7 disable if no LMCHAR
        DECR    R1                  ;   6 Slide it left 1
        BMI     @@no_level_marker   ; 7/9 \
        MVO     R1,     LMCNT       ;  11  |- Store it, or leave if none.
        BEQ     @@no_level_marker   ; 7/9 /
                                    ;----
                                    ;  52 (fallthru)


        MVII    #SPATLM,    R4      ;   8 point to level marker sprite attrs
        MVI@    R4,     R0          ;   8 get level marker X info
        ADDR    R1,     R0          ;   6 offset for X position
        MVO     R0,     SDAT+7      ;  11 store to MOB 7's X reg.
        MVI@    R4,     R0          ;   8 get level marker Y info
        MVO     R0,     SDAT+15     ;  11 store to MOB 7's Y reg.
        MVI     LMCHAR, R0          ;  10
        SLL     R0,     1           ;   6
        SLL     R0,     2           ;   8
                                    ;----
                                    ;  76


        CMPI    #$200,  R0          ;   8 is it a major ckpt?
        BNC     @@not_major_ckpt    ; 7/9   

        SUBI    #$100,  R0          ;   8 rewind back to uppercase
        MVI     TIMTIC, R1          ;  10 \ 
        ANDI    #4,     R1          ;   8  |
        BNEQ    @@not_major_ckpt    ; 7/9  |- Blink major checkpoints
        XORI    #X_GRY, R0          ;   8  |
        B       @@skip_color        ;   9 /
                                    ;----
                                    ;  65 (fall thru -> skip_color)
                                    ;  50 (2nd br to not_major_ckpt)

@@not_major_ckpt
        MVI     COURSE, R1          ;  10 \
        ADDI    #CCTBL, R1          ;   8  |- add course-specific color.
        ADD@    R1,     R0          ;   8 /
@@skip_color
        XOR@    R4,     R0          ;   8 get level marker other attributes
        MVO     R0,     SDAT+23     ;  11 store to MOB 7's A reg.
                                    ;----
                                    ;  45
                                    ;  50 (carried fwd worst case)
                                    ;  76 (carried fwd)
                                    ;  52 (carried fwd)
                                    ;  38 (carried fwd)
                                    ;----
                                    ; 261
@@no_level_marker:
@@done_level_marker:
        CLRC                        ;   4 C=0 means screen scrolled
        INCR    PC                  ;   7 Skip SETC below
                                    ;----
                                    ; 272 (worst case)
@@no_hscroll:
        SETC                        ;   4

        ;;------------------------------------------------------------------;;
        ;;  Update the X/Y positions of all 12 possible sprites             ;;
        ;;  This includes scrolling objects one pixel left horizontally if  ;;
        ;;  the screen scrolled by one pixel.                               ;;
        ;;------------------------------------------------------------------;;

        MVII    #SPXYP, R4          ;   8 Point to X/Y position table
        MVII    #SPXYV, R5          ;   8 Point to X/Y velocity table
        MVII    #2,     R2          ;   8 Rewind offset
        BC      @@no_hscroll_1      ; 7/9 Alternate update if no scroll.

                                    ;----
                                    ;  31 (fall-thru is overall worst case)
                                    ; 272 (fwd)
                                    ;----
                                    ; 303

@@sph   SET     0
        REPEAT  5 

        MVI@    R5,     R0          ;   8 Get velocity
        ADD@    R4,     R0          ;   8 Add velocity to position
        ADCR    R0                  ;   6 end-around carry for 1s compl
        SUB     SPHSCR+@@sph, R0    ;  10 Adjust for horizontal scroll
@@sph   SET     @@sph+1

        MVI@    R5,     R1          ;   8 Get velocity
        ADD@    R4,     R1          ;   8 Add velocity to position
        ADCR    R1                  ;   6 end-around carry for 1s compl

        SUBR    R2,     R4          ;   6 Rewind
        MVO@    R0,     R4          ;   9 Store new X position
        MVO@    R1,     R4          ;   9 Store new Y position
        ENDR                        ;----
                                    ; 390 (5 iterations * 78)

@@l
        REPEAT  2 
        MVI@    R5,     R0          ;   8 Get velocity
        ADD@    R4,     R0          ;   8 Add velocity to position
        ADCR    R0                  ;   6 end-around carry for 1s compl

        MVI@    R5,     R1          ;   8 Get velocity
        ADD@    R4,     R1          ;   8 Add velocity to position
        ADCR    R1                  ;   6 end-around carry for 1s compl

        SUBR    R2,     R4          ;   6 Rewind
        MVO@    R0,     R4          ;   9 Store new position
        MVO@    R1,     R4          ;   9 Store new position
        ENDR                        ;----
                                    ; 136 (2 iter * 68)
       
@@no_hscroll_1:
        MVI@    R5,     R0          ;   8 Get velocity
        ADD@    R4,     R0          ;   8 Add velocity to position
        ADCR    R0                  ;   6 end-around carry for 1s compl

        MVI@    R5,     R1          ;   8 Get velocity
        ADD@    R4,     R1          ;   8 Add velocity to position
        ADCR    R1                  ;   6 end-around carry for 1s compl

        SUBR    R2,     R4          ;   6 Rewind
        MVO@    R0,     R4          ;   9 Store new position
        MVO@    R1,     R4          ;   9 Store new position

        MVI@    R5,     R1          ;   8 Get velocity
        ADD@    R4,     R1          ;   8 Add velocity to position
        ADCR    R1                  ;   6 end-around carry for 1s compl
        DECR    R4                  ;   6 Rewind
        MVO@    R1,     R4          ;   9 Store new position
                                    ;----
                                    ; 105
                                    ; 136 (from @@l to @@no_hscroll)
                                    ;----
                                    ; 241
                                    


                                    ; 482 (2 iters from @@l to here)
        CMPI    #SPXYV+24, R5       ;  16 (8 * 2) 
        BLT     @@l                 ;  16 (9 + 7)
                                    ;----
                                    ; 514
                                    ; 390 (first 5 iters)
                                    ; 303 (carried forward)
                                    ;----
                                    ;1207

;       PULR    PC

        ENDP
