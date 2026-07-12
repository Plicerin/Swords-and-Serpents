;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  CKGGB     Checks the good guy's bullets and sees if they hit anything.  ;;
;;==========================================================================;;
CKGGB   PROC
;       PSHR    R5              ;   9

        ;;==================================================================;;
        ;;  Compare all bad guys and bad-guy bullets against our bullets.   ;;
        ;;  Also, disable bullets that go off the top of the screen.        ;;
        ;;==================================================================;;
@@checkit:

        MVII    #SPXY2+10,R4    ;   8
        MVII    #SPAT2+5,R5     ;   8
        MVII    #GGB1,  R3      ;   8

        ;;------------------------------------------------------------------;;
        ;;  Figure out where the "good guy" bullets are, if active.         ;;
        ;;------------------------------------------------------------------;;

        MVII    #$6060, R0
        MVI     HBCOL1, R1      ;      Let's look at the horizontal bullet
        SLL     R1
        BEQ     @@nohb
        SUBI    #$0004, R1

        MVII    #GROW_p + 4, R0
        SUB     HBROW,  R0
        SWAP    R0
        ADDR    R1,     R0
@@nohb:
        MVO     R0,     GGB0

@@ggbinit:
        MVI@    R5,     R0      ;   9  Is this bullet active?
        TSTR    R0              ;   6 
        BEQ     @@ggbskip       ;      No?  Store out a large coord for it then
                                      
        SDBD
        MVI@    R4,     R0      ;   8  Get Y/X coordinate of bullet 0
                                      
        CMPI    #$0500, R0      ;   8  Is it going off top of screen?
        BNC     @@ggbdie        ; 7/9  Yes:  Nuke the bullet
                                      
        SUBI    #$0301, R0      ;   8  R0 == Y/X Coordinate of upper left
                                      
        MVO@    R0,     R3      ;   9 
        INCR    R3              ;   6 
        CMPI    #GGB2+1,R3      ;   8 
        BNEQ    @@ggbinit       ; 9/7 
        B       @@do_bullet     ;   9 
                                      
@@ggbdie:                             
        DECR    R5              ;   6  \
        CLRR    R1              ;   6   |-- disable our bullet
        MVO@    R1,     R5      ;   9  /
        SUBI    #2,     R4      ;   8 
                                      
@@ggbskip:                            
        ADDI    #2,     R4      ;   8 
        MVII    #$6060, R0      ;   8  big enough that it won't hit anything
                                      
        MVO@    R0,     R3      ;   9 
        INCR    R3              ;   6 
        CMPI    #GGB2+1,R3      ;   8 
        BNEQ    @@ggbinit       ; 9/7 
                                      

        CMP     GGB0,   R0      ;  10 
        BNEQ    @@do_bullet     ; 7/9  Is bullet 0 active?  Yes?  Do it.
        CMP     GGB1,   R0      ;  10 
        BEQ     @@no_bullet     ; 7/9  Is bullet 1 active?  Yes?  Do it.
                                ;      Otherwise, none of 3 is, so leave.

        ;;------------------------------------------------------------------;;
        ;;  If we had active bullets, compare them against all the bad      ;;
        ;;  guys and all their bullets.                                     ;;
        ;;------------------------------------------------------------------;;
@@do_bullet:

        MVII    #SPAT,  R5      ;   8  Point to MOB Attribute Table
        MVII    #SPXYP, R4      ;   8  Point to MOB X/Y coordinates
                                      
@@checkmob:                           
        MVI@    R5,     R3      ;   8  Get attr for next mob
        DECR    R3              ;   6  Zero?  Skip to next.
        BMI     @@skipmob       ; 7/9
        ADDI    #SPATBL+3, R3   ;   8  Offset to 'size' info in MOB record
                                      
        SDBD                          
        MVI@    R4,     R1      ;   8  Get Y/X coordinate
                                      
        MOVR    R1,     R2      ;   6
                                      
        SUB     GGB1,   R1      ;  10  Check the lower right corner
        BNC     @@out1          ; 7/9  If Y went -ve, bullet's to the right
        SWAP    R1,     1       ;   6  
        SWAP    R1,     1       ;   6  
        BMI     @@out1          ; 7/9  If X went -ve, bullet's below


        ;;------------------------------------------------------------------;;
        ;;  At this point R1 contains our X distance to the right,          ;;
        ;;  and our Y distance to the right of the bullet's upper left      ;;
        ;;  corner vs. the lower right corner of the bad guy.  So, if       ;;
        ;;  we subtract the bad buy's width and we still end up positive,   ;;
        ;;  we're to the left or above.  (Note that we bias all bad-guy     ;;
        ;;  widths in our table by the width/height of the bullet.)         ;;
        ;;------------------------------------------------------------------;;
        SUB@    R3,     R1      ;   8  Compare to bad-guy's size.
        BPL     @@out1          ; 7/9  If Y still +ve, bullet's to the left
        SWAP    R1,     2       ;   8
        BPL     @@out1          ; 7/9  If X still +ve, bullet's above


        ;;------------------------------------------------------------------;;
        ;;  If we made it this far, it's a HIT.                             ;;
        ;;  Disable bullet 1 and then process the hit.                      ;;
        ;;------------------------------------------------------------------;;
        CLRR    R1              ;   6
        MVO     R1,     SPAT2+5 ;  11  disable the good-guy bullet #1

        B       @@hit           ;   9


@@out1:
        MOVR    R2,     R1
        SUB     GGB2,   R2      ;  10  Check the lower right corner
        BNC     @@out2          ; 7/9  If Y went -ve, bullet's to the right
        SWAP    R2,     1       ;   6   
        SWAP    R2,     1       ;   6   
        BMI     @@out2          ; 7/9  If X went -ve, bullet's below


        ;;------------------------------------------------------------------;;
        ;;  At this point R2 contains our X distance to the right,          ;;
        ;;  and our Y distance to the right of the bullet's upper left      ;;
        ;;  corner vs. the lower right corner of the bad guy.  So, if       ;;
        ;;  we subtract the bad buy's width and we still end up positive,   ;;
        ;;  we're to the left or above.  (Note that we bias all bad-guy     ;;
        ;;  widths in our table by the width/height of the bullet.)         ;;
        ;;------------------------------------------------------------------;;
        SUB@    R3,     R2      ;   8  Compare to bad-guy's size.
        BPL     @@out2          ; 7/9  If Y still +ve, bullet's to the left
        SWAP    R2,     2       ;   8   
        BPL     @@out2          ; 7/9  If X still +ve, bullet's above

        ;;------------------------------------------------------------------;;
        ;;  If we made it this far, it's a HIT..                            ;;
        ;;  Disable bullet 2 and then process the hit.                      ;;
        ;;------------------------------------------------------------------;;
        CLRR    R1              ;   6   
        MVO     R1,     SPAT2+6 ;  11  disable the good-guy bullet #2

        B       @@hit

        ;;------------------------------------------------------------------;;
        ;;  Check the horizontal bullet.                                    ;;
        ;;------------------------------------------------------------------;;
@@out2:
        SUB     GGB0,   R1      ;  10  Check the lower right corner
        BNC     @@out3          ; 7/9  If Y went -ve, bullet's to the right
        SWAP    R1,     1       ;   6   
        SWAP    R1,     1       ;   6   
        BMI     @@out3          ; 7/9  If X went -ve, bullet's below

        SUB@    R3,     R1      ;   8  Compare to bad-guy's size.
        BPL     @@out3          ; 7/9  If Y still +ve, bullet's to the left
        SWAP    R1,     2       ;   8   
        BPL     @@out3          ; 7/9  If X still +ve, bullet's above

        MVII    #1,     R1      ;   6  kill bullet indirectly by expiring it.
        MVO     R1,     HBCNT   ;  10

@@hit:
        ;;------------------------------------------------------------------;;
        ;;  Now process the hit.  For now, just nuke the sprite.            ;;
        ;;------------------------------------------------------------------;;
        DECR    R5              ;   6   

        ; ick... if we're in group 2, decr the bad-guy-bullet-count
        CMPI    #SPAT2,   R5    ;   8
        BLT     @@notbgb        ; 7/9

        CLRR    R1              ;   8
        MVO@    R1,     R5      ;   9  disable the bad-guy bullet
        MVO     R1,     SPINB   ;  10  and let a new spinner bullet out

        B       @@out3          ;   9
@@notbgb:

        MVII    #SPATBL.x1,R1   ;   8  Explosion animation
        MVI@    R5,     R0      ;   8  get bgtype
        DECR    R5
        MVO@    R1,     R5      ;   9  disable the bad-guy 
        SUBI    #2,     R4      ;   8


@@process
        PSHR    R1
        PSHR    R4
        PSHR    R5

        ; Update the wave counter
        CMPI    #S_end, R0
        BGT     @@notsauc
        MVI     WAVE,   R1
        DECR    R1
        MVO     R1,     WAVE
        MVI     WKILL,  R1
        INCR    R1
        MVO     R1,     WKILL

        ; If this was a saucer in a wave, score it specially.
        SUBI    #3,     R1
        BMI     @@notsauc

        CMPI    #3,     R1
        BLT     @@waveok
        MVII    #2,     R1
@@waveok 
        ADDI    #WBONUS,R1
        MOVR    R0,     R2
        MVI@    R1,     R0
        REGSCO
        MOVR    R2,     R0
        B       @@skipscore

@@notsauc

        ; Score this entity
        PSHR    R0
        MOVR    R0,     R4
        ADDI    #SPATBL,R4
        MVI@    R4,     R1      ; Get offset 1 of SPATBL
        MVI@    R4,     R2      ; Get offset 2 of SPATBL
        ANDI    #$3000, R1
        ANDI    #$0600, R2
        SLR     R1,     1
        XORR    R1,     R2
        SLR     R2,     1
        SWAP    R2
        CMPI    #12,    R2
        BC      @@randscore
        SARC    R2
        XORI    #SCORTBL, R2    ; Relies on SCORTBL being at $D000!!!
        MVI@    R2,     R0
        ADCR    PC
        SWAP    R0
        ANDI    #$FF,   R0
        REGSCO
        B       @@donescore
@@randscore
        MVII    #pack(Score(5000), Score(8000)), R0
        MVII    #pack(Score(3000), Score(6000)), R1
        CMPI    #13,    R2
        BLT     @@dorand
        MVII    #pack(Score(9000), Score(10000)),R1
        CMPI    #14,    R2
        BLT     @@dorand
        MVII    #pack(Score(2500), Score(5000)), R0
@@dorand
        RNDSCO

@@donescore
        PULR    R0
@@skipscore

        CMPI    #SPATBL.bld0a, R0
        BLT     @@nobld
        CMPI    #SPATBL.bld0d, R0
        BGT     @@nobld
        CALL    PLAYSFX
        DECLE   FXLGEXP
        B       @@kill

@@nobld CMPI    #SPATBL.stal,  R0
        BLT     @@nostal
        CMPI    #SPATBL.stalf, R0
        BGT     @@nostal
        CALL    PLAYSFX
        DECLE   FXSMEXP
        B       @@kill

@@nostal:
        CALL    PLAYSFX
        DECLE   FXALIEN

@@kill:
        PULR    R1
        PSHR    R1

        SUBI    #SPAT+1,R1
        CALL    BGKILL

        PULR    R5
        PULR    R4
        PULR    R1

@@skipmob:
        ADDI    #2,     R4      ;   8  Go to next MOB's X/Y

@@out3:
        CMPI    #SPAT2+5, R5    ;   8
        BNEQ    @@checkmob      ; 9/7

@@no_bullet:


;       PULR    PC
        ENDP

