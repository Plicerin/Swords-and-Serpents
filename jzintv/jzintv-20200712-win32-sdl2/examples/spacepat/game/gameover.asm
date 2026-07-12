;; ======================================================================== ;;
;;  GAMEOVER                                                                ;;
;;  Guess what?  It's game over time!!                                      ;;
;; ======================================================================== ;;
GAMEOVER    PROC
            PSHR    R5

            ; Clear all the sprites UNLESS crat6 is onscreen (end of Pluto)
            MVI     RCIDX,          R0
            CMPI    #PLUT_C.crat6,  R0
            BC      @@no_spinit
            CALL    SPINIT
@@no_spinit:
            CLRR    R0
            MVO     R0,         SDAT
            MVO     R0,         SDAT+1

            CALL    P16.FLS
            DECLE   X_WHT, disp_ptr(6, 4)
            S16     " Game Over "

            CALL    PLAY.mus
            DECLE   M_OVER

            JSRE    R5,         WAIT_SONG1
            DECLE   $FFFF

            CALL    WAIT
            DECLE   60

            JSRD    R5,         CLRSCR
            SETISR  CKPTISR
            JSRE    R5,         WAIT1

            ; set up color stack properly ahead of time
            CALL    INITMEM
            INIT    TMP,        1       ; default to "yes" on continue
            INIT    TMP+1,      1       ; highlight "yes" in blue
            INIT    TMP+2,      0       ; don't highlight "no"
            INIT_DONE

            SETISR  CONTISR
            CALL    WAIT1
            
            MVI     CONTS,      R0
            DECR    R0
            BMI     @@nocont
            MVO     R0,         CONTS

            CALL    DISPFINAL
            DECLE   disp_ptr(2, 0)
            CALL    DISPPEAK 
            DECLE   disp_ptr(4, 0)

            CALL    P16.FLS
            DECLE   X_WHT, disp_ptr(7, 5)
            S16     "Continue?"

            CALL    P16.FLS
            DECLE   X_YEL, disp_ptr(9, 6)
            S16     "Yes  No"

            MVII    #$2000,     R0
            MVO     R0,         disp_ptr(9, 5)
            MVO     R0,         disp_ptr(9,10)
            MVO     R0,         disp_ptr(9,14)


            B       @@first
@@loop_yn   CALL    TINK

@@first     MVII    #TMP,       R4
            MVI@    R4,         R0
            MVO@    R0,         R4
            XORI    #1,         R0
            MVO@    R0,         R4
            
@@keyl      CALL    MENUINP
            BPL     @@done_yn

            CLRR    R1

            SARC    R0,     2
            BOV     @@right
            SARC    R0,     2
            BNOV    @@keyl

@@left:     INCR    R1
@@right:    CMP     TMP,    R1
            BEQ     @@keyl
            MVO     R1,     TMP
            B       @@loop_yn

@@done_yn   CALL    TINK
            CALL    WAITNOKEY

            MVI     TMP,    R0
            DECR    R0                  ; Continue flag in S.
            
@@done      PULR    PC

FINALOVER   
            PSHR    R5
            JSRD    R5,         CLRSCR
            SETISR  CKPTISR
            JSRE    R5,         WAIT1
            SETISR  CONTISR
@@nocont    
            
            MVI     COURSE,     R5
            ANDI    #$6,        R5
            ADDI    #CNAME,     R5
            ADD     NN,         R5
            MVI@    R5,         R0      ; Get course name
            MVI@    R5,         R1      ; Get display offset
            SWAP    R1
            ANDI    #$7,        R1
            ADDI    #disp_ptr(1, 4), R1
            MOVR    R1,         R4
            MVII    #X_WHT,     R1
            CALL    P16.R

            MVI     COURSE,     R2
            MVII    #BEGINNER,  R0
            SARC    R2
            BNC     @@beg
            MVII    #CHAMPION,  R0
@@beg       MVII    #disp_ptr(3, 2), R4
            MVII    #X_WHT,     R1
            CALL    P16.R

            CALL    P16.P
            DECLE   TXTCOURSE


            CALL    DISPFINAL
            DECLE   disp_ptr(6, 0)
            CALL    DISPPEAK 
            DECLE   disp_ptr(8, 0)

    IF 0
            MVII    #WAITKEY.1, R5      ; Waitkey returns w/ S=1
            B       UPTSS               ; but go there via UPTSS
    ELSE
            B       WAITKEY.1
    ENDI

;           CLRR    R0                  ; Continue flag in S.
;           DECR    R0

;           PULR    PC
            ENDP

CONTISR     PROC
            MVI     TMP+1,  R0
            MVI     TMP+2,  R1
            CLRR    R2
            MVII    #$28,   R4
            MVO@    R2,     R4
            MVO@    R0,     R4
            MVO@    R1,     R4
            MVO@    R2,     R4
            MVI     $21,    R0
            B       MISCISR
            ENDP

