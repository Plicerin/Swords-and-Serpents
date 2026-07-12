;; ======================================================================== ;;
;;  TITLESCREEN                                                             ;;
;;  Draws the title screen and waits for user input.                        ;;
;; ======================================================================== ;;
TITLESCREEN;PROC
;           PSHR    R5

            CALL    CLRSCR
            CALL    LOADFONT
            DECLE   JOEFNT

            ; Set up the title screen;
            CALL    INITMEM.0
            INIT    FDROP,  0
            INIT    EBSY,   1
            INIT    RPTR,   LMPTITLE
            INIT    GDATA,  $3E
            INIT    MPTR,   TOPMOUNT
            INIT    MGRAM,  TOPGR
            INIT    MIDMSK, $3FFF
            INIT    MOBHIT, 1
            INIT    DNENG,  0
            INIT    INCITY, 0
            INIT    EMODE,  2
            INIT_DONE


            MVI     COURSE, R0
            ANDI    #7,     R0
            ADDI    #8,     R0
            MVO     R0,     COURSE

            CMPI    #14,    R0
            MVII    #C_TAN, R1
            BLT     @@tmclr_ok
            CLRR    R1
@@tmclr_ok  MVO     R1,     TMCLR

            CALL    SFXINIT
            CALL    INITLVL
            CALL    DRAWGAME

            SETISR  ENGINE1

            CALL    INITMEM.0
            INIT    GRATE,  VMED
            INIT    WANTVL, VMED
;           INIT    SKIPRC, 1
            INIT    EBSY,   0
            INIT    DOSCO,  0
            INIT    TMADDR, 0
            INIT    SDAT+7, $FC
            INIT    TMP,    $FC
            INIT_DONE

            ; Put up the title string.
            CALL    P16.FLS
            DECLE   gen_cstk_card(0, GRAM, Blue, NoAdvance)
            DECLE   disp_ptr(11, 3)
;           STRING  "   : 2007 !", $22, "#$%&'   ", 0
            S16     ": 2007 !\"#$%&'"

           ;B       TITLESCREEN_RET

           ;ENDP
