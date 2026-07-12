L_5F5B:
        MVII    #$0008, R2                      ; 5F5B   02BA 0008
        CLRR    R3                              ; 5F5D   01DB
L_5F5E:
        DECR    R2                              ; 5F5E   0012
        INCR    R7                              ; 5F5F   000F

L_5F60:
        CLRR    R2                              ; 5F60   01D2
L_5F61:
        PSHR    R5                              ; 5F61   0275
        PSHR    R3                              ; 5F62   0273
        MOVR    R3,     R4                      ; 5F63   009C
        MOVR    R3,     R5                      ; 5F64   009D
        ADDI    #$0325, R4                      ; 5F65   02FC 0325
        ADDI    #$033D, R5                      ; 5F67   02FD 033D
L_5F69:
        CLRR    R0                              ; 5F69   01C0
        MVO@    R0,     R4                      ; 5F6A   0260
        MVO@    R0,     R5                      ; 5F6B   0268
        PSHR    R5                              ; 5F6C   0275
        ADDI    #$000F, R5                      ; 5F6D   02FD 000F
        MVO@    R0,     R5                      ; 5F6F   0268
        SUBI    #$034E, R5                      ; 5F70   033D 034E
        MOVR    R5,     R3                      ; 5F72   00AB

        JSR     R5,     L_5FA7                  ; 5F73   0004 015C 03A7

        PULR    R5                              ; 5F76   02B5
        DECR    R2                              ; 5F77   0012
        BPL     L_5F69                          ; 5F78   0223 0010

        PULR    R3                              ; 5F7A   02B3
        PULR    R7                              ; 5F7B   02B7

L_5F7C:
        PSHR    R5                              ; 5F7C   0275
        MOVR    R3,     R2                      ; 5F7D   009A
        ADDI    #$0325, R2                      ; 5F7E   02FA 0325
        MVI@    R2,     R0                      ; 5F80   0290
        PSHR    R1                              ; 5F81   0271
        PSHR    R0                              ; 5F82   0270

        JSR     R5,     L_5F60                  ; 5F83   0004 015C 0360

        PULR    R0                              ; 5F86   02B0
        PULR    R1                              ; 5F87   02B1
        MOVR    R3,     R2                      ; 5F88   009A
        ADDI    #$0167, R2                      ; 5F89   02FA 0167
        ADDI    #$0325, R3                      ; 5F8B   02FB 0325
        MVO@    R3,     R2                      ; 5F8D   0253
        MVO@    R0,     R3                      ; 5F8E   0258
        ADDI    #$0018, R3                      ; 5F8F   02FB 0018
        MVO@    R1,     R3                      ; 5F91   0259
        PULR    R7                              ; 5F92   02B7

        PSHR    R5                              ; 5F93   0275
        MVI     G_01A4, R0                      ; 5F94   0280 01A4
        TSTR    R0                              ; 5F96   0080
        BEQ     L_5FA0                          ; 5F97   0204 0007

        DECR    R0                              ; 5F99   0010
        MVO     R0,     G_01A4                  ; 5F9A   0240 01A4
        BNEQ    L_5FA0                          ; 5F9C   020C 0002
        MVI     G_02F6, R7                      ; 5F9E   0287 02F6
L_5FA0:
        PULR    R7                              ; 5FA0   02B7

L_5FA1:
        MVI@    R5,     R0                      ; 5FA1   02A8
        MVO     R0,     G_01A4                  ; 5FA2   0240 01A4
        MVO     R5,     G_02F6                  ; 5FA4   0245 02F6
        PULR    R7                              ; 5FA6   02B7

L_5FA7:
        PSHR    R5                              ; 5FA7   0275
        MOVR    R3,     R0                      ; 5FA8   0098

        JSR     R5,     X_POW2                  ; 5FA9   0004 0114 0345

        COMR    R0                              ; 5FAC   0018
        DIS                                     ; 5FAD   0003
        AND     G_0117, R0                      ; 5FAE   0380 0117
        MVO     R0,     G_0117                  ; 5FB0   0240 0117
        EIS                                     ; 5FB2   0002
        PULR    R7                              ; 5FB3   02B7

L_5FB4:
        ADDI    #$0325, R3                      ; 5FB4   02FB 0325
        MVI@    R3,     R0                      ; 5FB6   0298
        ANDI    #$00FF, R0                      ; 5FB7   03B8 00FF
        ADDI    #$0008, R3                      ; 5FB9   02FB 0008
        MVI@    R3,     R1                      ; 5FBB   0299
        ANDI    #$007F, R1                      ; 5FBC   03B9 007F
        SUBI    #$032D, R3                      ; 5FBE   033B 032D
        MOVR    R5,     R7                      ; 5FC0   00AF

