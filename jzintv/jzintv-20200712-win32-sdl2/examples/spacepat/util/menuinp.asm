;; ======================================================================== ;;
;;  MENUINP:  Read controller looking for DISC/Action or Enter, w/debounce  ;;
;;  R0:     Value read from controller                                      ;;
;;  S flag: S == 0 if enter, S == 1 if not enter                            ;;
;; ======================================================================== ;;

MENUINP     PROC
            PSHR    R5
            CALL    WAITNOKEY

            CLRR    R0
@@db        MVO     R0,         TMP + 3
            MVII    #200,       R0
            MVO     R0,         TMP + 4

@@disc      CALL    DBHC
            TSTR    R0
            BEQ     @@db
            CMP     TMP + 3,    R0
            BNEQ    @@db 
            MVI     TMP + 4,    R1
            DECR    R1
            MVO     R1,         TMP + 4
            BNEQ    @@disc

            MVII    #KEYS,      R4
            MVII    #3,         R2
@@kloop:    CMP@    R4,         R0
            BEQ     @@leave
            DECR    R2
            BPL     @@kloop

            CMPI    #$20,       R0
            BGE     @@disc

@@leave     PULR    PC
            
;@@1:        PSHR    R5
;            B       @@disc
            ENDP

;; ======================================================================== ;;
;;  KEYS    Look for action keys and 'enter' to exit menu                   ;;
;; ======================================================================== ;;
KEYS        DECLE   $C0, $A0, $60, $28

