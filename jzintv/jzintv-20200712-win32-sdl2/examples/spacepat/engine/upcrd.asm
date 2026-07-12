;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPCRD     Do card-oriented screen updates (scroll cards, decode world)  ;;
;;==========================================================================;;
UPCRD   PROC
;       PSHR    R5

        ;;------------------------------------------------------------------;;
        ;;  If we're displaying a horizontal bullet, undisplay it.          ;;
        ;;------------------------------------------------------------------;;
        MVI     HBCOL0, R1          ;  10 Get horizontal bullet column
        SUBI    #2,     R1          ;   8 0 means no horizontal bullet
                                    ;     1 means bullet going away
        BMI     @@nohb0             ; 7/9 Skip if no bullet
        ADDI    #GROW+1,R1          ;   8 Make ptr to screen
        MVI@    R1,     R0          ;   8 \
        ANDI    #$8E00, R0          ;   8  |-- Undisplay the bullet
        MVO@    R0,     R1          ;   9 /
@@nohb0:                            ;----
                                    ;  58

        ;;------------------------------------------------------------------;;
        ;;  Determine if we need to move the "ground terrain" by a card.    ;;
        ;;------------------------------------------------------------------;;
        MVI     PGPHAS, R0          ;  10 Get ground phase
        SLR     R0,     2           ;   8
        SLR     R0,     1           ;   6 Bits 7..3 are card offset
        CMP     PGCARD, R0          ;  10 Same as before?
        BEQ     @@no_bot            ; 7/9 Don't do the ground then.
        MVO     R0,     PGCARD      ;  11 save new ground card offset.
                                    ;----
                                    ;  52

        MVI     HBKOS,  R0          ;  10
        DECR    R0                  ;   6
        BMI     @@nohbkos           ; 7/9

        CLRR    R0                  ;   6 \
        MVO     R0, HBKOS           ;  11  |
        MVO     R0, HBDATA          ;  11  |
        MVO     R0, HBCOL1          ;  11  |-- We hit the rock, so nuke the
        INCR    R0                  ;   6  |   bullet too.
        MVO     R0, HBCOL0          ;  11 /   
@@nohbkos                           ;----
                                    ;  79
                                    ;  52 (carried forward)
                                    ;  58 (carried forward)
                                    ;----
                                    ; 189 (worst case)

        ;;------------------------------------------------------------------;;
        ;;  Update the crater-maker refire counter.                         ;;
        ;;------------------------------------------------------------------;;
        MVI     CRATCNT, R3         ;  10 \
        DECR    R3                  ;   6  |__ Decrement the crater re-fire
        BMI     @@ccz               ; 7/9  |   counter.  Don't let it go -ve.
        MVO     R3,     CRATCNT     ;  11 /
@@ccz:                              ;----
                                    ;  34
                                    ; 189 (carried forward)
                                    ;----
                                    ; 223
                                    
        ;;------------------------------------------------------------------;;
        ;;  Scroll the ground by one card.                                  ;;
        ;;------------------------------------------------------------------;;
        MVII    #GROW,      R4      ;   8
        MVII    #GROW+1,    R5      ;   8
                                    
        MVI     GROW,       R0      ;  10
        ANDI    #$2000,     R0      ;   8
        XOR@    R5,         R0      ;   8
                                    ;----
                                    ;  42
                                    
@@crow  MVO@    R0,         R4      ;   9
                                    
        REPEAT  18                  
        MVI@    R5,         R0      ;   8
        MVO@    R0,         R4      ;   9
        ENDR                        ;----
                                    ; 306
                                    
        INCR    R5                  ;   6
        INCR    R4                  ;   6
        MVI@    R5,         R0      ;   8
        CMPI    #GROW+40,   R5      ;   8
        BLT     @@crow              ; 9/7
                                    ;----
                                    ; 702 (2 iterations: 352 + 350)
                                    ;  42 (carried forward)
                                    ;----
                                    ; 744


                                   
    IF 0
        MVI     EMODE,  R0          ;  10 \
        CMPI    #2,     R0          ;   8  |- Skip decoding rocks (title)
        BEQ     @@done_upcrd        ;   9 /    
                                    ;----
                                    ;  27
                                    ; 223 (carried forward)
                                    ; 744 (carried forward)
                                    ;----
                                    ; 994
    ELSE
                                    ; 223
                                    ; 744
                                    ;----
                                    ; 967
    ENDI

        ;;------------------------------------------------------------------;;
        ;;  Decode next Rock/Crater/Cue/Exit/Caution whatever.              ;;
        ;;------------------------------------------------------------------;;
        MVI     RCCNT,  R2          ;  10 \
        DECR    R2                  ;   6  |- Count down between items
        MVO     R2,     RCCNT       ;  11 /
        BPL     @@done_nxtrc        ; 7/9 Leave if count's not expired
                                    ;
        MVI     RCIDX,  R5          ;  10 Get current world pointer
        MVI@    R5,     R3          ;   8 Get next word from world
        MVO     R5,     RCIDX       ;  11 Save new world pointer
        RLC     R3                  ;   6 extract bit 15
        SLR     R3                  ;   6
        MVO     R3,     RCCNT       ;  11 store the rock/crater count
        ANDI    #$FF00, R3          ;   8 clear count byte (does not clobber C)
        SWAP    R3                  ;   6 details in lower byte
        BC      @@cue_spawn         ; 7/9 if bit 15 == 1, this is a spawn
        BEQ     @@end_of_lvl        ; 7/9 if it's all 0000s, end of world     
;       BNC     @@do_rc             ;     if bit 15 == 0, it's rock/crater
                                    ; 967 (carried forward)
                                    ;----
                                    ;1076 (to cue_spawn)
                                    ;1083 (to end_of_level)
                                    ;1081 (fallthru)
@@do_rc:
        CMPI    #$60,   R3          ;   8 \_ $60 - $7F:  Exit flags
        BC      @@exitmarker        ; 7/9 /
                                    ;----
                                    ;1098 to exitmarker

        CMPI    #$20,   R3          ;   8 \_ $20 - $3B:  Level marker
        BC      @@lvlmarker         ; 7/9 /
                                    ;----
                                    ;1115 to levelmarker

        CMPI    #$1C,   R3          ;   8 \_ $1C - $1F:  Caution lamp
        BC      @@caution           ; 7/9 /
                                    ;----
                                    ;1128 to caution       
                                    ;1126 (fallthru)

        MVI     RCPIC,  R1          ;  10
        ADDI    #RCS1-1,R1          ;   8
        MVI@    R1,     R1          ;   8
        DECR    R1                  ;   6
        BEQ     @@notcratz          ; 7/9
        MVII    #RCS1.cratz - RCS1 + 1, R3  ; 8
@@notcratz
        MVO     R3,     RCPIC       ;  10
        B       @@done_nxtrc        ;   9
                                    ;----
                                    ;1184 (fallthru)
                                     


@@cue_spawn:
        INCR    R3                  ;   6
@@c:    MVO     R3,     CUENUM      ;  10
        B       @@done_nxtrc        ;   9
                                    ;----
                                    ;  25
                                    ;1076
                                    ;----
                                    ;1101

@@end_of_lvl:
        DECR    R5                  ;   6 \
        MVO     R5,     RCIDX       ;  10  |  Just stay stuck at end.
        DECR    R3                  ;   6  |- Hitting the 'Z' marker will
        MVO     R3,     RCCNT       ;  10  |  take us to next world.
        B       @@done_nxtrc        ;   9 /
                                    ;----
                                    ;  41
                                    ;1083
                                    ;----
                                    ;1124

@@lvlmarker
        INCR    R3                  ;   6 \_ Store out the level marker
        MVO     R3,     LMCHAR      ;  10 /  character
        MVII    #168,   R3          ;   8 \_ Put it off right-hand side
        MVO     R3,     LMCNT       ;  10 /
        MVO     R5,     RCNXT       ;  10 \
        MOVR    R5,     R0          ;   6  |_ Remember decoding position
        SWAP    R0                  ;   6  |  so we can restore it on death
        MVO     R0,     RCNXT+1     ;  10 /
        B       @@done_nxtrc        ;   9
                                    ;----
                                    ;  75
                                    ;1115
                                    ;----
                                    ;1190

@@caution:
        ANDI    #$3,    R3          ;   8   2 LSBs are caution color
        ADDI    #8*4,   R3          ;   8   6 MSBs are blink count
        MVO     R3,     CAUTFL      ;  10   Start it a-blinkin'
        B       @@done_nxtrc        ;   9
                                    ;----
                                    ;  35
                                    ;1128
                                    ;----
                                    ;1163

@@exitmarker
        ADDI    #$21,   R3          ;   8   \_ Exits are a special cue
        MVO     R3,     CUENUM      ;  10   /
                                    ;----
                                    ;  18
                                    ;1098
                                    ;----
                                    ;1116
@@done_nxtrc:
                                    ;1190 <-- worst case to here

        MVII    #RCS2-1,R3          ;   8 \
        ADD     RCPIC,  R3          ;  10  |__ Copy over the top card from 
        MVI@    R3,     R2          ;   8  |   the current rock/crater
        MVO     R2,     GROW+39     ;  11 /

        SUBI    #RCS2-RCS1, R3      ;   8 \
        MVI@    R3,     R2          ;   8  |-- Copy over the bottom card 
        MVO     R2,     GROW+19     ;  11 /    

        SLLC    R2                  ;   6 \
        ADCR    R3                  ;   6  |__ Increment our picture ptr if
        SUBI    #RCS1-1,R3          ;   8  |   MSB was set.
        MVO     R3,     RCPIC       ;  11 /
                                    ;----
                                    ;  87
                                    ;1190
                                    ;----
                                    ;1277
@@no_bot:
@@done_upcrd:

        ENDP

