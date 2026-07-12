
;; ======================================================================== ;;
;;  ADDSCORE    Adds a constant, random value from table or register to     ;;
;;              the player's current score.                                 ;;
;; ======================================================================== ;;
ADDSCORE    PROC
@@cst       MVI@    R5,         R0      ; Get constant from after call
            B       @@reg       
                                
@@rnd       MVI     RSEED,      R2      ; \
            RLC     R2                  ;  |_ evolve random seed in case
            ADCR    R2                  ;  |  multple RNDSCOs in one tic
            MVO     R2,         RSEED   ; /
                                
            RLC     R2                  ;
            ADCR    PC                  ;
            MOVR    R1,         R0      ;
            RLC     R2                  ;
            ADCR    PC                  ;
            SWAP    R0
            ANDI    #$FF,       R0

@@reg       
            PSHR    R1
            MVII    #SCORE,     R4      ; \
            SDBD                        ;  |-  Add to 16-bit score
            ADD@    R4,         R0      ; /
            MOVR    R1,         R4     
                                       
            MVII    #SCORE,     R4      ; \
            MVO@    R0,         R4      ;  |_  Store it out.
            SWAP    R0                  ;  |
            MVO@    R0,         R4      ; /
            SWAP    R0                  ; Swap it back into normal order
                                       
@@peakagain 

            SDBD                        ; \__ See if this is a new peak score
            CMP@    R4,         R0      ; /   so we can record it if it is.
            BNC     @@checkbon

            ; Update peak score
            SUBI    #2,         R4
            MVO@    R0,         R4
            SWAP    R0     
            MVO@    R0,         R4
            SWAP    R0                  ; Swap it back into normal order

            ; While we're here, check for high score
            CMPI    #TOPSCO,    R4
            BNEQ    @@checkbon
            ADD     COURSE,     R4
            ADD     COURSE,     R4
            B       @@peakagain

@@checkbon
            MVI     CURBON,     R1      ; \
            ADDI    #XTRATNK,   R1      ;  |_ See if score is above next
            CMP@    R1,         R0      ;  |  bonus threshold
            BNC     @@nobon             ; /

            SUBI    #XTRATNK-1, R1      ; \
            MVO     R1,         CURBON  ;  |
            MVI     LIVES,      R0      ;  |- Yes:  Advance threshold and
            INCR    R0                  ;  |  increment life count
            MVO     R0,         LIVES   ; /

@@nobon     MVII    #1,         R0
            MVO     R0,         DOSCO
            PULR    R1
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  DEFSCORE    Adds the deferred score to the current score.               ;;
;; ======================================================================== ;;
DEFSCORE    PROC
            MVI     LANDED, R0          ; \
            SARC    R0,     2           ;  |_ Only do this if we just 
            BNOV    JRR5                ;  |  landed, and landed safely
            MVO     R0,     LANDED      ; /
@@1:        

            ; Scan for scorable jumpables to the left of us
            MVII    #JMPSCO,    R4
            MVII    #SPXYP,     R3
            MVI     DEFSCO,     R0      ; Get current deferred score
            PSHR    R3
            PSHR    R2

@@lp        MVI@    R4,         R1
            TSTR    R1
            BEQ     @@nxt

            MVI@    R3,         R2
            ANDI    #$FF,       R2
            CMP     TXLO,       R2
            BGT     @@nxt

            DECR    R4
            CLRR    R2
            MVO@    R2,         R4

@@sc        ADDI    #Score(500),R0
            DECR    R1
            BPL     @@sc

@@nxt       ADDI    #2,         R3
            CMPI    #JMPSCO+5,  R4
            BNEQ    @@lp

            PULR    R2
            PULR    R3

            TSTR    R0
            BEQ     JRR5
            CLRR    R1
            MVO     R1,     DEFSCO      ; Clear previous deferred
            B       ADDSCORE.reg        ; Add it in!
            ENDP

;; ======================================================================== ;;
;;  XTRATNK     Boundaries at which the player gets an additional tank      ;;
;; ======================================================================== ;;
XTRATNK     PROC
            DECLE   Score(100000), Score(300000), Score(500000), Score(700000)
            DECLE   $FFFF
            ENDP

;; ======================================================================== ;;
;;  WBONUS      Wave bonuses                                                ;;
;; ======================================================================== ;;
WBONUS      PROC
            DECLE   Score(5000), Score(8000), Score(10000)
            ENDP

;; ======================================================================== ;;
;;  DISPFINAL  Display final score                                          ;;
;;  DISPPEAK   Display peak score                                           ;;
;;  DISPSCORE  Display current score                                        ;;
;;  DISPSCORE2 Display arbitrary score that's in R0                         ;;
;; ======================================================================== ;;
DISPFINAL   PROC
            MVII    #FINALTXT,  R0
            MVII    #SCORE,     R3
            B       @@x
DISPPEAK    MVII    #PEAKTXT,   R0
            MVII    #PSCOR,     R3
@@x         MVII    #C_TAN,     R1
            MVI@    R5,         R4
            PSHR    R5
            PSHR    R3
            CALL    P16.R
            MVII    #gen_cstk_card(0, GRAM, White, NoAdvance), R3
            PULR    R5
            B       @@y
DISPSCORE2  MVI@    R5,         R4
            PSHR    R5
            MVII    #gen_cstk_card(0, GRAM, White, NoAdvance), R3
            B       @@z
DISPSCORE   MVI@    R5,         R4
            PSHR    R5
            MVII    #SCORE,     R5
            MVII    #gen_cstk_card(0, GRAM, Blue, NoAdvance), R3
@@y:        SDBD
            MVI@    R5,         R0
@@z:        

            MVII    #$10 * 8,   R2
            XORR    R3,         R2
            ADDI    #6,         R4
            MVO@    R2,         R4

            CLRC
            RRC     R0
            BNC     @@zend
            MVII    #$15 * 8,   R2
            XORR    R3,         R2
@@zend      SUBI    #2,         R4
            MVO@    R2,         R4
            
            MVII    #5,         R2
            SUBI    #6,         R4
            CALL    PRNUM16.z

            PULR    PC
            ENDP

FINALTXT    S16     "Final score: "
PEAKTXT     S16     " Peak score: "


    IF 0
UPTSS       PROC
            MOVR    R5,     R2
            MVII    #TOPSCO,R4
            MVII    #TSS,   R5
@@tss:      SDBD
            MVI@    R4,     R0
            ADDR    R0,     R1
            MVO@    R0,     R5
            CMPI    #TSS+8, R5
            BNEQ    @@tss
            MVO     R1,     TSSUM
            JR      R2
            ENDP
    ENDI
