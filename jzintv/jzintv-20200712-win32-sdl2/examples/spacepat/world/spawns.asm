;; ------------------------------------------------------------------------ ;;
;;  SPAWN cue, last, type, bgmp, exitmp, exittag, xpos, ypos                ;;
;; ------------------------------------------------------------------------ ;;
MACRO   SPAWN   c, e, t, b, eb, et, xp, yp
CUE.%c% EQU     (($ - SPAWNTBL) / 4) SHL 8
        DECLE   (%e% SHL 15) + (%b% SHL 8) + (EXIT.%et% SHR 5) + (%eb%)
        DECLE   @@%t%
        DECLE   $0000
        DECLE   (%yp% SHL 8) + %xp%
ENDM

;; ------------------------------------------------------------------------ ;;
;;  SPAWNX cue, last, type, bgmp, exitmp, exittag, xpos, ypos, stat0, stat1 ;;
;; ------------------------------------------------------------------------ ;;
MACRO   SPAWNX  c, e, t, b, eb, et, xp, yp, s0, s1
CUE.%c% EQU     (($ - SPAWNTBL) / 4) SHL 8
        DECLE   (%e% SHL 15) + (%b% SHL 8) + (EXIT.%et% SHR 5) + (%eb%)
        DECLE   @@%t%
        DECLE   (%s1% SHL 8) + %s0%
        DECLE   (%yp% SHL 8) + %xp%
ENDM

;; ------------------------------------------------------------------------ ;;
;;  BGTAG tag, value                                                        ;;
;; ------------------------------------------------------------------------ ;;
MACRO   BGTAG t, v
SPAWNTBL.%t% EQU    %v%
ENDM

;; ------------------------------------------------------------------------ ;;
;;  EXITTAG tag, value                                                      ;;
;; ------------------------------------------------------------------------ ;;
MACRO   EXITTAG t, v
EXIT.%t% EQU    ((%v%) SHL 8)
ENDM


;; ------------------------------------------------------------------------ ;;
;;  Bad Guy Tag defs.  Must be unique.  8 and up scroll w/the screen.       ;;
;; ------------------------------------------------------------------------ ;;
BGTAG   pnk     ,   0
BGTAG   blu     ,   1
BGTAG   wht     ,   2
BGTAG   fola    ,   3
BGTAG   folb    ,   4
BGTAG   pn2     ,   5
BGTAG   bl2     ,   6
BGTAG   wh2     ,   7
BGTAG   tur     ,   8
BGTAG   bld     ,   9
BGTAG   mine    ,   10
BGTAG   plant   ,   11
BGTAG   plbig   ,   12
BGTAG   stal    ,   13
BGTAG   crat6   ,   13

;; ------------------------------------------------------------------------ ;;
;;  EXIT TAG definitions.  The same value can be given to more than one.    ;;
;; ------------------------------------------------------------------------ ;;
EXITTAG 0,      0       ; no exit tag
EXITTAG pink_a, 1
EXITTAG blue_a, 2
EXITTAG whit_a, 3
EXITTAG pin2_a, 4
EXITTAG blu2_a, 5
EXITTAG whi2_a, 6

EXITTAG pink_b, 7
EXITTAG blue_b, 8
EXITTAG whit_b, 9
EXITTAG pin2_b, 10
EXITTAG blu2_b, 11
EXITTAG whi2_b, 12

EXITTAG pink_c, 13
EXITTAG blue_c, 14
EXITTAG whit_c, 15
EXITTAG pin2_c, 16
EXITTAG blu2_c, 17
EXITTAG whi2_c, 18

EXITTAG pink_d, 19
EXITTAG blue_d, 20
EXITTAG whit_d, 21
EXITTAG pin2_d, 22
EXITTAG blu2_d, 23
EXITTAG whi2_d, 24

EXITTAG pink_e, 25
EXITTAG blue_e, 26
EXITTAG whit_e, 27
EXITTAG pin2_e, 28
EXITTAG blu2_e, 29
EXITTAG whi2_e, 30

EXITTAG flexit, 31

;; ------------------------------------------------------------------------ ;;
;;  SPAWNTBL:  Where all the spawns live!                                   ;;
;; ------------------------------------------------------------------------ ;;
SPAWNTBL    PROC

; two mines right next to each other, lo/hi
SPAWN 2_mine_a, 0, mine, BGI.mine0, 0, 0, $A8, $49 ; two mines, lo/hi
SPAWN 1_mine_a, 1, mine, BGI.mine0, 0, 0, $A0, $4A ; one mine, hi

; two mines, about 40 pixels apart, hi/lo
SPAWN 2_mine_b, 0, mine, BGI.mine0, 0, 0, $AB, $4A ; two mines, hi/lo
SPAWN 1_mine_b, 1, mine, BGI.mine0, 0, 0, $A0, $49 ; one mine, lo

; two mines, about 45 pixels apart, lo/hi
SPAWN 2_mine_c, 0, mine, BGI.mine0, 0, 0, $AE, $49 ; two mines, lo/hi
SPAWN 1_mine_c, 1, mine, BGI.mine0, 0, 0, $A0, $4A ; one mine, hi

; two mines, about 45 pixels apart, lo/hi
SPAWN 2_mine_d, 0, mine, BGI.mine0, 0, 0, $A6, $4A ; two mines, hi/lo
SPAWN 1_mine_d, 1, mine, BGI.mine0, 0, 0, $A0, $49 ; one mine, lo

; two mines, about 45 pixels apart, lo/hi
SPAWN 2_mine_e, 0, mine, BGI.mine0, 0, 0, $A5, $49 ; two mines, lo/hi
SPAWN 1_mine_e, 1, mine, BGI.mine0, 0, 0, $A0, $4A ; one mine, hi

; two mines, about 45 pixels apart, lo/hi
SPAWN 2_mine_f, 0, mine, BGI.mine0, 0, 0, $A9, $49 ; two mines, lo/lo
SPAWN 1_mine_f, 1, mine, BGI.mine0, 0, 0, $A0, $49 ; one mine, hi


; Plants and boulders
SPAWN 1_plant,  1, plant, BGI.plant0, 0, 0, $AE, $4C ; one plant, lo
SPAWN 1_plbig,  1, plbig, BGI.plant0, 0, 0, $B6, $4E ; one plant, lo

SPAWN 1_turret, 1, tur, BGI.turret0,  0, 0, $A4, $47 ; One gun turret

; boulders are close to each other
SPAWN 2_boulc,  0, bld, BGI.boulder0, 0, 0, $B2, $46 ; Two boulders
SPAWN 1_boulc,  1, bld, BGI.boulder0, 0, 0, $A8, $46 ; One boulder

; boulders are spaced as the arcade
SPAWN 2_bould,  0, bld, BGI.boulder0, 0, 0, $B8, $46 ; Two boulders
SPAWN 1_bould,  1, bld, BGI.boulder0, 0, 0, $A8, $46 ; One boulder

; Saucers!

;     A "0" will use the                 FLIGHT             (see bg/saucer.sct)
;     next saucer 1 ends       XPOS YPOS  PROG  LEAVE ZERO

;                              xpos = 00 to A0h
;                              ypos = 01 to 25h (max is 60h)


SPAWNX 3_pink_a, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_a, $11, $15, $07, $00
SPAWNX 2_pink_a, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_a, $71, $05, $05, $00
SPAWNX 1_pink_a, 1, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_a, $A0, $20, $00, $00

SPAWNX 3_pink_b, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_b, $89, $06, $01, $00
SPAWNX 2_pink_b, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_b, $35, $07, $06, $00
SPAWNX 1_pink_b, 1, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_b, $16, $05, $05, $00

SPAWNX 3_pink_c, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_c, $73, $04, $02, $00
SPAWNX 2_pink_c, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_c, $91, $06, $04, $00
SPAWNX 1_pink_c, 1, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_c, $41, $05, $03, $00

SPAWNX 2_pink_d, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_d, $54, $06, $00, $00
SPAWNX 1_pink_d, 1, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_d, $88, $04, $03, $00

SPAWNX 3_pink_e, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_e, $95, $04, $02, $00
SPAWNX 2_pink_e, 0, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_e, $04, $15, $01, $00
SPAWNX 1_pink_e, 1, pnk, BGI.sauc_lr, BGI.sauc_ex, pink_e, $61, $05, $04, $00

;

SPAWNX 3_pin2_a, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_a, $09, $13, $00, $00
SPAWNX 2_pin2_a, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_a, $75, $06, $06, $00
SPAWNX 1_pin2_a, 1, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_a, $A0, $18, $05, $00

SPAWNX 2_pin2_b, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_b, $39, $06, $01, $00
SPAWNX 1_pin2_b, 1, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_b, $27, $04, $02, $00

SPAWNX 3_pin2_c, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_c, $72, $05, $04, $00
SPAWNX 2_pin2_c, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_c, $97, $04, $07, $00
SPAWNX 1_pin2_c, 1, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_c, $30, $06, $03, $00

SPAWNX 3_pin2_d, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_d, $32, $04, $07, $00
SPAWNX 2_pin2_d, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_d, $56, $05, $05, $00
SPAWNX 1_pin2_d, 1, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_d, $94, $06, $03, $00

SPAWNX 2_pin2_e, 0, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_e, $04, $13, $02, $00
SPAWNX 1_pin2_e, 1, pn2, BGI.sauc_lr, BGI.sauc_ex, pin2_e, $63, $06, $04, $00

;----------------------------------------------------------------------------

SPAWNX 2_blue_a, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_a, $A0, $1A, $01, $00
SPAWNX 1_blue_a, 1, blu, BGI.sauc_lr, BGI.sauc_ex, blue_a, $52, $04, $00, $00

SPAWNX 3_blue_b, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_b, $58, $06, $04, $00
SPAWNX 2_blue_b, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_b, $96, $04, $03, $00
SPAWNX 1_blue_b, 1, blu, BGI.sauc_lr, BGI.sauc_ex, blue_b, $33, $05, $01, $00

SPAWNX 3_blue_c, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_c, $14, $04, $05, $00
SPAWNX 2_blue_c, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_c, $83, $05, $07, $00
SPAWNX 1_blue_c, 1, blu, BGI.sauc_lr, BGI.sauc_ex, blue_c, $A0, $15, $02, $00

SPAWNX 3_blue_d, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_d, $04, $1E, $06, $00
SPAWNX 2_blue_d, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_d, $38, $05, $04, $00
SPAWNX 1_blue_d, 1, blu, BGI.sauc_lr, BGI.sauc_ex, blue_d, $77, $04, $03, $00

SPAWNX 3_blue_e, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_e, $31, $04, $02, $00
SPAWNX 2_blue_e, 0, blu, BGI.sauc_lr, BGI.sauc_ex, blue_e, $69, $05, $05, $00
SPAWNX 1_blue_e, 1, blu, BGI.sauc_lr, BGI.sauc_ex, blue_e, $12, $09, $00, $00

;

SPAWNX 2_blu2_a, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_a, $A0, $1C, $07, $00
SPAWNX 1_blu2_a, 1, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_a, $46, $04, $00, $00

SPAWNX 3_blu2_b, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_b, $98, $06, $02, $00
SPAWNX 2_blu2_b, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_b, $47, $04, $05, $00
SPAWNX 1_blu2_b, 1, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_b, $24, $05, $03, $00

SPAWNX 3_blu2_c, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_c, $13, $05, $06, $00
SPAWNX 2_blu2_c, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_c, $84, $04, $03, $00
SPAWNX 1_blu2_c, 1, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_c, $A0, $17, $02, $00

SPAWNX 3_blu2_d, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_d, $04, $1C, $04, $00
SPAWNX 2_blu2_d, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_d, $42, $04, $01, $00
SPAWNX 1_blu2_d, 1, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_d, $74, $05, $00, $00

SPAWNX 3_blu2_e, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_e, $34, $05, $04, $00
SPAWNX 2_blu2_e, 0, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_e, $68, $04, $05, $00
SPAWNX 1_blu2_e, 1, bl2, BGI.sauc_lr, BGI.sauc_ex, blu2_e, $07, $0F, $01, $00

;----------------------------------------------------------------------------

SPAWNX 3_whit_a, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_a, $15, $16, $07, $00
SPAWNX 2_whit_a, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_a, $A0, $23, $05, $00
SPAWNX 1_whit_a, 1, wht, BGI.sauc_lr, BGI.sauc_ex, whit_a, $50, $05, $03, $00

SPAWNX 3_whit_b, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_b, $85, $04, $06, $00
SPAWNX 2_whit_b, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_b, $A0, $25, $01, $00
SPAWNX 1_whit_b, 1, wht, BGI.sauc_lr, BGI.sauc_ex, whit_b, $36, $05, $03, $00

SPAWNX 3_whit_c, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_c, $90, $04, $07, $00
SPAWNX 2_whit_c, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_c, $40, $06, $02, $00
SPAWNX 1_whit_c, 1, wht, BGI.sauc_lr, BGI.sauc_ex, whit_c, $70, $05, $00, $00

SPAWNX 3_whit_d, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_d, $76, $04, $06, $00
SPAWNX 2_whit_d, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_d, $45, $05, $04, $00
SPAWNX 1_whit_d, 1, wht, BGI.sauc_lr, BGI.sauc_ex, whit_d, $08, $15, $01, $00

SPAWNX 3_whit_e, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_e, $04, $17, $00, $00
SPAWNX 2_whit_e, 0, wht, BGI.sauc_lr, BGI.sauc_ex, whit_e, $20, $05, $04, $00
SPAWNX 1_whit_e, 1, wht, BGI.sauc_lr, BGI.sauc_ex, whit_e, $60, $04, $02, $00

;

SPAWNX 3_whi2_a, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_a, $10, $14, $01, $00
SPAWNX 2_whi2_a, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_a, $A0, $16, $05, $00
SPAWNX 1_whi2_a, 1, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_a, $57, $04, $03, $00

SPAWNX 3_whi2_b, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_b, $92, $04, $04, $00
SPAWNX 2_whi2_b, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_b, $A0, $22, $01, $00
SPAWNX 1_whi2_b, 1, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_b, $44, $05, $05, $00

SPAWNX 3_whi2_c, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_c, $93, $05, $07, $00
SPAWNX 2_whi2_c, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_c, $28, $04, $02, $00
SPAWNX 1_whi2_c, 1, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_c, $67, $06, $00, $00

SPAWNX 3_whi2_d, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_d, $62, $06, $00, $00
SPAWNX 2_whi2_d, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_d, $43, $04, $02, $00
SPAWNX 1_whi2_d, 1, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_d, $06, $17, $04, $00

SPAWNX 2_whi2_e, 0, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_e, $26, $06, $06, $00
SPAWNX 1_whi2_e, 1, wh2, BGI.sauc_lr, BGI.sauc_ex, whi2_e, $64, $05, $03, $00

;----------------------------------------------------------------------------

;; Follower
SPAWN follower, 0, fola, BGI.follow0, BGI.flexit,  flexit, $9,  $47  ; Body of follower
SPAWN _followr, 1, folb, BGI.null,    BGI.null,    0,      $9,  $47  ; decoration on follower

;; Mine-laying follower:  Lays 2 mines.
SPAWN  minelyr2, 0, fola, BGI.follow0, BGI.flexit,  flexit, $9,  $47
SPAWNX _minlyr2, 1, folb, BGI.null,    BGI.null,    0,      $9,  $47, 2, 0

;; Mine-laying follower:  Lays 5 mines.
SPAWN  minelyr5, 0, fola, BGI.follow0, BGI.flexit,  flexit, $9,  $47
SPAWNX _minlyr5, 1, folb, BGI.null,    BGI.null,    0,      $9,  $47, 5, 0

;; Land-mine left by mine-laying follower
SPAWN laidmine, 1, mine, BGI.mine0, 0, 0, $00, $49

;; Charger:  Reverse-flying follower
SPAWN  charger,  0, fola, BGI.follow0, BGI.fladv,   flexit, $A8, $47
SPAWNX _chargr,  1, folb, BGI.null,    BGI.null,    0,      $A8, $47, 3, 0

;; Charger:  Reverse-flying follower
SPAWN  charger5,  0, fola, BGI.follow0, BGI.fladv,   flexit, $A8, $47
SPAWNX _chargr5,  1, folb, BGI.null,    BGI.null,    0,      $A8, $47, 5, 0

;; Charger:  Reverse-flying follower
SPAWN  charger7,  0, fola, BGI.follow0, BGI.fladv,   flexit, $A8, $47
SPAWNX _chargr7,  1, folb, BGI.null,    BGI.null,    0,      $A8, $47, 7, 0

;; Stalactites
SPAWNX stal_a,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $29, $00  ; will hit the tank at slow speed
SPAWNX stal_b,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $38, $00  ; will hit the tank at slow speed

SPAWNX stal_c,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $47, $00  ; will hit the tank at standard speed
SPAWNX stal_d,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $56, $00  ; will hit the tank at standard speed

SPAWNX stal_e,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $65, $00  ; will hit the tank at full speed
SPAWNX stal_f,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $76, $00  ; you must slow down if you are going full speed

SPAWNX stal_g,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $84, $00
SPAWNX stal_h,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $94, $00
SPAWNX stal_i,  1, stal, BGI.stal0,   BGI.null,    0,      $A8, 4,   $A7, $00

;----------------------------------------------------------------------------
SPAWN  crat6,   1, crat6,BGI.null,    BGI.null,    0,      $A9, $50


 ENDP
