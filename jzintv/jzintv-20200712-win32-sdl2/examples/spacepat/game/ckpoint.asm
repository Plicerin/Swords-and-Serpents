;; ======================================================================== ;;
;;  Checkpoint Summary Screen                                               ;;
;;                                                                          ;;
;;  This screen shows a summary of how long it took the player to reach     ;;
;;  the given checkpoint, as well as what the "par" and "record" times      ;;
;;  are for this checkpoint.  This screen counts up any bonus points that   ;;
;;  might've been earned as well.                                           ;;
;;                                                                          ;;
;;  Sequence:                                                               ;;
;;                                                                          ;;
;;   -- Hide, or at least freeze, all the sprites                           ;;
;;                                                                          ;;
;;   -- Play the 'congratulations' theme                                    ;;
;;                                                                          ;;
;;   -- Clear the screen                                                    ;;
;;      (Should I do the wipe I used for the demo loop?)                    ;;
;;                                                                          ;;
;;   -- Display the above screen in stages                                  ;;
;;       -- Display from top to bottom, with some pauses thrown in          ;;
;;       -- Once display is complete, count 'average time' down to          ;;
;;          actual time and add it to the bonus.                            ;;
;;                                                                          ;;
;;   -- Pause for 3 to 5 seconds                                            ;;
;;       -- or wait for tap from player, since this isn't an arcade.        ;;
;;                                                                          ;;
;;   -- Exit                                                                ;;
;;                                                                          ;;
;;                                                                          ;;
;; ======================================================================== ;;

CKPNT       PROC

            JSRD    R5,     SFXINIT
            SETISR  CKPTISR.1

            ;; ------------------------------------------------------------ ;;
            ;;  Play congrats song.                                         ;;
            ;; ------------------------------------------------------------ ;;
            MVI     POINT,      R3          ; Get current level
            CMPI    #26 SHL 3,  R3          ; is it point 'Z'?
            BC      @@end_of_course         ; Play special if it's exactly 'Z'

            CALL    PLAY.mus
            DECLE   M_LEVEL

            B       @@wait_music

@@end_of_course
            CALL    PLAY.mus
            DECLE   M_COURS


            ;; ------------------------------------------------------------ ;;
            ;;  Wait for congrats song to finish.                           ;;
            ;; ------------------------------------------------------------ ;;
@@wait_music
            JSRE    R5,         WAIT_SONG

            ;; ------------------------------------------------------------ ;;
            ;;  Ok, we've now officially shut down the display.  Go ahead   ;;
            ;;  and put up the congrats screen.                             ;;
            ;; ------------------------------------------------------------ ;;
            CALL    HALTENGINE
            SETISR  CKPTISR
            CALL    CLRSCR

            ;; ------------------------------------------------------------ ;;
            ;;  Step through the data table and draw up the screen.  The    ;;
            ;;  layout shifts slightly depending on whether the ECS is      ;;
            ;;  attached.                                                   ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #CPDAT.norec,   R5
            ; todo: put code here to detect ECS / top record table

            INCR    PC
@@dloop:
            PULR    R5
            MVI@    R5,         R1              ; get format word
            SARC    R1,         2
            BMI     @@special                   ; if -ve, this is special rec
            BEQ     @@dldone                    ; if 0, we're done.

            MVI@    R5,         R4              ; get display ptr
            MVI@    R5,         R0              ; get string ptr
            PSHR    R5                          ; \
            MVII    #@@dloop,   R5              ;  |- print it and loop
            B       P16.R                       ; /

@@special:
            PSHR    R5
            MVI     POINT,      R3              ; Get saved point # + course #
            BC      @@disp_point                ; point # and player's time
            BOV     @@disp_avg                  ; average for point #

@@disp_rec: HLT                                 ; not yet implemented!


@@disp_point:
            MOVR    R3,         R2              ; \
            ANDI    #7,         R2              ;  |- Course number in R2,
            SUBR    R2,         R3              ; /   Point number<<2 in R3
            ADDI    #CCTBL,     R2              ; Course-specific formatting
            ADDI    #32*8,      R3              ; Bias up to alphabet
            ADD@    R2,         R3              ; add formatting to point #
            MOVR    R3,         R2
            ANDI    #7,         R2
            BNEQ    @@color_ok
            XORI    #X_TAN,     R3
@@color_ok


            SUBI    #2,         R4              ; back up cursor 2 posns.

            MVO@    R3,         R4              ; Print it before the ":"

            ADDI    #4,         R4              ; \
            MVI     TIMSEC,     R0              ;  |- print player's time.
            CALL    PRNUM16.bfw                 ; /
            DECLE   gen_cstk_card(0, GRAM, White, NoAdvance), 3

            B       @@dloop

@@disp_avg:
            MVI     COURSE,     R1              ; 
            ADDI    #PARTBL,    R1              ; \__ Par time based course #
            MVI@    R1,         R0              ; /   
            CMPI    #15 SHL 3,  R3              ; \   keep upper/lower byte
            ADCR    PC                          ;  |- based on being in front
            SWAP    R0                          ; /   or back half of course
            MVO     R0,         TMP             ; Remember par time
            ANDI    #$FF,       R0

            ADDI    #4,         R4              ; \
            MVO     R4,         TMP+1           ;  |_ Print par time
            CALL    PRNUM16.bfw                 ;  |  
            DECLE   gen_cstk_card(0, GRAM, White, NoAdvance), 3

            B       @@dloop

@@dldone:   MVI     POINT,      R1
            CMPI    #26 SHL 3,  R1
            BLT     @@not_z

            MVI     LIVES,      R0
            TSTR    R0
            BNEQ    @@tank_bonus

            CALL    P16.FLS
            DECLE   X_TAN, disp_ptr(9,3)
            S16     "No tank bonus!" 
            B       @@not_z

@@tank_bonus:
            CALL    P16.FLS
            DECLE   X_TAN, disp_ptr(9,0)
            S16     "Tank bonus:" 

            CLRR    R0
            MVO     R0,         TMP+3

@@tb        MVI     TMP+3,      R0
            INCR    R0
            MVO     R0,         TMP+3

            SLL     R0,         1

            MVII    #disp_ptr(9, 13), R4
            CALL    PRNUM16.bfw
            DECLE   gen_cstk_card(0, GRAM, White, NoAdvance), 3
            MVII    #gen_cstk_card($10, GRAM, White, NoAdvance), R0
            MVO@    R0,     R4
            MVO@    R0,     R4
            MVO@    R0,     R4
            MVO@    R0,     R4

;           MVII    #X_WHT, R1
;           CALL    P16.S
;           S16     "10000"

            CSTSCO  20000

            CALL    PLAYSFX
            DECLE   FXDING

            CALL    WAIT
            DECLE   10

            MVI     TMP+3,      R0
            CMP     LIVES,      R0
            BLT     @@tb


@@not_z:

            MVI     TMP,        R2
            SUB     TIMSEC,     R2              ; Did we beat par?
            BGT     @@bonus

            CALL    P16.FLS
            DECLE   X_TAN
            DECLE   disp_ptr(10,3)
            S16     "No time bonus!"
            B       @@done

@@bonus:
            MOVR    R2,         R0
            SLL     R0,         2               ; \
            MOVR    R0,         R1              ;  |_ 1000 pts per sec
            SLL     R1,         2               ;  |
            ADDR    R1,         R0              ; /
            REGSCO

            CALL    WAIT
            DECLE   60

            CALL    P16.FLS
            DECLE   X_TAN
            DECLE   disp_ptr(10,0)
            S16     "Time bonus:  "
;           ADDI    #1,     R4
;           INCR    R4

;   CMPI    #21,    R2
;   BGT     @@done

            CLRR    R0
            PSHR    R0
            MOVR    R4,     R1
            B       @@bl1st
@@bloop:
            DECR    R0
            MVO     R0,     TMP
            MVI     TMP+1,  R4
            ADDI    #$200,  R4
            CALL    PRNUM16.bfw
            DECLE   gen_cstk_card(0, GRAM, White, NoAdvance), 3
            PULR    R0

            MOVR    R1,     R4
;           ADDI    #100,   R0
            INCR    R0
            PSHR    R0
            CALL    PRNUM16.bw
            DECLE   4
            MVII    #gen_cstk_card($10, GRAM, White, NoAdvance), R0
            MVO@    R0,     R4
            MVO@    R0,     R4
            MVO@    R0,     R4

;           MOVR    R1,     R2
            CALL    PLAYSFX
            DECLE   FXDING
;           MOVR    R2,     R1

            CALL    WAIT
            DECLE   10

@@bl1st     MVI     TMP,    R0
            CMP     TIMSEC, R0
            BNEQ    @@bloop

            PULR    R0


@@done      CALL    WAIT
            DECLE   60 * 4      ; wait 4 seconds

            DIS
            SETISR  ENGINE1

            CLRR    R0
            MVO     R0,     TIMSEC

;           CALL    UPTSS

            MVI     POINT,  R0
            ANDI    #$8,    R0
            MVII    #CKPNT_RET, R5
            EIS
            BNEQ    TOCITY
            B       TOCRATER

            ENDP

;; ------------------------------------------------------------------------ ;;
;;  PARTBL  Base par times for each of the 8 courses.                       ;;
;; ------------------------------------------------------------------------ ;;
                     ;Beg E/J, Beg OTZ,      Cmp E/J, Cmp OTZ
PARTBL      DECLE   pack(70,     90),      pack(80,    100)
            DECLE   pack(70,     90),      pack(80,    100)
            DECLE   pack(80,     100),     pack(90,    110)
            DECLE   pack(80,     100),     pack(90,    110)

;; ------------------------------------------------------------------------ ;;
;;                          01234567890123456789                            ;;
;;                                                                          ;;
;;                       0 :  CONGRATULATIONS!  :                           ;;
;;                       1 :                    :                           ;;
;;                       2 :Your time to        :                           ;;
;;                       3 :reach Point E:   XXX:                           ;;
;;                       4 :                    :                           ;;
;;                       5 :Average time:    XXX:                           ;;
;;                       6 :                    :                           ;;
;;                       7 :Top record time: XXX:  (if ECS attached)        ;;
;;                       8 :                    :                           ;;
;;                       9 : Course bonus: XXXXX:  (if point Z)             ;;
;;                      10 :   Time bonus: XXXXX:  (if better than avg.)    ;;
;;                      10 :   No time bonus!   :  (if not)                 ;;
;;                      11 :                    :                           ;;
;;                                                                          ;;
;;  Note:  If no ECS attached, shift rows 2 thru 5 down 2 and row 0 down 1. ;;
;; ------------------------------------------------------------------------ ;;
CPDAT       PROC
@@norec     DECLE   X_RED SHL 2,  disp_ptr(1, 2), @@congrat
            DECLE   X_TAN SHL 2,  disp_ptr(3, 0), @@yourtime
            DECLE   X_TAN SHL 2,  disp_ptr(4, 0), @@reach,   $FFFF
            DECLE   X_TAN SHL 2,  disp_ptr(6, 0), @@avgtime, $FFFE
            DECLE   0

@@congrat   S16     "CONGRATULATIONS!"
@@yourtime  S16     "Your time to"
@@reach     S16     "reach Point  :"
@@avgtime   S16     "Average time:"
            ENDP


;;==========================================================================;;
;;  CKPTISR                                                                 ;;
;;==========================================================================;;
CKPTISR PROC

        CLRR    R0
        CLRR    R4
        REPEAT  8
        MVO@    R0,     R4
        ENDR

        MVO     R0,     $28
        MVO     R0,     $2C
@@1:    MVO     R0,     $20

@@2:    MVII    #MISCISR.1, R5
        B       UPSND

        ENDP
