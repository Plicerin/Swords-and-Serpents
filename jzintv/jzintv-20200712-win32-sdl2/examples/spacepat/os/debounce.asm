;;==========================================================================;;
;;  DBHC     -- Read hand-controller inputs.                                ;;
;;                                                                          ;;
;;  OUTPUTS                                                                 ;;
;;      R0  Controller input                                                ;;
;;      R2  Previous controller input                                       ;;
;;==========================================================================;;
DBHC    PROC

        MVII    #$1FE,  R4      ;   8   Point to hand controllers
        MVI@    R4,     R0      ;   8   \_ Read and merge controller inputs
        XOR@    R4,     R0      ;   8   /
        MVI     DBOUT,  R2      ;  10   Previous input.
        MVO     R0,     DBOUT   ;  11   Store new input.
        JR      R5              ;   7
                                ;====
                                ; 154
        ENDP

