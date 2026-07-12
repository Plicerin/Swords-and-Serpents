
    IF 0
;; Ugly:  ISR address is packed into 5 MSBs of the 3 words of the CALL.
_SETISR     PROC
            SUBI    #3,     R5
            MVI@    R5,     R0  ; 5432:10__:____:_#__
            SWAP    R0          ; ____:_#__:5432:10__
            SLL     R0,     2   ; ___#:__54:3210:____
            XOR@    R5,     R0  ; BA98:7654:3210:____  5..0 gets XORd w/ opc.
            SLR     R0,     2   ; __BA:987:65432:10__
            SLR     R0,     2   ; ____:BA98:7654:3210
            XOR@    R5,     R0  ; FEDC:BA98:7654:3210  B..0 gets XORd w/ opc.
            MVO     R0,     ISRVEC
            SWAP    R0
            MVO     R0,     ISRVEC+1
            JR      R5
            ENDP
    ELSE
_SETISR     PROC
            MVI@    R5,     R0
            MVO     R0,     ISRVEC
            SWAP    R0
            MVO     R0,     ISRVEC+1
            JR      R5
            ENDP
    ENDI
