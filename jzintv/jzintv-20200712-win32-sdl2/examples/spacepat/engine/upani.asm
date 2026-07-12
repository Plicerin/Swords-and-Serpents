;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPANI      -- Update animation                                          ;;
;;==========================================================================;;
UPANI       PROC
            ;; ------------------------------------------------------------ ;;
            ;;  Step through SPAT1 looking at the SPATBL entries.           ;;
            ;;  SPENTs have 11 extra bits distributed around their 4 words: ;;
            ;;                                                              ;;
            ;;      Word 0:  Bits 15..11  -- Next SPAT bits 7:3             ;;
            ;;      Word 1:  Bits 15..12  -- Next SPAT bits 2:0.            ;;
            ;;      Word 2:  Bits 15..14  -- Animation rate: 60/30/15/0     ;;
            ;; ------------------------------------------------------------ ;;

            MVII    #SPAT,  R4

@@loop:
            MVI@    R4,     R1              ; Read SPATBL index
            DECR    R1                      ;\_ Skip if zero
            BMI     @@next                  ;/

            ADDI    #SPATBL+2, R1           ; R1 = &spatbl[idx*4 + 2]

            MVI@    R1,     R0              ; \
            ANDI    #$C000, R0              ;  |  Get animation rate from
            BEQ     @@next                  ;  |- 2 MSBs of Word #2.  00
            SLLC    R0,     2               ;  |  means no animation.
            RLC     R0,     2               ; /
            SUBI    #2,     R0              ; \_  Map 1, 2, 3 
            ANDI    #3,     R0              ; /   to  3, 0, 1

            MVI     TICK,   R2              ; \
            SLR     R2,     1               ;  |  Skip if 0, 1, or 2 LSBs
            XORR    R4,     R2              ;  |- of TICK XOR SPATIDX != 0
            ANDR    R2,     R0              ;  |
            BNEQ    @@next                  ; /

            DECR    R1                      ; \
            MVI@    R1,     R2              ;  |
            SLLC    R2,     1               ;  |_ Get bits 2, 0 from
            RLC     R0,     2               ;  |  bits 15:14.  Bit 1 is 
            SLLC    R2,     1               ;  |  always 0.
            RLC     R0,     1               ; /   

            DECR    R1                      ; \
            MVI@    R1,     R2              ;  |_ Get bits 7:3 from
            SWAP    R2                      ;  |  bits 15:11 
            ANDI    #$F8,   R2              ; /

            XORR    R2,     R0              ; Merge

            DECR    R4                      ; \_  Store merged result to 
            MVO@    R0,     R4              ; /   SPAT.

@@next:     CMPI    #SPAT+10, R4            ; Iterate over active objects
            BLT     @@loop

;           JR      R5

            ENDP
