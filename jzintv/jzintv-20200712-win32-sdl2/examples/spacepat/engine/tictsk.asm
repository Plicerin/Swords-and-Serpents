;; ======================================================================== ;;
;;  TICTSK                                                                  ;;
;;                                                                          ;;
;;  This is a sort of generic catch-all function called 30 times/sec        ;;
;;                                                                          ;;
;;   -- Update the game clock                                               ;;
;;   -- Update the score display                                            ;;
;;   -- Update the lives display                                            ;;
;;   -- Update the checkpoint display                                       ;;
;;   -- Check for crossing checkpoints                                      ;;
;;   -- Blink the caution lamp                                              ;;
;;                                                                          ;;
;;  TIC1ST is an alternate entry point used at the start of the game.       ;;
;;  It forces everything to refresh.                                        ;;
;; ======================================================================== ;;

TIC1ST  MVO     R5,         BGTTMP
        B       TICTSK.show_initial_time    ; Skip time increment

TICTSK  PROC
        MVO     R5,         BGTTMP


@@normal_update:
        ;; ---------------------------------------------------------------- ;;
        ;;  Update the game clock.  TIMTIC counts 31 - 1.  When it expires  ;;
        ;;  we update TIMSEC, being careful to not let it run over 255.     ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     TIMTIC,     R0
        DECR    R0
        BNEQ    @@tic_ok

        MVI     TIMSEC,     R0
        CMPI    #$FF,       R0
        ADCR    PC                      ;   don't increment if 255 already
        INCR    R0
@@show_initial_time:
        MVO     R0,         TIMSEC

        ;; ---------------------------------------------------------------- ;;
        ;;  Update the displayed time.                                      ;;
        ;; ---------------------------------------------------------------- ;;
        MVII    #3,         R2
        MVII    #gen_cstk_card(0, GRAM, Blue, NoAdvance), R3
        MVII    #disp_ptr(11, 16), R4
        CALL    PRNUM16.z

        ;; ---------------------------------------------------------------- ;;
        ;;  Reset the TIMTIC countdown.                                     ;;
        ;; ---------------------------------------------------------------- ;;
        MVII    #31,        R0
@@tic_ok:
        MVO     R0,         TIMTIC

        ;; ---------------------------------------------------------------- ;;
        ;;  Check to see if we've passed a level marker.  If we have:       ;;
        ;;   -- Record the new checkpoint letter                            ;;
        ;;   -- Alert the player with a DING                                ;;
        ;;   -- Remember where we are in the world so we can restart here   ;;
        ;;      (Copy RCNXT to RCLVL for restart code.)                     ;;
        ;; ---------------------------------------------------------------- ;;

        MVI     LMCNT,      R0          ; LMCNT holds column of level-marker
        TSTR    R0
        BLE     @@no_level_marker       ; Skip this code if none is active

        SUBI    #15,        R0          ; \
        CMP     TXLO,       R0          ;  |- Is nose of tank past it?
        BGE     @@no_level_marker       ; /   No:  Leave

        MVI     LMCHAR,     R0          ; \
        SLL     R0,         2           ;  |_ Merge ckpt char w/ current 
        SLL     R0,         1           ;  |  course # to see if this is new
        XOR     COURSE,     R0          ; /
        XORI    #$100,      R0          ; bit 8 set on normal ckpts.  Flip.
        CMP     POINT,      R0          ; \__ Only recognize it if it's new
        BEQ     @@no_level_marker       ; /

        CALL    PLAYSFX                 ; \__ Ding the bell!
        DECLE   FXDING                  ; /

        MVII    #RCNXT,     R4          
        MVI@    R4,         R1          ; RCNXT + 0   (LSBs)
        MVI@    R4,         R2          ; RCNXT + 1   (MSBs)
        MVO@    R1,         R4          ; RCLVL + 0   (MSBs)
        MVO@    R2,         R4          ; RCLVL + 1   (MSBs)


        MVO     R0,         POINT       ; encode current course # into POINT
        ANDI    #$100,      R0          ; \_  If bit 8's set, this is a 
        BEQ     @@no_level_marker       ; /   summary checkpoint.

        MVO     R0,         LMCNT       ; Disable level-marker character
        MVII    #2,         R2          ; \_  Tell RUNENG we need to exit
        MVO     R2,         DNENG       ; /
@@no_level_marker


        ;; ---------------------------------------------------------------- ;;
        ;;  Show either CAUTION lamp or # of lives.  Only do this every     ;;
        ;;  8 ticks (just shy of 4 Hz).                                     ;;
        ;; ---------------------------------------------------------------- ;;
        MVII    #7,         R0
        AND     TIMTIC,     R0
        CMPI    #7,         R0          ; \_ TIMTIC held at 31 during init,
                                        ; /  so this forces life disp at init
        BNEQ    @@done_caut_life

        MVII    #disp_ptr(11,11),  R4   ; Point to where caution/lives lives


        MVI     CAUTFL,     R1          ; \
        SUBI    #4,         R1          ;  |_ Count down caution blink count
        BMI     @@show_lives            ;  |  and display lives if negative
        MVO     R1,         CAUTFL      ; /

        ANDI    #7,         R1          ; \
        ADDI    #@@cauttbl, R1          ;  |- Look up the caution flag color
        MVI@    R1,         R1          ; /

        ADDI    #gen_cstk_card(5, GRAM, Black, NoAdvance), R1
        MVO@    R1,         R4          ; \
        ADDI    #8,         R1          ;  |- Card #1-3 of caution
        MVO@    R1,         R4          ;  |
        ADDI    #8,         R1          ;  |
        MVO@    R1,         R4          ; /

        B       @@done_caut_life

@@show_lives:
        MVO@    R0,         R4          ; First square is blank
        MVII    #gen_cstk_card($27, GRAM, Purple, NoAdvance), R0
        MVO@    R0,         R4          ; Show miniature tank graphic

        MVI     LIVES,      R0          ; \
        SLL     R0,         2           ;  |- Single digit for lives
        SLL     R0,         1           ; /
        ADDI    #gen_cstk_card($10, GRAM, Blue, NoAdvance), R0
        MVO@    R0,         R4          ; Show lives

@@done_caut_life

        ;; ---------------------------------------------------------------- ;;
        ;;  Display the current checkpoint letter.                          ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     POINT,      R0          ; Get current checkpoint
        MOVR    R0,         R1          ; ... and save a copy
        BEQ     @@no_pt                 ; If it was NUL, display blank

        ANDI    #7,         R1          ; 3 LSBs give course number
        SUBR    R1,         R0          ; Upper 5 bits are ckpt letter

        ADDI    #CCTBL,     R1          ; \_ Look up color based on course
        ADD@    R1,         R0          ; /  number
        ADDI    #$100,      R0          ; Offset into alphabet
@@no_pt:
        MVO     R0,         disp_ptr(11, 9) ; Checkpoint letter
        MVII    #gen_cstk_card(13, GROM, DarkGreen, NoAdvance), R0
        MVO     R0,         disp_ptr(11, 8) ; Green bar to left of letter

        ;; ---------------------------------------------------------------- ;;
        ;;  Display the current score, but only if:                         ;;
        ;;   -- DOSCO is set (meaning it's changed or we're just starting)  ;;
        ;;   -- There was no mountain update this frame.                    ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     DOSCO,  R0              ; \
        DECR    R0                      ;  |_ Do update only if DOSCO == 1
        CMP     MPTR,   R0              ;  |  and MPTR == 0
        BNEQ    @@done                  ; /
        MVO     R0,     DOSCO    

        CALL    DISPSCORE
        DECLE   disp_ptr(11,1)

@@done:
        MVI     BGTTMP, PC

@@cauttbl:
        DECLE   X_RED, X_GRN, X_PNK, X_BLU, 0,0,0,0
        ENDP


CCTBL   PROC    ; Course Color Table
        ;       Beginner    Champion
        DECLE   X_BLK,      X_RED       ; Moon
        DECLE   X_GRN,      X_DGR       ; Mars
        DECLE   X_BLU,      X_TAN       ; Pluto
        DECLE   X_YEL,      X_WHT       ; Mercury
        ENDP

