;; ======================================================================== ;;
;;  CKBGP   Check Bad Guy Position.                                         ;;
;; ======================================================================== ;;
CKBGP   PROC

        CLRR    R0
        MVII    #SPAT1, R3

@@cklp: CMP@    R3,     R0          ; Is this one open?
        BEQ     @@next              ; Yes: skip it

        MOVR    R3,     R1          ; Use R1 for indexing other structures

        SLL     R1,     1
        ADDI    #SPXYP-2*SPAT1, R1  ; Index into SPXYP

        MVI@    R1,     R2          ; \_ Put integer in upper half
        SWAP    R2                  ; /

        CMPI    #190*256, R2        ; Check if offsides on right
        BNC     @@next
        CMPI    #254*256, R2        ; Check if offsides on left
        BC      @@next

        MOVR    R3,     R2
        ADDI    #BGEXIT-SPAT1, R2   ; Index into BGEXIT
        MVO@    R0,     R2          ; clear BGEXIT

        SLL     R1,     1           ; \
        MOVR    R1,     R4          ;  |- Index into BGMPTBL
        ADDI    #BGMPTBL-2*SPXYP,R4 ; /
        
        MVO@    R0,     R4          ; program ptr
        MVO@    R0,     R4          ; delay
        MVO@    R0,     R4          ; loopa
        ADDI    #SPHSCR-BGEXIT, R2  ; Index into SPHSCR
        MVO@    R0,     R4          ; loopb

        MVI@    R3,     R1          ; \
        CMPI    #S_end, R1          ;  |
        BGT     @@notsauc           ;  |_ if this was a saucer decr the
        MVI     WAVE,   R1          ;  |  wave counter.
        DECR    R1                  ;  |
        MVO     R1,     WAVE        ; /
@@notsauc
        MVO@    R0,     R3          ; attr
        MVO@    R0,     R2          ; clear horiz scrolling

@@next: INCR    R3
        CMPI    #SPAT+5,R3
        BNEQ    @@cklp

;       JR      R5
        ENDP
