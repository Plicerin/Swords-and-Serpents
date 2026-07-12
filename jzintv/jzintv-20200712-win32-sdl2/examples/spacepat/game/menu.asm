;; Real simple for-debugging-purposes only menu

FMTSEL      EQU     gen_fgbg_card(0, GROM, Yellow, Blue)
FMTUNS      EQU     gen_fgbg_card(0, GROM, Tan,    Black)

    IF (DEFINED JUMPWORLD) <> 0
WORLDMENU   PROC
            MVII    #JUMPWORLD, R0
            MVO     R0,         COURSE
            CLRR    R0
            MVO     R0,         INCITY
            JR      R5
            ENDP
    ELSE

WORLDMENU   PROC
            PSHR    R5

            MVII    #CKPTISR,   R0
            MVOD    R0,         $100
            CALL    HALTENGINE
            CALL    SFXINIT

@@world:    CALL    CLRSCR

            P16_CSTK  0, 5, White, "World Menu"
                                    ; 01234567890123456789
            P16_CSTK  3, 1, Yellow,"       Begin Champ"
            P16_CSTK  4, 1, Blue,  "Moon     1     2"
            P16_CSTK  5, 1, Red,   "Mars     3     4"
            P16_CSTK  6, 1, Green, "Pluto    5     6"
            P16_CSTK  7, 1, Tan,   "Mercury  7     8"

            P16_CSTK 10, 0, White, "Select keypad button"
            P16_CSTK 11, 0, White, "for desired world."

            CALL    GETKEY
            DECR    R2
            ANDI    #7,     R2
            MVO     R2,     COURSE

            CLRR    R0
            MVO     R0,     INCITY

            PULR    PC

            ENDP

;; ======================================================================== ;;
;;  FIXMOB  Copy over a slate of MOBs for the menu                          ;;
;; ======================================================================== ;;
FIXMOB      PROC
            MVI     SDAT,       R4
            CLRR    R5

            MVII    #3,         R2
@@oloop
            MVII    #6,         R1
@@loop      MVI@    R4,         R0
            MVO@    R0,         R5
            DECR    R1
            BNEQ    @@loop
            ADDI    #2,         R5
            DECR    R2
            BNEQ    @@oloop

            SETISR  MENUISR
            B       MENUISR
            ENDP

;; ======================================================================== ;;
;;  MENUISR Really simple ISR once we arrive at menu.                       ;;
;; ======================================================================== ;;
MENUISR     PROC
            MVO     R0,     $20
            MVO     R0,     $21

@@timer:    MVI     WTIMER,     R0
            DECR    R0
            BMI     @@nuts
            MVO     R0,         WTIMER
@@nuts:
            B       $1014
            ENDP


;; ======================================================================== ;;
;;  TINK    This should sound familiar                                      ;;
;; ======================================================================== ;;
TINK        PROC
            MVII    #@@tbl, R4
            B       INITMEM.2

@@tbl:      INIT    $1F0,   $18
            INIT    $1F4,   $00
            INIT    $1F3,   $80
            INIT    $1F7,   $00
            INIT    $1FB,   $3F
            INIT    $1FA,   $00
            INIT_DONE
            ENDP


;; Temporary function until menu rewrite
GETKEY      PROC

@@wnk:
            MVI     $1FE,   R0
            AND     $1FF,   R0
            XORI    #$FF,   R0
            BNEQ    @@wnk

@@wk:       MVI     $1FE,   R0
            AND     $1FF,   R0
            XORI    #$FF,   R0
            BEQ     @@wk

            MVII    #@@pad, R4

@@decl:     CMP@    R4,     R0
            BEQ     @@gotkey
            CMPI    #@@pade,R4
            BNEQ    @@decl
            B       @@wk

@@gotkey    SUBI    #@@pade,R4
            NEGR    R4
            MOVR    R4,     R2

            JR      R5
            ;        E    C    9    8    7    6    5    4    3    2    1    0
@@pad:      BYTE    $28, $88, $24, $44, $84, $22, $42, $82, $21, $41, $81, $48
@@pade:
            ENDP

    ENDI    ; JUMPWORLD

