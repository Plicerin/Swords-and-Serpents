L_5E00:
        J       L_6377                          ; 5E00   0004 0360 0377

L_5E03:
        PSHR    R5                              ; 5E03   0275
        MVI     G_0176, R0                      ; 5E04   0280 0176
        CMPI    #$0002, R2                      ; 5E06   037A 0002
        BEQ     L_5E0C                          ; 5E08   0204 0002

        INCR    R0                              ; 5E0A   0008
        INCR    R7                              ; 5E0B   000F

L_5E0C:
        DECR    R0                              ; 5E0C   0010
L_5E0D:
        ANDI    #$003F, R0                      ; 5E0D   03B8 003F
        MVO     R0,     G_0176                  ; 5E0F   0240 0176
        MVII    #$0200, R4                      ; 5E11   02BC 0200
        RRC     R2,     1                       ; 5E13   0072
        BNC     L_5E1A                          ; 5E14   0209 0004

        ADDI    #$00DC, R4                      ; 5E16   02FC 00DC
        ADDI    #$000B, R0                      ; 5E18   02F8 000B
L_5E1A:
        MVO     R0,     G_0178                  ; 5E1A   0240 0178
        MVI     G_0175, R2                      ; 5E1C   0282 0175

        JSR     R5,     L_5E48                  ; 5E1E   0004 015C 0248

        MVII    #$0014, R0                      ; 5E21   02B8 0014
        MVI     G_0175, R1                      ; 5E23   0281 0175
        ANDI    #$001F, R1                      ; 5E25   03B9 001F
L_5E27:
        PSHR    R1                              ; 5E27   0271
        MVI@    R2,     R1                      ; 5E28   0291

        JSR     R5,     L_5EC7                  ; 5E29   0004 015C 02C7

        MVO@    R1,     R4                      ; 5E2C   0261
        PULR    R1                              ; 5E2D   02B1
        DECR    R0                              ; 5E2E   0010
        BEQ     L_5E47                          ; 5E2F   0204 0016

        INCR    R1                              ; 5E31   0009
        DECR    R3                              ; 5E32   0013
        BNEQ    L_5E27                          ; 5E33   022C 000D

        CMPI    #$001F, R1                      ; 5E35   0379 001F
        BGT     L_5E3F                          ; 5E37   020E 0006

        INCR    R2                              ; 5E39   000A
        MVI@    R2,     R3                      ; 5E3A   0293
        ANDI    #$001F, R3                      ; 5E3B   03BB 001F
        B       L_5E27                          ; 5E3D   0220 0017

L_5E3F:
        PSHR    R0                              ; 5E3F   0270

        JSR     R5,     L_5E80                  ; 5E40   0004 015C 0280

        PULR    R0                              ; 5E43   02B0
        CLRR    R1                              ; 5E44   01C9
        B       L_5E27                          ; 5E45   0220 001F
L_5E47:
        PULR    R7                              ; 5E47   02B7

