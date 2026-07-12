;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPBSP     Update Moon Buggy sprites                                     ;;
;;==========================================================================;;
UPBSP   PROC

        ;;------------------------------------------------------------------;;
        ;;  Do buggy sprites manually -- they always get MOBs 0 and 1.      ;;
        ;;------------------------------------------------------------------;;
        MVI     GRATE,  R0          ;  10 Get buggy's current rate
        SAR     R0,     2           ;   8 \___ X coord == (rate/4) - 4
        SUBI    #$4,    R0          ;   8 /
        ANDI    #$FF,   R0          ;   8 Mask to 8-bit range
        MOVR    R0,     R1          ;   6 copy X coord
        XORI #_X.xsiz+_X.visb+_X.intr,R0 ;   8 Merge in XSIZE, VISB, INTR bits
        MVO     R0,     $01 + SDAT  ;  11 Set position of buggy
        ADDI    #$3,    R0          ;   8 Wheels/guns are 3 pixels to right
        MVO     R0,     $00 + SDAT  ;  11 Set position of wheels/guns
        SUBI    #8,     R1          ;   8 \__ back end of moon buggy
        MVO     R1,     TXLO        ;  11 / 
                                    ;----
                                    ;  97
@@1:                                     
        MVI     JHGT,   R1          ;  10 \    
        ADDI    #15,    R1          ;   8  |   Load in the jump height.  It's
        SAR     R1,     2           ;   8  |-- a Q5 number.  Round it up as
        SAR     R1,     2           ;   8  |   we truncate it.
        SAR     R1,     1           ;   6 /    
        MVII    #$100+GROW_p+7, R0  ;   8 \___ Y = $47 - jump_height
        SUBR    R1,     R0          ;   6 /    Set 2x-height flag
        MVO     R0,     $09 + SDAT  ;  11 Store Y coord for buggy. 
        MVII    #$180+GROW_p+7, R0  ;   8 \___ Y = $47 - jump_height
        SUBR    R1,     R0          ;   6 /    Set 2x-height, 16-rows flags
        MVO     R0,     $08 + SDAT  ;  11 Store Y coord for wheels/guns
                                    ;----
                                    ;  90
                                         
        MVII    #$1807+BCARD*8, R0  ;   8 Buggy is maroon, uses GRAM card
        MVO     R0,     $11 + SDAT  ;  11 Set attributes for buggy
        MVII    #$0800+WCARD*8, R0  ;   8 Wheels/guns are black, use GRAM 
        MVO     R0,     $10 + SDAT  ;  11 Set attributes for wheels/guns
                                    ;----
                                    ;  38
        

                                    ;  12 (fxn call)
                                    ;  97
                                    ;  90
                                    ;  38 
        JR      R5                  ;   7
                                    ;----
                                    ; 246

        ENDP
