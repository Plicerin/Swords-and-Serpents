L_5E48:
        PSHR    R5                              ; 5E48   0275
        PSHR    R4                              ; 5E49   0274
        PSHR    R2                              ; 5E4A   0272
        PSHR    R0                              ; 5E4B   0270
        ANDI    #$0030, R0                      ; 5E4C   03B8 0030
        SLR     R0,     2                       ; 5E4E   0064
        SLR     R0,     1                       ; 5E4F   0060
        ADD     G_02F4, R0                      ; 5E50   02C0 02F4
        ANDI    #$0060, R2                      ; 5E52   03BA 0060
        SLR     R2,     2                       ; 5E54   0066
        SLR     R2,     2                       ; 5E55   0066
        SLR     R2,     1                       ; 5E56   0062
        MOVR    R2,     R3                      ; 5E57   0093
        SLR     R3,     1                       ; 5E58   0063
        ADDR    R0,     R3                      ; 5E59   00C3
        MVI@    R3,     R0                      ; 5E5A   0298
        RRC     R2,     1                       ; 5E5B   0072
        BNC     L_5E60                          ; 5E5C   0209 0002

        SLR     R0,     2                       ; 5E5E   0064
        SLR     R0,     2                       ; 5E5F   0064
L_5E60:
        ANDI    #$000F, R0                      ; 5E60   03B8 000F
        DECLE   $0001                           ; 5E62   0001

        MVII    #$00CE, R4                      ; 5E63   02BC 00CE
        SLR     R1,     2                       ; 5E65   0065
        ADDR    R0,     R4                      ; 5E66   00C4
        SDBD                                    ; 5E67   0001
        MVI@    R4,     R2                      ; 5E68   02A2
        PULR    R0                              ; 5E69   02B0
        ANDI    #$000F, R0                      ; 5E6A   03B8 000F
L_5E6C:
        TSTR    R0                              ; 5E6C   0080
        BEQ     L_5E73                          ; 5E6D   0204 0004

        ADD@    R2,     R2                      ; 5E6F   02D2
        DECR    R0                              ; 5E70   0010
        B       L_5E6C                          ; 5E71   0220 0006

L_5E73:
        PULR    R3                              ; 5E73   02B3
        ANDI    #$001F, R3                      ; 5E74   03BB 001F
L_5E76:
        INCR    R2                              ; 5E76   000A
        MVI@    R2,     R0                      ; 5E77   0290
        ANDI    #$001F, R0                      ; 5E78   03B8 001F
        SUBR    R0,     R3                      ; 5E7A   0103
        BGE     L_5E76                          ; 5E7B   022D 0006

        NEGR    R3                              ; 5E7D   0023
        PULR    R4                              ; 5E7E   02B4
        PULR    R7                              ; 5E7F   02B7

L_5E80:
        PSHR    R5                              ; 5E80   0275
        MVI     G_0175, R2                      ; 5E81   0282 0175
        ADDI    #$0020, R2                      ; 5E83   02FA 0020
        ANDI    #$0060, R2                      ; 5E85   03BA 0060
        MVI     G_0178, R0                      ; 5E87   0280 0178

        JSR     R5,     L_5E48                  ; 5E89   0004 015C 0248

        PULR    R7                              ; 5E8C   02B7

L_5E8D:
        PSHR    R5                              ; 5E8D   0275
        MVI     G_0175, R0                      ; 5E8E   0280 0175
        TSTR    R2                              ; 5E90   0092
        BEQ     L_5E95                          ; 5E91   0204 0002

        INCR    R0                              ; 5E93   0008
        INCR    R7                              ; 5E94   000F

L_5E95:
        DECR    R0                              ; 5E95   0010
L_5E96:
        ANDI    #$007F, R0                      ; 5E96   03B8 007F
        MVO     R0,     G_0175                  ; 5E98   0240 0175
        MVII    #$0200, R4                      ; 5E9A   02BC 0200
        TSTR    R2                              ; 5E9C   0092
        BEQ     L_5EA3                          ; 5E9D   0204 0004

        ADDI    #$0013, R0                      ; 5E9F   02F8 0013
        ADDI    #$0013, R4                      ; 5EA1   02FC 0013
L_5EA3:
        ANDI    #$007F, R0                      ; 5EA3   03B8 007F
        MVO     R0,     G_0177                  ; 5EA5   0240 0177
        MOVR    R0,     R2                      ; 5EA7   0082
        MVI     G_0176, R0                      ; 5EA8   0280 0176
        MVO     R0,     G_0178                  ; 5EAA   0240 0178
        MVII    #$000C, R1                      ; 5EAC   02B9 000C
L_5EAE:
        PSHR    R1                              ; 5EAE   0271

        JSR     R5,     L_5E48                  ; 5EAF   0004 015C 0248

        MVI@    R2,     R1                      ; 5EB2   0291

        JSR     R5,     L_5EC7                  ; 5EB3   0004 015C 02C7

        MVO@    R1,     R4                      ; 5EB6   0261
        MVI     G_0177, R2                      ; 5EB7   0282 0177
        MVI     G_0178, R0                      ; 5EB9   0280 0178
        INCR    R0                              ; 5EBB   0008
        ANDI    #$003F, R0                      ; 5EBC   03B8 003F
        MVO     R0,     G_0178                  ; 5EBE   0240 0178
        ADDI    #$0013, R4                      ; 5EC0   02FC 0013
        PULR    R1                              ; 5EC2   02B1
        DECR    R1                              ; 5EC3   0011
        BNEQ    L_5EAE                          ; 5EC4   022C 0017
        PULR    R7                              ; 5EC6   02B7

