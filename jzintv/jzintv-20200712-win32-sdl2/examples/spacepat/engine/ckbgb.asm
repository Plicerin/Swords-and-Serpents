;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  CKBGB     Checks the bad guys' bullets and sees if they hit anything.   ;;
;;==========================================================================;;
CKBGB   PROC
;       PSHR    R5

        MVI     MOBHIT, R0
        DECR    R0
        BEQ     @@nomobhit

  IF DODEAD
    P16_CSTK  0, 0, White, "DEAD"

    MVII    #1,     R0
    MVO     R0,     MOBHIT
  ELSE
        CLRR    R0              ; \
        MVO     R0,     DEFSCO  ;  |_  Tank died; pop out of RUNENG.
        INCR    R0              ;  |   and kill any deferred score
        MVO     R0,     DNENG   ; /
        B       @@skipdbloop
  ENDI

@@nomobhit

        MVII    #$FF,   R0
        MVO     R0,     TMP

        ;;------------------------------------------------------------------;;
        ;;  Step through group 2, 1st 5.                                    ;;
        ;;  If the Y position matches the ground, disable the bullet.       ;;
        ;;------------------------------------------------------------------;;
        MVII    #5,     R1
        MVII    #SPXY2, R4
        MVII    #SPAT2, R5
        B       @@db1st
@@dbskip:
        ADDI    #2,     R4
        DECR    R1
        BEQ     @@dbdone
@@dbloop:
@@db1st:
        MVI@    R5,     R0      ; get attr for bullet
        DECR    R0              ; is it 0
        BMI     @@dbskip        ; yes... skip it


        MVI@    R4,     R3      ; get X position
        MVI@    R4,     R0      ; get Y position
        SWAP    R3
        SWAP    R0
        CMPI    #250*256, R3    ;\
        BC      @@xok           ; |__ disable bullets that go off the
        CMPI    #170*256, R3    ; |   sides of the screen.
        BC      @@disspinX      ;/
@@xok:
        CMPI    #(GROW_p+9)*256, R0   ;
        BLT     @@dbyok         ; Is it on the ground yet?

        MVI     TMP,    R0      ; \ 
        ANDI    #$FE,   R0      ;  |- Small explosion if normal bullet
        MVO     R0,     TMP     ; /

        DECR    R5              ; Is it a spinner bullet?
        MVI@    R5,     R0
        CMPI    #SPATBL.b1, R0
        BEQ     @@spinb  
        CMPI    #SPATBL.b1b,R0
        BNEQ    @@disable
@@spinb

        MVI     CRATCNT, R0     ; \ 
        DECR    R0              ;  |-- If we did one too recently,
        BPL     @@disable0      ; /    don't do another yet

        ; If this was a spinner bullet, decide whether to make a crater.
        SUBI    #2,     R4      ;
        MVI@    R4,     R3      ; Get the X coord
        INCR    R4              ;
        ANDI    #$FF,   R3      ; \ 
        MVI     PGPHAS, R0      ;  |
        ANDI    #7,     R0      ;  |
        SUBR    R0,     R3      ;  |   Calculate card address of potential
        SLR     R3,     2       ;  |   crater location.  Account for phase.
        SLR     R3,     1       ;  |-- Disable stuff too far to right 
        CMPI    #18,    R3      ;  |   or too far to the left.
        BGE     @@disable1      ;  |
        CMPI    #9,     R3      ;  |
        BLT     @@disable2      ;  | 
        ADDI    #GROW,  R3      ; /
        CLRR    R0
        CMP@    R3,     R0      ; \
        BGT     @@disable3      ;  |
        INCR    R3              ;  |   Check a four-card range around 
        CMP@    R3,     R0      ;  |   the potential crash site.  We
        BGT     @@disable4      ;  |__ check the following pattern (X's): 
        ADDI    #18,    R3      ;  |    .XX.   This ensures that we
        CMP@    R3,     R0      ;  |    X..X   allow landing areas near
        BGT     @@disable5      ;  |   craters we make, keeping it fair.
        ADDI    #3,     R3      ;  |
        CMP@    R3,     R0      ;  |
        BGT     @@disable6      ; /

        ; If we get here, make the crater!
        SUBI    #GROW+20+3, R3
        MVO     R3,     CRATCNT ; Set up the "no new craters" counter.
        ADDI    #GROW-1+3,  R3

        MVI     TMP,    R0      ; \
        ANDI    #$FD,   R0      ;  |- Large explosion if we make a crater
        MVO     R0,     TMP     ; /
       
        MVII    #$0800 + RCS1.nosc,  R0
        MVO@    R0,     R3
        DECR    R3
        MVII    #$0800 + RCS1.sc500, R0
        MVO@    R0,     R3
        ADDI    #20,    R3
        MVII    #$8800 + X_ORG + (RCARD + 7)*8, R0
        MVO@    R0,     R3
        INCR    R3
        ADDI    #8,     R0
        MVO@    R0,     R3

        B @@disspin

@@disspinX:
        CMPI    #240*256, R3    ;
        BC      @@disable       ; Ignore bullets going off left.

@@disable0:
@@disable1:
@@disable2:
@@disable3:
@@disable4:
@@disable5:
@@disable6:

@@disspin:
        CLRR    R0              ;
        MVO     R0,     SPINB   ; Allow a new spinner bullet

@@disable:
        CLRR    R0              ; \  
        DECR    R5              ;  |-- Disable the sprite.
        MVO@    R0,     R5      ; / 
        DECR    R2
@@dbyok:

        DECR    R1
        BNEQ    @@dbloop
@@dbdone:

        MVI     TMP,    R2
        RRC     R2
        BC      @@nosmexp
        CALL    PLAYSFX
        DECLE   FXSMEXP
@@nosmexp:
        RRC     R2
        BC      @@nolgexp
        MVII    #FXLGEXP,   R1
        MVII    #@@nolgexp, R5
        B       DOPLAYSFX
@@nolgexp:
@@skipdbloop
;       PULR    PC
        ENDP
