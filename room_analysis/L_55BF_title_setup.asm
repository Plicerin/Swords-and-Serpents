L_55BF:
        PSHR    R5                              ; 55BF   0275
        CLRR    R0                              ; 55C0   01C0
        MVO     R0,     G_019C                  ; 55C1   0240 019C
        SDBD                                    ; 55C3   0001
        MVII    #$65DC, R0                      ; 55C4   02B8 00DC 0065
        MVO     R0,     G_02F4                  ; 55C7   0240 02F4
        SDBD                                    ; 55C9   0001
        MVII    #$65B7, R0                      ; 55CA   02B8 00B7 0065
        MVO     R0,     G_02F5                  ; 55CD   0240 02F5
        MVII    #$0002, R0                      ; 55CF   02B8 0002
        MVO     R0,     G_0175                  ; 55D1   0240 0175
        MVII    #$001A, R0                      ; 55D3   02B8 001A
        MVO     R0,     G_0176                  ; 55D5   0240 0176

        JSR     R5,     L_5EE2                  ; 55D7   0004 015C 02E2

        PULR    R7                              ; 55DA   02B7

L_55DB:
        MVII    #$0003, R0                      ; 55DB   02B8 0003
        MVI     G_018B, R2                      ; 55DD   0282 018B
        ANDI    #$0002, R2                      ; 55DF   03BA 0002
        BEQ     L_55E5                          ; 55E1   0204 0002

        XORI    #$000C, R0                      ; 55E3   03F8 000C
L_55E5:
        MVII    #$017B, R4                      ; 55E5   02BC 017B
        MVO@    R0,     R4                      ; 55E7   0260
        MVII    #$0009, R0                      ; 55E8   02B8 0009
        MVO@    R0,     R4                      ; 55EA   0260
        MVO@    R0,     R4                      ; 55EB   0260
        MVO@    R0,     R4                      ; 55EC   0260
        MVII    #$0032, R0                      ; 55ED   02B8 0032
        MVO@    R0,     R4                      ; 55EF   0260
        MVII    #$00FF, R0                      ; 55F0   02B8 00FF
        MVO@    R0,     R4                      ; 55F2   0260
        MVO@    R0,     R4                      ; 55F3   0260
        MVO@    R0,     R4                      ; 55F4   0260
        MVO@    R0,     R4                      ; 55F5   0260
        MOVR    R5,     R7                      ; 55F6   00AF

L_55F7:
        MVI     G_019C, R1                      ; 55F7   0281 019C
        MVII    #$0184, R4                      ; 55F9   02BC 0184
        SDBD                                    ; 55FB   0001
        ADDI    #$5617, R1                      ; 55FC   02F9 0017 0056
        MVI@    R1,     R0                      ; 55FF   0288
        MVO@    R0,     R4                      ; 5600   0260
        SDBD                                    ; 5601   0001
        ADDI    #$0004, R1                      ; 5602   02F9 0004 0000
        MVI@    R1,     R0                      ; 5605   0288
        MVO@    R0,     R4                      ; 5606   0260
        SDBD                                    ; 5607   0001
        ADDI    #$0004, R1                      ; 5608   02F9 0004 0000
        MVI@    R1,     R0                      ; 560B   0288
        MVO@    R0,     R4                      ; 560C   0260
        MVII    #$02F2, R4                      ; 560D   02BC 02F2
        SDBD                                    ; 560F   0001
        ADDI    #$0004, R1                      ; 5610   02F9 0004 0000
        MVI@    R1,     R0                      ; 5613   0288
        MVO@    R0,     R4                      ; 5614   0260
        MVO@    R0,     R4                      ; 5615   0260
        MOVR    R5,     R7                      ; 5616   00AF

        COMR    R6                              ; 5617   001E
        DECR    R4                              ; 5618   0014
        DECR    R4                              ; 5619   0014
        INCR    R2                              ; 561A   000A
        COMR    R6                              ; 561B   001E
        NEGR    R3                              ; 561C   0023
        ADCR    R0                              ; 561D   0028
        ADCR    R5                              ; 561E   002D
        SLLC    R2,     1                       ; 561F   005A
        RSWD    R4                              ; 5620   003C
        COMR    R6                              ; 5621   001E
        DECR    R4                              ; 5622   0014
        MOVR    R6,     R0                      ; 5623   00B0
        MOVR    R4,     R0                      ; 5624   00A0
        MOVR    R2,     R0                      ; 5625   0090
        TSTR    R0                              ; 5626   0080
