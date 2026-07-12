;; ======================================================================== ;;
;;  Bad guy thinker routines for the Follower                               ;;
;;                                                                          ;;
;;  The follower is a special challenge because it's actually TWO BGs.      ;;
;;  This code assumes the follower was spawned as two consecutive BGs,      ;;
;;  which, to quote Kernighan, is an "unwarranted chumminess with the       ;;
;;  implementation."  The follower is the only thing that does this.        ;;
;;                                                                          ;;
;;  The follower also needs two exit tags.  The first exit tag tells it to  ;;
;;  charge in front of the buggy.  The second tag tells it to leave.        ;;
;;                                                                          ;;
;;  TODO:  Do we want a follower that fires at the tank?                    ;;
;;                                                                          ;;
;;  The thinkers are called with R1 == slot #, R3 == state pointer.         ;;
;;  R0, R2, R4 are available as scratch.                                    ;;
;;                                                                          ;;
;;  Thinkers return with delay in R0.                                       ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  BGT_FOLLOW0  -- Follower initialization                                 ;;
;;                  On first think, identify slot number of second half     ;;
;;                  so we can link together.  Then set thinker to main      ;;
;;                  hover algo.                                             ;;
;; ======================================================================== ;;
BGT_FOLLOW0     PROC
;               MVII    #99,        R0
;               B       BGT_RET

                MVII    #SPAT1,     R4      ;\_ Search sprite attrs for
                                            ;/  the other half of follower
@@l             MVI@    R4,         R2
                CMPI    #SPATBL.fol0b, R2
                BLT     @@nope
                CMPI    #SPATBL.fol3b, R2
                BLE     @@found_it
@@nope:         CMPI    #SPAT1+5,   R4
                BNC     @@l

;               MVII    #1,     R0          ;\_ Failed?  Just try again
                B       @@ret               ;/  next tic

@@found_it      SUBI    #SPAT1+1,   R4      ;\_ Store f1 slot# in 1st
                MVO@    R4,         R3      ;/  stat byte

                CMPI    #SPATBL.fol2b,  R2  ; Is it the reverse follower?
                MVII    #$14,       R2      ; Default target column
                BNEQ    @@set_it
                MVII    #$83,       R2      ; Reverse follower target column

@@set_it:       INCR    R3                  ;\_  Set target column in
                MVO@    R2,         R3      ;/   2nd status byte

                MVII    #BGI.follow1,R2     ;\
                SUBI    #3,         R3      ; |- Set thinker to primary
                MVO@    R2,         R3      ;/   thinker.
                ADDI    #2,         R3

@@ret           MVII    #1,         R0
                B       BGT_RET
                ENDP

;; ======================================================================== ;;
;;  BGT_FOLLOW1  -- Hover near the target column.  The target column        ;;
;;                  starts out to the left of the tank.  The exit method    ;;
;;                  sets the target column ahead of the tank causing the    ;;
;;                  follower to charge the tank.  Cute, eh?                 ;;
;; ======================================================================== ;;
BGT_FOLLOW1     PROC
;               MVII    #99,        R0
;               B       BGT_RET

                ; Get current Follower position and use to calculate
                ; new target velocity.
                MOVR    R1,         R2      ;\
                SLL     R2,         1       ; |- Point at follower's X coord
                ADDI    #SPXY1,     R2      ;/

                MVI@    R2,         R0      ;\_ record it so BGMAKE can spawn
                MVO     R0,         FXLO    ;/  mines under minelayer

                INCR    R3
                MVI@    R3,         R0      ; Get target column
                DECR    R3

                CALL    FLR_HONE            ; Hone in on target column
                DECLE   3
;               DECLE   $0000,  $FFFF

                ADDI    #SPAT1,     R1
                MVI@    R1,         R0
                CMPI    #SPATBL.fol2a, R0
                MVII    #$46,       R0      ; Reverse follower target Y coord
                BEQ     @@rev_follower

                MVII    #$49,       R0      ; Normal target Y coord
@@rev_follower  SUBI    #SPAT1,     R1
                INCR    R2                  ; Point at follower's Y coord

                ;; Look for rocks to our right
                MVO     R3,         BGTTMP
                MVI     FXLO,       R3
                SLR     R3,         2
                SLR     R3,         1
                MOVR    R3,         R4
                ADDI    #GROW - 1,  R4

                MVII    #3,         R5
@@rloop:
                MVI@    R4,         R3
                INCR    R4
                ANDI    #$1F8,      R3
                CMPI    #RCARD*8,   R3
                BNC     @@nextr
                CMPI    #(RCARD+6)*8, R3
                BNC     @@float
@@nextr:        DECR    R5
                BNEQ    @@rloop

                MVI     FHCNT,      R3
                DECR    R3
                BMI     @@hone3
                MVO     R3,         FHCNT
                B       @@hone

@@float:        MVII    #20,        R3
                MVO     R3,         FHCNT
                SUBI    #10,        R0

@@hone:         MVI     BGTTMP,     R3
                CALL    FLR_HONE
                DECLE   0
                B       @@sync

@@hone3:        MVI     BGTTMP,     R3
                CALL    FLR_HONE
                DECLE   3
;               DECLE   $4800,  $4A00

@@sync:         CALL    FLR_SYNC            ; Ensure flr halves stay sync'd

                MVII    #2,         R2      ; \
                CALL    BGBRAND             ;  |_ Wait 1 - 2 tics
                INCR    R0                  ;  |
                B       BGT_RET             ; /
                ENDP

;; ======================================================================== ;;
;;  FLR_HONE    Hone in on a target coord.                                  ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      R0 -- Target ordinate value                                         ;;
;;      R1 -- Slot # (not used but must be preserved)                       ;;
;;      R2 -- Ptr to current ordinate                                       ;;
;;      R3 -- Ptr to state byte (not used but must be preserved)            ;;
;;      R4 -- scratch                                                       ;;
;;      R5 -- Return address                                                ;;
;;                                                                          ;;
;;  OUTPUT                                                                  ;;
;;      Preserves R1, R2, R3                                                ;;
;;                                                                          ;;
;; ======================================================================== ;;
FLR_HONE        PROC

                TSTR    R0
                BNEQ    @@notz
                SUBI    #8,         R0      ; Treat 0 as -8.
@@notz
                PSHR    R0                  ; Save target ordinate
                MVI@    R2,         R0      ; Get current ordinate (8.8)
                ANDI    #$FF,       R0      ; make it integer
                SUB@    SP,         R0      ; \_ Find delta to target
                NEGR    R0                  ; /
                SLL     R0,         2       ; \_ *8
                SLL     R0,         1       ; /

                ADD@    R5,         PC
                SLL     R0,         2       ; *32 if arg is 1
                SUBI    #4,         R0

                PSHR    R5

                MOVR    R0,         R4      ; Save it

                CALL    BGRAND              ;

                PSHR    R2                  ; \
                SLR     R2                  ;  |_ pick bits 5:2 or 3:0
                BC      @@o                 ;  |  of RAND based on odd/even
                SLR     R0,         2       ;  |  (x/y) coordinate address
@@o:            PULR    R2                  ; /

                ANDI    #$0F,       R0      ; \
                SUBI    #$08,       R0      ;  |- Round randomly in 2 LSBs
                ADDR    R0,         R4      ; /

                SUBI    #SPXYP-SPXYV,R2     ; \
                MVI@    R2,         R0      ;  |
                SWAP    R0                  ;  |
                SLL     R0                  ;  |
                ADDR    R4,         R0      ;  |  Average new velocity
                SARC    R0,         2       ;  |_ with current velocity
                ADCR    R0                  ;  |  to accelerate toward
                SWAP    R0                  ;  |  goal.
                MVO@    R0,         R2      ;  |
                ADDI    #SPXYP-SPXYV,R2     ; /

                PULR    R5
    IF 0
                CMP@    R5,         R2      ; Check lower bound
                BC      @@lok
                DECR    R5
                MVI@    R5,         R0
                MVO@    R0,         R2
                INCR    R5
                JR      R5
@@lok:
                CMP@    R5,         R2      ; Check upper bound
                BNC     @@hok
                DECR    R5
                MVI@    R5,         R0
                MVO@    R0,         R2
    ENDI

@@hok:          JR      R5
                ENDP

;; ======================================================================== ;;
;;  FLR_SYNC    Synchronize the two halves of the follower.                 ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      R0 -- scratch                                                       ;;
;;      R1 -- Slot # of parent                                              ;;
;;      R2 -- scratch                                                       ;;
;;      R3 -- Ptr to state byte (pts to slot# of other half!)               ;;
;;      R4 -- scratch                                                       ;;
;;      R5 -- Return address                                                ;;
;; ======================================================================== ;;
FLR_SYNC        PROC

                MVI@    R3,         R0      ; Get slot # of other half

                ; Ick:  Follower may have died but we'll tick it once more?
   IF 0
                MVII    #SPAT,      R2
                ADDR    R0,         R2
                MVI@    R2,         R2
                CMPI    #SPATBL.fol0b, R2
                BLT     @@skip
                CMPI    #SPATBL.fol3b, R2
                BGT     @@skip
   ENDI

                SUBR    R1,         R0
;               ADDR    R0,         R0      ;
                SLL     R0,         1       ; non-interruptible on purpose

                MOVR    R1,         R4      ; \
                ADDR    R1,         R4      ;  |- Point to parent's XY vel
                ADDI    #SPXYV,     R4      ; /

                MVI@    R4,         R2      ; \
                DECR    R4                  ;  |_ Copy X vel
                ADDR    R0,         R4      ;  |
                MVO@    R2,         R4      ; /
                SUBR    R0,         R4
                MVI@    R4,         R2      ; \
                DECR    R4                  ;  |_ Copy Y vel
                ADDR    R0,         R4      ;  |
                MVO@    R2,         R4      ; /
                SUBR    R0,         R4


                ADDI    #SPXY1-SPXYV-2, R4  ; Move to position table
                MVI@    R4,         R2      ; \
                PSHR    R2                  ;  |- Get X, Y positions
                MVI@    R4,         R2      ; /
                SUBI    #2,         R4
                ADDR    R0,         R4
                PULR    R0
                MVO@    R0,         R4      ; \_ Write out X, Y positions
                MVO@    R2,         R4      ; /

@@skip:         JR      R5
                ENDP


;; ======================================================================== ;;
;;  BGT_FLEXIT   -- Charge the tank, wait                                   ;;
;; ======================================================================== ;;
BGT_FLEXIT      PROC
@@laymine       EQU     (CUE.laidmine  SHR 8) + 1

                INCR    R3                  ; 2nd state byte is target vel.
                MVII    #$1C,       R0      ; \
                CMP@    R3,         R0      ;  |- Advance to 1st stopping pt?
                BGT     @@set               ; /

                MVII    #120,       R0      ; \
                CMP@    R3,         R0      ;  |- Advance to 2nd stopping pt?
                BGT     @@set               ; /

                ; Ok, at 2nd stopping point.  See if we need to lay a mine.
                DECR    R3                  ; \
                MVI@    R3,         R2      ;  |  Index to other half of
                INCR    R3                  ;  |- follower, since its state
                SLL     R2,         2       ;  |  byte holds the mine count
                ADDI    #BGMPTBL+2, R2      ; /

                MVI@    R2,         R5      ; \_  Any mines left?
                DECR    R5                  ; /
                BMI     @@nomine            ; No: Proceed to 3rd stop (exit)
                MVO@    R5,         R2      ; Store updated mine count

                MVII    #125,       R0      ; Inch forward slightly
                MVII    #@@laymine, R2      ; \_ Lay mine using CUE mechanism.
                MVO     R2,         CUENUM  ; /  X coord comes from FXLO.
                B       @@set

@@nomine:       MVII    #225,       R0

@@set:          MVO@    R0,         R3
                DECR    R3

                CALL    FLR_SYNC

                MVII    #BGI.follow1,   R0
                B       BG_SETTHINK
                ENDP

;; ======================================================================== ;;
;;  BGT_FLADV   -- Reverse follower:  Fire available bullets, then charge.  ;;
;; ======================================================================== ;;
BGT_FLADV       PROC
                MVI@    R3,         R2      ; Get 2nd half slot #
                SLL     R2,         2       ; \
                ADDI    #BGMPTBL+2, R2      ;  |- Look up remaining bullets
                MVI@    R2,         R0      ; /
                DECR    R0
                BMI     @@advance
                MVO@    R0,         R2      ; Store updated bullet count

                MVII    #@@leave,   R5
                B       BGFIRE.d

@@advance:      INCR    R3

;               MVII    #$20,       R0
;               CMP@    R3,         R0
;               BLT     @@set

                CLRR    R0
@@set:          MVO@    R0,         R3

                DECR    R3

@@leave:        MVII    #BGI.follow1,   R0
                B       BG_SETTHINK

                ENDP
