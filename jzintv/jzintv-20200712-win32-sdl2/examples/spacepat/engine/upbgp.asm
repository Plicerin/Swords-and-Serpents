;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPBGP     Update buggy velocity and related ground-phase info.          ;;
;;==========================================================================;;
UPBGP   PROC
        ;;------------------------------------------------------------------;;
        ;;  Do velocity updates for buggy and related ground phase updates. ;;
        ;;------------------------------------------------------------------;;
        MVI     JHGT,   R1          ;  10 
        TSTR    R1                  ;   6 
        BNEQ    @@njvl              ; 7/9 Don't update horiz vel when in air
                                    ;----
                                    ;  25 (taken case)
                                    ;  23 (fallthru case)
                                   
        MVI     WANTVL, R1          ;  10 Get the "desired velocity" 
        MVI     GRATE,  R0          ;  10 Get current buggy velocity
        SUBR    R0,     R1          ;   6 Find diff between desired and actual
        BEQ     @@njvl              ; 7/9 If none, just fall through
        BMI     @@vnr               ; 7/9 If below, round down when dividing
        ADDI    #31,    R1          ;   8 If above, round up when dividing
                                         
@@vnr:  SARC    R1,     2           ;   8 Divide difference by 32. (signed)
        SARC    R1,     2           ;   8 
        SARC    R1,     1           ;   6 
        CMPI    #$FFFE, R1          ;   8 \
        BGE     @@vdok              ; 7/9  |-- Don't slow down too fast.
        MVII    #$FFFE, R1          ;   8 /
@@vdok:                            
                                    ;     Add diff to rate, so we grow towards
        ADDR    R1,     R0          ;   6 desired rate gradually, rather 
                                    ;     than all at once.                                  
                                         
        MVO     R0,     GRATE       ;  11 save updated velocity.  At the
                                    ;     start of the game, the vel may be
                                    ;     "-ve" while buggy scrolls onscreen.
                                    ;----
                                    ; 110 (worst case)
                                    ;  23 (carried forward)
                                    ;----
                                    ; 133 (worst case)
@@njvl:
        ;;------------------------------------------------------------------;;
        ;;  Update the "phase" of the ground plane.                         ;;
        ;;------------------------------------------------------------------;;
        MVI     GRATE,  R0          ;  10 Get our buggy's velocity
        INCR    R0                  ;   6 Allow 0x001 - 0x100.
@@grok: MOVR    R0,     R3          ;   6 Save clamped rate in R3
        ADD     GPHASE, R0          ;  10 Add it to our "ground phase"
        ANDI    #$FFF,  R0          ;   8 
@@gpok  MVO     R0,     GPHASE      ;  11 Store updated phase.
        SWAP    R0,     1           ;   6 Put integer in lower byte
                                    ;----
                                    ;  57 (worst case)
                                    ; 133 (carried forward)
                                    ;----
                                    ; 190 (worst case)

        ;;------------------------------------------------------------------;;
        ;;  Calculate ground graphics pointer                               ;;
        ;;------------------------------------------------------------------;;
        MVO     R0,     PGPHAS      ;  11 Save current phase as previous phase
        ANDI    #$7,    R0          ;   8 
        MOVR    R0,     R2          ;   6 Copy current pos to generate pointer
        ADDI    #GROUND,R2          ;   8 \
        MVI@    R2,     R2          ;   8  |-- Look up ground pixel pattern.
        MVO     R2,     GDATA       ;  11 /    and copy it out.
        MVI     SPAT,   R2          ;  10 \
        CMPI    #SPATBL.hut0, R2    ;   8  |- suppress rock/crater update if
        BEQ     @@norock            ; 7/9 /   hut is onscreen (shares GRAM)
        MOVR    R0,     R2          ;   6 \
        SLL     R2,     1           ;   6  |
        ADDR    R0,     R2          ;   6  |-- R2 = pixel*48 + rock/crater tbl
        SLL     R2,     2           ;   8  |
        SLL     R2,     2           ;   8  |
        ADDI    #ROCKCRAT,R2        ;   8 /
        MVO     R2,     RPTR        ;  11 Save rock/crater data pointer
@@norock                            ;----
                                    ; 130 (worst case)
                                    ; 190 (carried forward)
                                    ;----
                                    ; 320 (worst case)

        ;;------------------------------------------------------------------;;
        ;;  Update buggy's jump state.                                      ;;
        ;;------------------------------------------------------------------;;
        MVI     JVEL,   R0          ;  10 \    Add our current vertical vel
        XORI    #$80,   R0          ;   8  |__ to our jump height, and accel
        SUBI    #$81,   R0          ;   8  |   downwards.
        MVO     R0,     JVEL        ;  11  |
        ADD     JHGT,   R0          ;  10 /    
        BGT     @@jok               ; 7/9 If this makes it -ve, stop the jump
        INCR    R0                  ;   6 \___ Zero if already on ground
        ADD     LANDED, R0
        MVO     R0,     LANDED      ;  10 /    Non-zero if just landed
        CLRR    R0                  ;   6 \___ Otherwise, we hit ground so set
        MVO     R0,     JVEL        ;  11 /    velocity to zero.
        MVO     R0,     JHGT        ;  11 
@@noj:  B       @@gwhl              ;   9
                                    ;----
                                    ; 107 (worst case)
                                    ; 320 (carried forward)
                                    ;----
                                    ; 427

        ;;------------------------------------------------------------------;;
        ;;  Update the wheels on the buggy.                                 ;;
        ;;------------------------------------------------------------------;;
@@jok:  MVO     R0,     JHGT        ;  11 \   Pull wheels all up
        MVII    #WHEELS.jump, R4    ;   8  |- while jumping.
        B       @@gdone             ;   9 /
                                    ;----
                                    ;  28
                                     
@@gwhl: MVI     GRATE,  R1          ;  10 Get buggy's velocity
;       INCR    R1                  ;   6
        SAR     R1,     2           ;   8 Divide it down
        ADD     PGPHAS, R1          ;  10 Add it to ground offset to get
                                    ;     relative position of buggy to ground.
        ANDI    #7,     R1          ;   8 Modulo 8 (1 card)
        SUBI    #8,     R1          ;   8 1st table is 8 words before @@data
                                         
        MVII    #WHEELS.data, R4    ;   8 \
        ADDR    R4,     R1          ;   6  |-- Look up desired wheel
        ADD@    R1,     R4          ;   8 /    orientation.
@@gdone MVO     R4,     WPTR        ;  11 Save resulting pointer to gfx data.
                                    ;----
                                    ;  83 (worst case)
                                    ; 427 (carried forward)
                                    ;----
                                    ; 510

        ;;------------------------------------------------------------------;;
        ;;  Now calculate the "top" and "mid" mountain "phases":            ;;
        ;;------------------------------------------------------------------;;
        MOVR    R3,     R0          ;   6 Get clamped rate into R0, R1 for top
        MOVR    R3,     R1          ;   6 mtn, and R2, R3 for mid mtn.
        MOVR    R3,     R2          ;   6 
        SAR     R1,     2           ;   8 \                                     
        ADDR    R1,     R0          ;   6  |__ Determine "top mtn" rate as 
        SAR     R0,     2           ;   8  |   fraction of buggy's base rate.   
        SAR     R0,     1           ;   6 /    R0 = TRATE = 0.15625 * GRATE 
        ADD     TPHASE, R0          ;   6 Add TRATE to current phase
        ANDI    #$1FFF, R0          ;   8 
        MVO     R0,     TPHASE      ;  11 Save new top-mountain phase.
                                    ;----
                                    ;  71
                                    ; 510 (carried forward)
                                    ;----
                                    ; 581
                                         
        ADDR    R3,     R2          ;   6 \    
        SAR     R2,     2           ;   8  |   Determine "mid mtn" rate as 
        MOVR    R2,     R3          ;   6  |-- fraction of buggy's base rate.   
        SAR     R3,     2           ;   8  |   R2 = MRATE = 0.28125 * GRATE        
        SUBR    R3,     R2          ;   6 /
        ADD     MPHASE, R2          ;   8 Add MRATE to current phase
        MVI     MIDMSK, R3          ;  10
        SWAP    R3                  ;   6
        COMR    R3                  ;   6
        ANDR    R3,     R2          ;  10
        MVO     R2,     MPHASE      ;  11 Save new mid-mountain phase.
                                    ;----
                                    ;  85
                                    ; 581 (carried forward)
                                    ;----
                                    ; 666

        ;;------------------------------------------------------------------;;
        ;;  Decide which mountains need moving, and which mountains we can  ;;
        ;;  actually move according to round-robin priority.                ;;
        ;;------------------------------------------------------------------;;
        SWAP    R0,     1           ;   6 
        SWAP    R2,     1           ;   6 
        ANDI    #$1F,   R0          ;   8 Strip fractional portion of TPHASE
        ANDI    #$3F,   R2          ;   8 Strip fractional portion of MPHASE
                                         
        CLRR    R3                  ;   6 For do-none case
        MVI     TSKIP,  R1          ;  10 If TSKIP == 0, top has priority
        CMPR    R3,     R1          ;   6
                                    ;----
                                    ;  50
                                    ; 666 (carried forward)
                                    ;----
                                    ; 716

        BEQ     @@tprio             ; 7/9 yes, check top b4 mid, else mid b4 top
@@mprio CMP     PMPHAS, R2          ;  10 If doing mid, see if mid needs it.
        BNEQ    @@do_mid            ; 7/9 yes -- update mid
@@tprio CMP     PTPHAS, R0          ;  10 If doing top, see if top needs it.
        BNEQ    @@do_top            ; 7/9 yes -- update top
        CMP     PMPHAS, R2          ;  10 If top didn't need it, check mid.
        BEQ     @@do_none           ; 7/9 if mid needed it, update mid.
                                    ;----
                                    ;  60 tskip != 0, do_none  <--
                                    ;  45 tskip == 0, do_none
                                    ;  43 tskip != 0, do_top
                                    ;  43 tskip == 0, do_mid
                                    ;  26 tskip != 0, do_mid
                                    ;  28 tskip == 0, do_top


@@do_mid:
        ; Bits 2..0 of MPHASE give pixel alignment
        ; Bits 5..3 of MPHASE give char. alignment if not CITY
        ; Bits 4..3 of MPHASE give char. alignment if CITY
        MVO     R2,     PMPHAS      ;  11 Store our new previous "mid" phase
        MOVR    R2,     R3          ;   6 Copy MPHASE to R3 for calculation
        ANDI    #7,     R3          ;   8 Keep bits 0..2 for gfx ptr generation
        SWAP    R3                  ;   6 \   Each "phase" takes up 32 words 
        SLR     R3,     2           ;   8  |- of ROM, so multiply by 32.
        SLR     R3,     1           ;   8 /
        MVI     MIDGFX, R0          ;  10 Offset into "middle-mountain" gfx 
        SWAP    R0                  ;   6
        ADDR    R0,     R3          ;   6
        CLRR    R1                  ;   6 Set flag so we give top mtn prio next
        CMP     INCITY, R1          ;  10 Are we in the city?
        MVO     R1,     TSKIP       ;  11 Give top prio next frame
        BEQ     @@ncity             ; 7/9 No: do 'crater' mid-mountain update
        ANDI    #$18,   R2          ;   8
        SLL     R2,     1           ;   6 
        B       @@iscity            ;   9
@@ncity                            
        ANDI    #$38,   R2          ;   8
        MVII    #MIDGR, R0          ;   8
@@iscity
        MVII    #MIDGR, R0          ;   8
        ADDR    R0,     R2          ;   8 Point to middle-mountain in GRAM
                                         
        B       @@m_done            ;   9 
                                    ;----
                                    ; 151 (worst case)
                                    ;  43 (worst case coming to mid)
                                    ; 716
                                    ;----
                                    ; 910 (worst case)


@@do_top:
        ; Bits 2..0 of TPHASE give pixel alignment
        ; Bits 4..3 of TPHASE give char. alignment
        MVO     R0,     PTPHAS      ;  11 Store our new previous "top" phase
        MOVR    R0,     R3          ;   6 Copy TPHASE to R3 for calculation
        MOVR    R0,     R2          ;   6
        ANDI    #7,     R3          ;   8 Keep bits 0..2 for gfx ptr generation
        SWAP    R3                  ;   6 \   Each "phase" takes up 32 words 
        SLR     R3,     2           ;   8  |- of ROM, so multiply by 32.
        SLR     R3,     1           ;   8 /
        ADDI    #TOPMOUNT,R3        ;   8 Offset into "top-mountain" gfx 
        MVII    #2,     R1          ;   8 (as side effect sets mid to top prio)
        CMP     INCITY, R1          ;  10
        MVO     R1,     TSKIP       ;  11 Give mid prio next frame
        BNEQ    @@asis              ; 7/9 \   Display rock background if
        ADDI    #ROCKBG-TOPMOUNT,R3 ;   8 /   in underground.
@@asis:
        ANDI    #$18,   R2          ;   8
        SLL     R2,     1           ;   6
        MVII    #TOPGR, R0          ;   8
        ADDR    R0,     R2          ;   8 Point to top-mountain in GRAM
                                    ;----
                                    ; 135 (worst case)
                                    ;  43 (worst case coming to top)
                                    ; 716
                                    ;----
                                    ; 894

@@m_done:
        MVO     R0,     MGRAM       ;  11
@@do_none:                          ;     R1 is zero on this path
        MVO     R3,     MPTR        ;  11 Save this as our gfx ptr.
        MVO     R2,     MGOFS       ;  11 Save that as our mountain GRAM ptr.
                                    ;----
                                    ;  33
                                    ; 910 (worst case)
                                    ;====
                                    ; 943 final, worst case

        ENDP
