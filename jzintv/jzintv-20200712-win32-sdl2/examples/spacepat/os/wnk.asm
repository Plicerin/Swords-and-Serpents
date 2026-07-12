
;; ======================================================================== ;;
;;  WAITKEY     Wait for release/press/release                              ;;
;;  WAITNOKEY   Wait for key release                                        ;;
;; ======================================================================== ;;
WAITKEY     PROC
            PSHR    R5
@@1:        CALL    WAITNOKEY   ; Wait for release-press-release
@@wk        MVI     $1FE,       R0
            XOR     $1FF,       R0
            BEQ     @@wk
            INCR    PC          ; skip PSHR R5 
WAITNOKEY   PSHR    R5

@@waitnokey MVII    #200,       R0
            MVO     R0,         TMP+4

@@stillnk   ADD     RSEED,      R0
            MVO     R0,         RSEED
            CALL    DBHC
            TSTR    R0
            BNEQ    @@waitnokey
            TSTR    R2
            BNEQ    @@waitnokey

            MVI     TMP+4,      R0
            DECR    R0
            MVO     R0,         TMP+4
            BPL     @@stillnk

            PULR    PC
            ENDP
