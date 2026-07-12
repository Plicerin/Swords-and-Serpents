;; ======================================================================== ;;
;;  Bad guy thinker routines                                                ;;
;;                                                                          ;;
;;  These are called when their timers expire.  Timers are counted down     ;;
;;  at a 30Hz rate.                                                         ;;
;;                                                                          ;;
;;  Thinkers have 2 bytes of state at their disposal, and can call BGRAND,  ;;
;;  which returns a predictable hash of level-offset, elapsed time, R1, R3. ;;
;;  The first byte of state is initialized when the bad-guy is spawned.     ;;
;;  The intended use of this bytes is to specify "aggressiveness" and       ;;
;;  "evasiveness."  Aggressiveness is how often the bad-guy fires.          ;;
;;  Evasiveness is how much the bad guy tries to stay away from the tank.   ;;
;;                                                                          ;;
;;  Thinkers:                                                               ;;
;;                                                                          ;;
;;      BGT_SAUCxx  -- saucer flight programs.                              ;;
;;      BGT_BOULDER -- rolling boulder program (set hscroll, roll)          ;;
;;      BGT_TURRET  -- turret firing program (set hscroll, fire)            ;;
;;      BGT_MINE    -- Land mine:  (set hscroll, blink randomly)            ;;
;;      BGT_PLANT   -- space-plant program:  duck up/down randomly          ;;
;;                                                                          ;;
;;  Support (implemented):                                                  ;;
;;                                                                          ;;
;;      BGRAND      -- predictable RAND                                     ;;
;;      BGBRAND     -- predictable RAND, bounded by R2                      ;;
;;      BGFIRE      -- make a bad guy fire                                  ;;
;;      BGKILL      -- remove bad guy from list of bad guys                 ;;
;;                                                                          ;;
;;  Support (todo -- maybe won't bother):                                   ;;
;;                                                                          ;;
;;      BGSETHS     -- Set horiz-scroll bit for this bad-guy                ;;
;;      BGSETVEL    -- Set velocity for this bad-guy                        ;;
;;      BGSETATTR   -- Set attribute number for this bad-guy                ;;
;;                                                                          ;;
;;  The thinkers are called with R1 == slot #, R3 == state pointer.         ;;
;;  R0, R2, R4 are available as scratch.                                    ;;
;;                                                                          ;;
;;  Thinkers return with delay in R0.                                       ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  BGRAND  -- A purposefully not-very-random random.  The LSBs are the     ;;
;;             only useful bits.                                            ;;
;; ======================================================================== ;;
BGRAND      PROC

            MVI     RCIDX,  R0      ; mix in rock/crater/spawn index
            ADDR    R3,     R0      ; add BGMPTBL pointer
            XORR    R1,     R0      ; mix in slot number
            ADD     TIMSEC, R0      ; add time in seconds.

            JR      R5
            ENDP

;; ======================================================================== ;;
;;  BGBRAND -- Like BGRAND, only bounded to the range specified in R2.      ;;
;; ======================================================================== ;;
BGBRAND     PROC

            CLRR    R0
            CMPR    R2,     R0
            BEQ     @@leave

@@l1        SETC
            RLC     R0,     1
            CMPR    R2,     R0
            BNC     @@l1

            ; add a couple extra bits to mask.
            ; this hopefully reduces the bias we give to certain numbers
            ; with our crappy modulo technique.
            SLLC    R0,     2
            ADDI    #3,     R0

            PSHR    R0

            MVI     RCIDX,  R0      ; mix in rock/crater/spawn index
            ADDR    R3,     R0      ; add BGMPTBL pointer
            XORR    R1,     R0      ; mix in slot number
            ADD     TIMSEC, R0      ; add time in seconds.

            PSHR    R0              ;\
            SWAP    R0              ; |-- fold upper, lower halves
            XOR@    R6,     R0      ;/

            AND@    R6,     R0      ; mask approximately into range.

@@l2        SUBR    R2,     R0
            BPL     @@l2

            ADDR    R2,     R0
@@leave:
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  BGT_TURRET0:  Set horiz scroll, then set thinker to fire program.       ;;
;; ======================================================================== ;;
BGT_TURRET0 PROC

            ;; ------------------------------------------------------------ ;;
            ;;  Set up thinker for turret to just fire occasionally.        ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #BGI.turret1, R0
            B       BG_SETTHINK

            ENDP

;; ======================================================================== ;;
;;  BGT_BOULDER0:  Set horiz scroll + left vel, then set thinker to roller. ;;
;; ======================================================================== ;;
BGT_BOULDER0 PROC

            ;; ------------------------------------------------------------ ;;
            ;;  Set up boulder to have some leftward velocity in addition   ;;
            ;;  to what hscroll will give us.                               ;;
            ;; ------------------------------------------------------------ ;;
            MOVR    R1,     R2
            ADDR    R1,     R2
            ADDI    #SPXYV, R2

            MVII    #$A8FF, R0
            MVO@    R0,     R2

            ; Set up thinker for boulder to just animate.
            MVII    #BGI.boulder1, R0
            B       BG_SETTHINK

            ENDP

;; ======================================================================== ;;
;;  BGT_PLANT0: Set horizontal-scroll, and then set ducker as thinker.      ;;
;; ======================================================================== ;;
BGT_PLANT0  PROC

            MVII    #BGI.plant1, R0
            B       BG_SETTHINK

            ENDP

;; ======================================================================== ;;
;;  BGT_MINE0:  Set horizontal-scroll, and then set blinker as thinker.     ;;
;; ======================================================================== ;;
BGT_MINE0   PROC

            ;; ------------------------------------------------------------ ;;
            ;;  The mines just blink after they've been set h-scroll.       ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #BGI.mine1, R0          ;   Get address of main thinker
;           B       BG_SETTHINK
            ; XXX: fall through to BG_SETTHINK

            ENDP


;; ======================================================================== ;;
;;  BG_SETTHINK                                                             ;;
;;  This changes the thinker for the bad-guy in R1.                         ;;
;;  R3 is expected to point to offset 3 in the BGMPTBL record (the first    ;;
;;  "status" byte).                                                         ;;
;; ======================================================================== ;;
BG_SETTHINK PROC
            ;; ------------------------------------------------------------ ;;
            ;;  Set the thinker-pointer for this bad-guy.                   ;;
            ;; ------------------------------------------------------------ ;;
            SUBI    #2,     R3              ;   Rewind to program pointer
@@1:        MVO@    R0,     R3              ;   Set thinker to R0
            ADDI    #2,     R3              ;   Restore R3

            ;; ------------------------------------------------------------ ;;
            ;;  Return a delay of 1 + (slot >> 1) for this MOB to stagger   ;;
            ;;  the thinking out over multiple frames.  This should help    ;;
            ;;  stagger boulders/mines that cue as a group.                 ;;
            ;; ------------------------------------------------------------ ;;
            MOVR    R1,     R0
            SLR     R0,     1
            INCR    R0

            B       BGT_RET
            ENDP


;; ======================================================================== ;;
;;  BGT_MINE1:  Just blink pseudo-randomly.                                 ;;
;; ======================================================================== ;;
BGT_MINE1   PROC

            CALL    BGRAND                  ;   random number to R0
            ADD@    R3,     R0              ;   Get status byte 1
            MVO@    R0,     R3


            SARC    R0

            ; Set Red/White based on lsb of status byte.
            PSHR    R0                      ;

            MVII    #SPATBL.lmna,   R0
            BC      @@not1
            MVII    #SPATBL.lmnb,   R0
@@not1:
            MVII    #SPAT,  R2              ;
            ADDR    R1,     R2              ;

            MVO@    R0,     R2

            PULR    R0

            ; delay randomly from 4 to 11
            ANDI    #7,     R0
            ADDI    #4,     R0

            B       BGT_RET
            ENDP


;; ======================================================================== ;;
;;  BGT_PLANT1:  Just duck pseudo-randomly.                                 ;;
;; ======================================================================== ;;
BGT_PLANT1  PROC

            MVII    #SPAT,  R2              ;
            ADDR    R1,     R2              ;
            MVI@    R2,     R0
            CMPI    #SPATBL.plta,   R0
            BEQ     @@pltb
            CMPI    #SPATBL.pltb,   R0
            BEQ     @@plta
            CMPI    #SPATBL.pltc,   R0
            BEQ     @@pltd
@@pltc      MVII    #SPATBL.pltc,   R0
            B       @@done
@@pltd      MVII    #SPATBL.pltd,   R0
            B       @@done
@@plta      MVII    #SPATBL.plta,   R0
            B       @@done
@@pltb      MVII    #SPATBL.pltb,   R0
@@done:

            MVO@    R0,     R2

            CALL    BGRAND                  ;   random number to R0
            ADD@    R3,     R0              ;   Get status byte 1
            MVO@    R0,     R3
            ; delay randomly from 5 to 12
            ANDI    #7,     R0
            ADDI    #5,     R0

            B       BGT_RET
            ENDP

;; ======================================================================== ;;
;;  BGT_TURRET1 -- turret firing program                                    ;;
;; ======================================================================== ;;
BGT_TURRET1 PROC

            MVI@    R3,     R0
            TSTR    R0
            BEQ     @@not_1st
@@1st       MVII    #15,    R0          ;   First time 'round, wait 16 tics
            MVO@    R0,     R3          ;   Initialize flag saying "not 1st"
            B       BGT_RET

@@not_1st:                              ;   2nd and subsequent times,
            MVI     HBCOL1, R0
            SLL     R0,     1
            BEQ     @@ok_fire
            ADDI    #8,     R0

            MOVR    R1,     R2
            SLL     R2,     1
            ADDI    #SPXYP, R2

            MVI@    R2,     R4
            ANDI    #$FF,   R4
            CMPR    R0,     R4
            BLT     @@no_fire           ; don't fire -- bullet too close


@@ok_fire   CALL    BGFIRE.c            ;   fire every 45 tics.
@@no_fire   MVII    #44,    R0
            B       BGT_RET
            ENDP

;; ======================================================================== ;;
;;  BGT_STAL0    -- Stalactite:  Shudder when nearing fall point.           ;;
;; ======================================================================== ;;
BGT_STAL0   PROC

            MOVR    R1,     R2
            SLL     R2,     1
            ADDI    #SPXYP, R2

            MVI@    R2,     R4
            SUBI    #16,    R4
            ANDI    #$FF,   R4

            CLRR    R0
            CMP@    R3,     R4

            BGT     BGT_RET

            MVII    #SPATBL.stala, R0
            MVII    #BGI.stal1, R4

@@1:        MVII    #SPAT,  R2
            ADDR    R1,     R2
            MVO@    R0,     R2


            MOVR    R3,     R2
            SUBI    #2,     R2
            MVO@    R4,     R2

            CLRR    R0
            B       BGT_RET

            ENDP

;; ======================================================================== ;;
;;  BGT_STAL1    -- Stalactite:  Fall once X gets below state byte 1.       ;;
;;                  Then go to STAL2, which is for accel and landing.       ;;
;; ======================================================================== ;;
BGT_STAL1   PROC

            MOVR    R1,     R2
            SLL     R2,     1
            ADDI    #SPXYP, R2

            MVI@    R2,     R4
            ANDI    #$FF,   R4

            CLRR    R0
            CMP@    R3,     R4

            BGT     BGT_RET


            MVII    #SPATBL.stal, R0
            MVII    #BGI.stal2, R4
            B       BGT_STAL0.1

            ENDP


;; ======================================================================== ;;
;;  BGT_STAL2    -- Fall, and then stick in the ground once we get there.   ;;
;; ======================================================================== ;;
BGT_STAL2   PROC

            MOVR    R1,         R2          ;
            SLL     R2,         1           ;

            ADDI    #SPXYP+1,   R2          ; \
            MVI@    R2,         R0          ;  |_ Are we on the ground yet?
            SWAP    R0                      ;  |
            CMPI    #$4500,     R0          ; /
            BGE     @@hit

            ADDI    #SPXYV-SPXYP,R2         ;
            MVI@    R2,         R4          ; \
            ADDI    #$4000,     R4          ;  |_ accelerate by $00.40
            ADCR    R4                      ;  |
            MVO@    R4,         R2          ; /

            CLRR    R0
            B       BGT_RET

@@hit
            MVII    #$4A,       R0          ; \_ stick in the ground
            MVO@    R0,         R2          ; /
            ADDI    #SPXYV-SPXYP,R2         ;
            CLRR    R0                      ; \_ zero out our velocity
            MVO@    R0,         R2          ; /
            MVII    #SPAT,      R2          ;
            ADDR    R1,         R2          ;

            MVII    #SPATBL.stalf, R0       ; \_ Set prio so we're behind
            MVO@    R0,         R2          ; /  the ground

;           PSHR    R1
            CALL    PLAYSFX
            DECLE   FXSMEXP
;           PULR    R1

            MVII    #BGI.null, R0
            B       BG_SETTHINK
            ENDP

;; ======================================================================== ;;
;;  See 'bgsaucer.asm' for the Pink/Blue/White saucer motion programs.      ;;
;; ======================================================================== ;;
