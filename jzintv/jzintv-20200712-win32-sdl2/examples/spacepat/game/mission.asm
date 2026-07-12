;; ======================================================================== ;;
;;  Mission Menu                                                            ;;
;; ======================================================================== ;;

FMTSEL      EQU     gen_fgbg_card(0, GROM, Yellow, Blue)
FMTUNS      EQU     gen_fgbg_card(0, GROM, Tan,    Black)

WORLDMENU   PROC
            SETISR  CKPTISR

            MVO     R0,         TMP

            CALL    HALTENGINE
            CALL    SFXINIT

            MVI     COURSE,     R2
@@again:    ANDI    #7,         R2
            MVO     R2,         COURSE

@@world:    SETISR  JRR5
            CALL    CLRSCR

            P16_FGBG  0, 3, White, Black, "SELECT MISSION"

            ;; ------------------------------------------------------------ ;;
            ;;  Print currently selected course name.                       ;;
            ;; ------------------------------------------------------------ ;;
            MVI     COURSE,     R5          
            ANDI    #$6,        R5
            CMPI    #6,         R5
            ADDI    #CNAME,     R5
            ADD     NN,         R5
            MVI@    R5,         R0      ; Get name of course
            MVI@    R5,         R1      ; Get position to print it
            MOVR    R1,         R4      ; \
            SWAP    R1                  ;  |_ Unpack color from upper nibble
            SLR     R1,         2       ;  |
            SLR     R1,         2       ;  |
            ANDI    #$F,        R1      ; /
            ANDI    #$FF,       R4      ; \_ unpack position from lower byte
            ADDI    #$200,      R4      ; /
            CALL    P16.R

            ;; ------------------------------------------------------------ ;;
            ;;  Load up graphics associated with selected world.            ;;
            ;; ------------------------------------------------------------ ;;
            CALL    LOADCRP             ; Load creeps associated with world

            MVII    #1,         R1      ; \
            MVI     COURSE,     R2      ;  |  Force to "INCITY", taking
            CMPI    #6,         R2      ;  |- into account that Mercury
            ADCR    R1                  ;  |  needs INCITY = 2.
            MVO     R1,         INCITY  ; /

            CALL    SETGFX              ; Load background GFX for this world

            SETISR  FIXGFX              ; Invert either top or middle GFX 
                                        ; because we are using FGBG mode.

            ;; ------------------------------------------------------------ ;;
            ;;  Draw a small sample of the selected world.  This lives in   ;;
            ;;  an 8 x 8 box on the left side of the display.               ;;
            ;; ------------------------------------------------------------ ;;
            MVI     COURSE,         R1   
            CMPI    #6,             R1
            BC      @@draw_merc

            SLR     R1,             1
            ADDI    #CITYMNU,       R1
            MVI@    R1,             R2  ; \_ R2 has card to draw in city
            ADDI    #gen_fgbg_card(CCARD + 7, GRAM, Black, Black), R2

            MVII    #disp_ptr(6,1), R4  ; \
            MVII    #disp_ptr(7,1), R5  ;  |_ Reuse DRAWGAME's code to
            MVII    #2,             R0  ;  |  draw the city 
            MVII    #@@draw_mntn,   R3  ; / 
            B       DRAWGAME.city_fill1
@@draw_mntn
            MVII    #gen_fgbg_card(TCARD + 7, GRAM, Black, Black), R2
            MVI     COURSE,         R1
            SLR     R1,             1
            ADDI    #MNTNMNU,       R1
            ADD@    R1,             R2
            MOVR    R2,             R1
   
            MVII    #disp_ptr(3,1), R4
            MVII    #disp_ptr(4,1), R5
            MVII    #2,             R0
            MVII    #@@finish_mntn, R3
            B       DRAWGAME.city_fill1
@@finish_mntn:
            SUBI    #4*8,           R1
            MOVR    R1,             R2
            MVII    #2,             R0
            MVII    #disp_ptr(5,1), R4
            MVII    #@@done_draw,   R5
            B       DRAWGAME.mntn_loop

@@draw_merc
            CALL    @@mntn_loop         ;
            DECLE   gen_fgbg_card(CCARD+2, GRAM, Green, YellowGreen)
            DECLE   disp_ptr(3,1)

            CALL    @@mntn_loop  ; 
            DECLE   gen_fgbg_card(CCARD+3, GRAM, Green, YellowGreen)
            DECLE   disp_ptr(9,1)

            MVII    #gen_fgbg_card(TCARD+7, GRAM, Green, DarkGreen), R2
            MVII    #disp_ptr(5,1), R4  ;  first 2 rows
            MVII    #disp_ptr(6,1), R5  ;  first 2 rows
            MVII    #@@a,           R3  ;
            MVII    #2,             R0
            B       DRAWGAME.city_fill1 ;  fill 2 rows of background rocks
@@a
            CALL    @@mntn_loop         ;  fill 1 row of background cards
            DECLE   gen_fgbg_card(TCARD+2, GRAM, Green, DarkGreen)
            DECLE   disp_ptr(7,1)       ;  3rd row

            CALL    @@mntn_loop         ;  fill 1 row of background cards
            DECLE   gen_fgbg_card(TCARD+3, GRAM, Green, DarkGreen)
            DECLE   disp_ptr(8,1)       ;  4th row

            CALL    @@mntn_loop         ;  fill 1 row of background cards
            DECLE   gen_fgbg_card(TCARD+3, GRAM, Green, DarkGreen)
            DECLE   disp_ptr(4,1)       ;  0th row

            CALL    FILLMEM.vlp
            DECLE   gen_fgbg_card(0, GROM, Black, YellowGreen)
            DECLE   8
            DECLE   disp_ptr(10,1)
            B       @@skip_ground

@@mntn_loop MVI@    R5,             R2
            MVI@    R5,             R4
            MVII    #2,             R0
            B       DRAWGAME.mntn_loop

@@done_draw:
            ;; ------------------------------------------------------------ ;;
            ;;  Draw the fixed portion of the scene that includes ground    ;;
            ;;  and the crater row.                                         ;;
            ;; ------------------------------------------------------------ ;;
            MVI     COURSE,         R5
            ANDI    #$6,            R5
            ADDI    #GROWMNU,       R5
            MVI@    R5,             R0
            MVI@    R5,             R1
            PSHR    R1
            CALL    FILLMEM.lp
            DECLE   8
            DECLE   disp_ptr(8,1)

            PULR    R0
;           MVII    #8,             R1
;           MVII    #disp_ptr(9,1), R4
            CALL    FILLMEM.lp
            DECLE   8
            DECLE   disp_ptr(9,1)

            CALL    FILLMEM.vlp
            DECLE   gen_fgbg_card(0, GROM, Black, Orange)
            DECLE   8
            DECLE   disp_ptr(10,1)

@@skip_ground:
            ;; ------------------------------------------------------------ ;;
            ;;  Now set up a little activity scene to give it some life.    ;;
            ;; ------------------------------------------------------------ ;;
            CALL    WAIT1

            MVI     COURSE,     R0      ; \
            ANDI    #6,         R0      ;  |
            MOVR    R0,         R1      ;  |
            SLL     R1,         2       ;  |- Pick MOB set as 18 * planet #
            SLL     R1,         1       ;  |
            ADDR    R1,         R0      ;  |
            ADDI    #VIGMOB,    R0      ; /

            MVO     R0,         SDAT
            SETISR  FIXMOB
            CALL    SHOW
                
            ;; ------------------------------------------------------------ ;;
            ;;  Display the top scores for this world.                      ;;
            ;; ------------------------------------------------------------ ;;
            MVI     COURSE,     R4
            ANDI    #6,         R4
            ADDR    R4,         R4
            ADDI    #TOPSCO,    R4
            SDBD
            MVI@    R4,         R0
            PSHR    R4
            CALL    DISPSCORE2
            DECLE   disp_ptr(7, 12)
            PULR    R4
            SDBD
            MVI@    R4,         R0
            CALL    DISPSCORE2
            DECLE   disp_ptr(10, 12)

            ;; ------------------------------------------------------------ ;;
            ;;  Display and highlight Beginner or Champion.                 ;;
            ;; ------------------------------------------------------------ ;;
@@skill:
            MVII    #FMTSEL,    R1
            MVII    #FMTUNS,    R2
            MVI     COURSE,     R0
            SARC    R0
            BNC     @@beginner
;           MVII    #FMTSEL,    R2
;           MVII    #FMTUNS,    R1
            XORR    R1,         R2
            XORR    R2,         R1
            XORR    R1,         R2
@@beginner
            PSHR    R2
            CALL    P16.LP
            DECLE   disp_ptr(6, 10), BEGINNER

            PULR    R1
            CALL    P16.LP
            DECLE   disp_ptr(9, 10), CHAMPION
            
            ;; ------------------------------------------------------------ ;;
            ;;  Ok, with that all set up, now wait for user input.          ;;
            ;;  Tap left/right to select world, up/down for beg/champ,      ;;
            ;;  action button or enter to accept.                           ;;
            ;; ------------------------------------------------------------ ;;
;           SETISR  MENUISR

;           MVI     TMP,        R0
;           TSTR    R0
;           BNEQ    @@notink
            CALL    TINK
@@notink:   CLRR    R0
            MVO     R0,         TMP
            MVO     R0,         TMP+1

            CALL    MENUINP
            BPL     @@leave

            MVI     COURSE,     R2
            MOVR    R2,         R3

            SARC    R0,         2
            BC      @@down
            BOV     @@right
            SARC    R0,         2
            BC      @@up
            BNOV    @@notink

@@left:     SUBI    #2,         R2
            B       @@again

@@right:    ADDI    #2,         R2
            B       @@again

@@down:     ANDI    #$6,        R2
            INCR    R2
            B       @@maybe

@@up:       ANDI    #$6,        R2
@@maybe     CMPR    R2,         R3
            BEQ     @@notink
            MVO     R2,         COURSE
            B       @@skill

@@leave:    CLRR    R0
            MVO     R0,         INCITY

            SETISR  SETCSG

            CALL    WAIT
            DECLE   1

            B       WORLDMENU_RET

            ENDP


;; ======================================================================== ;;
;;  FIXGFX  Invert either top or middle GFX based on course.                ;;
;; ======================================================================== ;;
FIXGFX      PROC
            DIS
            MVI     COURSE,     R0
            ANDI    #2,         R0
            MVII    #TOPGR,     R4
            BEQ     @@inv_mntn
            MVII    #MIDGR,     R4
@@inv_mntn: MOVR    R4,         R5

            MVII    #64,        R1
@@loop      MVI@    R4,         R0
            COMR    R0
            MVO@    R0,         R5
            DECR    R1
            BNEQ    @@loop

            MVI     COURSE,     R0
            CMPI    #6,         R0
            BLT     @@not_merc

            MVII    #MIDGR+8,   R4
            MOVR    R4,         R5
            MVII    #32,        R1
            MVII    #8,         R2
@@loopm:    MVI@    R4,         R0
            COMR    R0
            MVO@    R0,         R5
            DECR    R2
            BNEQ    @@n
            MVII    #8,         R2
            ADDR    R2,         R4
            ADDR    R2,         R5
@@n         DECR    R1
            BNEQ    @@loopm

            MVII    #$3000 + $92*8, R4
            MVII    #$3800,     R5
@@copy      MVI@    R4,         R0
            MVO@    R0,         R5
            CMPI    #$3808,     R5
            BNEQ    @@copy

@@not_merc
            MVII    #GGRAM,     R4
            MOVR    R4,         R5
            MVII    #8,         R1
@@loop2     MVI@    R4,         R0
            COMR    R0
            MVO@    R0,         R5
            DECR    R1
            BNEQ    @@loop2


            MVII    #32,        R1
            MVII    #$3978,     R4
            MVII    #HUT+12,    R5
@@hloop:    MVI@    R5,         R0
            MVO@    R0,         R4
            SWAP    R0
            MVO@    R0,         R4
            DECR    R1
            BNEQ    @@hloop

            EIS
            SETISR  MISCISR.1
            B       MISCISR.wtimer

            ENDP

;; ======================================================================== ;;
;;  MENUISR Really simple ISR once we arrive at menu.                       ;;
;; ======================================================================== ;;
MENUISR     PROC
            MVO     R0,     $21
            B       MISCISR
            ENDP


;; ======================================================================== ;;
;;  xxxxMNU Color schemes for mountain, city and ground row while in menu   ;;
;; ======================================================================== ;;
MNTNMNU     PROC
            DECLE   gen_fgbg_card(0, GROM, Black,  Cyan)        ; Invert mntn
            DECLE   gen_fgbg_card(0, GROM, Red,    Black)
            DECLE   gen_fgbg_card(0, GROM, Black,  YellowGreen) ; Invert mntn
            ENDP

CITYMNU     PROC
            DECLE   gen_fgbg_card(0, GROM, Yellow, Cyan)
            DECLE   gen_fgbg_card(0, GROM, Red,    Tan)         ; Invert city
            DECLE   gen_fgbg_card(0, GROM, Yellow, YellowGreen)
            ENDP

GROWMNU     PROC
            DECLE   gen_fgbg_card(0,     GROM, Black,  Yellow)
            DECLE   gen_fgbg_card(GCARD, GRAM, Yellow, Orange)

            DECLE   gen_fgbg_card(0,     GROM, Black,  Tan   )
            DECLE   gen_fgbg_card(GCARD, GRAM, Tan,    Orange)

            DECLE   gen_fgbg_card(0,     GROM, Black,  Yellow)
            DECLE   gen_fgbg_card(GCARD, GRAM, Yellow, Orange)
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
;;  SPREC:  Modified SPENT (see gfx/mobattr.asm) used for setting up the    ;;
;;          vignettes that adorn the mission control screen                 ;;
;; ======================================================================== ;;
MACRO SPREC lbl,xsiz,xofs,yres,ysiz,xmir,ymir,yofs,color,card
@@%lbl%0:   SET _X.visb + _X.%xsiz% + (%xofs%)
@@%lbl%1:   SET _Y.%yres% + _Y.%ysiz% + _Y.%ymir% + _Y.%xmir% + (%yofs%)
@@%lbl%2:   SET %color% + 8*%card%
ENDM

MACRO SPEMIT a,b,c,d,e,f

            DECLE @@%a%0, @@%b%0, @@%c%0, @@%d%0, @@%e%0, @@%f%0
            DECLE @@%a%1, @@%b%1, @@%c%1, @@%d%1, @@%e%1, @@%f%1
            DECLE @@%a%2, @@%b%2, @@%c%2, @@%d%2, @@%e%2, @@%f%2
ENDM


;; ======================================================================== ;;
;;  VIGMOB  MOB programming for the vignettes                               ;;
;; ======================================================================== ;;
VIGMOB      PROC
@@moon:

SPREC a,    xsiz,20, na  ,siz2,na  ,na  ,48, X_PNK, $121    ; pink 
SPREC b,    xsiz,40, na  ,siz1,na  ,na  ,33, X_BLU, $122    ; blue
SPREC c,    xsiz,50, na  ,siz2,na  ,na  ,43, X_PNK, $121    ; blue
SPREC d,    na  ,20, na  ,siz2,na  ,na  ,58, X_WHT, $126    ; bullet
SPREC e,    na  ,45, na  ,siz2,na  ,na  ,63, X_WHT, $126    ; bullet
SPREC f,    na  ,55, na  ,siz2,na  ,na  ,48, X_WHT, $126    ; bullet
SPEMIT a,b,c,d,e,f

@@mars:
SPREC a,    xsiz,40, na  ,siz2,na  ,na  ,29, X_GRY, $123    ; spinner
SPREC b,    na  ,65, na  ,siz2,na  ,na  ,73, X_GRN, $120    ; turret
SPREC c,    na  ,55, na  ,siz2,na  ,na  ,43, X_WHT, $124    ; spinner bullet
SPREC d,    na  ,47, na  ,na  ,na  ,na  ,74, X_BLK, $00D    ; turret bullet
SPREC e,    xsiz,20, na  ,siz1,na  ,na  ,43, X_YGR, $11A    ; saucer
SPREC f,    na  ,23, na  ,siz2,na  ,na  ,70, X_WHT, $126    ; saucer bullet
SPEMIT a,b,c,d,e,f

@@pluto:
SPREC a,    na  ,22, na  ,siz1,na  ,na  ,30, X_PUR, $121    ; 
SPREC b,    na  ,63, na  ,siz1,xmir,na  ,48, X_RED, $11A    ; 
SPREC c,    xsiz,33, na  ,siz2,na  ,na  ,75, X_WHT, $00E    ; mine
SPREC d,    xsiz,49, na  ,siz2,na  ,na  ,74, X_RED, $00E    ; mine
SPREC e,    na  ,20, na  ,siz2,na  ,na  ,48, X_WHT, $126    ; saucer bullet
SPREC f,    na  ,60, na  ,siz2,na  ,na  ,60, X_WHT, $126    ; saucer bullet
SPEMIT a,b,c,d,e,f

@@mercury:
SPREC a,    na  ,50, na  ,siz1,na  ,na  ,48, X_CYN, $123
SPREC b,    na  ,25, na  ,siz1,na  ,na  ,38, X_ORG, $121
SPREC c,    na  ,65, na  ,siz2,na  ,na  ,63, X_WHT, $124    ; spinner bullet
SPREC d,    na  ,34, na  ,siz2,na  ,na  ,53, X_DGR, $100
SPREC e,    na  ,42, na  ,siz2,na  ,na  ,63, X_DGR, $100
SPREC f,    na  ,58, na  ,siz2,na  ,na  ,38, X_DGR, $100
SPEMIT a,b,c,d,e,f
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
