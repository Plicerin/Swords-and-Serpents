;; ======================================================================== ;;
;;  Bad guy thinker routines for saucer                                     ;;
;;  I broke these out into a separate file since they're so involved.       ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  SCTBL -- Saucer control table.                                          ;;
;;                                                                          ;;
;;  Saucer Control Table Format                                             ;;
;;                                                                          ;;
;;      Top level is a series of 4-word records.  Each record contains      ;;
;;                                                                          ;;
;;       -- Magnitude of random component for bullet fire delay.            ;;
;;       -- Minimum delay between bullet fire                               ;;
;;       -- Pointer to Delta-X table                                        ;;
;;       -- Pointer to Delta-Y table                                        ;;
;;                                                                          ;;
;;      Delta-X table consists of a 3-word header followed by a series of   ;;
;;      2-word entries.                                                     ;; 
;;                                                                          ;;
;;      DXT header:                                                         ;;
;;       -- Minimum X coordinate, in 8Q8                                    ;;
;;       -- Maximum X coordinate, in 8Q8                                    ;;
;;       -- Number of entries in table                                      ;;
;;                                                                          ;;
;;      DXT entry:                                                          ;;
;;       -- Rightward velocity in lower byte of first word (biased 2Q6)     ;;
;;       -- Number of ticks in upper byte of first word.                    ;;
;;       -- Total delta-X for this motion, in 8Q8                           ;;
;;                                                                          ;;
;;      Delta-Y table format is identical to Delta-X table.                 ;;
;;                                                                          ;;
;;  The saucer control tables are compiled by SCTC.                         ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  Saucer Control State Machine                                            ;;
;;                                                                          ;;
;;  Saucers have at their heart a three-state control machine.  The three   ;;
;;  states are "Move left/right", "Fire", and "Move up/down".  The          ;;
;;  following diagram indicates the allowed state transitions:              ;;
;;                                                                          ;;
;;                                                                          ;;
;;                            +--------------+                              ;;
;;                            |              |                              ;;
;;                            |   +------+   |                              ;;
;;        +----------+        +-->|      |---+           +----------+       ;;
;;        |          |            | FIRE |               |          |       ;;
;;    +-->|          |----------->|      |-------------->|          |---+   ;;
;;    |   | MOVE L/R |            +------+               | MOVE U/D |   |   ;;
;;    |   |          |                                   |          |   |   ;;
;;    |   |          |---------------------------------->|          |   |   ;;
;;    |   +----------+                                   +----------+   |   ;;
;;    |                                                                 |   ;;
;;    |                                                                 |   ;;
;;    +-----------------------------------------------------------------+   ;;
;;                                                                          ;;
;;  Saucers start out in the MOVE L/R state.  They exit from this state     ;;
;;  into either FIRE or MOVE U/D based on whether the random delay the      ;;
;;  MOB picked is longer than the delay specified for the selected L/R      ;;
;;  move.                                                                   ;;
;;                                                                          ;;
;;  If the saucer enters the FIRE state, it records the total delay         ;;
;;  req'd for the L/R sweep in the second state byte.  The firing code      ;;
;;  then fires after random delays, until the total delay is consumed.      ;;
;;                                                                          ;;
;;  The MOVE L/R and MOVE U/D code picks motions from the Delta-X and       ;;
;;  Delta-Y tables.  These tables contain various motion parameters, in     ;;
;;  the form of a velocity, tick count, and total delta.  The total         ;;
;;  delta is used to calculate the saucer's endpoint for a given motion,    ;;
;;  and thus ultimately ensure that the saucer stays within its bounding    ;;
;;  box.  The velocity and tick count are used directly to control the      ;;
;;  saucer motion.                                                          ;;
;; ======================================================================== ;;

;; ======================================================================== ;;
;;  SAUC_PICK_D  -- Given a current position and DXT/DYT pointer, pick a    ;;
;;                  a slot in the DXT/DYT at random.                        ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      R1  Slot #                                                          ;;
;;      R2  DXT/DYT pointer.                                                ;;
;;      R3  Pointer to BGMPTBL slot                                         ;;
;;      R4  Current X/Y coordinate, in 8Q8 format                           ;;
;;      R5  Return address.                                                 ;;
;;                                                                          ;;
;;  OUTPUTS                                                                 ;;
;;      R0  Velocity                                                        ;;
;;      R1  unmodified                                                      ;;
;;      R2  Tick count                                                      ;;
;;      R3  unmodified                                                      ;;
;;      R4  unmodified                                                      ;;
;;      R5  trashed.                                                        ;;
;;                                                                          ;;
;; ======================================================================== ;;
SAUC_PICK_D PROC
            PSHR    R5              ; Save return addr.
            PSHR    R3
            MOVR    R2,     R3      ; Save DXT/DYT pointer

            ADDI    #2,     R2
            MVI@    R2,     R2      ; Get # of entries

            CALL    BGBRAND         ; pick a random starting point
            SLL     R0,     1       ;

            MOVR    R3,     R2
@@try_next:
            MOVR    R2,     R3      ; \
            ADDI    #4,     R3      ;  |-- Index to selected entry's 'delta'
            ADDR    R0,     R3      ; /    field.

            MOVR    R4,     R5      ; Copy X/Y coord to temp
            ADD@    R3,     R5      ; Try going right/down

            INCR    R2              ;  |-- Is it too big?
            BC      @@not_ok_pos    ; (overflowed!)
            CMP@    R2,     R5      ; /
            BNC     @@ok_pos        ; No:  This entry is ok in the +ve dir.
@@not_ok_pos

            MOVR    R4,     R5
            SUB@    R3,     R5

            DECR    R2              ; \___ Is it too small?
            BNC     @@not_ok_neg    ; (underflowed!)
            CMP@    R2,     R5      ; /
            BC      @@ok_neg        ; No:  This entry is ok in the -ve dir.
@@not_ok_neg:

            SUBI    #2,     R0      ; Neither direction ok, so go to prev entry
            BPL     @@try_next

            ADDI    #2,     R2      ; \
            MVI@    R2,     R0      ;  |   Wrap around if go prior to 1st
            SUBI    #2,     R2      ;  |-- entry in DXT/DYT
            DECR    R0              ;  |
            SLL     R0              ; /

            B       @@try_next

@@ok_pos:
            DECR    R3              ; point to vel/tick field
            MVI@    R3,     R0      ; Read vel/tick
            B       @@unpack_vel_tick

@@ok_neg:   
            DECR    R3              ; point to vel/tick field
            MVI@    R3,     R0      ; Read vel/tick
            XORI    #$FF,   R0      ; \__ negate velocity field
;           INCR    R0              ; /   (no incr for 1s compl)

@@unpack_vel_tick:
            MOVR    R0,     R2      ; copy packed field over
            ANDI    #$FF,   R0      ; keep only velocity in R0
            XORR    R0,     R2      ; clear velocity from R2
            SWAP    R2              ; put tick in lower half of R2

            XORI    #$80,   R0      ; \
            SUBI    #$80,   R0      ;  |- Sign extend and scale velocity
            SLL     R0,     2       ; /   from 2Q6 to 8Q8
            SWAP    R0              ; swapped 1s compl.

            PULR    R3              ; restore R3
            PULR    PC              ; return

            ENDP
           
;; ======================================================================== ;;
;;  BGT_SAUC_LR -- Left/Right motion state for Saucer.                      ;;
;; ======================================================================== ;;
BGT_SAUC_LR PROC

            SLL     R1,     1       ; double slot number for x/y indexing

            MVI@    R3,     R2      ; Get SCP # from status byte 1.
            SLL     R2,     2       ; \
            ADDI    #SCTBL, R2      ;  |-- Index into SCTBL and remember it.
            MVO     R2,     BGTTMP  ; /

            ADDI    #2,     R2
            MVI@    R2,     R2      ; Get DXT pointer into R2.

            ADDI    #SPXY1, R1      ;\
            MVI@    R1,     R0      ; |-- Get current X coordinate into R4
            SWAP    R0
            MOVR    R0,     R4
            SUBI    #SPXY1, R1      ;/

            CALL    SAUC_PICK_D     ; pick a velocity and tick-count

            INCR    R3
            MVO@    R2,     R3      ; record tick count in status byte 2

            MOVR    R1,     R4      ; \   Set the velocity of this saucer
            ADDI    #SPXYV, R4      ;  |- to the selected horiz velocity.
            MVO@    R0,     R4      ; / 
            CLRR    R0              ; \__ no vertical velocity
            MVO@    R0,     R4      ; /
            
            SLR     R1,     1       ; restore slot number
            
            MVI     BGTTMP, R4      ; \
            MVI@    R4,     R2      ;  |-- calculate random portion of delay
            CALL    BGBRAND         ; /
            ADD@    R4,     R0      ; Add fixed portion of delay

            MOVR    R0,     R2      ; \
            SUB@    R3,     R2      ;  |-- Is this delay >= than motion
            BGE     @@next_is_ud    ; /    duration?

            ; If not (eg. result was negative), then next state is "FIRE"
            COMR    R2              ; \__ Store updated "remaining ticks",
            MVO@    R2,     R3      ; /   compensating for off-by-1 tick counts

            ; Decide whether we're running firing program 0 or 1 based on
            ; whether this is a spinner or a regular saucer.
            MVII    #SPAT1, R2          ; \
            ADDR    R1,     R2          ;  |- look up the saucer's attribute
            MVI@    R2,     R2          ; /

            ; Set firing program to #1 for spinners, #0 otherwise
            ; NOTE: Change this if we get more than 2 spinners to check a
            ; range.  This will force spinners to be consecutive in SPATBL.

            CMPI    #SPATBL.wht0, R2    ; Is it the spinner?
            BLT     @@set_next_state    ; 
            CMPI    #SPATBL.wht3, R2    ; Is it the spinner?
            MVII    #BGI.sauc_f0, R2    ; Assume not a spinner
            BGT     @@set_next_state
@@spinner:  MVII    #BGI.sauc_f1, R2    ; Oh, it was a spinner

@@set_next_state:
            SUBI    #3,     R3      ; Rewind to program pointer
            MVO@    R2,     R3      ; Set thinker to "FIRE" or "MOVE U/D"

            ADDI    #2,     R3      ; Restore R3

            B       BGT_RET

@@next_is_ud:
            ;; We picked a random delay that's longer than the delay for
            ;; this left/right motion, so clamp to the L/R motion length
            ;; and transition directly to the MOVE U/D state.
            MVI@    R3,     R0      ; Get movement's duration as our delay
            MVII    #BGI.sauc_ud,R2
            B       @@set_next_state

            ENDP
            
;; ======================================================================== ;;
;;  BGT_SAUC_UD -- Up/Down motion state for Saucer.                         ;;
;; ======================================================================== ;;
BGT_SAUC_UD PROC
            SLL     R1,     1

            MVI@    R3,     R2      ; Get SCP # from status byte 1.
            SLL     R2,     2       ; \
            ADDI    #SCTBL, R2      ;  |-- Index into SCTBL and remember it.
            MVO     R2,     BGTTMP  ; /

            ADDI    #3,     R2
            MVI@    R2,     R2      ; Get DYT pointer into R2.

            ADDI    #SPXY1+1,R1     ; \
            MVI@    R1,      R0     ;  |-- Get current Y coordinate into R4
            SWAP    R0
            MOVR    R0,      R4
            SUBI    #SPXY1+1,R1     ; /

            CALL    SAUC_PICK_D     ; pick a velocity and tick-count

            INCR    R3
            MVO@    R2,     R3      ; record tick count in status byte 2

            MOVR    R1,     R4      ; \
            CLRR    R2              ;  |
            ADDI    #SPXYV, R4      ;  |__ Set the velocity of this saucer
            MVO@    R2,     R4      ;  |   to the selected vert velocity.
            MVO@    R0,     R4      ; /  

            MVI@    R3,     R0      ; get tick count back into R0.
            
            MVII    #BGI.sauc_lr,R2

            SUBI    #3,     R3      ; Rewind to program pointer
            MVO@    R2,     R3      ; Set thinker to "MOVE L/R"

            ADDI    #2,     R3      ; Restore R3

            SLR     R1,     1
            B       BGT_RET

            ENDP

;; ======================================================================== ;;
;;  BGT_SAUC_F1 -- FIRE state for White Spinner Saucer                      ;;
;; ======================================================================== ;;
BGT_SAUC_F1 PROC

            MVII    #BGI.sauc_f1, R2
            MVO     R2,     BGTTMP  

            ;; ------------------------------------------------------------ ;;
            ;;  We only let spinners fire in the left half of the screen.   ;;
            ;; ------------------------------------------------------------ ;;
            MVI     SPINB,  R0
            TSTR    R0
            BNEQ    @@cd2

            MVII    #SPXY1, R4      ; \
            ADDR    R1,     R4      ;  |_ Get the X&Y coordinate of the bad guy
            ADDR    R1,     R4      ;  |  
            SDBD                    ;  | 
            MVI@    R4,     R2      ; /
            MOVR    R2,     R0
            SWAP    R2              ; Put X in MSB
            SUBI    #$1800, R2
            BNC     @@cd2           ; Underflow?  Too far left
            CMPR    R0,     R2      ; \__ ok to fire if X-24 > Y.
@@cd2       MVII    #1,     R0      ; (default delay if not firing)
            BNC     @@com_dly       ; /   (note unsigned comparisons.)

            ; XXX: Add rule here to prevent firing if ship too far right.

            MVI     CRATCNT,R2      ; \
            CMPI    #3,     R2      ;  |- Don't fire if crater still onscreen
            BGT     @@com_dly       ; /   (Allow it in the last several cards)

            MVO     R0,     SPINB
            CALL    BGFIRE.b
@@common:   
            MVI@    R3,     R4      ; Get SCP # from status byte 1.
            ADDR    R4,     R4      ; \
            ADDR    R4,     R4      ;  |-- Index into SCTBL  (SCTBL + 4*SCP#)
            ADDI    #SCTBL, R4      ; / 

            MVI@    R4,     R2      ; \___ calculate random portion of delay
            CALL    BGBRAND         ; /
            ADD@    R4,     R0      ; Add fixed portion of delay
            INCR    R0              ; Compensate for "off-by-1" on delay counts
@@com_dly:
            MOVR    R0,     R2      ; \
            INCR    R3              ;  |__ Is this delay >= than motion
            SUB@    R3,     R2      ;  |   duration?
            BGE     @@next_is_ud    ; / 

            ; If not (eg. result was negative), then next state is "FIRE"
            COMR    R2              ; \__ Store updated "remaining ticks",
            MVO@    R2,     R3      ; /   compensating for off-by-1 tick counts
            MVI     BGTTMP, R2      ; (we saved proper ptr earlier.)

@@set_next_state:
            SUBI    #3,     R3      ; Rewind to program pointer
            MVO@    R2,     R3      ; Set thinker to "FIRE" or "MOVE U/D"
            ADDI    #2,     R3      ; Restore R3

            B       BGT_RET

@@next_is_ud:
            ;; We picked a random delay that's longer than the delay for
            ;; this left/right motion, so clamp to the L/R motion length
            ;; and transition directly to the MOVE U/D state.
            MVI@    R3,     R0      ; Get movement's duration as our delay
            MVII    #BGI.sauc_ud,R2
            B       @@set_next_state

            ENDP

;; ======================================================================== ;;
;;  BGT_SAUC_F0 -- FIRE state for Pink/Blue Sacuers                         ;;
;; ======================================================================== ;;
BGT_SAUC_F0 PROC

            MVII    #BGI.sauc_f0, R2
            MVO     R2,     BGTTMP  

            MVII    #2,     R0      ; default delay if not firing
@@no_fire   SET     BGT_SAUC_F1.com_dly

            ;; ------------------------------------------------------------ ;;
            ;;  We only let saucers fire in certain ranges of the screen,   ;;
            ;;  in order to keep it 'fair'.  Those ranges are set up like   ;;
            ;;  so, with X representing "no fire" areas:                    ;;
            ;;                                                              ;;
            ;;          ---------------X-XX--XXXXXXXXXXXXXXXXXXX            ;;
            ;;                                                              ;;
            ;;  The island of X-XX's represents the area to the right of    ;;
            ;;  the moon buggy's vertical gun turret up through the tip of  ;;
            ;;  of its horizontal turret, when the buggy is at its maximum  ;;
            ;;  velocity.                                                   ;;
            ;;                                                              ;;
            ;;  We allow some bullets just in front of the buggy as a sort  ;;
            ;;  of "bluffing" bullet fire.  We disallow unproductive fire   ;;
            ;;  through the rest of the right hand of the screen since it   ;;
            ;;  just wastes bullet sprites from group 2.                    ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #SPXY1, R2      ; \
            ADDR    R1,     R2      ;  |_ Get the X coordinate of the bad guy
            ADDR    R1,     R2      ;  |  
            MVI@    R2,     R2      ; /
            SWAP    R2
            CMPI    #55*256,R2      ; \__ ok to fire in left part of screen
            BNC     @@ok_fire       ; /   (note unsigned comparisons.)

            CMPI    #60*256,R2      ; \
            BNC     @@no_fire       ;  |_ tiny island to allow firing directly
            CMPI    #62*256,R2      ;  |  above buggy's gun turret  :-)
            BNC     @@ok_fire       ; /

            ; If there's a crater directly beneath the saucer, 
            ; only fire 25% of the time
            MVI     TICK,   R0
            ANDI    #7,     R0
            BEQ     @@skipnice

            PSHR    R2
            SWAP    R2
            SLR     R2,     2
            SLR     R2,     1
            MOVR    R2,     R4
            PULR    R2
            ANDI    #$1F,   R4
            ADDI    #GROW+20, R4
            MVII    #GCARDx,R0
            CMP@    R4,     R0
            BNEQ    @@no_fire1
            INCR    R4
            CMP@    R4,     R0
            BNEQ    @@no_fire1
            
            ; Skip the next test with odds proportional to 
            ; (POINT + COURSE*4 + k) / 128
@@skipnice: CALL    BGRAND
            ANDI    #$7F,   R0
            SLL     R0,     2
            SLL     R0,     1
            MOVR    R0,     R4
            MVI     COURSE, R0
            SLL     R0,     2
            SLL     R0,     2
            SLL     R0,     1
            ADDI    #30,    R0
            ADD     POINT,  R0
            CMPR    R0,     R4
            MVII    #2,     R0
            BLT     @@ok_fire

@@nofireovertank
            CMPI    #81*256,R2      ; \
            BC      @@no_fire       ;  |_ make sure we don't fire inside the
            CMPI    #77*256,R2      ;  |  two no-fire islands.
            BNC     @@no_fire       ; /   

@@ok_fire:  MVII    #BGT_SAUC_F1.common, R5
            B       BGFIRE.a        ;

@@no_fire1: MVII    #5,     R0      ; If over crater, wait 1/6th second
            B       @@no_fire
            ENDP

;; ======================================================================== ;;
;;  BGT_SAUC_EX -- Exit motion state for Saucer.                            ;;
;;                                                                          ;;
;;  When exiting, go in the direction that'll take us over the tank.  This  ;;
;;  allows the tank to make one last pot shot at the saucer.  Note that     ;;
;;  the test need only be approximate--if the saucer is near the tank       ;;
;;  anyway, the player doesn't need the extra help so much.                 ;;
;; ======================================================================== ;;
BGT_SAUC_EX PROC

            MOVR    R1,     R2      ; \
            SLL     R2,     1       ;  |- index into SPXYP table
            ADDI    #SPXYP, R2      ; /

            MVI@    R2,     R0      ; \
            SUBI    #4,     R0      ;  |_ Are we to the left or right of
            ANDI    #$FF,   R0      ;  |  the tank?  (approximately)
            CMP     TXLO,   R0      ; / 

@@got_xvel: MVII    #$00FE, R0      ; default to moving left.
            ADCR    PC              ; Exit right if compared velocity >= 0
            COMR    R0              ; $0200 is high speed to right.

            ADDI    #SPXYV-SPXYP, R2

            MVO@    R0,     R2      ; Store as new X velocity
            INCR    R2
            CLRR    R0
            MVO@    R0,     R2      ; Store zero out Y velocity
            
            MVII    #$FF,   R0
            B       BGT_RET         ; Sleep a long time.

            ENDP


            
