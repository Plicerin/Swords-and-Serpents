;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

CRPTBL      DECLE   CREEPFNT2, CREEPFNT3, CREEPFNT4

;; ======================================================================== ;;
;;  LOADCRP  -- Load course-specific creeps.  Used below and mission menu   ;;
;; ======================================================================== ;;
LOADCRP     PROC
            MVO     R5,     BGTTMP
            
            CALL    LOADFONT
            DECLE   FONT

            CALL    LOADFONT
            DECLE   CREEPFNT

            MVI     COURSE, R1
            SLR     R1,     1
            DECR    R1
            BMI     @@course0
            ADDI    #CRPTBL,R1
            MVI@    R1,     R2
            CALL    LOADFONT.1
@@course0:  
            MVI     COURSE, R1
            SWAP    R1
;           ANDI    #$200,  R1
            SARC    R1,     2
            MVO     R1,     SPINCNT

            MVI     BGTTMP, PC
            ENDP

;; ======================================================================== ;;
;;  Initializer list for init'ing world.                                    ;;
;; ======================================================================== ;;
WINIT       PROC
            INIT    BGFLAG, 0
            INIT    LMCHAR, 0
            INIT    LMCNT,  0
            INIT    CAUTFL, 0
            INIT    JHGT,   0
            INIT    JVEL,   0
            INIT    RCCNT,  0
            INIT    RCPIC,  RCS1.blank - RCS1 + 1
            INIT    CUENUM, 0
            INIT    WAVE,   0
            INIT    WANTVL, VMED
            INIT    GRATE,  VMED
            INIT    WPTR,   WHEELS.data + WHEELS.nnn
            INIT    HBCNT2, 5 
            INIT    FCNT,   5 
            INIT    DOSCO,  1
            INIT_DONE
            ENDP

;; ======================================================================== ;;
;;  Top level game loop.  Wraps "INGAME".                                   ;;
;; ======================================================================== ;;
GAMELOOP    PROC
@@title:    CALL    INITMEM.1
            DECLE   WINIT

 IF (DEFINED SKIPTITLE) = 0
            SETISR  MISCISR
           
            INCLUDE "game/title.asm"; Set up 'Title Screen'
            B       RUNENG          ; Do title screen.
 ENDI      
RUNENG_RET_TITLE:

            SETISR  MISCISR

           
;           CALL    WAITHAND
@@menu      B       WORLDMENU
WORLDMENU_RET:
            
            SETISR  JRR5
            CALL    LOADCRP 

            CALL    INITMEM.0
            INIT    LMCNT,      0
            INIT    LMCHAR,     0
            INIT    FDROP,      0
            INIT    LIVES,      3
            INIT    CONTS,      2
;           INIT    LIVES,      0
;           INIT    CONTS,      0
            INIT    CURBON,     0
            INIT    TIMSEC,     0
            INIT    TIMTIC,     31
            INIT    EBSY,       1
;           INIT    GRATE,      0
;           INIT    WANTVL,     $90
            INIT    MOBHIT,     1
            INIT    POINT,      0
            INIT    SCORE,      0
            INIT    SCORE+1,    0
            INIT    PSCOR,      0
            INIT    PSCOR+1,    0
            INIT    DEFSCO ,    0
            INIT_DONE

            MVI     COURSE, R3
            ADDI    #WINDEX,R3
            MVI@    R3,     R3
            MVO     R3,     RCIDX
            MVO     R3,     RCLVL
            SWAP    R3
            MVO     R3,     RCLVL+1
          
            CALL    INITLVL

 IF (DEFINED SKIPHUT) = 0
            MVII    #4,     R0      ; \_ prepare to show "hut"
            MVO     R0,     EMODE   ; /
 ELSE
            MVII    #1,     R0      ; \_ Go straight to in-game
            MVO     R0,     EMODE   ; /
 ENDI

            B       @@cont
@@do_continue:
            CALL    INITMEM.0
            INIT    SCORE,  0
            INIT    SCORE+1,0
            INIT    CURBON, 0
            INIT    LIVES,  1
            INIT_DONE

@@again:    MVI     RCLVL+1,R0
            SWAP    R0
            XOR     RCLVL,  R0
            MVO     R0,     RCIDX
@@cont:     
            DIS

            CALL    INITMEM.1
            DECLE   WINIT
            CALL    SPINIT
            CALL    DRAWGAME 
            CALL    SFXINIT

            MVI     EMODE,  R0
            SUBI    #4,     R0
            BNEQ    @@do_restart

            CALL    TIC1ST          ; wants R0 == 0


            ; Ugly.  Rewrite this?  Actually it's not TOO bad.
            CALL    INITMEM.0
            INIT    SPAT+0,     SPATBL.hut0
            INIT    SPAT+1,     SPATBL.hut1
            INIT    SPAT+2,     SPATBL.hut2
            INIT    SPAT+3,     SPATBL.hut3
            INIT    SPXYP+0,    $20
            INIT    SPXYP+2,    $20
            INIT    SPXYP+4,    $20
            INIT    SPXYP+6,    $20
            INIT    SPHSCR+0,   1
            INIT    SPHSCR+1,   1
            INIT    SPHSCR+2,   1
            INIT    SPHSCR+3,   1
            INIT    RPTR,       HUT
            INIT    EMODE,      1
            INIT    GP1MOB,     4
            INIT    GDATA,      00111110b
            INIT    EBSY,       0
            INIT_DONE

            CALL    UPBSP
            CALL    UPMUX
            SETISR  ENGINE1             ; In case somehow it's not...

            JSRE    R5,         PLAY.mus
            DECLE   M_INTRO

            MVI     COURSE,     R5
            ANDI    #$6,        R5
            ADDI    #CNAME,     R5
            ADD     NN,         R5
            MVI@    R5,         R0      ; Get course name
            MVI@    R5,         R1      ; Get display offset
            SWAP    R1
            ANDI    #$7,        R1
            ADDI    #disp_ptr(6, 4), R1
            MOVR    R1,         R4
            MVII    #X_WHT,     R1
            CALL    P16.R

            CALL    WAIT_SONG1
            DECLE   128

            MVI     COURSE,     R2
            MVII    #BEGINNER,  R0
            SARC    R2
            BNC     @@beg
            MVII    #CHAMPION,  R0
@@beg       MVII    #disp_ptr(6, 2), R4
            MVII    #X_WHT,     R1
            CALL    P16.R

            CALL    P16.S
TXTCOURSE   S16     "COURSE"

            CALL    WAIT_SONG1
            DECLE   128

            CALL    P16.FLS
            DECLE   X_WHT, disp_ptr(6, 3)
                    ;
;           STRING  "     GO ", $14F, "      ", 0
            S16     "     GO \x0F      "

            CALL    WAIT_SONG1
            DECLE   $FFFF

            CALL    FILLZERO.lp
            DECLE   17
            DECLE   disp_ptr(6, 2)

@@do_restart:
            JSRE    R5,     PLAY.mus
            DECLE   M_GAME


    IF (DEFINED DOIDLEHST) <> 0
            CALL    FILLZERO.lp
            DECLE   256
            DECLE   IDLEHST
    ENDI
            B       RUNENG
RUNENG_RET_NORMAL:

            ; R2 tells us what to do next.
            ; R2 = 0 means the tank died, so just start the level over
            ;        or do game over.
            ; R2 = 1 means we hit a checkpoint, so do the checkpoint stuff
            ; R2 = 2 means go back to the menu

            CMPI    #2,     R2
            BEQ     @@title

            DECR    R2
            BMI     @@died

            B       CKPNT
CKPNT_RET

            MVI     POINT,  R0
            CMPI    #26 SHL 3, R0
            BNC     @@notafterz

            ; After Pt. Z, go to the game over screen w/out continues.
@@afterz:   MVII    #@@title, R5
            B       FINALOVER

@@notafterz MVII    #1,     R0
            MVO     R0,     EMODE
            
            B       @@again

@@died:     ; do tank dying stuff
            ; branch to @@over if the game's done.
            DIS

            MVI     LIVES,  R0
            DECR    R0
            MVO     R0,     LIVES

            ; the below code is mostly a temporary hack.  Eventually
            ; this will move to its own source file.

            MVI     HBCOL0, R1
            DECR    R1
            CMPI    #3,     R1
            BLT     @@x
            ADDI    #GROW,  R1
            CLRR    R0
            MVO@    R0,     R1
@@x
            SETISR  DIEDISR

            CLRR    R0              ; \
            MVO     R0,     SONG    ;  |-  Nuke any playing sounds and music
            MVO     R0,     DEFSCO  ;  |   and deferred score
            CALL    SFXINIT         ; / 

            CALL    PLAYSFX
            DECLE   FXDIED
;           EIS

            JSRE    R5,     UPSPA

            CLRR    R0             
@@diedspin: CMP     SFXTBL+6, R0    ; hack hack hack hack
            BNEQ    @@diedspin


            ; Now just wait a sec
            MVII    #120,       R1
            MVO     R1,         WTIMER
@@diedwait: CMP     WTIMER,     R0
            BNEQ    @@diedwait

            MVI     LIVES,      R0
            CMPI    #$FF,       R0
            BEQ     @@over

;           CALL    RSTLVL
            CALL    INITLVL.1
            B       @@again

            
           
@@over:     CALL    GAMEOVER        ; Do the 'Game Over' sequence.
            BPL     @@do_continue

;           CALL    WAIT
;           DECLE   60

            B       @@title
           
;           SETISR  RESTART
;           DECR    PC              ; Loop back to title screen after re-init
           
            ENDP
           
DIEDISR     PROC

            MVI     SDAT,   R0      ; \
            ANDI    #$FEFF, R0      ;  |
            MVO     R0,     SDAT    ;  |_ Clear INTR bits on tank.
            MVI     SDAT+1, R0      ;  | 
            ANDI    #$FEFF, R0      ;  | 
            MVO     R0,     SDAT+1  ; /

            MVI     SDAT+$10, R0
            MOVR    R0,     R1
            ANDI    #$FFF8, R0
            INCR    R1
            ANDI    #$7,    R1
            XORR    R1,     R0
            MVO     R0,     SDAT+$10 

            MVI     SDAT+$11, R0
            MOVR    R0,     R1
            ANDI    #$EFF8, R0
            INCR    R1
            ANDI    #$7,    R1
            XORR    R1,     R0
            MVO     R0,     SDAT+$11

            MVII    #SDAT,  R4
            CLRR    R5
            MVII    #8,     R2

@@l         MVI@    R4,     R0
            MVO@    R0,     R5
            MVI@    R4,     R0
            MVO@    R0,     R5
            MVI@    R4,     R0
            MVO@    R0,     R5
            DECR    R2
            BNEQ    @@l

            CLRR    R0
            MVO@    R0,     R5      ;
            MVO@    R0,     R5      ; clear tank collision bits

            MVO     R0,     $20
            CALL    UPSND
            MVII    #MISCISR.1, R5
            B       UPMUX
            ENDP
           
            
;; ======================================================================== ;;
;;  COLOR SCHEMEs                                                           ;;
;; ======================================================================== ;;

MNTNCLR     DECLE   X_CYN,  X_RED,  X_YGR,  X_TAN,  X_CYN
CRATCLR     DECLE   X_TAN,  X_GRY,  X_GRN,  X_YEL,  X_TAN
CITYCLR     DECLE   X_YEL,  X_TAN,  X_YEL

MACRO       pack_cstk(a,b,c,d)
    (%a%)+(%b% SHL 4)+(%c% SHL 8) + (%d% SHL 12)
ENDM

;; ======================================================================== ;;
;;  Color Scheme                                                            ;;
;; ======================================================================== ;;
CSTKCLR     DECLE   pack_cstk(C_BLK, C_CYN, C_TAN, C_GRY) ; moon crater
            DECLE   pack_cstk(C_BLK, C_CYN, C_YEL, C_GRY) ; moon city
            DECLE   pack_cstk(C_BLK, C_RED, C_GRY, C_GRY) ; mars crater
            DECLE   pack_cstk(C_BLK, C_RED, C_TAN, C_GRY) ; mars city
            DECLE   pack_cstk(C_BLK, C_YGR, C_GRN, C_GRY) ; pluto crater
            DECLE   pack_cstk(C_BLK, C_YGR, C_YEL, C_GRY) ; pluto city
            DECLE   pack_cstk(C_BLK, C_TAN, C_YEL, C_GRY) ; mercury crater
            DECLE   pack_cstk(C_GRN, C_DGR, C_YGR, C_GRY) ; mercury underground
;           DECLE   pack_cstk(C_BLK, C_CYN, C_TAN, C_BLK) ; title screen


; Underground scene for Mercury
X_RKBG      EQU     X_GRN
C_RKBG      EQU     C_GRN

X_STAL      EQU     X_YGR
C_STAL      EQU     C_YGR

;; ======================================================================== ;;
;;  DRAWGAME                                                                ;;
;;                                                                          ;;
;;  This intends to be a rewrite of the DRAWGAME function from LunarMP.     ;;
;;  Rather than using long-hand tables, it should compute the cards going   ;;
;;  to the display, since drawing the display isn't terribly time critical. ;;
;;                                                                          ;;
;;  It needs to understand color schemes as well as the three screen        ;;
;;  layouts:  Craters, City, and Underground.                               ;;
;; ======================================================================== ;;
DRAWGAME    PROC
            PSHR    R5

            ;; ------------------------------------------------------------ ;;
            ;;  Shut off stuff for a bit.                                   ;;
            ;; ------------------------------------------------------------ ;;
            MVI     EMODE,      R0
            MVO     R0,         TMP
            CLRR    R0
            MVO     R0,         EMODE 

            ;; ------------------------------------------------------------ ;;
            ;;  Initialize the color stack.                                 ;;
            ;; ------------------------------------------------------------ ;;
            SETISR  SETCSG              ; request colorstack update for game
            JSRE    R5,         WAIT
            DECLE   1
           
            ;; ------------------------------------------------------------ ;;
            ;;  Go incognito for a moment and start building the screen.    ;;
            ;; ------------------------------------------------------------ ;;
            DIS

            CALL    RSGGB               ; Reset good guy bullets.
           
            CALL    FILLZERO.lp         ; \
            DECLE   25                  ;  |- nuke any remaining bad guys
            DECLE   BGMPTBL             ; /
           
            CALL    FILLZERO.lp         ; \
            DECLE   10                  ;  |- and their sprites
            DECLE   SPAT                ; /
           
            CALL    CLRSCR              ; nuke the display.
           
            ;; ------------------------------------------------------------ ;;
            ;;  For all scenes other than underground, twinkle some stars.  ;;
            ;; ------------------------------------------------------------ ;;
            MVI     INCITY,     R0
            CMPI    #2,         R0
            BEQ     @@notwinkle

            MVII    #100,       R0
@@twloop
            PSHR    R0
            CALL    TWINKLE
            PULR    R0
            DECR    R0
            BNEQ    @@twloop
@@notwinkle
           

            ;; ------------------------------------------------------------ ;;
            ;;  Draw initial status bar graphics.                           ;;
            ;; ------------------------------------------------------------ ;;
;           CALL    PRINT.FLS
;           DECLE   gen_cstk_card(0, GRAM, Black, NoAdvance)
;           DECLE   disp_ptr(11, 0)
;                   ;01234567890123456789
;           STRING  "           #$    :  ", 0   ; "Time" and "Pt"

            MVII    #TMCARDx,   R0
            MVO     R0,         disp_ptr(11, 15)
;           MVII    #PTCARDx,   R0
;           MVO     R0,         disp_ptr(11, 17)
           
           
            ;; ------------------------------------------------------------ ;;
            ;;  Draw the display elements.  Logic:                          ;;
            ;;                                                              ;;
            ;;  Draw the underground scene if INCITY == 2, else             ;;
            ;;     (draw the crater strip if INCITY = 0, or                 ;;
            ;;      draw the city strip if INCITY = 1), and then            ;;
            ;;      draw the upper mountain chain.                          ;;
            ;; ------------------------------------------------------------ ;;

            MVI     INCITY,     R1      ; \
            CMPI    #2,         R1      ;  |- Underground gets special 
            BEQ     @@underground       ; /   treatment.

            MVII    #CCARD*8+$0800, R0  ; City/crater starting card #

            TSTR    R1                  ; \__ decide whether to draw the 
            BNEQ    @@in_city           ; /   crater or city strips.

            ;; ------------------------------------------------------------ ;;
            ;;  Draw the crater strip in selected color scheme.             ;;
            ;; ------------------------------------------------------------ ;;
            MVI     COURSE,     R1      ; \
            ANDI    #7,         R1
            SLR     R1,         1       ;  |_ Adjust color for course
            ADDI    #CRATCLR,   R1      ;  |
            ADD@    R1,         R0      ; /
            MOVR    R0,         R2      ;
            ADDI    #7*8,       R2      ; City/crater ending card #
            
            MVII    #MROW,      R4  
            MVII    #20,        R3
@@crat_loop:
            MVO@    R2,         R4      ; display card
            SUBI    #8,         R2      ; move to prev card #
            CMPR    R0,         R2      ; \
            BGE     @@crat_ok           ;  |- wrap from 0 back to 7 as needed
            ADDI    #64,        R2      ; /
@@crat_ok:  DECR    R3                  ;
            BNEQ    @@crat_loop         ; loop it!
            
            B       @@done_mid

            ;; ------------------------------------------------------------ ;;
            ;;  Draw the city strip in selected color scheme.               ;;
            ;; ------------------------------------------------------------ ;;
@@in_city:
            MVI     COURSE,     R1      ; \
            SLR     R1,         1       ;  |_ Adjust color for course
            ADDI    #CITYCLR,   R1      ;  |
            ADD@    R1,         R0      ; /
            MOVR    R0,         R2      ;
            ADDI    #7*8,       R2      ; City/crater ending card #

            MVII    #CROW,      R4
            MVII    #CROW + 20, R5

            MVII    #@@done_mid, R3     ; will reuse this loop as a func below
            B       @@city_fill_start
@@city_fill:
            MOVR    R5,         R3
            MOVR    R4,         R5
            ADDI    #20,        R5

@@city_fill_start:
            MVII    #5,         R0
@@city_fill1
            PSHR    R3
            MVII    #8,         R3

@@city_loop:
            MVO@    R2,         R5      ; \
            SUBR    R3,         R2      ;  |_ column 0 mod 4
            MVO@    R2,         R4      ;  |
            SUBR    R3,         R2      ; /

            MVO@    R2,         R5      ; \
            SUBR    R3,         R2      ;  |_ column 1 mod 4
            MVO@    R2,         R4      ;  |
            SUBR    R3,         R2      ; /

            MVO@    R2,         R5      ; \
            SUBR    R3,         R2      ;  |_ column 2 mod 4
            MVO@    R2,         R4      ;  |
            SUBR    R3,         R2      ; /

            MVO@    R2,         R5      ; \
            SUBR    R3,         R2      ;  |_ column 3 mod 4
            MVO@    R2,         R4      ;  |
            ADDI    #56,        R2      ; /

            DECR    R0
            BNEQ    @@city_loop

            PULR    PC                  ; "return"

@@done_mid:

            ;; ------------------------------------------------------------ ;;
            ;;  Fix up color stack on city after drawing it.                ;;
            ;; ------------------------------------------------------------ ;;
            MVI     TROW+60,R0          ;  10 
            XORI    #$2000, R0          ;   8
            MVO     R0,     TROW+60     ;  11

            ;; ------------------------------------------------------------ ;;
            ;;  Draw the mountain chain in selected color scheme.           ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #(TCARD + 7)*8 + $800, R2 ; 
            MVI     COURSE,     R1      ; \
            ANDI    #7,         R1
            SLR     R1,         1       ;  |_ Adjust color for course
            ADDI    #MNTNCLR,   R1      ;  |
            ADD@    R1,         R2      ; /
            MOVR    R2,         R1

            MVII    #TROW,      R4
            CALL    @@city_fill         ; Reuse the city_loop to fill mountain

            MVII    #TROW + 40, R4
            SUBI    #4*8,       R1
            MOVR    R1,         R2
            MVII    #@@finish_mntn, R5  ; will reuse like a function below
@@mntn_fill:
            MVII    #5,         R0
@@mntn_loop:
            MVO@    R2,         R4
            SUBI    #16,        R2
            MVO@    R2,         R4
            ADDI    #48,        R2
            MVO@    R2,         R4
            SUBI    #16,        R2
            MVO@    R2,         R4
            SUBI    #16,        R2

            DECR    R0
            BNEQ    @@mntn_loop

            JR      R5

@@finish_mntn:
            MVII    #$2000,     R0          ; \ _ Color stack advance for
            MVO     R0,         GROW        ; /   ground
            B       @@done_field

            ;; ------------------------------------------------------------ ;;
            ;;  Draw the underground scene.                                 ;;
            ;; ------------------------------------------------------------ ;;
@@underground:
            MVII    #(CCARD+2)*8 + $800 + X_STAL, R2 ; stalagtites/stalagmites
            MVII    #STROW1,    R4
            CALL    @@mntn_fill

            MVII    #(CCARD+3)*8 + $800 + X_RKBG, R2 ; stalagtites/stalagmites
            MVII    #STROW2,    R4
            CALL    @@mntn_fill

            MVII    #(TCARD+7)*8 + $800 + X_RKBG, R2 ; background rocks
            MVII    #RKROW + 4*20,  R4  ;  last 2 rows
            CALL    @@city_fill         ;  fill 2 rows of background rocks

            MVII    #(TCARD+7)*8 + $800 + X_RKBG, R2 ; background rocks
            MVII    #RKROW,         R4  ;  first 2 rows
            CALL    @@city_fill         ;  fill 2 rows of background rocks

            MVII    #(TCARD+2)*8 + $800 + X_RKBG, R2 ; background rocks
            MVII    #RKROW + 40,    R4  ;  
            CALL    @@mntn_fill         ;  fill 3rd row 

            MVII    #(TCARD+3)*8 + $800 + X_RKBG, R2 ; background rocks
            CALL    @@mntn_fill         ;  fill 4th row 

            ;; ------------------------------------------------------------ ;;
            ;;  Fixup color stack for background scene.                     ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$2000,     R0
            XOR     RKROW,      R0
            MVO     R0,         RKROW
                               
            MVII    #$2000,     R0
            XOR     STROW2,     R0
            MVO     R0,         STROW2
                               
            CLRR    R0         
            MVO     R0,         GROW 

            ;; ------------------------------------------------------------ ;;
            ;;  Now draw the remaining invariant portions of the screen.    ;;
            ;;  The "ground row" -- e.g. where the buggy drives.            ;;
            ;; ------------------------------------------------------------ ;;
@@done_field:
            CALL    FILLMEM.vlp
            DECLE   1, 19, GROW+1

        
            CALL    FILLMEM.vlp
            DECLE   GCARDx, 20, GROW+20
           
            CALL    FILLMEM.vlp
            DECLE   $0800 + (74-32)*8 + X_GRND
            DECLE   19
            DECLE   GROW + 41
            
            MVII    #$2800 + (74-32)*8 + X_GRND, R0 ; \  Color stack adv. for
            MVO     R0,         GROW + 40           ; /  status line
           
            ;; ------------------------------------------------------------ ;;
            ;;  Ok, ready to show the world, kinda.  Mark the engine as     ;;
            ;;  busy so that we can load the GRAM.  We will set our ISR     ;;
            ;;  such that the display won't enable.                         ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #1,         R0
            MVO     R0,         EBSY
           
            MVI     TMP,        R0
            MVO     R0,         EMODE 
           
            ;; ------------------------------------------------------------ ;;
            ;;  Ok, disable interrupts again and set up the scroll engine   ;;
            ;;  internal variables.                                         ;;
            ;; ------------------------------------------------------------ ;;
            JSRD    R5,     INITMEM.0
            INIT    EBSY,   0
            INIT    FDROP,  0
            INIT    GPHASE, $80
            INIT    TPHASE, 0
            INIT    MPHASE, 0
            INIT    PGCARD, $FF
            INIT    PGPHAS, $FF
            INIT    PTCARD, $FF
            INIT    PMPHAS, $FF
            INIT_DONE
@@xxx:
            ;; ------------------------------------------------------------ ;;
            ;;  Ok, let everything settle out, so that when we turn on the  ;;
            ;;  lights, hopefully the right GRAM images are all loaded.     ;;
            ;; ------------------------------------------------------------ ;;
            CALL    SETGFX

            MVII    #1,         R0          ; Clear any lingering death.
            MVO     R0,         MOBHIT      ; Do it after SETGFX.

           
            ;; ------------------------------------------------------------ ;;
            ;;  Restore the normal engine and let 'er rip!                  ;;
            ;; ------------------------------------------------------------ ;;
            SETISR  ENGINE1
           
            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  SETGFX  Load up mid and top mountain graphics for game display.         ;;
;; ======================================================================== ;;
SETGFX      PROC

            MVII    #ROCKCRAT,  R0
            MVO     R0,         RPTR

            ;; ------------------------------------------------------------ ;;
            ;;  The 'INCITY' flag toggles us between the three layouts.     ;;
            ;;  The 'COURSE' flag indicates which color scheme and graphic  ;;
            ;;  set to use.                                                 ;;
            ;; ------------------------------------------------------------ ;;
            MVI     INCITY,     R0
            TSTR    R0
            BEQ     @@start_crater

@@start_city:
            MVII    #$E0,       R1      ; update mask for cities
            MVI     COURSE,     R2      ;\
            SLR     R2,         1       ; |_load city graphic ptr for course
            ADDI    #@@cities,  R2      ; |
            MVI@    R2,         R0      ;/ 
            B       @@start_cont 

@@cities:   DECLE   MIDCITY1 SHR 8, MIDCITY2 SHR 8
            DECLE   MIDCITY3 SHR 8, MIDCITY4 SHR 8
            IF ((MIDCITY1 OR MIDCITY2 OR MIDCITY3 OR MIDCITY4) AND $FF) <> 0
                ERR "MIDCITY must be 256-word aligned"
            ENDI
            IF ((MIDMOUNT) AND $FF) <> 0
                ERR "MIDMOUNT must be 256-word aligned"
            ENDI

@@start_crater:
            MVII    #MIDMOUNT SHR 8, R0 ; Stalagtite/stalagmites
            MVII    #$C0,       R1      ; update mask for craters

@@start_cont:
            MVO     R0,         MIDGFX
            MVO     R1,         MIDMSK
            MVO     R5,         BGTTMP

            SETISR  ENGINE1.1

            MVI     MIDGFX,     R0
            SWAP    R0
            MVO     R0,         MPTR
            MVII    #MIDGR,     R0
            MVO     R0,         MGRAM
            CLRR    R0
            MVO     R0,         MGOFS
            JSRE    R5,         WAIT
            DECLE   1

            DIS
            MVII    #TOPMOUNT,  R0
            MVI     INCITY,     R3
            CMPI    #2,         R3
            BNEQ    @@asis
            MVII    #ROCKBG,    R0
@@asis:     MVO     R0,         MPTR
            MVII    #TOPGR,     R0
            MVO     R0,         MGRAM
            JSRE    R5,         WAIT
            DECLE   1 

            CLRR    R0
            MVO     R0,         MPTR

            MVI     BGTTMP,     PC
            ENDP

           
;; ======================================================================== ;;
;;  SETCSG  Sets up the color stack for the in-game sequences.              ;;
;; ======================================================================== ;;
SETCSG      PROC

            MVI     $21,        R0          ; set Color stack mode

            MVI     INCITY,     R1          ; \
            CMPI    #1,         R1          ;  |
            MVI     COURSE,     R1          ;  |_ Get color scheme for course
            MOVR    R1,         R0
            ANDI    #6,         R1
;           SLR     R1,         1           ;  |
;           RLC     R1,         1           ;  |
            ADCR    R1
            ADDI    #CSTKCLR,   R1          ;  |
            MVI@    R1,         R1          ; /

            CMPI    #8,         R0          ; \
            BLT     @@ok                    ;  |- black strip at bottom 
            ANDI    #$0FFF,     R1          ; /   of title screen


@@ok        MVII    #CS0,       R4
            MVO@    R1,         R4
            SLR     R1,         2
            SLR     R1,         2
            MVO@    R1,         R4
            SLR     R1,         2
            SLR     R1,         2
            MVO@    R1,         R4
            SLR     R1,         2
            SLR     R1,         2
            MVO@    R1,         R4
       
;           MVI     FDROP,      R0
;           INCR    R0
;           MVO     R0,         FDROP
            B       MISCISR.wtimer
            
            ENDP


;* ======================================================================== *;
;*  This program is free software; you can redistribute it and/or modify    *;
;*  it under the terms of the GNU General Public License as published by    *;
;*  the Free Software Foundation; either version 2 of the License, or       *;
;*  (at your option) any later version.                                     *;
;*                                                                          *;
;*  This program is distributed in the hope that it will be useful,         *;
;*  but WITHOUT ANY WARRANTY; without even the implied warranty of          *;
;*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       *;
;*  General Public License for more details.                                *;
;*                                                                          *;
;*  You should have received a copy of the GNU General Public License       *;
;*  along with this program; if not, write to the Free Software             *;
;*  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.               *;
;* ======================================================================== *;
;*                   Copyright (c) 2006, Joseph Zbiciak                     *;
;* ======================================================================== *;
