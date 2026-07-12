L_5EC7:
        PSHR    R5                              ; 5EC7   0275
        PSHR    R3                              ; 5EC8   0273
        MVI     G_02F5, R3                      ; 5EC9   0283 02F5
        SDBD                                    ; 5ECB   0001
        MVII    #$65A0, R5                      ; 5ECC   02BD 00A0 0065
        SLR     R1,     2                       ; 5ECF   0065
        SLR     R1,     2                       ; 5ED0   0065
        SLR     R1,     1                       ; 5ED1   0061
        ADDR    R1,     R3                      ; 5ED2   00CB
        ADDR    R1,     R5                      ; 5ED3   00CD
        MVI@    R3,     R1                      ; 5ED4   0299
        SLR     R1,     2                       ; 5ED5   0065
        SWAP    R1,     1                       ; 5ED6   0041
        XOR@    R3,     R1                      ; 5ED7   03D9
        SDBD                                    ; 5ED8   0001
        ANDI    #$3607, R1                      ; 5ED9   03B9 0007 0036
        MVI@    R5,     R3                      ; 5EDC   02AB
        SLL     R3,     2                       ; 5EDD   004F
        SLL     R3,     1                       ; 5EDE   004B
        XORR    R3,     R1                      ; 5EDF   01D9
        PULR    R3                              ; 5EE0   02B3
        PULR    R7                              ; 5EE1   02B7

