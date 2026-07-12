;;==========================================================================;;
;;  DATA for title screen sprites                                           ;;
;;==========================================================================;;
LMPFONT PROC
;; Skipped 32 indices.
;; Encoding span of 12 entries
        DECLE   $0061

LMPTITLE
;; Character #32, GRAM character index 0
        DECLE   $1C07  ;.....###
;       - - -          ;...###..
        DECLE   $0F1C  ;...###..
;       - - -          ;....####
        DECLE   $0103  ;......##
;       - - -          ;.......#
        DECLE   $0701  ;.......#
;       - - -          ;.....###

;; Character #33, GRAM character index 1
        DECLE   $FF1E  ;...####.
;       - - -          ;########
        DECLE   $1C00  ;........
;       - - -          ;...###..
        DECLE   $381F  ;...#####
;       - - -          ;..###...
        DECLE   $7038  ;..###...
;       - - -          ;.###....

;; Character #34, GRAM character index 2
        DECLE   $00C0  ;##......
;       - - -          ;........
        DECLE   $003F  ;..######
;       - - -          ;........
        DECLE   $CCCF  ;##..####
;       - - -          ;##..##..
        DECLE   $98D8  ;##.##...
;       - - -          ;#..##...

;; Character #35, GRAM character index 3
        DECLE   $C000  ;........
;       - - -          ;##......
        DECLE   $DE60  ;.##.....
;       - - -          ;##.####.
        DECLE   $7EB6  ;#.##.##.
;       - - -          ;.######.
        DECLE   $6666  ;.##..##.
;       - - -          ;.##..##.

;; Character #36, GRAM character index 4
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $863C  ;..####..
;       - - -          ;#....##.
        DECLE   $46BE  ;#.#####.
;       - - -          ;.#...##.
        DECLE   $7A4C  ;.#..##..
;       - - -          ;.####.#.

;; Character #37, GRAM character index 5
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $FF00  ;........
;       - - -          ;########
        DECLE   $3330  ;..##....
;       - - -          ;..##..##
        DECLE   $6666  ;.##..##.
;       - - -          ;.##..##.

;; Character #38, GRAM character index 6
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $601E  ;...####.
;       - - -          ;.##.....
        DECLE   $C160  ;.##.....
;       - - -          ;##.....#
        DECLE   $78C1  ;##.....#
;       - - -          ;.####...

;; Character #39, GRAM character index 7
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $E300  ;........
;       - - -          ;###...##
        DECLE   $CC66  ;.##..##.
;       - - -          ;##..##..
        DECLE   $676C  ;.##.##..
;       - - -          ;.##..###

;; Character #40, GRAM character index 8
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $C878  ;.####...
;       - - -          ;##..#...
        DECLE   $80F0  ;####....
;       - - -          ;#.......
        DECLE   $E080  ;#.......
;       - - -          ;###.....

;; Character #41, GRAM character index 9
        DECLE   $0000  ;........
;       - - -          ;........
        DECLE   $8C00  ;........
;       - - -          ;#...##..
        DECLE   $D8CC  ;##..##..
;       - - -          ;##.##...
        DECLE   $9ED8  ;##.##...
;       - - -          ;#..####.

;; Character #42, GRAM character index 10
;; Character #43, GRAM character index 11
        REPEAT  8
        DECLE   $BA5D  ;.#.###.#
;       - - -          ;#.###.#.
        ENDR


;; End of font.
        DECLE   $0000

;; Total chars:          12 characters
;; Total length:         50 decles
;; Decles/char:       4.167 decles/character
        ENDP


;;==========================================================================;;
;;  DATA for title screen sprites                                           ;;
;;==========================================================================;;
TITLESP PROC
@@x     EQU 54 + 16 - 22
@@y     EQU 20
        ; X coordinates
 IF 0
        DECLE   @@x + 0   + _X.visb
        DECLE   @@x + 8   + _X.visb
        DECLE   @@x + 16  + _X.visb
        DECLE   @@x + 24  + _X.visb
        DECLE   @@x + 32  + _X.visb
 ELSE
        DECLE   @@x + 0   + _X.xsiz + _X.visb
        DECLE   @@x + 16  + _X.xsiz + _X.visb
        DECLE   @@x + 32  + _X.xsiz + _X.visb
        DECLE   @@x + 48  + _X.xsiz + _X.visb
        DECLE   @@x + 64  + _X.xsiz + _X.visb
 ENDI

        ; Y coordinates
        DECLE   @@y      + _Y.siz4 + _Y.yres
        DECLE   @@y      + _Y.siz4 + _Y.yres
        DECLE   @@y      + _Y.siz4 + _Y.yres
        DECLE   @@y      + _Y.siz4 + _Y.yres
        DECLE   @@y      + _Y.siz4 + _Y.yres

        ; Attributes
        DECLE   LMPCARDx + 0*8 
        DECLE   LMPCARDx + 2*8 
        DECLE   LMPCARDx + 4*8
        DECLE   LMPCARDx + 6*8
        DECLE   LMPCARDx + 8*8

        ENDP

;;==========================================================================;;
;;  TITLE MESSAGE TABLE                                                     ;;
;;==========================================================================;;
TMTBL   PROC
        DECLE   @@m0, @@m1, @@m2, @@m3
        DECLE   @@m0, @@m1, @@m2, @@m3
        DECLE   @@m4, @@m5, @@m6, @@m7
        DECLE   0

                ;01234567890123456789
@@m0    S16B    "   >> SDK-1600 <<   "
@@m1    S16B    "      presents      "
@@m2    S16B    "a space action game "
@@m3    S16B    "   by Joe Zbiciak   "
@@m4    S16B    "      Credits:      "
@@m5    S16B    " Prog & Gfx:  Joe Z "
@@m6    S16B    " Levels:    David H "
@@m7    S16B    " Music:   Arnauld C "
        ENDP
