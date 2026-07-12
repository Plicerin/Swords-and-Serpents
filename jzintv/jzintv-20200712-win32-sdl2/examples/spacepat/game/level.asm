
    IF (DEFINED SEEKKEYS) <> 0
;; ======================================================================== ;;
;;  World Checkpoint Table (used only for PRV/RST/NXTLVL).                  ;;
;; ======================================================================== ;;
WCKPT       PROC

            DECLE   MOON_B.ckpt_0a, MOON_B.ckpt_0b, MOON_B.ckpt_0c
            DECLE   MOON_B.ckpt_0d, MOON_B.ckpt_0e, MOON_B.ckpt_0f
            DECLE   MOON_B.ckpt_0g, MOON_B.ckpt_0h, MOON_B.ckpt_0i
            DECLE   MOON_B.ckpt_0j, MOON_B.ckpt_0k, MOON_B.ckpt_0l
            DECLE   MOON_B.ckpt_0m, MOON_B.ckpt_0n, MOON_B.ckpt_0o
            DECLE   MOON_B.ckpt_0p, MOON_B.ckpt_0q, MOON_B.ckpt_0r
            DECLE   MOON_B.ckpt_0s, MOON_B.ckpt_0t, MOON_B.ckpt_0u
            DECLE   MOON_B.ckpt_0v, MOON_B.ckpt_0w, MOON_B.ckpt_0x
            DECLE   MOON_B.ckpt_0y, MOON_B.ckpt_0z

            DECLE   MOON_C.ckpt_0a, MOON_C.ckpt_0b, MOON_C.ckpt_0c
            DECLE   MOON_C.ckpt_0d, MOON_C.ckpt_0e, MOON_C.ckpt_0f
            DECLE   MOON_C.ckpt_0g, MOON_C.ckpt_0h, MOON_C.ckpt_0i
            DECLE   MOON_C.ckpt_0j, MOON_C.ckpt_0k, MOON_C.ckpt_0l
            DECLE   MOON_C.ckpt_0m, MOON_C.ckpt_0n, MOON_C.ckpt_0o
            DECLE   MOON_C.ckpt_0p, MOON_C.ckpt_0q, MOON_C.ckpt_0r
            DECLE   MOON_C.ckpt_0s, MOON_C.ckpt_0t, MOON_C.ckpt_0u
            DECLE   MOON_C.ckpt_0v, MOON_C.ckpt_0w, MOON_C.ckpt_0x
            DECLE   MOON_C.ckpt_0y, MOON_C.ckpt_0z

            DECLE   MARS_B.ckpt_0a, MARS_B.ckpt_0b, MARS_B.ckpt_0c
            DECLE   MARS_B.ckpt_0d, MARS_B.ckpt_0e, MARS_B.ckpt_0f
            DECLE   MARS_B.ckpt_0g, MARS_B.ckpt_0h, MARS_B.ckpt_0i
            DECLE   MARS_B.ckpt_0j, MARS_B.ckpt_0k, MARS_B.ckpt_0l
            DECLE   MARS_B.ckpt_0m, MARS_B.ckpt_0n, MARS_B.ckpt_0o
            DECLE   MARS_B.ckpt_0p, MARS_B.ckpt_0q, MARS_B.ckpt_0r
            DECLE   MARS_B.ckpt_0s, MARS_B.ckpt_0t, MARS_B.ckpt_0u
            DECLE   MARS_B.ckpt_0v, MARS_B.ckpt_0w, MARS_B.ckpt_0x
            DECLE   MARS_B.ckpt_0y, MARS_B.ckpt_0z

            DECLE   MARS_C.ckpt_0a, MARS_C.ckpt_0b, MARS_C.ckpt_0c
            DECLE   MARS_C.ckpt_0d, MARS_C.ckpt_0e, MARS_C.ckpt_0f
            DECLE   MARS_C.ckpt_0g, MARS_C.ckpt_0h, MARS_C.ckpt_0i
            DECLE   MARS_C.ckpt_0j, MARS_C.ckpt_0k, MARS_C.ckpt_0l
            DECLE   MARS_C.ckpt_0m, MARS_C.ckpt_0n, MARS_C.ckpt_0o
            DECLE   MARS_C.ckpt_0p, MARS_C.ckpt_0q, MARS_C.ckpt_0r
            DECLE   MARS_C.ckpt_0s, MARS_C.ckpt_0t, MARS_C.ckpt_0u
            DECLE   MARS_C.ckpt_0v, MARS_C.ckpt_0w, MARS_C.ckpt_0x
            DECLE   MARS_C.ckpt_0y, MARS_C.ckpt_0z

            DECLE   PLUT_B.ckpt_0a, PLUT_B.ckpt_0b, PLUT_B.ckpt_0c
            DECLE   PLUT_B.ckpt_0d, PLUT_B.ckpt_0e, PLUT_B.ckpt_0f
            DECLE   PLUT_B.ckpt_0g, PLUT_B.ckpt_0h, PLUT_B.ckpt_0i
            DECLE   PLUT_B.ckpt_0j, PLUT_B.ckpt_0k, PLUT_B.ckpt_0l
            DECLE   PLUT_B.ckpt_0m, PLUT_B.ckpt_0n, PLUT_B.ckpt_0o
            DECLE   PLUT_B.ckpt_0p, PLUT_B.ckpt_0q, PLUT_B.ckpt_0r
            DECLE   PLUT_B.ckpt_0s, PLUT_B.ckpt_0t, PLUT_B.ckpt_0u
            DECLE   PLUT_B.ckpt_0v, PLUT_B.ckpt_0w, PLUT_B.ckpt_0x
            DECLE   PLUT_B.ckpt_0y, PLUT_B.ckpt_0z

            DECLE   PLUT_C.ckpt_0a, PLUT_C.ckpt_0b, PLUT_C.ckpt_0c
            DECLE   PLUT_C.ckpt_0d, PLUT_C.ckpt_0e, PLUT_C.ckpt_0f
            DECLE   PLUT_C.ckpt_0g, PLUT_C.ckpt_0h, PLUT_C.ckpt_0i
            DECLE   PLUT_C.ckpt_0j, PLUT_C.ckpt_0k, PLUT_C.ckpt_0l
            DECLE   PLUT_C.ckpt_0m, PLUT_C.ckpt_0n, PLUT_C.ckpt_0o
            DECLE   PLUT_C.ckpt_0p, PLUT_C.ckpt_0q, PLUT_C.ckpt_0r
            DECLE   PLUT_C.ckpt_0s, PLUT_C.ckpt_0t, PLUT_C.ckpt_0u
            DECLE   PLUT_C.ckpt_0v, PLUT_C.ckpt_0w, PLUT_C.ckpt_0x
            DECLE   PLUT_C.ckpt_0y, PLUT_C.ckpt_0z

            DECLE   MERC_B.ckpt_0a, MERC_B.ckpt_0b, MERC_B.ckpt_0c
            DECLE   MERC_B.ckpt_0d, MERC_B.ckpt_0e, MERC_B.ckpt_0f
            DECLE   MERC_B.ckpt_0g, MERC_B.ckpt_0h, MERC_B.ckpt_0i
            DECLE   MERC_B.ckpt_0j, MERC_B.ckpt_0k, MERC_B.ckpt_0l
            DECLE   MERC_B.ckpt_0m, MERC_B.ckpt_0n, MERC_B.ckpt_0o
            DECLE   MERC_B.ckpt_0p, MERC_B.ckpt_0q, MERC_B.ckpt_0r
            DECLE   MERC_B.ckpt_0s, MERC_B.ckpt_0t, MERC_B.ckpt_0u
            DECLE   MERC_B.ckpt_0v, MERC_B.ckpt_0w, MERC_B.ckpt_0x
            DECLE   MERC_B.ckpt_0y, MERC_B.ckpt_0z

            DECLE   MERC_C.ckpt_0a, MERC_C.ckpt_0b, MERC_C.ckpt_0c
            DECLE   MERC_C.ckpt_0d, MERC_C.ckpt_0e, MERC_C.ckpt_0f
            DECLE   MERC_C.ckpt_0g, MERC_C.ckpt_0h, MERC_C.ckpt_0i
            DECLE   MERC_C.ckpt_0j, MERC_C.ckpt_0k, MERC_C.ckpt_0l
            DECLE   MERC_C.ckpt_0m, MERC_C.ckpt_0n, MERC_C.ckpt_0o
            DECLE   MERC_C.ckpt_0p, MERC_C.ckpt_0q, MERC_C.ckpt_0r
            DECLE   MERC_C.ckpt_0s, MERC_C.ckpt_0t, MERC_C.ckpt_0u
            DECLE   MERC_C.ckpt_0v, MERC_C.ckpt_0w, MERC_C.ckpt_0x
            DECLE   MERC_C.ckpt_0y, MERC_C.ckpt_0z

            ENDP

;; ======================================================================== ;;
;;  PRVLVL:  Restart the current level.                                     ;;
;; ======================================================================== ;;
PRVLVL      PROC
           
            MVI     POINT,  R0
            SUBI    #8,     R0
            BMI     RSTLVL
           
            MVO     R0,     POINT
            ; fallthru

;; ======================================================================== ;;
;;  RSTLVL:  Restart the current level.                                     ;;
;; ======================================================================== ;;
RSTLVL      PSHR    R5
            PSHR    R1

            CALL    INITLVL.1
            MVI     POINT,  R0
            
            MVII    #@@done_redraw, R5

            CMPI    #5*8,   R0
            BLT     TOCRATER.1
            CMPI    #10*8,  R0
            BLT     TOCITY.1
            CMPI    #15*8,  R0
            BLT     TOCRATER.1
            CMPI    #20*8,  R0
            BLT     TOCITY.1
            B       TOCRATER.1

@@done_redraw

            MVI     POINT,  R1
            ANDI    #$F8,   R1
            SLR     R1,     2
            SLR     R1,     1
            MVI     COURSE, R0      ;
            SLL     R0,     1       ;
            ADDR    R0,     R1      ; + *2
            SLL     R0,     2       ;
            ADDR    R0,     R1      ; + *8
            SLL     R0,     1       ;
            ADDR    R0,     R1      ; + *16

            ADDI    #WCKPT, R1
            MVI@    R1,     R0

            MVO     R0,     RCIDX
            MVO     R0,     RCLVL
            SWAP    R0
            MVO     R0,     RCLVL+1
            CLRR    R0
            MVO     R0,     RCCNT

            PULR    R1
            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  NXTLVL:  Skip forward to the next level.                                ;;
;; ======================================================================== ;;
NXTLVL      PROC
           
            MVI     POINT,  R0
            ADDI    #8,     R0
            CMPI    #26*8,  R0
            BGE     RSTLVL
            MVO     R0,     POINT
            B       RSTLVL
            ENDP

    ENDI

;; ======================================================================== ;;
;;  INITLVL Initialize the level in preparation for the game.               ;;
;; ======================================================================== ;;
INITLVL     PROC

            CLRR    R0
            MVO     R0,     RCCNT 
            MVO     R0,     POINT 
@@1:        CLRR    R0
            MVO     R0,     LMCNT
            MVO     R0,     CUENUM
            MVO     R0,     SPINB
            MVI     COURSE, R1
            ADDI    #WINDEX,R1
            MVI@    R1,     R1
            MVO     R1,     RCIDX

            MVII    #1,     R0
            MVO     R0,     MOBHIT

            B       RSGGB           ; reset GGBs and return
            ENDP


TOCRATER    PROC
            
            MVI     INCITY, R0
            TSTR    R0
            BEQ     @@done
@@1:
            CLRR    R0
            MVO     R0,     INCITY
            B       DRAWGAME

@@done:     JR      R5
            ENDP

TOCITY      PROC
            
            MVI     INCITY, R0
            TSTR    R0
            BNEQ    @@done
@@1:
            MVII    #1,     R0

            MVI     COURSE, R1
            CMPI    #6,     R1
            BNC     @@not_mercury
            INCR    R0

@@not_mercury
            MVO     R0,     INCITY
            B       DRAWGAME

@@done:     JR      R5
            ENDP


TOPLANET    PROC
            SUBI    #3,     R2
            SLL     R2,     1
            CMP     COURSE, R2
            BEQ     @@done
            MVO     R2,     COURSE
            CMPI    #6,     R2
            BNC     @@not_mercury
            MVI     INCITY, R1      ; \
            SLL     R1              ;  |- make sure Mercury city
            MVO     R1,     INCITY  ; /   maps to underground
            B       DRAWGAME
@@not_mercury:
            MVI     INCITY, R1      ; \
            SARC    R1              ;  |_ make sure other planets don't
            ADCR    R1              ;  |  get underground.
            MVO     R1,     INCITY  ; / 
            B       DRAWGAME

@@done      JR      R5
            ENDP

           
