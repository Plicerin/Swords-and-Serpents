
        ORG     $5000
.HEADER:
        BIDECLE $0000           ; 5000  End of timer table

        BIDECLE $5000           ; 5002  Ptr: EXEC timer table
        BIDECLE $5017           ; 5004  Ptr: Start of game
        BIDECLE $500F           ; 5006  Ptr: Backgnd gfx list
        BIDECLE $500D           ; 5008  Ptr: GRAM init sequence
        BIDECLE $500F           ; 500A  Ptr: Date/Title
        DECLE   $0080           ; 500C  Key-click / flags
        DECLE   $0001           ; 500D  Border extension
        DECLE   $0000           ; 500E  Color Stack / FGBG
.TITLE:
        DECLE   $0052           ; 500F  Cartridge year
        STRING  "I"                             ; 5010  Title string
        STRING  "MA"            ; 5011  Color Stack init (2, 3)
        STRING  "G"             ; 5013  Border color init

        STRING  "IC"                            ; 5014   0049 0043
        DECLE   $0000                           ; 5016  

.TITLECODE:
        DIS                                     ; 5017   0003
        SDBD                                    ; 5018   0001
        MVII    #$538E, R0                      ; 5019   02B8 008E 0053
        MVO     R0,     .ISRVEC.0               ; 501C   0240 0100
        SWAP    R0,     1                       ; 501E   0040
        MVO     R0,     .ISRVEC.1               ; 501F   0240 0101
        MVII    #$02F7, R6                      ; 5021   02BE 02F7
        MVII    #$00F0, R0                      ; 5023   02B8 00F0
        MVII    #$0200, R4                      ; 5025   02BC 0200

        JSR     R5,     X_FILL_ZERO             ; 5027   0004 0114 0338

        MVII    #$0325, R4                      ; 502A   02BC 0325
        MVII    #$0047, R0                      ; 502C   02B8 0047

        JSR     R5,     X_FILL_ZERO             ; 502E   0004 0114 0338

        MVII    #$0102, R4                      ; 5031   02BC 0102
        MVII    #$00EE, R0                      ; 5033   02B8 00EE

        JSR     R5,     X_FILL_ZERO             ; 5035   0004 0114 0338

        SDBD                                    ; 5038   0001
        MVII    #$5C4C, R0                      ; 5039   02B8 004C 005C
        MVO     R0,     G_035D                  ; 503C   0240 035D
        MVII    #$0001, R0                      ; 503E   02B8 0001
        MVO     R0,     G_0147                  ; 5040   0240 0147
        MVII    #$0002, R0                      ; 5042   02B8 0002
        MVO     R0,     G_0116                  ; 5044   0240 0116
        MVO     R0,     G_010E                  ; 5046   0240 010E
        MVO     R0,     G_0119                  ; 5048   0240 0119
        SDBD                                    ; 504A   0001
        MVII    #$FFFF, R0                      ; 504B   02B8 00FF 00FF
        MVO     R0,     G_035E                  ; 504E   0240 035E
        MVII    #$0008, R2                      ; 5050   02BA 0008
        SWAP    R2,     1                       ; 5052   0042
        MVII    #$0008, R1                      ; 5053   02B9 0008
        SDBD                                    ; 5055   0001
        MVII    #$5555, R4                      ; 5056   02BC 0055 0055
        MVII    #$0335, R5                      ; 5059   02BD 0335
L_505B:
        MVI@    R4,     R0                      ; 505B   02A0
        XORR    R2,     R0                      ; 505C   01D0
        MVO@    R0,     R5                      ; 505D   0268
        DECR    R1                              ; 505E   0011
        BNEQ    L_505B                          ; 505F   022C 0005

        MVII    #$016F, R4                      ; 5061   02BC 016F
        MVII    #$0003, R2                      ; 5063   02BA 0003
L_5065:
        MVO@    R0,     R4                      ; 5065   0260
        DECR    R2                              ; 5066   0012
        BNEQ    L_5065                          ; 5067   022C 0003

        EIS                                     ; 5069   0002
L_506A:
        MVI     G_0119, R0                      ; 506A   0280 0119
        TSTR    R0                              ; 506C   0080
        BNEQ    L_506A                          ; 506D   022C 0004

        JSR     R5,     L_5627                  ; 506F   0004 0154 0227
L_5072:
        JSR     R5,     L_5086                  ; 5072   0004 0150 0086
        JSR     R5,     L_50BD                  ; 5075   0004 0150 00BD
        JSR     R5,     L_50E2                  ; 5078   0004 0150 00E2
        JSR     R5,     L_5143                  ; 507B   0004 0150 0143
        JSR     R5,     .EXEC.4F1               ; 507E   0004 0114 00F1
        JSR     R5,     .EXEC.AAD               ; 5081   0004 0118 02AD

        B       L_5072                          ; 5084   0220 0013

L_5086:
        PSHR    R5                              ; 5086   0275
        MVI     G_0118, R0                      ; 5087   0280 0118
        TSTR    R0                              ; 5089   0080
        BNEQ    L_50BC                          ; 508A   020C 0030

        JSR     R5,     L_5D08                  ; 508C   0004 015C 0108

        MVII    #$0003, R0                      ; 508F   02B8 0003
        MVO     R0,     G_0118                  ; 5091   0240 0118
        SDBD                                    ; 5093   0001
        MVII    #$5566, R4                      ; 5094   02BC 0066 0055
        MVII    #$0163, R3                      ; 5097   02BB 0163
L_5099:
        MVI@    R3,     R0                      ; 5099   0298

        JSR     R5,     X_EXT_SIGN_LO           ; 509A   0004 0114 0268

        TSTR    R0                              ; 509D   0080
        BMI     L_50B3                          ; 509E   020B 0013
        BEQ     L_50A5                          ; 50A0   0204 0003

        DECR    R0                              ; 50A2   0010
        BNEQ    L_50B3                          ; 50A3   020C 000E

L_50A5:
        MVI@    R4,     R0                      ; 50A5   02A0
        MVO@    R0,     R3                      ; 50A6   0258
        PSHR    R4                              ; 50A7   0274
        PSHR    R3                              ; 50A8   0273
        SDBD                                    ; 50A9   0001
        MVII    #$50AF, R5                      ; 50AA   02BD 00AF 0050
        SDBD                                    ; 50AD   0001
        MVI@    R4,     R7                      ; 50AE   02A7

        PULR    R3                              ; 50AF   02B3
        PULR    R4                              ; 50B0   02B4
        B       L_50B5                          ; 50B1   0200 0002

L_50B3:
        MVO@    R0,     R3                      ; 50B3   0258
        INCR    R4                              ; 50B4   000C
L_50B5:
        INCR    R3                              ; 50B5   000B
        ADDI    #$0002, R4                      ; 50B6   02FC 0002
        CMPI    #$0167, R3                      ; 50B8   037B 0167
        BLT     L_5099                          ; 50BA   0225 0022
L_50BC:
        PULR    R7                              ; 50BC   02B7

L_50BD:
        PSHR    R5                              ; 50BD   0275
        CLRR    R1                              ; 50BE   01C9
        DIS                                     ; 50BF   0003
        MVI     G_0117, R2                      ; 50C0   0282 0117
        MVO     R1,     G_0117                  ; 50C2   0241 0117
        EIS                                     ; 50C4   0002
        MVII    #$033D, R3                      ; 50C5   02BB 033D
L_50C7:
        RRC     R2,     1                       ; 50C7   0072
        BNC     L_50DC                          ; 50C8   0209 0012

        MVI@    R3,     R4                      ; 50CA   029C
        TSTR    R4                              ; 50CB   00A4
        BEQ     L_50DC                          ; 50CC   0204 000E

        ADDI    #$0000, R4                      ; 50CE   02FC 0000
        SDBD                                    ; 50D0   0001
        MVII    #$50DA, R5                      ; 50D1   02BD 00DA 0050
        PSHR    R2                              ; 50D4   0272
        PSHR    R3                              ; 50D5   0273
        SUBI    #$033D, R3                      ; 50D6   033B 033D
        SDBD                                    ; 50D8   0001
        MVI@    R4,     R7                      ; 50D9   02A7

        PULR    R3                              ; 50DA   02B3
        PULR    R2                              ; 50DB   02B2
L_50DC:
        INCR    R3                              ; 50DC   000B
        CMPI    #$0344, R3                      ; 50DD   037B 0344
        BLE     L_50C7                          ; 50DF   0226 0019
        PULR    R7                              ; 50E1   02B7

L_50E2:
        PSHR    R5                              ; 50E2   0275
        MVII    #$0355, R3                      ; 50E3   02BB 0355
        MVII    #$0325, R2                      ; 50E5   02BA 0325
L_50E7:
        CLRR    R5                              ; 50E7   01ED
        MVI@    R2,     R0                      ; 50E8   0290
        ANDI    #$0100, R0                      ; 50E9   03B8 0100
        BNEQ    L_50EE                          ; 50EB   020C 0001

        INCR    R5                              ; 50ED   000D
L_50EE:
        ADDI    #$0018, R2                      ; 50EE   02FA 0018
        MVI@    R2,     R4                      ; 50F0   0294
        TSTR    R4                              ; 50F1   00A4
        BNEQ    L_50F5                          ; 50F2   020C 0001

        INCR    R5                              ; 50F4   000D
L_50F5:
        CLRR    R1                              ; 50F5   01C9
        MVII    #$03FF, R0                      ; 50F6   02B8 03FF
        DIS                                     ; 50F8   0003
        AND@    R3,     R0                      ; 50F9   0398
        MVO@    R1,     R3                      ; 50FA   0259
        EIS                                     ; 50FB   0002
        TSTR    R5                              ; 50FC   00AD
        BNEQ    L_513B                          ; 50FD   020C 003C

        ADDI    #$0005, R4                      ; 50FF   02FC 0005
        MVI@    R4,     R1                      ; 5101   02A1
        ANDR    R1,     R0                      ; 5102   0188
        BEQ     L_513B                          ; 5103   0204 0036

        MVII    #$000A, R5                      ; 5105   02BD 000A
L_5107:
        SARC    R0,     1                       ; 5107   0078
        BNC     L_5133                          ; 5108   0209 0029

        SLR     R1,     1                       ; 510A   0061
        PSHR    R5                              ; 510B   0275
        PSHR    R4                              ; 510C   0274
        PSHR    R3                              ; 510D   0273
        NOP                                     ; 510E   0034
        PSHR    R2                              ; 510F   0272
        PSHR    R1                              ; 5110   0271
        PSHR    R0                              ; 5111   0270
        SUBI    #$033D, R2                      ; 5112   033A 033D
        NEGR    R5                              ; 5114   0025
        MOVR    R5,     R1                      ; 5115   00A9
        ADDI    #$000A, R1                      ; 5116   02F9 000A
        CMPI    #$0007, R1                      ; 5118   0379 0007
        BGT     L_5125                          ; 511A   020E 0009

        ADDI    #$0325, R1                      ; 511C   02F9 0325
        MVI@    R1,     R0                      ; 511E   0288
        ANDI    #$0100, R0                      ; 511F   03B8 0100
        BEQ     L_512B                          ; 5121   0204 0008

        SUBI    #$0325, R1                      ; 5123   0339 0325
L_5125:
        SDBD                                    ; 5125   0001
        MVII    #$512B, R5                      ; 5126   02BD 002B 0051
        SDBD                                    ; 5129   0001
        MVI@    R4,     R7                      ; 512A   02A7

L_512B:
        PULR    R0                              ; 512B   02B0
        PULR    R1                              ; 512C   02B1
        PULR    R2                              ; 512D   02B2
        PULR    R3                              ; 512E   02B3
        PULR    R4                              ; 512F   02B4
        PULR    R5                              ; 5130   02B5
        B       L_5136                          ; 5131   0200 0003

L_5133:
        SARC    R1,     1                       ; 5133   0079
        BNC     L_5138                          ; 5134   0209 0002

L_5136:
        ADDI    #$0002, R4                      ; 5136   02FC 0002
L_5138:
        DECR    R5                              ; 5138   0015
        BNEQ    L_5107                          ; 5139   022C 0033

L_513B:
        SUBI    #$0017, R2                      ; 513B   033A 0017
        INCR    R3                              ; 513D   000B
        CMPI    #$035D, R3                      ; 513E   037B 035D
        BLT     L_50E7                          ; 5140   0225 005A
        PULR    R7                              ; 5142   02B7

L_5143:
        PSHR    R5                              ; 5143   0275
        MVI     G_011A, R0                      ; 5144   0280 011A
        RRC     R0,     1                       ; 5146   0070
        BC      L_5159                          ; 5147   0201 0010

        SETC                                    ; 5149   0007
        RLC     R0,     1                       ; 514A   0050
        MVO     R0,     G_011A                  ; 514B   0240 011A
        MVII    #$0345, R2                      ; 514D   02BA 0345
        MVII    #$033D, R4                      ; 514F   02BC 033D
        MVII    #$0004, R1                      ; 5151   02B9 0004
        MVII    #$0008, R0                      ; 5153   02B8 0008

        JSR     R5,     L_516F                  ; 5155   0004 0150 016F

        PULR    R7                              ; 5158   02B7

L_5159:
        RRC     R0,     1                       ; 5159   0070
        BC      L_516E                          ; 515A   0201 0012

        MVII    #$0003, R0                      ; 515C   02B8 0003
        MVO     R0,     G_011A                  ; 515E   0240 011A
        MVII    #$02F1, R2                      ; 5160   02BA 02F1
        MVII    #$015D, R4                      ; 5162   02BC 015D
        MVII    #$0002, R1                      ; 5164   02B9 0002
        MVII    #$0003, R0                      ; 5166   02B8 0003
        TSTR    R0                              ; 5168   0080
        BEQ     L_516E                          ; 5169   0204 0003

        JSR     R5,     L_516F                  ; 516B   0004 0150 016F

L_516E:
        PULR    R7                              ; 516E   02B7

L_516F:
        PSHR    R5                              ; 516F   0275
L_5170:
        MVI@    R2,     R3                      ; 5170   0293
        DECLE   $0272,  $037A,  $02F8,  $0206   ; 5171   0272 037A 02F8 0206
        DECLE   $0001,  $000F,  $0001           ; 5175   0001 000F 0001

        MVI@    R4,     R2                      ; 5178   02A2
        TSTR    R2                              ; 5179   0092
        BEQ     L_5185                          ; 517A   0204 0009

        ADDR    R1,     R2                      ; 517C   00CA
        MVI@    R2,     R2                      ; 517D   0292
        PSHR    R0                              ; 517E   0270
        PSHR    R1                              ; 517F   0271

        JSR     R5,     L_518C                  ; 5180   0004 0150 018C

        PULR    R1                              ; 5183   02B1
        PULR    R0                              ; 5184   02B0
L_5185:
        PULR    R2                              ; 5185   02B2
        MVO@    R3,     R2                      ; 5186   0253
        INCR    R2                              ; 5187   000A
        DECR    R0                              ; 5188   0010
        BNEQ    L_5170                          ; 5189   022C 001A
        PULR    R7                              ; 518B   02B7

L_518C:
        PSHR    R5                              ; 518C   0275
        DECR    R2                              ; 518D   0012
        MOVR    R3,     R1                      ; 518E   0099
        ANDI    #$000F, R1                      ; 518F   03B9 000F
        MOVR    R3,     R0                      ; 5191   0098
        SWAP    R0,     1                       ; 5192   0040
        ANDI    #$003E, R0                      ; 5193   03B8 003E
        SLR     R0,     1                       ; 5195   0060
        TSTR    R0                              ; 5196   0080
        BEQ     L_51AA                          ; 5197   0204 0011

        DECR    R0                              ; 5199   0010
        BNEQ    L_51AF                          ; 519A   020C 0013

        TSTR    R3                              ; 519C   009B
        BPL     L_51A1                          ; 519D   0203 0002

        DECR    R1                              ; 519F   0011
        INCR    R7                              ; 51A0   000F

L_51A1:
        INCR    R1                              ; 51A1   0009
L_51A2:
        TSTR    R1                              ; 51A2   0089
        BMI     L_51A9                          ; 51A3   020B 0004

        CMPR    R2,     R1                      ; 51A5   0151
        BLE     L_51AA                          ; 51A6   0206 0002

        CLRR    R2                              ; 51A8   01D2
L_51A9:
        MOVR    R2,     R1                      ; 51A9   0091
L_51AA:
        MOVR    R3,     R0                      ; 51AA   0098
        ANDI    #$01F0, R0                      ; 51AB   03B8 01F0
        SLR     R0,     2                       ; 51AD   0064
        SLR     R0,     2                       ; 51AE   0064
L_51AF:
        SDBD                                    ; 51AF   0001
        ANDI    #$81F0, R3                      ; 51B0   03BB 00F0 0081
        SWAP    R0,     1                       ; 51B3   0040
        SLL     R0,     1                       ; 51B4   0048
        XORR    R0,     R3                      ; 51B5   01C3
        XORR    R1,     R3                      ; 51B6   01CB
        PULR    R7                              ; 51B7   02B7

L_51B8:
        MVI     .STIC.BORD,R0                   ; 51B8   0280 002C
        MVO     R0,     G_0174                  ; 51BA   0240 0174
        MVO     R1,     .STIC.BORD              ; 51BC   0241 002C
        MVII    #$0081, R1                      ; 51BE   02B9 0081
        MVO     R1,     G_0102                  ; 51C0   0241 0102
        PULR    R7                              ; 51C2   02B7

        PSHR    R5                              ; 51C3   0275
        MVI     G_0103, R0                      ; 51C4   0280 0103
        TSTR    R0                              ; 51C6   0080
        BEQ     L_51CC                          ; 51C7   0204 0003

        MVO     R0,     .STIC.VIDEN             ; 51C9   0240 0020
L_51CB:
        PULR    R7                              ; 51CB   02B7

L_51CC:
        MVI     G_0102, R1                      ; 51CC   0281 0102
        SUBI    #$0080, R1                      ; 51CE   0339 0080
        BMI     L_51DD                          ; 51D0   020B 000B
        BEQ     L_51B8                          ; 51D2   0224 001B

        DECR    R1                              ; 51D4   0011
        BEQ     L_51CB                          ; 51D5   0224 000B

        MVI     G_0174, R1                      ; 51D7   0281 0174
        MVO     R1,     .STIC.BORD              ; 51D9   0241 002C
        MVO     R0,     G_0102                  ; 51DB   0240 0102
L_51DD:
        MVO     R0,     .STIC.VIDEN             ; 51DD   0240 0020
        INCR    R0                              ; 51DF   0008
        MVO     R0,     G_0103                  ; 51E0   0240 0103

        JSR     R5,     L_535A                  ; 51E2   0004 0150 035A

        MVII    #$0355, R3                      ; 51E5   02BB 0355
        MVII    #$0018, R2                      ; 51E7   02BA 0018
        CLRR    R5                              ; 51E9   01ED
        MVII    #$0008, R4                      ; 51EA   02BC 0008
L_51EC:
        MVI@    R2,     R0                      ; 51EC   0290
        MVO@    R5,     R2                      ; 51ED   0255
        MVI@    R3,     R1                      ; 51EE   0299
        COMR    R0                              ; 51EF   0018
        ANDR    R0,     R1                      ; 51F0   0181
        COMR    R0                              ; 51F1   0018
        XORR    R0,     R1                      ; 51F2   01C1
        MVO@    R1,     R3                      ; 51F3   0259
        INCR    R2                              ; 51F4   000A
        INCR    R3                              ; 51F5   000B
        DECR    R4                              ; 51F6   0014
        BNEQ    L_51EC                          ; 51F7   022C 000C

        MVI     G_0106, R0                      ; 51F9   0280 0106
        MVO     R0,     .STIC.HDLY              ; 51FB   0240 0030
        MVI     G_010A, R0                      ; 51FD   0280 010A
        MVO     R0,     .STIC.VDLY              ; 51FF   0240 0031
        MVI     G_0104, R2                      ; 5201   0282 0104
        SLL     R2,     1                       ; 5203   004A
        MVII    #$0345, R4                      ; 5204   02BC 0345
        MVII    #$033D, R5                      ; 5206   02BD 033D
        ADDR    R2,     R4                      ; 5208   00D4
        ADDR    R2,     R5                      ; 5209   00D5
L_520A:
        MVI@    R4,     R3                      ; 520A   02A3
        ANDI    #$000F, R3                      ; 520B   03BB 000F
        PSHR    R4                              ; 520D   0274
        MVI@    R5,     R4                      ; 520E   02AC
        TSTR    R4                              ; 520F   00A4
        BEQ     L_526A                          ; 5210   0204 0058

        MVII    #$0167, R1                      ; 5212   02B9 0167
        ADDR    R2,     R1                      ; 5214   00D1
        CMP@    R1,     R3                      ; 5215   034B
        BEQ     L_526A                          ; 5216   0204 0052

        MVO@    R3,     R1                      ; 5218   024B
        PSHR    R5                              ; 5219   0275
        MVII    #$0325, R1                      ; 521A   02B9 0325
        ADDR    R2,     R1                      ; 521C   00D1
        MVI@    R1,     R0                      ; 521D   0288
        PSHR    R1                              ; 521E   0271
        MOVR    R0,     R1                      ; 521F   0081
        SDBD                                    ; 5220   0001
        ANDI    #$FDFF, R0                      ; 5221   03B8 00FF 00FD
        SDBD                                    ; 5224   0001
        ANDI    #$0800, R1                      ; 5225   03B9 0000 0008
        SLR     R1,     2                       ; 5228   0065
        XORR    R1,     R0                      ; 5229   01C8
        PULR    R1                              ; 522A   02B1
        MVO@    R0,     R1                      ; 522B   0248
        ADDI    #$0002, R4                      ; 522C   02FC 0002
        SDBD                                    ; 522E   0001
        MVII    #$5555, R5                      ; 522F   02BD 0055 0055
        ADDR    R2,     R5                      ; 5232   00D5
        MVI@    R5,     R5                      ; 5233   02AD
        SDBD                                    ; 5234   0001
        ADDI    #$3800, R5                      ; 5235   02FD 0000 0038
        MVII    #$032D, R1                      ; 5238   02B9 032D
        ADDR    R2,     R1                      ; 523A   00D1
        MVI@    R1,     R0                      ; 523B   0288
        SLL     R3,     2                       ; 523C   004F
        SLL     R3,     1                       ; 523D   004B
        SDBD                                    ; 523E   0001
        MVI@    R4,     R1                      ; 523F   02A1
        MOVR    R1,     R4                      ; 5240   008C
        ANDI    #$0080, R0                      ; 5241   03B8 0080
        BEQ     L_5258                          ; 5243   0204 0013

        SLL     R3,     1                       ; 5245   004B
        ADDR    R3,     R4                      ; 5246   00DC
        MVI@    R4,     R0                      ; 5247   02A0
        MVO@    R0,     R5                      ; 5248   0268
        MVI@    R4,     R0                      ; 5249   02A0
        MVO@    R0,     R5                      ; 524A   0268
        MVI@    R4,     R0                      ; 524B   02A0
        MVO@    R0,     R5                      ; 524C   0268
        MVI@    R4,     R0                      ; 524D   02A0
        MVO@    R0,     R5                      ; 524E   0268
        MVI@    R4,     R0                      ; 524F   02A0
        MVO@    R0,     R5                      ; 5250   0268
        MVI@    R4,     R0                      ; 5251   02A0
        MVO@    R0,     R5                      ; 5252   0268
        MVI@    R4,     R0                      ; 5253   02A0
        MVO@    R0,     R5                      ; 5254   0268
        MVI@    R4,     R0                      ; 5255   02A0
        MVO@    R0,     R5                      ; 5256   0268
        INCR    R7                              ; 5257   000F

L_5258:
        ADDR    R3,     R4                      ; 5258   00DC
L_5259:
        MVI@    R4,     R0                      ; 5259   02A0
        MVO@    R0,     R5                      ; 525A   0268
        MVI@    R4,     R0                      ; 525B   02A0
        MVO@    R0,     R5                      ; 525C   0268
        MVI@    R4,     R0                      ; 525D   02A0
        MVO@    R0,     R5                      ; 525E   0268
        MVI@    R4,     R0                      ; 525F   02A0
        MVO@    R0,     R5                      ; 5260   0268
        MVI@    R4,     R0                      ; 5261   02A0
        MVO@    R0,     R5                      ; 5262   0268
        MVI@    R4,     R0                      ; 5263   02A0
        MVO@    R0,     R5                      ; 5264   0268
        MVI@    R4,     R0                      ; 5265   02A0
        MVO@    R0,     R5                      ; 5266   0268
        MVI@    R4,     R0                      ; 5267   02A0
        MVO@    R0,     R5                      ; 5268   0268
        PULR    R5                              ; 5269   02B5
L_526A:
        PULR    R4                              ; 526A   02B4
        INCR    R2                              ; 526B   000A
        MOVR    R2,     R0                      ; 526C   0090
        SARC    R0,     1                       ; 526D   0078
        BC      L_520A                          ; 526E   0221 0065

        MVI     G_0104, R2                      ; 5270   0282 0104
        SLL     R2,     1                       ; 5272   004A
        MVII    #$02F1, R4                      ; 5273   02BC 02F1
        MVII    #$015D, R5                      ; 5275   02BD 015D
        ADDR    R2,     R4                      ; 5277   00D4
        SLL     R2,     1                       ; 5278   004A
        ADDR    R2,     R5                      ; 5279   00D5
        SLR     R2,     1                       ; 527A   0062
L_527B:
        MOVR    R2,     R1                      ; 527B   0091
        INCR    R1                              ; 527C   0009
        CMPI    #$0003, R1                      ; 527D   0379 0003
        BGT     L_52B3                          ; 527F   020E 0032

        MVI@    R4,     R3                      ; 5281   02A3
        ANDI    #$000F, R3                      ; 5282   03BB 000F
        PSHR    R4                              ; 5284   0274
        SDBD                                    ; 5285   0001
        MVI@    R5,     R4                      ; 5286   02AC
        PSHR    R5                              ; 5287   0275
        MVII    #$016F, R1                      ; 5288   02B9 016F
        ADDR    R2,     R1                      ; 528A   00D1
        CMP@    R1,     R3                      ; 528B   034B
        BEQ     L_52AC                          ; 528C   0204 001E

        MVO@    R3,     R1                      ; 528E   024B
        SLL     R3,     2                       ; 528F   004F
        SLL     R3,     1                       ; 5290   004B
        SDBD                                    ; 5291   0001
        ADD@    R4,     R3                      ; 5292   02E3
        MOVR    R3,     R4                      ; 5293   009C
        MOVR    R2,     R1                      ; 5294   0091
        SLL     R1,     2                       ; 5295   004D
        SLL     R1,     1                       ; 5296   0049
        SDBD                                    ; 5297   0001
        ADDI    #$3800, R1                      ; 5298   02F9 0000 0038
        MOVR    R1,     R5                      ; 529B   008D
        MVI@    R4,     R0                      ; 529C   02A0
        MVO@    R0,     R5                      ; 529D   0268
        MVI@    R4,     R0                      ; 529E   02A0
        MVO@    R0,     R5                      ; 529F   0268
        MVI@    R4,     R0                      ; 52A0   02A0
        MVO@    R0,     R5                      ; 52A1   0268
        MVI@    R4,     R0                      ; 52A2   02A0
        MVO@    R0,     R5                      ; 52A3   0268
        MVI@    R4,     R0                      ; 52A4   02A0
        MVO@    R0,     R5                      ; 52A5   0268
        MVI@    R4,     R0                      ; 52A6   02A0
        MVO@    R0,     R5                      ; 52A7   0268
        MVI@    R4,     R0                      ; 52A8   02A0
        MVO@    R0,     R5                      ; 52A9   0268
        MVI@    R4,     R0                      ; 52AA   02A0
        MVO@    R0,     R5                      ; 52AB   0268
L_52AC:
        PULR    R5                              ; 52AC   02B5
        PULR    R4                              ; 52AD   02B4
        INCR    R2                              ; 52AE   000A
        MOVR    R2,     R0                      ; 52AF   0090
        SARC    R0,     1                       ; 52B0   0078
        BC      L_527B                          ; 52B1   0221 0037

L_52B3:
        JSR     R5,     L_5400                  ; 52B3   0004 0154 0000

        CLRR    R2                              ; 52B6   01D2
        MVI     G_0104, R1                      ; 52B7   0281 0104
        RRC     R1,     1                       ; 52B9   0071
        BC      L_52C2                          ; 52BA   0201 0006

        MVI     G_0109, R0                      ; 52BC   0280 0109

        JSR     R5,     X_EXT_SIGN_LO           ; 52BE   0004 0114 0268

        MOVR    R0,     R2                      ; 52C1   0082
L_52C2:
        MVII    #$00FF, R0                      ; 52C2   02B8 00FF
        MVII    #$0325, R3                      ; 52C4   02BB 0325
        MVII    #$0125, R4                      ; 52C6   02BC 0125

        JSR     R5,     L_5323                  ; 52C8   0004 0150 0323

        CLRR    R2                              ; 52CB   01D2
        MVI     G_0104, R1                      ; 52CC   0281 0104
        RRC     R1,     1                       ; 52CE   0071
        BNC     L_52D7                          ; 52CF   0209 0006

        MVI     G_010D, R0                      ; 52D1   0280 010D

        JSR     R5,     X_EXT_SIGN_LO           ; 52D3   0004 0114 0268

        MOVR    R0,     R2                      ; 52D6   0082
L_52D7:
        MVII    #$007F, R0                      ; 52D7   02B8 007F
        MVII    #$032D, R3                      ; 52D9   02BB 032D
        MVII    #$0135, R4                      ; 52DB   02BC 0135

        JSR     R5,     L_5323                  ; 52DD   0004 0150 0323

        MVII    #$0100, R4                      ; 52E0   02BC 0100
        SDBD                                    ; 52E2   0001
        MVI@    R4,     R0                      ; 52E3   02A0
        SDBD                                    ; 52E4   0001
        CMPI    #$544A, R0                      ; 52E5   0378 004A 0054
        BNEQ    L_52ED                          ; 52E8   020C 0003

        JSR     R5,     L_5492                  ; 52EA   0004 0154 0092
L_52ED:
        JSR     R5,     X_PLAY_NOTE             ; 52ED   0004 0118 02BD

        CLRR    R1                              ; 52F0   01C9
        MVII    #$034D, R3                      ; 52F1   02BB 034D
L_52F3:
        CLRC                                    ; 52F3   0006
        MVI@    R3,     R0                      ; 52F4   0298
        TSTR    R0                              ; 52F5   0080
        BEQ     L_52FC                          ; 52F6   0204 0004

        DECR    R0                              ; 52F8   0010
        BNEQ    L_52FC                          ; 52F9   020C 0001

        SETC                                    ; 52FB   0007
L_52FC:
        RRC     R1,     1                       ; 52FC   0071
        MVO@    R0,     R3                      ; 52FD   0258
        INCR    R3                              ; 52FE   000B
        CMPI    #$0354, R3                      ; 52FF   037B 0354
        BLE     L_52F3                          ; 5301   0226 000F

        SWAP    R1,     1                       ; 5303   0041
        MVI     G_0117, R0                      ; 5304   0280 0117
        COMR    R0                              ; 5306   0018
        ANDR    R0,     R1                      ; 5307   0181
        COMR    R0                              ; 5308   0018
        XORR    R0,     R1                      ; 5309   01C1
        MVO     R1,     G_0117                  ; 530A   0241 0117
        MVI     G_0118, R0                      ; 530C   0280 0118
        TSTR    R0                              ; 530E   0080
        BEQ     L_5318                          ; 530F   0204 0007

        AND     G_011A, R0                      ; 5311   0380 011A
        MVO     R0,     G_011A                  ; 5313   0240 011A
        DECR    R0                              ; 5315   0010
        MVO     R0,     G_0118                  ; 5316   0240 0118
L_5318:
        MVI     G_0104, R0                      ; 5318   0280 0104
        INCR    R0                              ; 531A   0008
        ANDI    #$0003, R0                      ; 531B   03B8 0003
        MVO     R0,     G_0104                  ; 531D   0240 0104
        CLRR    R0                              ; 531F   01C0
        MVO     R0,     G_0103                  ; 5320   0240 0103
        PULR    R7                              ; 5322   02B7

L_5323:
        PSHR    R5                              ; 5323   0275
        MVII    #$0008, R5                      ; 5324   02BD 0008
L_5326:
        PSHR    R5                              ; 5326   0275
        MVI@    R3,     R1                      ; 5327   0299
        SDBD                                    ; 5328   0001
        MVII    #$4000, R5                      ; 5329   02BD 0000 0040
        ANDR    R1,     R5                      ; 532C   018D
        BEQ     L_5334                          ; 532D   0204 0005

        JSR     R5,     L_5378                  ; 532F   0004 0150 0378

        B       L_5354                          ; 5332   0200 0020

L_5334:
        PSHR    R2                              ; 5334   0272
        ANDR    R0,     R1                      ; 5335   0181
        PSHR    R0                              ; 5336   0270
        SWAP    R1,     1                       ; 5337   0041
        PSHR    R4                              ; 5338   0274
        XOR@    R4,     R1                      ; 5339   03E1
        MVI@    R4,     R0                      ; 533A   02A0

        JSR     R5,     X_EXT_SIGN_LO           ; 533B   0004 0114 0268

        MVI     G_0116, R2                      ; 533E   0282 0116

        JSR     R5,     L_5546                  ; 5340   0004 0154 0146

        ADDR    R0,     R1                      ; 5343   00C1
        PULR    R2                              ; 5344   02B2
        MVO@    R1,     R2                      ; 5345   0251
        SWAP    R1,     1                       ; 5346   0041
        PULR    R0                              ; 5347   02B0
        ANDR    R0,     R1                      ; 5348   0181
        MOVR    R0,     R2                      ; 5349   0082
        COMR    R2                              ; 534A   001A
        PULR    R5                              ; 534B   02B5
        AND@    R3,     R2                      ; 534C   039A
        BMI     L_5351                          ; 534D   020B 0002

        SUBR    R5,     R1                      ; 534F   0129
        ANDR    R0,     R1                      ; 5350   0181
L_5351:
        XORR    R2,     R1                      ; 5351   01D1
        MVO@    R1,     R3                      ; 5352   0259
        MOVR    R5,     R2                      ; 5353   00AA
L_5354:
        INCR    R3                              ; 5354   000B
        PULR    R5                              ; 5355   02B5
        DECR    R5                              ; 5356   0015
        BNEQ    L_5326                          ; 5357   022C 0032
        PULR    R7                              ; 5359   02B7

L_535A:
        MVII    #$0001, R1                      ; 535A   02B9 0001
        INCR    R7                              ; 535C   000F

        CLRR    R1                              ; 535D   01C9
L_535E:
        PSHR    R5                              ; 535E   0275
        MVII    #$0325, R4                      ; 535F   02BC 0325
        CLRR    R5                              ; 5361   01ED
        ADDI    #$0002, R1                      ; 5362   02F9 0002
L_5364:
        MVI@    R4,     R0                      ; 5364   02A0
        MVO@    R0,     R5                      ; 5365   0268
        MVI@    R4,     R0                      ; 5366   02A0
        MVO@    R0,     R5                      ; 5367   0268
        MVI@    R4,     R0                      ; 5368   02A0
        MVO@    R0,     R5                      ; 5369   0268
        MVI@    R4,     R0                      ; 536A   02A0
        MVO@    R0,     R5                      ; 536B   0268
        MVI@    R4,     R0                      ; 536C   02A0
        MVO@    R0,     R5                      ; 536D   0268
        MVI@    R4,     R0                      ; 536E   02A0
        MVO@    R0,     R5                      ; 536F   0268
        MVI@    R4,     R0                      ; 5370   02A0
        MVO@    R0,     R5                      ; 5371   0268
        MVI@    R4,     R0                      ; 5372   02A0
        MVO@    R0,     R5                      ; 5373   0268
        DECR    R1                              ; 5374   0011
        BNEQ    L_5364                          ; 5375   022C 0012
        PULR    R7                              ; 5377   02B7

L_5378:
        PSHR    R5                              ; 5378   0275
        PSHR    R0                              ; 5379   0270
        MOVR    R0,     R5                      ; 537A   0085
        DECR    R3                              ; 537B   0013
        MVI@    R3,     R1                      ; 537C   0299
        ANDR    R0,     R1                      ; 537D   0181
        INCR    R3                              ; 537E   000B
        INCR    R4                              ; 537F   000C
        MVI@    R4,     R0                      ; 5380   02A0
        PSHR    R5                              ; 5381   0275

        JSR     R5,     X_EXT_SIGN_LO           ; 5382   0004 0114 0268

        PULR    R5                              ; 5385   02B5
        ADDR    R0,     R1                      ; 5386   00C1
        ANDR    R5,     R1                      ; 5387   01A9
        COMR    R5                              ; 5388   001D
        AND@    R3,     R5                      ; 5389   039D
        XORR    R5,     R1                      ; 538A   01E9
        MVO@    R1,     R3                      ; 538B   0259
        PULR    R0                              ; 538C   02B0
        PULR    R7                              ; 538D   02B7

        PSHR    R5                              ; 538E   0275
        DIS                                     ; 538F   0003

        JSR     R5,     L_53A8                  ; 5390   0004 0150 03A8

        MVII    #$0020, R0                      ; 5393   02B8 0020
        CLRR    R4                              ; 5395   01E4
        MVO     R4,     G_0119                  ; 5396   0244 0119

        JSR     R5,     X_FILL_ZERO             ; 5398   0004 0114 0338
        JSR     R5,     L_53C8                  ; 539B   0004 0150 03C8

        MVII    #$00C3, R0                      ; 539E   02B8 00C3
        MVO     R0,     .ISRVEC.0               ; 53A0   0240 0100
        MVII    #$0051, R0                      ; 53A2   02B8 0051
        MVO     R0,     .ISRVEC.1               ; 53A4   0240 0101
        EIS                                     ; 53A6   0002
        PULR    R7                              ; 53A7   02B7

L_53A8:
        PSHR    R5                              ; 53A8   0275
        CLRR    R0                              ; 53A9   01C0
        MVO     R0,     .STIC.HDLY              ; 53AA   0240 0030
        MVO     R0,     .STIC.VDLY              ; 53AC   0240 0031
        SDBD                                    ; 53AE   0001
        MVII    #$554E, R4                      ; 53AF   02BC 004E 0055
        MVI@    R4,     R0                      ; 53B2   02A0
        MVO     R0,     G_0105                  ; 53B3   0240 0105
        MVII    #$0021, R1                      ; 53B5   02B9 0021
        TSTR    R0                              ; 53B7   0080
        BEQ     L_53BC                          ; 53B8   0204 0002

        MVO@    R0,     R1                      ; 53BA   0248
        INCR    R7                              ; 53BB   000F

L_53BC:
        MVI@    R1,     R0                      ; 53BC   0288
L_53BD:
        MVII    #$0028, R1                      ; 53BD   02B9 0028
        MVII    #$0005, R0                      ; 53BF   02B8 0005

        JSR     R5,     .EXEC.730               ; 53C1   0004 0114 0330

        MVI@    R4,     R0                      ; 53C4   02A0
        MVO     R0,     .STIC.EDGE              ; 53C5   0240 0032
        PULR    R7                              ; 53C7   02B7

L_53C8:
        PSHR    R5                              ; 53C8   0275
        MVII    #$0003, R0                      ; 53C9   02B8 0003
        MVII    #$02F1, R1                      ; 53CB   02B9 02F1
        SDBD                                    ; 53CD   0001
        MVII    #$555D, R4                      ; 53CE   02BC 005D 0055
        TSTR    R0                              ; 53D1   0080
        BEQ     L_53E2                          ; 53D2   0204 000E

        JSR     R5,     .EXEC.730               ; 53D4   0004 0114 0330

        MVII    #$0003, R0                      ; 53D7   02B8 0003
        MVII    #$015D, R5                      ; 53D9   02BD 015D
L_53DB:
        MVI@    R4,     R1                      ; 53DB   02A1
        MVO@    R1,     R5                      ; 53DC   0269
        MVI@    R4,     R1                      ; 53DD   02A1
        MVO@    R1,     R5                      ; 53DE   0269
        DECR    R0                              ; 53DF   0010
        BNEQ    L_53DB                          ; 53E0   022C 0006

L_53E2:
        SDBD                                    ; 53E2   0001
        MVII    #$61E7, R4                      ; 53E3   02BC 00E7 0061

        JSR     R5,     L_53EA                  ; 53E6   0004 0150 03EA

        PULR    R7                              ; 53E9   02B7

L_53EA:
        PSHR    R5                              ; 53EA   0275
        MVI@    R4,     R5                      ; 53EB   02A5
        SDBD                                    ; 53EC   0001
        ADDI    #$3800, R5                      ; 53ED   02FD 0000 0038
        MVI@    R4,     R0                      ; 53F0   02A0
L_53F1:
        MVI@    R4,     R1                      ; 53F1   02A1
        MOVR    R1,     R2                      ; 53F2   008A
        SWAP    R2,     1                       ; 53F3   0042
        ANDI    #$0003, R2                      ; 53F4   03BA 0003
        ANDI    #$00FF, R1                      ; 53F6   03B9 00FF
L_53F8:
        MVO@    R1,     R5                      ; 53F8   0269
        DECR    R2                              ; 53F9   0012
        BPL     L_53F8                          ; 53FA   0223 0003

        DECR    R0                              ; 53FC   0010
        BNEQ    L_53F1                          ; 53FD   022C 000D
        PULR    R7                              ; 53FF   02B7

L_5400:
        PSHR    R5                              ; 5400   0275
        MVII    #$0106, R4                      ; 5401   02BC 0106
        MVI     G_0104, R2                      ; 5403   0282 0104
        ANDI    #$0001, R2                      ; 5405   03BA 0001
        BEQ     L_540B                          ; 5407   0204 0002

        ADDI    #$0004, R4                      ; 5409   02FC 0004
L_540B:
        MVI@    R4,     R1                      ; 540B   02A1
        SWAP    R1,     1                       ; 540C   0041
        XOR@    R4,     R1                      ; 540D   03E1
        MVI@    R4,     R0                      ; 540E   02A0
        PSHR    R2                              ; 540F   0272

        JSR     R5,     X_EXT_SIGN_LO           ; 5410   0004 0114 0268

        MVI     G_010E, R2                      ; 5413   0282 010E

        JSR     R5,     L_5546                  ; 5415   0004 0154 0146

        PULR    R2                              ; 5418   02B2
        ADDR    R0,     R1                      ; 5419   00C1
        MOVR    R1,     R0                      ; 541A   0088
        SLL     R2,     1                       ; 541B   004A
        SAR     R0,     2                       ; 541C   006C
        SAR     R0,     2                       ; 541D   006C
        SAR     R0,     2                       ; 541E   006C
        SAR     R0,     2                       ; 541F   006C
        BMI     L_5427                          ; 5420   020B 0005

        CMPI    #$0007, R0                      ; 5422   0378 0007
        BLE     L_5440                          ; 5424   0206 001A
        INCR    R7                              ; 5426   000F

L_5427:
        INCR    R2                              ; 5427   000A
L_5428:
        MVO     R2,     G_010F                  ; 5428   0242 010F
        MVI     .ISRVEC.0,R2                    ; 542A   0282 0100
        MVO     R2,     G_0172                  ; 542C   0242 0172
        MVI     .ISRVEC.1,R2                    ; 542E   0282 0101
        MVO     R2,     G_0173                  ; 5430   0242 0173
        SDBD                                    ; 5432   0001
        MVII    #$004A, R2                      ; 5433   02BA 004A 0000
        MVO     R2,     .ISRVEC.0               ; 5436   0242 0100
        SDBD                                    ; 5438   0001
        MVII    #$0054, R2                      ; 5439   02BA 0054 0000
        MVO     R2,     .ISRVEC.1               ; 543C   0242 0101
        ANDI    #$0007, R0                      ; 543E   03B8 0007
L_5440:
        SUBI    #$0003, R4                      ; 5440   033C 0003
        MOVR    R0,     R2                      ; 5442   0082
        SUB@    R4,     R2                      ; 5443   0322
        DECR    R4                              ; 5444   0014
        MVO@    R0,     R4                      ; 5445   0260
        MVO@    R1,     R4                      ; 5446   0261
        INCR    R4                              ; 5447   000C
        MVO@    R2,     R4                      ; 5448   0262
        PULR    R7                              ; 5449   02B7

        PSHR    R5                              ; 544A   0275
        MVO     R0,     .STIC.VIDEN             ; 544B   0240 0020
        MVI     G_0103, R0                      ; 544D   0280 0103
        TSTR    R0                              ; 544F   0080
        BEQ     L_5453                          ; 5450   0204 0001
        PULR    R7                              ; 5452   02B7

L_5453:
        INCR    R0                              ; 5453   0008
        MVO     R0,     G_0103                  ; 5454   0240 0103
        MVI     G_0106, R0                      ; 5456   0280 0106
        MVO     R0,     .STIC.HDLY              ; 5458   0240 0030
        MVI     G_010A, R0                      ; 545A   0280 010A
        MVO     R0,     .STIC.VDLY              ; 545C   0240 0031
        MVII    #$0008, R5                      ; 545E   02BD 0008
        MVII    #$032D, R4                      ; 5460   02BC 032D
        MVI     G_010F, R2                      ; 5462   0282 010F
        RRC     R2,     2                       ; 5464   0076
        BOV     L_5469                          ; 5465   0202 0002

        SUBR    R5,     R4                      ; 5467   012C
        CLRR    R5                              ; 5468   01ED
L_5469:
        MVI@    R4,     R0                      ; 5469   02A0
        MVO@    R0,     R5                      ; 546A   0268
        MVI@    R4,     R0                      ; 546B   02A0
        MVO@    R0,     R5                      ; 546C   0268
        MVI@    R4,     R0                      ; 546D   02A0
        MVO@    R0,     R5                      ; 546E   0268
        MVI@    R4,     R0                      ; 546F   02A0
        MVO@    R0,     R5                      ; 5470   0268
        MVI@    R4,     R0                      ; 5471   02A0
        MVO@    R0,     R5                      ; 5472   0268
        MVI@    R4,     R0                      ; 5473   02A0
        MVO@    R0,     R5                      ; 5474   0268
        MVI@    R4,     R0                      ; 5475   02A0
        MVO@    R0,     R5                      ; 5476   0268
        MVI@    R4,     R0                      ; 5477   02A0
        MVO@    R0,     R5                      ; 5478   0268
        MVI     G_010F, R2                      ; 5479   0282 010F

        JSR     R5,     L_54B9                  ; 547B   0004 0154 00B9
        JSR     R5,     L_5DF3                  ; 547E   0004 015C 01F3
        JSR     R5,     X_PLAY_NOTE             ; 5481   0004 0118 02BD

        DIS                                     ; 5484   0003
        MVI     G_0172, R0                      ; 5485   0280 0172
        MVO     R0,     .ISRVEC.0               ; 5487   0240 0100
        MVI     G_0173, R0                      ; 5489   0280 0173
        MVO     R0,     .ISRVEC.1               ; 548B   0240 0101
        EIS                                     ; 548D   0002
        CLRR    R0                              ; 548E   01C0
        MVO     R0,     G_0103                  ; 548F   0240 0103
        PULR    R7                              ; 5491   02B7

L_5492:
        PSHR    R5                              ; 5492   0275
        MVII    #$0008, R5                      ; 5493   02BD 0008
        MVII    #$0325, R3                      ; 5495   02BB 0325
        MVII    #$0008, R0                      ; 5497   02B8 0008
        MVI     G_010F, R1                      ; 5499   0281 010F
        RRC     R1,     1                       ; 549B   0071
        BNC     L_549F                          ; 549C   0209 0001

        NEGR    R0                              ; 549E   0020
L_549F:
        MVII    #$00FF, R2                      ; 549F   02BA 00FF
        RRC     R1,     1                       ; 54A1   0071
        BNC     L_54A7                          ; 54A2   0209 0003

        ADDR    R5,     R3                      ; 54A4   00EB
        MVII    #$007F, R2                      ; 54A5   02BA 007F
L_54A7:
        MVI@    R3,     R4                      ; 54A7   029C
        TSTR    R4                              ; 54A8   00A4
        BPL     L_54B4                          ; 54A9   0203 0009

        COMR    R2                              ; 54AB   001A
        ANDR    R2,     R4                      ; 54AC   0194
        COMR    R2                              ; 54AD   001A
        MVI@    R3,     R1                      ; 54AE   0299
        ANDR    R2,     R1                      ; 54AF   0191
        ADDR    R0,     R1                      ; 54B0   00C1
        ANDR    R2,     R1                      ; 54B1   0191
        XORR    R4,     R1                      ; 54B2   01E1
        MVO@    R1,     R3                      ; 54B3   0259
L_54B4:
        INCR    R3                              ; 54B4   000B
        DECR    R5                              ; 54B5   0015
        BNEQ    L_54A7                          ; 54B6   022C 0010
        PULR    R7                              ; 54B8   02B7

L_54B9:
        PSHR    R5                              ; 54B9   0275
        PSHR    R2                              ; 54BA   0272
        RRC     R2,     1                       ; 54BB   0072
        BC      L_54CB                          ; 54BC   0201 000D

        RRC     R2,     1                       ; 54BE   0072
        BC      L_54C6                          ; 54BF   0201 0005

        JSR     R5,     L_54D8                  ; 54C1   0004 0154 00D8

        B       L_54D6                          ; 54C4   0200 0010

L_54C6:
        JSR     R5,     L_54EF                  ; 54C6   0004 0154 00EF

        B       L_54D6                          ; 54C9   0200 000B

L_54CB:
        RRC     R2,     1                       ; 54CB   0072
        BC      L_54D3                          ; 54CC   0201 0005

        JSR     R5,     L_5526                  ; 54CE   0004 0154 0126

        B       L_54D6                          ; 54D1   0200 0003

L_54D3:
        JSR     R5,     L_5539                  ; 54D3   0004 0154 0139

L_54D6:
        PULR    R2                              ; 54D6   02B2
        PULR    R7                              ; 54D7   02B7

L_54D8:
        PSHR    R5                              ; 54D8   0275
        MVII    #$0213, R3                      ; 54D9   02BB 0213
        MVII    #$0212, R2                      ; 54DB   02BA 0212
L_54DD:
        MVII    #$0013, R1                      ; 54DD   02B9 0013
L_54DF:
        MVI@    R2,     R0                      ; 54DF   0290
        MVO@    R0,     R3                      ; 54E0   0258
        DECR    R3                              ; 54E1   0013
        DECR    R2                              ; 54E2   0012
        DECR    R1                              ; 54E3   0011
        BNEQ    L_54DF                          ; 54E4   022C 0006

        ADDI    #$0027, R3                      ; 54E6   02FB 0027
        ADDI    #$0027, R2                      ; 54E8   02FA 0027
        CMPI    #$02F0, R2                      ; 54EA   037A 02F0
        BLT     L_54DD                          ; 54EC   0225 0010
        PULR    R7                              ; 54EE   02B7

L_54EF:
        PSHR    R5                              ; 54EF   0275
        MVII    #$02C8, R4                      ; 54F0   02BC 02C8
        MVII    #$02DC, R5                      ; 54F2   02BD 02DC
        MVII    #$0028, R1                      ; 54F4   02B9 0028
        MVII    #$000B, R2                      ; 54F6   02BA 000B
L_54F8:
        MVI@    R4,     R0                      ; 54F8   02A0
        MVO@    R0,     R5                      ; 54F9   0268
        MVI@    R4,     R0                      ; 54FA   02A0
        MVO@    R0,     R5                      ; 54FB   0268
        MVI@    R4,     R0                      ; 54FC   02A0
        MVO@    R0,     R5                      ; 54FD   0268
        MVI@    R4,     R0                      ; 54FE   02A0
        MVO@    R0,     R5                      ; 54FF   0268
        MVI@    R4,     R0                      ; 5500   02A0
        MVO@    R0,     R5                      ; 5501   0268
        MVI@    R4,     R0                      ; 5502   02A0
        MVO@    R0,     R5                      ; 5503   0268
        MVI@    R4,     R0                      ; 5504   02A0
        MVO@    R0,     R5                      ; 5505   0268
        MVI@    R4,     R0                      ; 5506   02A0
        MVO@    R0,     R5                      ; 5507   0268
        MVI@    R4,     R0                      ; 5508   02A0
        MVO@    R0,     R5                      ; 5509   0268
        MVI@    R4,     R0                      ; 550A   02A0
        MVO@    R0,     R5                      ; 550B   0268
        MVI@    R4,     R0                      ; 550C   02A0
        MVO@    R0,     R5                      ; 550D   0268
        MVI@    R4,     R0                      ; 550E   02A0
        MVO@    R0,     R5                      ; 550F   0268
        MVI@    R4,     R0                      ; 5510   02A0
        MVO@    R0,     R5                      ; 5511   0268
        MVI@    R4,     R0                      ; 5512   02A0
        MVO@    R0,     R5                      ; 5513   0268
        MVI@    R4,     R0                      ; 5514   02A0
        MVO@    R0,     R5                      ; 5515   0268
        MVI@    R4,     R0                      ; 5516   02A0
        MVO@    R0,     R5                      ; 5517   0268
        MVI@    R4,     R0                      ; 5518   02A0
        MVO@    R0,     R5                      ; 5519   0268
        MVI@    R4,     R0                      ; 551A   02A0
        MVO@    R0,     R5                      ; 551B   0268
        MVI@    R4,     R0                      ; 551C   02A0
        MVO@    R0,     R5                      ; 551D   0268
        MVI@    R4,     R0                      ; 551E   02A0
        MVO@    R0,     R5                      ; 551F   0268
        SUBR    R1,     R4                      ; 5520   010C
        SUBR    R1,     R5                      ; 5521   010D
        DECR    R2                              ; 5522   0012
        BNEQ    L_54F8                          ; 5523   022C 002C
        PULR    R7                              ; 5525   02B7

L_5526:
        PSHR    R5                              ; 5526   0275
        MVII    #$0200, R5                      ; 5527   02BD 0200
        MVII    #$0201, R4                      ; 5529   02BC 0201
L_552B:
        MVII    #$0013, R1                      ; 552B   02B9 0013
L_552D:
        MVI@    R4,     R0                      ; 552D   02A0
        MVO@    R0,     R5                      ; 552E   0268
        DECR    R1                              ; 552F   0011
        BNEQ    L_552D                          ; 5530   022C 0004

        INCR    R4                              ; 5532   000C
        INCR    R5                              ; 5533   000D
        CMPI    #$02DD, R4                      ; 5534   037C 02DD
        BLE     L_552B                          ; 5536   0226 000C
        PULR    R7                              ; 5538   02B7

L_5539:
        PSHR    R5                              ; 5539   0275
        MVII    #$0200, R5                      ; 553A   02BD 0200
        MVII    #$0214, R4                      ; 553C   02BC 0214
        MVII    #$00DC, R1                      ; 553E   02B9 00DC
L_5540:
        MVI@    R4,     R0                      ; 5540   02A0
        MVO@    R0,     R5                      ; 5541   0268
        DECR    R1                              ; 5542   0011
        BNEQ    L_5540                          ; 5543   022C 0004
        PULR    R7                              ; 5545   02B7

L_5546:
        TSTR    R2                              ; 5546   0092
        BEQ     L_554D                          ; 5547   0204 0004

L_5549:
        SLL     R0,     1                       ; 5549   0048
        DECR    R2                              ; 554A   0012
        BNEQ    L_5549                          ; 554B   022C 0003
L_554D:
        MOVR    R5,     R7                      ; 554D   00AF

        DECLE   $0001,  $0000,  $0003,  $0000   ; 554E   0001 0000 0003 0000
        DECLE   $0000,  $0000,  $0003,  $0180   ; 5552   0000 0000 0003 0180
        DECLE   $0190,  $01A0,  $01B0,  $01C0   ; 5556   0190 01A0 01B0 01C0
        DECLE   $01D0,  $01E0,  $01F0,  $0020   ; 555A   01D0 01E0 01F0 0020
        DECLE   $0080,  $0080,  $0072,  $0055   ; 555E   0080 0080 0072 0055
        DECLE   $0075,  $0055,  $0078,  $0055   ; 5562   0075 0055 0078 0055
        DECLE   $0023,  $00FA,  $0069,  $0001   ; 5566   0023 00FA 0069 0001
        DECLE   $0093,  $005F,  $0004,  $0083   ; 556A   0093 005F 0004 0083
        DECLE   $006C,  $0001,  $003D,  $0069   ; 556E   006C 0001 003D 0069
        DECLE   $00B0,  $0062,  $0004,  $00D6   ; 5572   00B0 0062 0004 00D6
        DECLE   $0062,  $0004,  $00F8,  $0062   ; 5576   0062 0004 00F8 0062
        DECLE   $0004                           ; 557A   0004
L_557B:
        PSHR    R5                              ; 557B   0275

        JSR     R5,     L_6076                  ; 557C   0004 0160 0076
        JSR     R5,     L_55BF                  ; 557F   0004 0154 01BF

        MVII    #$0002, R2                      ; 5582   02BA 0002
        MVI     G_018B, R0                      ; 5584   0280 018B
        MVII    #$0001, R1                      ; 5586   02B9 0001
        ANDI    #$0002, R0                      ; 5588   03B8 0002
        BEQ     L_558F                          ; 558A   0204 0003

        ADDI    #$0002, R2                      ; 558C   02FA 0002
        CLRR    R1                              ; 558E   01C9
L_558F:
        MVO     R1,     G_019A                  ; 558F   0241 019A
        MVII    #$0325, R3                      ; 5591   02BB 0325
        SDBD                                    ; 5593   0001
        MVII    #$5A40, R4                      ; 5594   02BC 0040 005A

        JSR     R5,     L_5FC1                  ; 5597   0004 015C 03C1

        MVII    #$0327, R2                      ; 559A   02BA 0327
        CMPR    R2,     R3                      ; 559C   0153
        BEQ     L_55AB                          ; 559D   0204 000C

        MVI@    R2,     R0                      ; 559F   0290
        SDBD                                    ; 55A0   0001
        XORI    #$0958, R0                      ; 55A1   03F8 0058 0009
        MVO@    R0,     R2                      ; 55A4   0250
        MVI     G_032F, R0                      ; 55A5   0280 032F
        XORI    #$0044, R0                      ; 55A7   03F8 0044
        MVO     R0,     G_032F                  ; 55A9   0240 032F

L_55AB:
        JSR     R5,     L_55DB                  ; 55AB   0004 0154 01DB
        JSR     R5,     L_55F7                  ; 55AE   0004 0154 01F7

        MVI     G_018B, R0                      ; 55B1   0280 018B
        MVII    #$0004, R1                      ; 55B3   02B9 0004
        CLRR    R2                              ; 55B5   01D2
        ANDI    #$0002, R0                      ; 55B6   03B8 0002
        BNEQ    L_55BB                          ; 55B8   020C 0001

        DECR    R1                              ; 55BA   0011

L_55BB:
        JSR     R5,     L_5F43                  ; 55BB   0004 015C 0343

        PULR    R7                              ; 55BE   02B7

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
L_5627:
        PSHR    R5                              ; 5627   0275
        MVII    #$0001, R0                      ; 5628   02B8 0001
        MVO     R0,     G_018B                  ; 562A   0240 018B
        DIS                                     ; 562C   0003

        JSR     R5,     L_557B                  ; 562D   0004 0154 017B

        MVII    #$00F0, R0                      ; 5630   02B8 00F0
        SDBD                                    ; 5632   0001
        MVII    #$1603, R1                      ; 5633   02B9 0003 0016
        MVII    #$0200, R4                      ; 5636   02BC 0200

        JSR     R5,     X_FILL_MEM              ; 5638   0004 0114 0341

        MOVR    R1,     R3                      ; 563B   008B
        MVII    #$022A, R4                      ; 563C   02BC 022A

        JSR     R5,     X_PRINT_R5              ; 563E   0004 0118 007B
        STRING  "SWORDS & SERPENTS"             ; 5641  
        DECLE   $0000                           ; 5652   0000

        MVII    #$0255, R4                      ; 5653   02BC 0255
        SDBD                                    ; 5655   0001
        MVII    #$1EBB, R0                      ; 5656   02B8 00BB 001E
        MVO@    R0,     R4                      ; 5659   0260

        JSR     R5,     X_PRINT_R5              ; 565A   0004 0118 007B
        STRING  " IMAGIC 1982"                  ; 565D  
        DECLE   $0000                           ; 5669   0000

        MVII    #$02B6, R4                      ; 566A   02BC 02B6

        JSR     R5,     X_PRINT_R5              ; 566C   0004 0118 007B
        STRING  "ENTER GAME (1,2,3)"            ; 566F  
        DECLE   $0000                           ; 5681   0000

        EIS                                     ; 5682   0002
        PULR    R7                              ; 5683   02B7

        PSHR    R5                              ; 5684   0275
        CMPI    #$000A, R0                      ; 5685   0378 000A
        BGT     L_56C9                          ; 5687   020E 0040
        BLT     L_568E                          ; 5689   0205 0003

        CLRR    R0                              ; 568B   01C0
        MVO     R0,     G_018C                  ; 568C   0240 018C
L_568E:
        PSHR    R0                              ; 568E   0270
        MVII    #$0014, R0                      ; 568F   02B8 0014
        SDBD                                    ; 5691   0001
        MVII    #$1603, R1                      ; 5692   02B9 0003 0016
        MVII    #$02DC, R4                      ; 5695   02BC 02DC

        JSR     R5,     X_FILL_MEM              ; 5697   0004 0114 0341

        PULR    R0                              ; 569A   02B0
        MOVR    R1,     R3                      ; 569B   008B
        TSTR    R0                              ; 569C   0080
        BEQ     L_56C8                          ; 569D   0204 0029

        CMPI    #$0003, R0                      ; 569F   0378 0003
        BGT     L_56C8                          ; 56A1   020E 0025

        MVO     R0,     G_018C                  ; 56A3   0240 018C
        BLT     L_56B5                          ; 56A5   0205 000E

        MVII    #$02E7, R4                      ; 56A7   02BC 02E7

        JSR     R5,     X_PRINT_R5              ; 56A9   0004 0118 007B
        STRING  "/MAGIC"                        ; 56AC  
        DECLE   $0000                           ; 56B2   0000

        MVII    #$0002, R0                      ; 56B3   02B8 0002
L_56B5:
        MVII    #$0001, R1                      ; 56B5   02B9 0001
        MVII    #$02DF, R4                      ; 56B7   02BC 02DF

        JSR     R5,     X_PRNUM_RGT             ; 56B9   0004 0118 00C5

        INCR    R4                              ; 56BC   000C

        JSR     R5,     X_PRINT_R5              ; 56BD   0004 0118 007B
        STRING  " PLAYER"                       ; 56C0  
        DECLE   $0000                           ; 56C7   0000
L_56C8:
        PULR    R7                              ; 56C8   02B7

L_56C9:
        MVI     G_018C, R0                      ; 56C9   0280 018C
        TSTR    R0                              ; 56CB   0080
        BEQ     L_56F8                          ; 56CC   0204 002A

        CMPI    #$0003, R0                      ; 56CE   0378 0003
        BLT     L_56DB                          ; 56D0   0205 0009

        MOVR    R0,     R2                      ; 56D2   0082
        MOVR    R0,     R1                      ; 56D3   0081
        DECR    R0                              ; 56D4   0010
        MVII    #$018E, R4                      ; 56D5   02BC 018E
L_56D7:
        MVO@    R2,     R4                      ; 56D7   0262
        DECR    R1                              ; 56D8   0011
        BNEQ    L_56D7                          ; 56D9   022C 0003

L_56DB:
        XORI    #$0080, R0                      ; 56DB   03F8 0080
        MVO     R0,     G_018B                  ; 56DD   0240 018B
        SDBD                                    ; 56DF   0001
        MVII    #$62D0, R0                      ; 56E0   02B8 00D0 0062
        MVO     R0,     G_035D                  ; 56E3   0240 035D

        JSR     R5,     L_5F5B                  ; 56E5   0004 015C 035B

        SDBD                                    ; 56E8   0001
        MVII    #$0980, R0                      ; 56E9   02B8 0080 0009
        MVO     R0,     G_0335                  ; 56EC   0240 0335
        CLRR    R0                              ; 56EE   01C0
        MVO     R0,     G_01A4                  ; 56EF   0240 01A4
        MVO     R0,     G_01AB                  ; 56F1   0240 01AB
        MVO     R0,     G_01A3                  ; 56F3   0240 01A3

        JSR     R5,     L_557B                  ; 56F5   0004 0154 017B

L_56F8:
        PULR    R7                              ; 56F8   02B7

        PSHR    R5                              ; 56F9   0275
        MVI     G_018B, R2                      ; 56FA   0282 018B
        ANDI    #$0002, R2                      ; 56FC   03BA 0002
        BEQ     L_5703                          ; 56FE   0204 0003

        TSTR    R1                              ; 5700   0089
        BEQ     L_5749                          ; 5701   0204 0046

L_5703:
        CLRR    R2                              ; 5703   01D2
        MVO     R2,     G_01AA                  ; 5704   0242 01AA
        MVI     G_0179, R2                      ; 5706   0282 0179
        ANDI    #$0001, R2                      ; 5708   03BA 0001
        BNEQ    L_5748                          ; 570A   020C 003C

        TSTR    R0                              ; 570C   0080
        BMI     L_5742                          ; 570D   020B 0033

        MVO     R0,     G_01A9                  ; 570F   0240 01A9
        MVI     G_033D, R3                      ; 5711   0283 033D
        MVO     R3,     G_01AA                  ; 5713   0243 01AA
        SDBD                                    ; 5715   0001
        CMPI    #$5B9A, R3                      ; 5716   037B 009A 005B
        BEQ     L_5742                          ; 5719   0204 0027

        SDBD                                    ; 571B   0001
        CMPI    #$5B28, R3                      ; 571C   037B 0028 005B
        BNEQ    L_5742                          ; 571F   020C 0021

        CLRR    R3                              ; 5721   01DB
        SDBD                                    ; 5722   0001
        MVII    #$5BAE, R4                      ; 5723   02BC 00AE 005B

        JSR     R5,     L_6318                  ; 5726   0004 0160 0318

        MVI     G_0325, R1                      ; 5729   0281 0325
        SDBD                                    ; 572B   0001
        ANDI    #$2000, R1                      ; 572C   03B9 0000 0020
        BNEQ    L_5742                          ; 572F   020C 0011

        MVI     G_017F, R1                      ; 5731   0281 017F
        MVI     G_0179, R2                      ; 5733   0282 0179
        ANDI    #$0002, R2                      ; 5735   03BA 0002
        BEQ     L_573C                          ; 5737   0204 0003

        SUBI    #$000A, R1                      ; 5739   0339 000A
        INCR    R7                              ; 573B   000F

L_573C:
        NEGR    R1                              ; 573C   0021

L_573D:
        JSR     R5,     L_6046                  ; 573D   0004 0160 0046

        B       L_5744                          ; 5740   0200 0002

L_5742:
        CLRR    R1                              ; 5742   01C9
        CLRR    R2                              ; 5743   01D2
L_5744:
        MVO     R1,     G_0108                  ; 5744   0241 0108
        MVO     R2,     G_010C                  ; 5746   0242 010C
L_5748:
        PULR    R7                              ; 5748   02B7

L_5749:
        TSTR    R0                              ; 5749   0080
        BMI     L_5778                          ; 574A   020B 002C

        MVO     R0,     G_0196                  ; 574C   0240 0196
        MVI     G_033F, R3                      ; 574E   0283 033F
        SDBD                                    ; 5750   0001
        CMPI    #$5B9A, R3                      ; 5751   037B 009A 005B
        BEQ     L_5778                          ; 5754   0204 0022

        SDBD                                    ; 5756   0001
        CMPI    #$5B5E, R3                      ; 5757   037B 005E 005B
        BNEQ    L_5778                          ; 575A   020C 001C

        MVII    #$0002, R3                      ; 575C   02BB 0002

        JSR     R5,     L_5885                  ; 575E   0004 0158 0085

        MVI     G_0327, R1                      ; 5761   0281 0327
        SDBD                                    ; 5763   0001
        ANDI    #$2000, R1                      ; 5764   03B9 0000 0020
        BNEQ    L_5778                          ; 5767   020C 000F

        MVII    #$0019, R1                      ; 5769   02B9 0019
        MVI     G_017A, R2                      ; 576B   0282 017A
        TSTR    R2                              ; 576D   0092
        BEQ     L_5773                          ; 576E   0204 0003

        SUBI    #$0005, R1                      ; 5770   0339 0005
        NEGR    R1                              ; 5772   0021

L_5773:
        JSR     R5,     L_6046                  ; 5773   0004 0160 0046

        B       L_577A                          ; 5776   0200 0002

L_5778:
        CLRR    R1                              ; 5778   01C9
        CLRR    R2                              ; 5779   01D2
L_577A:
        MVII    #$012A, R3                      ; 577A   02BB 012A

        JSR     R5,     L_6041                  ; 577C   0004 0160 0041

        PULR    R7                              ; 577F   02B7

        TSTR    R0                              ; 5780   0080
        BEQ     L_579A                          ; 5781   0204 0017

        MVII    #$0179, R3                      ; 5783   02BB 0179
        MVI     G_018B, R2                      ; 5785   0282 018B
        ANDI    #$0002, R2                      ; 5787   03BA 0002
        BEQ     L_578F                          ; 5789   0204 0004

        TSTR    R1                              ; 578B   0089
        BNEQ    L_578F                          ; 578C   020C 0001

        INCR    R3                              ; 578E   000B
L_578F:
        MVII    #$0002, R2                      ; 578F   02BA 0002
        MVI@    R3,     R1                      ; 5791   0299
        COMR    R2                              ; 5792   001A
        ANDR    R2,     R1                      ; 5793   0191
        TSTR    R0                              ; 5794   0080
        BMI     L_5799                          ; 5795   020B 0002

        COMR    R2                              ; 5797   001A
        XORR    R2,     R1                      ; 5798   01D1
L_5799:
        MVO@    R1,     R3                      ; 5799   0259
L_579A:
        MOVR    R5,     R7                      ; 579A   00AF

        PSHR    R5                              ; 579B   0275
        MVI     G_018B, R2                      ; 579C   0282 018B
        ANDI    #$0002, R2                      ; 579E   03BA 0002
        BEQ     L_57A7                          ; 57A0   0204 0005

        TSTR    R1                              ; 57A2   0089
        BNEQ    L_57A7                          ; 57A3   020C 0002
        B       L_57BE                          ; 57A5   0200 0017

L_57A7:
        TSTR    R0                              ; 57A7   0080
        BNEQ    L_57AE                          ; 57A8   020C 0004

        JSR     R5,     L_57DA                  ; 57AA   0004 0154 03DA

        PULR    R7                              ; 57AD   02B7

L_57AE:
        CMPI    #$000A, R0                      ; 57AE   0378 000A
        BGT     L_57B9                          ; 57B0   020E 0007
        BLT     L_57BD                          ; 57B2   0205 0009

        CLRR    R3                              ; 57B4   01DB

        JSR     R5,     L_5894                  ; 57B5   0004 0158 0094

        PULR    R7                              ; 57B8   02B7

L_57B9:
        CLRR    R3                              ; 57B9   01DB

        JSR     R5,     L_63F5                  ; 57BA   0004 0160 03F5

L_57BD:
        PULR    R7                              ; 57BD   02B7

L_57BE:
        CMPI    #$0001, R0                      ; 57BE   0378 0001
        BLT     L_57C9                          ; 57C0   0205 0007

        CMPI    #$0009, R0                      ; 57C2   0378 0009
        BGT     L_57CC                          ; 57C4   020E 0006
        J       L_608B                          ; 57C6   0004 0360 008B
L_57C9:
        J       L_57DB                          ; 57C9   0004 0354 03DB

L_57CC:
        CMPI    #$000A, R0                      ; 57CC   0378 000A
        BGT     L_57D5                          ; 57CE   020E 0005

        MVII    #$0002, R3                      ; 57D0   02BB 0002
        J       L_5895                          ; 57D2   0004 0358 0095

L_57D5:
        MVII    #$0002, R3                      ; 57D5   02BB 0002
        J       L_63F6                          ; 57D7   0004 0360 03F6

L_57DA:
        PSHR    R5                              ; 57DA   0275
L_57DB:
        SDBD                                    ; 57DB   0001
        MVII    #$5876, R1                      ; 57DC   02B9 0076 0058
        MVII    #$0080, R2                      ; 57DF   02BA 0080
        SWAP    R2,     1                       ; 57E1   0042
        MVII    #$0002, R3                      ; 57E2   02BB 0002
        MVII    #$022A, R4                      ; 57E4   02BC 022A

        JSR     R5,     L_59CF                  ; 57E6   0004 0158 01CF

        MVII    #$0240, R4                      ; 57E9   02BC 0240

        JSR     R5,     X_PRINT_R5              ; 57EB   0004 0118 007B
        STRING  "Knight: "                      ; 57EE  
        DECLE   $0000                           ; 57F6   0000

        MVI     G_017C, R0                      ; 57F7   0280 017C
        MVII    #$0002, R1                      ; 57F9   02B9 0002

        JSR     R5,     X_PRNUM_RGT             ; 57FB   0004 0118 00C5

        MVI     G_018B, R0                      ; 57FE   0280 018B
        ANDI    #$0002, R0                      ; 5800   03B8 0002
        BEQ     L_5819                          ; 5802   0204 0015

        MVII    #$0254, R4                      ; 5804   02BC 0254

        JSR     R5,     X_PRINT_R5              ; 5806   0004 0118 007B
        STRING  "Wizard: "                      ; 5809  
        DECLE   $0000                           ; 5811   0000

        MVI     G_017D, R0                      ; 5812   0280 017D
        MVII    #$0002, R1                      ; 5814   02B9 0002

        JSR     R5,     X_PRNUM_RGT             ; 5816   0004 0118 00C5

L_5819:
        MVII    #$027A, R4                      ; 5819   02BC 027A

        JSR     R5,     X_PRINT_R5              ; 581B   0004 0118 007B
        STRING  "Treasures"                     ; 581E  
        DECLE   $0000                           ; 5827   0000

        MVII    #$0290, R4                      ; 5828   02BC 0290

        JSR     R5,     X_PRINT_R5              ; 582A   0004 0118 007B
        STRING  "Inhand: "                      ; 582D  
        DECLE   $0000                           ; 5835   0000

        MVI     G_01A8, R0                      ; 5836   0280 01A8
        MVII    #$0002, R1                      ; 5838   02B9 0002
        XORR    R2,     R3                      ; 583A   01D3

        JSR     R5,     X_PRNUM_RGT             ; 583B   0004 0118 00C5

        MVII    #$02A4, R4                      ; 583E   02BC 02A4

        JSR     R5,     X_PRINT_R5              ; 5840   0004 0118 007B
        STRING  "Stored: "                      ; 5843  
        DECLE   $0000                           ; 584B   0000

        MVI     G_01A7, R0                      ; 584C   0280 01A7
        MVII    #$0002, R1                      ; 584E   02B9 0002
        XORR    R2,     R3                      ; 5850   01D3

        JSR     R5,     X_PRNUM_RGT             ; 5851   0004 0118 00C5

        MVII    #$02B9, R4                      ; 5854   02BC 02B9

        JSR     R5,     X_PRINT_R5              ; 5856   0004 0118 007B
        STRING  "Value: "                       ; 5859  
        DECLE   $0000                           ; 5860   0000

        MVII    #$01A5, R5                      ; 5861   02BD 01A5
        SDBD                                    ; 5863   0001
        MVI@    R5,     R0                      ; 5864   02A8
        MVII    #$0004, R1                      ; 5865   02B9 0004
        XORR    R2,     R3                      ; 5867   01D3

        JSR     R5,     X_PRNUM_RGT             ; 5868   0004 0118 00C5

L_586B:
        MVI     G_0103, R0                      ; 586B   0280 0103
        TSTR    R0                              ; 586D   0080
        BNEQ    L_586B                          ; 586E   022C 0004

        DIS                                     ; 5870   0003

        JSR     R5,     L_5EE2                  ; 5871   0004 015C 02E2

        EIS                                     ; 5874   0002
        PULR    R7                              ; 5875   02B7

        DECLE   $0052,  $0065,  $0069,  $006E   ; 5876   0052 0065 0069 006E
        DECLE   $0063,  $0061,  $0072,  $006E   ; 587A   0063 0061 0072 006E
        DECLE   $0061,  $0074,  $0069,  $006F   ; 587E   0061 0074 0069 006F
        DECLE   $006E,  $0073,  $0000           ; 5882   006E 0073 0000
L_5885:
        PSHR    R5                              ; 5885   0275

        JSR     R5,     L_6361                  ; 5886   0004 0160 0361

        ADDI    #$0345, R3                      ; 5889   02FB 0345
        MVO@    R1,     R3                      ; 588B   0259
        SUBI    #$0018, R3                      ; 588C   033B 0018
        MVII    #$0001, R2                      ; 588E   02BA 0001

        JSR     R5,     L_6344                  ; 5890   0004 0160 0344

        PULR    R7                              ; 5893   02B7

L_5894:
        PSHR    R5                              ; 5894   0275
L_5895:
        PSHR    R3                              ; 5895   0273

        JSR     R5,     L_58C1                  ; 5896   0004 0158 00C1

        PULR    R3                              ; 5899   02B3
        TSTR    R1                              ; 589A   0089
        BMI     L_58C0                          ; 589B   020B 0023

        CMPI    #$0002, R1                      ; 589D   0379 0002
        BGE     L_58A6                          ; 589F   020D 0005

        JSR     R5,     L_59FF                  ; 58A1   0004 0158 01FF

        B       L_58B5                          ; 58A4   0200 000F

L_58A6:
        CMPI    #$0002, R3                      ; 58A6   037B 0002
        BNEQ    L_58B5                          ; 58A8   020C 000B

        SUBI    #$0002, R1                      ; 58AA   0339 0002
        MVI     G_019C, R2                      ; 58AC   0282 019C
        SLL     R2,     1                       ; 58AE   004A
        ADDR    R1,     R2                      ; 58AF   00CA
        ADDI    #$018E, R2                      ; 58B0   02FA 018E
        MVII    #$000A, R0                      ; 58B2   02B8 000A
        MVO@    R0,     R2                      ; 58B4   0250
L_58B5:
        MVI     G_0103, R0                      ; 58B5   0280 0103
        ANDI    #$0002, R0                      ; 58B7   03B8 0002
        BNEQ    L_58B5                          ; 58B9   022C 0005

        DIS                                     ; 58BB   0003

        JSR     R5,     L_5EE2                  ; 58BC   0004 015C 02E2

        EIS                                     ; 58BF   0002
L_58C0:
        PULR    R7                              ; 58C0   02B7

L_58C1:
        PSHR    R5                              ; 58C1   0275

        JSR     R5,     L_5982                  ; 58C2   0004 0158 0182

        TSTR    R1                              ; 58C5   0089
        BMI     L_58DD                          ; 58C6   020B 0015

        PSHR    R1                              ; 58C8   0271
        MVI     G_019C, R2                      ; 58C9   0282 019C
        SLL     R2,     2                       ; 58CB   004E
        ADDR    R2,     R1                      ; 58CC   00D1
        SDBD                                    ; 58CD   0001
        ADDI    #$5972, R1                      ; 58CE   02F9 0072 0059
        MVI@    R1,     R1                      ; 58D1   0289
        SDBD                                    ; 58D2   0001
        ADDI    #$58DE, R1                      ; 58D3   02F9 00DE 0058
        CLRR    R3                              ; 58D6   01DB
        MVII    #$0266, R4                      ; 58D7   02BC 0266

        JSR     R5,     L_59CF                  ; 58D9   0004 0158 01CF

        PULR    R1                              ; 58DC   02B1
L_58DD:
        PULR    R7                              ; 58DD   02B7

        DECLE   $0079,  $0065,  $0020,  $0072   ; 58DE   0079 0065 0020 0072
        DECLE   $0065,  $0061,  $0064,  $002C   ; 58E2   0065 0061 0064 002C
        DECLE   $0020,  $0079,  $0065,  $0020   ; 58E6   0020 0079 0065 0020
        DECLE   $006D,  $006F,  $0076,  $0065   ; 58EA   006D 006F 0076 0065
        DECLE   $0000,  $0032,  $0020,  $0046   ; 58EE   0000 0032 0020 0046
        DECLE   $0069,  $0072,  $0065,  $0062   ; 58F2   0069 0072 0065 0062
        DECLE   $0061,  $006C,  $006C,  $0000   ; 58F6   0061 006C 006C 0000
        DECLE   $0033,  $0020,  $0048,  $0065   ; 58FA   0033 0020 0048 0065
        DECLE   $0061,  $006C,  $0000,  $0034   ; 58FE   0061 006C 0000 0034
        DECLE   $0020,  $0046,  $0061,  $0073   ; 5902   0020 0046 0061 0073
        DECLE   $0074,  $0020,  $0046,  $0065   ; 5906   0074 0020 0046 0065
        DECLE   $0065,  $0074,  $0000,  $0035   ; 590A   0065 0074 0000 0035
        DECLE   $0020,  $0049,  $006E,  $0076   ; 590E   0020 0049 006E 0076
        DECLE   $0069,  $006E,  $0063,  $0069   ; 5912   0069 006E 0063 0069
        DECLE   $0062,  $006C,  $0065,  $0000   ; 5916   0062 006C 0065 0000
        DECLE   $0036,  $0020,  $0044,  $0065   ; 591A   0036 0020 0044 0065
        DECLE   $0073,  $0074,  $0072,  $006F   ; 591E   0073 0074 0072 006F
        DECLE   $0079,  $0020,  $0077,  $0061   ; 5922   0079 0020 0077 0061
        DECLE   $006C,  $006C,  $0073,  $0000   ; 5926   006C 006C 0073 0000
        DECLE   $0037,  $0020,  $0054,  $006F   ; 592A   0037 0020 0054 006F
        DECLE   $0020,  $0063,  $0068,  $0065   ; 592E   0020 0063 0068 0065
        DECLE   $0073,  $0074,  $0000,  $0038   ; 5932   0073 0074 0000 0038
        DECLE   $0020,  $0049,  $006E,  $0076   ; 5936   0020 0049 006E 0076
        DECLE   $0069,  $006E,  $0063,  $002D   ; 593A   0069 006E 0063 002D
        DECLE   $0077,  $0069,  $007A,  $0000   ; 593E   0077 0069 007A 0000
        DECLE   $0039,  $0020,  $0054,  $006F   ; 5942   0039 0020 0054 006F
        DECLE   $0020,  $004B,  $006E,  $0069   ; 5946   0020 004B 006E 0069
        DECLE   $0067,  $0068,  $0074,  $0000   ; 594A   0067 0068 0074 0000
        DECLE   $0074,  $006F,  $0020,  $0072   ; 594E   0074 006F 0020 0072
        DECLE   $0065,  $0061,  $0064,  $0020   ; 5952   0065 0061 0064 0020
        DECLE   $0074,  $0068,  $0069,  $0073   ; 5956   0074 0068 0069 0073
        DECLE   $0020,  $006E,  $006F,  $0074   ; 595A   0020 006E 006F 0074
        DECLE   $0065,  $0020,  $0020,  $0069   ; 595E   0065 0020 0020 0069
        DECLE   $0073,  $0020,  $0061,  $0020   ; 5962   0073 0020 0061 0020
        DECLE   $0066,  $006F,  $006F,  $006C   ; 5966   0066 006F 006F 006C
        DECLE   $0073,  $0020,  $0066,  $006F   ; 596A   0073 0020 0066 006F
        DECLE   $006C,  $006C,  $0079,  $0000   ; 596E   006C 006C 0079 0000
        DECLE   $0000,  $0000,  $0011,  $001C   ; 5972   0000 0000 0011 001C
        DECLE   $0000,  $0000,  $0023,  $002F   ; 5976   0000 0000 0023 002F
        DECLE   $0000,  $0000                   ; 597A   0000 0000

        RSWD    R4                              ; 597C   003C
        SLL     R0,     2                       ; 597D   004C
        RRC     R0,     1                       ; 597E   0070
        RRC     R0,     1                       ; 597F   0070
        RLC     R3,     2                       ; 5980   0057
        SLR     R0,     2                       ; 5981   0064
L_5982:
        PSHR    R5                              ; 5982   0275

        JSR     R5,     L_6054                  ; 5983   0004 0160 0054

        MVII    #$0003, R1                      ; 5986   02B9 0003
L_5988:
        MVI@    R4,     R0                      ; 5988   02A0
        SDBD                                    ; 5989   0001
        ANDI    #$09F8, R0                      ; 598A   03B8 00F8 0009
        SDBD                                    ; 598D   0001
        CMPI    #$0858, R0                      ; 598E   0378 0058 0008
        BEQ     L_599E                          ; 5991   0204 000B

        DECR    R1                              ; 5993   0011
        BMI     L_59A3                          ; 5994   020B 000D

        CMPI    #$0001, R1                      ; 5996   0379 0001
        BNEQ    L_5988                          ; 5998   022C 0011

        ADDI    #$0012, R4                      ; 599A   02FC 0012
        B       L_5988                          ; 599C   0220 0015

L_599E:
        CLRR    R1                              ; 599E   01C9
        DECR    R4                              ; 599F   0014
        MVI@    R4,     R0                      ; 59A0   02A0
        RLC     R0,     2                       ; 59A1   0054
        RLC     R1,     2                       ; 59A2   0055
L_59A3:
        PULR    R7                              ; 59A3   02B7

        MVI     .STIC.MODE,R0                   ; 59A4   0280 0021
        CLRR    R0                              ; 59A6   01C0
        MVO     R0,     G_0105                  ; 59A7   0240 0105
        MVO     R0,     .STIC.HDLY              ; 59A9   0240 0030
        MVO     R0,     .STIC.VDLY              ; 59AB   0240 0031
        CLRR    R4                              ; 59AD   01E4
        MVII    #$0008, R1                      ; 59AE   02B9 0008
L_59B0:
        MVO@    R0,     R4                      ; 59B0   0260
        DECR    R1                              ; 59B1   0011
        BNEQ    L_59B0                          ; 59B2   022C 0003

        MVI     G_0104, R0                      ; 59B4   0280 0104
        DECR    R0                              ; 59B6   0010
        BNEQ    L_59CA                          ; 59B7   020C 0011

        MVO     R0,     G_0103                  ; 59B9   0240 0103
        INCR    R0                              ; 59BB   0008
        MVO     R0,     .STIC.MODE              ; 59BC   0240 0021
        MVO     R0,     G_0105                  ; 59BE   0240 0105
        MVII    #$00C3, R0                      ; 59C0   02B8 00C3
        MVO     R0,     .ISRVEC.0               ; 59C2   0240 0100
        MVII    #$0051, R0                      ; 59C4   02B8 0051
        MVO     R0,     .ISRVEC.1               ; 59C6   0240 0101
        B       L_59CE                          ; 59C8   0200 0004

L_59CA:
        MVO     R0,     G_0104                  ; 59CA   0240 0104
        MVO     R0,     .STIC.VIDEN             ; 59CC   0240 0020
L_59CE:
        MOVR    R5,     R7                      ; 59CE   00AF

L_59CF:
        PSHR    R5                              ; 59CF   0275
        PSHR    R4                              ; 59D0   0274
        DIS                                     ; 59D1   0003
        MVII    #$00F0, R0                      ; 59D2   02B8 00F0
        MVII    #$0200, R4                      ; 59D4   02BC 0200

        JSR     R5,     X_FILL_ZERO             ; 59D6   0004 0114 0338

        TSTR    R3                              ; 59D9   009B
        BNEQ    L_59E2                          ; 59DA   020C 0006

        SDBD                                    ; 59DC   0001
        MVII    #$2000, R0                      ; 59DD   02B8 0000 0020
        MVO     R0,     .BTAB.00                ; 59E0   0240 0200
L_59E2:
        PULR    R4                              ; 59E2   02B4

        JSR     R5,     X_PRINT_R1              ; 59E3   0004 0118 0067

        MVII    #$00A4, R0                      ; 59E6   02B8 00A4
        MVO     R0,     .ISRVEC.0               ; 59E8   0240 0100
        MVII    #$0059, R0                      ; 59EA   02B8 0059
        MVO     R0,     .ISRVEC.1               ; 59EC   0240 0101
        MVII    #$0002, R0                      ; 59EE   02B8 0002
        MVO     R0,     G_0103                  ; 59F0   0240 0103
        MVII    #$00E1, R0                      ; 59F2   02B8 00E1
        MVO     R0,     G_0104                  ; 59F4   0240 0104
        EIS                                     ; 59F6   0002
        PSHR    R3                              ; 59F7   0273
        PSHR    R4                              ; 59F8   0274

        JSR     R5,     .EXEC.A83               ; 59F9   0004 0118 0283

        PULR    R4                              ; 59FC   02B4
        PULR    R3                              ; 59FD   02B3
        PULR    R7                              ; 59FE   02B7

L_59FF:
        PSHR    R5                              ; 59FF   0275
        MVI     G_019C, R0                      ; 5A00   0280 019C
        SLL     R0,     2                       ; 5A02   004C
        SLL     R1,     1                       ; 5A03   0049
        ADDR    R0,     R1                      ; 5A04   00C1
        SDBD                                    ; 5A05   0001
        ADDI    #$5A17, R1                      ; 5A06   02F9 0017 005A
        MVI@    R1,     R0                      ; 5A09   0288
        MVO     R0,     G_0175                  ; 5A0A   0240 0175
        INCR    R1                              ; 5A0C   0009
        MVI@    R1,     R0                      ; 5A0D   0288
        MVO     R0,     G_0176                  ; 5A0E   0240 0176

        JSR     R5,     L_5A27                  ; 5A10   0004 0158 0227

        B       L_5A16                          ; 5A13   0200 0001

        NOP                                     ; 5A15   0034
L_5A16:
        PULR    R7                              ; 5A16   02B7

        DECLE   $0062,  $000B,  $000C,  $001A   ; 5A17   0062 000B 000C 001A
        DECLE   $001B,  $001C,  $0062,  $0004   ; 5A1B   001B 001C 0062 0004

        RSWD    R3                              ; 5A1F   003B
        RSWD    R4                              ; 5A20   003C
        NEGR    R2                              ; 5A21   0022
        INCR    R4                              ; 5A22   000C
        SLR     R1,     1                       ; 5A23   0061
        INCR    R1                              ; 5A24   0009
        SLR     R1,     1                       ; 5A25   0061
        INCR    R1                              ; 5A26   0009
L_5A27:
        PSHR    R5                              ; 5A27   0275
        MVII    #$0004, R2                      ; 5A28   02BA 0004
        MOVR    R2,     R3                      ; 5A2A   0093
        MVI     G_017B, R4                      ; 5A2B   0284 017B
        ANDI    #$000F, R4                      ; 5A2D   03BC 000F
        MVI     G_018B, R0                      ; 5A2F   0280 018B
        ANDI    #$0002, R0                      ; 5A31   03B8 0002
        BNEQ    L_5A3A                          ; 5A33   020C 0005

        SUBI    #$0002, R3                      ; 5A35   033B 0002
        ADDR    R3,     R2                      ; 5A37   00DA
        ANDI    #$0003, R4                      ; 5A38   03BC 0003
L_5A3A:
        MVO     R4,     G_017B                  ; 5A3A   0244 017B

        JSR     R5,     L_5F5E                  ; 5A3C   0004 015C 035E

        PULR    R7                              ; 5A3F   02B7

L_SPELL_DISP:
        DECLE   $0058,  $0019,  $00B8,  $0020   ; 5A40   0058 0019 00B8 0020
        DECLE   $0007,  $0000,  $0028,  $005B   ; 5A44   0007 0000 0028 005B
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A48   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0069   ; 5A4C   0000 0000 0000 0069
        DECLE   $0080,  $0040,  $0001,  $0020   ; 5A50   0080 0040 0001 0020
        DECLE   $0036,  $005B,  $0000,  $0000   ; 5A54   0036 005B 0000 0000
        DECLE   $0000,  $0000,  $0008,  $0000   ; 5A58   0000 0000 0008 0000
        DECLE   $0000,  $0090,  $0080,  $00A0   ; 5A5C   0000 0090 0080 00A0
        DECLE   $0005,  $0010,  $005E,  $005B   ; 5A60   0005 0010 005E 005B
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A64   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $00E0   ; 5A68   0000 0000 0000 00E0
        DECLE   $0000                           ; 5A6C   0000

        ADDR    R0,     R0                      ; 5A6D   00C0

        JSR     R4,     .EXEC.066               ; 5A6E   0004 0010 0066
        DECLE   $005B,  $0010,  $0000,  $0000   ; 5A71   005B 0010 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A75   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0018,  $0018   ; 5A79   0000 0000 0018 0018
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A7D   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A81   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A85   0000 0000 0000 0000
        DECLE   $0000,  $0014,  $0028,  $0008   ; 5A89   0000 0014 0028 0008
        DECLE   $0024,  $0000,  $0000,  $0000   ; 5A8D   0024 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0081   ; 5A91   0000 0000 0000 0081
        DECLE   $0004,  $0040,  $0010,  $0000   ; 5A95   0004 0040 0010 0000
        DECLE   $0041,  $0000,  $0080,  $0004   ; 5A99   0041 0000 0080 0004
        DECLE   $0000,  $0040,  $0004,  $0020   ; 5A9D   0000 0040 0004 0020
        DECLE   $0000,  $0001,  $0080,  $0041   ; 5AA1   0000 0001 0080 0041
        DECLE   $0080,  $0000,  $0000,  $0000   ; 5AA5   0080 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5AA9   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5AAD   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0082,  $0000   ; 5AB1   0000 0000 0082 0000
        DECLE   $0099,  $0080,  $00A0,  $0000   ; 5AB5   0099 0080 00A0 0000
        DECLE   $0020,  $0030,  $005B,  $0000   ; 5AB9   0020 0030 005B 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5ABD   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $00C9,  $0080   ; 5AC1   0000 0000 00C9 0080
        DECLE   $00C0,  $0000,  $0020,  $0048   ; 5AC5   00C0 0000 0020 0048
        DECLE   $005B,  $0000,  $0000,  $0000   ; 5AC9   005B 0000 0000 0000
        DECLE   $0000,  $0008,  $0000,  $0000   ; 5ACD   0000 0008 0000 0000
        DECLE   $0098,  $0080,  $00A0,  $0007   ; 5AD1   0098 0080 00A0 0007
        DECLE   $0000,  $0076,  $005B,  $0020   ; 5AD5   0000 0076 005B 0020
        DECLE   $0000,  $0028,  $0000,  $0000   ; 5AD9   0000 0028 0000 0000
        DECLE   $0000,  $0000,  $00C1,  $0080   ; 5ADD   0000 0000 00C1 0080
        DECLE   $00C0,  $0006,  $0000,  $0082   ; 5AE1   00C0 0006 0000 0082
        DECLE   $005B,  $0010,  $0000,  $0000   ; 5AE5   005B 0010 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0018   ; 5AE9   0000 0000 0000 0018
        DECLE   $0024,  $003C,  $0066,  $0066   ; 5AED   0024 003C 0066 0066
        DECLE   $003C,  $0024,  $0018,  $0000   ; 5AF1   003C 0024 0018 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5AF5   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0042,  $0018   ; 5AF9   0000 0000 0042 0018
        DECLE   $0024,  $0024,  $005A,  $005A   ; 5AFD   0024 0024 005A 005A
        DECLE   $0024,  $0024,  $0018,  $0042   ; 5B01   0024 0024 0018 0042
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5B05   0000 0000 0000 0000
        DECLE   $0000,  $0018,  $0000,  $0042   ; 5B09   0000 0018 0000 0042
        DECLE   $0000,  $0018,  $00BD,  $00BD   ; 5B0D   0000 0018 00BD 00BD
        DECLE   $0018,  $0000,  $0042,  $0000   ; 5B11   0018 0000 0042 0000
        DECLE   $0018,  $0000,  $0000,  $0042   ; 5B15   0018 0000 0000 0042
        DECLE   $0000,  $0000,  $0081,  $0000   ; 5B19   0000 0000 0081 0000
        DECLE   $00A5,  $0018,  $003C,  $003C   ; 5B1D   00A5 0018 003C 003C
        DECLE   $0018,  $00A5,  $0000,  $0081   ; 5B21   0018 00A5 0000 0081
        DECLE   $0000,  $0000,  $0042,  $0067   ; 5B25   0000 0000 0042 0067
        DECLE   $005D,  $00CE,  $005B,  $0005   ; 5B29   005D 00CE 005B 0005
        DECLE   $0100,  $0079,  $0066,  $00F0   ; 5B2D   0100 0079 0066 00F0
        DECLE   $006A,  $00CE,  $005B,  $0005   ; 5B31   006A 00CE 005B 0005
        DECLE   $0000                           ; 5B35   0000

        ADDR    R4,     R7                      ; 5B36   00E7

        DECLE   $005D,  $0050,  $005C,  $0005   ; 5B37   005D 0050 005C 0005
        DECLE   $00FC,  $0062,  $0067,  $0062   ; 5B3B   00FC 0062 0067 0062
        DECLE   $0067,  $0062,  $0067,  $0062   ; 5B3F   0067 0062 0067 0062
        DECLE   $0067,  $0062,  $0067,  $0062   ; 5B43   0067 0062 0067 0062
        DECLE   $0067,  $0024,  $005D,  $0050   ; 5B47   0067 0024 005D 0050
        DECLE   $005C,  $0005,  $0057,  $0062   ; 5B4B   005C 0005 0057 0062
        DECLE   $0067,  $0062,  $0067,  $0062   ; 5B4F   0067 0062 0067 0062
        DECLE   $0067,  $0062,  $0067,  $0062   ; 5B53   0067 0062 0067 0062
        DECLE   $0067,  $0059,  $005D,  $0050   ; 5B57   0067 0059 005D 0050
        DECLE   $005C,  $0005,  $0000,  $00E1   ; 5B5B   005C 0005 0000 00E1
        DECLE   $005D,  $00A0,  $005C,  $0005   ; 5B5F   005D 00A0 005C 0005
        DECLE   $0100,  $00CB,  $0066,  $0000   ; 5B63   0100 00CB 0066 0000
        DECLE   $0000,  $00F0,  $005C,  $0003   ; 5B67   0000 00F0 005C 0003
        DECLE   $0351,  $003A,  $0061,  $003A   ; 5B6B   0351 003A 0061 003A
        DECLE   $0061,  $003A,  $0061,  $00B5   ; 5B6F   0061 003A 0061 00B5
        DECLE   $0061,  $00D1,  $0061,  $001F   ; 5B73   0061 00D1 0061 001F
        DECLE   $006B,  $00E8,  $005A,  $0004   ; 5B77   006B 00E8 005A 0004
        DECLE   $0000,  $0077,  $006B,  $00A0   ; 5B7B   0000 0077 006B 00A0
        DECLE   $005C,  $0005,  $0000           ; 5B7F   005C 0005 0000

        SLL     R3,     1                       ; 5B82   004B
        SLLC    R1,     2                       ; 5B83   005D
        COMR    R6                              ; 5B84   001E
        SLLC    R0,     2                       ; 5B85   005C
        DIS                                     ; 5B86   0003
        MVO@    R7,     R2                      ; 5B87   0257
        MOVR    R1,     R7                      ; 5B88   008F

        SLR     R3,     2                       ; 5B89   0067
        MOVR    R1,     R7                      ; 5B8A   008F

        SLR     R3,     2                       ; 5B8B   0067
        MOVR    R1,     R7                      ; 5B8C   008F

        SLR     R3,     2                       ; 5B8D   0067
        MOVR    R1,     R7                      ; 5B8E   008F

        SLR     R3,     2                       ; 5B8F   0067
        MOVR    R1,     R7                      ; 5B90   008F

        DECLE   $0067,  $0021,  $0069,  $0093   ; 5B91   0067 0021 0069 0093
        DECLE   $0068,  $0074,  $005A,  $0004   ; 5B95   0068 0074 005A 0004
        DECLE   $0000,  $007F,  $005D,  $0074   ; 5B99   0000 007F 005D 0074
        DECLE   $005A,  $0004,  $0000,  $004B   ; 5B9D   005A 0004 0000 004B
        DECLE   $005D,  $001E,  $005C,  $0003   ; 5BA1   005D 001E 005C 0003
        DECLE   $0251,  $003A,  $0061,  $003A   ; 5BA5   0251 003A 0061 003A
        DECLE   $0061,  $003A,  $0061,  $00D1   ; 5BA9   0061 003A 0061 00D1
        DECLE   $0061,  $0008,  $0000,  $0008   ; 5BAD   0061 0008 0000 0008
        DECLE   $03FE,  $0007,  $03F9,  $0003   ; 5BB1   03FE 0007 03F9 0003
        DECLE   $03F8,  $0000,  $03F8,  $03FD   ; 5BB5   03F8 0000 03F8 03FD
        DECLE   $03F8,  $03F9,  $03F9,  $03F8   ; 5BB9   03F8 03F9 03F9 03F8
        DECLE   $03FE,  $03F8,  $0000,  $03F8   ; 5BBD   03FE 03F8 0000 03F8
        DECLE   $0002,  $03F9,  $0007,  $03FD   ; 5BC1   0002 03F9 0007 03FD
        DECLE   $0008,  $0000,  $0008,  $0003   ; 5BC5   0008 0000 0008 0003
        DECLE   $0008,  $0007,  $0007,  $0008   ; 5BC9   0008 0007 0007 0008
        DECLE   $0002,  $0018,  $003C,  $007E   ; 5BCD   0002 0018 003C 007E
        DECLE   $0073,  $00F9,  $0099,  $0089   ; 5BD1   0073 00F9 0099 0089
        DECLE   $0089,  $0089,  $0089,  $0099   ; 5BD5   0089 0089 0089 0099
        DECLE   $00F9,  $0073,  $007E,  $003C   ; 5BD9   00F9 0073 007E 003C
        DECLE   $0018,  $001E,  $003E,  $0033   ; 5BDD   0018 001E 003E 0033
        DECLE   $007B,  $0079,  $00E8,  $0089   ; 5BE1   007B 0079 00E8 0089
        DECLE   $0089,  $0089,  $008B,  $009A   ; 5BE5   0089 0089 008B 009A
        DECLE   $00DA,  $00FE,  $007C,  $007C   ; 5BE9   00DA 00FE 007C 007C
        DECLE   $001C,  $001C,  $001C,  $0032   ; 5BED   001C 001C 001C 0032
        DECLE   $0032,  $0061,  $0061,  $00F1   ; 5BF1   0032 0061 0061 00F1
        DECLE   $00B9,  $008B,  $008A,  $008E   ; 5BF5   00B9 008B 008A 008E
        DECLE   $008E,  $00C4,  $007C,  $0078   ; 5BF9   008E 00C4 007C 0078
        DECLE   $0030,  $003B,  $003B,  $0061   ; 5BFD   0030 003B 003B 0061
        DECLE   $0061,  $00C1,  $00C3,  $00FB   ; 5C01   0061 00C1 00C3 00FB
        DECLE   $00FF,  $008F,  $0086,  $0086   ; 5C05   00FF 008F 0086 0086
        DECLE   $00C4,  $0064,  $007C,  $0038   ; 5C09   00C4 0064 007C 0038
        DECLE   $0038,  $003C,  $007E,  $0042   ; 5C0D   0038 003C 007E 0042
        DECLE   $0042,  $00C3,  $0081,  $00BB   ; 5C11   0042 00C3 0081 00BB
        DECLE   $00FF,  $00E7,  $00C3,  $00C3   ; 5C15   00FF 00E7 00C3 00C3
        DECLE   $00C3,  $0042,  $007E,  $003C   ; 5C19   00C3 0042 007E 003C
        DECLE   $003C,  $0000,  $0024,  $0011   ; 5C1D   003C 0000 0024 0011
        DECLE   $003A,  $00AE,  $007B,  $006E   ; 5C21   003A 00AE 007B 006E
        DECLE   $00FE,  $007F,  $007C,  $00FE   ; 5C25   00FE 007F 007C 00FE
        DECLE   $005C,  $0088,  $0024,  $0000   ; 5C29   005C 0088 0024 0000
        DECLE   $0000,  $0000,  $0001,  $0054   ; 5C2D   0000 0000 0001 0054
        DECLE   $001E,  $007F,  $00FA,  $007F   ; 5C31   001E 007F 00FA 007F
        DECLE   $007B,  $00FE,  $007E,  $00B6   ; 5C35   007B 00FE 007E 00B6
        DECLE   $005D,  $0024,  $0040,  $0010   ; 5C39   005D 0024 0040 0010
        DECLE   $0000,  $0010,  $0000,  $0020   ; 5C3D   0000 0010 0000 0020
        DECLE   $001C,  $005F,  $007E,  $007E   ; 5C41   001C 005F 007E 007E
        DECLE   $00FB,  $005E,  $007B,  $00BE   ; 5C45   00FB 005E 007B 00BE
L_INIT_PTRS:
        DECLE   $007C,  $008A,  $0010,  $0000   ; 5C49   007C 008A 0010 0000
        DECLE   $0000,  $0084,  $0056,  $0000   ; 5C4D   0000 0084 0056 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5C51   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $00FF,  $0000   ; 5C55   0000 0000 00FF 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5C59   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5C5D   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5C61   0000 0000 0000 0000
        DECLE   $0006,  $000C,  $0030,  $0060   ; 5C65   0006 000C 0030 0060
        DECLE   $00C0,  $0000,  $0000,  $0000   ; 5C69   00C0 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5C6D   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0004   ; 5C71   0000 0000 0000 0004
        DECLE   $0004,  $0008,  $0008,  $0010   ; 5C75   0004 0008 0008 0010
        DECLE   $0010,  $0020,  $0020,  $0040   ; 5C79   0010 0020 0020 0040
        DECLE   $0040,  $0080,  $0080,  $0000   ; 5C7D   0040 0080 0080 0000
        DECLE   $0000,  $0000,  $0000,  $0008   ; 5C81   0000 0000 0000 0008
        DECLE   $0008,  $0008,  $0008,  $0010   ; 5C85   0008 0008 0008 0010
        DECLE   $0010,  $0010,  $0010,  $0020   ; 5C89   0010 0010 0010 0020
        DECLE   $0020,  $0020,  $0020,  $0000   ; 5C8D   0020 0020 0020 0000
        DECLE   $0000,  $0010,  $0010,  $0010   ; 5C91   0000 0010 0010 0010
        DECLE   $0010,  $0010,  $0010,  $0010   ; 5C95   0010 0010 0010 0010
        DECLE   $0010,  $0010,  $0010,  $0010   ; 5C99   0010 0010 0010 0010
        DECLE   $0010,  $0010,  $0010,  $006D   ; 5C9D   0010 0010 0010 006D
        DECLE   $003E,  $007F,  $00F6,  $00F1   ; 5CA1   003E 007F 00F6 00F1
        DECLE   $00D8,  $0088,  $00A8,  $00A8   ; 5CA5   00D8 0088 00A8 00A8
        DECLE   $0088,  $00D8,  $00F1,  $00F6   ; 5CA9   0088 00D8 00F1 00F6
        DECLE   $007F,  $003E,  $006D,  $0002   ; 5CAD   007F 003E 006D 0002
        DECLE   $0025,  $006E,  $003F,  $007C   ; 5CB1   0025 006E 003F 007C
        DECLE   $00F4,  $0098,  $0098,  $00A8   ; 5CB5   00F4 0098 0098 00A8
        DECLE   $00AA,  $008D,  $007A,  $00BF   ; 5CB9   00AA 008D 007A 00BF
        DECLE   $001E,  $0034,  $0000,  $0005   ; 5CBD   001E 0034 0000 0005
        DECLE   $000E,  $0016,  $003E,  $001C   ; 5CC1   000E 0016 003E 001C
        DECLE   $00F8,  $0050,  $008A,  $00AD   ; 5CC5   00F8 0050 008A 00AD
        DECLE   $00AA,  $00CA,  $00FF,  $00FF   ; 5CC9   00AA 00CA 00FF 00FF

        MOVR    R3,     R6                      ; 5CCD   009E
        INCR    R6                              ; 5CCE   000E
        COMR    R0                              ; 5CCF   0018
        RLC     R0,     1                       ; 5CD0   0050
        RRC     R0,     1                       ; 5CD1   0070
        RSWD    R0                              ; 5CD2   0038
        RRC     R0,     1                       ; 5CD3   0070
        RSWD    R2                              ; 5CD4   003A
        ADDR    R6,     R5                      ; 5CD5   00F5
        RRC     R2,     1                       ; 5CD6   0072
        ADDR    R7,     R3                      ; 5CD7   00FB
        ADDR    R3,     R6                      ; 5CD8   00DE
        ADDR    R1,     R6                      ; 5CD9   00CE
        ADDR    R2,     R6                      ; 5CDA   00D6
        ADDR    R2,     R7                      ; 5CDB   00D7

        DECLE   $0047,  $00FD,  $0030,  $0000   ; 5CDC   0047 00FD 0030 0000
        DECLE   $00A5,  $0042,  $0042,  $00F7   ; 5CE0   00A5 0042 0042 00F7
        DECLE   $00F7                           ; 5CE4   00F7

        ADDR    R4,     R3                      ; 5CE5   00E3
        SLR     R2,     2                       ; 5CE6   0066
        SARC    R2,     2                       ; 5CE7   007E
        ADDR    R4,     R3                      ; 5CE8   00E3
        ADDR    R4,     R3                      ; 5CE9   00E3
        ADDR    R5,     R3                      ; 5CEA   00EB
        ADDR    R5,     R3                      ; 5CEB   00EB
        ADDR    R4,     R7                      ; 5CEC   00E7

        DECLE   $00BD,  $003C,  $003C,  $0000   ; 5CED   00BD 003C 003C 0000
        DECLE   $0000,  $0000,  $0010,  $0038   ; 5CF1   0000 0000 0010 0038
        DECLE   $0010,  $0000,  $0000,  $0000   ; 5CF5   0010 0000 0000 0000
        DECLE   $0000,  $0008,  $0010,  $0054   ; 5CF9   0000 0008 0010 0054
        DECLE   $0010,  $0020,  $0000,  $0000   ; 5CFD   0010 0020 0000 0000
        DECLE   $0000,  $0028,  $0092,  $0044   ; 5D01   0000 0028 0092 0044
        DECLE   $0092,  $0028,  $0000           ; 5D05   0092 0028 0000
L_5D08:
        PSHR    R5                              ; 5D08   0275
        MVII    #$0003, R0                      ; 5D09   02B8 0003

        JSR     R5,     X_RAND1                 ; 5D0B   0004 0114 027D

        SDBD                                    ; 5D0E   0001
        MVII    #$2000, R2                      ; 5D0F   02BA 0000 0020
        MVII    #$0335, R3                      ; 5D12   02BB 0335
        MVII    #$0325, R4                      ; 5D14   02BC 0325
        MVII    #$0008, R5                      ; 5D16   02BD 0008
L_5D18:
        MVI@    R4,     R1                      ; 5D18   02A1
        ANDR    R2,     R1                      ; 5D19   0191
        BEQ     L_5D1F                          ; 5D1A   0204 0003

        MVI@    R3,     R1                      ; 5D1C   0299
        XORR    R0,     R1                      ; 5D1D   01C1
        MVO@    R1,     R3                      ; 5D1E   0259
L_5D1F:
        INCR    R3                              ; 5D1F   000B
        DECR    R5                              ; 5D20   0015
        BNEQ    L_5D18                          ; 5D21   022C 000A
        PULR    R7                              ; 5D23   02B7

        DECLE   $0275,  $009A,  $02FA,  $034D   ; 5D24   0275 009A 02FA 034D
        DECLE   $02B8,  $000F,  $0250,  $0013   ; 5D28   02B8 000F 0250 0013
        DECLE   $009A,  $0062,  $0012,  $02FA   ; 5D2C   009A 0062 0012 02FA
        DECLE   $0188,  $0290,  $02F8,  $0040   ; 5D30   0188 0290 02F8 0040
        DECLE   $0250,  $0081,  $03B8,  $000F   ; 5D34   0250 0081 03B8 000F
        DECLE   $0041,  $0055,  $020A,  $0007   ; 5D38   0041 0055 020A 0007

        BNC     L_5D40                          ; 5D3C   0209 0002

        INCR    R0                              ; 5D3E   0008
        INCR    R7                              ; 5D3F   000F

L_5D40:
        DECR    R0                              ; 5D40   0010
L_5D41:
        ANDI    #$000F, R0                      ; 5D41   03B8 000F
        DECLE   $0001                           ; 5D43   0001

        MVII    #$00AE, R4                      ; 5D44   02BC 00AE
        SLLC    R3,     1                       ; 5D46   005B

        JSR     R5,     L_6318                  ; 5D47   0004 0160 0318

        PULR    R7                              ; 5D4A   02B7

        ADDI    #$0335, R3                      ; 5D4B   02FB 0335
        MVI@    R3,     R0                      ; 5D4D   0298
        SDBD                                    ; 5D4E   0001
        XORI    #$1004, R0                      ; 5D4F   03F8 0004 0010
        MVO@    R0,     R3                      ; 5D52   0258
        ADDI    #$0018, R3                      ; 5D53   02FB 0018
        MVII    #$0004, R0                      ; 5D55   02B8 0004
        MVO@    R0,     R3                      ; 5D57   0258
        MOVR    R5,     R7                      ; 5D58   00AF

        PSHR    R5                              ; 5D59   0275
        SDBD                                    ; 5D5A   0001
        MVII    #$5B48, R1                      ; 5D5B   02B9 0048 005B

        JSR     R5,     L_5F7C                  ; 5D5E   0004 015C 037C

        ADDI    #$0010, R3                      ; 5D61   02FB 0010
        MVII    #$000F, R0                      ; 5D63   02B8 000F
        MVO@    R0,     R3                      ; 5D65   0258
        PULR    R7                              ; 5D66   02B7

        ADDI    #$0325, R3                      ; 5D67   02FB 0325
        MVI@    R3,     R0                      ; 5D69   0298
        MVII    #$0100, R1                      ; 5D6A   02B9 0100
        COMR    R1                              ; 5D6C   0019
        ANDR    R1,     R0                      ; 5D6D   0188
        COMR    R1                              ; 5D6E   0019
        XORR    R1,     R0                      ; 5D6F   01C8
        MVO@    R0,     R3                      ; 5D70   0258
        MVI     G_0179, R0                      ; 5D71   0280 0179
        ANDI    #$0002, R0                      ; 5D73   03B8 0002
        MVO     R0,     G_0179                  ; 5D75   0240 0179
        CLRR    R0                              ; 5D77   01C0
        MVO     R0,     G_0108                  ; 5D78   0240 0108
        MVO     R0,     G_010C                  ; 5D7A   0240 010C
        MVO     R0,     G_01AB                  ; 5D7C   0240 01AB
        MOVR    R5,     R7                      ; 5D7E   00AF

        PSHR    R5                              ; 5D7F   0275
        SDBD                                    ; 5D80   0001
        MVII    #$5A40, R4                      ; 5D81   02BC 0040 005A
        TSTR    R3                              ; 5D84   009B
        BEQ     L_5D95                          ; 5D85   0204 000E

        SDBD                                    ; 5D87   0001
        ADDI    #$001C, R4                      ; 5D88   02FC 001C 0000
        MVII    #$0003, R2                      ; 5D8B   02BA 0003

        JSR     R5,     L_5F41                  ; 5D8D   0004 015C 0341

        CLRR    R2                              ; 5D90   01D2
        MVO     R2,     G_018D                  ; 5D91   0242 018D
        B       L_5D99                          ; 5D93   0200 0004

L_5D95:
        MVII    #$0032, R0                      ; 5D95   02B8 0032
        MVO     R0,     G_017F                  ; 5D97   0240 017F
L_5D99:
        MOVR    R3,     R1                      ; 5D99   0099
        ADDI    #$0335, R1                      ; 5D9A   02F9 0335
        SDBD                                    ; 5D9C   0001
        MVII    #$5555, R2                      ; 5D9D   02BA 0055 0055
        ADDR    R3,     R2                      ; 5DA0   00DA
        MVI@    R2,     R2                      ; 5DA1   0292
        SDBD                                    ; 5DA2   0001
        XORI    #$0800, R2                      ; 5DA3   03FA 0000 0008
        MVO@    R2,     R1                      ; 5DA6   024A

        JSR     R5,     L_5FB4                  ; 5DA7   0004 015C 03B4

        PSHR    R1                              ; 5DAA   0271
        PSHR    R0                              ; 5DAB   0270
        ADDI    #$0325, R3                      ; 5DAC   02FB 0325
        MVII    #$0002, R2                      ; 5DAE   02BA 0002

        JSR     R5,     L_5FC1                  ; 5DB0   0004 015C 03C1

        SUBI    #$0002, R3                      ; 5DB3   033B 0002
        MVII    #$00FF, R0                      ; 5DB5   02B8 00FF
        MVII    #$0009, R1                      ; 5DB7   02B9 0009
        SWAP    R1,     1                       ; 5DB9   0041
        XORR    R1,     R0                      ; 5DBA   01C8
        XOR@    R6,     R1                      ; 5DBB   03F1

        JSR     R5,     L_692A                  ; 5DBC   0004 0168 012A

        ADDI    #$0008, R3                      ; 5DBF   02FB 0008
        MVII    #$007F, R0                      ; 5DC1   02B8 007F
        PULR    R1                              ; 5DC3   02B1

        JSR     R5,     L_692A                  ; 5DC4   0004 0168 012A

        SUBI    #$032D, R3                      ; 5DC7   033B 032D
        BNEQ    L_5DD8                          ; 5DC9   020C 000D

        SDBD                                    ; 5DCB   0001
        MVII    #$5BAE, R4                      ; 5DCC   02BC 00AE 005B
        MVI     G_01A9, R0                      ; 5DCF   0280 01A9

        JSR     R5,     L_6318                  ; 5DD1   0004 0160 0318

        CLRR    R0                              ; 5DD4   01C0
        MVO     R0,     G_01AB                  ; 5DD5   0240 01AB
        PULR    R7                              ; 5DD7   02B7

L_5DD8:
        MVI     G_0196, R0                      ; 5DD8   0280 0196

        JSR     R5,     L_5885                  ; 5DDA   0004 0158 0085

        CLRR    R0                              ; 5DDD   01C0
        MVO     R0,     G_01AC                  ; 5DDE   0240 01AC
        PULR    R7                              ; 5DE0   02B7

        SDBD                                    ; 5DE1   0001
        MVII    #$1005, R4                      ; 5DE2   02BC 0005 0010
        B       L_5DEE                          ; 5DE5   0200 0007

        MVII    #$0032, R0                      ; 5DE7   02B8 0032
        MVO     R0,     G_017F                  ; 5DE9   0240 017F
        CLRR    R3                              ; 5DEB   01DB
        MVII    #$0007, R4                      ; 5DEC   02BC 0007
L_5DEE:
        PSHR    R5                              ; 5DEE   0275

        JSR     R5,     L_6832                  ; 5DEF   0004 0168 0032

        PULR    R7                              ; 5DF2   02B7

L_5DF3:
        PSHR    R5                              ; 5DF3   0275
        CMPI    #$0002, R2                      ; 5DF4   037A 0002
        BLT     L_5DFD                          ; 5DF6   0205 0005

        JSR     R5,     L_5E03                  ; 5DF8   0004 015C 0203

        B       L_5E00                          ; 5DFB   0200 0003

L_5DFD:
        JSR     R5,     L_5E8D                  ; 5DFD   0004 015C 028D

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

        MVII    #$65CE, R4                      ; 5E63   02BC 00CE
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

L_5F35:
        SLL     R1,     1                       ; 5F35   0049
        ADDI    #$0126, R1                      ; 5F36   02F9 0126
        MVI@    R1,     R0                      ; 5F38   0288
        ADDI    #$0010, R1                      ; 5F39   02F9 0010
        MVI@    R1,     R2                      ; 5F3B   028A
        MOVR    R5,     R7                      ; 5F3C   00AF

        MVII    #$0003, R1                      ; 5F3D   02B9 0003
        CLRR    R2                              ; 5F3F   01D2
        INCR    R7                              ; 5F40   000F

L_5F41:
        CLRR    R1                              ; 5F41   01C9
L_5F42:
        INCR    R7                              ; 5F42   000F

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

L_5FC1:
        DECR    R2                              ; 5FC1   0012
        INCR    R7                              ; 5FC2   000F

L_5FC3:
        CLRR    R2                              ; 5FC3   01D2
L_5FC4:
        PSHR    R5                              ; 5FC4   0275
L_5FC5:
        MVII    #$0002, R1                      ; 5FC5   02B9 0002

        JSR     R5,     L_5FF1                  ; 5FC7   0004 015C 03F1

        SDBD                                    ; 5FCA   0001
        MVI@    R4,     R0                      ; 5FCB   02A0
        MVI@    R3,     R1                      ; 5FCC   0299
        SDBD                                    ; 5FCD   0001
        ANDI    #$0FF8, R1                      ; 5FCE   03B9 00F8 000F
        XORR    R0,     R1                      ; 5FD1   01C1
        MVO@    R1,     R3                      ; 5FD2   0259
        ADDI    #$0008, R3                      ; 5FD3   02FB 0008
        MVII    #$0003, R1                      ; 5FD5   02B9 0003

        JSR     R5,     L_5FF1                  ; 5FD7   0004 015C 03F1

        SUBI    #$0355, R3                      ; 5FDA   033B 0355
        MVII    #$0167, R1                      ; 5FDC   02B9 0167
        ADDR    R3,     R1                      ; 5FDE   00D9
        MVO@    R1,     R1                      ; 5FDF   0249
        PSHR    R3                              ; 5FE0   0273
        SLL     R3,     1                       ; 5FE1   004B
        ADDI    #$0126, R3                      ; 5FE2   02FB 0126
        MVI@    R4,     R0                      ; 5FE4   02A0
        MVO@    R0,     R3                      ; 5FE5   0258
        ADDI    #$0010, R3                      ; 5FE6   02FB 0010
        MVI@    R4,     R0                      ; 5FE8   02A0
        MVO@    R0,     R3                      ; 5FE9   0258
        PULR    R3                              ; 5FEA   02B3
        ADDI    #$0326, R3                      ; 5FEB   02FB 0326
        DECR    R2                              ; 5FED   0012
        BPL     L_5FC5                          ; 5FEE   0223 002A
        PULR    R7                              ; 5FF0   02B7

L_5FF1:
        SDBD                                    ; 5FF1   0001
        MVI@    R4,     R0                      ; 5FF2   02A0
        MVO@    R0,     R3                      ; 5FF3   0258
        ADDI    #$0008, R3                      ; 5FF4   02FB 0008
        DECR    R1                              ; 5FF6   0011
        BNEQ    L_5FF1                          ; 5FF7   022C 0007
        MOVR    R5,     R7                      ; 5FF9   00AF

L_5FFA:
        MVI@    R4,     R0                      ; 5FFA   02A0
        ANDI    #$00FF, R0                      ; 5FFB   03B8 00FF
        ADDI    #$0007, R4                      ; 5FFD   02FC 0007
        MVI@    R4,     R1                      ; 5FFF   02A1
        ANDI    #$007F, R1                      ; 6000   03B9 007F
        PSHR    R5                              ; 6002   0275

        JSR     R5,     .EXEC.78C               ; 6003   0004 0114 038C

        MOVR    R0,     R3                      ; 6006   0083
        MOVR    R1,     R4                      ; 6007   008C
        MOVR    R2,     R1                      ; 6008   0091
        SDBD                                    ; 6009   0001
        ANDI    #$7FFF, R1                      ; 600A   03B9 00FF 007F

        JSR     R5,     X_SQRT                  ; 600D   0004 011C 0223

        PULR    R7                              ; 6010   02B7

L_6011:
        PSHR    R5                              ; 6011   0275
        PSHR    R0                              ; 6012   0270
        PSHR    R4                              ; 6013   0274
        PSHR    R1                              ; 6014   0271

        JSR     R5,     L_5FFA                  ; 6015   0004 015C 03FA

        MOVR    R3,     R0                      ; 6018   0098
        MOVR    R2,     R3                      ; 6019   0093
        PULR    R1                              ; 601A   02B1
        PSHR    R1                              ; 601B   0271

        JSR     R5,     X_MPY                   ; 601C   0004 011C 01DC

        MOVR    R2,     R1                      ; 601F   0091
        MOVR    R3,     R2                      ; 6020   009A

        JSR     R5,     X_DIVR                  ; 6021   0004 011C 01F8

        PULR    R1                              ; 6024   02B1
        PSHR    R0                              ; 6025   0270
        MOVR    R4,     R0                      ; 6026   00A0
        MOVR    R1,     R4                      ; 6027   008C

        JSR     R5,     X_MPY                   ; 6028   0004 011C 01DC

        MOVR    R2,     R1                      ; 602B   0091
        MOVR    R3,     R2                      ; 602C   009A

        JSR     R5,     X_DIVR                  ; 602D   0004 011C 01F8

        PULR    R1                              ; 6030   02B1
        PULR    R2                              ; 6031   02B2
        PULR    R5                              ; 6032   02B5
        SUBI    #$0325, R2                      ; 6033   033A 0325
        PSHR    R2                              ; 6035   0272
        SLL     R2,     1                       ; 6036   004A
        ADDI    #$0126, R2                      ; 6037   02FA 0126
        MVO@    R1,     R2                      ; 6039   0251
        ADDI    #$0010, R2                      ; 603A   02FA 0010
        MVO@    R0,     R2                      ; 603C   0250
        PULR    R2                              ; 603D   02B2
        PULR    R7                              ; 603E   02B7

L_603F:
        CLRR    R1                              ; 603F   01C9
        CLRR    R2                              ; 6040   01D2
L_6041:
        MVO@    R1,     R3                      ; 6041   0259
        ADDI    #$0010, R3                      ; 6042   02FB 0010
        MVO@    R2,     R3                      ; 6044   025A
        MOVR    R5,     R7                      ; 6045   00AF

L_6046:
        PSHR    R5                              ; 6046   0275
        MOVR    R1,     R2                      ; 6047   008A
        MOVR    R0,     R1                      ; 6048   0081
        MOVR    R2,     R0                      ; 6049   0090
        SLR     R0,     1                       ; 604A   0060

        JSR     R5,     .EXEC.629               ; 604B   0004 0114 0229
        JSR     R5,     X_UNPK_BYTES            ; 604E   0004 0114 0357

        MOVR    R1,     R2                      ; 6051   008A
        MOVR    R0,     R1                      ; 6052   0081
        PULR    R7                              ; 6053   02B7

L_6054:
        ADDI    #$0325, R3                      ; 6054   02FB 0325
        MVI@    R3,     R0                      ; 6056   0298
        ANDI    #$00FF, R0                      ; 6057   03B8 00FF
        SUBI    #$0008, R0                      ; 6059   0338 0008
        BPL     L_605E                          ; 605B   0203 0001

        CLRR    R0                              ; 605D   01C0
L_605E:
        SLR     R0,     2                       ; 605E   0064
        SLR     R0,     1                       ; 605F   0060
        ADDI    #$0008, R3                      ; 6060   02FB 0008
        MOVR    R0,     R4                      ; 6062   0084
        MVI@    R3,     R1                      ; 6063   0299
        ANDI    #$007F, R1                      ; 6064   03B9 007F
        SUBI    #$0008, R1                      ; 6066   0339 0008
        BPL     L_606B                          ; 6068   0203 0001

        CLRR    R1                              ; 606A   01C9
L_606B:
        SLR     R1,     2                       ; 606B   0065
        SLR     R1,     1                       ; 606C   0061
        SLL     R1,     2                       ; 606D   004D
        ADDR    R1,     R4                      ; 606E   00CC
        SLL     R1,     2                       ; 606F   004D
        ADDR    R1,     R4                      ; 6070   00CC
        ADDI    #$0200, R4                      ; 6071   02FC 0200
        SUBI    #$032D, R3                      ; 6073   033B 032D
        MOVR    R5,     R7                      ; 6075   00AF

L_6076:
        MVII    #$0003, R1                      ; 6076   02B9 0003
        CLRR    R2                              ; 6078   01D2
        INCR    R7                              ; 6079   000F

L_607A:
        CLRR    R1                              ; 607A   01C9
L_607B:
        INCR    R7                              ; 607B   000F

        DECR    R1                              ; 607C   0011
L_607D:
        ADDI    #$0163, R2                      ; 607D   02FA 0163
L_607F:
        MVI@    R2,     R0                      ; 607F   0290
        ANDI    #$007F, R0                      ; 6080   03B8 007F
        XORI    #$0080, R0                      ; 6082   03F8 0080
        MVO@    R0,     R2                      ; 6084   0250
        INCR    R2                              ; 6085   000A
        DECR    R1                              ; 6086   0011
        BPL     L_607F                          ; 6087   0223 0009
        MOVR    R5,     R7                      ; 6089   00AF

        PSHR    R5                              ; 608A   0275
L_608B:
        MVI     G_018D, R2                      ; 608B   0282 018D
        TSTR    R2                              ; 608D   0092
        BNEQ    L_60B0                          ; 608E   020C 0020

        MVI     G_019A, R2                      ; 6090   0282 019A
        TSTR    R2                              ; 6092   0092
        BEQ     L_6099                          ; 6093   0204 0004

        CMPI    #$0009, R0                      ; 6095   0378 0009
        BEQ     L_60A1                          ; 6097   0204 0008

L_6099:
        MVI     G_033F, R1                      ; 6099   0281 033F
        SDBD                                    ; 609B   0001
        CMPI    #$5B5E, R1                      ; 609C   0379 005E 005B
        BNEQ    L_60B0                          ; 609F   020C 000F

L_60A1:
        MOVR    R0,     R3                      ; 60A1   0083
        DECR    R3                              ; 60A2   0013
        BEQ     L_60AD                          ; 60A3   0204 0008

        ADDI    #$018D, R3                      ; 60A5   02FB 018D
        MVI@    R3,     R1                      ; 60A7   0299
        TSTR    R1                              ; 60A8   0089
        BEQ     L_60B0                          ; 60A9   0204 0005

        DECR    R1                              ; 60AB   0011
        MVO@    R1,     R3                      ; 60AC   0259

L_60AD:
        JSR     R5,     L_60B1                  ; 60AD   0004 0160 00B1

L_60B0:
        PULR    R7                              ; 60B0   02B7

L_60B1:
        PSHR    R5                              ; 60B1   0275
        PSHR    R0                              ; 60B2   0270

        JSR     R5,     L_6C26                  ; 60B3   0004 016C 0026

        PULR    R0                              ; 60B6   02B0
        CMPI    #$0006, R0                      ; 60B7   0378 0006
        BGT     L_6103                          ; 60B9   020E 0048

        MVO     R0,     G_018D                  ; 60BB   0240 018D
        CMPI    #$0002, R0                      ; 60BD   0378 0002
        BNEQ    L_60E9                          ; 60BF   020C 0028

        MVII    #$0328, R3                      ; 60C1   02BB 0328
        MVII    #$0008, R5                      ; 60C3   02BD 0008
        MVI@    R3,     R0                      ; 60C5   0298
        SDBD                                    ; 60C6   0001
        XORI    #$2000, R0                      ; 60C7   03F8 0000 0020
        MVO@    R0,     R3                      ; 60CA   0258
        ADDR    R5,     R3                      ; 60CB   00EB
        MVI@    R3,     R0                      ; 60CC   0298
        XORI    #$0080, R0                      ; 60CD   03F8 0080
        MVO@    R0,     R3                      ; 60CF   0258
        ADDR    R5,     R3                      ; 60D0   00EB
        MVI@    R3,     R0                      ; 60D1   0298
        SDBD                                    ; 60D2   0001
        ANDI    #$EFF8, R0                      ; 60D3   03B8 00F8 00EF
        XORI    #$0006, R0                      ; 60D6   03F8 0006
        MVO@    R0,     R3                      ; 60D8   0258
        SDBD                                    ; 60D9   0001
        MVII    #$5BA0, R1                      ; 60DA   02B9 00A0 005B
        MVII    #$0003, R3                      ; 60DD   02BB 0003

        JSR     R5,     L_5F7C                  ; 60DF   0004 015C 037C

        MVII    #$0004, R0                      ; 60E2   02B8 0004
        MVO     R0,     G_0350                  ; 60E4   0240 0350

        JSR     R5,     L_6BF8                  ; 60E6   0004 0168 03F8

L_60E9:
        MVII    #$0328, R3                      ; 60E9   02BB 0328
        SDBD                                    ; 60EB   0001
        XORI    #$0900, R0                      ; 60EC   03F8 0000 0009
        MOVR    R0,     R1                      ; 60EF   0081

        JSR     R5,     L_692A                  ; 60F0   0004 0168 012A
        JSR     R5,     L_5F4F                  ; 60F3   0004 015C 034F

        MVI     G_0196, R0                      ; 60F6   0280 0196
        MVII    #$0040, R1                      ; 60F8   02B9 0040

        JSR     R5,     L_6046                  ; 60FA   0004 0160 0046

        MVII    #$012C, R3                      ; 60FD   02BB 012C

        JSR     R5,     L_6041                  ; 60FF   0004 0160 0041

        PULR    R7                              ; 6102   02B7

L_6103:
        CLRR    R5                              ; 6103   01ED
        MVO     R5,     G_018D                  ; 6104   0245 018D
        CMPI    #$0008, R0                      ; 6106   0378 0008
        BGT     L_6129                          ; 6108   020E 001F
        BLT     L_6121                          ; 610A   0205 0015

        MVI     G_01AC, R0                      ; 610C   0280 01AC
        TSTR    R0                              ; 610E   0080
        BNEQ    L_6120                          ; 610F   020C 000F

        MVII    #$0029, R0                      ; 6111   02B8 0029
        SWAP    R0,     1                       ; 6113   0040
        MVII    #$0028, R1                      ; 6114   02B9 0028
        SWAP    R1,     1                       ; 6116   0041
        MVII    #$0327, R3                      ; 6117   02BB 0327

        JSR     R5,     L_692A                  ; 6119   0004 0168 012A

        MVII    #$0258, R0                      ; 611C   02B8 0258
        MVO     R0,     G_034F                  ; 611E   0240 034F
L_6120:
        PULR    R7                              ; 6120   02B7

L_6121:
        DIS                                     ; 6121   0003

        JSR     R5,     L_55BF                  ; 6122   0004 0154 01BF
        JSR     R5,     L_55F7                  ; 6125   0004 0154 01F7

        EIS                                     ; 6128   0002
L_6129:
        MVI     G_019C, R0                      ; 6129   0280 019C
        MVO     R0,     G_0199                  ; 612B   0240 0199
        MVI     G_0175, R0                      ; 612D   0280 0175
        ADDI    #$000A, R0                      ; 612F   02F8 000A
        MVO     R0,     G_0197                  ; 6131   0240 0197
        MVI     G_0176, R0                      ; 6133   0280 0176
        ADDI    #$0006, R0                      ; 6135   02F8 0006
        MVO     R0,     G_0198                  ; 6137   0240 0198
        PULR    R7                              ; 6139   02B7

        PSHR    R5                              ; 613A   0275
        MVI     G_018D, R0                      ; 613B   0280 018D
        DECR    R0                              ; 613D   0010
        BMI     L_61E6                          ; 613E   020B 00A6

        TSTR    R1                              ; 6140   0089
        BNEQ    L_614B                          ; 6141   020C 0008

        MVI     G_033D, R5                      ; 6143   0285 033D
        SDBD                                    ; 6145   0001
        CMPI    #$5B28, R5                      ; 6146   037D 0028 005B
        BNEQ    L_61D2                          ; 6149   020C 0087

L_614B:
        SLL     R0,     1                       ; 614B   0048
        ADDR    R0,     R7                      ; 614C   00C7
        B       L_6159                          ; 614D   0200 000A
        B       L_6175                          ; 614F   0200 0024
        B       L_617A                          ; 6151   0200 0027
        B       L_618A                          ; 6153   0200 0035
        B       L_619C                          ; 6155   0200 0045
        B       L_61B3                          ; 6157   0200 005A

L_6159:
        ADDI    #$033D, R1                      ; 6159   02F9 033D
        MVI@    R1,     R0                      ; 615B   0288
        SDBD                                    ; 615C   0001
        CMPI    #$5B30, R0                      ; 615D   0378 0030 005B
        BNEQ    L_6173                          ; 6160   020C 0011

        ADDI    #$0010, R1                      ; 6162   02F9 0010
        MVII    #$00F0, R0                      ; 6164   02B8 00F0
        MVO@    R0,     R1                      ; 6166   0248
        SUBI    #$034D, R1                      ; 6167   0339 034D
        MOVR    R1,     R3                      ; 6169   008B

        JSR     R5,     L_5FA7                  ; 616A   0004 015C 03A7

        SLL     R3,     1                       ; 616D   004B
        ADDI    #$0126, R3                      ; 616E   02FB 0126

        JSR     R5,     L_603F                  ; 6170   0004 0160 003F

L_6173:
        B       L_61D2                          ; 6173   0200 005D

L_6175:
        JSR     R5,     L_678F                  ; 6175   0004 0164 038F

        B       L_61D2                          ; 6178   0200 0058

L_617A:
        TSTR    R1                              ; 617A   0089
        BNEQ    L_6188                          ; 617B   020C 000B

        MVI     G_01AB, R0                      ; 617D   0280 01AB
        TSTR    R0                              ; 617F   0080
        BNEQ    L_61D2                          ; 6180   020C 0050

        SDBD                                    ; 6182   0001
        MVII    #$0987, R0                      ; 6183   02B8 0087 0009
        MVO     R0,     G_0335                  ; 6186   0240 0335
L_6188:
        B       L_61D2                          ; 6188   0200 0048

L_618A:
        TSTR    R1                              ; 618A   0089
        BNEQ    L_61D2                          ; 618B   020C 0045

        MVI     G_01AB, R0                      ; 618D   0280 01AB
        TSTR    R0                              ; 618F   0080
        BNEQ    L_61D2                          ; 6190   020C 0040

        MVII    #$007E, R0                      ; 6192   02B8 007E
        MVO     R0,     G_017F                  ; 6194   0240 017F
        MVII    #$021C, R0                      ; 6196   02B8 021C
        MVO     R0,     G_034E                  ; 6198   0240 034E
        B       L_61D2                          ; 619A   0200 0036

L_619C:
        TSTR    R1                              ; 619C   0089
        BNEQ    L_61D2                          ; 619D   020C 0033

        MVI     G_01AB, R0                      ; 619F   0280 01AB
        TSTR    R0                              ; 61A1   0080
        BNEQ    L_61D2                          ; 61A2   020C 002E

        MVII    #$0325, R3                      ; 61A4   02BB 0325
        MVII    #$0020, R1                      ; 61A6   02B9 0020
        SWAP    R1,     1                       ; 61A8   0041
        MOVR    R1,     R0                      ; 61A9   0088
        XORI    #$0100, R0                      ; 61AA   03F8 0100

        JSR     R5,     L_692A                  ; 61AC   0004 0168 012A

        MVII    #$021C, R0                      ; 61AF   02B8 021C
        MVO     R0,     G_034E                  ; 61B1   0240 034E
L_61B3:
        B       L_61D2                          ; 61B3   0200 001D

        PSHR    R5                              ; 61B5   0275
        MVI     G_018D, R0                      ; 61B6   0280 018D
        CMPI    #$0006, R0                      ; 61B8   0378 0006
        BNEQ    L_61E6                          ; 61BA   020C 002A

        MOVR    R2,     R3                      ; 61BC   0093

        JSR     R5,     L_6054                  ; 61BD   0004 0160 0054

        MVI@    R4,     R0                      ; 61C0   02A0
        ANDI    #$01F8, R0                      ; 61C1   03B8 01F8
        CMPI    #$0008, R0                      ; 61C3   0378 0008
        BLT     L_61E6                          ; 61C5   0205 001F

        CMPI    #$0030, R0                      ; 61C7   0378 0030
        BGT     L_61E6                          ; 61C9   020E 001B

        MVII    #$0016, R0                      ; 61CB   02B8 0016
        SWAP    R0,     1                       ; 61CD   0040
        DECR    R4                              ; 61CE   0014
        MVO@    R0,     R4                      ; 61CF   0260
        INCR    R7                              ; 61D0   000F

        PSHR    R5                              ; 61D1   0275
L_61D2:
        MVII    #$0003, R3                      ; 61D2   02BB 0003

        JSR     R5,     L_5F60                  ; 61D4   0004 015C 0360
        JSR     R5,     .EXEC.A83               ; 61D7   0004 0118 0283

        CLRR    R1                              ; 61DA   01C9
        MVO     R1,     G_018D                  ; 61DB   0241 018D
        MVII    #$0328, R3                      ; 61DD   02BB 0328
        SDBD                                    ; 61DF   0001
        MVII    #$5A6A, R4                      ; 61E0   02BC 006A 005A

        JSR     R5,     L_5FC3                  ; 61E3   0004 015C 03C3

L_61E6:
        PULR    R7                              ; 61E6   02B7

        COMR    R0                              ; 61E7   0018
        ADDR    R0,     R7                      ; 61E8   00C7

        ADDR    R6,     R0                      ; 61E9   00F0
        ADDR    R7,     R0                      ; 61EA   00F8
        ADDR    R5,     R0                      ; 61EB   00E8
        SARC    R0,     1                       ; 61EC   0078
        ADDR    R6,     R0                      ; 61ED   00F0
        ADDI    #$00F7, R0                      ; 61EE   02F8 00F7
        ADDI    #$00EF, R7                      ; 61F0   02FF 00EF

        ADDR    R4,     R6                      ; 61F2   00E6
        SUBR    R0,     R0                      ; 61F3   0100
        ADDR    R5,     R7                      ; 61F4   00EF

        DECLE   $00FF,  $007F,  $01FF,  $00FD   ; 61F5   00FF 007F 01FF 00FD
        DECLE   $01F8,  $00F0,  $00F8,  $00E8   ; 61F9   01F8 00F0 00F8 00E8
        DECLE   $00F8,  $00F0,  $00B8,  $0100   ; 61FD   00F8 00F0 00B8 0100
        DECLE   $0080,  $00C0,  $03E0,  $01E0   ; 6201   0080 00C0 03E0 01E0
        DECLE   $00FF,  $007F,  $0300,  $0100   ; 6205   00FF 007F 0300 0100
        DECLE   $00E0,  $00EC,  $03ED,  $00EC   ; 6209   00E0 00EC 03ED 00EC
        DECLE   $00E0,  $00E0,  $00EC,  $03ED   ; 620D   00E0 00E0 00EC 03ED
        DECLE   $00EC,  $00E0,  $007F,  $002E   ; 6211   00EC 00E0 007F 002E
        DECLE   $003A,  $0036,  $006C,  $0074   ; 6215   003A 0036 006C 0074
        DECLE   $005C,  $00FE,  $00FF,  $0000   ; 6219   005C 00FE 00FF 0000
        DECLE   $00FF,  $01FE,  $00FF,  $0000   ; 621D   00FF 01FE 00FF 0000
        DECLE   $00FF                           ; 6221   00FF

        MVI@    R5,     R3                      ; 6222   02AB
        ANDR    R5,     R2                      ; 6223   01AA
        MVI@    R5,     R3                      ; 6224   02AB
        SUBR    R0,     R0                      ; 6225   0100
        MOVR    R0,     R7                      ; 6226   0087

        DECLE   $009D,  $00FD,  $003F,  $0018   ; 6227   009D 00FD 003F 0018
        DECLE   $003C,  $0042,  $0081,  $0099   ; 622B   003C 0042 0081 0099
        DECLE   $00BD,  $005A,  $0024,  $00DB   ; 622F   00BD 005A 0024 00DB
        DECLE   $007E,  $0000,  $0018,  $0024   ; 6233   007E 0000 0018 0024
        DECLE   $0018,  $00BD,  $00FF,  $00A5   ; 6237   0018 00BD 00FF 00A5
        DECLE   $00FF,  $0000,  $003C,  $004A   ; 623B   00FF 0000 003C 004A
        DECLE   $00D1,  $0085,  $00A9,  $004A   ; 623F   00D1 0085 00A9 004A
        DECLE   $003C,  $00FF                   ; 6243   003C 00FF

        ADDR    R7,     R1                      ; 6245   00F9
        ADDR    R6,     R3                      ; 6246   00F3
        ADDR    R4,     R7                      ; 6247   00E7
        ADDR    R1,     R7                      ; 6248   00CF

        DECLE   $007E,  $003C,  $0018,  $0099   ; 6249   007E 003C 0018 0099
        DECLE   $01BD,  $00FF                   ; 624D   01BD 00FF

        SWAP    R2,     1                       ; 624F   0042
        CMPR    R4,     R6                      ; 6250   0166
        NEGR    R4                              ; 6251   0024
        ADDR    R0,     R1                      ; 6252   00C1
        RLC     R1,     2                       ; 6253   0055
        SARC    R3,     2                       ; 6254   007F
        CMP@    R2,     R5                      ; 6255   0355
        RSWD    R6                              ; 6256   003E
        COMR    R0                              ; 6257   0018
        RSWD    R4                              ; 6258   003C
        COMR    R0                              ; 6259   0018
        RSWD    R4                              ; 625A   003C
        SAR     R2,     2                       ; 625B   006E
        ADDR    R3,     R7                      ; 625C   00DF

        DECLE   $006E,  $003C,  $0100,  $0040   ; 625D   006E 003C 0100 0040
        DECLE   $00BF                           ; 6261   00BF

        SWAP    R1,     2                       ; 6262   0045
        B       L_62A1                          ; 6263   0200 003C

        DECLE   $0042,  $0099,  $0191,  $0099   ; 6265   0042 0099 0191 0099
        DECLE   $0042,  $003C,  $0000           ; 6269   0042 003C 0000

        SARC    R0,     1                       ; 626C   0078
        COMR    R6                              ; 626D   001E
        ADDR    R7,     R4                      ; 626E   00FC
        SUBR    R3,     R0                      ; 626F   0118
        GSWD    R1                              ; 6270   0031
        RRC     R3,     1                       ; 6271   0073
        SUBR    R0,     R0                      ; 6272   0100
        DECR    R0                              ; 6273   0010
        RSWD    R3                              ; 6274   003B
        SARC    R3,     2                       ; 6275   007F
        ADDI    #$000F, R7                      ; 6276   02FF 000F

        RSWD    R4                              ; 6278   003C
        ADDR    R7,     R0                      ; 6279   00F8
        ADDR    R6,     R0                      ; 627A   00F0
        ADDR    R4,     R2                      ; 627B   00E2
        ADDR    R1,     R2                      ; 627C   00CA
        MOVR    R3,     R7                      ; 627D   009F

        DECLE   $0039,  $0000,  $0009,  $0095   ; 627E   0039 0000 0009 0095
        DECLE   $01FF,  $0095,  $0009,  $0000   ; 6282   01FF 0095 0009 0000
        DECLE   $0000                           ; 6286   0000
L_6287:
        MOVR    R0,     R3                      ; 6287   0083
        DECLE   $001F,  $01FD,  $001F,  $0083   ; 6288   001F 01FD 001F 0083
        DECLE   $0000                           ; 628C   0000

        ADDR    R6,     R1                      ; 628D   00F1
        ADDR    R3,     R7                      ; 628E   00DF

        MOVR    R7,     R6                      ; 628F   00BE
        CMPR    R6,     R6                      ; 6290   0176
        MOVR    R7,     R6                      ; 6291   00BE
        ADDR    R3,     R7                      ; 6292   00DF

        DECLE   $00F1,  $0000                   ; 6293   00F1 0000

        CLRC                                    ; 6295   0006
        INCR    R7                              ; 6296   000F

        MOVR    R3,     R1                      ; 6297   0099
L_6298:
        ADDR    R6,     R3                      ; 6298   00F3
        DECLE   $00E6,  $000C,  $0000           ; 6299   00E6 000C 0000

        RRC     R3,     1                       ; 629C   0073
        GSWD    R1                              ; 629D   0031
        SUBR    R3,     R0                      ; 629E   0118
        ADDR    R7,     R4                      ; 629F   00FC
        COMR    R6                              ; 62A0   001E
L_62A1:
        SARC    R0,     1                       ; 62A1   0078
        DECLE   $0000                           ; 62A2   0000

        ADDI    #$007F, R7                      ; 62A3   02FF 007F

        RSWD    R3                              ; 62A5   003B
        DECR    R0                              ; 62A6   0010
        SUBR    R0,     R0                      ; 62A7   0100
        RSWD    R1                              ; 62A8   0039
        MOVR    R3,     R7                      ; 62A9   009F

        ADDR    R1,     R2                      ; 62AA   00CA
        ADDR    R4,     R2                      ; 62AB   00E2
        ADDR    R6,     R0                      ; 62AC   00F0
        ADDR    R7,     R0                      ; 62AD   00F8
        RSWD    R4                              ; 62AE   003C
        INCR    R7                              ; 62AF   000F

        DECLE   $0000                           ; 62B0   0000
L_62B1:
        ADCR    R0                              ; 62B1   0028
        SARC    R3,     2                       ; 62B2   007F
        COMR    R0                              ; 62B3   0018
        ADCR    R7                              ; 62B4   002F

        INCR    R5                              ; 62B5   000D
L_62B6:
        DECR    R0                              ; 62B6   0010
        DECLE   $0000,  $0090,  $0020,  $00FE   ; 62B7   0000 0090 0020 00FE
        DECLE   $003F                           ; 62BB   003F

        SARC    R0,     1                       ; 62BC   0078
        MOVR    R3,     R7                      ; 62BD   009F

        DECLE   $0004,  $0020,  $0040,  $0020   ; 62BE   0004 0020 0040 0020
        DECLE   $00FD,  $007F,  $003B,  $001E   ; 62C2   00FD 007F 003B 001E
        DECLE   $0024,  $0008,  $0000,  $0040   ; 62C6   0024 0008 0000 0040
        DECLE   $001B,  $003F,  $007C,  $00FF   ; 62CA   001B 003F 007C 00FF
L_LEVEL_DATA:
        DECLE   $0020,  $0010,  $00F9,  $0056   ; 62CE   0020 0010 00F9 0056
        DECLE   $009B,  $0057,  $0080,  $0057   ; 62D2   009B 0057 0080 0057
        DECLE   $0000,  $0000,  $0000,  $0000   ; 62D6   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 62DA   0000 0000 0000 0000

        ADDR    R6,     R0                      ; 62DE   00F0
        ADDR    R6,     R0                      ; 62DF   00F0
        RRC     R0,     1                       ; 62E0   0070
L_62E1:
        NEGR    R0                              ; 62E1   0020
        DECLE   $0020,  $0000,  $0000,  $0000   ; 62E2   0020 0000 0000 0000
        DECLE   $00F0,  $00F0,  $00F0,  $0070   ; 62E6   00F0 00F0 00F0 0070
        DECLE   $0070,  $0020,  $00A0,  $00A0   ; 62EA   0070 0020 00A0 00A0
        DECLE   $00F0,  $00F0,  $0070,  $0020   ; 62EE   00F0 00F0 0070 0020
        DECLE   $0020,  $0000,  $0000,  $0000   ; 62F2   0020 0000 0000 0000
        DECLE   $00DA,  $0057,  $0000,  $0000   ; 62F6   00DA 0057 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 62FA   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 62FE   0000 0000 0000 0000
        DECLE   $0080,  $0080,  $00D0,  $00D0   ; 6302   0080 0080 00D0 00D0
        DECLE   $00F0,  $00F0,  $00A0,  $00A0   ; 6306   00F0 00F0 00A0 00A0
        DECLE   $0080,  $00D0,  $00D0,  $00F0   ; 630A   0080 00D0 00D0 00F0
        DECLE   $00F0,  $00F0,  $0000,  $0000   ; 630E   00F0 00F0 0000 0000

        TSTR    R0                              ; 6312   0080
        TSTR    R0                              ; 6313   0080
        ADDR    R2,     R0                      ; 6314   00D0
        ADDR    R2,     R0                      ; 6315   00D0
        ADDR    R6,     R0                      ; 6316   00F0
        ADDR    R6,     R0                      ; 6317   00F0
L_6318:
        PSHR    R5                              ; 6318   0275

        JSR     R5,     L_6361                  ; 6319   0004 0160 0361

        MOVR    R3,     R2                      ; 631C   009A
        ADDI    #$0345, R3                      ; 631D   02FB 0345
        MVO@    R1,     R3                      ; 631F   0259
        INCR    R3                              ; 6320   000B
        MVO@    R1,     R3                      ; 6321   0259
        MOVR    R2,     R3                      ; 6322   0093
        INCR    R2                              ; 6323   000A
L_6324:
        SLL     R2,     1                       ; 6324   004A
        ADDI    #$0126, R2                      ; 6325   02FA 0126

        JSR     R5,     L_6332                  ; 6327   0004 0160 0332

        ADDI    #$032D, R3                      ; 632A   02FB 032D
        MVII    #$0002, R2                      ; 632C   02BA 0002

        JSR     R5,     L_6344                  ; 632E   0004 0160 0344

        PULR    R7                              ; 6331   02B7

L_6332:
        PSHR    R5                              ; 6332   0275
        MOVR    R0,     R1                      ; 6333   0081
        SLL     R0,     1                       ; 6334   0048
        ADDR    R0,     R4                      ; 6335   00C4
        MVI@    R4,     R0                      ; 6336   02A0

        JSR     R5,     X_EXT_SIGN_LO           ; 6337   0004 0114 0268

        MVO@    R0,     R2                      ; 633A   0250
        ADDI    #$0010, R2                      ; 633B   02FA 0010
        MVI@    R4,     R0                      ; 633D   02A0

        JSR     R5,     X_EXT_SIGN_LO           ; 633E   0004 0114 0268

        MVO@    R0,     R2                      ; 6341   0250
        MOVR    R1,     R0                      ; 6342   0088
        PULR    R7                              ; 6343   02B7

L_6344:
        PSHR    R5                              ; 6344   0275
        PSHR    R2                              ; 6345   0272
        SDBD                                    ; 6346   0001
        MVII    #$635D, R4                      ; 6347   02BC 005D 0063
        MOVR    R0,     R1                      ; 634A   0081
        SLR     R1,     2                       ; 634B   0065
        ADDR    R1,     R4                      ; 634C   00CC
        MVI@    R4,     R1                      ; 634D   02A1
        SWAP    R1,     1                       ; 634E   0041
        SDBD                                    ; 634F   0001
        MVII    #$F3FF, R5                      ; 6350   02BD 00FF 00F3
L_6353:
        MVI@    R3,     R4                      ; 6353   029C
        ANDR    R5,     R4                      ; 6354   01AC
        XORR    R1,     R4                      ; 6355   01CC
        MVO@    R4,     R3                      ; 6356   025C
        INCR    R3                              ; 6357   000B
        DECR    R2                              ; 6358   0012
        BNEQ    L_6353                          ; 6359   022C 0007

        SUB@    R6,     R3                      ; 635B   0333
        PULR    R7                              ; 635C   02B7

        DECLE   $0000,  $0004                   ; 635D   0000 0004

        INCR    R4                              ; 635F   000C
        INCR    R0                              ; 6360   0008
L_6361:
        MVII    #$0008, R2                      ; 6361   02BA 0008
        MOVR    R0,     R1                      ; 6363   0081
        CMPI    #$0004, R1                      ; 6364   0379 0004
        BLE     L_6373                          ; 6366   0206 000B

        CMPI    #$0008, R1                      ; 6368   0379 0008
        BLE     L_6371                          ; 636A   0206 0005

        CMPI    #$000C, R1                      ; 636C   0379 000C
        BLT     L_6373                          ; 636E   0205 0003

        SUBR    R2,     R1                      ; 6370   0111
L_6371:
        SUBR    R1,     R2                      ; 6371   010A
        MOVR    R2,     R1                      ; 6372   0091
L_6373:
        ANDI    #$0007, R1                      ; 6373   03B9 0007
        MOVR    R5,     R7                      ; 6375   00AF

        PSHR    R5                              ; 6376   0275
L_6377:
        SDBD                                    ; 6377   0001
        MVII    #$64DE, R4                      ; 6378   02BC 00DE 0064
        MVI     G_019C, R0                      ; 637B   0280 019C
        MVII    #$0005, R2                      ; 637D   02BA 0005

        JSR     R5,     L_5546                  ; 637F   0004 0154 0146

        ADDR    R0,     R4                      ; 6382   00C4
        MVII    #$0010, R3                      ; 6383   02BB 0010
L_6385:
        MVI@    R4,     R0                      ; 6385   02A0
        MVI@    R4,     R1                      ; 6386   02A1

        JSR     R5,     L_6394                  ; 6387   0004 0160 0394

        TSTR    R0                              ; 638A   0080
        BMI     L_6390                          ; 638B   020B 0003

        JSR     R5,     L_63B9                  ; 638D   0004 0160 03B9

L_6390:
        DECR    R3                              ; 6390   0013
        BNEQ    L_6385                          ; 6391   022C 000D
        PULR    R7                              ; 6393   02B7

L_6394:
        SUB     G_0175, R0                      ; 6394   0300 0175
        SDBD                                    ; 6396   0001
        CMPI    #$FF97, R0                      ; 6397   0378 0097 00FF
        BGE     L_639E                          ; 639A   020D 0002

        ANDI    #$001F, R0                      ; 639C   03B8 001F
L_639E:
        TSTR    R0                              ; 639E   0080
        BLT     L_63B6                          ; 639F   0205 0015

        CMPI    #$0013, R0                      ; 63A1   0378 0013
        BGT     L_63B6                          ; 63A3   020E 0011

        SUB     G_0176, R1                      ; 63A5   0301 0176
        SDBD                                    ; 63A7   0001
        CMPI    #$FFCE, R1                      ; 63A8   0379 00CE 00FF
        BGE     L_63AF                          ; 63AB   020D 0002

        ANDI    #$000F, R1                      ; 63AD   03B9 000F
L_63AF:
        TSTR    R1                              ; 63AF   0089
        BLT     L_63B6                          ; 63B0   0205 0004

        CMPI    #$000B, R1                      ; 63B2   0379 000B
        BLE     L_63B8                          ; 63B4   0206 0002

L_63B6:
        CLRR    R0                              ; 63B6   01C0
        DECR    R0                              ; 63B7   0010
L_63B8:
        MOVR    R5,     R7                      ; 63B8   00AF

L_63B9:
        PSHR    R5                              ; 63B9   0275
        MVII    #$0200, R5                      ; 63BA   02BD 0200
        ADDR    R0,     R5                      ; 63BC   00C5
        SLL     R1,     2                       ; 63BD   004D
        ADDR    R1,     R5                      ; 63BE   00CD
        SLL     R1,     2                       ; 63BF   004D
        ADDR    R1,     R5                      ; 63C0   00CD
        PSHR    R4                              ; 63C1   0274
        SDBD                                    ; 63C2   0001
        SUBI    #$64E0, R4                      ; 63C3   033C 00E0 0064
        MOVR    R4,     R1                      ; 63C6   00A1
        CLRR    R0                              ; 63C7   01C0
        ADDI    #$0000, R0                      ; 63C8   02F8 0000
        RRC     R1,     2                       ; 63CA   0075
        RLC     R0,     2                       ; 63CB   0054
        SDBD                                    ; 63CC   0001
        ADDI    #$6580, R1                      ; 63CD   02F9 0080 0065
        MVI@    R1,     R2                      ; 63D0   028A
        RRC     R0,     2                       ; 63D1   0074
        BNC     L_63D7                          ; 63D2   0209 0003

        SLR     R2,     2                       ; 63D4   0066
        SLR     R2,     2                       ; 63D5   0066
        SLR     R2,     1                       ; 63D6   0062
L_63D7:
        ANDI    #$001F, R2                      ; 63D7   03BA 001F
        SLL     R2,     1                       ; 63D9   004A
        MOVR    R2,     R4                      ; 63DA   0094
        SLR     R2,     1                       ; 63DB   0062
        CMPI    #$0007, R2                      ; 63DC   037A 0007
        BGT     L_63EC                          ; 63DE   020E 000C

        MVII    #$0180, R1                      ; 63E0   02B9 0180
        ADD     G_019C, R1                      ; 63E2   02C1 019C
        PSHR    R5                              ; 63E4   0275

        JSR     R5,     L_646A                  ; 63E5   0004 0164 006A

        PULR    R5                              ; 63E8   02B5
        TSTR    R0                              ; 63E9   0080
        BEQ     L_63F3                          ; 63EA   0204 0007

L_63EC:
        SDBD                                    ; 63EC   0001
        ADDI    #$655E, R4                      ; 63ED   02FC 005E 0065
        SDBD                                    ; 63F0   0001
        MVI@    R4,     R0                      ; 63F1   02A0
        MVO@    R0,     R5                      ; 63F2   0268
L_63F3:
        PULR    R4                              ; 63F3   02B4
        PULR    R7                              ; 63F4   02B7

L_63F5:
        PSHR    R5                              ; 63F5   0275
L_63F6:
        MVI     G_01AB, R1                      ; 63F6   0281 01AB
        TSTR    R3                              ; 63F8   009B
        BEQ     L_63FD                          ; 63F9   0204 0002

        MVI     G_01AC, R1                      ; 63FB   0281 01AC
L_63FD:
        TSTR    R1                              ; 63FD   0089
        BNEQ    L_6458                          ; 63FE   020C 0058

        JSR     R5,     L_6054                  ; 6400   0004 0160 0054

        MVII    #$0003, R1                      ; 6403   02B9 0003
L_6405:
        MVI@    R4,     R2                      ; 6405   02A2
        SDBD                                    ; 6406   0001
        ANDI    #$09F8, R2                      ; 6407   03BA 00F8 0009
        SDBD                                    ; 640A   0001
        CMPI    #$0860, R2                      ; 640B   037A 0060 0008
        BLT     L_6416                          ; 640E   0205 0006

        SDBD                                    ; 6410   0001
        CMPI    #$08B0, R2                      ; 6411   037A 00B0 0008
        BLE     L_6421                          ; 6414   0206 000B

L_6416:
        DECR    R1                              ; 6416   0011
        BMI     L_6458                          ; 6417   020B 003F

        CMPI    #$0001, R1                      ; 6419   0379 0001
        BNEQ    L_6405                          ; 641B   022C 0017

        ADDI    #$0012, R4                      ; 641D   02FC 0012
        B       L_6405                          ; 641F   0220 001B

L_6421:
        SDBD                                    ; 6421   0001
        SUBI    #$0860, R2                      ; 6422   033A 0060 0008
        SLR     R2,     2                       ; 6425   0066
        SLR     R2,     1                       ; 6426   0062
        CMPI    #$0002, R2                      ; 6427   037A 0002
        BGT     L_6436                          ; 6429   020E 000B
        BEQ     L_6434                          ; 642B   0204 0007

        TSTR    R2                              ; 642D   0092
        BNEQ    L_6432                          ; 642E   020C 0002
        B       L_6472                          ; 6430   0200 0040
L_6432:
        B       L_64BC                          ; 6432   0200 0088
L_6434:
        B       L_64CB                          ; 6434   0200 0095

L_6436:
        SUBI    #$0003, R2                      ; 6436   033A 0003
        CMPI    #$0007, R2                      ; 6438   037A 0007
        BEQ     L_6445                          ; 643A   0204 0009

        MVI     G_01A8, R0                      ; 643C   0280 01A8
        CMPI    #$0006, R0                      ; 643E   0378 0006
        BGE     L_6458                          ; 6440   020D 0016

        INCR    R0                              ; 6442   0008
        MVO     R0,     G_01A8                  ; 6443   0240 01A8
L_6445:
        DECR    R4                              ; 6445   0014
        MVII    #$0016, R0                      ; 6446   02B8 0016
        SWAP    R0,     1                       ; 6448   0040
        MVO@    R0,     R4                      ; 6449   0260
        MVII    #$019D, R1                      ; 644A   02B9 019D
        ADD     G_019C, R1                      ; 644C   02C1 019C

        JSR     R5,     L_6459                  ; 644E   0004 0164 0059

        MVII    #$0180, R1                      ; 6451   02B9 0180
        ADD     G_019C, R1                      ; 6453   02C1 019C

        JSR     R5,     L_6466                  ; 6455   0004 0164 0066

L_6458:
        PULR    R7                              ; 6458   02B7

L_6459:
        PSHR    R5                              ; 6459   0275
        MVII    #$0001, R0                      ; 645A   02B8 0001

        JSR     R5,     L_5546                  ; 645C   0004 0154 0146

        MVI@    R1,     R2                      ; 645F   028A
        COMR    R0                              ; 6460   0018
        ANDR    R0,     R2                      ; 6461   0182
        COMR    R0                              ; 6462   0018
        XORR    R0,     R2                      ; 6463   01C2
        MVO@    R2,     R1                      ; 6464   024A
        PULR    R7                              ; 6465   02B7

L_6466:
        COMR    R0                              ; 6466   0018
        AND@    R1,     R0                      ; 6467   0388
        MVO@    R0,     R1                      ; 6468   0248
        MOVR    R5,     R7                      ; 6469   00AF

L_646A:
        PSHR    R5                              ; 646A   0275
        MVII    #$0001, R0                      ; 646B   02B8 0001

        JSR     R5,     L_5546                  ; 646D   0004 0154 0146

        AND@    R1,     R0                      ; 6470   0388
        PULR    R7                              ; 6471   02B7

L_6472:
        MVII    #$0032, R4                      ; 6472   02BC 0032
        MVI     G_01A7, R1                      ; 6474   0281 01A7
        MVII    #$019D, R3                      ; 6476   02BB 019D
        CLRR    R2                              ; 6478   01D2
L_6479:
        MVI@    R3,     R0                      ; 6479   0298
        MVII    #$0007, R5                      ; 647A   02BD 0007
L_647C:
        SARC    R0,     1                       ; 647C   0078
        BNC     L_6481                          ; 647D   0209 0002

        ADDR    R4,     R2                      ; 647F   00E2
        INCR    R1                              ; 6480   0009
L_6481:
        DECR    R5                              ; 6481   0015
        BNEQ    L_647C                          ; 6482   022C 0007

        MVI@    R3,     R0                      ; 6484   0298
        ANDI    #$0080, R0                      ; 6485   03B8 0080
        MVO@    R0,     R3                      ; 6487   0258
        INCR    R3                              ; 6488   000B
        ADDI    #$0032, R4                      ; 6489   02FC 0032
        CMPI    #$00C8, R4                      ; 648B   037C 00C8
        BLE     L_6479                          ; 648D   0226 0015

        MVO     R1,     G_01A7                  ; 648F   0241 01A7
        MVII    #$01A5, R4                      ; 6491   02BC 01A5
        SDBD                                    ; 6493   0001
        MVI@    R4,     R0                      ; 6494   02A0
        ADDR    R2,     R0                      ; 6495   00D0
        MVO     R0,     G_01A5                  ; 6496   0240 01A5
        SWAP    R0,     1                       ; 6498   0040
        MVO     R0,     G_01A6                  ; 6499   0240 01A6
        ADD     G_01AD, R2                      ; 649B   02C2 01AD
L_649D:
        CMPI    #$012C, R2                      ; 649D   037A 012C
        BLT     L_64B3                          ; 649F   0205 0012

        SUBI    #$012C, R2                      ; 64A1   033A 012C
        MVII    #$017C, R3                      ; 64A3   02BB 017C
        MVI@    R3,     R0                      ; 64A5   0298
        INCR    R0                              ; 64A6   0008
        MVO@    R0,     R3                      ; 64A7   0258
        MVI     G_033F, R0                      ; 64A8   0280 033F
        TSTR    R0                              ; 64AA   0080
        BEQ     L_649D                          ; 64AB   0224 000F

        INCR    R3                              ; 64AD   000B
        MVI@    R3,     R0                      ; 64AE   0298
        INCR    R0                              ; 64AF   0008
        MVO@    R0,     R3                      ; 64B0   0258
        B       L_649D                          ; 64B1   0220 0015

L_64B3:
        MVO     R2,     G_01AD                  ; 64B3   0242 01AD
        CLRR    R0                              ; 64B5   01C0
        MVO     R0,     G_01A8                  ; 64B6   0240 01A8

        JSR     R5,     L_57DA                  ; 64B8   0004 0154 03DA

        PULR    R7                              ; 64BB   02B7

L_64BC:
        MVII    #$019D, R2                      ; 64BC   02BA 019D
        DECLE   $02C2,  $019C,  $0290,  $03B8   ; 64BE   02C2 019C 0290 03B8
        DECLE   $0080,  $0204,  $0005,  $0001   ; 64C2   0080 0204 0005 0001

        MVII    #$004B, R0                      ; 64C6   02B8 004B
        INCR    R0                              ; 64C8   0008
        MVO@    R0,     R4                      ; 64C9   0260
        PULR    R7                              ; 64CA   02B7

L_64CB:
        SDBD                                    ; 64CB   0001
        MVII    #$EFF8, R0                      ; 64CC   02B8 00F8 00EF
        MVII    #$0007, R1                      ; 64CF   02B9 0007
        TSTR    R3                              ; 64D1   009B
        BEQ     L_64D8                          ; 64D2   0204 0004

        SDBD                                    ; 64D4   0001
        MVII    #$1005, R1                      ; 64D5   02B9 0005 0010
L_64D8:
        ADDI    #$0335, R3                      ; 64D8   02FB 0335
        AND@    R3,     R0                      ; 64DA   0398
        XORR    R1,     R0                      ; 64DB   01C8
        MVO@    R0,     R3                      ; 64DC   0258
        PULR    R7                              ; 64DD   02B7

        DECLE   $0014,  $0020,  $006C,  $0011   ; 64DE   0014 0020 006C 0011
        DECLE   $004C,  $0027,  $004C,  $0001   ; 64E2   004C 0027 004C 0001
        DECLE   $006C,  $0007,  $003A,  $001E   ; 64E6   006C 0007 003A 001E
        DECLE   $005C,  $0031,  $000C,  $0020   ; 64EA   005C 0031 000C 0020
        DECLE   $0026,  $0036,  $0033,  $0009   ; 64EE   0026 0036 0033 0009
        DECLE   $004F,  $0019,  $000C,  $0027   ; 64F2   004F 0019 000C 0027

        ADCR    R7                              ; 64F6   002F

        ADCR    R1                              ; 64F7   0029
L_64F8:
        RRC     R1,     1                       ; 64F8   0071
        DECLE   $0022,  $0006,  $0036           ; 64F9   0022 0006 0036

        ADCR    R3                              ; 64FC   002B
        INCR    R6                              ; 64FD   000E
        SAR     R0,     1                       ; 64FE   0068
        CLRC                                    ; 64FF   0006
        ADCR    R3                              ; 6500   002B
        NEGR    R1                              ; 6501   0021
        SAR     R0,     2                       ; 6502   006C
        INCR    R2                              ; 6503   000A
        NEGR    R4                              ; 6504   0024
        NEGR    R2                              ; 6505   0022
        SARC    R1,     2                       ; 6506   007D
        INCR    R2                              ; 6507   000A
        SLL     R1,     2                       ; 6508   004D
        ADCR    R6                              ; 6509   002E
        INCR    R7                              ; 650A   000F

        INCR    R1                              ; 650B   0009
L_650C:
        SAR     R3,     2                       ; 650C   006F
        DECLE   $0029,  $000C,  $0018,  $000C   ; 650D   0029 000C 0018 000C
        DECLE   $0037                           ; 6511   0037

        ADCR    R5                              ; 6512   002D
        ADCR    R6                              ; 6513   002E
        ADCR    R5                              ; 6514   002D
        INCR    R2                              ; 6515   000A
        RLC     R0,     2                       ; 6516   0054
        NEGR    R4                              ; 6517   0024
        INCR    R7                              ; 6518   000F

        ADCR    R1                              ; 6519   0029
L_651A:
        SAR     R0,     2                       ; 651A   006C
        DECLE   $0037,  $001A,  $0002,  $0029   ; 651B   0037 001A 0002 0029
        DECLE   $0021,  $004C,  $0001,  $002C   ; 651F   0021 004C 0001 002C
        DECLE   $0012,  $0045,  $0002,  $0002   ; 6523   0012 0045 0002 0002
        DECLE   $001A,  $003D,  $002A,  $002F   ; 6527   001A 003D 002A 002F
        DECLE   $0009,  $0004                   ; 652B   0009 0004

        NEGR    R6                              ; 652D   0026
        DECR    R3                              ; 652E   0013
        ADCR    R6                              ; 652F   002E
        INCR    R3                              ; 6530   000B
        RSWD    R5                              ; 6531   003D
        RLC     R2,     1                       ; 6532   0052
        COMR    R0                              ; 6533   0018
        RSWD    R2                              ; 6534   003A
        NEGR    R2                              ; 6535   0022
L_6536:
        RLC     R3,     1                       ; 6536   0053
        DECLE   $0036,  $0073,  $0028,  $0075   ; 6537   0036 0073 0028 0075
        DECLE   $002A,  $002A,  $002E,  $004B   ; 653B   002A 002A 002E 004B
        DECLE   $0001,  $0054,  $0001           ; 653F   0001 0054 0001

        RSWD    R4                              ; 6542   003C
        GSWD    R0                              ; 6543   0030
        COMR    R6                              ; 6544   001E
        DECR    R0                              ; 6545   0010
        INCR    R4                              ; 6546   000C
        ADCR    R6                              ; 6547   002E
        SLL     R1,     2                       ; 6548   004D
L_6549:
        DECR    R7                              ; 6549   0017

        SLL     R3,     2                       ; 654A   004F
L_654B:
        DECR    R7                              ; 654B   0017

        RLC     R1,     1                       ; 654C   0051
L_654D:
        DECR    R7                              ; 654D   0017

        DECLE   $0074,  $0004                   ; 654E   0074 0004

        SAR     R3,     1                       ; 6550   006B
        INCR    R7                              ; 6551   000F

        CLRC                                    ; 6552   0006
L_6553:
        DECR    R6                              ; 6553   0016
        ADCR    R7                              ; 6554   002F

        COMR    R1                              ; 6555   0019
L_6556:
        ADCR    R4                              ; 6556   002C
        SETC                                    ; 6557   0007
        GSWD    R2                              ; 6558   0032
        RSWD    R2                              ; 6559   003A
        ADCR    R3                              ; 655A   002B
        RSWD    R4                              ; 655B   003C
        SLL     R3,     2                       ; 655C   004F
        RSWD    R0                              ; 655D   0038
        SARC    R2,     2                       ; 655E   007E
        COMR    R6                              ; 655F   001E
        MOVR    R0,     R7                      ; 6560   0087

        DECLE   $001E,  $008E,  $001E,  $0090   ; 6561   001E 008E 001E 0090
        DECLE   $001E,  $0098,  $001E,  $00A6   ; 6565   001E 0098 001E 00A6
        DECLE   $001E,  $00AE,  $001E,  $00B0   ; 6569   001E 00AE 001E 00B0
        DECLE   $001E,  $0076,  $001E,  $0060   ; 656D   001E 0076 001E 0060
        DECLE   $000E,  $006B,  $0008,  $004B   ; 6571   000E 006B 0008 004B
        DECLE   $0008,  $0053,  $001E,  $005B   ; 6575   0008 0053 001E 005B
        DECLE   $001E,  $005B,  $005E,  $005B   ; 6579   001E 005B 005E 005B
        DECLE   $009E,  $005B,  $00DE,  $01CD   ; 657D   009E 005B 00DE 01CD
        DECLE   $020F,  $010A,  $0128,  $0007   ; 6581   020F 010A 0128 0007
        DECLE   $00C1,  $0083,  $0045,  $014C   ; 6585   00C1 0083 0045 014C
        DECLE   $01CD,  $020F,  $0108,  $0020   ; 6589   01CD 020F 0108 0020
        DECLE   $0062,  $00A4,  $00E6,  $014C   ; 658D   0062 00A4 00E6 014C
        DECLE   $01CD,  $020F,  $0048,  $0020   ; 6591   01CD 020F 0048 0020
        DECLE   $0062,  $00A4,  $00E6,  $01AC   ; 6595   0062 00A4 00E6 01AC
        DECLE   $01EE,  $0050,  $0020,  $0083   ; 6599   01EE 0050 0020 0083
        DECLE   $00C5,  $0042,  $0000           ; 659D   00C5 0042 0000

        SUBR    R0,     R0                      ; 65A0   0100
        SUBR    R0,     R1                      ; 65A1   0101
        SUBR    R0,     R2                      ; 65A2   0102
        SUBR    R0,     R3                      ; 65A3   0103
        SUBR    R0,     R4                      ; 65A4   0104
        SUBR    R0,     R5                      ; 65A5   0105
        SUBR    R0,     R6                      ; 65A6   0106
        SUBR    R0,     R7                      ; 65A7   0107

        DECLE   $0108,  $0000                   ; 65A8   0108 0000

        SUBR    R3,     R0                      ; 65AA   0118
        SUBR    R3,     R1                      ; 65AB   0119
        SUBR    R3,     R2                      ; 65AC   011A
        SUBR    R3,     R3                      ; 65AD   011B
        SUBR    R3,     R4                      ; 65AE   011C
        SUBR    R3,     R5                      ; 65AF   011D
        SUBR    R3,     R6                      ; 65B0   011E
        SUBR    R3,     R7                      ; 65B1   011F

        DECLE   $0120,  $0121,  $0022,  $0030   ; 65B2   0120 0121 0022 0030
L_G02F5_DATA:
        DECLE   $0024,  $005A,  $005B,  $005B   ; 65B6   0024 005A 005B 005B
        DECLE   $0003,  $0003,  $0003,  $0003   ; 65BA   0003 0003 0003 0003
        DECLE   $0058,  $0058,  $005B,  $005D   ; 65BE   0058 0058 005B 005D
        DECLE   $005D,  $005D,  $005D,  $005D   ; 65C2   005D 005D 005D 005D
        DECLE   $0015,  $005D,  $005D,  $005D   ; 65C6   0015 005D 005D 005D
        DECLE   $005D,  $0058,  $0058,  $0058   ; 65CA   005D 0058 0058 0058
        DECLE   $0098,  $006C,  $0011,  $006D   ; 65CE   0098 006C 0011 006D
        DECLE   $0086,  $006D,  $0013,  $006E   ; 65D2   0086 006D 0013 006E
        DECLE   $009E,  $006E,  $0020,  $006F   ; 65D6   009E 006E 0020 006F
L_G02F4_DATA:
        DECLE   $009E,  $006F,  $0042,  $006A   ; 65DA   009E 006F 0042 006A
        DECLE   $0084,  $0020,  $0006,  $00A6   ; 65DE   0084 0020 0006 00A6
        DECLE   $00AA,  $0002,  $0080,  $0040   ; 65E2   00AA 0002 0080 0040
        DECLE   $002A,  $0086,  $00A2,  $0004   ; 65E6   002A 0086 00A2 0004
        DECLE   $0026,  $006A,  $0004           ; 65EA   0026 006A 0004

        MOVR    R1,     R2                      ; 65ED   008A
        MOVR    R0,     R6                      ; 65EE   0086
        NEGR    R4                              ; 65EF   0024
        SLL     R2,     1                       ; 65F0   004A
        MOVR    R5,     R0                      ; 65F1   00A8
        SLR     R0,     1                       ; 65F2   0060
        NEGR    R4                              ; 65F3   0024
        SAR     R0,     1                       ; 65F4   0068
        SWAP    R2,     2                       ; 65F5   0046
        INCR    R2                              ; 65F6   000A
        ADCR    R4                              ; 65F7   002C
        MOVR    R4,     R2                      ; 65F8   00A2
        SLL     R0,     1                       ; 65F9   0048
        INCR    R0                              ; 65FA   0008
        SLR     R0,     1                       ; 65FB   0060
L_65FC:
        PSHR    R5                              ; 65FC   0275
        MOVR    R2,     R3                      ; 65FD   0093

        JSR     R5,     L_6054                  ; 65FE   0004 0160 0054

        SDBD                                    ; 6601   0001
        MVII    #$662A, R0                      ; 6602   02B8 002A 0066
        CLRR    R1                              ; 6605   01C9
        SDBD                                    ; 6606   0001
        MVII    #$6632, R2                      ; 6607   02BA 0032 0066
L_660A:
        PSHR    R2                              ; 660A   0272
        PSHR    R1                              ; 660B   0271

        JSR     R5,     L_664E                  ; 660C   0004 0164 024E

        PULR    R2                              ; 660F   02B2
        COMR    R2                              ; 6610   001A
        ANDR    R2,     R1                      ; 6611   0191
        COMR    R2                              ; 6612   001A
        XORR    R2,     R1                      ; 6613   01D1
        PULR    R2                              ; 6614   02B2
        SDBD                                    ; 6615   0001
        ADDI    #$0007, R2                      ; 6616   02FA 0007 0000
        SDBD                                    ; 6619   0001
        CMPI    #$6647, R2                      ; 661A   037A 0047 0066
        BGT     L_6629                          ; 661D   020E 000A

        SDBD                                    ; 661F   0001
        CMPI    #$6640, R2                      ; 6620   037A 0040 0066
        BNEQ    L_660A                          ; 6623   022C 001A

        ADDI    #$0012, R4                      ; 6625   02FC 0012
        B       L_660A                          ; 6627   0220 001E
L_6629:
        PULR    R7                              ; 6629   02B7

        DECLE   $0101,  $0102,  $010A,  $0109   ; 662A   0101 0102 010A 0109
        DECLE   $0103,  $0104,  $0105,  $0000   ; 662E   0103 0104 0105 0000
        DECLE   $0005,  $0004,  $0001,  $0010   ; 6632   0005 0004 0001 0010
        DECLE   $0020,  $0041,  $0041,  $0006   ; 6636   0020 0041 0041 0006
        DECLE   $0004,  $0002,  $0010,  $0020   ; 663A   0004 0002 0010 0020
        DECLE   $0042,  $0042,  $0009,  $0008   ; 663E   0042 0042 0009 0008
        DECLE   $0001                           ; 6642   0001

        DECR    R0                              ; 6643   0010
        NEGR    R0                              ; 6644   0020
        SWAP    R1,     1                       ; 6645   0041
        SWAP    R1,     1                       ; 6646   0041
        INCR    R2                              ; 6647   000A
        INCR    R0                              ; 6648   0008
        EIS                                     ; 6649   0002
        DECR    R0                              ; 664A   0010
        NEGR    R0                              ; 664B   0020
        SWAP    R2,     1                       ; 664C   0042
        SWAP    R2,     1                       ; 664D   0042
L_664E:
        PSHR    R5                              ; 664E   0275
        PSHR    R2                              ; 664F   0272

        JSR     R5,     L_665F                  ; 6650   0004 0164 025F

        PULR    R2                              ; 6653   02B2
        TSTR    R1                              ; 6654   0089
        BEQ     L_665E                          ; 6655   0204 0007

L_6657:
        RRC     R1,     1                       ; 6657   0071
        BC      L_665D                          ; 6658   0201 0003

        INCR    R2                              ; 665A   000A
        B       L_6657                          ; 665B   0220 0005

L_665D:
        MVI@    R2,     R1                      ; 665D   0291
L_665E:
        PULR    R7                              ; 665E   02B7

L_665F:
        PSHR    R5                              ; 665F   0275
        PSHR    R0                              ; 6660   0270
        MOVR    R0,     R5                      ; 6661   0085
        SDBD                                    ; 6662   0001
        MVII    #$09F8, R0                      ; 6663   02B8 00F8 0009
        AND@    R4,     R0                      ; 6666   03A0
        CLRR    R1                              ; 6667   01C9
L_6668:
        MVI@    R5,     R2                      ; 6668   02AA
        TSTR    R2                              ; 6669   0092
        BEQ     L_6677                          ; 666A   0204 000B

        SLL     R2,     2                       ; 666C   004E
        SLL     R2,     1                       ; 666D   004A
        CMPR    R2,     R0                      ; 666E   0150
        BNEQ    L_6673                          ; 666F   020C 0002

        SETC                                    ; 6671   0007
        INCR    R7                              ; 6672   000F

L_6673:
        CLRC                                    ; 6673   0006
L_6674:
        RLC     R1,     1                       ; 6674   0051
        B       L_6668                          ; 6675   0220 000E

L_6677:
        PULR    R0                              ; 6677   02B0
        PULR    R7                              ; 6678   02B7

        PSHR    R5                              ; 6679   0275

        JSR     R5,     L_65FC                  ; 667A   0004 0164 01FC

        TSTR    R1                              ; 667D   0089
        BEQ     L_66CA                          ; 667E   0204 004A

        CMPI    #$0010, R1                      ; 6680   0379 0010
        BLT     L_6699                          ; 6682   0205 0015
        BGT     L_6688                          ; 6684   020E 0002
        B       L_6717                          ; 6686   0200 008F

L_6688:
        CMPI    #$0040, R1                      ; 6688   0379 0040
        BGE     L_668E                          ; 668A   020D 0002
        B       L_671B                          ; 668C   0200 008D

L_668E:
        MVO     R1,     G_018C                  ; 668E   0241 018C

        JSR     R5,     L_6713                  ; 6690   0004 0164 0313

        MVI     G_018C, R1                      ; 6693   0281 018C
        XORI    #$0040, R1                      ; 6695   03F9 0040
        B       L_669C                          ; 6697   0200 0003

L_6699:
        JSR     R5,     L_6932                  ; 6699   0004 0168 0132

L_669C:
        ADDI    #$0325, R3                      ; 669C   02FB 0325
        MVI@    R3,     R0                      ; 669E   0298
        SDBD                                    ; 669F   0001
        ANDI    #$FEFF, R0                      ; 66A0   03B8 00FF 00FE
        MVO@    R0,     R3                      ; 66A3   0258
        MVII    #$0001, R0                      ; 66A4   02B8 0001
        MVI     G_0179, R2                      ; 66A6   0282 0179
        COMR    R0                              ; 66A8   0018
        ANDR    R0,     R2                      ; 66A9   0182
        COMR    R0                              ; 66AA   0018
        XORR    R0,     R2                      ; 66AB   01C2
        MVO     R2,     G_0179                  ; 66AC   0242 0179
        MVII    #$0028, R0                      ; 66AE   02B8 0028
        RRC     R1,     2                       ; 66B0   0075
        BNC     L_66B6                          ; 66B1   0209 0003

        NEGR    R0                              ; 66B3   0020
        B       L_66B8                          ; 66B4   0200 0002
L_66B6:
        BNOV    L_66BA                          ; 66B6   020A 0002

L_66B8:
        MVO     R0,     G_0108                  ; 66B8   0240 0108
L_66BA:
        MVII    #$0028, R0                      ; 66BA   02B8 0028
        RRC     R1,     2                       ; 66BC   0075
        BNC     L_66C2                          ; 66BD   0209 0003

        NEGR    R0                              ; 66BF   0020
        B       L_66C4                          ; 66C0   0200 0002
L_66C2:
        BNOV    L_66C6                          ; 66C2   020A 0002

L_66C4:
        MVO     R0,     G_010C                  ; 66C4   0240 010C
L_66C6:
        MVII    #$000A, R0                      ; 66C6   02B8 000A
        MVO     R0,     G_034D                  ; 66C8   0240 034D
L_66CA:
        PULR    R7                              ; 66CA   02B7

        PSHR    R5                              ; 66CB   0275

        JSR     R5,     L_65FC                  ; 66CC   0004 0164 01FC

        TSTR    R1                              ; 66CF   0089
        BEQ     L_66F6                          ; 66D0   0204 0024

        CMPI    #$0010, R1                      ; 66D2   0379 0010
        BLT     L_66E4                          ; 66D4   0205 000E

        MOVR    R1,     R0                      ; 66D6   0088
        ANDI    #$0040, R0                      ; 66D7   03B8 0040
        BEQ     L_66F6                          ; 66D9   0204 001B

        PSHR    R1                              ; 66DB   0271
        PSHR    R3                              ; 66DC   0273

        JSR     R5,     L_6713                  ; 66DD   0004 0164 0313

        PULR    R3                              ; 66E0   02B3
        PULR    R1                              ; 66E1   02B1
        XORI    #$0040, R1                      ; 66E2   03F9 0040
L_66E4:
        MVII    #$0325, R0                      ; 66E4   02B8 0325
        MVII    #$0126, R2                      ; 66E6   02BA 0126
        MVII    #$00F8, R4                      ; 66E8   02BC 00F8

        JSR     R5,     L_66F7                  ; 66EA   0004 0164 02F7

        MVII    #$032D, R0                      ; 66ED   02B8 032D
        MVII    #$0136, R2                      ; 66EF   02BA 0136
        MVII    #$0078, R4                      ; 66F1   02BC 0078

        JSR     R5,     L_66F7                  ; 66F3   0004 0164 02F7

L_66F6:
        PULR    R7                              ; 66F6   02B7

L_66F7:
        PSHR    R5                              ; 66F7   0275
        PSHR    R3                              ; 66F8   0273
        SLL     R3,     1                       ; 66F9   004B
        ADDR    R3,     R2                      ; 66FA   00DA
        SLR     R3,     1                       ; 66FB   0063
        ADDR    R0,     R3                      ; 66FC   00C3
        MVI@    R3,     R0                      ; 66FD   0298
        RRC     R1,     2                       ; 66FE   0075
        BNC     L_6706                          ; 66FF   0209 0005

        ADDI    #$0008, R0                      ; 6701   02F8 0008
        ANDR    R4,     R0                      ; 6703   01A0
        B       L_6709                          ; 6704   0200 0003
L_6706:
        BNOV    L_6711                          ; 6706   020A 0009

        ANDR    R4,     R0                      ; 6708   01A0
L_6709:
        XORI    #$0007, R4                      ; 6709   03FC 0007
        COMR    R4                              ; 670B   001C
        AND@    R3,     R4                      ; 670C   039C
        XORR    R4,     R0                      ; 670D   01E0
        MVO@    R0,     R3                      ; 670E   0258
        CLRR    R4                              ; 670F   01E4
        MVO@    R4,     R2                      ; 6710   0254
L_6711:
        PULR    R3                              ; 6711   02B3
        PULR    R7                              ; 6712   02B7

L_6713:
        PSHR    R5                              ; 6713   0275
        MOVR    R3,     R1                      ; 6714   0099
        B       L_6797                          ; 6715   0200 0080

L_6717:
        MVII    #$0001, R1                      ; 6717   02B9 0001
        B       L_671D                          ; 6719   0200 0002

L_671B:
        CLRR    R1                              ; 671B   01C9
        DECR    R1                              ; 671C   0011
L_671D:
        SDBD                                    ; 671D   0001
        MVII    #$0008, R2                      ; 671E   02BA 0008 0000
        TSTR    R1                              ; 6721   0089
        BPL     L_6725                          ; 6722   0203 0001

        NEGR    R2                              ; 6724   0022
L_6725:
        ADD     G_019C, R1                      ; 6725   02C1 019C
        MVO     R1,     G_019C                  ; 6727   0241 019C

        JSR     R5,     L_55F7                  ; 6729   0004 0154 01F7

        ADD     G_02F4, R2                      ; 672C   02C2 02F4
        MVO     R2,     G_02F4                  ; 672E   0242 02F4
        SDBD                                    ; 6730   0001
        MVII    #$6751, R1                      ; 6731   02B9 0051 0067
        MVII    #$0002, R3                      ; 6734   02BB 0002
        MVII    #$0266, R4                      ; 6736   02BC 0266

        JSR     R5,     L_59CF                  ; 6738   0004 0158 01CF

        MVI     G_019C, R0                      ; 673B   0280 019C
        INCR    R0                              ; 673D   0008
        MVII    #$0001, R1                      ; 673E   02B9 0001

        JSR     R5,     X_PRNUM_RGT             ; 6740   0004 0118 00C5
        JSR     R5,     L_5A27                  ; 6743   0004 0158 0227

L_6746:
        MVI     G_0103, R0                      ; 6746   0280 0103
        TSTR    R0                              ; 6748   0080
        BNEQ    L_6746                          ; 6749   022C 0004

        DIS                                     ; 674B   0003

        JSR     R5,     L_5EE2                  ; 674C   0004 015C 02E2

        EIS                                     ; 674F   0002
        PULR    R7                              ; 6750   02B7

        DECLE   $0053,  $0074,  $0061,  $0069   ; 6751   0053 0074 0061 0069
        DECLE   $0072,  $0073,  $0020,  $0074   ; 6755   0072 0073 0020 0074
        DECLE   $006F,  $0020,  $006C,  $0065   ; 6759   006F 0020 006C 0065
        DECLE   $0076,  $0065,  $006C,  $0020   ; 675D   0076 0065 006C 0020
        DECLE   $0000                           ; 6761   0000

        PSHR    R5                              ; 6762   0275
        MOVR    R2,     R0                      ; 6763   0090
        DECR    R0                              ; 6764   0010
        CMPR    R0,     R1                      ; 6765   0141
        BNEQ    L_6769                          ; 6766   020C 0001
        PULR    R7                              ; 6768   02B7

L_6769:
        PSHR    R1                              ; 6769   0271
        PSHR    R2                              ; 676A   0272
        TSTR    R0                              ; 676B   0080
        BEQ     L_677B                          ; 676C   0204 000D

        MOVR    R2,     R3                      ; 676E   0093
        SDBD                                    ; 676F   0001
        MVII    #$5B58, R1                      ; 6770   02B9 0058 005B

        JSR     R5,     L_5F7C                  ; 6773   0004 015C 037C

        ADDI    #$0010, R3                      ; 6776   02FB 0010
        MVII    #$0014, R0                      ; 6778   02B8 0014
        MVO@    R0,     R3                      ; 677A   0258
L_677B:
        MVII    #$0001, R0                      ; 677B   02B8 0001

        JSR     R5,     X_RAND1                 ; 677D   0004 0114 027D

        TSTR    R0                              ; 6780   0080
        BNEQ    L_6788                          ; 6781   020C 0005

        JSR     R5,     L_6C65                  ; 6783   0004 016C 0065

        B       L_678B                          ; 6786   0200 0003

L_6788:
        JSR     R5,     L_6C74                  ; 6788   0004 016C 0074

L_678B:
        PULR    R2                              ; 678B   02B2
        PULR    R1                              ; 678C   02B1
        B       L_6797                          ; 678D   0200 0008

L_678F:
        PSHR    R5                              ; 678F   0275
        PSHR    R1                              ; 6790   0271
        PSHR    R2                              ; 6791   0272

        JSR     R5,     L_6921                  ; 6792   0004 0168 0121

        PULR    R2                              ; 6795   02B2
        PULR    R1                              ; 6796   02B1
L_6797:
        MVI     G_018B, R0                      ; 6797   0280 018B
        ANDI    #$0002, R0                      ; 6799   03B8 0002
        BEQ     L_67AE                          ; 679B   0204 0011

        CMPI    #$0002, R1                      ; 679D   0379 0002
        BNEQ    L_67AE                          ; 679F   020C 000D

        CMPI    #$0001, R2                      ; 67A1   037A 0001
        BEQ     L_67C6                          ; 67A3   0204 0021

        SDBD                                    ; 67A5   0001
        MVII    #$1005, R3                      ; 67A6   02BB 0005 0010

        JSR     R5,     L_692F                  ; 67A9   0004 0168 012F

        B       L_67C7                          ; 67AC   0200 0019

L_67AE:
        TSTR    R1                              ; 67AE   0089
        BNEQ    L_67B8                          ; 67AF   020C 0007

        MVII    #$0007, R3                      ; 67B1   02BB 0007

        JSR     R5,     L_6932                  ; 67B3   0004 0168 0132

        B       L_67C7                          ; 67B6   0200 000F

L_67B8:
        ADDI    #$032D, R1                      ; 67B8   02F9 032D
        MVI@    R1,     R0                      ; 67BA   0288
        SDBD                                    ; 67BB   0001
        ANDI    #$2000, R0                      ; 67BC   03B8 0000 0020
        BEQ     L_67C6                          ; 67BF   0204 0005

        SUBI    #$032D, R1                      ; 67C1   0339 032D

        JSR     R5,     L_684A                  ; 67C3   0004 0168 004A

L_67C6:
        PULR    R7                              ; 67C6   02B7

L_67C7:
        ADDI    #$0335, R1                      ; 67C7   02F9 0335
        MVI@    R1,     R0                      ; 67C9   0288
        SDBD                                    ; 67CA   0001
        ANDI    #$1007, R0                      ; 67CB   03B8 0007 0010
        CMPR    R3,     R0                      ; 67CE   0158
        BNEQ    L_67D3                          ; 67CF   020C 0002
        B       L_67E8                          ; 67D1   0200 0015

L_67D3:
        CLRR    R5                              ; 67D3   01ED
        SDBD                                    ; 67D4   0001
        CMPI    #$1000, R0                      ; 67D5   0378 0000 0010
        BNEQ    L_67E2                          ; 67D8   020C 0008

        MVO     R5,     G_0179                  ; 67DA   0245 0179
        MVO     R5,     G_0108                  ; 67DC   0245 0108
        MVO     R5,     G_010C                  ; 67DE   0245 010C
        B       L_67E4                          ; 67E0   0200 0002

L_67E2:
        MVO     R5,     G_018D                  ; 67E2   0245 018D
L_67E4:
        SUBI    #$0335, R1                      ; 67E4   0339 0335
        B       L_684B                          ; 67E6   0200 0063

L_67E8:
        SUBI    #$0010, R1                      ; 67E8   0339 0010
        MOVR    R1,     R3                      ; 67EA   008B
        MVII    #$0029, R0                      ; 67EB   02B8 0029
        SWAP    R0,     1                       ; 67ED   0040
        MVII    #$0028, R1                      ; 67EE   02B9 0028
        SWAP    R1,     1                       ; 67F0   0041

        JSR     R5,     L_692A                  ; 67F1   0004 0168 012A

        SUBI    #$0325, R3                      ; 67F4   033B 0325
        MOVR    R3,     R0                      ; 67F6   0098

        JSR     R5,     X_POW2                  ; 67F7   0004 0114 0345

        MVI     G_01A3, R1                      ; 67FA   0281 01A3
        XORR    R0,     R1                      ; 67FC   01C1
        MVO     R1,     G_01A3                  ; 67FD   0241 01A3
        SLL     R3,     1                       ; 67FF   004B
        BEQ     L_6809                          ; 6800   0204 0007

        ADDI    #$0126, R3                      ; 6802   02FB 0126

        JSR     R5,     L_603F                  ; 6804   0004 0160 003F

        B       L_680D                          ; 6807   0200 0004

L_6809:
        MVO     R3,     G_0108                  ; 6809   0243 0108
        MVO     R3,     G_010C                  ; 680B   0243 010C

L_680D:
        JSR     R5,     L_5FA1                  ; 680D   0004 015C 03A1
        DECLE   $0028                           ; 6810   0028

        MVI     G_01A3, R2                      ; 6811   0282 01A3
        CLRR    R0                              ; 6813   01C0
        MVO     R0,     G_01A3                  ; 6814   0240 01A3
        RRC     R2,     2                       ; 6816   0076
        BNC     L_6824                          ; 6817   0209 000B

        SDBD                                    ; 6819   0001
        MVII    #$1000, R4                      ; 681A   02BC 0000 0010
        CLRR    R3                              ; 681D   01DB

        JSR     R5,     L_6832                  ; 681E   0004 0168 0032

        CLRR    R0                              ; 6821   01C0
        MVO     R0,     G_01AB                  ; 6822   0240 01AB
L_6824:
        RRC     R2,     1                       ; 6824   0072
        BNC     L_6831                          ; 6825   0209 000A

        MVII    #$0001, R4                      ; 6827   02BC 0001
        MVII    #$0002, R3                      ; 6829   02BB 0002

        JSR     R5,     L_6832                  ; 682B   0004 0168 0032

        CLRR    R0                              ; 682E   01C0
        MVO     R0,     G_01AC                  ; 682F   0240 01AC
L_6831:
        PULR    R7                              ; 6831   02B7

L_6832:
        PSHR    R5                              ; 6832   0275
        ADDI    #$0325, R3                      ; 6833   02FB 0325
        MVII    #$0029, R0                      ; 6835   02B8 0029
        SWAP    R0,     1                       ; 6837   0040
        SDBD                                    ; 6838   0001
        MVII    #$0900, R1                      ; 6839   02B9 0000 0009

        JSR     R5,     L_692A                  ; 683C   0004 0168 012A

        ADDI    #$0010, R3                      ; 683F   02FB 0010
        SDBD                                    ; 6841   0001
        MVII    #$1007, R0                      ; 6842   02B8 0007 0010
        MOVR    R4,     R1                      ; 6845   00A1

        JSR     R5,     L_692A                  ; 6846   0004 0168 012A

        PULR    R7                              ; 6849   02B7

L_684A:
        PSHR    R5                              ; 684A   0275
L_684B:
        MOVR    R1,     R3                      ; 684B   008B
        PSHR    R3                              ; 684C   0273
        SLL     R3,     1                       ; 684D   004B
        ADDI    #$0126, R3                      ; 684E   02FB 0126

        JSR     R5,     L_603F                  ; 6850   0004 0160 003F

        CMPI    #$0136, R3                      ; 6853   037B 0136
        BNEQ    L_685A                          ; 6855   020C 0003

        JSR     R5,     L_5A27                  ; 6857   0004 0158 0227

L_685A:
        PULR    R3                              ; 685A   02B3
        ADDI    #$0325, R3                      ; 685B   02FB 0325
        MVII    #$002C, R1                      ; 685D   02B9 002C
        SWAP    R1,     1                       ; 685F   0041
        MOVR    R1,     R0                      ; 6860   0088
        XORI    #$0100, R0                      ; 6861   03F8 0100

        JSR     R5,     L_692A                  ; 6863   0004 0168 012A

        ADDI    #$0008, R3                      ; 6866   02FB 0008
        MVII    #$0100, R0                      ; 6868   02B8 0100
        MOVR    R0,     R1                      ; 686A   0081

        JSR     R5,     L_692A                  ; 686B   0004 0168 012A

        ADDI    #$0018, R3                      ; 686E   02FB 0018
        MVII    #$0040, R0                      ; 6870   02B8 0040
        MVO@    R0,     R3                      ; 6872   0258
        SDBD                                    ; 6873   0001
        MVII    #$5B94, R1                      ; 6874   02B9 0094 005B
        SUBI    #$0345, R3                      ; 6877   033B 0345

        JSR     R5,     L_5F7C                  ; 6879   0004 015C 037C

        ADDI    #$0010, R3                      ; 687C   02FB 0010
        MVII    #$0040, R0                      ; 687E   02B8 0040
        MVO@    R0,     R3                      ; 6880   0258
        SUBI    #$0027, R3                      ; 6881   033B 0027
        MVI@    R3,     R0                      ; 6883   0298
        SDBD                                    ; 6884   0001
        ANDI    #$4000, R0                      ; 6885   03B8 0000 0040
        BEQ     L_6892                          ; 6888   0204 0008

        SUBI    #$0325, R3                      ; 688A   033B 0325

        JSR     R5,     L_5F60                  ; 688C   0004 015C 0360
        JSR     R5,     L_6C54                  ; 688F   0004 016C 0054

L_6892:
        PULR    R7                              ; 6892   02B7

        PSHR    R5                              ; 6893   0275
        MVI     G_018B, R0                      ; 6894   0280 018B
        ANDI    #$0002, R0                      ; 6896   03B8 0002
        BEQ     L_68B8                          ; 6898   0204 001E

        CMPI    #$0002, R3                      ; 689A   037B 0002
        BNEQ    L_68B8                          ; 689C   020C 001A

        MVII    #$0003, R2                      ; 689E   02BA 0003

        JSR     R5,     L_607A                  ; 68A0   0004 0160 007A

        MVI     G_017D, R0                      ; 68A3   0280 017D
        TSTR    R0                              ; 68A5   0080
        BNEQ    L_68B3                          ; 68A6   020C 000B

        JSR     R5,     L_5F60                  ; 68A8   0004 015C 0360

        CLRR    R0                              ; 68AB   01C0
        MVO     R0,     G_0187                  ; 68AC   0240 0187
        INCR    R0                              ; 68AE   0008
        MVO     R0,     G_019A                  ; 68AF   0240 019A
        B       L_68FF                          ; 68B1   0200 004C

L_68B3:
        DECR    R0                              ; 68B3   0010
        MVO     R0,     G_017D                  ; 68B4   0240 017D
        B       L_68D4                          ; 68B6   0200 001C

L_68B8:
        TSTR    R3                              ; 68B8   009B
        BNEQ    L_68FC                          ; 68B9   020C 0041

        MVO     R3,     G_0108                  ; 68BB   0243 0108
        MVO     R3,     G_010C                  ; 68BD   0243 010C
        MVO     R3,     G_0179                  ; 68BF   0243 0179
        MVI     G_018B, R0                      ; 68C1   0280 018B
        ANDI    #$0080, R0                      ; 68C3   03B8 0080
        BEQ     L_68D4                          ; 68C5   0204 000D

        MVI     G_017C, R0                      ; 68C7   0280 017C
        TSTR    R0                              ; 68C9   0080
        BNEQ    L_68D1                          ; 68CA   020C 0005

        JSR     R5,     L_6BC7                  ; 68CC   0004 0168 03C7

        B       L_68FF                          ; 68CF   0200 002E

L_68D1:
        DECR    R0                              ; 68D1   0010
        MVO     R0,     G_017C                  ; 68D2   0240 017C
L_68D4:
        ADDI    #$0325, R3                      ; 68D4   02FB 0325
        MVII    #$0024, R0                      ; 68D6   02B8 0024
        SWAP    R0,     1                       ; 68D8   0040
        MVII    #$0020, R1                      ; 68D9   02B9 0020
        SWAP    R1,     1                       ; 68DB   0041

        JSR     R5,     L_692A                  ; 68DC   0004 0168 012A

        ADDI    #$0008, R3                      ; 68DF   02FB 0008
        MVI@    R3,     R0                      ; 68E1   0298
        SDBD                                    ; 68E2   0001
        ANDI    #$FE7F, R0                      ; 68E3   03B8 007F 00FE
        MVO@    R0,     R3                      ; 68E6   0258
        ADDI    #$0008, R3                      ; 68E7   02FB 0008
        MVII    #$01C0, R0                      ; 68E9   02B8 01C0
        MVO@    R0,     R3                      ; 68EB   0258
        SUBI    #$0335, R3                      ; 68EC   033B 0335
        SDBD                                    ; 68EE   0001
        MVII    #$5B9A, R1                      ; 68EF   02B9 009A 005B

        JSR     R5,     L_5F7C                  ; 68F2   0004 015C 037C

        ADDI    #$0010, R3                      ; 68F5   02FB 0010
        MVII    #$00B4, R0                      ; 68F7   02B8 00B4
        MVO@    R0,     R3                      ; 68F9   0258
        B       L_68FF                          ; 68FA   0200 0003

L_68FC:
        JSR     R5,     L_6900                  ; 68FC   0004 0168 0100

L_68FF:
        PULR    R7                              ; 68FF   02B7

L_6900:
        PSHR    R5                              ; 6900   0275

        JSR     R5,     L_6913                  ; 6901   0004 0168 0113

        MOVR    R3,     R0                      ; 6904   0098

        JSR     R5,     X_POW2                  ; 6905   0004 0114 0345

        COMR    R0                              ; 6908   0018
        AND     G_0187, R0                      ; 6909   0380 0187
        MVO     R0,     G_0187                  ; 690B   0240 0187
        MVII    #$0002, R2                      ; 690D   02BA 0002

        JSR     R5,     L_5F5E                  ; 690F   0004 015C 035E

        PULR    R7                              ; 6912   02B7

L_6913:
        MOVR    R3,     R2                      ; 6913   009A
        MVII    #$0003, R0                      ; 6914   02B8 0003
        SLR     R2,     1                       ; 6916   0062
L_6917:
        SLL     R0,     2                       ; 6917   004C
        DECR    R2                              ; 6918   0012
        BNEQ    L_6917                          ; 6919   022C 0003

        COMR    R0                              ; 691B   0018
        AND     G_017B, R0                      ; 691C   0380 017B
        MVO     R0,     G_017B                  ; 691E   0240 017B
        MOVR    R5,     R7                      ; 6920   00AF

L_6921:
        PSHR    R5                              ; 6921   0275
        MOVR    R2,     R3                      ; 6922   0093

        JSR     R5,     L_5F60                  ; 6923   0004 015C 0360
        JSR     R5,     .EXEC.A83               ; 6926   0004 0118 0283

        PULR    R7                              ; 6929   02B7

L_692A:
        COMR    R0                              ; 692A   0018
        AND@    R3,     R0                      ; 692B   0398
        XORR    R1,     R0                      ; 692C   01C8
        MVO@    R0,     R3                      ; 692D   0258
        MOVR    R5,     R7                      ; 692E   00AF

L_692F:
        MVII    #$0001, R2                      ; 692F   02BA 0001
        INCR    R7                              ; 6931   000F

L_6932:
        CLRR    R2                              ; 6932   01D2
L_6933:
        ADDI    #$01AB, R2                      ; 6933   02FA 01AB
        MVI@    R2,     R0                      ; 6935   0290
        TSTR    R0                              ; 6936   0080
        BEQ     L_693A                          ; 6937   0204 0001
        PULR    R7                              ; 6939   02B7

L_693A:
        INCR    R0                              ; 693A   0008
        MVO@    R0,     R2                      ; 693B   0250
        MOVR    R5,     R7                      ; 693C   00AF

        PSHR    R5                              ; 693D   0275
        MVI     G_019A, R0                      ; 693E   0280 019A
        TSTR    R0                              ; 6940   0080
        BNEQ    L_6945                          ; 6941   020C 0002
        B       L_6947                          ; 6943   0200 0002
L_6945:
        B       L_69A5                          ; 6945   0200 005E

L_6947:
        MVII    #$0002, R3                      ; 6947   02BB 0002

        JSR     R5,     L_5FB4                  ; 6949   0004 015C 03B4

        MVII    #$00A7, R4                      ; 694C   02BC 00A7
        MVII    #$0015, R3                      ; 694E   02BB 0015

        JSR     R5,     L_6996                  ; 6950   0004 0168 0196

        PSHR    R0                              ; 6953   0270
        MVII    #$0068, R4                      ; 6954   02BC 0068
        MVII    #$000D, R3                      ; 6956   02BB 000D
        MOVR    R1,     R0                      ; 6958   0088

        JSR     R5,     L_6996                  ; 6959   0004 0168 0196

        PULR    R1                              ; 695C   02B1
        CLRR    R5                              ; 695D   01ED
        MVII    #$007F, R2                      ; 695E   02BA 007F
        CMPR    R2,     R1                      ; 6960   0151
        BLT     L_6965                          ; 6961   0205 0002

        INCR    R5                              ; 6963   000D
        ANDR    R2,     R1                      ; 6964   0191
L_6965:
        CMPR    R2,     R0                      ; 6965   0150
        BLT     L_696A                          ; 6966   0205 0002

        INCR    R5                              ; 6968   000D
        ANDR    R2,     R1                      ; 6969   0191
L_696A:
        TSTR    R5                              ; 696A   00AD
        BEQ     L_6995                          ; 696B   0204 0028

        ADD     G_0175, R1                      ; 696D   02C1 0175
        DECR    R1                              ; 696F   0011
        ANDR    R2,     R1                      ; 6970   0191
        MVO     R1,     G_0197                  ; 6971   0241 0197
        ADD     G_0176, R0                      ; 6973   02C0 0176
        DECR    R0                              ; 6975   0010
        SLR     R2,     1                       ; 6976   0062
        ANDR    R2,     R0                      ; 6977   0190
        MVO     R0,     G_0198                  ; 6978   0240 0198
        CLRR    R0                              ; 697A   01C0
        MVO     R0,     G_0187                  ; 697B   0240 0187
        INCR    R0                              ; 697D   0008
        MVO     R0,     G_019A                  ; 697E   0240 019A
        MVI     G_0337, R1                      ; 6980   0281 0337
        SDBD                                    ; 6982   0001
        ANDI    #$1000, R1                      ; 6983   03B9 0000 0010
        BEQ     L_6989                          ; 6986   0204 0001

        DECR    R0                              ; 6988   0010
L_6989:
        MVO     R0,     G_019B                  ; 6989   0240 019B
        MVI     G_019C, R0                      ; 698B   0280 019C
        MVO     R0,     G_0199                  ; 698D   0240 0199
        MVII    #$0002, R2                      ; 698F   02BA 0002
        MOVR    R2,     R3                      ; 6991   0093

        JSR     R5,     L_5F5E                  ; 6992   0004 015C 035E

L_6995:
        PULR    R7                              ; 6995   02B7

L_6996:
        MOVR    R0,     R2                      ; 6996   0082
        SUBR    R4,     R2                      ; 6997   0122
        BGT     L_699D                          ; 6998   020E 0003

        SLR     R0,     2                       ; 699A   0064
        SLR     R0,     1                       ; 699B   0060
        MOVR    R5,     R7                      ; 699C   00AF

L_699D:
        MVII    #$0080, R0                      ; 699D   02B8 0080
        SUBI    #$000A, R2                      ; 699F   033A 000A
        BGT     L_69A4                          ; 69A1   020E 0001

        ADDR    R3,     R0                      ; 69A3   00D8
L_69A4:
        MOVR    R5,     R7                      ; 69A4   00AF

L_69A5:
        MVI     G_019C, R0                      ; 69A5   0280 019C
        CMP     G_0199, R0                      ; 69A7   0340 0199
        BNEQ    L_69F9                          ; 69A9   020C 004E

        MVI     G_0197, R0                      ; 69AB   0280 0197
        MVI     G_0198, R1                      ; 69AD   0281 0198

        JSR     R5,     L_6394                  ; 69AF   0004 0160 0394

        TSTR    R0                              ; 69B2   0080
        BMI     L_69F9                          ; 69B3   020B 0044

        PSHR    R1                              ; 69B5   0271
        PSHR    R0                              ; 69B6   0270
        MVII    #$0002, R2                      ; 69B7   02BA 0002
        MVII    #$0327, R3                      ; 69B9   02BB 0327
        SDBD                                    ; 69BB   0001
        MVII    #$5A5C, R4                      ; 69BC   02BC 005C 005A

        JSR     R5,     L_5FC1                  ; 69BF   0004 015C 03C1

        PULR    R1                              ; 69C2   02B1
        SLL     R1,     2                       ; 69C3   004D
        SLL     R1,     1                       ; 69C4   0049
        MVII    #$0008, R4                      ; 69C5   02BC 0008
        ADDR    R4,     R1                      ; 69C7   00E1
        SDBD                                    ; 69C8   0001
        MVII    #$9900, R0                      ; 69C9   02B8 0000 0099
        XORR    R0,     R1                      ; 69CC   01C1
        MVII    #$0327, R3                      ; 69CD   02BB 0327

        JSR     R5,     L_692A                  ; 69CF   0004 0168 012A

        ADDR    R4,     R3                      ; 69D2   00E3
        PULR    R1                              ; 69D3   02B1
        SLL     R1,     2                       ; 69D4   004D
        SLL     R1,     1                       ; 69D5   0049
        ADDR    R4,     R1                      ; 69D6   00E1
        SDBD                                    ; 69D7   0001
        MVII    #$A080, R0                      ; 69D8   02B8 0080 00A0
        XORR    R0,     R1                      ; 69DB   01C1

        JSR     R5,     L_692A                  ; 69DC   0004 0168 012A

        MVI     G_019B, R0                      ; 69DF   0280 019B
        TSTR    R0                              ; 69E1   0080
        BEQ     L_69EB                          ; 69E2   0204 0007

        ADDR    R4,     R3                      ; 69E4   00E3
        MVI@    R3,     R0                      ; 69E5   0298
        SDBD                                    ; 69E6   0001
        XORI    #$1004, R0                      ; 69E7   03F8 0004 0010
        MVO@    R0,     R3                      ; 69EA   0258
L_69EB:
        CLRR    R0                              ; 69EB   01C0
        MVO     R0,     G_019A                  ; 69EC   0240 019A
        MVO     R0,     G_018D                  ; 69EE   0240 018D
        MVO     R0,     G_01AC                  ; 69F0   0240 01AC
        MVII    #$0002, R3                      ; 69F2   02BB 0002
        MVI     G_0196, R0                      ; 69F4   0280 0196

        JSR     R5,     L_5885                  ; 69F6   0004 0158 0085

L_69F9:
        PULR    R7                              ; 69F9   02B7

        PSHR    R5                              ; 69FA   0275
        MVI     G_0184, R0                      ; 69FB   0280 0184
        TSTR    R0                              ; 69FD   0080
        BEQ     L_6A0A                          ; 69FE   0204 000A

        MVI     G_017E, R1                      ; 6A00   0281 017E
        DECR    R1                              ; 6A02   0011
        BNEQ    L_6A0A                          ; 6A03   020C 0005

        MVII    #$0004, R1                      ; 6A05   02B9 0004
        DECR    R0                              ; 6A07   0010
        MVO     R0,     G_0184                  ; 6A08   0240 0184
L_6A0A:
        MVO     R1,     G_017E                  ; 6A0A   0241 017E
        ADD     G_0163, R0                      ; 6A0C   02C0 0163
        MVO     R0,     G_0163                  ; 6A0E   0240 0163
        MVII    #$0005, R0                      ; 6A10   02B8 0005
        SUB     G_019C, R0                      ; 6A12   0300 019C

        JSR     R5,     X_RAND2                 ; 6A14   0004 0114 029E

        TSTR    R0                              ; 6A17   0080
        BNEQ    L_6A4D                          ; 6A18   020C 0033

        MVII    #$0002, R2                      ; 6A1A   02BA 0002
        MVII    #$0003, R0                      ; 6A1C   02B8 0003

        JSR     R5,     L_6A6A                  ; 6A1E   0004 0168 026A

        TSTR    R3                              ; 6A21   009B
        BMI     L_6A4D                          ; 6A22   020B 0029

        JSR     R5,     L_6A7D                  ; 6A24   0004 0168 027D

        ADDI    #$0325, R3                      ; 6A27   02FB 0325
        MVII    #$0002, R2                      ; 6A29   02BA 0002
        PSHR    R3                              ; 6A2B   0273

        JSR     R5,     L_5FC1                  ; 6A2C   0004 015C 03C1

        PULR    R3                              ; 6A2F   02B3
        MOVR    R3,     R2                      ; 6A30   009A
        ADDI    #$0018, R2                      ; 6A31   02FA 0018
        MVI@    R2,     R0                      ; 6A33   0290
        SDBD                                    ; 6A34   0001
        CMPI    #$5B76, R0                      ; 6A35   0378 0076 005B
        BNEQ    L_6A3F                          ; 6A38   020C 0005

        JSR     R5,     L_6AF9                  ; 6A3A   0004 0168 02F9

        B       L_6A4D                          ; 6A3D   0200 000E

L_6A3F:
        JSR     R5,     L_6A8F                  ; 6A3F   0004 0168 028F

        SUBI    #$0325, R3                      ; 6A42   033B 0325

        JSR     R5,     L_6A4E                  ; 6A44   0004 0168 024E
        JSR     R5,     L_6AAE                  ; 6A47   0004 0168 02AE
        JSR     R5,     L_6ADB                  ; 6A4A   0004 0168 02DB

L_6A4D:
        PULR    R7                              ; 6A4D   02B7

L_6A4E:
        PSHR    R5                              ; 6A4E   0275
        MOVR    R3,     R2                      ; 6A4F   009A
        MVII    #$0001, R0                      ; 6A50   02B8 0001

        JSR     R5,     L_5546                  ; 6A52   0004 0154 0146

        MOVR    R0,     R1                      ; 6A55   0081
        MVII    #$0002, R0                      ; 6A56   02B8 0002

        JSR     R5,     X_RAND2                 ; 6A58   0004 0114 029E

        TSTR    R0                              ; 6A5B   0080
        BEQ     L_6A5F                          ; 6A5C   0204 0001

        CLRR    R1                              ; 6A5E   01C9
L_6A5F:
        MVI     G_019A, R0                      ; 6A5F   0280 019A
        TSTR    R0                              ; 6A61   0080
        BEQ     L_6A65                          ; 6A62   0204 0001

        CLRR    R1                              ; 6A64   01C9
L_6A65:
        XOR     G_0187, R1                      ; 6A65   03C1 0187
        MVO     R1,     G_0187                  ; 6A67   0241 0187
        PULR    R7                              ; 6A69   02B7

L_6A6A:
        CLRR    R3                              ; 6A6A   01DB
L_6A6B:
        MVI     G_017B, R1                      ; 6A6B   0281 017B
        ANDR    R0,     R1                      ; 6A6D   0181
        BEQ     L_6A78                          ; 6A6E   0204 0008

        SLL     R0,     2                       ; 6A70   004C
        ADDI    #$0002, R3                      ; 6A71   02FB 0002
        CMPI    #$0007, R3                      ; 6A73   037B 0007
        BLE     L_6A6B                          ; 6A75   0226 000B

        NEGR    R3                              ; 6A77   0023
L_6A78:
        XOR     G_017B, R0                      ; 6A78   03C0 017B
        MVO     R0,     G_017B                  ; 6A7A   0240 017B
        MOVR    R5,     R7                      ; 6A7C   00AF

L_6A7D:
        PSHR    R5                              ; 6A7D   0275
        MVII    #$0005, R0                      ; 6A7E   02B8 0005
        SUB     G_019C, R0                      ; 6A80   0300 019C

        JSR     R5,     X_RAND2                 ; 6A82   0004 0114 029E

        SDBD                                    ; 6A85   0001
        MVII    #$5AB4, R4                      ; 6A86   02BC 00B4 005A
        TSTR    R0                              ; 6A89   0080
        BNEQ    L_6A8E                          ; 6A8A   020C 0002

        ADDI    #$001C, R4                      ; 6A8C   02FC 001C
L_6A8E:
        PULR    R7                              ; 6A8E   02B7

L_6A8F:
        PSHR    R5                              ; 6A8F   0275
        MVII    #$0004, R0                      ; 6A90   02B8 0004

        JSR     R5,     X_RAND2                 ; 6A92   0004 0114 029E

        SLL     R0,     1                       ; 6A95   0048
        SDBD                                    ; 6A96   0001
        MVII    #$6AA6, R4                      ; 6A97   02BC 00A6 006A
        ADDR    R0,     R4                      ; 6A9A   00C4
        MVI@    R4,     R0                      ; 6A9B   02A0
        XOR@    R3,     R0                      ; 6A9C   03D8
        MVO@    R0,     R3                      ; 6A9D   0258
        ADDI    #$0008, R3                      ; 6A9E   02FB 0008
        MVI@    R4,     R0                      ; 6AA0   02A0
        XOR@    R3,     R0                      ; 6AA1   03D8
        MVO@    R0,     R3                      ; 6AA2   0258
        SUBI    #$0008, R3                      ; 6AA3   033B 0008
        PULR    R7                              ; 6AA5   02B7

        DECLE   $0000,  $0034,  $0058,  $0000   ; 6AA6   0000 0034 0058 0000

        MOVR    R5,     R0                      ; 6AAA   00A8
        NOP                                     ; 6AAB   0034
        SLLC    R0,     1                       ; 6AAC   0058
        SAR     R3,     1                       ; 6AAD   006B
L_6AAE:
        PSHR    R5                              ; 6AAE   0275
        MOVR    R3,     R4                      ; 6AAF   009C
        ADDI    #$0325, R4                      ; 6AB0   02FC 0325
        PSHR    R3                              ; 6AB2   0273
        MOVR    R3,     R2                      ; 6AB3   009A
        MVII    #$0325, R3                      ; 6AB4   02BB 0325
        MVII    #$0001, R0                      ; 6AB6   02B8 0001

        JSR     R5,     L_5546                  ; 6AB8   0004 0154 0146

        AND     G_0187, R0                      ; 6ABB   0380 0187
        BEQ     L_6AC1                          ; 6ABD   0204 0002

        ADDI    #$0002, R3                      ; 6ABF   02FB 0002
L_6AC1:
        MVI@    R3,     R2                      ; 6AC1   029A
        ANDI    #$00FF, R2                      ; 6AC2   03BA 00FF
        ADDI    #$0008, R3                      ; 6AC4   02FB 0008
        MVI@    R3,     R3                      ; 6AC6   029B
        ANDI    #$007F, R3                      ; 6AC7   03BB 007F
        MOVR    R4,     R1                      ; 6AC9   00A1
        ADDI    #$0028, R1                      ; 6ACA   02F9 0028
        MVI     G_0186, R0                      ; 6ACC   0280 0186
        MVO@    R0,     R1                      ; 6ACE   0248
        MVI     G_0185, R1                      ; 6ACF   0281 0185

        JSR     R5,     L_6011                  ; 6AD1   0004 0160 0011

        PULR    R1                              ; 6AD4   02B1
        PSHR    R1                              ; 6AD5   0271

        JSR     R5,     L_5F23                  ; 6AD6   0004 015C 0323

        PULR    R3                              ; 6AD9   02B3
        PULR    R7                              ; 6ADA   02B7

L_6ADB:
        PSHR    R5                              ; 6ADB   0275
        MOVR    R3,     R2                      ; 6ADC   009A
        SLR     R2,     1                       ; 6ADD   0062
        DECR    R2                              ; 6ADE   0012
        ADDI    #$0188, R2                      ; 6ADF   02FA 0188
        MVO@    R0,     R2                      ; 6AE1   0250
        MOVR    R3,     R2                      ; 6AE2   009A
        ADDI    #$034E, R2                      ; 6AE3   02FA 034E
        MVII    #$000F, R1                      ; 6AE5   02B9 000F
        MVO@    R1,     R2                      ; 6AE7   0251
        SDBD                                    ; 6AE8   0001
        MVII    #$5BAE, R4                      ; 6AE9   02BC 00AE 005B

        JSR     R5,     L_6318                  ; 6AEC   0004 0160 0318

        PULR    R7                              ; 6AEF   02B7

        PSHR    R5                              ; 6AF0   0275
        CLRR    R0                              ; 6AF1   01C0

        JSR     R5,     L_6AAE                  ; 6AF2   0004 0168 02AE
        JSR     R5,     L_6ADB                  ; 6AF5   0004 0168 02DB

        PULR    R7                              ; 6AF8   02B7

L_6AF9:
        PSHR    R5                              ; 6AF9   0275
        PSHR    R3                              ; 6AFA   0273
        MVII    #$0010, R0                      ; 6AFB   02B8 0010

        JSR     R5,     X_RAND2                 ; 6AFD   0004 0114 029E

        MVO     R0,     G_01A1                  ; 6B00   0240 01A1
        MVII    #$001C, R1                      ; 6B02   02B9 001C
        NEGR    R1                              ; 6B04   0021

        JSR     R5,     L_6046                  ; 6B05   0004 0160 0046

        ADDI    #$0058, R1                      ; 6B08   02F9 0058
        ADDI    #$0038, R2                      ; 6B0A   02FA 0038
        MVII    #$00FF, R0                      ; 6B0C   02B8 00FF
        COMR    R0                              ; 6B0E   0018
        PULR    R3                              ; 6B0F   02B3
        MVI@    R3,     R4                      ; 6B10   029C
        ANDR    R0,     R4                      ; 6B11   0184
        XORR    R1,     R4                      ; 6B12   01CC
        MVO@    R4,     R3                      ; 6B13   025C
        ADDI    #$0008, R3                      ; 6B14   02FB 0008
        MVI@    R3,     R4                      ; 6B16   029C
        SAR     R0,     1                       ; 6B17   0068
        ANDR    R0,     R4                      ; 6B18   0184
        XORR    R2,     R4                      ; 6B19   01D4
        MVO@    R4,     R3                      ; 6B1A   025C

        JSR     R5,     L_6BEA                  ; 6B1B   0004 0168 03EA

        PULR    R7                              ; 6B1E   02B7

        PSHR    R5                              ; 6B1F   0275
        ADDI    #$0345, R3                      ; 6B20   02FB 0345
        MVI@    R3,     R0                      ; 6B22   0298
        TSTR    R0                              ; 6B23   0080
        BMI     L_6B2B                          ; 6B24   020B 0005

        JSR     R5,     L_6B32                  ; 6B26   0004 0168 0332

        B       L_6B31                          ; 6B29   0200 0006

L_6B2B:
        JSR     R5,     .EXEC.A83               ; 6B2B   0004 0118 0283
        JSR     R5,     L_6B52                  ; 6B2E   0004 0168 0352

L_6B31:
        PULR    R7                              ; 6B31   02B7

L_6B32:
        PSHR    R5                              ; 6B32   0275
        MVI     G_01A1, R0                      ; 6B33   0280 01A1
        SUBI    #$0345, R3                      ; 6B35   033B 0345

        JSR     R5,     L_5885                  ; 6B37   0004 0158 0085

        ADDI    #$0008, R3                      ; 6B3A   02FB 0008
        MVI@    R3,     R1                      ; 6B3C   0299
        XORI    #$0005, R1                      ; 6B3D   03F9 0005
        MVO@    R1,     R3                      ; 6B3F   0259
        ADDI    #$0008, R3                      ; 6B40   02FB 0008
        SDBD                                    ; 6B42   0001
        MVII    #$5B7C, R1                      ; 6B43   02B9 007C 005B
        MVO@    R1,     R3                      ; 6B46   0259
        ADDI    #$0010, R3                      ; 6B47   02FB 0010
        MVII    #$0019, R1                      ; 6B49   02B9 0019
        MVO@    R1,     R3                      ; 6B4B   0259
        SUBI    #$01E6, R3                      ; 6B4C   033B 01E6
        MVII    #$00FF, R0                      ; 6B4E   02B8 00FF
        MVO@    R0,     R3                      ; 6B50   0258
        PULR    R7                              ; 6B51   02B7

L_6B52:
        PSHR    R5                              ; 6B52   0275
        SUBI    #$0345, R3                      ; 6B53   033B 0345
        MVII    #$0002, R2                      ; 6B55   02BA 0002

        JSR     R5,     L_5F5E                  ; 6B57   0004 015C 035E

        MVII    #$0003, R0                      ; 6B5A   02B8 0003

        JSR     R5,     X_RAND2                 ; 6B5C   0004 0114 029E

        TSTR    R0                              ; 6B5F   0080
        BEQ     L_6B66                          ; 6B60   0204 0004

        JSR     R5,     L_6913                  ; 6B62   0004 0168 0113

        PULR    R7                              ; 6B65   02B7

L_6B66:
        MVII    #$0002, R2                      ; 6B66   02BA 0002
        ADDI    #$0325, R3                      ; 6B68   02FB 0325
        SDBD                                    ; 6B6A   0001
        MVII    #$5AD0, R4                      ; 6B6B   02BC 00D0 005A
        PSHR    R3                              ; 6B6E   0273

        JSR     R5,     L_5FC1                  ; 6B6F   0004 015C 03C1

        PULR    R3                              ; 6B72   02B3

        JSR     R5,     L_6AF9                  ; 6B73   0004 0168 02F9

        PULR    R7                              ; 6B76   02B7

        PSHR    R5                              ; 6B77   0275
        MOVR    R3,     R4                      ; 6B78   009C
        ADDI    #$0326, R3                      ; 6B79   02FB 0326
        MVI@    R3,     R0                      ; 6B7B   0298
        SDBD                                    ; 6B7C   0001
        ANDI    #$4000, R0                      ; 6B7D   03B8 0000 0040
        BEQ     L_6BAA                          ; 6B80   0204 0028

        ADDI    #$034D, R4                      ; 6B82   02FC 034D
        MVII    #$0023, R0                      ; 6B84   02B8 0023
        MVO@    R0,     R4                      ; 6B86   0260
        MVI@    R3,     R0                      ; 6B87   0298
        SDBD                                    ; 6B88   0001
        XORI    #$0800, R0                      ; 6B89   03F8 0000 0008
        MVO@    R0,     R3                      ; 6B8C   0258

        JSR     R5,     L_5F4F                  ; 6B8D   0004 015C 034F

        MOVR    R3,     R4                      ; 6B90   009C
        SUBI    #$0008, R4                      ; 6B91   033C 0008
        ADDI    #$0020, R3                      ; 6B93   02FB 0020
        MVII    #$0004, R2                      ; 6B95   02BA 0004
        MVO@    R2,     R3                      ; 6B97   025A
        MVI     G_0325, R2                      ; 6B98   0282 0325
        ANDI    #$00FF, R2                      ; 6B9A   03BA 00FF
        MVI     G_032D, R3                      ; 6B9C   0283 032D
        ANDI    #$007F, R3                      ; 6B9E   03BB 007F
        MVII    #$0064, R1                      ; 6BA0   02B9 0064

        JSR     R5,     L_6011                  ; 6BA2   0004 0160 0011
        JSR     R5,     L_6BF8                  ; 6BA5   0004 0168 03F8

        B       L_6BC6                          ; 6BA8   0200 001C

L_6BAA:
        ADDI    #$001F, R3                      ; 6BAA   02FB 001F
        SDBD                                    ; 6BAC   0001
        MVII    #$8023, R0                      ; 6BAD   02B8 0023 0080
        MVO@    R0,     R3                      ; 6BB0   0258
        SUBI    #$0008, R3                      ; 6BB1   033B 0008
        SDBD                                    ; 6BB3   0001
        MVII    #$5B76, R0                      ; 6BB4   02B8 0076 005B
        MVO@    R0,     R3                      ; 6BB7   0258
        SUBI    #$0008, R3                      ; 6BB8   033B 0008
        MVI@    R3,     R0                      ; 6BBA   0298
        XORI    #$0005, R0                      ; 6BBB   03F8 0005
        MVO@    R0,     R3                      ; 6BBD   0258
        ADDI    #$0018, R3                      ; 6BBE   02FB 0018
        MVII    #$002D, R0                      ; 6BC0   02B8 002D
        MVO@    R0,     R3                      ; 6BC2   0258

        JSR     R5,     L_6C54                  ; 6BC3   0004 016C 0054

L_6BC6:
        PULR    R7                              ; 6BC6   02B7

L_6BC7:
        PSHR    R5                              ; 6BC7   0275

        JSR     R5,     L_5F5B                  ; 6BC8   0004 015C 035B
        JSR     R5,     L_6076                  ; 6BCB   0004 0160 0076

        SDBD                                    ; 6BCE   0001
        MVII    #$62F4, R0                      ; 6BCF   02B8 00F4 0062
        MVO     R0,     G_035D                  ; 6BD2   0240 035D
        MVII    #$027D, R4                      ; 6BD4   02BC 027D
        SDBD                                    ; 6BD6   0001
        MVII    #$1600, R3                      ; 6BD7   02BB 0000 0016

        JSR     R5,     X_PRINT_R5              ; 6BDA   0004 0118 007B
        STRING  " GAME OVER "                   ; 6BDD  
        DECLE   $0000                           ; 6BE8   0000

        PULR    R7                              ; 6BE9   02B7

L_6BEA:
        PSHR    R5                              ; 6BEA   0275

        JSR     R5,     X_PLAY_SFX2             ; 6BEB   0004 0118 03BE
        DECLE   $0088                           ; 6BEE  SFX prio
        DECLE   $01ED                           ; 6BEF  SFX data
        DECLE   $0137                           ; 6BF0  SFX data
        DECLE   $03CB                           ; 6BF1  SFX data
        DECLE   $003C,  $00F8                   ; 6BF2  SFX data
        DECLE   $02F9                           ; 6BF4  SFX data
        DECLE   $008F,  $0020                   ; 6BF5  SFX data
        DECLE   $02CF                           ; 6BF7  SFX end

L_6BF8:
        CLRR    R0                              ; 6BF8   01C0
        PSHR    R5                              ; 6BF9   0275

        JSR     R5,     X_PLAY_SFX2             ; 6BFA   0004 0118 03BE
        DECLE   $0090                           ; 6BFD  SFX prio
        DECLE   $03ED                           ; 6BFE  SFX data
        DECLE   $03E5                           ; 6BFF  SFX data
        DECLE   $02F9                           ; 6C00  SFX data
        DECLE   $016B                           ; 6C01  SFX data
        DECLE   $0077,  $0009,  $006C           ; 6C02  SFX data
        DECLE   $0023,  $03EC                   ; 6C05  SFX data
        DECLE   $0023,  $03F8                   ; 6C07  SFX data
UC_6C09:
        MVI     G_0155, R0                      ; 6C09  SLIB UCALL target
        CMPI    #$0004, R0                      ; 6C0B   0378 0004
        BLE     L_6C14                          ; 6C0D   0206 0005

        SUBI    #$0004, R0                      ; 6C0F   0338 0004
        MVO     R0,     G_0155                  ; 6C11   0240 0155
        PULR    R7                              ; 6C13   02B7

L_6C14:
        SDBD                                    ; 6C14   0001
        MVII    #$6C07, R4                      ; 6C15   02BC 0007 006C
        PULR    R7                              ; 6C18   02B7

L_6C19:
        PSHR    R5                              ; 6C19   0275

        JSR     R5,     X_PLAY_SFX2             ; 6C1A   0004 0118 03BE
        DECLE   $0084                           ; 6C1D  SFX prio
        DECLE   $000D,  $0137                   ; 6C1E   000D 0137

        INCR    R3                              ; 6C20   000B
        INCR    R4                              ; 6C21   000C
        TSTR    R0                              ; 6C22   0080
        ADDI    #$006B, R1                      ; 6C23   02F9 006B
        ADD@    R1,     R7                      ; 6C25   02CF

L_6C26:
        PSHR    R5                              ; 6C26   0275

        JSR     R5,     X_PLAY_SFX2             ; 6C27   0004 0118 03BE
        DECLE   $0090                           ; 6C2A  SFX prio

        MOVR    R1,     R0                      ; 6C2B   0088
        SWAP    R0,     1                       ; 6C2C   0040
        XOR@    R3,     R1                      ; 6C2D   03D9
        MOVR    R5,     R3                      ; 6C2E   00AB
        MVO@    R0,     R1                      ; 6C2F   0248
        SLL     R0,     1                       ; 6C30   0048
        MOVR    R5,     R3                      ; 6C31   00AB
        ADD@    R1,     R0                      ; 6C32   02C8
        SWAP    R1,     1                       ; 6C33   0041
        MOVR    R5,     R3                      ; 6C34   00AB
        SUB@    R1,     R0                      ; 6C35   0308
        SWAP    R3,     2                       ; 6C36   0047
        MOVR    R5,     R3                      ; 6C37   00AB
        CMP@    R1,     R0                      ; 6C38   0348
        SWAP    R2,     1                       ; 6C39   0042
        MOVR    R5,     R3                      ; 6C3A   00AB
        AND@    R1,     R0                      ; 6C3B   0388
        SWAP    R2,     2                       ; 6C3C   0046
        MOVR    R5,     R3                      ; 6C3D   00AB
        XOR@    R1,     R0                      ; 6C3E   03C8
        SWAP    R3,     1                       ; 6C3F   0043
        MOVR    R5,     R3                      ; 6C40   00AB
        AND@    R1,     R0                      ; 6C41   0388
        SWAP    R1,     2                       ; 6C42   0045
        MOVR    R5,     R3                      ; 6C43   00AB
        CMP@    R1,     R0                      ; 6C44   0348
        SWAP    R0,     2                       ; 6C45   0044
        MOVR    R5,     R3                      ; 6C46   00AB
        SUB@    R1,     R0                      ; 6C47   0308
        SWAP    R2,     2                       ; 6C48   0046
        MOVR    R5,     R3                      ; 6C49   00AB
        ADD@    R1,     R0                      ; 6C4A   02C8
        SWAP    R0,     1                       ; 6C4B   0040
        MOVR    R5,     R3                      ; 6C4C   00AB
        MVO@    R0,     R1                      ; 6C4D   0248
        SWAP    R0,     2                       ; 6C4E   0044
        MOVR    R5,     R3                      ; 6C4F   00AB
        MOVR    R1,     R0                      ; 6C50   0088
        SWAP    R0,     1                       ; 6C51   0040
        MOVR    R5,     R3                      ; 6C52   00AB
        ADD@    R1,     R7                      ; 6C53   02CF

L_6C54:
        PSHR    R5                              ; 6C54   0275

        JSR     R5,     X_PLAY_SFX2             ; 6C55   0004 0118 03BE
        DECLE   $009A                           ; 6C58  SFX prio

        ADDI    #$0137, R1                      ; 6C59   02F9 0137
        INCR    R5                              ; 6C5B   000D
        INCR    R4                              ; 6C5C   000C
        B       L_6FEA                          ; 6C5D   0200 038B

        DECLE   $022B,  $003C                   ; 6C5F   022B 003C

        SUB     G_008F, R0                      ; 6C61   0300 008F
        SWAP    R0,     1                       ; 6C63   0040
        ADD@    R1,     R7                      ; 6C64   02CF

L_6C65:
        PSHR    R5                              ; 6C65   0275

        JSR     R5,     X_PLAY_SFX2             ; 6C66   0004 0118 03BE
        DECLE   $0090                           ; 6C69  SFX prio
        DECLE   $0048,  $0020,  $0137           ; 6C6A   0048 0020 0137

        INCR    R3                              ; 6C6D   000B
        ADCR    R4                              ; 6C6E   002C
        B       L_6DDE                          ; 6C6F   0200 016D

        ADD@    R3,     R1                      ; 6C71   02D9
        XOR@    R5,     R3                      ; 6C72   03EB
        ADD@    R1,     R7                      ; 6C73   02CF

L_6C74:
        PSHR    R5                              ; 6C74   0275

        JSR     R5,     X_PLAY_SFX2             ; 6C75   0004 0118 03BE
        DECLE   $0090                           ; 6C78  SFX prio
        DECLE   $0048,  $0040,  $0137           ; 6C79   0048 0040 0137

        INCR    R3                              ; 6C7C   000B
        ADCR    R4                              ; 6C7D   002C
        B       L_6F59                          ; 6C7E   0200 02D9

        CMPR    R5,     R5                      ; 6C80   016D
        XOR@    R5,     R3                      ; 6C81   03EB
        ADD@    R1,     R7                      ; 6C82   02CF

        PSHR    R5                              ; 6C83   0275
        MVI     G_01AA, R0                      ; 6C84   0280 01AA
        TSTR    R0                              ; 6C86   0080
        BEQ     L_6C97                          ; 6C87   0204 000E

        CLRR    R0                              ; 6C89   01C0
        MVI     G_017F, R1                      ; 6C8A   0281 017F
        CMPI    #$0064, R1                      ; 6C8C   0379 0064
        BGT     L_6C94                          ; 6C8E   020E 0004

        MVI@    R3,     R1                      ; 6C90   0299
        ADDI    #$0005, R1                      ; 6C91   02F9 0005
        MVO@    R1,     R3                      ; 6C93   0259

L_6C94:
        JSR     R5,     L_6C19                  ; 6C94   0004 016C 0019

L_6C97:
        PULR    R7                              ; 6C97   02B7

        INCR    R2                              ; 6C98   000A
        SUBR    R4,     R2                      ; 6C99   0122
        SLR     R1,     1                       ; 6C9A   0061
        SUBR    R4,     R5                      ; 6C9B   0125
        SLR     R1,     1                       ; 6C9C   0061
        SUBR    R4,     R6                      ; 6C9D   0126
        SLR     R1,     1                       ; 6C9E   0061
        SUBR    R5,     R0                      ; 6C9F   0128
        SLR     R1,     1                       ; 6CA0   0061
        SUBR    R4,     R7                      ; 6CA1   0127

        INCR    R2                              ; 6CA2   000A
        SUBR    R4,     R2                      ; 6CA3   0122
        SLR     R1,     1                       ; 6CA4   0061
        SUBR    R4,     R5                      ; 6CA5   0125
        SLR     R1,     1                       ; 6CA6   0061
        SUBR    R4,     R6                      ; 6CA7   0126
        SLR     R1,     1                       ; 6CA8   0061
        SUBR    R5,     R0                      ; 6CA9   0128
        SLR     R1,     1                       ; 6CAA   0061
        SUBR    R4,     R7                      ; 6CAB   0127

        DECLE   $000C,  $0122,  $0061,  $0124   ; 6CAC   000C 0122 0061 0124
        DECLE   $0001                           ; 6CB0   0001

        MOVR    R4,     R1                      ; 6CB1   00A1
        MOVR    R1,     R2                      ; 6CB2   008A
        ADDR    R4,     R1                      ; 6CB3   00E1
        SUBR    R4,     R1                      ; 6CB4   0121
        MOVR    R0,     R3                      ; 6CB5   0083
        SLR     R1,     1                       ; 6CB6   0061
        SUBR    R4,     R7                      ; 6CB7   0127

        INCR    R0                              ; 6CB8   0008
        SUBR    R4,     R2                      ; 6CB9   0122
        SLR     R1,     1                       ; 6CBA   0061
        SUBR    R4,     R5                      ; 6CBB   0125
        SLR     R1,     1                       ; 6CBC   0061
        SUBR    R5,     R7                      ; 6CBD   012F

        SLR     R1,     1                       ; 6CBE   0061
        SUBR    R4,     R7                      ; 6CBF   0127

        SETC                                    ; 6CC0   0007
        MOVR    R0,     R2                      ; 6CC1   0082
        ADDR    R0,     R1                      ; 6CC2   00C1
        SUBR    R4,     R5                      ; 6CC3   0125
        SLR     R1,     1                       ; 6CC4   0061
        SUBR    R5,     R7                      ; 6CC5   012F

        DECLE   $0088,  $0004,  $0128,  $0101   ; 6CC6   0088 0004 0128 0101
        DECLE   $0137,  $0003,  $013F,  $0121   ; 6CCA   0137 0003 013F 0121
        DECLE   $0003,  $013F,  $0121,  $0007   ; 6CCE   0003 013F 0121 0007
        DECLE   $0088,  $0061,  $012E,  $0001   ; 6CD2   0088 0061 012E 0001

        MOVR    R4,     R1                      ; 6CD6   00A1
        MOVR    R0,     R7                      ; 6CD7   0087

        CLRC                                    ; 6CD8   0006
        SUBR    R5,     R0                      ; 6CD9   0128
        SLR     R1,     1                       ; 6CDA   0061
        SUBR    R5,     R7                      ; 6CDB   012F

        SLR     R1,     1                       ; 6CDC   0061
        SUBR    R4,     R7                      ; 6CDD   0127

        CLRC                                    ; 6CDE   0006
        SUBR    R5,     R0                      ; 6CDF   0128
        SLR     R1,     1                       ; 6CE0   0061
        SUBR    R5,     R7                      ; 6CE1   012F

        SUBR    R0,     R1                      ; 6CE2   0101
        SUBR    R4,     R7                      ; 6CE3   0127

        DECLE   $0004,  $0128,  $0061,  $0137   ; 6CE4   0004 0128 0061 0137
        DECLE   $000C,  $0082,  $0061,  $0124   ; 6CE8   000C 0082 0061 0124
        DECLE   $0001                           ; 6CEC   0001

        SLR     R1,     1                       ; 6CED   0061
        SUBR    R5,     R7                      ; 6CEE   012F

        MOVR    R4,     R1                      ; 6CEF   00A1
        MOVR    R0,     R4                      ; 6CF0   0084
        ADDR    R4,     R1                      ; 6CF1   00E1
        SUBR    R4,     R1                      ; 6CF2   0121
        MOVR    R0,     R1                      ; 6CF3   0081
        INCR    R0                              ; 6CF4   0008
        SUBR    R4,     R2                      ; 6CF5   0122
        SLR     R1,     1                       ; 6CF6   0061
        SUBR    R4,     R5                      ; 6CF7   0125
        SLR     R1,     1                       ; 6CF8   0061
        SUBR    R5,     R7                      ; 6CF9   012F

        SLR     R1,     1                       ; 6CFA   0061
        SUBR    R4,     R7                      ; 6CFB   0127

        INCR    R0                              ; 6CFC   0008
        SUBR    R4,     R2                      ; 6CFD   0122
        SLR     R1,     1                       ; 6CFE   0061
        SUBR    R4,     R5                      ; 6CFF   0125
        SLR     R1,     1                       ; 6D00   0061
        SUBR    R5,     R7                      ; 6D01   012F

        SLR     R1,     1                       ; 6D02   0061
        SUBR    R4,     R7                      ; 6D03   0127

        INCR    R5                              ; 6D04   000D
        SUBR    R4,     R2                      ; 6D05   0122
        SLR     R1,     1                       ; 6D06   0061
        SUBR    R4,     R5                      ; 6D07   0125
        MOVR    R4,     R1                      ; 6D08   00A1
        MOVR    R0,     R6                      ; 6D09   0086
        MOVR    R4,     R1                      ; 6D0A   00A1
        MOVR    R0,     R4                      ; 6D0B   0084
        ADDR    R4,     R1                      ; 6D0C   00E1
        SUBR    R4,     R1                      ; 6D0D   0121
        MOVR    R0,     R2                      ; 6D0E   0082
        SLR     R1,     1                       ; 6D0F   0061
        SUBR    R4,     R7                      ; 6D10   0127

        INCR    R5                              ; 6D11   000D
        SUBR    R4,     R2                      ; 6D12   0122
        SLR     R1,     1                       ; 6D13   0061
        SUBR    R4,     R5                      ; 6D14   0125
        SLR     R1,     1                       ; 6D15   0061
        SUBR    R4,     R6                      ; 6D16   0126
        MOVR    R4,     R1                      ; 6D17   00A1
        MOVR    R0,     R3                      ; 6D18   0083
        ADDR    R4,     R1                      ; 6D19   00E1
        SUBR    R4,     R1                      ; 6D1A   0121
        MOVR    R0,     R3                      ; 6D1B   0083
        ADDR    R0,     R1                      ; 6D1C   00C1
        SUBR    R4,     R7                      ; 6D1D   0127

        DECLE   $0009,  $0122,  $0061,  $0124   ; 6D1E   0009 0122 0061 0124
        DECLE   $0001                           ; 6D22   0001

        SLR     R1,     1                       ; 6D23   0061
        SUBR    R4,     R6                      ; 6D24   0126
        SLR     R1,     1                       ; 6D25   0061
        SUBR    R6,     R0                      ; 6D26   0130
        INCR    R0                              ; 6D27   0008
        SUBR    R4,     R2                      ; 6D28   0122
        SLR     R1,     1                       ; 6D29   0061
        SUBR    R4,     R5                      ; 6D2A   0125
        SLR     R1,     1                       ; 6D2B   0061
        SUBR    R4,     R6                      ; 6D2C   0126
        SLR     R1,     1                       ; 6D2D   0061
        SUBR    R6,     R0                      ; 6D2E   0130
        SETC                                    ; 6D2F   0007
        SUBR    R4,     R2                      ; 6D30   0122
        SLR     R1,     1                       ; 6D31   0061
        SUBR    R4,     R5                      ; 6D32   0125
        MOVR    R0,     R7                      ; 6D33   0087

        DECLE   $00C1,  $0130,  $0005           ; 6D34   00C1 0130 0005

        MOVR    R0,     R5                      ; 6D37   0085
        ADDR    R4,     R1                      ; 6D38   00E1
        SUBR    R5,     R7                      ; 6D39   012F

        DECLE   $008B,  $0003,  $013F,  $0121   ; 6D3A   008B 0003 013F 0121
        DECLE   $0003,  $013F,  $0121,  $0003   ; 6D3E   0003 013F 0121 0003
        DECLE   $013F,  $0121,  $0006,  $008A   ; 6D42   013F 0121 0006 008A
        DECLE   $0061,  $0126,  $0001,  $008E   ; 6D46   0061 0126 0001 008E
        DECLE   $0004,  $012A,  $0061,  $0135   ; 6D4A   0004 012A 0061 0135
        DECLE   $0004,  $012A,  $0101,  $0135   ; 6D4E   0004 012A 0101 0135
        DECLE   $0003,  $013F                   ; 6D52   0003 013F

        SUBR    R4,     R1                      ; 6D54   0121
        DECR    R3                              ; 6D55   0013
        MOVR    R0,     R2                      ; 6D56   0082
        MOVR    R4,     R1                      ; 6D57   00A1
        MOVR    R0,     R1                      ; 6D58   0081
        ADDR    R4,     R1                      ; 6D59   00E1
        SUBR    R4,     R1                      ; 6D5A   0121
        MOVR    R0,     R2                      ; 6D5B   0082
        MOVR    R4,     R1                      ; 6D5C   00A1
        MOVR    R0,     R6                      ; 6D5D   0086
        MOVR    R4,     R1                      ; 6D5E   00A1
        MOVR    R0,     R2                      ; 6D5F   0082
        ADDR    R4,     R1                      ; 6D60   00E1
        SUBR    R4,     R2                      ; 6D61   0122
        MOVR    R0,     R3                      ; 6D62   0083
        MOVR    R4,     R1                      ; 6D63   00A1
        MOVR    R0,     R1                      ; 6D64   0081
        ADDR    R4,     R1                      ; 6D65   00E1
        SUBR    R4,     R2                      ; 6D66   0122
        MOVR    R0,     R3                      ; 6D67   0083
        INCR    R2                              ; 6D68   000A
        SUBR    R4,     R2                      ; 6D69   0122
        SLR     R1,     1                       ; 6D6A   0061
        SUBR    R4,     R5                      ; 6D6B   0125
        SLR     R1,     1                       ; 6D6C   0061
        SUBR    R4,     R6                      ; 6D6D   0126
        SLR     R1,     1                       ; 6D6E   0061
        SUBR    R5,     R0                      ; 6D6F   0128
        SLR     R1,     1                       ; 6D70   0061
        SUBR    R4,     R7                      ; 6D71   0127

        INCR    R2                              ; 6D72   000A
        SUBR    R4,     R2                      ; 6D73   0122
        SLR     R1,     1                       ; 6D74   0061
        SUBR    R4,     R5                      ; 6D75   0125
        SLR     R1,     1                       ; 6D76   0061
        SUBR    R4,     R6                      ; 6D77   0126
        SLR     R1,     1                       ; 6D78   0061
        SUBR    R5,     R0                      ; 6D79   0128
        SLR     R1,     1                       ; 6D7A   0061
        SUBR    R4,     R7                      ; 6D7B   0127

        INCR    R2                              ; 6D7C   000A
        SUBR    R4,     R2                      ; 6D7D   0122
        SLR     R1,     1                       ; 6D7E   0061
        SUBR    R4,     R5                      ; 6D7F   0125
        SLR     R1,     1                       ; 6D80   0061
        SUBR    R4,     R6                      ; 6D81   0126
        SLR     R1,     1                       ; 6D82   0061
        SUBR    R5,     R0                      ; 6D83   0128
        SLR     R1,     1                       ; 6D84   0061
        SUBR    R4,     R7                      ; 6D85   0127

        INCR    R2                              ; 6D86   000A
        SUBR    R4,     R2                      ; 6D87   0122
        SLR     R1,     1                       ; 6D88   0061
        SUBR    R4,     R5                      ; 6D89   0125
        SLR     R1,     1                       ; 6D8A   0061
        SUBR    R4,     R6                      ; 6D8B   0126
        SLR     R1,     1                       ; 6D8C   0061
        SUBR    R5,     R0                      ; 6D8D   0128
        SLR     R1,     1                       ; 6D8E   0061
        SUBR    R4,     R7                      ; 6D8F   0127

        INCR    R3                              ; 6D90   000B
L_6D91:
        SUBR    R4,     R1                      ; 6D91   0121
        DECLE   $0001                           ; 6D92   0001

        SLR     R1,     1                       ; 6D93   0061
        SUBR    R4,     R5                      ; 6D94   0125
        SLR     R1,     1                       ; 6D95   0061
        SUBR    R4,     R6                      ; 6D96   0126
        SLR     R1,     1                       ; 6D97   0061
        SUBR    R5,     R0                      ; 6D98   0128
        NEGR    R1                              ; 6D99   0021
        SUBR    R4,     R7                      ; 6D9A   0127

        INCR    R2                              ; 6D9B   000A
        SUBR    R4,     R2                      ; 6D9C   0122
        SLR     R1,     1                       ; 6D9D   0061
        SUBR    R4,     R5                      ; 6D9E   0125
        SUBR    R0,     R1                      ; 6D9F   0101
        SUBR    R4,     R6                      ; 6DA0   0126
        SLR     R1,     1                       ; 6DA1   0061
        SUBR    R5,     R0                      ; 6DA2   0128
        SWAP    R1,     1                       ; 6DA3   0041
        SUBR    R4,     R7                      ; 6DA4   0127

        INCR    R0                              ; 6DA5   0008
        SUBR    R4,     R2                      ; 6DA6   0122
        SLR     R1,     1                       ; 6DA7   0061
        SUBR    R5,     R4                      ; 6DA8   012C
        SLR     R1,     1                       ; 6DA9   0061
        SUBR    R5,     R0                      ; 6DAA   0128
        SLR     R1,     1                       ; 6DAB   0061
        SUBR    R4,     R7                      ; 6DAC   0127

        CLRC                                    ; 6DAD   0006
        MOVR    R1,     R7                      ; 6DAE   008F

        SLR     R1,     1                       ; 6DAF   0061
        SUBR    R5,     R0                      ; 6DB0   0128
        MOVR    R4,     R1                      ; 6DB1   00A1
        MOVR    R0,     R7                      ; 6DB2   0087

        CLRC                                    ; 6DB3   0006
        SUBR    R5,     R7                      ; 6DB4   012F

        SLR     R1,     1                       ; 6DB5   0061
        SUBR    R5,     R0                      ; 6DB6   0128
        SLR     R1,     1                       ; 6DB7   0061
        SUBR    R4,     R7                      ; 6DB8   0127

        CLRC                                    ; 6DB9   0006
        SUBR    R5,     R7                      ; 6DBA   012F

        SLR     R1,     1                       ; 6DBB   0061
        SUBR    R5,     R0                      ; 6DBC   0128
        NEGR    R1                              ; 6DBD   0021
        SUBR    R4,     R7                      ; 6DBE   0127

        CLRC                                    ; 6DBF   0006
        SUBR    R5,     R7                      ; 6DC0   012F

        SLR     R1,     1                       ; 6DC1   0061
        SUBR    R5,     R0                      ; 6DC2   0128
        SWAP    R1,     1                       ; 6DC3   0041
        SUBR    R4,     R7                      ; 6DC4   0127

        INCR    R2                              ; 6DC5   000A
        MOVR    R0,     R6                      ; 6DC6   0086
        ADDR    R4,     R1                      ; 6DC7   00E1
        SUBR    R4,     R4                      ; 6DC8   0124
        MOVR    R0,     R4                      ; 6DC9   0084
        SLR     R1,     1                       ; 6DCA   0061
        SUBR    R5,     R0                      ; 6DCB   0128
        MOVR    R0,     R3                      ; 6DCC   0083
        MOVR    R4,     R1                      ; 6DCD   00A1
        MOVR    R0,     R4                      ; 6DCE   0084
        INCR    R2                              ; 6DCF   000A
        SUBR    R5,     R0                      ; 6DD0   0128
        SLR     R1,     1                       ; 6DD1   0061
        SUBR    R4,     R6                      ; 6DD2   0126
        NEGR    R1                              ; 6DD3   0021
        SUBR    R5,     R0                      ; 6DD4   0128
        NEGR    R1                              ; 6DD5   0021
        SUBR    R4,     R2                      ; 6DD6   0122
        SLR     R1,     1                       ; 6DD7   0061
        SUBR    R4,     R4                      ; 6DD8   0124
        INCR    R2                              ; 6DD9   000A
        SUBR    R5,     R0                      ; 6DDA   0128
        SLR     R1,     1                       ; 6DDB   0061
        SUBR    R4,     R6                      ; 6DDC   0126
        SWAP    R1,     1                       ; 6DDD   0041
L_6DDE:
        SUBR    R5,     R0                      ; 6DDE   0128
        DECLE   $0041,  $0122,  $0061,  $0124   ; 6DDF   0041 0122 0061 0124
        DECLE   $000A,  $0128,  $0061,  $0126   ; 6DE3   000A 0128 0061 0126
        DECLE   $0061,  $0128,  $0061,  $0122   ; 6DE7   0061 0128 0061 0122
        DECLE   $0061,  $0124,  $000C,  $0082   ; 6DEB   0061 0124 000C 0082
        DECLE   $0061,  $0122,  $0083,  $00A1   ; 6DEF   0061 0122 0083 00A1
        DECLE   $0086,  $00A1,  $0088,  $00C1   ; 6DF3   0086 00A1 0088 00C1
        DECLE   $0122,  $0085,  $0008,  $0122   ; 6DF7   0122 0085 0008 0122
        DECLE   $0061,  $0125,  $0061,  $0126   ; 6DFB   0061 0125 0061 0126
        DECLE   $0061,  $0130,  $0000           ; 6DFF   0061 0130 0000

        SUBR    R4,     R2                      ; 6E02   0122
        SLR     R1,     1                       ; 6E03   0061
        SUBR    R4,     R5                      ; 6E04   0125
        SLR     R1,     1                       ; 6E05   0061
        SUBR    R4,     R6                      ; 6E06   0126
        SLR     R1,     1                       ; 6E07   0061
        SUBR    R6,     R0                      ; 6E08   0130
        INCR    R2                              ; 6E09   000A
        SUBR    R4,     R2                      ; 6E0A   0122
        SLR     R1,     1                       ; 6E0B   0061
        SUBR    R4,     R5                      ; 6E0C   0125
        SLR     R1,     1                       ; 6E0D   0061
        SUBR    R4,     R6                      ; 6E0E   0126
        SLR     R1,     1                       ; 6E0F   0061
        SUBR    R5,     R0                      ; 6E10   0128
        SLR     R1,     1                       ; 6E11   0061
        SUBR    R4,     R7                      ; 6E12   0127

        INCR    R2                              ; 6E13   000A
        SUBR    R4,     R2                      ; 6E14   0122
        SLR     R1,     1                       ; 6E15   0061
        SUBR    R4,     R5                      ; 6E16   0125
        SLR     R1,     1                       ; 6E17   0061
        SUBR    R4,     R6                      ; 6E18   0126
        SLR     R1,     1                       ; 6E19   0061
        SUBR    R5,     R0                      ; 6E1A   0128
        SLR     R1,     1                       ; 6E1B   0061
        SUBR    R4,     R7                      ; 6E1C   0127

        INCR    R2                              ; 6E1D   000A
        SUBR    R4,     R2                      ; 6E1E   0122
        SLR     R1,     1                       ; 6E1F   0061
        SUBR    R4,     R5                      ; 6E20   0125
        SLR     R1,     1                       ; 6E21   0061
        SUBR    R4,     R6                      ; 6E22   0126
        SUBR    R0,     R1                      ; 6E23   0101
        SUBR    R5,     R0                      ; 6E24   0128
        SLR     R1,     1                       ; 6E25   0061
        SUBR    R4,     R7                      ; 6E26   0127

        INCR    R0                              ; 6E27   0008
        SUBR    R4,     R2                      ; 6E28   0122
        SUBR    R0,     R1                      ; 6E29   0101
        SUBR    R4,     R5                      ; 6E2A   0125
        SLR     R1,     1                       ; 6E2B   0061
        SUBR    R5,     R7                      ; 6E2C   012F

        SLR     R1,     1                       ; 6E2D   0061
        SUBR    R4,     R7                      ; 6E2E   0127

        CLRC                                    ; 6E2F   0006
        SUBR    R5,     R0                      ; 6E30   0128
        SLR     R1,     1                       ; 6E31   0061
        SUBR    R5,     R7                      ; 6E32   012F

        SLR     R1,     1                       ; 6E33   0061
        SUBR    R4,     R7                      ; 6E34   0127

        DECLE   $000D,  $0083,  $00E1,  $0123   ; 6E35   000D 0083 00E1 0123
        DECLE   $0001                           ; 6E39   0001

        MOVR    R4,     R1                      ; 6E3A   00A1
        MOVR    R0,     R6                      ; 6E3B   0086
        SLR     R1,     1                       ; 6E3C   0061
        SUBR    R4,     R2                      ; 6E3D   0122
        MOVR    R1,     R0                      ; 6E3E   0088
        ADDR    R4,     R1                      ; 6E3F   00E1
        SUBR    R4,     R2                      ; 6E40   0122
        MOVR    R0,     R3                      ; 6E41   0083
        CLRC                                    ; 6E42   0006
        SUBR    R5,     R0                      ; 6E43   0128
        SLR     R1,     1                       ; 6E44   0061
        SUBR    R4,     R6                      ; 6E45   0126
        SLR     R1,     1                       ; 6E46   0061
        SUBR    R6,     R0                      ; 6E47   0130
        CLRC                                    ; 6E48   0006
        SUBR    R5,     R0                      ; 6E49   0128
        SLR     R1,     1                       ; 6E4A   0061
        SUBR    R4,     R6                      ; 6E4B   0126
        SLR     R1,     1                       ; 6E4C   0061
        SUBR    R6,     R0                      ; 6E4D   0130
        CLRC                                    ; 6E4E   0006
        SUBR    R5,     R0                      ; 6E4F   0128
        SLR     R1,     1                       ; 6E50   0061
        SUBR    R4,     R6                      ; 6E51   0126
        SLR     R1,     1                       ; 6E52   0061
        SUBR    R6,     R0                      ; 6E53   0130
        INCR    R0                              ; 6E54   0008
        MOVR    R0,     R4                      ; 6E55   0084
        SLR     R1,     1                       ; 6E56   0061
        SUBR    R4,     R3                      ; 6E57   0123
        SUBR    R0,     R1                      ; 6E58   0101
        SUBR    R4,     R6                      ; 6E59   0126
        MOVR    R4,     R1                      ; 6E5A   00A1
        MOVR    R2,     R0                      ; 6E5B   0090
        CLRC                                    ; 6E5C   0006
        SUBR    R4,     R4                      ; 6E5D   0124
        SLR     R1,     1                       ; 6E5E   0061
        SUBR    R5,     R2                      ; 6E5F   012A
        SLR     R1,     1                       ; 6E60   0061
        SUBR    R6,     R0                      ; 6E61   0130
        INCR    R0                              ; 6E62   0008
        SUBR    R4,     R4                      ; 6E63   0124
        SLR     R1,     1                       ; 6E64   0061
        SUBR    R4,     R3                      ; 6E65   0123
        SLR     R1,     1                       ; 6E66   0061
        SUBR    R4,     R6                      ; 6E67   0126
        SLR     R1,     1                       ; 6E68   0061
        SUBR    R6,     R0                      ; 6E69   0130
        INCR    R0                              ; 6E6A   0008
        SUBR    R4,     R4                      ; 6E6B   0124
        SLR     R1,     1                       ; 6E6C   0061
        SUBR    R4,     R3                      ; 6E6D   0123
        MOVR    R4,     R1                      ; 6E6E   00A1
        MOVR    R0,     R6                      ; 6E6F   0086
        SLR     R1,     1                       ; 6E70   0061
        SUBR    R6,     R0                      ; 6E71   0130
        DECR    R0                              ; 6E72   0010
        MOVR    R0,     R2                      ; 6E73   0082
        MOVR    R4,     R1                      ; 6E74   00A1
        MOVR    R0,     R1                      ; 6E75   0081
        ADDR    R0,     R1                      ; 6E76   00C1
        SUBR    R4,     R3                      ; 6E77   0123
        SLR     R1,     1                       ; 6E78   0061
        SUBR    R4,     R6                      ; 6E79   0126
        NEGR    R1                              ; 6E7A   0021
        SUBR    R4,     R3                      ; 6E7B   0123
        MOVR    R0,     R5                      ; 6E7C   0085
        MOVR    R4,     R1                      ; 6E7D   00A1
        MOVR    R0,     R2                      ; 6E7E   0082
        ADDR    R4,     R1                      ; 6E7F   00E1
        SUBR    R4,     R2                      ; 6E80   0122
        MOVR    R0,     R2                      ; 6E81   0082
        INCR    R2                              ; 6E82   000A
        SUBR    R4,     R2                      ; 6E83   0122
        SLR     R1,     1                       ; 6E84   0061
        SUBR    R4,     R5                      ; 6E85   0125
        SUBR    R0,     R1                      ; 6E86   0101
        SUBR    R4,     R6                      ; 6E87   0126
        SWAP    R1,     1                       ; 6E88   0041
        SUBR    R5,     R0                      ; 6E89   0128
        SLR     R1,     1                       ; 6E8A   0061
        SUBR    R4,     R7                      ; 6E8B   0127

        INCR    R0                              ; 6E8C   0008
        SUBR    R4,     R2                      ; 6E8D   0122
        SLR     R1,     1                       ; 6E8E   0061
        SUBR    R5,     R4                      ; 6E8F   012C
        SLR     R1,     1                       ; 6E90   0061
        SUBR    R5,     R0                      ; 6E91   0128
        SLR     R1,     1                       ; 6E92   0061
        SUBR    R4,     R7                      ; 6E93   0127

        INCR    R2                              ; 6E94   000A
        SUBR    R4,     R2                      ; 6E95   0122
        SLR     R1,     1                       ; 6E96   0061
        SUBR    R4,     R5                      ; 6E97   0125
        SLR     R1,     1                       ; 6E98   0061
        SUBR    R4,     R6                      ; 6E99   0126
        SLR     R1,     1                       ; 6E9A   0061
        SUBR    R5,     R0                      ; 6E9B   0128
        SLR     R1,     1                       ; 6E9C   0061
        SUBR    R4,     R7                      ; 6E9D   0127

        INCR    R2                              ; 6E9E   000A
        SUBR    R4,     R2                      ; 6E9F   0122
        SLR     R1,     1                       ; 6EA0   0061
        SUBR    R4,     R5                      ; 6EA1   0125
        SLR     R1,     1                       ; 6EA2   0061
        SUBR    R4,     R6                      ; 6EA3   0126
        SLR     R1,     1                       ; 6EA4   0061
        SUBR    R5,     R0                      ; 6EA5   0128
        SLR     R1,     1                       ; 6EA6   0061
        SUBR    R4,     R7                      ; 6EA7   0127

        INCR    R2                              ; 6EA8   000A
        SUBR    R4,     R2                      ; 6EA9   0122
        SUBR    R0,     R1                      ; 6EAA   0101
        SUBR    R4,     R5                      ; 6EAB   0125
        SLR     R1,     1                       ; 6EAC   0061
        SUBR    R4,     R6                      ; 6EAD   0126
        SLR     R1,     1                       ; 6EAE   0061
        SUBR    R5,     R0                      ; 6EAF   0128
        SLR     R1,     1                       ; 6EB0   0061
        SUBR    R4,     R7                      ; 6EB1   0127

        INCR    R0                              ; 6EB2   0008
        SUBR    R5,     R0                      ; 6EB3   0128
        SLR     R1,     1                       ; 6EB4   0061
        SUBR    R4,     R6                      ; 6EB5   0126
        SLR     R1,     1                       ; 6EB6   0061
        SUBR    R5,     R0                      ; 6EB7   0128
        SLR     R1,     1                       ; 6EB8   0061
        SUBR    R4,     R7                      ; 6EB9   0127

        INCR    R0                              ; 6EBA   0008
        SUBR    R5,     R0                      ; 6EBB   0128
        SLR     R1,     1                       ; 6EBC   0061
        SUBR    R4,     R6                      ; 6EBD   0126
        SLR     R1,     1                       ; 6EBE   0061
        SUBR    R5,     R0                      ; 6EBF   0128
        SLR     R1,     1                       ; 6EC0   0061
        SUBR    R4,     R7                      ; 6EC1   0127

        DECLE   $000D,  $0088,  $00C1,  $0125   ; 6EC2   000D 0088 00C1 0125
        DECLE   $0001,  $00A1,  $0082,  $00E1   ; 6EC6   0001 00A1 0082 00E1
        DECLE   $0122,  $0085,  $00E1,  $0121   ; 6ECA   0122 0085 00E1 0121
        DECLE   $0084,  $0004,  $012F,  $0061   ; 6ECE   0084 0004 012F 0061
        DECLE   $0130,  $0004,  $012F,  $0061   ; 6ED2   0130 0004 012F 0061
        DECLE   $0130,  $0004,  $012F,  $0061   ; 6ED6   0130 0004 012F 0061
        DECLE   $0130,  $0008,  $008C,  $00E1   ; 6EDA   0130 0008 008C 00E1
        DECLE   $0121,  $0081,  $0061,  $0128   ; 6EDE   0121 0081 0061 0128
        DECLE   $0088,  $0004,  $012F,  $0061   ; 6EE2   0088 0004 012F 0061
        DECLE   $0130,  $0004,  $012F,  $0061   ; 6EE6   0130 0004 012F 0061
        DECLE   $0130,  $0004                   ; 6EEA   0130 0004

        SUBR    R5,     R7                      ; 6EEC   012F

        SLR     R1,     1                       ; 6EED   0061
        SUBR    R6,     R0                      ; 6EEE   0130
        DECR    R3                              ; 6EEF   0013
        MOVR    R0,     R2                      ; 6EF0   0082
        MOVR    R4,     R1                      ; 6EF1   00A1
        MOVR    R0,     R1                      ; 6EF2   0081
        ADDR    R4,     R1                      ; 6EF3   00E1
        SUBR    R4,     R1                      ; 6EF4   0121
        MOVR    R0,     R2                      ; 6EF5   0082
        MOVR    R4,     R1                      ; 6EF6   00A1
        MOVR    R0,     R2                      ; 6EF7   0082
        ADDR    R4,     R1                      ; 6EF8   00E1
        SUBR    R4,     R1                      ; 6EF9   0121
        MOVR    R0,     R2                      ; 6EFA   0082
        MOVR    R4,     R1                      ; 6EFB   00A1
        MOVR    R0,     R5                      ; 6EFC   0085
        ADDR    R4,     R1                      ; 6EFD   00E1
        SUBR    R4,     R1                      ; 6EFE   0121
        MOVR    R0,     R1                      ; 6EFF   0081
        MOVR    R4,     R1                      ; 6F00   00A1
        MOVR    R0,     R7                      ; 6F01   0087

        INCR    R2                              ; 6F02   000A
        SUBR    R4,     R2                      ; 6F03   0122
        SLR     R1,     1                       ; 6F04   0061
        SUBR    R4,     R5                      ; 6F05   0125
        SLR     R1,     1                       ; 6F06   0061
        SUBR    R4,     R6                      ; 6F07   0126
        SLR     R1,     1                       ; 6F08   0061
        SUBR    R5,     R0                      ; 6F09   0128
        SLR     R1,     1                       ; 6F0A   0061
        SUBR    R4,     R7                      ; 6F0B   0127

        INCR    R2                              ; 6F0C   000A
        SUBR    R4,     R2                      ; 6F0D   0122
        SLR     R1,     1                       ; 6F0E   0061
        SUBR    R4,     R5                      ; 6F0F   0125
        SLR     R1,     1                       ; 6F10   0061
        SUBR    R4,     R6                      ; 6F11   0126
        SLR     R1,     1                       ; 6F12   0061
        SUBR    R5,     R0                      ; 6F13   0128
        SLR     R1,     1                       ; 6F14   0061
        SUBR    R4,     R7                      ; 6F15   0127

        INCR    R2                              ; 6F16   000A
        SUBR    R4,     R2                      ; 6F17   0122
        SLR     R1,     1                       ; 6F18   0061
        SUBR    R4,     R5                      ; 6F19   0125
        SLR     R1,     1                       ; 6F1A   0061
        SUBR    R4,     R6                      ; 6F1B   0126
        SLR     R1,     1                       ; 6F1C   0061
        SUBR    R5,     R0                      ; 6F1D   0128
        SLR     R1,     1                       ; 6F1E   0061
        SUBR    R4,     R7                      ; 6F1F   0127

        INCR    R2                              ; 6F20   000A
        SUBR    R4,     R2                      ; 6F21   0122
        SLR     R1,     1                       ; 6F22   0061
        SUBR    R4,     R5                      ; 6F23   0125
        SLR     R1,     1                       ; 6F24   0061
        SUBR    R4,     R6                      ; 6F25   0126
        SLR     R1,     1                       ; 6F26   0061
        SUBR    R5,     R0                      ; 6F27   0128
        SLR     R1,     1                       ; 6F28   0061
        SUBR    R4,     R7                      ; 6F29   0127

        INCR    R2                              ; 6F2A   000A
        SUBR    R4,     R2                      ; 6F2B   0122
        SLR     R1,     1                       ; 6F2C   0061
        SUBR    R4,     R5                      ; 6F2D   0125
        SUBR    R0,     R1                      ; 6F2E   0101
        SUBR    R4,     R6                      ; 6F2F   0126
        SLR     R1,     1                       ; 6F30   0061
        SUBR    R5,     R0                      ; 6F31   0128
        SLR     R1,     1                       ; 6F32   0061
        SUBR    R4,     R7                      ; 6F33   0127

        INCR    R0                              ; 6F34   0008
        SUBR    R4,     R2                      ; 6F35   0122
        SLR     R1,     1                       ; 6F36   0061
        SUBR    R5,     R4                      ; 6F37   012C
        SLR     R1,     1                       ; 6F38   0061
        SUBR    R5,     R0                      ; 6F39   0128
        SUBR    R0,     R1                      ; 6F3A   0101
        SUBR    R4,     R7                      ; 6F3B   0127

        INCR    R0                              ; 6F3C   0008
        SUBR    R4,     R2                      ; 6F3D   0122
        SLR     R1,     1                       ; 6F3E   0061
        SUBR    R4,     R5                      ; 6F3F   0125
        SLR     R1,     1                       ; 6F40   0061
        SUBR    R4,     R6                      ; 6F41   0126
        SLR     R1,     1                       ; 6F42   0061
        SUBR    R6,     R0                      ; 6F43   0130
        INCR    R6                              ; 6F44   000E
        MOVR    R1,     R0                      ; 6F45   0088
        MOVR    R4,     R1                      ; 6F46   00A1
        MOVR    R0,     R2                      ; 6F47   0082
        ADDR    R4,     R1                      ; 6F48   00E1
        SUBR    R4,     R1                      ; 6F49   0121
        MOVR    R0,     R2                      ; 6F4A   0082
        MOVR    R4,     R1                      ; 6F4B   00A1
        MOVR    R0,     R4                      ; 6F4C   0084
        ADDR    R4,     R1                      ; 6F4D   00E1
        SUBR    R4,     R1                      ; 6F4E   0121
        MOVR    R0,     R2                      ; 6F4F   0082
        MOVR    R4,     R1                      ; 6F50   00A1
        MOVR    R0,     R7                      ; 6F51   0087

        INCR    R0                              ; 6F52   0008
        SUBR    R5,     R0                      ; 6F53   0128
        SLR     R1,     1                       ; 6F54   0061
        SUBR    R4,     R6                      ; 6F55   0126
        SLR     R1,     1                       ; 6F56   0061
        SUBR    R5,     R0                      ; 6F57   0128
        SLR     R1,     1                       ; 6F58   0061
L_6F59:
        SUBR    R4,     R7                      ; 6F59   0127

        INCR    R0                              ; 6F5A   0008
        SUBR    R5,     R0                      ; 6F5B   0128
        SLR     R1,     1                       ; 6F5C   0061
        SUBR    R4,     R6                      ; 6F5D   0126
        SLR     R1,     1                       ; 6F5E   0061
        SUBR    R5,     R0                      ; 6F5F   0128
        SUBR    R0,     R1                      ; 6F60   0101
        SUBR    R4,     R7                      ; 6F61   0127

        DECLE   $0006,  $0128,  $0061,  $0126   ; 6F62   0006 0128 0061 0126
        DECLE   $0061,  $0130,  $0007,  $0088   ; 6F66   0061 0130 0007 0088
        DECLE   $0061,  $0126,  $0061,  $0128   ; 6F6A   0061 0126 0061 0128
        DECLE   $0088,  $0006,  $0128,  $0061   ; 6F6E   0088 0006 0128 0061
        DECLE   $0126,  $0061,  $0130,  $0006   ; 6F72   0126 0061 0130 0006
        DECLE   $0128,  $0101,  $0126,  $0101   ; 6F76   0128 0101 0126 0101
        DECLE   $0130,  $0003,  $013F           ; 6F7A   0130 0003 013F

        SUBR    R4,     R1                      ; 6F7D   0121
        INCR    R2                              ; 6F7E   000A
        MOVR    R0,     R2                      ; 6F7F   0082
        MOVR    R4,     R1                      ; 6F80   00A1
        MOVR    R0,     R4                      ; 6F81   0084
        ADDR    R4,     R1                      ; 6F82   00E1
        SUBR    R4,     R2                      ; 6F83   0122
        MOVR    R0,     R5                      ; 6F84   0085
        SLR     R1,     1                       ; 6F85   0061
        SUBR    R5,     R0                      ; 6F86   0128
        MOVR    R1,     R0                      ; 6F87   0088
        CLRC                                    ; 6F88   0006
        SUBR    R4,     R2                      ; 6F89   0122
        SLR     R1,     1                       ; 6F8A   0061
        SUBR    R5,     R4                      ; 6F8B   012C
        SLR     R1,     1                       ; 6F8C   0061
        SUBR    R6,     R0                      ; 6F8D   0130
        CLRC                                    ; 6F8E   0006
        SUBR    R4,     R2                      ; 6F8F   0122
        SLR     R1,     1                       ; 6F90   0061
        SUBR    R5,     R4                      ; 6F91   012C
        SLR     R1,     1                       ; 6F92   0061
        SUBR    R6,     R0                      ; 6F93   0130
        SLR     R1,     1                       ; 6F94   0061
        SUBR    R4,     R2                      ; 6F95   0122
        SLR     R1,     1                       ; 6F96   0061
        SUBR    R4,     R5                      ; 6F97   0125
        SLR     R1,     1                       ; 6F98   0061
        SUBR    R4,     R6                      ; 6F99   0126
        SLR     R1,     1                       ; 6F9A   0061
        SUBR    R5,     R0                      ; 6F9B   0128
        SLR     R1,     1                       ; 6F9C   0061
        SUBR    R4,     R7                      ; 6F9D   0127

        DECLE   $0004,  $00A1,  $009E,  $0061   ; 6F9E   0004 00A1 009E 0061
        DECLE   $0005,  $0061,  $00A1,  $009C   ; 6FA2   0005 0061 00A1 009C
        DECLE   $0062,  $0005,  $0062,  $00A1   ; 6FA6   0062 0005 0062 00A1
        DECLE   $009A,  $0063,  $0005,  $0063   ; 6FAA   009A 0063 0005 0063
        DECLE   $00A1,  $0098,  $0064,  $0005   ; 6FAE   00A1 0098 0064 0005

        SLR     R0,     2                       ; 6FB2   0064
        MOVR    R4,     R1                      ; 6FB3   00A1
        MOVR    R2,     R6                      ; 6FB4   0096
        SLR     R1,     2                       ; 6FB5   0065

        JSRE    R4,     L_6536                  ; 6FB6   0004 0065 0136
        DECLE   $0065,  $0007,  $0065,  $0141   ; 6FB9   0065 0007 0065 0141
        DECLE   $0161,  $0181,  $0133,  $0065   ; 6FBD   0161 0181 0133 0065
        DECLE   $000E,  $0003,  $01A1,  $01C1   ; 6FC1   000E 0003 01A1 01C1
        DECLE   $01E3,  $0201                   ; 6FC5   01E3 0201

        SUBR    R4,     R4                      ; 6FC7   0124
        MVI     G_0121, R1                      ; 6FC8   0281 0121
        MVI@    R4,     R1                      ; 6FCA   02A1
        SUBR    R4,     R1                      ; 6FCB   0121
        ADD     G_0129, R1                      ; 6FCC   02C1 0129
        SLR     R1,     2                       ; 6FCE   0065
        SETC                                    ; 6FCF   0007
        SLR     R1,     2                       ; 6FD0   0065
        BC      L_6D91                          ; 6FD1   0221 0241

        MVO@    R1,     R4                      ; 6FD3   0261
        SUBR    R6,     R3                      ; 6FD4   0133
        SLR     R1,     2                       ; 6FD5   0065

        JSRE    R4,     L_6536                  ; 6FD6   0004 0065 0136

        SLR     R1,     2                       ; 6FD9   0065

        JSRE    R4,     L_6536                  ; 6FDA   0004 0065 0136
        DECLE   $0065,  $0005                   ; 6FDD   0065 0005

        SLR     R0,     2                       ; 6FDF   0064
        MOVR    R2,     R7                      ; 6FE0   0097

        DECLE   $00C1,  $0064,  $0005,  $0063   ; 6FE1   00C1 0064 0005 0063
        DECLE   $0099,  $00C1,  $0063,  $0005   ; 6FE5   0099 00C1 0063 0005

        SLR     R2,     1                       ; 6FE9   0062
L_6FEA:
        TSTR    R3                              ; 6FEA   009B
        DECLE   $00C1,  $0062,  $0005           ; 6FEB   00C1 0062 0005

        SLR     R1,     1                       ; 6FEE   0061
        MOVR    R3,     R5                      ; 6FEF   009D
        ADDR    R0,     R1                      ; 6FF0   00C1
        SLR     R1,     1                       ; 6FF1   0061
        DIS                                     ; 6FF2   0003
        MOVR    R3,     R7                      ; 6FF3   009F

        ADDR    R0,     R1                      ; 6FF4   00C1
        DECLE   $0000,  $0000,  $0000,  $0000   ; 6FF5   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0000   ; 6FF9   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000           ; 6FFD   0000 0000 0000
;; ======================================================================== ;;
;;  Branch cross-reference
;; ------------------------------------------------------------------------ ;;
;;  Target      Target of
;;  $5017       <entry>
;;  $505B       $505F  
;;  $5065       $5067  
;;  $506A       $506D  
;;  $5072       $5084  
;;  $5086       $5072  
;;  $5099       $50BA  
;;  $50A5       $50A0  
;;  $50B3       $509E   $50A3  
;;  $50B5       $50B1  
;;  $50BC       $508A  
;;  $50BD       $5075  
;;  $50C7       $50DF  
;;  $50DC       $50C8   $50CC  
;;  $50E2       $5078  
;;  $50E7       $5140  
;;  $50EE       $50EB  
;;  $50F5       $50F2  
;;  $5107       $5139  
;;  $5125       $511A  
;;  $512B       $5121  
;;  $5133       $5108  
;;  $5136       $5131  
;;  $5138       $5134  
;;  $513B       $50FD   $5103  
;;  $5143       $507B  
;;  $5159       $5147  
;;  $516E       $515A   $5169  
;;  $516F       $5155   $516B  
;;  $5170       $5189  
;;  $5185       $517A  
;;  $518C       $5180  
;;  $51A1       $519D  
;;  $51A2       $51A0  
;;  $51A9       $51A3  
;;  $51AA       $5197   $51A6  
;;  $51AF       $519A  
;;  $51B8       $51D2  
;;  $51CB       $51D5  
;;  $51CC       $51C7  
;;  $51DD       $51D0  
;;  $51EC       $51F7  
;;  $520A       $526E  
;;  $5258       $5243  
;;  $5259       $5257  
;;  $526A       $5210   $5216  
;;  $527B       $52B1  
;;  $52AC       $528C  
;;  $52B3       $527F  
;;  $52C2       $52BA  
;;  $52D7       $52CF  
;;  $52ED       $52E8  
;;  $52F3       $5301  
;;  $52FC       $52F6   $52F9  
;;  $5318       $530F  
;;  $5323       $52C8   $52DD  
;;  $5326       $5357  
;;  $5334       $532D  
;;  $5351       $534D  
;;  $5354       $5332  
;;  $535A       $51E2  
;;  $535E       $535C  
;;  $5364       $5375  
;;  $5378       $532F  
;;  $53A8       $5390  
;;  $53BC       $53B8  
;;  $53BD       $53BB  
;;  $53C8       $539B  
;;  $53DB       $53E0  
;;  $53E2       $53D2  
;;  $53EA       $53E6  
;;  $53F1       $53FD  
;;  $53F8       $53FA  
;;  $5400       $52B3  
;;  $540B       $5407  
;;  $5427       $5420  
;;  $5428       $5426  
;;  $5440       $5424  
;;  $5453       $5450  
;;  $5469       $5465  
;;  $5492       $52EA  
;;  $549F       $549C  
;;  $54A7       $54A2   $54B6  
;;  $54B4       $54A9  
;;  $54B9       $547B  
;;  $54C6       $54BF  
;;  $54CB       $54BC  
;;  $54D3       $54CC  
;;  $54D6       $54C4   $54C9   $54D1  
;;  $54D8       $54C1  
;;  $54DD       $54EC  
;;  $54DF       $54E4  
;;  $54EF       $54C6  
;;  $54F8       $5523  
;;  $5526       $54CE  
;;  $552B       $5536  
;;  $552D       $5530  
;;  $5539       $54D3  
;;  $5540       $5543  
;;  $5546       $5340   $5415   $637F   $645C   $646D   $6A52   $6AB8  
;;  $5549       $554B  
;;  $554D       $5547  
;;  $557B       $562D   $56F5  
;;  $558F       $558A  
;;  $55AB       $559D  
;;  $55BB       $55B8  
;;  $55BF       $557F   $6122  
;;  $55DB       $55AB  
;;  $55E5       $55E1  
;;  $55F7       $55AE   $6125   $6729  
;;  $5627       $506F  
;;  $568E       $5689  
;;  $56B5       $56A5  
;;  $56C8       $569D   $56A1  
;;  $56C9       $5687  
;;  $56D7       $56D9  
;;  $56DB       $56D0  
;;  $56F8       $56CC  
;;  $5703       $56FE  
;;  $573C       $5737  
;;  $573D       $573B  
;;  $5742       $570D   $5719   $571F   $572F  
;;  $5744       $5740  
;;  $5748       $570A  
;;  $5749       $5701  
;;  $5773       $576E  
;;  $5778       $574A   $5754   $575A   $5767  
;;  $577A       $5776  
;;  $578F       $5789   $578C  
;;  $5799       $5795  
;;  $579A       $5781  
;;  $57A7       $57A0   $57A3  
;;  $57AE       $57A8  
;;  $57B9       $57B0  
;;  $57BD       $57B2  
;;  $57BE       $57A5  
;;  $57C9       $57C0  
;;  $57CC       $57C4  
;;  $57D5       $57CE  
;;  $57DA       $57AA   $64B8  
;;  $57DB       $57C9  
;;  $5819       $5802  
;;  $586B       $586E  
;;  $5885       $575E   $5DDA   $69F6   $6B37  
;;  $5894       $57B5  
;;  $5895       $57D2  
;;  $58A6       $589F  
;;  $58B5       $58A4   $58A8   $58B9  
;;  $58C0       $589B  
;;  $58C1       $5896  
;;  $58DD       $58C6  
;;  $5982       $58C2  
;;  $5988       $5998   $599C  
;;  $599E       $5991  
;;  $59A3       $5994  
;;  $59B0       $59B2  
;;  $59CA       $59B7  
;;  $59CE       $59C8  
;;  $59CF       $57E6   $58D9   $6738  
;;  $59E2       $59DA  
;;  $59FF       $58A1  
;;  $5A16       $5A13  
;;  $5A27       $5A10   $6743   $6857  
;;  $5A3A       $5A33  
;;  $5D08       $508C  
;;  $5D18       $5D21  
;;  $5D1F       $5D1A  
;;  $5D40       $5D3C  
;;  $5D41       $5D3F  
;;  $5D95       $5D85  
;;  $5D99       $5D93  
;;  $5DD8       $5DC9  
;;  $5DEE       $5DE5  
;;  $5DF3       $547E  
;;  $5DFD       $5DF6  
;;  $5E00       $5DFB   $5F21  
;;  $5E03       $5DF8  
;;  $5E0C       $5E08  
;;  $5E0D       $5E0B  
;;  $5E1A       $5E14  
;;  $5E27       $5E33   $5E3D   $5E45  
;;  $5E3F       $5E37  
;;  $5E47       $5E2F  
;;  $5E48       $5E1E   $5E89   $5EAF   $5EEB  
;;  $5E60       $5E5C  
;;  $5E6C       $5E71  
;;  $5E73       $5E6D  
;;  $5E76       $5E7B  
;;  $5E80       $5E40   $5F0D  
;;  $5E8D       $5DFD  
;;  $5E95       $5E91  
;;  $5E96       $5E94  
;;  $5EA3       $5E9D  
;;  $5EAE       $5EC4  
;;  $5EC7       $5E29   $5EB3   $5EF6  
;;  $5EE2       $55D7   $5871   $58BC   $674C  
;;  $5EEB       $5F1F  
;;  $5EF4       $5F00   $5F0A   $5F12  
;;  $5F0C       $5F04  
;;  $5F14       $5EFC  
;;  $5F21       $5F16  
;;  $5F23       $6AD6  
;;  $5F35       $5F25  
;;  $5F41       $5D8D  
;;  $5F42       $5F40  
;;  $5F43       $55BB  
;;  $5F44       $5F42  
;;  $5F46       $5F4C  
;;  $5F4F       $60F3   $6B8D  
;;  $5F5B       $56E5   $6BC8  
;;  $5F5E       $5A3C   $690F   $6992   $6B57  
;;  $5F60       $5F83   $61D4   $688C   $68A8   $6923  
;;  $5F61       $5F5F  
;;  $5F69       $5F78  
;;  $5F7C       $5D5E   $60DF   $6773   $6879   $68F2  
;;  $5FA0       $5F97   $5F9C  
;;  $5FA1       $680D  
;;  $5FA7       $5F73   $616A  
;;  $5FB4       $5DA7   $6949  
;;  $5FC1       $5597   $5DB0   $69BF   $6A2C   $6B6F  
;;  $5FC3       $61E3  
;;  $5FC4       $5FC2  
;;  $5FC5       $5FEE  
;;  $5FF1       $5FC7   $5FD7   $5FF7  
;;  $5FFA       $6015  
;;  $6011       $6AD1   $6BA2  
;;  $603F       $6170   $6804   $6850  
;;  $6041       $577C   $60FF  
;;  $6046       $573D   $5773   $60FA   $6B05  
;;  $6054       $5983   $61BD   $6400   $65FE  
;;  $605E       $605B  
;;  $606B       $6068  
;;  $6076       $557C   $6BCB  
;;  $607A       $68A0  
;;  $607B       $6079  
;;  $607D       $607B  
;;  $607F       $6087  
;;  $608B       $57C6  
;;  $6099       $6093  
;;  $60A1       $6097  
;;  $60AD       $60A3  
;;  $60B0       $608E   $609F   $60A9  
;;  $60B1       $60AD  
;;  $60E9       $60BF  
;;  $6103       $60B9  
;;  $6120       $610F  
;;  $6121       $610A  
;;  $6129       $6108  
;;  $614B       $6141  
;;  $6159       $614D  
;;  $6173       $6160  
;;  $6175       $614F  
;;  $617A       $6151  
;;  $6188       $617B  
;;  $618A       $6153  
;;  $619C       $6155  
;;  $61B3       $6157  
;;  $61D2       $6149   $6173   $6178   $6180   $6188   $618B   $6190   $619A  
;;  $61D2       $619D   $61A2   $61B3   $61D0  
;;  $61E6       $613E   $61BA   $61C5   $61C9  
;;  $6287       $6276  
;;  $6298       $6296  
;;  $62A1       $6263  
;;  $62B1       $62AF  
;;  $62B6       $62B4  
;;  $62E1       $61F0  
;;  $6318       $5726   $5D47   $5DD1   $6AEC  
;;  $6324       $62A3  
;;  $6332       $6327  
;;  $6344       $5890   $632E  
;;  $6353       $6359  
;;  $6361       $5886   $6319  
;;  $6371       $636A  
;;  $6373       $6366   $636E  
;;  $6377       $5E00  
;;  $6385       $6391  
;;  $6390       $638B  
;;  $6394       $6387   $69AF  
;;  $639E       $639A  
;;  $63AF       $63AB  
;;  $63B6       $639F   $63A3   $63B0  
;;  $63B8       $63B4  
;;  $63B9       $638D  
;;  $63D7       $63D2  
;;  $63EC       $63DE  
;;  $63F3       $63EA  
;;  $63F5       $57BA  
;;  $63F6       $57D7  
;;  $63FD       $63F9  
;;  $6405       $641B   $641F  
;;  $6416       $640E  
;;  $6421       $6414  
;;  $6432       $642E  
;;  $6434       $642B  
;;  $6436       $6429  
;;  $6445       $643A  
;;  $6458       $63FE   $6417   $6440  
;;  $6459       $644E  
;;  $6466       $6455  
;;  $646A       $63E5  
;;  $6472       $6430  
;;  $6479       $648D  
;;  $647C       $6482  
;;  $6481       $647D  
;;  $649D       $64AB   $64B1  
;;  $64B3       $649F  
;;  $64BC       $6432  
;;  $64CB       $6434  
;;  $64D8       $64D2  
;;  $64F8       $64F6  
;;  $650C       $650A  
;;  $651A       $6518  
;;  $6536       $6FB6   $6FD6   $6FDA  
;;  $6549       $6549  
;;  $654B       $654B  
;;  $654D       $654D  
;;  $6553       $6551  
;;  $6556       $6554  
;;  $65FC       $667A   $66CC  
;;  $660A       $6623   $6627  
;;  $6629       $661D  
;;  $664E       $660C  
;;  $6657       $665B  
;;  $665D       $6658  
;;  $665E       $6655  
;;  $665F       $6650  
;;  $6668       $6675  
;;  $6673       $666F  
;;  $6674       $6672  
;;  $6677       $666A  
;;  $6688       $6684  
;;  $668E       $668A  
;;  $6699       $6682  
;;  $669C       $6697  
;;  $66B6       $66B1  
;;  $66B8       $66B4  
;;  $66BA       $66B6  
;;  $66C2       $66BD  
;;  $66C4       $66C0  
;;  $66C6       $66C2  
;;  $66CA       $667E  
;;  $66E4       $66D4  
;;  $66F6       $66D0   $66D9  
;;  $66F7       $66EA   $66F3  
;;  $6706       $66FF  
;;  $6709       $6704  
;;  $6711       $6706  
;;  $6713       $6690   $66DD  
;;  $6717       $6686  
;;  $671B       $668C  
;;  $671D       $6719  
;;  $6725       $6722  
;;  $6746       $6749  
;;  $6769       $6766  
;;  $677B       $676C  
;;  $6788       $6781  
;;  $678B       $6786  
;;  $678F       $6175  
;;  $6797       $6715   $678D  
;;  $67AE       $679B   $679F  
;;  $67B8       $67AF  
;;  $67C6       $67A3   $67BF  
;;  $67C7       $67AC   $67B6  
;;  $67D3       $67CF  
;;  $67E2       $67D8  
;;  $67E4       $67E0  
;;  $67E8       $67D1  
;;  $6809       $6800  
;;  $680D       $6807  
;;  $6824       $6817  
;;  $6831       $6825  
;;  $6832       $5DEF   $681E   $682B  
;;  $684A       $67C3  
;;  $684B       $67E6  
;;  $685A       $6855  
;;  $6892       $6888  
;;  $68B3       $68A6  
;;  $68B8       $6898   $689C  
;;  $68D1       $68CA  
;;  $68D4       $68B6   $68C5  
;;  $68FC       $68B9  
;;  $68FF       $68B1   $68CF   $68FA  
;;  $6900       $68FC  
;;  $6913       $6901   $6B62  
;;  $6917       $6919  
;;  $6921       $6792  
;;  $692A       $5DBC   $5DC4   $60F0   $6119   $61AC   $67F1   $683C   $6846  
;;  $692A       $6863   $686B   $68DC   $69CF   $69DC  
;;  $692F       $67A9  
;;  $6932       $6699   $67B3  
;;  $6933       $6931  
;;  $693A       $6937  
;;  $6945       $6941  
;;  $6947       $6943  
;;  $6965       $6961  
;;  $696A       $6966  
;;  $6989       $6986  
;;  $6995       $696B  
;;  $6996       $6950   $6959  
;;  $699D       $6998  
;;  $69A4       $69A1  
;;  $69A5       $6945  
;;  $69EB       $69E2  
;;  $69F9       $69A9   $69B3  
;;  $6A0A       $69FE   $6A03  
;;  $6A3F       $6A38  
;;  $6A4D       $6A18   $6A22   $6A3D  
;;  $6A4E       $6A44  
;;  $6A5F       $6A5C  
;;  $6A65       $6A62  
;;  $6A6A       $6A1E  
;;  $6A6B       $6A75  
;;  $6A78       $6A6E  
;;  $6A7D       $6A24  
;;  $6A8E       $6A8A  
;;  $6A8F       $6A3F  
;;  $6AAE       $6A47   $6AF2  
;;  $6AC1       $6ABD  
;;  $6ADB       $6A4A   $6AF5  
;;  $6AF9       $6A3A   $6B73  
;;  $6B2B       $6B24  
;;  $6B31       $6B29  
;;  $6B32       $6B26  
;;  $6B52       $6B2E  
;;  $6B66       $6B60  
;;  $6BAA       $6B80  
;;  $6BC6       $6BA8  
;;  $6BC7       $68CC  
;;  $6BEA       $6B1B  
;;  $6BF8       $60E6   $6BA5  
;;  $6C09       <entry>
;;  $6C14       $6C0D  
;;  $6C19       $6C94  
;;  $6C26       $60B3  
;;  $6C54       $688F   $6BC3  
;;  $6C65       $6783  
;;  $6C74       $6788  
;;  $6C94       $6C8E  
;;  $6C97       $6C87  
;;  $6D91       $6FD1  
;;  $6DDE       $6C6F  
;;  $6F59       $6C7E  
;;  $6FEA       $6C5D  
;; ======================================================================== ;;

; ============================================================
; Data Section: $7000 - $8FFF
; Previously undisassembled - level data, text, tables
; ============================================================

D_7000:  DECLE   $03B9, $007F, $0275, $0004, $0114, $038C, $0083, $008C
D_7010:  DECLE   $0091, $0001, $03B9, $00FF, $007F, $0004, $011C, $0223
D_7020:  DECLE   $02B7, $0275, $0270, $0274, $0271, $0004, $015C, $03FA  ; "...u.p.t.q...\.."
D_7030:  DECLE   $0098, $0093, $02B1, $0271, $0004, $011C, $01DC, $0091
D_7040:  DECLE   $009A, $0004, $011C, $01F8, $02B1, $0270, $00A0, $008C
D_7050:  DECLE   $0004, $011C, $01DC, $0091, $009A, $0004, $011C, $01F8
D_7060:  DECLE   $02B1, $02B2, $02B5, $033A, $0325, $0272, $004A, $02FA  ; ".......:.%.r.J.."
D_7070:  DECLE   $0126, $0251, $02FA, $0010, $0250, $02B2, $02B7, $01C9
D_7080:  DECLE   $01D2, $0259, $02FB, $0010, $025A, $00AF, $0275, $008A
D_7090:  DECLE   $0081, $0090, $0060, $0004, $0114, $0229, $0004, $0114
D_70A0:  DECLE   $0357, $008A, $0081, $02B7, $02FB, $0325, $0298, $03B8
D_70B0:  DECLE   $00FF, $0338, $0008, $0203, $0001, $01C0, $0064, $0060
D_70C0:  DECLE   $02FB, $0008, $0084, $0299, $03B9, $007F, $0339, $0008
D_70D0:  DECLE   $0203, $0001, $01C9, $0065, $0061, $004D, $00CC, $004D  ; ".......e.a.M...M"
D_70E0:  DECLE   $00CC, $02FC, $0200, $033B, $032D, $00AF, $02B9, $0003
D_70F0:  DECLE   $01D2, $000F, $01C9, $000F, $0011, $02FA, $0163, $0290
D_7100:  DECLE   $03B8, $007F, $03F8, $0080, $0250, $000A, $0011, $0223
D_7110:  DECLE   $0009, $00AF, $0275, $0282, $018D, $0092, $020C, $0020
D_7120:  DECLE   $0282, $019A, $0092, $0204, $0004, $0378, $0009, $0204
D_7130:  DECLE   $0008, $0281, $033F, $0001, $0379, $005E, $005B, $020C  ; ".....?...y.^.[.."
D_7140:  DECLE   $000F, $0083, $0013, $0204, $0008, $02FB, $018D, $0299
D_7150:  DECLE   $0089, $0204, $0005, $0011, $0259, $0004, $0160, $00B1
D_7160:  DECLE   $02B7, $0275, $0270, $0004, $016C, $0026, $02B0, $0378  ; "...u.p...l.&...x"
D_7170:  DECLE   $0006, $020E, $0048, $0240, $018D, $0378, $0002, $020C
D_7180:  DECLE   $0028, $02BB, $0328, $02BD, $0008, $0298, $0001, $03F8
D_7190:  DECLE   $0000, $0020, $0258, $00EB, $0298, $03F8, $0080, $0258
D_71A0:  DECLE   $00EB, $0298, $0001, $03B8, $00F8, $00EF, $03F8, $0006
D_71B0:  DECLE   $0258, $0001, $02B9, $00A0, $005B, $02BB, $0003, $0004
D_71C0:  DECLE   $015C, $037C, $02B8, $0004, $0240, $0350, $0004, $0168  ; ".\.|.....@.P...h"
D_71D0:  DECLE   $03F8, $02BB, $0328, $0001, $03F8, $0000, $0009, $0081
D_71E0:  DECLE   $0004, $0168, $012A, $0004, $015C, $034F, $0280, $0196  ; "...h.*...\.O...."
D_71F0:  DECLE   $02B9, $0040, $0004, $0160, $0046, $02BB, $012C, $0004  ; "...@...`.F...,.."
D_7200:  DECLE   $0160, $0041, $02B7, $01ED, $0245, $018D, $0378, $0008  ; ".`.A.....E...x.."
D_7210:  DECLE   $020E, $001F, $0205, $0015, $0280, $01AC, $0080, $020C
D_7220:  DECLE   $000F, $02B8, $0029, $0040, $02B9, $0028, $0041, $02BB  ; ".....).@...(.A.."
D_7230:  DECLE   $0327, $0004, $0168, $012A, $02B8, $0258, $0240, $034F  ; ".'...h.*...X.@.O"
D_7240:  DECLE   $02B7, $0003, $0004, $0154, $01BF, $0004, $0154, $01F7
D_7250:  DECLE   $0002, $0280, $019C, $0240, $0199, $0280, $0175, $02F8
D_7260:  DECLE   $000A, $0240, $0197, $0280, $0176, $02F8, $0006, $0240
D_7270:  DECLE   $0198, $02B7, $0275, $0280, $018D, $0010, $020B, $00A6
D_7280:  DECLE   $0089, $020C, $0008, $0285, $033D, $0001, $037D, $0028
D_7290:  DECLE   $005B, $020C, $0087, $0048, $00C7, $0200, $000A, $0200
D_72A0:  DECLE   $0024, $0200, $0027, $0200, $0035, $0200, $0045, $0200  ; ".$...'...5...E.."
D_72B0:  DECLE   $005A, $02F9, $033D, $0288, $0001, $0378, $0030, $005B  ; ".Z...=.....x.0.["
D_72C0:  DECLE   $020C, $0011, $02F9, $0010, $02B8, $00F0, $0248, $0339
D_72D0:  DECLE   $034D, $008B, $0004, $015C, $03A7, $004B, $02FB, $0126  ; ".M.....\...K...&"
D_72E0:  DECLE   $0004, $0160, $003F, $0200, $005D, $0004, $0164, $038F  ; "...`.?...]...d.."
D_72F0:  DECLE   $0200, $0058, $0089, $020C, $000B, $0280, $01AB, $0080
D_7300:  DECLE   $020C, $0050, $0001, $02B8, $0087, $0009, $0240, $0335
D_7310:  DECLE   $0200, $0048, $0089, $020C, $0045, $0280, $01AB, $0080
D_7320:  DECLE   $020C, $0040, $02B8, $007E, $0240, $017F, $02B8, $021C
D_7330:  DECLE   $0240, $034E, $0200, $0036, $0089, $020C, $0033, $0280  ; ".@.N...6.....3.."
D_7340:  DECLE   $01AB, $0080, $020C, $002E, $02BB, $0325, $02B9, $0020
D_7350:  DECLE   $0041, $0088, $03F8, $0100, $0004, $0168, $012A, $02B8
D_7360:  DECLE   $021C, $0240, $034E, $0200, $001D, $0275, $0280, $018D
D_7370:  DECLE   $0378, $0006, $020C, $002A, $0093, $0004, $0160, $0054  ; ".x.....*.....`.T"
D_7380:  DECLE   $02A0, $03B8, $01F8, $0378, $0008, $0205, $001F, $0378
D_7390:  DECLE   $0030, $020E, $001B, $02B8, $0016, $0040, $0014, $0260
D_73A0:  DECLE   $000F, $0275, $02BB, $0003, $0004, $015C, $0360, $0004
D_73B0:  DECLE   $0118, $0283, $01C9, $0241, $018D, $02BB, $0328, $0001
D_73C0:  DECLE   $02BC, $006A, $005A, $0004, $015C, $03C3, $02B7, $0018
D_73D0:  DECLE   $00C7, $00F0, $00F8, $00E8, $0078, $00F0, $02F8, $00F7
D_73E0:  DECLE   $02FF, $00EF, $00E6, $0100, $00EF, $00FF, $007F, $01FF
D_73F0:  DECLE   $00FD, $01F8, $00F0, $00F8, $00E8, $00F8, $00F0, $00B8
D_7400:  DECLE   $0100, $0080, $00C0, $03E0, $01E0, $00FF, $007F, $0300
D_7410:  DECLE   $0100, $00E0, $00EC, $03ED, $00EC, $00E0, $00E0, $00EC
D_7420:  DECLE   $03ED, $00EC, $00E0, $007F, $002E, $003A, $0036, $006C  ; "...........:.6.l"
D_7430:  DECLE   $0074, $005C, $00FE, $00FF, $0000, $00FF, $01FE, $00FF
D_7440:  DECLE   $0000, $00FF, $02AB, $01AA, $02AB, $0100, $0087, $009D
D_7450:  DECLE   $00FD, $003F, $0018, $003C, $0042, $0081, $0099, $00BD
D_7460:  DECLE   $005A, $0024, $00DB, $007E, $0000, $0018, $0024, $0018  ; ".Z.$...~.....$.."
D_7470:  DECLE   $00BD, $00FF, $00A5, $00FF, $0000, $003C, $004A, $00D1
D_7480:  DECLE   $0085, $00A9, $004A, $003C, $00FF, $00F9, $00F3, $00E7
D_7490:  DECLE   $00CF, $007E, $003C, $0018, $0099, $01BD, $00FF, $0042
D_74A0:  DECLE   $0166, $0024, $00C1, $0055, $007F, $0355, $003E, $0018  ; ".f.$...U...U.>.."
D_74B0:  DECLE   $003C, $0018, $003C, $006E, $00DF, $006E, $003C, $0100  ; ".<...<.n...n.<.."
D_74C0:  DECLE   $0040, $00BF, $0045, $0200, $003C, $0042, $0099, $0191  ; ".@...E...<.B...."
D_74D0:  DECLE   $0099, $0042, $003C, $0000, $0078, $001E, $00FC, $0118
D_74E0:  DECLE   $0031, $0073, $0100, $0010, $003B, $007F, $02FF, $000F
D_74F0:  DECLE   $003C, $00F8, $00F0, $00E2, $00CA, $009F, $0039, $0000
D_7500:  DECLE   $0009, $0095, $01FF, $0095, $0009, $0000, $0000, $0083
D_7510:  DECLE   $001F, $01FD, $001F, $0083, $0000, $00F1, $00DF, $00BE
D_7520:  DECLE   $0176, $00BE, $00DF, $00F1, $0000, $0006, $000F, $0099
D_7530:  DECLE   $00F3, $00E6, $000C, $0000, $0073, $0031, $0118, $00FC
D_7540:  DECLE   $001E, $0078, $0000, $02FF, $007F, $003B, $0010, $0100
D_7550:  DECLE   $0039, $009F, $00CA, $00E2, $00F0, $00F8, $003C, $000F
D_7560:  DECLE   $0000, $0028, $007F, $0018, $002F, $000D, $0010, $0000
D_7570:  DECLE   $0090, $0020, $00FE, $003F, $0078, $009F, $0004, $0020  ; "... ...?.x..... "
D_7580:  DECLE   $0040, $0020, $00FD, $007F, $003B, $001E, $0024, $0008  ; ".@. .....;...$.."
D_7590:  DECLE   $0000, $0040, $001B, $003F, $007C, $00FF, $0020, $0010  ; "...@...?.|... .."
D_75A0:  DECLE   $00F9, $0056, $009B, $0057, $0080, $0057, $0000, $0000
D_75B0:  DECLE   $0000, $0000, $0000, $0000, $0000, $0000, $00F0, $00F0
D_75C0:  DECLE   $0070, $0020, $0020, $0000, $0000, $0000, $00F0, $00F0
D_75D0:  DECLE   $00F0, $0070, $0070, $0020, $00A0, $00A0, $00F0, $00F0
D_75E0:  DECLE   $0070, $0020, $0020, $0000, $0000, $0000, $00DA, $0057  ; ".p. . .........W"
D_75F0:  BIDECLE $0000, $0000, $0000, $0000, $0000, $0000, $0000, $0000
D_7600:  DECLE   $0000, $0000, $0080, $0080, $00D0, $00D0, $00F0, $00F0
D_7610:  DECLE   $00A0, $00A0, $0080, $00D0, $00D0, $00F0, $00F0, $00F0
D_7620:  DECLE   $0000, $0000, $0080, $0080, $00D0, $00D0, $00F0, $00F0
D_7630:  DECLE   $0275, $0004, $0160, $0361, $009A, $02FB, $0345, $0259  ; ".u...`.a.....E.Y"
D_7640:  DECLE   $000B, $0259, $0093, $000A, $004A, $02FA, $0126, $0004
D_7650:  DECLE   $0160, $0332, $02FB, $032D, $02BA, $0002, $0004, $0160  ; ".`.2...-.......`"
D_7660:  DECLE   $0344, $02B7, $0275, $0081, $0048, $00C4, $02A0, $0004
D_7670:  DECLE   $0114, $0268, $0250, $02FA, $0010, $02A0, $0004, $0114
D_7680:  DECLE   $0268, $0250, $0088, $02B7, $0275, $0272, $0001, $02BC  ; ".h.P.....u.r...."
D_7690:  DECLE   $005D, $0063, $0081, $0065, $00CC, $02A1, $0041, $0001  ; ".].c...e.....A.."
D_76A0:  DECLE   $02BD, $00FF, $00F3, $029C, $01AC, $01CC, $025C, $000B
D_76B0:  DECLE   $0012, $022C, $0007, $0333, $02B7, $0000, $0004, $000C
D_76C0:  DECLE   $0008, $02BA, $0008, $0081, $0379, $0004, $0206, $000B
D_76D0:  DECLE   $0379, $0008, $0206, $0005, $0379, $000C, $0205, $0003
D_76E0:  DECLE   $0111, $010A, $0091, $03B9, $0007, $00AF, $0275, $0001
D_76F0:  DECLE   $02BC, $00DE, $0064, $0280, $019C, $02BA, $0005, $0004
D_7700:  DECLE   $0154, $0146, $00C4, $02BB, $0010, $02A0, $02A1, $0004
D_7710:  DECLE   $0160, $0394, $0080, $020B, $0003, $0004, $0160, $03B9
D_7720:  DECLE   $0013, $022C, $000D, $02B7, $0300, $0175, $0001, $0378
D_7730:  DECLE   $0097, $00FF, $020D, $0002, $03B8, $001F, $0080, $0205
D_7740:  DECLE   $0015, $0378, $0013, $020E, $0011, $0301, $0176, $0001
D_7750:  DECLE   $0379, $00CE, $00FF, $020D, $0002, $03B9, $000F, $0089
D_7760:  DECLE   $0205, $0004, $0379, $000B, $0206, $0002, $01C0, $0010
D_7770:  DECLE   $00AF, $0275, $02BD, $0200, $00C5, $004D, $00CD, $004D
D_7780:  DECLE   $00CD, $0274, $0001, $033C, $00E0, $0064, $00A1, $01C0
D_7790:  DECLE   $02F8, $0000, $0075, $0054, $0001, $02F9, $0080, $0065
D_77A0:  DECLE   $028A, $0074, $0209, $0003, $0066, $0066, $0062, $03BA  ; "...t.....f.f.b.."
D_77B0:  DECLE   $001F, $004A, $0094, $0062, $037A, $0007, $020E, $000C
D_77C0:  DECLE   $02B9, $0180, $02C1, $019C, $0275, $0004, $0164, $006A
D_77D0:  DECLE   $02B5, $0080, $0204, $0007, $0001, $02FC, $005E, $0065
D_77E0:  DECLE   $0001, $02A0, $0268, $02B4, $02B7, $0275, $0281, $01AB
D_77F0:  DECLE   $009B, $0204, $0002, $0281, $01AC, $0089, $020C, $0058
D_7800:  DECLE   $0004, $0160, $0054, $02B9, $0003, $02A2, $0001, $03BA
D_7810:  DECLE   $00F8, $0009, $0001, $037A, $0060, $0008, $0205, $0006
D_7820:  DECLE   $0001, $037A, $00B0, $0008, $0206, $000B, $0011, $020B
D_7830:  DECLE   $003F, $0379, $0001, $022C, $0017, $02FC, $0012, $0220  ; ".?.y...,....... "
D_7840:  DECLE   $001B, $0001, $033A, $0060, $0008, $0066, $0062, $037A  ; ".....:.`...f.b.z"
D_7850:  DECLE   $0002, $020E, $000B, $0204, $0007, $0092, $020C, $0002
D_7860:  DECLE   $0200, $0040, $0200, $0088, $0200, $0095, $033A, $0003
D_7870:  DECLE   $037A, $0007, $0204, $0009, $0280, $01A8, $0378, $0006
D_7880:  DECLE   $020D, $0016, $0008, $0240, $01A8, $0014, $02B8, $0016
D_7890:  DECLE   $0040, $0260, $02B9, $019D, $02C1, $019C, $0004, $0164
D_78A0:  DECLE   $0059, $02B9, $0180, $02C1, $019C, $0004, $0164, $0066
D_78B0:  DECLE   $02B7, $0275, $02B8, $0001, $0004, $0154, $0146, $028A
D_78C0:  DECLE   $0018, $0182, $0018, $01C2, $024A, $02B7, $0018, $0388
D_78D0:  DECLE   $0248, $00AF, $0275, $02B8, $0001, $0004, $0154, $0146  ; ".H...u.......T.F"
D_78E0:  DECLE   $0388, $02B7, $02BC, $0032, $0281, $01A7, $02BB, $019D
D_78F0:  DECLE   $01D2, $0298, $02BD, $0007, $0078, $0209, $0002, $00E2
D_7900:  DECLE   $0009, $0015, $022C, $0007, $0298, $03B8, $0080, $0258
D_7910:  DECLE   $000B, $02FC, $0032, $037C, $00C8, $0226, $0015, $0241  ; ".....2.|...&...A"
D_7920:  DECLE   $01A7, $02BC, $01A5, $0001, $02A0, $00D0, $0240, $01A5
D_7930:  DECLE   $0040, $0240, $01A6, $02C2, $01AD, $037A, $012C, $0205  ; ".@.@.......z.,.."
D_7940:  DECLE   $0012, $033A, $012C, $02BB, $017C, $0298, $0008, $0258  ; "...:.,...|.....X"
D_7950:  DECLE   $0280, $033F, $0080, $0224, $000F, $000B, $0298, $0008
D_7960:  DECLE   $0258, $0220, $0015, $0242, $01AD, $01C0, $0240, $01A8  ; ".X. ...B.....@.."
D_7970:  DECLE   $0004, $0154, $03DA, $02B7, $02BA, $019D, $02C2, $019C
D_7980:  DECLE   $0290, $03B8, $0080, $0204, $0005, $0001, $02B8, $004B
D_7990:  DECLE   $0008, $0260, $02B7, $0001, $02B8, $00F8, $00EF, $02B9
D_79A0:  DECLE   $0007, $009B, $0204, $0004, $0001, $02B9, $0005, $0010
D_79B0:  DECLE   $02FB, $0335, $0398, $01C8, $0258, $02B7, $0014, $0020
D_79C0:  DECLE   $006C, $0011, $004C, $0027, $004C, $0001, $006C, $0007  ; ".l...L.'.L...l.."
D_79D0:  DECLE   $003A, $001E, $005C, $0031, $000C, $0020, $0026, $0036  ; ".:...\.1... .&.6"
D_79E0:  DECLE   $0033, $0009, $004F, $0019, $000C, $0027, $002F, $0029  ; ".3...O.....'./.)"
D_79F0:  DECLE   $0071, $0022, $0006, $0036, $002B, $000E, $0068, $0006  ; ".q."...6.+...h.."
D_7A00:  DECLE   $002B, $0021, $006C, $000A, $0024, $0022, $007D, $000A  ; ".+.!.l...$.".}.."
D_7A10:  DECLE   $004D, $002E, $000F, $0009, $006F, $0029, $000C, $0018  ; ".M.......o.)...."
D_7A20:  DECLE   $000C, $0037, $002D, $002E, $002D, $000A, $0054, $0024  ; "...7.-...-...T.$"
D_7A30:  DECLE   $000F, $0029, $006C, $0037, $001A, $0002, $0029, $0021  ; "...).l.7.....).!"
D_7A40:  DECLE   $004C, $0001, $002C, $0012, $0045, $0002, $0002, $001A
D_7A50:  DECLE   $003D, $002A, $002F, $0009, $0004, $0026, $0013, $002E  ; ".=.*./.....&...."
D_7A60:  DECLE   $000B, $003D, $0052, $0018, $003A, $0022, $0053, $0036  ; "...=.R...:.".S.6"
D_7A70:  DECLE   $0073, $0028, $0075, $002A, $002A, $002E, $004B, $0001  ; ".s.(.u.*.*...K.."
D_7A80:  DECLE   $0054, $0001, $003C, $0030, $001E, $0010, $000C, $002E  ; ".T...<.0........"
D_7A90:  DECLE   $004D, $0017, $004F, $0017, $0051, $0017, $0074, $0004  ; ".M...O...Q...t.."
D_7AA0:  DECLE   $006B, $000F, $0006, $0016, $002F, $0019, $002C, $0007
D_7AB0:  DECLE   $0032, $003A, $002B, $003C, $004F, $0038, $007E, $001E  ; ".2.:.+.<.O.8.~.."
D_7AC0:  DECLE   $0087, $001E, $008E, $001E, $0090, $001E, $0098, $001E
D_7AD0:  DECLE   $00A6, $001E, $00AE, $001E, $00B0, $001E, $0076, $001E
D_7AE0:  DECLE   $0060, $000E, $006B, $0008, $004B, $0008, $0053, $001E  ; ".`...k...K...S.."
D_7AF0:  DECLE   $005B, $001E, $005B, $005E, $005B, $009E, $005B, $00DE  ; ".[...[.^.[...[.."
D_7B00:  DECLE   $01CD, $020F, $010A, $0128, $0007, $00C1, $0083, $0045
D_7B10:  DECLE   $014C, $01CD, $020F, $0108, $0020, $0062, $00A4, $00E6
D_7B20:  DECLE   $014C, $01CD, $020F, $0048, $0020, $0062, $00A4, $00E6  ; ".L.....H. .b...."
D_7B30:  DECLE   $01AC, $01EE, $0050, $0020, $0083, $00C5, $0042, $0000
D_7B40:  DECLE   $0100, $0101, $0102, $0103, $0104, $0105, $0106, $0107
D_7B50:  DECLE   $0108, $0000, $0118, $0119, $011A, $011B, $011C, $011D
D_7B60:  DECLE   $011E, $011F, $0120, $0121, $0022, $0030, $0024, $005A  ; "..... .!.".0.$.Z"
D_7B70:  DECLE   $005B, $005B, $0003, $0003, $0003, $0003, $0058, $0058  ; ".[.[.........X.X"
D_7B80:  DECLE   $005B, $005D, $005D, $005D, $005D, $005D, $0015, $005D  ; ".[.].].].].]...]"
D_7B90:  DECLE   $005D, $005D, $005D, $0058, $0058, $0058, $0098, $006C  ; ".].].].X.X.X...l"
D_7BA0:  DECLE   $0011, $006D, $0086, $006D, $0013, $006E, $009E, $006E  ; "...m...m...n...n"
D_7BB0:  DECLE   $0020, $006F, $009E, $006F, $0042, $006A, $0084, $0020  ; ". .o...o.B.j... "
D_7BC0:  DECLE   $0006, $00A6, $00AA, $0002, $0080, $0040, $002A, $0086
D_7BD0:  DECLE   $00A2, $0004, $0026, $006A, $0004, $008A, $0086, $0024
D_7BE0:  DECLE   $004A, $00A8, $0060, $0024, $0068, $0046, $000A, $002C  ; ".J...`.$.h.F...,"
D_7BF0:  DECLE   $00A2, $0048, $0008, $0060, $0275, $0093, $0004, $0160  ; "...H...`.u.....`"
D_7C00:  DECLE   $0054, $0001, $02B8, $002A, $0066, $01C9, $0001, $02BA
D_7C10:  DECLE   $0032, $0066, $0272, $0271, $0004, $0164, $024E, $02B2  ; ".2.f.r.q...d.N.."
D_7C20:  DECLE   $001A, $0191, $001A, $01D1, $02B2, $0001, $02FA, $0007
D_7C30:  DECLE   $0000, $0001, $037A, $0047, $0066, $020E, $000A, $0001
D_7C40:  DECLE   $037A, $0040, $0066, $022C, $001A, $02FC, $0012, $0220  ; ".z.@.f.,....... "
D_7C50:  DECLE   $001E, $02B7, $0101, $0102, $010A, $0109, $0103, $0104
D_7C60:  DECLE   $0105, $0000, $0005, $0004, $0001, $0010, $0020, $0041
D_7C70:  DECLE   $0041, $0006, $0004, $0002, $0010, $0020, $0042, $0042  ; ".A......... .B.B"
D_7C80:  DECLE   $0009, $0008, $0001, $0010, $0020, $0041, $0041, $000A
D_7C90:  DECLE   $0008, $0002, $0010, $0020, $0042, $0042, $0275, $0272  ; "....... .B.B.u.r"
D_7CA0:  DECLE   $0004, $0164, $025F, $02B2, $0089, $0204, $0007, $0071
D_7CB0:  DECLE   $0201, $0003, $000A, $0220, $0005, $0291, $02B7, $0275
D_7CC0:  DECLE   $0270, $0085, $0001, $02B8, $00F8, $0009, $03A0, $01C9
D_7CD0:  DECLE   $02AA, $0092, $0204, $000B, $004E, $004A, $0150, $020C
D_7CE0:  DECLE   $0002, $0007, $000F, $0006, $0051, $0220, $000E, $02B0
D_7CF0:  DECLE   $02B7, $0275, $0004, $0164, $01FC, $0089, $0204, $004A
D_7D00:  DECLE   $0379, $0010, $0205, $0015, $020E, $0002, $0200, $008F
D_7D10:  DECLE   $0379, $0040, $020D, $0002, $0200, $008D, $0241, $018C
D_7D20:  DECLE   $0004, $0164, $0313, $0281, $018C, $03F9, $0040, $0200
D_7D30:  DECLE   $0003, $0004, $0168, $0132, $02FB, $0325, $0298, $0001
D_7D40:  DECLE   $03B8, $00FF, $00FE, $0258, $02B8, $0001, $0282, $0179
D_7D50:  DECLE   $0018, $0182, $0018, $01C2, $0242, $0179, $02B8, $0028
D_7D60:  DECLE   $0075, $0209, $0003, $0020, $0200, $0002, $020A, $0002
D_7D70:  DECLE   $0240, $0108, $02B8, $0028, $0075, $0209, $0003, $0020  ; ".@.....(.u..... "
D_7D80:  DECLE   $0200, $0002, $020A, $0002, $0240, $010C, $02B8, $000A
D_7D90:  DECLE   $0240, $034D, $02B7, $0275, $0004, $0164, $01FC, $0089  ; ".@.M...u...d...."
D_7DA0:  DECLE   $0204, $0024, $0379, $0010, $0205, $000E, $0088, $03B8
D_7DB0:  DECLE   $0040, $0204, $001B, $0271, $0273, $0004, $0164, $0313  ; ".@.....q.s...d.."
D_7DC0:  DECLE   $02B3, $02B1, $03F9, $0040, $02B8, $0325, $02BA, $0126
D_7DD0:  DECLE   $02BC, $00F8, $0004, $0164, $02F7, $02B8, $032D, $02BA
D_7DE0:  DECLE   $0136, $02BC, $0078, $0004, $0164, $02F7, $02B7, $0275  ; ".6...x...d.....u"
D_7DF0:  DECLE   $0273, $004B, $00DA, $0063, $00C3, $0298, $0075, $0209  ; ".s.K...c.....u.."
D_7E00:  DECLE   $0005, $02F8, $0008, $01A0, $0200, $0003, $020A, $0009
D_7E10:  DECLE   $01A0, $03FC, $0007, $001C, $039C, $01E0, $0258, $01E4
D_7E20:  DECLE   $0254, $02B3, $02B7, $0275, $0099, $0200, $0080, $02B9
D_7E30:  DECLE   $0001, $0200, $0002, $01C9, $0011, $0001, $02BA, $0008
D_7E40:  DECLE   $0000, $0089, $0203, $0001, $0022, $02C1, $019C, $0241
D_7E50:  DECLE   $019C, $0004, $0154, $01F7, $02C2, $02F4, $0242, $02F4
D_7E60:  DECLE   $0001, $02B9, $0051, $0067, $02BB, $0002, $02BC, $0266
D_7E70:  DECLE   $0004, $0158, $01CF, $0280, $019C, $0008, $02B9, $0001
D_7E80:  DECLE   $0004, $0118, $00C5, $0004, $0158, $0227, $0280, $0103
D_7E90:  DECLE   $0080, $022C, $0004, $0003, $0004, $015C, $02E2, $0002
L_TEXT_STAIRS:
        DECLE   $02B7, $0053, $0074, $0061, $0069, $0072, $0073, $0020  ; "...S.t.a.i.r.s. "
D_7EB0:  DECLE   $0074, $006F, $0020, $006C, $0065, $0076, $0065, $006C  ; ".t.o. .l.e.v.e.l"
D_7EC0:  DECLE   $0020, $0000, $0275, $0090, $0010, $0141, $020C, $0001
D_7ED0:  DECLE   $02B7, $0271, $0272, $0080, $0204, $000D, $0093, $0001
D_7EE0:  DECLE   $02B9, $0058, $005B, $0004, $015C, $037C, $02FB, $0010  ; "...X.[...\.|...."
D_7EF0:  DECLE   $02B8, $0014, $0258, $02B8, $0001, $0004, $0114, $027D
D_7F00:  DECLE   $0080, $020C, $0005, $0004, $016C, $0065, $0200, $0003
D_7F10:  DECLE   $0004, $016C, $0074, $02B2, $02B1, $0200, $0008, $0275
D_7F20:  DECLE   $0271, $0272, $0004, $0168, $0121, $02B2, $02B1, $0280  ; ".q.r...h.!......"
D_7F30:  DECLE   $018B, $03B8, $0002, $0204, $0011, $0379, $0002, $020C
D_7F40:  DECLE   $000D, $037A, $0001, $0204, $0021, $0001, $02BB, $0005
D_7F50:  DECLE   $0010, $0004, $0168, $012F, $0200, $0019, $0089, $020C
D_7F60:  DECLE   $0007, $02BB, $0007, $0004, $0168, $0132, $0200, $000F
D_7F70:  DECLE   $02F9, $032D, $0288, $0001, $03B8, $0000, $0020, $0204
D_7F80:  DECLE   $0005, $0339, $032D, $0004, $0168, $004A, $02B7, $02F9  ; "...9.-...h.J...."
D_7F90:  DECLE   $0335, $0288, $0001, $03B8, $0007, $0010, $0158, $020C
D_7FA0:  DECLE   $0002, $0200, $0015, $01ED, $0001, $0378, $0000, $0010
D_7FB0:  DECLE   $020C, $0008, $0245, $0179, $0245, $0108, $0245, $010C  ; ".....E.y.E...E.."
D_7FC0:  DECLE   $0200, $0002, $0245, $018D, $0339, $0335, $0200, $0063  ; ".....E...9.5...c"
D_7FD0:  DECLE   $0339, $0010, $008B, $02B8, $0029, $0040, $02B9, $0028  ; ".9.......).@...("
D_7FE0:  DECLE   $0041, $0004, $0168, $012A, $033B, $0325, $0098, $0004  ; ".A...h.*.;.%...."
D_7FF0:  DECLE   $0114, $0345, $0281, $01A3, $01C1, $0241, $01A3, $004B
D_8000:  DECLE   $0204, $0007, $02FB, $0126, $0004, $0160, $003F, $0200
D_8010:  DECLE   $0004, $0243, $0108, $0243, $010C, $0004, $015C, $03A1
D_8020:  DECLE   $0028, $0282, $01A3, $01C0, $0240, $01A3, $0076, $0209
D_8030:  DECLE   $000B, $0001, $02BC, $0000, $0010, $01DB, $0004, $0168
D_8040:  DECLE   $0032, $01C0, $0240, $01AB, $0072, $0209, $000A, $02BC
D_8050:  DECLE   $0001, $02BB, $0002, $0004, $0168, $0032, $01C0, $0240
D_8060:  DECLE   $01AC, $02B7, $0275, $02FB, $0325, $02B8, $0029, $0040  ; ".....u...%...).@"
D_8070:  DECLE   $0001, $02B9, $0000, $0009, $0004, $0168, $012A, $02FB
D_8080:  DECLE   $0010, $0001, $02B8, $0007, $0010, $00A1, $0004, $0168
D_8090:  DECLE   $012A, $02B7, $0275, $008B, $0273, $004B, $02FB, $0126  ; ".*...u...s.K...&"
D_80A0:  DECLE   $0004, $0160, $003F, $037B, $0136, $020C, $0003, $0004  ; "...`.?.{.6......"
D_80B0:  DECLE   $0158, $0227, $02B3, $02FB, $0325, $02B9, $002C, $0041  ; ".X.'.....%...,.A"
D_80C0:  DECLE   $0088, $03F8, $0100, $0004, $0168, $012A, $02FB, $0008
D_80D0:  DECLE   $02B8, $0100, $0081, $0004, $0168, $012A, $02FB, $0018
D_80E0:  DECLE   $02B8, $0040, $0258, $0001, $02B9, $0094, $005B, $033B  ; "...@.X.......[.;"
D_80F0:  DECLE   $0345, $0004, $015C, $037C, $02FB, $0010, $02B8, $0040  ; ".E...\.|.......@"
D_8100:  DECLE   $0258, $033B, $0027, $0298, $0001, $03B8, $0000, $0040  ; ".X.;.'.........@"
D_8110:  DECLE   $0204, $0008, $033B, $0325, $0004, $015C, $0360, $0004  ; ".....;.%...\.`.."
D_8120:  DECLE   $016C, $0054, $02B7, $0275, $0280, $018B, $03B8, $0002
D_8130:  DECLE   $0204, $001E, $037B, $0002, $020C, $001A, $02BA, $0003
D_8140:  DECLE   $0004, $0160, $007A, $0280, $017D, $0080, $020C, $000B
D_8150:  DECLE   $0004, $015C, $0360, $01C0, $0240, $0187, $0008, $0240  ; "...\.`...@.....@"
D_8160:  DECLE   $019A, $0200, $004C, $0010, $0240, $017D, $0200, $001C
D_8170:  DECLE   $009B, $020C, $0041, $0243, $0108, $0243, $010C, $0243  ; ".....A.C...C...C"
D_8180:  DECLE   $0179, $0280, $018B, $03B8, $0080, $0204, $000D, $0280
D_8190:  DECLE   $017C, $0080, $020C, $0005, $0004, $0168, $03C7, $0200
D_81A0:  DECLE   $002E, $0010, $0240, $017C, $02FB, $0325, $02B8, $0024  ; ".....@.|...%...$"
D_81B0:  DECLE   $0040, $02B9, $0020, $0041, $0004, $0168, $012A, $02FB  ; ".@... .A...h.*.."
D_81C0:  DECLE   $0008, $0298, $0001, $03B8, $007F, $00FE, $0258, $02FB
D_81D0:  DECLE   $0008, $02B8, $01C0, $0258, $033B, $0335, $0001, $02B9
D_81E0:  DECLE   $009A, $005B, $0004, $015C, $037C, $02FB, $0010, $02B8
D_81F0:  DECLE   $00B4, $0258, $0200, $0003, $0004, $0168, $0100, $02B7
D_8200:  DECLE   $0275, $0004, $0168, $0113, $0098, $0004, $0114, $0345
D_8210:  DECLE   $0018, $0380, $0187, $0240, $0187, $02BA, $0002, $0004
D_8220:  DECLE   $015C, $035E, $02B7, $009A, $02B8, $0003, $0062, $004C  ; ".\.^.........b.L"
D_8230:  DECLE   $0012, $022C, $0003, $0018, $0380, $017B, $0240, $017B  ; "...,.......{.@.{"
D_8240:  DECLE   $00AF, $0275, $0093, $0004, $015C, $0360, $0004, $0118
D_8250:  DECLE   $0283, $02B7, $0018, $0398, $01C8, $0258, $00AF, $02BA
D_8260:  DECLE   $0001, $000F, $01D2, $02FA, $01AB, $0290, $0080, $0204
D_8270:  DECLE   $0001, $02B7, $0008, $0250, $00AF, $0275, $0280, $019A
D_8280:  DECLE   $0080, $020C, $0002, $0200, $0002, $0200, $005E, $02BB
D_8290:  DECLE   $0002, $0004, $015C, $03B4, $02BC, $00A7, $02BB, $0015
D_82A0:  DECLE   $0004, $0168, $0196, $0270, $02BC, $0068, $02BB, $000D
D_82B0:  DECLE   $0088, $0004, $0168, $0196, $02B1, $01ED, $02BA, $007F
D_82C0:  DECLE   $0151, $0205, $0002, $000D, $0191, $0150, $0205, $0002
D_82D0:  DECLE   $000D, $0191, $00AD, $0204, $0028, $02C1, $0175, $0011
D_82E0:  DECLE   $0191, $0241, $0197, $02C0, $0176, $0010, $0062, $0190
D_82F0:  DECLE   $0240, $0198, $01C0, $0240, $0187, $0008, $0240, $019A
D_8300:  DECLE   $0281, $0337, $0001, $03B9, $0000, $0010, $0204, $0001
D_8310:  DECLE   $0010, $0240, $019B, $0280, $019C, $0240, $0199, $02BA
D_8320:  DECLE   $0002, $0093, $0004, $015C, $035E, $02B7, $0082, $0122
D_8330:  DECLE   $020E, $0003, $0064, $0060, $00AF, $02B8, $0080, $033A
D_8340:  DECLE   $000A, $020E, $0001, $00D8, $00AF, $0280, $019C, $0340
D_8350:  DECLE   $0199, $020C, $004E, $0280, $0197, $0281, $0198, $0004
D_8360:  DECLE   $0160, $0394, $0080, $020B, $0044, $0271, $0270, $02BA  ; ".`.......D.q.p.."
D_8370:  DECLE   $0002, $02BB, $0327, $0001, $02BC, $005C, $005A, $0004
D_8380:  DECLE   $015C, $03C1, $02B1, $004D, $0049, $02BC, $0008, $00E1
D_8390:  DECLE   $0001, $02B8, $0000, $0099, $01C1, $02BB, $0327, $0004
D_83A0:  DECLE   $0168, $012A, $00E3, $02B1, $004D, $0049, $00E1, $0001  ; ".h.*.....M.I...."
D_83B0:  DECLE   $02B8, $0080, $00A0, $01C1, $0004, $0168, $012A, $0280
D_83C0:  DECLE   $019B, $0080, $0204, $0007, $00E3, $0298, $0001, $03F8
D_83D0:  DECLE   $0004, $0010, $0258, $01C0, $0240, $019A, $0240, $018D
D_83E0:  DECLE   $0240, $01AC, $02BB, $0002, $0280, $0196, $0004, $0158
D_83F0:  DECLE   $0085, $02B7, $0275, $0280, $0184, $0080, $0204, $000A
D_8400:  DECLE   $0281, $017E, $0011, $020C, $0005, $02B9, $0004, $0010
D_8410:  DECLE   $0240, $0184, $0241, $017E, $02C0, $0163, $0240, $0163  ; ".@...A.~...c.@.c"
D_8420:  DECLE   $02B8, $0005, $0300, $019C, $0004, $0114, $029E, $0080
D_8430:  DECLE   $020C, $0033, $02BA, $0002, $02B8, $0003, $0004, $0168
D_8440:  DECLE   $026A, $009B, $020B, $0029, $0004, $0168, $027D, $02FB  ; ".j.....)...h.}.."
D_8450:  DECLE   $0325, $02BA, $0002, $0273, $0004, $015C, $03C1, $02B3
D_8460:  DECLE   $009A, $02FA, $0018, $0290, $0001, $0378, $0076, $005B
D_8470:  DECLE   $020C, $0005, $0004, $0168, $02F9, $0200, $000E, $0004
D_8480:  DECLE   $0168, $028F, $033B, $0325, $0004, $0168, $024E, $0004  ; ".h...;.%...h.N.."
D_8490:  DECLE   $0168, $02AE, $0004, $0168, $02DB, $02B7, $0275, $009A
D_84A0:  DECLE   $02B8, $0001, $0004, $0154, $0146, $0081, $02B8, $0002
D_84B0:  DECLE   $0004, $0114, $029E, $0080, $0204, $0001, $01C9, $0280
D_84C0:  DECLE   $019A, $0080, $0204, $0001, $01C9, $03C1, $0187, $0241
D_84D0:  DECLE   $0187, $02B7, $01DB, $0281, $017B, $0181, $0204, $0008
D_84E0:  DECLE   $004C, $02FB, $0002, $037B, $0007, $0226, $000B, $0023  ; ".L.....{...&...#"
D_84F0:  DECLE   $03C0, $017B, $0240, $017B, $00AF, $0275, $02B8, $0005  ; "...{.@.{...u...."
D_8500:  DECLE   $0300, $019C, $0004, $0114, $029E, $0001, $02BC, $00B4
D_8510:  DECLE   $005A, $0080, $020C, $0002, $02FC, $001C, $02B7, $0275
D_8520:  DECLE   $02B8, $0004, $0004, $0114, $029E, $0048, $0001, $02BC
D_8530:  DECLE   $00A6, $006A, $00C4, $02A0, $03D8, $0258, $02FB, $0008
D_8540:  DECLE   $02A0, $03D8, $0258, $033B, $0008, $02B7, $0000, $0034
D_8550:  DECLE   $0058, $0000, $00A8, $0034, $0058, $006B, $0275, $009C  ; ".X.....4.X.k.u.."
D_8560:  DECLE   $02FC, $0325, $0273, $009A, $02BB, $0325, $02B8, $0001
D_8570:  DECLE   $0004, $0154, $0146, $0380, $0187, $0204, $0002, $02FB
D_8580:  DECLE   $0002, $029A, $03BA, $00FF, $02FB, $0008, $029B, $03BB
D_8590:  DECLE   $007F, $00A1, $02F9, $0028, $0280, $0186, $0248, $0281
D_85A0:  DECLE   $0185, $0004, $0160, $0011, $02B1, $0271, $0004, $015C
D_85B0:  DECLE   $0323, $02B3, $02B7, $0275, $009A, $0062, $0012, $02FA
D_85C0:  DECLE   $0188, $0250, $009A, $02FA, $034E, $02B9, $000F, $0251
D_85D0:  DECLE   $0001, $02BC, $00AE, $005B, $0004, $0160, $0318, $02B7
D_85E0:  DECLE   $0275, $01C0, $0004, $0168, $02AE, $0004, $0168, $02DB
D_85F0:  DECLE   $02B7, $0275, $0273, $02B8, $0010, $0004, $0114, $029E
D_8600:  DECLE   $0240, $01A1, $02B9, $001C, $0021, $0004, $0160, $0046  ; ".@.......!...`.F"
D_8610:  DECLE   $02F9, $0058, $02FA, $0038, $02B8, $00FF, $0018, $02B3
D_8620:  DECLE   $029C, $0184, $01CC, $025C, $02FB, $0008, $029C, $0068
D_8630:  DECLE   $0184, $01D4, $025C, $0004, $0168, $03EA, $02B7, $0275
D_8640:  DECLE   $02FB, $0345, $0298, $0080, $020B, $0005, $0004, $0168
D_8650:  DECLE   $0332, $0200, $0006, $0004, $0118, $0283, $0004, $0168
D_8660:  DECLE   $0352, $02B7, $0275, $0280, $01A1, $033B, $0345, $0004  ; ".R...u.....;.E.."
D_8670:  DECLE   $0158, $0085, $02FB, $0008, $0299, $03F9, $0005, $0259
D_8680:  DECLE   $02FB, $0008, $0001, $02B9, $007C, $005B, $0259, $02FB
D_8690:  DECLE   $0010, $02B9, $0019, $0259, $033B, $01E6, $02B8, $00FF
D_86A0:  DECLE   $0258, $02B7, $0275, $033B, $0345, $02BA, $0002, $0004  ; ".X...u.;.E......"
D_86B0:  DECLE   $015C, $035E, $02B8, $0003, $0004, $0114, $029E, $0080
D_86C0:  DECLE   $0204, $0004, $0004, $0168, $0113, $02B7, $02BA, $0002
D_86D0:  DECLE   $02FB, $0325, $0001, $02BC, $00D0, $005A, $0273, $0004
D_86E0:  DECLE   $015C, $03C1, $02B3, $0004, $0168, $02F9, $02B7, $0275
D_86F0:  DECLE   $009C, $02FB, $0326, $0298, $0001, $03B8, $0000, $0040
D_8700:  DECLE   $0204, $0028, $02FC, $034D, $02B8, $0023, $0260, $0298  ; "...(...M...#.`.."
D_8710:  DECLE   $0001, $03F8, $0000, $0008, $0258, $0004, $015C, $034F
D_8720:  DECLE   $009C, $033C, $0008, $02FB, $0020, $02BA, $0004, $025A
D_8730:  DECLE   $0282, $0325, $03BA, $00FF, $0283, $032D, $03BB, $007F
D_8740:  DECLE   $02B9, $0064, $0004, $0160, $0011, $0004, $0168, $03F8
D_8750:  DECLE   $0200, $001C, $02FB, $001F, $0001, $02B8, $0023, $0080
D_8760:  DECLE   $0258, $033B, $0008, $0001, $02B8, $0076, $005B, $0258  ; ".X.;.......v.[.X"
D_8770:  DECLE   $033B, $0008, $0298, $03F8, $0005, $0258, $02FB, $0018
D_8780:  DECLE   $02B8, $002D, $0258, $0004, $016C, $0054, $02B7, $0275  ; "...-.X...l.T...u"
D_8790:  DECLE   $0004, $015C, $035B, $0004, $0160, $0076, $0001, $02B8  ; "...\.[...`.v...."
D_87A0:  DECLE   $00F4, $0062, $0240, $035D, $02BC, $027D, $0001, $02BB  ; "...b.@.]...}...."
L_TEXT_GAMEOVER:
        DECLE   $0000, $0016, $0004, $0118, $007B, $0020, $0047, $0041  ; ".........{. .G.A"
D_87C0:  DECLE   $004D, $0045, $0020, $004F, $0056, $0045, $0052, $0020  ; ".M.E. .O.V.E.R. "
D_87D0:  DECLE   $0000, $02B7, $0275, $0004, $0118, $03BE, $0088, $01ED
D_87E0:  DECLE   $0137, $03CB, $003C, $00F8, $02F9, $008F, $0020, $02CF
D_87F0:  DECLE   $01C0, $0275, $0004, $0118, $03BE, $0090, $03ED, $03E5
D_8800:  DECLE   $02F9, $016B, $0077, $0009, $006C, $0023, $03EC, $0023  ; "...k.w...l.#...#"
D_8810:  DECLE   $03F8, $0280, $0155, $0378, $0004, $0206, $0005, $0338
D_8820:  DECLE   $0004, $0240, $0155, $02B7, $0001, $02BC, $0007, $006C
D_8830:  DECLE   $02B7, $0275, $0004, $0118, $03BE, $0084, $000D, $0137
D_8840:  DECLE   $000B, $000C, $0080, $02F9, $006B, $02CF, $0275, $0004
D_8850:  DECLE   $0118, $03BE, $0090, $0088, $0040, $03D9, $00AB, $0248
D_8860:  DECLE   $0048, $00AB, $02C8, $0041, $00AB, $0308, $0047, $00AB
D_8870:  DECLE   $0348, $0042, $00AB, $0388, $0046, $00AB, $03C8, $0043  ; ".H.B.....F.....C"
D_8880:  DECLE   $00AB, $0388, $0045, $00AB, $0348, $0044, $00AB, $0308
D_8890:  DECLE   $0046, $00AB, $02C8, $0040, $00AB, $0248, $0044, $00AB  ; ".F.....@...H.D.."
D_88A0:  DECLE   $0088, $0040, $00AB, $02CF, $0275, $0004, $0118, $03BE
D_88B0:  DECLE   $009A, $02F9, $0137, $000D, $000C, $0200, $038B, $022B
D_88C0:  DECLE   $003C, $0300, $008F, $0040, $02CF, $0275, $0004, $0118
D_88D0:  DECLE   $03BE, $0090, $0048, $0020, $0137, $000B, $002C, $0200  ; ".....H. .7...,.."
D_88E0:  DECLE   $016D, $02D9, $03EB, $02CF, $0275, $0004, $0118, $03BE
D_88F0:  DECLE   $0090, $0048, $0040, $0137, $000B, $002C, $0200, $02D9  ; "...H.@.7...,...."
D_8900:  DECLE   $016D, $03EB, $02CF, $0275, $0280, $01AA, $0080, $0204
D_8910:  DECLE   $000E, $01C0, $0281, $017F, $0379, $0064, $020E, $0004
D_8920:  DECLE   $0299, $02F9, $0005, $0259, $0004, $016C, $0019, $02B7
D_8930:  DECLE   $000A, $0122, $0061, $0125, $0061, $0126, $0061, $0128  ; "...".a.%.a.&.a.("
D_8940:  DECLE   $0061, $0127, $000A, $0122, $0061, $0125, $0061, $0126  ; ".a.'...".a.%.a.&"
D_8950:  DECLE   $0061, $0128, $0061, $0127, $000C, $0122, $0061, $0124  ; ".a.(.a.'...".a.$"
D_8960:  DECLE   $0001, $00A1, $008A, $00E1, $0121, $0083, $0061, $0127
D_8970:  DECLE   $0008, $0122, $0061, $0125, $0061, $012F, $0061, $0127  ; "...".a.%.a./.a.'"
D_8980:  DECLE   $0007, $0082, $00C1, $0125, $0061, $012F, $0088, $0004
D_8990:  DECLE   $0128, $0101, $0137, $0003, $013F, $0121, $0003, $013F  ; ".(...7...?.!...?"
D_89A0:  DECLE   $0121, $0007, $0088, $0061, $012E, $0001, $00A1, $0087
D_89B0:  DECLE   $0006, $0128, $0061, $012F, $0061, $0127, $0006, $0128  ; "...(.a./.a.'...("
D_89C0:  DECLE   $0061, $012F, $0101, $0127, $0004, $0128, $0061, $0137  ; ".a./...'...(.a.7"
D_89D0:  DECLE   $000C, $0082, $0061, $0124, $0001, $0061, $012F, $00A1  ; ".....a.$...a./.."
D_89E0:  DECLE   $0084, $00E1, $0121, $0081, $0008, $0122, $0061, $0125  ; ".....!.....".a.%"
D_89F0:  DECLE   $0061, $012F, $0061, $0127, $0008, $0122, $0061, $0125  ; ".a./.a.'...".a.%"
D_8A00:  DECLE   $0061, $012F, $0061, $0127, $000D, $0122, $0061, $0125  ; ".a./.a.'...".a.%"
D_8A10:  DECLE   $00A1, $0086, $00A1, $0084, $00E1, $0121, $0082, $0061
D_8A20:  DECLE   $0127, $000D, $0122, $0061, $0125, $0061, $0126, $00A1  ; ".'...".a.%.a.&.."
D_8A30:  DECLE   $0083, $00E1, $0121, $0083, $00C1, $0127, $0009, $0122
D_8A40:  DECLE   $0061, $0124, $0001, $0061, $0126, $0061, $0130, $0008  ; ".a.$...a.&.a.0.."
D_8A50:  DECLE   $0122, $0061, $0125, $0061, $0126, $0061, $0130, $0007  ; ".".a.%.a.&.a.0.."
D_8A60:  DECLE   $0122, $0061, $0125, $0087, $00C1, $0130, $0005, $0085  ; ".".a.%.....0...."
D_8A70:  DECLE   $00E1, $012F, $008B, $0003, $013F, $0121, $0003, $013F  ; ".../.....?.!...?"
D_8A80:  DECLE   $0121, $0003, $013F, $0121, $0006, $008A, $0061, $0126  ; ".!...?.!.....a.&"
D_8A90:  DECLE   $0001, $008E, $0004, $012A, $0061, $0135, $0004, $012A  ; ".......*.a.5...*"
D_8AA0:  DECLE   $0101, $0135, $0003, $013F, $0121, $0013, $0082, $00A1
D_8AB0:  DECLE   $0081, $00E1, $0121, $0082, $00A1, $0086, $00A1, $0082
D_8AC0:  DECLE   $00E1, $0122, $0083, $00A1, $0081, $00E1, $0122, $0083
D_8AD0:  DECLE   $000A, $0122, $0061, $0125, $0061, $0126, $0061, $0128  ; "...".a.%.a.&.a.("
D_8AE0:  DECLE   $0061, $0127, $000A, $0122, $0061, $0125, $0061, $0126  ; ".a.'...".a.%.a.&"
D_8AF0:  DECLE   $0061, $0128, $0061, $0127, $000A, $0122, $0061, $0125  ; ".a.(.a.'...".a.%"
D_8B00:  DECLE   $0061, $0126, $0061, $0128, $0061, $0127, $000A, $0122  ; ".a.&.a.(.a.'...""
D_8B10:  DECLE   $0061, $0125, $0061, $0126, $0061, $0128, $0061, $0127  ; ".a.%.a.&.a.(.a.'"
D_8B20:  DECLE   $000B, $0121, $0001, $0061, $0125, $0061, $0126, $0061  ; "...!...a.%.a.&.a"
D_8B30:  DECLE   $0128, $0021, $0127, $000A, $0122, $0061, $0125, $0101  ; ".(.!.'...".a.%.."
D_8B40:  DECLE   $0126, $0061, $0128, $0041, $0127, $0008, $0122, $0061  ; ".&.a.(.A.'...".a"
D_8B50:  DECLE   $012C, $0061, $0128, $0061, $0127, $0006, $008F, $0061  ; ".,.a.(.a.'.....a"
D_8B60:  DECLE   $0128, $00A1, $0087, $0006, $012F, $0061, $0128, $0061  ; ".(......./.a.(.a"
D_8B70:  DECLE   $0127, $0006, $012F, $0061, $0128, $0021, $0127, $0006  ; ".'.../.a.(.!.'.."
D_8B80:  DECLE   $012F, $0061, $0128, $0041, $0127, $000A, $0086, $00E1  ; "./.a.(.A.'......"
D_8B90:  DECLE   $0124, $0084, $0061, $0128, $0083, $00A1, $0084, $000A
D_8BA0:  DECLE   $0128, $0061, $0126, $0021, $0128, $0021, $0122, $0061  ; ".(.a.&.!.(.!.".a"
D_8BB0:  DECLE   $0124, $000A, $0128, $0061, $0126, $0041, $0128, $0041  ; ".$...(.a.&.A.(.A"
D_8BC0:  DECLE   $0122, $0061, $0124, $000A, $0128, $0061, $0126, $0061  ; ".".a.$...(.a.&.a"
D_8BD0:  DECLE   $0128, $0061, $0122, $0061, $0124, $000C, $0082, $0061  ; ".(.a.".a.$.....a"
D_8BE0:  DECLE   $0122, $0083, $00A1, $0086, $00A1, $0088, $00C1, $0122
D_8BF0:  DECLE   $0085, $0008, $0122, $0061, $0125, $0061, $0126, $0061  ; ".....".a.%.a.&.a"
D_8C00:  DECLE   $0130, $0000, $0122, $0061, $0125, $0061, $0126, $0061  ; ".0...".a.%.a.&.a"
D_8C10:  DECLE   $0130, $000A, $0122, $0061, $0125, $0061, $0126, $0061  ; ".0...".a.%.a.&.a"
D_8C20:  DECLE   $0128, $0061, $0127, $000A, $0122, $0061, $0125, $0061  ; ".(.a.'...".a.%.a"
D_8C30:  DECLE   $0126, $0061, $0128, $0061, $0127, $000A, $0122, $0061  ; ".&.a.(.a.'...".a"
D_8C40:  DECLE   $0125, $0061, $0126, $0101, $0128, $0061, $0127, $0008  ; ".%.a.&...(.a.'.."
D_8C50:  DECLE   $0122, $0101, $0125, $0061, $012F, $0061, $0127, $0006  ; "."...%.a./.a.'.."
D_8C60:  DECLE   $0128, $0061, $012F, $0061, $0127, $000D, $0083, $00E1  ; ".(.a./.a.'......"
D_8C70:  DECLE   $0123, $0001, $00A1, $0086, $0061, $0122, $0088, $00E1
D_8C80:  DECLE   $0122, $0083, $0006, $0128, $0061, $0126, $0061, $0130  ; ".".....(.a.&.a.0"
D_8C90:  DECLE   $0006, $0128, $0061, $0126, $0061, $0130, $0006, $0128  ; "...(.a.&.a.0...("
D_8CA0:  DECLE   $0061, $0126, $0061, $0130, $0008, $0084, $0061, $0123  ; ".a.&.a.0.....a.#"
D_8CB0:  DECLE   $0101, $0126, $00A1, $0090, $0006, $0124, $0061, $012A  ; "...&.......$.a.*"
D_8CC0:  DECLE   $0061, $0130, $0008, $0124, $0061, $0123, $0061, $0126  ; ".a.0...$.a.#.a.&"
D_8CD0:  DECLE   $0061, $0130, $0008, $0124, $0061, $0123, $00A1, $0086  ; ".a.0...$.a.#...."
D_8CE0:  DECLE   $0061, $0130, $0010, $0082, $00A1, $0081, $00C1, $0123
D_8CF0:  DECLE   $0061, $0126, $0021, $0123, $0085, $00A1, $0082, $00E1  ; ".a.&.!.#........"
D_8D00:  DECLE   $0122, $0082, $000A, $0122, $0061, $0125, $0101, $0126  ; ".".....".a.%...&"
D_8D10:  DECLE   $0041, $0128, $0061, $0127, $0008, $0122, $0061, $012C  ; ".A.(.a.'...".a.,"
D_8D20:  DECLE   $0061, $0128, $0061, $0127, $000A, $0122, $0061, $0125  ; ".a.(.a.'...".a.%"
D_8D30:  DECLE   $0061, $0126, $0061, $0128, $0061, $0127, $000A, $0122  ; ".a.&.a.(.a.'...""
D_8D40:  DECLE   $0061, $0125, $0061, $0126, $0061, $0128, $0061, $0127  ; ".a.%.a.&.a.(.a.'"
D_8D50:  DECLE   $000A, $0122, $0101, $0125, $0061, $0126, $0061, $0128  ; "..."...%.a.&.a.("
D_8D60:  DECLE   $0061, $0127, $0008, $0128, $0061, $0126, $0061, $0128  ; ".a.'...(.a.&.a.("
D_8D70:  DECLE   $0061, $0127, $0008, $0128, $0061, $0126, $0061, $0128  ; ".a.'...(.a.&.a.("
D_8D80:  DECLE   $0061, $0127, $000D, $0088, $00C1, $0125, $0001, $00A1
D_8D90:  DECLE   $0082, $00E1, $0122, $0085, $00E1, $0121, $0084, $0004
D_8DA0:  DECLE   $012F, $0061, $0130, $0004, $012F, $0061, $0130, $0004  ; "./.a.0.../.a.0.."
D_8DB0:  DECLE   $012F, $0061, $0130, $0008, $008C, $00E1, $0121, $0081  ; "./.a.0.......!.."
D_8DC0:  DECLE   $0061, $0128, $0088, $0004, $012F, $0061, $0130, $0004  ; ".a.(...../.a.0.."
D_8DD0:  DECLE   $012F, $0061, $0130, $0004, $012F, $0061, $0130, $0013  ; "./.a.0.../.a.0.."
D_8DE0:  DECLE   $0082, $00A1, $0081, $00E1, $0121, $0082, $00A1, $0082
D_8DF0:  DECLE   $00E1, $0121, $0082, $00A1, $0085, $00E1, $0121, $0081
D_8E00:  DECLE   $00A1, $0087, $000A, $0122, $0061, $0125, $0061, $0126  ; ".......".a.%.a.&"
D_8E10:  DECLE   $0061, $0128, $0061, $0127, $000A, $0122, $0061, $0125  ; ".a.(.a.'...".a.%"
D_8E20:  DECLE   $0061, $0126, $0061, $0128, $0061, $0127, $000A, $0122  ; ".a.&.a.(.a.'...""
D_8E30:  DECLE   $0061, $0125, $0061, $0126, $0061, $0128, $0061, $0127  ; ".a.%.a.&.a.(.a.'"
D_8E40:  DECLE   $000A, $0122, $0061, $0125, $0061, $0126, $0061, $0128  ; "...".a.%.a.&.a.("
D_8E50:  DECLE   $0061, $0127, $000A, $0122, $0061, $0125, $0101, $0126  ; ".a.'...".a.%...&"
D_8E60:  DECLE   $0061, $0128, $0061, $0127, $0008, $0122, $0061, $012C  ; ".a.(.a.'...".a.,"
D_8E70:  DECLE   $0061, $0128, $0101, $0127, $0008, $0122, $0061, $0125  ; ".a.(...'...".a.%"
D_8E80:  DECLE   $0061, $0126, $0061, $0130, $000E, $0088, $00A1, $0082  ; ".a.&.a.0........"
D_8E90:  DECLE   $00E1, $0121, $0082, $00A1, $0084, $00E1, $0121, $0082
D_8EA0:  DECLE   $00A1, $0087, $0008, $0128, $0061, $0126, $0061, $0128  ; ".......(.a.&.a.("
D_8EB0:  DECLE   $0061, $0127, $0008, $0128, $0061, $0126, $0061, $0128  ; ".a.'...(.a.&.a.("
D_8EC0:  DECLE   $0101, $0127, $0006, $0128, $0061, $0126, $0061, $0130  ; "...'...(.a.&.a.0"
D_8ED0:  DECLE   $0007, $0088, $0061, $0126, $0061, $0128, $0088, $0006  ; ".....a.&.a.(...."
D_8EE0:  DECLE   $0128, $0061, $0126, $0061, $0130, $0006, $0128, $0101  ; ".(.a.&.a.0...(.."
D_8EF0:  DECLE   $0126, $0101, $0130, $0003, $013F, $0121, $000A, $0082  ; ".&...0...?.!...."
D_8F00:  DECLE   $00A1, $0084, $00E1, $0122, $0085, $0061, $0128, $0088
D_8F10:  DECLE   $0006, $0122, $0061, $012C, $0061, $0130, $0006, $0122  ; "...".a.,.a.0...""
D_8F20:  DECLE   $0061, $012C, $0061, $0130, $0061, $0122, $0061, $0125  ; ".a.,.a.0.a.".a.%"
D_8F30:  DECLE   $0061, $0126, $0061, $0128, $0061, $0127, $0004, $00A1  ; ".a.&.a.(.a.'...."
D_8F40:  DECLE   $009E, $0061, $0005, $0061, $00A1, $009C, $0062, $0005
D_8F50:  DECLE   $0062, $00A1, $009A, $0063, $0005, $0063, $00A1, $0098
D_8F60:  DECLE   $0064, $0005, $0064, $00A1, $0096, $0065, $0004, $0065  ; ".d...d.....e...e"
D_8F70:  DECLE   $0136, $0065, $0007, $0065, $0141, $0161, $0181, $0133  ; ".6.e...e.A.a...3"
D_8F80:  DECLE   $0065, $000E, $0003, $01A1, $01C1, $01E3, $0201, $0124
D_8F90:  DECLE   $0281, $0121, $02A1, $0121, $02C1, $0129, $0065, $0007  ; "...!...!...).e.."
D_8FA0:  DECLE   $0065, $0221, $0241, $0261, $0133, $0065, $0004, $0065  ; ".e.!.A.a.3.e...e"
D_8FB0:  DECLE   $0136, $0065, $0004, $0065, $0136, $0065, $0005, $0064  ; ".6.e...e.6.e...d"
D_8FC0:  DECLE   $0097, $00C1, $0064, $0005, $0063, $0099, $00C1, $0063
D_8FD0:  DECLE   $0005, $0062, $009B, $00C1, $0062, $0005, $0061, $009D
D_8FE0:  DECLE   $00C1, $0061, $0003, $009F, $00C1, $0000, $0000, $0000
D_8FF0:  BIDECLE $0000, $0000, $0000, $0000, $0000, $0000, $0000, $0000

; End of Data Section $7000-$8FFF
