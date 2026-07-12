;; ======================================================================== ;;
;;  BGMPIND  -- Indirect lookup table for Bad Guy Motion Program state      ;;
;;              functions.  Up to 255 different states across all BGMPs     ;;
;;              are possible.  Initial states are confined to first 127.    ;;
;;              Exit states are confined to first 8.                        ;;
;; ======================================================================== ;;
BGMPIND     PROC
@@sauc_ex   DECLE   BGT_SAUC_EX         ; Exit functions must be in 1st 8.
@@flexit    DECLE   BGT_FLEXIT          ; 
@@fladv     DECLE   BGT_FLADV           ; 
@@null      DECLE   BGT_RET 

@@boulder0  DECLE   BGT_BOULDER0
@@boulder1  EQU     @@null
@@mine0     DECLE   BGT_MINE0  
@@mine1     DECLE   BGT_MINE1  
@@plant0    DECLE   BGT_PLANT0 
@@plant1    DECLE   BGT_PLANT1 
@@sauc_f0   DECLE   BGT_SAUC_F0         ; blue, pink firing programs
@@sauc_f1   DECLE   BGT_SAUC_F1         ; white firing program
@@sauc_lr   DECLE   BGT_SAUC_LR
@@sauc_ud   DECLE   BGT_SAUC_UD
@@turret0   DECLE   BGT_TURRET0
@@turret1   DECLE   BGT_TURRET1
@@follow0   DECLE   BGT_FOLLOW0         ; Thinker for the follower
@@follow1   DECLE   BGT_FOLLOW1         ; No thinker for 2nd half of follower
@@stal0     DECLE   BGT_STAL0
@@stal1     DECLE   BGT_STAL1
@@stal2     DECLE   BGT_STAL2
            ENDP

BGI         STRUCT  0
@@boulder0  EQU     BGMPIND.boulder0 - BGMPIND + 1
@@boulder1  EQU     BGMPIND.boulder1 - BGMPIND + 1
@@mine0     EQU     BGMPIND.mine0    - BGMPIND + 1
@@mine1     EQU     BGMPIND.mine1    - BGMPIND + 1
@@plant0    EQU     BGMPIND.plant0   - BGMPIND + 1
@@plant1    EQU     BGMPIND.plant1   - BGMPIND + 1
@@sauc_f0   EQU     BGMPIND.sauc_f0  - BGMPIND + 1
@@sauc_f1   EQU     BGMPIND.sauc_f1  - BGMPIND + 1
@@sauc_lr   EQU     BGMPIND.sauc_lr  - BGMPIND + 1
@@sauc_ud   EQU     BGMPIND.sauc_ud  - BGMPIND + 1
@@sauc_ex   EQU     BGMPIND.sauc_ex  - BGMPIND + 1
@@turret0   EQU     BGMPIND.turret0  - BGMPIND + 1
@@turret1   EQU     BGMPIND.turret1  - BGMPIND + 1
@@follow0   EQU     BGMPIND.follow0  - BGMPIND + 1
@@follow1   EQU     BGMPIND.follow1  - BGMPIND + 1
@@flexit    EQU     BGMPIND.flexit   - BGMPIND + 1
@@fladv     EQU     BGMPIND.fladv    - BGMPIND + 1
@@stal0     EQU     BGMPIND.stal0    - BGMPIND + 1
@@stal1     EQU     BGMPIND.stal1    - BGMPIND + 1
@@stal2     EQU     BGMPIND.stal2    - BGMPIND + 1
@@null      EQU     BGMPIND.null     - BGMPIND + 1
            ENDS

