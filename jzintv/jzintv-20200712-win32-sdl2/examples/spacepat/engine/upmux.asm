;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPMUX     Update sprite multiplexing.                                   ;;
;;==========================================================================;;
UPMUX   PROC
        PSHR    R5                  ;   9
        CLRR    R0                  ;   6
        MVO     R0,     SDATP       ;  11
                                    ;----
                                    ;  26

        ;;------------------------------------------------------------------;;
        ;;  Now that we know what sprites go in what groups, mux them into  ;;
        ;;  our object groups.  We keep a counter for each group that tells ;;
        ;;  us where we left off last frame when displaying sprites for     ;;
        ;;  that group.  We merely pick up at that point and start again.   ;;
        ;;                                                                  ;;
        ;;  The variables GP1CNT, GP2CNT tell us our starting point.        ;;
        ;;                                                                  ;;
        ;;  The object table consists of two arrays, the SPXYP array that   ;;
        ;;  holds our X/Y position as an 8.8 number.  The SPAT array holds  ;;
        ;;  object attributes, stored as an index into the SPATBL plus 1.   ;;
        ;;  Inactive objects have their SPAT value set to 0.  This allows   ;;
        ;;  gaps in the object table, simplifying bookkeeping elsewhere.    ;;
        ;;------------------------------------------------------------------;;
        MVI     GP1CNT, R1          ;  10
        MVII    #SPXY1, R4          ;   8 Point to Group 1's X/Y pos base
        MVII    #SPAT1 - 1, R2      ;   8 Point to Group 1's attr base
        ADDR    R1,     R2          ;   6 Offset to current counter offset
        SLL     R1,     1           ;   6 Offset to current counter offset
        ADDR    R1,     R4          ;   6 Offset to current counter offset
        MVII    #SDAT+2,R3          ;   8 Point to MOB #2.
        MVI     GP1MOB, R1          ;  10 
        B       @@gp1mobf           ;   9
                                    ;----
                                    ;  71
                                    ;  26 (caried forward)
                                    ;----
                                    ;  97

@@gp1skip:
        ADDI    #2,     R4          ;   8 Move to next X/Y pair
@@gp1mobl:
        CMPI    #SPAT1+MAXGP1-1,R2  ;   8 Count >= 5? (5 slots in group 1)
        BLT     @@1cntok            ; 7/9 If no, skip CLRR R2
        MVII    #SPXY1, R4          ;   8 Point to Group 1's X/Y pos base
        MVII    #SPAT1 - 1, R2      ;   8 Point to Group 1's attr base
@@1cntok:
        INCR    R2                  ;   6 Go to next attr entry
        MVI@    R2,     R5          ;   8 Get attribute #
        DECR    R5                  ;   6 Inactive object?
        BMI     @@gp1skip           ; 7/9 Yes:  Skip it.
                                    ;----
                                    ;     Assuming BMI not taken:
                                    ;  66 gp1skip to here, 1cntok not taken
                                    ;  58 gp1mobl to here, 1cntok not taken
                                    ;  52 gp1skip to here, 1cntok taken
                                    ;  44 gp1mobl to here, 1cntok taken

        ADDI    #SPATBL,R5          ;   8 Index into global attribute table

        MVI@    R4,     R0          ;   8 Get x position
        ANDI    #$FF,   R0          ;   8
        ADD@    R5,     R0          ;   8 Merge w/ x-pos attr template
        MVO@    R0,     R3          ;   9 Store to MOB X position 

        ADDI    #8,     R3          ;   8 Move to MOB Y register

        MVI@    R4,     R0          ;   8 Get y position
        ANDI    #$FF,   R0          ;   8
        ADD@    R5,     R0          ;   8 Merge w/ y-pos attr template
        MVO@    R0,     R3          ;   9 Store to MOB Y position 

        ADDI    #8,     R3          ;   8 Move to MOB A register

        MVI@    R5,     R0          ;   8 Get attr register
        MVO@    R0,     R3          ;   9 Store to MOB A register

        SUBI    #15,    R3          ;   8 Go to next MOB X register

@@gp1mobf
        DECR    R1                  ;   6 Any more MOBs to do?
        BPL     @@gp1mobl           ; 9/7 
                                    ;----
                                    ; 130 loop body
                                    ;  44 baseline for initial part
                                    ;----
                                    ; 174 baseline loop iter.

                                    ; 130 loop body
                                    ;  58 gp1mobl, 1cntok not taken (1/mux)
                                    ;----
                                    ; 188 once-per-mux iter.

                                    ; Worst case:  3 active + 1 wrap
                                    ; 348 (174 * 2)
                                    ; 188 (wrap iteration)
                                    ;  -2 (last iter)
                                    ;  97 (carried fwd)
                                    ;----
                                    ; 631
        

        SUBI    #SPAT1-1, R2        ;   8
        MVO     R2,     GP1CNT      ;  10 Save group 1's mux counter

        MVI     GP2MOB, R1          ;  10 Get # of MOBs in group 2
        MVI     GP2CNT, R0          ;  10 Get group 2's mux counter
        MVII    #SPXY2, R4          ;   8 Point to Group 2's X/Y pos base
        MVII    #SPAT2 - 1, R2      ;   8 Point to Group 2's attr base
        ADDR    R0,     R2          ;   6 Offset to current counter offset
        SLL     R0,     1           ;   6 Offset to current counter offset
        ADDR    R0,     R4          ;   6 Offset to current counter offset
        B       @@gp2mobf           ;   9
                                    ;----
                                    ;  81
                                    ; 631 (carried fwd)
                                    ;----
                                    ; 712

@@gp2skip:
        ADDI    #2,     R4          ;   8 Move to next X/Y pair
@@gp2mobl:
        CMPI    #SPAT2+MAXGP2-1,R2  ;  10 Count >= 7? (7 slots in group 2)
        BLT     @@2cntok            ; 7/9 If no, skip CLRR R2
        MVII    #SPXY2, R4          ;   8 Point to Group 2's X/Y pos base
        MVII    #SPAT2 - 1, R2      ;   8 Point to Group 2's attr base
@@2cntok:
        INCR    R2                  ;   6 Go to next attr entry
        MVI@    R2,     R5          ;   8 Get attribute #
        DECR    R5                  ;   6 Inactive object?
        BMI     @@gp2skip           ; 7/9 Yes:  Skip it.
                                    ;----
                                    ;     Assuming BMI not taken:
                                    ;  66 gp1skip to here, 1cntok not taken
                                    ;  58 gp1mobl to here, 1cntok not taken
                                    ;  52 gp1skip to here, 1cntok taken
                                    ;  44 gp1mobl to here, 1cntok taken
                                    
        ADDI    #SPATBL,R5          ;   8 Index into global attribute table

        MVI@    R4,     R0          ;   8 Get x position
        ANDI    #$FF,   R0          ;   8
        ADD@    R5,     R0          ;   8 Merge w/ x-pos attr template
        MVO@    R0,     R3          ;   9 Store to MOB X position 

        ADDI    #8,     R3          ;   8 Move to MOB Y register

        MVI@    R4,     R0          ;   8 Get y position
        ANDI    #$FF,   R0          ;   8
        ADD@    R5,     R0          ;   8 Merge w/ y-pos attr template
        MVO@    R0,     R3          ;   9 Store to MOB Y position 

        ADDI    #8,     R3          ;   8 Move to MOB A register

        MVI@    R5,     R0          ;   8 Get attr register
        MVO@    R0,     R3          ;   9 Store to MOB A register

        SUBI    #15,    R3          ;   8 Go to next MOB X register

@@gp2mobf
        DECR    R1                  ;   6 Any more MOBs to do?
        BPL     @@gp2mobl           ; 9/7 
                                    ;----
                                    ; 130 loop body
                                    ;  44 baseline for initial part
                                    ;----
                                    ; 174 baseline loop iter.

                                    ; 130 loop body
                                    ;  58 gp1mobl, 1cntok not taken (1/mux)
                                    ;----
                                    ; 188 once-per-mux iter.

                                    ; Worst case:  3 active + 1 wrap
                                    ; 348 (174 * 2)
                                    ; 188 (wrap iteration)
                                    ;  -2 (last iter)
                                    ;----
                                    ; 534

        SUBI    #SPAT2-1, R2        ;   8
        MVO     R2,     GP2CNT      ;  10 Save group 2's mux counter
                                    ;----
                                    ;  18
                                    ; 534 (carried fwd)
                                    ; 712 (carried fwd)
                                    ;----
                                    ;1264 (worst case)

                                    ;

        ;;------------------------------------------------------------------;;
        ;;  Clear out the unallocated MOBs.  Note that we never clear MOB   ;;
        ;;  #7.  That MOB may be allocated to the level-marker character.   ;;
        ;;  Rather, the LMCHAR code will clear that ahead of this function. ;;
        ;;------------------------------------------------------------------;;
        MOVR    R3,     R4          ;   6
        SUBI    #SDAT+7,R3          ;   8
        BPL     @@done              ; 9/7
                                    ;----
                                    ;  23
                                    ;1264 (carried fwd)
                                    ;----
                                    ;1287 (worst case)
                                    ; Note in worst case, none of MVO@ fire

        CLRR    R0                  ;   6
        MVO@    R0,     R4          ;   9
        ADDI    #@@d1,  R3          ;   8
        MOVR    R3,     PC          ;   7

        MVO@    R0,     R4          ;   9
        MVO@    R0,     R4          ;   9
        MVO@    R0,     R4          ;   9
        MVO@    R0,     R4          ;   9
        NOP                         ;   6
@@d1:   NOP

@@done: MVII    #SDAT,  R0          ;   8
        MVO     R0,     SDATP       ;  11
        PULR    PC                  ;  11 
                                    ;----
                                    ;  30
                                    ;1287
                                    ;  12 CALL overhead
                                    ;====
                                    ;1329
                               
        ENDP
