L_5EE2:
        PSHR    R5                              ; 5EE2   0275
        MVI     G_0175, R2                      ; 5EE3   0282 0175
        MVI     G_0176, R0                      ; 5EE5   0280 0176
        MVO     R0,     G_0178                  ; 5EE7   0240 0178
        MVII    #$0200, R4                      ; 5EE9   02BC 0200

L_5EEB:
        JSR     R5,     L_5E48                  ; 5EEB   0004 015C 0248

        MVII    #$0014, R0                      ; 5EEE   02B8 0014
        MVI     G_0175, R1                      ; 5EF0   0281 0175
        ANDI    #$001F, R1                      ; 5EF2   03B9 001F
L_5EF4:
        PSHR    R1                              ; 5EF4   0271
        MVI@    R2,     R1                      ; 5EF5   0291

        JSR     R5,     L_5EC7                  ; 5EF6   0004 015C 02C7

        MVO@    R1,     R4                      ; 5EF9   0261
        PULR    R1                              ; 5EFA   02B1
        DECR    R0                              ; 5EFB   0010
        BEQ     L_5F14                          ; 5EFC   0204 0016

        INCR    R1                              ; 5EFE   0009
        DECR    R3                              ; 5EFF   0013
        BNEQ    L_5EF4                          ; 5F00   022C 000D

        CMPI    #$001F, R1                      ; 5F02   0379 001F
        BGT     L_5F0C                          ; 5F04   020E 0006

        INCR    R2                              ; 5F06   000A
        MVI@    R2,     R3                      ; 5F07   0293
        ANDI    #$001F, R3                      ; 5F08   03BB 001F
        B       L_5EF4                          ; 5F0A   0220 0017

L_5F0C:
        PSHR    R0                              ; 5F0C   0270

        JSR     R5,     L_5E80                  ; 5F0D   0004 015C 0280

        PULR    R0                              ; 5F10   02B0
        CLRR    R1                              ; 5F11   01C9
        B       L_5EF4                          ; 5F12   0220 001F

L_5F14:
        CMPI    #$02EF, R4                      ; 5F14   037C 02EF
        BGE     L_5F21                          ; 5F16   020D 0009

        MVI     G_0175, R2                      ; 5F18   0282 0175
        MVI     G_0178, R0                      ; 5F1A   0280 0178
        INCR    R0                              ; 5F1C   0008
        MVO     R0,     G_0178                  ; 5F1D   0240 0178
        B       L_5EEB                          ; 5F1F   0220 0035
L_5F21:
        B       L_5E00                          ; 5F21   0220 0122

L_5F23:
        PSHR    R5                              ; 5F23   0275
        PSHR    R1                              ; 5F24   0271

        JSR     R5,     L_5F35                  ; 5F25   0004 015C 0335

        MOVR    R2,     R1                      ; 5F28   0091

        JSR     R5,     X_PACK_BYTES            ; 5F29   0004 0114 034F
        JSR     R5,     X_UNPK_BYTES            ; 5F2C   0004 0114 0357
        JSR     R5,     .EXEC.A2F               ; 5F2F   0004 0118 022F

        MOVR    R1,     R0                      ; 5F32   0088
        PULR    R1                              ; 5F33   02B1
        PULR    R7                              ; 5F34   02B7

