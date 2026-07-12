L_5F43:
        DECR    R1                              ; 5F43   0011
L_5F44:
        ADDI    #$0163, R2                      ; 5F44   02FA 0163
L_5F46:
        MVI@    R2,     R0                      ; 5F46   0290
        ANDI    #$007F, R0                      ; 5F47   03B8 007F
        MVO@    R0,     R2                      ; 5F49   0250
        INCR    R2                              ; 5F4A   000A
        DECR    R1                              ; 5F4B   0011
        BPL     L_5F46                          ; 5F4C   0223 0007
        MOVR    R5,     R7                      ; 5F4E   00AF

L_5F4F:
        SDBD                                    ; 5F4F   0001
        MVII    #$BFFF, R0                      ; 5F50   02B8 00FF 00BF
        MVI@    R3,     R1                      ; 5F53   0299
        ANDR    R0,     R1                      ; 5F54   0181
        MVO@    R1,     R3                      ; 5F55   0259
        ADDI    #$0008, R3                      ; 5F56   02FB 0008
        AND@    R3,     R0                      ; 5F58   0398
        MVO@    R0,     R3                      ; 5F59   0258
        MOVR    R5,     R7                      ; 5F5A   00AF

