
        ORG     $1000
X_RESET:
        JSRD    R5,     X_INIT                  ; 1000   0004 0112 0026

X_RET_R5:
        MOVR    R5,     R7                      ; 1003   00AF
X_ISR:
        PSHR    R0                              ; 1004   0270
.EXEC.005:
        GSWD    R0                              ; 1005   0030
.EXEC.006:
        PSHR    R0                              ; 1006   0270
.EXEC.007:
        PSHR    R1                              ; 1007   0271
.EXEC.008:
        PSHR    R2                              ; 1008   0272
.EXEC.009:
        NOP                                     ; 1009   0034
.EXEC.00A:
        PSHR    R3                              ; 100A   0273
.EXEC.00B:
        PSHR    R4                              ; 100B   0274
.EXEC.00C:
        PSHR    R5                              ; 100C   0275
.EXEC.00D:
        MOVR    R7,     R5                      ; 100D   00BD
.EXEC.00E:
        ADDI    #$0006, R5                      ; 100E   02FD 0006
.EXEC.010:
        MVII    #$0100, R4                      ; 1010   02BC 0100
.EXEC.012:
        SDBD                                    ; 1012   0001
.EXEC.013:
        MVI@    R4,     R7                      ; 1013   02A7
X_ISRRET:
        PULR    R5                              ; 1014   02B5
.EXEC.015:
        PULR    R4                              ; 1015   02B4
.EXEC.016:
        PULR    R3                              ; 1016   02B3
.EXEC.017:
        PULR    R2                              ; 1017   02B2
.EXEC.018:
        PULR    R1                              ; 1018   02B1
.EXEC.019:
        PULR    R0                              ; 1019   02B0
.EXEC.01A:
        RSWD    R0                              ; 101A   0038
.EXEC.01B:
        PULR    R0                              ; 101B   02B0
.EXEC.01C:
        PULR    R7                              ; 101C   02B7
X_CHK_KBD_OR_CBL:
        MVI@    R5,     R1                      ; 101D   02A9
.EXEC.01E:
        SWAP    R1,     1                       ; 101E   0041
.EXEC.01F:
        MVI@    R1,     R0                      ; 101F   0288
.EXEC.020:
        SWAP    R0,     1                       ; 1020   0040
.EXEC.021:
        ANDI    #$00FC, R0                      ; 1021   03B8 00FC
.EXEC.023:
        BNEQ    X_RET_R5                        ; 1023   022C 0021

.EXEC.025:
        MOVR    R1,     R7                      ; 1025   008F
X_INIT:
        MVII    #$02F1, R6                      ; 1026   02BE 02F1

.EXEC.028:
        JSR     R5,     .EXEC.A83               ; 1028   0004 0118 0283

.EXEC.02B:
        MVII    #$0026, R0                      ; 102B   02B8 0026
.EXEC.02D:
        MVO     R0,     .ISRVEC.0               ; 102D   0240 0100
.EXEC.02F:
        MVII    #$0011, R0                      ; 102F   02B8 0011
.EXEC.031:
        MVO     R0,     .ISRVEC.1               ; 1031   0240 0101
.EXEC.033:
        SDBD                                    ; 1033   0001
.EXEC.034:
        MVII    #$5014, R0                      ; 1034   02B8 0014 0050
.EXEC.037:
        MVO     R0,     G_02F0                  ; 1037   0240 02F0

.EXEC.039:
        JSR     R5,     X_CHK_KBD_OR_CBL        ; 1039   0004 0110 001D

.EXEC.03C:
        RRC     R0,     1                       ; 103C   0070

.EXEC.03D:
        JSR     R5,     X_CHK_KBD_OR_CBL        ; 103D   0004 0110 001D

.EXEC.040:
        SLL     R0,     1                       ; 1040   0048
.EXEC.041:
        MVII    #$00FE, R0                      ; 1041   02B8 00FE
.EXEC.043:
        MVII    #$0102, R4                      ; 1043   02BC 0102

.EXEC.045:
        JSR     R5,     X_FILL_ZERO             ; 1045   0004 0114 0338
.EXEC.048:
        JSR     R5,     .EXEC.060               ; 1048   0004 0110 0060

.EXEC.04B:
        CMP@    R3,     R6                      ; 104B   035E
.EXEC.04C:
        XORI    #$0147, R7                      ; 104C   03FF 0147
.EXEC.04E:
        DECLE   $0001                           ; 104E   0001
.EXEC.04F:
        SUBR    R2,     R5                      ; 104F   0115
.EXEC.050:
        INCR    R4                              ; 1050   000C
.EXEC.051:
        SUBR    R2,     R6                      ; 1051   0116
.EXEC.052:
        MOVR    R4,     R0                      ; 1052   00A0
.EXEC.053:
        SUBR    R2,     R7                      ; 1053   0117
.EXEC.054:
        INCR    R0                              ; 1054   0008
.EXEC.055:
        SUBR    R3,     R0                      ; 1055   0118
.EXEC.056:
        SLR     R0,     1                       ; 1056   0060
.EXEC.057:
        SUBR    R3,     R1                      ; 1057   0119
.EXEC.058:
        INCR    R0                              ; 1058   0008
.EXEC.059:
        SUBR    R0,     R4                      ; 1059   0104
.EXEC.05A:
        INCR    R0                              ; 105A   0008
.EXEC.05B:
        SUBR    R0,     R2                      ; 105B   0102
.EXEC.05C:
        MOVR    R0,     R4                      ; 105C   0084
.EXEC.05D:
        HLT                                     ; 105D   0000
.EXEC.05E:
        MVI@    R5,     R0                      ; 105E   02A8
.EXEC.05F:
        MVO@    R0,     R1                      ; 105F   0248
.EXEC.060:
        MVI@    R5,     R1                      ; 1060   02A9
.EXEC.061:
        TSTR    R1                              ; 1061   0089
.EXEC.062:
        BNEQ    .EXEC.05E                       ; 1062   022C 0005

.EXEC.064:
        EIS                                     ; 1064   0002
.EXEC.065:
        CMP     G_0102, R0                      ; 1065   0340 0102
.EXEC.067:
        BEQ     .EXEC.065                       ; 1067   0224 0003

.EXEC.069:
        JSR     R5,     .EXEC.E38               ; 1069   0004 011C 0238
.EXEC.06C:
        JSRD    R5,     .EXEC.7B3               ; 106C   0004 0116 03B3
.EXEC.06F:
        JSR     R5,     .EXEC.7FE               ; 106F   0004 0114 03FE

.EXEC.072:
        MVII    #$0090, R0                      ; 1072   02B8 0090
.EXEC.074:
        MVO     R0,     G_0102                  ; 1074   0240 0102
.EXEC.076:
        SDBD                                    ; 1076   0001
.EXEC.077:
        MVII    #$1906, R0                      ; 1077   02B8 0006 0019
.EXEC.07A:
        MVO     R0,     G_035D                  ; 107A   0240 035D

.EXEC.07C:
        JSR     R5,     .EXEC.4F1               ; 107C   0004 0114 00F1
.EXEC.07F:
        JSR     R5,     .EXEC.41C               ; 107F   0004 0114 001C
.EXEC.082:
        JSR     R5,     X_READ_ROM_HDR          ; 1082   0004 0110 00AB

.EXEC.085:
        INCR    R6                              ; 1085   000E
.EXEC.086:
        MVO     R5,     G_0105                  ; 1086   0245 0105
.EXEC.088:
        SUBI    #$000B, R4                      ; 1088   033C 000B
.EXEC.08A:
        MOVR    R7,     R5                      ; 108A   00BD
.EXEC.08B:
        ADDI    #$0004, R5                      ; 108B   02FD 0004
.EXEC.08D:
        SDBD                                    ; 108D   0001
.EXEC.08E:
        MVI@    R4,     R7                      ; 108E   02A7
.EXEC.08F:
        EIS                                     ; 108F   0002
.EXEC.090:
        MVI     G_0102, R0                      ; 1090   0280 0102
.EXEC.092:
        DECR    R0                              ; 1092   0010
.EXEC.093:
        BPL     .EXEC.08F                       ; 1093   0223 0005

.EXEC.095:
        MVI     G_0103, R1                      ; 1095   0281 0103
.EXEC.097:
        MVO     R1,     G_0102                  ; 1097   0241 0102
.EXEC.099:
        NEGR    R0                              ; 1099   0020

.EXEC.09A:
        JSR     R5,     X_RAND1                 ; 109A   0004 0114 027D
.EXEC.09D:
        JSR     R5,     .EXEC.1FA               ; 109D   0004 0110 01FA
.EXEC.0A0:
        JSR     R5,     .EXEC.7D5               ; 10A0   0004 0114 03D5
.EXEC.0A3:
        JSR     R5,     .EXEC.4F1               ; 10A3   0004 0114 00F1
.EXEC.0A6:
        JSR     R5,     .EXEC.AAD               ; 10A6   0004 0118 02AD

.EXEC.0A9:
        B       .EXEC.08F                       ; 10A9   0220 001B

X_READ_ROM_HDR:
        MVI@    R5,     R4                      ; 10AB   02AC
.EXEC.0AC:
        PSHR    R5                              ; 10AC   0275
.EXEC.0AD:
        CMPI    #$000C, R4                      ; 10AD   037C 000C
.EXEC.0AF:
        BGE     .EXEC.0B8                       ; 10AF   020D 0007

.EXEC.0B1:
        ADD     G_02F0, R4                      ; 10B1   02C4 02F0
.EXEC.0B3:
        SUBI    #$0014, R4                      ; 10B3   033C 0014
.EXEC.0B5:
        SDBD                                    ; 10B5   0001
.EXEC.0B6:
        MVI@    R4,     R5                      ; 10B6   02A5
.EXEC.0B7:
        PULR    R7                              ; 10B7   02B7
.EXEC.0B8:
        ADD     G_02F0, R4                      ; 10B8   02C4 02F0
.EXEC.0BA:
        SUBI    #$0014, R4                      ; 10BA   033C 0014
.EXEC.0BC:
        MVI@    R4,     R5                      ; 10BC   02A5
.EXEC.0BD:
        PULR    R7                              ; 10BD   02B7
.EXEC.0BE:
        SARC    R1,     2                       ; 10BE   007D
.EXEC.0BF:
        BC      .EXEC.100                       ; 10BF   0201 003F
.EXEC.0C1:
        BOV     .EXEC.0D6                       ; 10C1   0202 0013

.EXEC.0C3:
        SARC    R1,     2                       ; 10C3   007D
.EXEC.0C4:
        BC      .EXEC.101                       ; 10C4   0201 003B
.EXEC.0C6:
        BOV     .EXEC.14E                       ; 10C6   0202 0086

.EXEC.0C8:
        SARC    R1,     2                       ; 10C8   007D
.EXEC.0C9:
        BC      .EXEC.107                       ; 10C9   0201 003C
.EXEC.0CB:
        BOV     .EXEC.11E                       ; 10CB   0202 0051

.EXEC.0CD:
        MVII    #$0080, R1                      ; 10CD   02B9 0080
.EXEC.0CF:
        MVO     R1,     .STIC.BORD              ; 10CF   0241 002C
.EXEC.0D1:
        INCR    R1                              ; 10D1   0009
.EXEC.0D2:
        MVO     R1,     G_0102                  ; 10D2   0241 0102
.EXEC.0D4:
        B       .EXEC.0FE                       ; 10D4   0200 0028

.EXEC.0D6:
        MVI     .STIC.MODE,R5                   ; 10D6   0285 0021
.EXEC.0D8:
        CLRR    R5                              ; 10D8   01ED
.EXEC.0D9:
        MVII    #$0030, R4                      ; 10D9   02BC 0030
.EXEC.0DB:
        MVO@    R5,     R4                      ; 10DB   0265
.EXEC.0DC:
        MVO@    R5,     R4                      ; 10DC   0265
.EXEC.0DD:
        MVO@    R5,     R4                      ; 10DD   0265
.EXEC.0DE:
        MVII    #$000B, R0                      ; 10DE   02B8 000B
.EXEC.0E0:
        MVO     R0,     .STIC.CS.0              ; 10E0   0240 0028
.EXEC.0E2:
        MVO     R0,     .STIC.BORD              ; 10E2   0240 002C
.EXEC.0E4:
        MVO@    R0,     R5                      ; 10E4   0268
.EXEC.0E5:
        CMPI    #$0008, R5                      ; 10E5   037D 0008
.EXEC.0E7:
        BNEQ    .EXEC.0E4                       ; 10E7   022C 0004

.EXEC.0E9:
        SDBD                                    ; 10E9   0001
.EXEC.0EA:
        MVII    #$36A8, R1                      ; 10EA   02B9 00A8 0036
.EXEC.0ED:
        MVII    #$0007, R3                      ; 10ED   02BB 0007
.EXEC.0EF:
        MVII    #$023D, R4                      ; 10EF   02BC 023D

.EXEC.0F1:
        JSRD    R5,     X_PRINT_R1              ; 10F1   0004 011A 0067

.EXEC.0F4:
        MOVR    R5,     R1                      ; 10F4   00A9
.EXEC.0F5:
        MVII    #$02C9, R4                      ; 10F5   02BC 02C9

.EXEC.0F7:
        JSR     R5,     X_PRINT_R1              ; 10F7   0004 0118 0067

.EXEC.0FA:
        MVII    #$0088, R0                      ; 10FA   02B8 0088
.EXEC.0FC:
        MVO     R0,     G_0102                  ; 10FC   0240 0102
.EXEC.0FE:
        MVO     R0,     .STIC.VIDEN             ; 10FE   0240 0020
.EXEC.100:
        PULR    R7                              ; 1100   02B7
.EXEC.101:
        MVO     R1,     G_0102                  ; 1101   0241 0102

.EXEC.103:
        JSRD    R5,     X_DO_GRAM_INIT          ; 1103   0004 011E 032F

.EXEC.106:
        PULR    R7                              ; 1106   02B7

.EXEC.107:
        JSR     R5,     X_READ_ROM_HDR          ; 1107   0004 0110 00AB

.EXEC.10A:
        INCR    R5                              ; 110A   000D
.EXEC.10B:
        MVO     R5,     .STIC.EDGE              ; 110B   0245 0032
.EXEC.10D:
        MVI@    R4,     R0                      ; 110D   02A0
.EXEC.10E:
        SARC    R0,     1                       ; 110E   0078
.EXEC.10F:
        MVI     .STIC.MODE,R0                   ; 110F   0280 0021
.EXEC.111:
        BNC     .EXEC.115                       ; 1111   0209 0002

.EXEC.113:
        MVO     R0,     .STIC.MODE              ; 1113   0240 0021
.EXEC.115:
        MVII    #$0028, R1                      ; 1115   02B9 0028
.EXEC.117:
        MVII    #$0005, R0                      ; 1117   02B8 0005

.EXEC.119:
        JSR     R5,     .EXEC.730               ; 1119   0004 0114 0330

.EXEC.11C:
        MVO     R1,     G_0106                  ; 111C   0241 0106
.EXEC.11E:
        MVI     G_0106, R1                      ; 111E   0281 0106
.EXEC.120:
        MVO     R1,     .STIC.BORD              ; 1120   0241 002C
.EXEC.122:
        MVII    #$0003, R0                      ; 1122   02B8 0003
.EXEC.124:
        B       .EXEC.0FC                       ; 1124   0220 0029

X_DEF_ISR:
        PSHR    R5                              ; 1126   0275
.EXEC.127:
        MVI     G_0102, R1                      ; 1127   0281 0102
.EXEC.129:
        SWAP    R1,     1                       ; 1129   0041
.EXEC.12A:
        SWAP    R1,     1                       ; 112A   0041
.EXEC.12B:
        BMI     .EXEC.0BE                       ; 112B   022B 006E

.EXEC.12D:
        DECR    R1                              ; 112D   0011
.EXEC.12E:
        BMI     .EXEC.14E                       ; 112E   020B 001E

.EXEC.130:
        MVO     R1,     G_0102                  ; 1130   0241 0102
.EXEC.132:
        CMPI    #$0003, R1                      ; 1132   0379 0003
.EXEC.134:
        BGE     .EXEC.14E                       ; 1134   020D 0018

.EXEC.136:
        JSR     R5,     .EXEC.154               ; 1136   0004 0110 0154

.EXEC.139:
        MVI     G_0114, R0                      ; 1139   0280 0114
.EXEC.13B:
        TSTR    R0                              ; 113B   0080
.EXEC.13C:
        BEQ     .EXEC.144                       ; 113C   0204 0006

.EXEC.13E:
        XOR     G_0102, R0                      ; 113E   03C0 0102
.EXEC.140:
        BNEQ    .EXEC.14E                       ; 1140   020C 000C

.EXEC.142:
        MVO     R0,     G_0114                  ; 1142   0240 0114
.EXEC.144:
        MVO     R0,     .STIC.VIDEN             ; 1144   0240 0020

.EXEC.146:
        JSR     R5,     .EXEC.1C0               ; 1146   0004 0110 01C0
.EXEC.149:
        JSR     R5,     .EXEC.414               ; 1149   0004 0114 0014

.EXEC.14C:
        B       .EXEC.150                       ; 114C   0200 0002

.EXEC.14E:
        MVO     R0,     .STIC.VIDEN             ; 114E   0240 0020
.EXEC.150:
        PULR    R5                              ; 1150   02B5
.EXEC.151:
        J       X_PLAY_NOTE                     ; 1151   0004 0318 02BD

.EXEC.154:
        PSHR    R5                              ; 1154   0275
.EXEC.155:
        SLL     R1,     1                       ; 1155   0049
.EXEC.156:
        ADDR    R1,     R7                      ; 1156   00CF
.EXEC.157:
        B       .EXEC.1AB                       ; 1157   0200 0052
.EXEC.159:
        B       .EXEC.161                       ; 1159   0200 0006

.EXEC.15B:
        CLRR    R5                              ; 115B   01ED
.EXEC.15C:
        MVII    #$031D, R4                      ; 115C   02BC 031D
.EXEC.15E:
        CLRR    R3                              ; 115E   01DB
.EXEC.15F:
        B       .EXEC.167                       ; 115F   0200 0006

.EXEC.161:
        MVII    #$0004, R5                      ; 1161   02BD 0004
.EXEC.163:
        MVII    #$033D, R4                      ; 1163   02BC 033D
.EXEC.165:
        MVII    #$0004, R3                      ; 1165   02BB 0004
.EXEC.167:
        MVI@    R4,     R0                      ; 1167   02A0
.EXEC.168:
        MOVR    R0,     R1                      ; 1168   0081
.EXEC.169:
        SLR     R1,     2                       ; 1169   0065
.EXEC.16A:
        SLR     R1,     2                       ; 116A   0065
.EXEC.16B:
        ANDI    #$0380, R1                      ; 116B   03B9 0380
.EXEC.16D:
        SLL     R1,     1                       ; 116D   0049
.EXEC.16E:
        MVI@    R4,     R2                      ; 116E   02A2
.EXEC.16F:
        TSTR    R2                              ; 116F   0092
.EXEC.170:
        MVI@    R4,     R2                      ; 1170   02A2
.EXEC.171:
        BEQ     .EXEC.177                       ; 1171   0204 0004

.EXEC.173:
        CMP     G_0104, R3                      ; 1173   0343 0104
.EXEC.175:
        BLT     .EXEC.17A                       ; 1175   0205 0003

.EXEC.177:
        MVII    #$00FF, R2                      ; 1177   02BA 00FF
.EXEC.179:
        INCR    R7                              ; 1179   000F
.EXEC.17A:
        SWAP    R2,     1                       ; 117A   0042
.EXEC.17B:
        ANDI    #$00FF, R2                      ; 117B   03BA 00FF
.EXEC.17D:
        XORR    R2,     R1                      ; 117D   01D1
.EXEC.17E:
        MVO@    R1,     R5                      ; 117E   0269
.EXEC.17F:
        MOVR    R0,     R1                      ; 117F   0081
.EXEC.180:
        SLR     R1,     1                       ; 1180   0061
.EXEC.181:
        ANDI    #$03E0, R1                      ; 1181   03B9 03E0
.EXEC.183:
        SLL     R1,     2                       ; 1183   004D
.EXEC.184:
        MVI@    R4,     R2                      ; 1184   02A2
.EXEC.185:
        SWAP    R2,     1                       ; 1185   0042
.EXEC.186:
        ANDI    #$007F, R2                      ; 1186   03BA 007F
.EXEC.188:
        XORR    R2,     R1                      ; 1188   01D1
.EXEC.189:
        ADDI    #$0007, R5                      ; 1189   02FD 0007
.EXEC.18B:
        MVO@    R1,     R5                      ; 118B   0269
.EXEC.18C:
        MOVR    R0,     R1                      ; 118C   0081
.EXEC.18D:
        ANDI    #$0007, R0                      ; 118D   03B8 0007
.EXEC.18F:
        ANDI    #$0030, R1                      ; 118F   03B9 0030
.EXEC.191:
        XORI    #$0008, R1                      ; 1191   03F9 0008
.EXEC.193:
        SWAP    R1,     1                       ; 1193   0041
.EXEC.194:
        XORR    R0,     R1                      ; 1194   01C1
.EXEC.195:
        MOVR    R3,     R2                      ; 1195   009A
.EXEC.196:
        ADD     G_02F0, R2                      ; 1196   02C2 02F0
.EXEC.198:
        XOR@    R2,     R1                      ; 1198   03D1
.EXEC.199:
        ADDI    #$0007, R5                      ; 1199   02FD 0007
.EXEC.19B:
        MVO@    R1,     R5                      ; 119B   0269
.EXEC.19C:
        ADDI    #$0007, R5                      ; 119C   02FD 0007
.EXEC.19E:
        CLRR    R0                              ; 119E   01C0
.EXEC.19F:
        MVO@    R0,     R5                      ; 119F   0268
.EXEC.1A0:
        ADDI    #$0004, R4                      ; 11A0   02FC 0004
.EXEC.1A2:
        SUBI    #$0018, R5                      ; 11A2   033D 0018
.EXEC.1A4:
        INCR    R3                              ; 11A4   000B
.EXEC.1A5:
        MOVR    R3,     R0                      ; 11A5   0098
.EXEC.1A6:
        ANDI    #$0003, R0                      ; 11A6   03B8 0003
.EXEC.1A8:
        BNEQ    .EXEC.167                       ; 11A8   022C 0042

.EXEC.1AA:
        PULR    R7                              ; 11AA   02B7
.EXEC.1AB:
        MVII    #$0018, R4                      ; 11AB   02BC 0018
.EXEC.1AD:
        MVII    #$0107, R5                      ; 11AD   02BD 0107
.EXEC.1AF:
        MVI@    R4,     R0                      ; 11AF   02A0
.EXEC.1B0:
        MVO@    R0,     R5                      ; 11B0   0268
.EXEC.1B1:
        SWAP    R0,     1                       ; 11B1   0040
.EXEC.1B2:
        RRC     R0,     1                       ; 11B2   0070
.EXEC.1B3:
        NOP                                     ; 11B3   0034
.EXEC.1B4:
        RRC     R2,     1                       ; 11B4   0072
.EXEC.1B5:
        RRC     R0,     1                       ; 11B5   0070
.EXEC.1B6:
        RRC     R3,     1                       ; 11B6   0073
.EXEC.1B7:
        CMPI    #$010F, R5                      ; 11B7   037D 010F
.EXEC.1B9:
        BNEQ    .EXEC.1AF                       ; 11B9   022C 000B

.EXEC.1BB:
        SWAP    R2,     1                       ; 11BB   0042
.EXEC.1BC:
        MVO@    R2,     R5                      ; 11BC   026A
.EXEC.1BD:
        SWAP    R3,     1                       ; 11BD   0043
.EXEC.1BE:
        MVO@    R3,     R5                      ; 11BE   026B
.EXEC.1BF:
        PULR    R7                              ; 11BF   02B7
.EXEC.1C0:
        PSHR    R5                              ; 11C0   0275
.EXEC.1C1:
        MVI     G_0112, R4                      ; 11C1   0284 0112
.EXEC.1C3:
        MVI     G_0111, R2                      ; 11C3   0282 0111
.EXEC.1C5:
        SARC    R2,     2                       ; 11C5   007E

.EXEC.1C6:
        JSR     R5,     .EXEC.1D1               ; 11C6   0004 0110 01D1

.EXEC.1C9:
        MVI     G_0113, R4                      ; 11C9   0284 0113
.EXEC.1CB:
        MVI     G_0111, R2                      ; 11CB   0282 0111
.EXEC.1CD:
        SLR     R2,     1                       ; 11CD   0062
.EXEC.1CE:
        SARC    R2,     1                       ; 11CE   007A
.EXEC.1CF:
        INCR    R2                              ; 11CF   000A
.EXEC.1D0:
        INCR    R7                              ; 11D0   000F
.EXEC.1D1:
        PSHR    R5                              ; 11D1   0275
.EXEC.1D2:
        DECR    R4                              ; 11D2   0014
.EXEC.1D3:
        BMI     .EXEC.100                       ; 11D3   022B 00D4

.EXEC.1D5:
        CLRR    R1                              ; 11D5   01C9
.EXEC.1D6:
        ADCR    R1                              ; 11D6   0029
.EXEC.1D7:
        ADDR    R4,     R4                      ; 11D7   00E4
.EXEC.1D8:
        ADDR    R4,     R4                      ; 11D8   00E4
.EXEC.1D9:
        ADDR    R4,     R4                      ; 11D9   00E4
.EXEC.1DA:
        MVI     G_02F0, R5                      ; 11DA   0285 02F0
.EXEC.1DC:
        ADDR    R5,     R2                      ; 11DC   00EA
.EXEC.1DD:
        SUBI    #$0014, R5                      ; 11DD   033D 0014
.EXEC.1DF:
        SDBD                                    ; 11DF   0001
.EXEC.1E0:
        ADD@    R5,     R4                      ; 11E0   02EC
.EXEC.1E1:
        MVI@    R2,     R5                      ; 11E1   0295
.EXEC.1E2:
        SDBD                                    ; 11E2   0001
.EXEC.1E3:
        ADDI    #$3800, R5                      ; 11E3   02FD 0000 0038
.EXEC.1E6:
        MVI@    R4,     R0                      ; 11E6   02A0
.EXEC.1E7:
        MVO@    R0,     R5                      ; 11E7   0268
.EXEC.1E8:
        MVI@    R4,     R0                      ; 11E8   02A0
.EXEC.1E9:
        MVO@    R0,     R5                      ; 11E9   0268
.EXEC.1EA:
        MVI@    R4,     R0                      ; 11EA   02A0
.EXEC.1EB:
        MVO@    R0,     R5                      ; 11EB   0268
.EXEC.1EC:
        MVI@    R4,     R0                      ; 11EC   02A0
.EXEC.1ED:
        MVO@    R0,     R5                      ; 11ED   0268
.EXEC.1EE:
        MVI@    R4,     R0                      ; 11EE   02A0
.EXEC.1EF:
        MVO@    R0,     R5                      ; 11EF   0268
.EXEC.1F0:
        MVI@    R4,     R0                      ; 11F0   02A0
.EXEC.1F1:
        MVO@    R0,     R5                      ; 11F1   0268
.EXEC.1F2:
        MVI@    R4,     R0                      ; 11F2   02A0
.EXEC.1F3:
        MVO@    R0,     R5                      ; 11F3   0268
.EXEC.1F4:
        MVI@    R4,     R0                      ; 11F4   02A0
.EXEC.1F5:
        MVO@    R0,     R5                      ; 11F5   0268
.EXEC.1F6:
        DECR    R1                              ; 11F6   0011
.EXEC.1F7:
        BEQ     .EXEC.1E6                       ; 11F7   0224 0012

.EXEC.1F9:
        PULR    R7                              ; 11F9   02B7
.EXEC.1FA:
        PSHR    R5                              ; 11FA   0275
.EXEC.1FB:
        CLRR    R0                              ; 11FB   01C0
.EXEC.1FC:
        MVII    #$031D, R1                      ; 11FC   02B9 031D
.EXEC.1FE:
        MVII    #$0001, R2                      ; 11FE   02BA 0001
.EXEC.200:
        B       .EXEC.221                       ; 1200   0200 001F

.EXEC.202:
        MVO     R0,     G_011B                  ; 1202   0240 011B
.EXEC.204:
        MVO     R1,     G_031B                  ; 1204   0241 031B
.EXEC.206:
        MVO     R2,     G_011C                  ; 1206   0242 011C

.EXEC.208:
        JSR     R5,     .EXEC.226               ; 1208   0004 0110 0226

.EXEC.20B:
        ADCR    R7                              ; 120B   002F
.EXEC.20C:
        DECR    R2                              ; 120C   0012

.EXEC.20D:
        JSR     R5,     .EXEC.226               ; 120D   0004 0110 0226

.EXEC.210:
        INCR    R3                              ; 1210   000B
.EXEC.211:
        DECR    R3                              ; 1211   0013

.EXEC.212:
        JSR     R5,     .EXEC.226               ; 1212   0004 0110 0226

.EXEC.215:
        ADDR    R7,     R1                      ; 1215   00F9
.EXEC.216:
        DECR    R3                              ; 1216   0013
.EXEC.217:
        MVI     G_011C, R2                      ; 1217   0282 011C
.EXEC.219:
        SLL     R2,     1                       ; 1219   004A
.EXEC.21A:
        MVI     G_031B, R1                      ; 121A   0281 031B
.EXEC.21C:
        ADDI    #$0008, R1                      ; 121C   02F9 0008
.EXEC.21E:
        MVI     G_011B, R0                      ; 121E   0280 011B
.EXEC.220:
        INCR    R0                              ; 1220   0008
.EXEC.221:
        CMP     G_0104, R0                      ; 1221   0340 0104
.EXEC.223:
        BLT     .EXEC.202                       ; 1223   0225 0022

.EXEC.225:
        PULR    R7                              ; 1225   02B7
.EXEC.226:
        MVI     G_031B, R1                      ; 1226   0281 031B
.EXEC.228:
        INCR    R1                              ; 1228   0009
.EXEC.229:
        MVI@    R1,     R4                      ; 1229   028C
.EXEC.22A:
        TSTR    R4                              ; 122A   00A4
.EXEC.22B:
        BEQ     .EXEC.217                       ; 122B   0224 0015

.EXEC.22D:
        SDBD                                    ; 122D   0001
.EXEC.22E:
        MVI@    R5,     R7                      ; 122E   02AF
.EXEC.22F:
        PSHR    R5                              ; 122F   0275
.EXEC.230:
        MVO     R4,     G_0319                  ; 1230   0244 0319
.EXEC.232:
        MVI@    R4,     R1                      ; 1232   02A1
.EXEC.233:
        ANDI    #$0300, R1                      ; 1233   03B9 0300
.EXEC.235:
        BNEQ    .EXEC.249                       ; 1235   020C 0012

.EXEC.237:
        MVI     G_011C, R0                      ; 1237   0280 011C
.EXEC.239:
        AND     G_0110, R0                      ; 1239   0380 0110
.EXEC.23B:
        BEQ     .EXEC.249                       ; 123B   0204 000C

.EXEC.23D:
        PSHR    R4                              ; 123D   0274
.EXEC.23E:
        DECR    R4                              ; 123E   0014
.EXEC.23F:
        SDBD                                    ; 123F   0001
.EXEC.240:
        XOR@    R4,     R1                      ; 1240   03E1
.EXEC.241:
        BEQ     .EXEC.248                       ; 1241   0204 0005

.EXEC.243:
        MVO     R1,     G_031C                  ; 1243   0241 031C

.EXEC.245:
        JSR     R5,     .EXEC.4A1               ; 1245   0004 0114 00A1

.EXEC.248:
        PULR    R4                              ; 1248   02B4
.EXEC.249:
        ADDI    #$0005, R4                      ; 1249   02FC 0005
.EXEC.24B:
        MVI@    R4,     R0                      ; 124B   02A0
.EXEC.24C:
        SARC    R0,     1                       ; 124C   0078
.EXEC.24D:
        BNC     .EXEC.261                       ; 124D   0209 0012

.EXEC.24F:
        SDBD                                    ; 124F   0001
.EXEC.250:
        MVI@    R4,     R2                      ; 1250   02A2
.EXEC.251:
        MVI     G_011C, R1                      ; 1251   0281 011C
.EXEC.253:
        AND     G_010F, R1                      ; 1253   0381 010F
.EXEC.255:
        BEQ     .EXEC.260                       ; 1255   0204 0009

.EXEC.257:
        MVO     R2,     G_031C                  ; 1257   0242 031C
.EXEC.259:
        PSHR    R0                              ; 1259   0270
.EXEC.25A:
        PSHR    R4                              ; 125A   0274

.EXEC.25B:
        JSR     R5,     .EXEC.4A1               ; 125B   0004 0114 00A1

.EXEC.25E:
        PULR    R4                              ; 125E   02B4
.EXEC.25F:
        PULR    R0                              ; 125F   02B0
.EXEC.260:
        TSTR    R0                              ; 1260   0080
.EXEC.261:
        BEQ     .EXEC.225                       ; 1261   0224 003D

.EXEC.263:
        MVI     G_011B, R1                      ; 1263   0281 011B
.EXEC.265:
        ADDI    #$0107, R1                      ; 1265   02F9 0107
.EXEC.267:
        MVI@    R1,     R1                      ; 1267   0289
.EXEC.268:
        ANDI    #$00FF, R1                      ; 1268   03B9 00FF
.EXEC.26A:
        BEQ     .EXEC.225                       ; 126A   0224 0046

.EXEC.26C:
        CLRR    R5                              ; 126C   01ED
.EXEC.26D:
        SARC    R1,     1                       ; 126D   0079
.EXEC.26E:
        BNC     .EXEC.292                       ; 126E   0209 0022

.EXEC.270:
        PSHR    R5                              ; 1270   0275
.EXEC.271:
        PSHR    R4                              ; 1271   0274
.EXEC.272:
        PSHR    R1                              ; 1272   0271
.EXEC.273:
        PSHR    R0                              ; 1273   0270
.EXEC.274:
        MVI@    R4,     R2                      ; 1274   02A2
.EXEC.275:
        SWAP    R2,     1                       ; 1275   0042
.EXEC.276:
        RRC     R2,     2                       ; 1276   0076
.EXEC.277:
        CLRR    R3                              ; 1277   01DB
.EXEC.278:
        RLC     R3,     2                       ; 1278   0057
.EXEC.279:
        MVI@    R4,     R1                      ; 1279   02A1
.EXEC.27A:
        SWAP    R1,     1                       ; 127A   0041
.EXEC.27B:
        RRC     R1,     1                       ; 127B   0071
.EXEC.27C:
        RLC     R3,     1                       ; 127C   0053
.EXEC.27D:
        CMPR    R5,     R3                      ; 127D   016B
.EXEC.27E:
        BNEQ    .EXEC.28B                       ; 127E   020C 000B

.EXEC.280:
        SLL     R1,     1                       ; 1280   0049
.EXEC.281:
        SLL     R2,     2                       ; 1281   004E
.EXEC.282:
        SWAP    R2,     1                       ; 1282   0042
.EXEC.283:
        XORR    R1,     R2                      ; 1283   01CA
.EXEC.284:
        MVO     R2,     G_031C                  ; 1284   0242 031C

.EXEC.286:
        JSR     R5,     .EXEC.29B               ; 1286   0004 0110 029B

.EXEC.289:
        B       .EXEC.28E                       ; 1289   0200 0003

.EXEC.28B:
        DECR    R0                              ; 128B   0010
.EXEC.28C:
        BNEQ    .EXEC.274                       ; 128C   022C 0019

.EXEC.28E:
        PULR    R0                              ; 128E   02B0
.EXEC.28F:
        PULR    R1                              ; 128F   02B1
.EXEC.290:
        PULR    R4                              ; 1290   02B4
.EXEC.291:
        PULR    R5                              ; 1291   02B5
.EXEC.292:
        INCR    R5                              ; 1292   000D
.EXEC.293:
        CMP     G_0104, R5                      ; 1293   0345 0104
.EXEC.295:
        BGE     .EXEC.225                       ; 1295   022D 0071

.EXEC.297:
        TSTR    R1                              ; 1297   0089
.EXEC.298:
        BNEQ    .EXEC.26D                       ; 1298   022C 002C

.EXEC.29A:
        PULR    R7                              ; 129A   02B7
.EXEC.29B:
        PSHR    R5                              ; 129B   0275
.EXEC.29C:
        MOVR    R3,     R0                      ; 129C   0098

.EXEC.29D:
        JSR     R5,     .EXEC.76C               ; 129D   0004 0114 036C

.EXEC.2A0:
        INCR    R1                              ; 12A0   0009
.EXEC.2A1:
        MVI@    R1,     R0                      ; 12A1   0288
.EXEC.2A2:
        TSTR    R0                              ; 12A2   0080
.EXEC.2A3:
        BEQ     .EXEC.225                       ; 12A3   0224 007F

.EXEC.2A5:
        MVI     G_031B, R1                      ; 12A5   0281 031B
.EXEC.2A7:
        INCR    R1                              ; 12A7   0009
.EXEC.2A8:
        MVI@    R1,     R2                      ; 12A8   028A
.EXEC.2A9:
        CMP     G_0319, R2                      ; 12A9   0342 0319
.EXEC.2AB:
        BEQ     .EXEC.4A0                       ; 12AB   0204 01F3

.EXEC.2AD:
        PULR    R7                              ; 12AD   02B7
.EXEC.2AE:
        PSHR    R5                              ; 12AE   0275

.EXEC.2AF:
        JSR     R5,     .EXEC.6F7               ; 12AF   0004 0114 02F7

.EXEC.2B2:
        BNC     .EXEC.225                       ; 12B2   0229 008E

.EXEC.2B4:
        MVII    #$0001, R0                      ; 12B4   02B8 0001
.EXEC.2B6:
        CMPR    R4,     R5                      ; 12B6   0165
.EXEC.2B7:
        BLE     .EXEC.2E5                       ; 12B7   0206 002C

.EXEC.2B9:
        SLL     R0,     1                       ; 12B9   0048
.EXEC.2BA:
        B       .EXEC.2E5                       ; 12BA   0200 0029

.EXEC.2BC:
        PSHR    R5                              ; 12BC   0275

.EXEC.2BD:
        JSR     R5,     .EXEC.70F               ; 12BD   0004 0114 030F

.EXEC.2C0:
        BNC     .EXEC.225                       ; 12C0   0229 009C

.EXEC.2C2:
        MVII    #$0001, R0                      ; 12C2   02B8 0001
.EXEC.2C4:
        CMPR    R4,     R5                      ; 12C4   0165
.EXEC.2C5:
        BLE     .EXEC.2CD                       ; 12C5   0206 0006

.EXEC.2C7:
        SLL     R0,     1                       ; 12C7   0048
.EXEC.2C8:
        B       .EXEC.2CD                       ; 12C8   0200 0003

.EXEC.2CA:
        PSHR    R5                              ; 12CA   0275
.EXEC.2CB:
        MVII    #$0003, R0                      ; 12CB   02B8 0003
.EXEC.2CD:
        PSHR    R0                              ; 12CD   0270
.EXEC.2CE:
        MOVR    R1,     R4                      ; 12CE   008C
.EXEC.2CF:
        MOVR    R3,     R0                      ; 12CF   0098

.EXEC.2D0:
        JSR     R5,     .EXEC.76C               ; 12D0   0004 0114 036C

.EXEC.2D3:
        ADDI    #$0003, R1                      ; 12D3   02F9 0003
.EXEC.2D5:
        MVI@    R1,     R0                      ; 12D5   0288
.EXEC.2D6:
        MVII    #$00FF, R2                      ; 12D6   02BA 00FF
.EXEC.2D8:
        SWAP    R0,     1                       ; 12D8   0040
.EXEC.2D9:
        ANDR    R2,     R0                      ; 12D9   0190
.EXEC.2DA:
        DECR    R1                              ; 12DA   0011
.EXEC.2DB:
        SWAP    R2,     1                       ; 12DB   0042
.EXEC.2DC:
        AND@    R1,     R2                      ; 12DC   038A
.EXEC.2DD:
        XORR    R0,     R2                      ; 12DD   01C2
.EXEC.2DE:
        MOVR    R4,     R1                      ; 12DE   00A1
.EXEC.2DF:
        PULR    R0                              ; 12DF   02B0
.EXEC.2E0:
        B       .EXEC.2E5                       ; 12E0   0200 0003

.EXEC.2E2:
        PSHR    R5                              ; 12E2   0275
.EXEC.2E3:
        MVII    #$0003, R0                      ; 12E3   02B8 0003
.EXEC.2E5:
        PSHR    R3                              ; 12E5   0273
.EXEC.2E6:
        MOVR    R1,     R4                      ; 12E6   008C
.EXEC.2E7:
        ADDI    #$0002, R4                      ; 12E7   02FC 0002
.EXEC.2E9:
        ADDI    #$0004, R1                      ; 12E9   02F9 0004
.EXEC.2EB:
        MVI@    R1,     R3                      ; 12EB   028B

.EXEC.2EC:
        JSR     R5,     .EXEC.2FB               ; 12EC   0004 0110 02FB

.EXEC.2EF:
        SWAP    R3,     1                       ; 12EF   0043
.EXEC.2F0:
        SWAP    R2,     1                       ; 12F0   0042

.EXEC.2F1:
        JSR     R5,     .EXEC.2FB               ; 12F1   0004 0110 02FB

.EXEC.2F4:
        SWAP    R3,     1                       ; 12F4   0043
.EXEC.2F5:
        SWAP    R2,     1                       ; 12F5   0042
.EXEC.2F6:
        MVO@    R3,     R1                      ; 12F6   024B
.EXEC.2F7:
        SUBI    #$0004, R1                      ; 12F7   0339 0004
.EXEC.2F9:
        PULR    R3                              ; 12F9   02B3
.EXEC.2FA:
        PULR    R7                              ; 12FA   02B7
.EXEC.2FB:
        CMP@    R4,     R2                      ; 12FB   0362
.EXEC.2FC:
        TSTR    R3                              ; 12FC   009B
.EXEC.2FD:
        BC      .EXEC.307                       ; 12FD   0201 0008
.EXEC.2FF:
        BPL     .EXEC.309                       ; 12FF   0203 0008

.EXEC.301:
        SARC    R0,     1                       ; 1301   0078
.EXEC.302:
        BNC     .EXEC.35C                       ; 1302   0209 0058

.EXEC.304:
        ANDI    #$00FF, R3                      ; 1304   03BB 00FF
.EXEC.306:
        MOVR    R5,     R7                      ; 1306   00AF
.EXEC.307:
        BPL     .EXEC.301                       ; 1307   0223 0007

.EXEC.309:
        SLR     R0,     1                       ; 1309   0060
.EXEC.30A:
        MOVR    R5,     R7                      ; 130A   00AF
.EXEC.30B:
        PSHR    R5                              ; 130B   0275
.EXEC.30C:
        MOVR    R1,     R5                      ; 130C   008D
.EXEC.30D:
        DECR    R5                              ; 130D   0015
.EXEC.30E:
        MVI@    R5,     R3                      ; 130E   02AB
.EXEC.30F:
        INCR    R5                              ; 130F   000D
.EXEC.310:
        MVI@    R5,     R1                      ; 1310   02A9
.EXEC.311:
        MVO     R1,     G_0319                  ; 1311   0241 0319
.EXEC.313:
        MVI     G_011C, R2                      ; 1313   0282 011C
.EXEC.315:
        AND     G_011A, R2                      ; 1315   0382 011A
.EXEC.317:
        MVI@    R5,     R2                      ; 1317   02AA
.EXEC.318:
        MVO     R2,     G_031A                  ; 1318   0242 031A
.EXEC.31A:
        MVI@    R5,     R0                      ; 131A   02A8
.EXEC.31B:
        BEQ     .EXEC.329                       ; 131B   0204 000C

.EXEC.31D:
        MOVR    R0,     R1                      ; 131D   0081
.EXEC.31E:
        MOVR    R0,     R2                      ; 131E   0082
.EXEC.31F:
        ANDI    #$00FF, R2                      ; 131F   03BA 00FF
.EXEC.321:
        XORR    R2,     R1                      ; 1321   01D1
.EXEC.322:
        SWAP    R2,     1                       ; 1322   0042
.EXEC.323:
        SUBI    #$000B, R5                      ; 1323   033D 000B
.EXEC.325:
        ADD@    R5,     R1                      ; 1325   02E9
.EXEC.326:
        ADD@    R5,     R2                      ; 1326   02EA
.EXEC.327:
        B       .EXEC.32F                       ; 1327   0200 0006

.EXEC.329:
        RLC     R3,     1                       ; 1329   0053
.EXEC.32A:
        BC      .EXEC.32F                       ; 132A   0201 0003

.EXEC.32C:
        JSR     R5,     .EXEC.477               ; 132C   0004 0114 0077

.EXEC.32F:
        MVI@    R4,     R3                      ; 132F   02A3
.EXEC.330:
        ANDI    #$0300, R3                      ; 1330   03BB 0300
.EXEC.332:
        SWAP    R3,     1                       ; 1332   0043
.EXEC.333:
        MOVR    R3,     R5                      ; 1333   009D
.EXEC.334:
        DECR    R4                              ; 1334   0014
.EXEC.335:
        SDBD                                    ; 1335   0001
.EXEC.336:
        MVI@    R4,     R3                      ; 1336   02A3
.EXEC.337:
        MVO     R3,     G_031C                  ; 1337   0243 031C
.EXEC.339:
        MVI     G_031B, R3                      ; 1339   0283 031B
.EXEC.33B:
        ADDI    #$0002, R3                      ; 133B   02FB 0002
.EXEC.33D:
        MOVR    R3,     R4                      ; 133D   009C
.EXEC.33E:
        CMP@    R3,     R1                      ; 133E   0359
.EXEC.33F:
        MVO@    R1,     R4                      ; 133F   0261
.EXEC.340:
        BNEQ    .EXEC.346                       ; 1340   020C 0004

.EXEC.342:
        CMP@    R4,     R2                      ; 1342   0362
.EXEC.343:
        BEQ     .EXEC.225                       ; 1343   0224 011F

.EXEC.345:
        DECR    R4                              ; 1345   0014
.EXEC.346:
        MVO@    R2,     R4                      ; 1346   0262
.EXEC.347:
        DECR    R5                              ; 1347   0015
.EXEC.348:
        BMI     .EXEC.225                       ; 1348   022B 0124
.EXEC.34A:
        BNEQ    .EXEC.35D                       ; 134A   020C 0011

.EXEC.34C:
        MOVR    R1,     R0                      ; 134C   0088
.EXEC.34D:
        XOR     G_0319, R0                      ; 134D   03C0 0319
.EXEC.34F:
        BPL     .EXEC.358                       ; 134F   0203 0007

.EXEC.351:
        MOVR    R1,     R0                      ; 1351   0088
.EXEC.352:
        RLC     R0,     1                       ; 1352   0050
.EXEC.353:
        BUSC    .EXEC.358                       ; 1353   0207 0003

.EXEC.355:
        JSR     R5,     .EXEC.3B1               ; 1355   0004 0110 03B1

.EXEC.358:
        TSTR    R2                              ; 1358   0092
.EXEC.359:
        PULR    R5                              ; 1359   02B5
.EXEC.35A:
        BMI     .EXEC.3BA                       ; 135A   020B 005E

.EXEC.35C:
        MOVR    R5,     R7                      ; 135C   00AF
.EXEC.35D:
        MVII    #$00FF, R4                      ; 135D   02BC 00FF
.EXEC.35F:
        SWAP    R1,     1                       ; 135F   0041
.EXEC.360:
        ANDR    R4,     R1                      ; 1360   01A1
.EXEC.361:
        SWAP    R2,     1                       ; 1361   0042
.EXEC.362:
        ANDR    R4,     R2                      ; 1362   01A2
.EXEC.363:
        DECR    R5                              ; 1363   0015
.EXEC.364:
        BEQ     .EXEC.397                       ; 1364   0204 0031

.EXEC.366:
        MVI     G_0319, R3                      ; 1366   0283 0319
.EXEC.368:
        SWAP    R3,     1                       ; 1368   0043
.EXEC.369:
        ANDR    R4,     R3                      ; 1369   01A3
.EXEC.36A:
        CMP     G_0116, R3                      ; 136A   0343 0116
.EXEC.36C:
        BGT     .EXEC.225                       ; 136C   022E 0148

.EXEC.36E:
        CMP     G_0117, R3                      ; 136E   0343 0117
.EXEC.370:
        BLT     .EXEC.225                       ; 1370   0225 014C

.EXEC.372:
        MVI     G_031A, R3                      ; 1372   0283 031A
.EXEC.374:
        SWAP    R3,     1                       ; 1374   0043
.EXEC.375:
        ANDR    R4,     R3                      ; 1375   01A3
.EXEC.376:
        CMP     G_0118, R3                      ; 1376   0343 0118
.EXEC.378:
        BGT     .EXEC.225                       ; 1378   022E 0154

.EXEC.37A:
        CMP     G_0119, R3                      ; 137A   0343 0119
.EXEC.37C:
        BLT     .EXEC.225                       ; 137C   0225 0158

.EXEC.37E:
        CLRR    R0                              ; 137E   01C0
.EXEC.37F:
        CMP     G_0116, R1                      ; 137F   0341 0116
.EXEC.381:
        BGT     .EXEC.388                       ; 1381   020E 0005

.EXEC.383:
        INCR    R0                              ; 1383   0008
.EXEC.384:
        CMP     G_0117, R1                      ; 1384   0341 0117
.EXEC.386:
        BGE     .EXEC.38B                       ; 1386   020D 0003

.EXEC.388:
        JSR     R5,     .EXEC.3C3               ; 1388   0004 0110 03C3

.EXEC.38B:
        MVII    #$0002, R0                      ; 138B   02B8 0002
.EXEC.38D:
        CMP     G_0118, R2                      ; 138D   0342 0118
.EXEC.38F:
        BGT     .EXEC.3C4                       ; 138F   020E 0033

.EXEC.391:
        INCR    R0                              ; 1391   0008
.EXEC.392:
        CMP     G_0119, R2                      ; 1392   0342 0119
.EXEC.394:
        BLT     .EXEC.3C4                       ; 1394   0205 002E

.EXEC.396:
        PULR    R7                              ; 1396   02B7
.EXEC.397:
        CMPI    #$00A7, R1                      ; 1397   0379 00A7
.EXEC.399:
        BLE     .EXEC.3A4                       ; 1399   0206 0009

.EXEC.39B:
        CLRR    R0                              ; 139B   01C0
.EXEC.39C:
        CMPI    #$00B3, R1                      ; 139C   0379 00B3
.EXEC.39E:
        BLT     .EXEC.3A1                       ; 139E   0205 0001

.EXEC.3A0:
        INCR    R0                              ; 13A0   0008

.EXEC.3A1:
        JSR     R5,     .EXEC.3C3               ; 13A1   0004 0110 03C3

.EXEC.3A4:
        CMPI    #$0067, R2                      ; 13A4   037A 0067
.EXEC.3A6:
        BLE     .EXEC.225                       ; 13A6   0226 0182

.EXEC.3A8:
        MVII    #$0002, R0                      ; 13A8   02B8 0002
.EXEC.3AA:
        CMPI    #$0073, R2                      ; 13AA   037A 0073
.EXEC.3AC:
        BLT     .EXEC.3C4                       ; 13AC   0205 0016

.EXEC.3AE:
        INCR    R0                              ; 13AE   0008
.EXEC.3AF:
        B       .EXEC.3C4                       ; 13AF   0200 0013

.EXEC.3B1:
        RLC     R1,     1                       ; 13B1   0051
.EXEC.3B2:
        GSWD    R0                              ; 13B2   0030
.EXEC.3B3:
        RRC     R1,     1                       ; 13B3   0071
.EXEC.3B4:
        RSWD    R0                              ; 13B4   0038
.EXEC.3B5:
        CLRR    R0                              ; 13B5   01C0
.EXEC.3B6:
        BNC     .EXEC.3C3                       ; 13B6   0209 000B
.EXEC.3B8:
        B       .EXEC.3C2                       ; 13B8   0200 0008

.EXEC.3BA:
        RLC     R2,     2                       ; 13BA   0056
.EXEC.3BB:
        GSWD    R0                              ; 13BB   0030
.EXEC.3BC:
        RRC     R2,     2                       ; 13BC   0076
.EXEC.3BD:
        RSWD    R0                              ; 13BD   0038
.EXEC.3BE:
        MVII    #$0002, R0                      ; 13BE   02B8 0002
.EXEC.3C0:
        BNOV    .EXEC.3C3                       ; 13C0   020A 0001

.EXEC.3C2:
        INCR    R0                              ; 13C2   0008
.EXEC.3C3:
        PSHR    R5                              ; 13C3   0275
.EXEC.3C4:
        MVII    #$0001, R5                      ; 13C4   02BD 0001
.EXEC.3C6:
        CMPR    R5,     R0                      ; 13C6   0168
.EXEC.3C7:
        BLE     .EXEC.3CA                       ; 13C7   0206 0001

.EXEC.3C9:
        ADDR    R5,     R5                      ; 13C9   00ED
.EXEC.3CA:
        PSHR    R1                              ; 13CA   0271
.EXEC.3CB:
        PSHR    R2                              ; 13CB   0272
.EXEC.3CC:
        MVI     G_031B, R1                      ; 13CC   0281 031B
.EXEC.3CE:
        INCR    R1                              ; 13CE   0009
.EXEC.3CF:
        ADDR    R5,     R1                      ; 13CF   00E9
.EXEC.3D0:
        ADDI    #$0318, R5                      ; 13D0   02FD 0318
.EXEC.3D2:
        MVI@    R5,     R2                      ; 13D2   02AA
.EXEC.3D3:
        MVI@    R1,     R3                      ; 13D3   028B
.EXEC.3D4:
        MVO@    R2,     R1                      ; 13D4   024A
.EXEC.3D5:
        MOVR    R0,     R2                      ; 13D5   0082

.EXEC.3D6:
        JSR     R5,     .EXEC.4A1               ; 13D6   0004 0114 00A1

.EXEC.3D9:
        PULR    R2                              ; 13D9   02B2
.EXEC.3DA:
        PULR    R1                              ; 13DA   02B1
.EXEC.3DB:
        PULR    R7                              ; 13DB   02B7
.EXEC.3DC:
        MVI     G_011C, R0                      ; 13DC   0280 011C
.EXEC.3DE:
        MVI     G_031B, R4                      ; 13DE   0284 031B
.EXEC.3E0:
        PSHR    R5                              ; 13E0   0275
.EXEC.3E1:
        ADDI    #$0002, R4                      ; 13E1   02FC 0002
.EXEC.3E3:
        MVI@    R4,     R3                      ; 13E3   02A3
.EXEC.3E4:
        MVI@    R4,     R5                      ; 13E4   02A5
.EXEC.3E5:
        MVI     G_011A, R1                      ; 13E5   0281 011A
.EXEC.3E7:
        ANDR    R0,     R1                      ; 13E7   0181
.EXEC.3E8:
        BEQ     .EXEC.225                       ; 13E8   0224 01C4

.EXEC.3EA:
        SLR     R0,     1                       ; 13EA   0060
.EXEC.3EB:
        MVI@    R4,     R1                      ; 13EB   02A1
.EXEC.3EC:
        MOVR    R1,     R2                      ; 13EC   008A
.EXEC.3ED:
        ANDI    #$00FF, R2                      ; 13ED   03BA 00FF
.EXEC.3EF:
        XORR    R2,     R1                      ; 13EF   01D1
.EXEC.3F0:
        SWAP    R2,     1                       ; 13F0   0042
.EXEC.3F1:
        SUBR    R1,     R3                      ; 13F1   010B
.EXEC.3F2:
        SUBR    R2,     R5                      ; 13F2   0115
.EXEC.3F3:
        SUBI    #$000B, R4                      ; 13F3   033C 000B
.EXEC.3F5:
        MVO@    R3,     R4                      ; 13F5   0263
.EXEC.3F6:
        MVO@    R5,     R4                      ; 13F6   0265
.EXEC.3F7:
        B       .EXEC.3E5                       ; 13F7   0220 0013

.EXEC.3F9:
        ADDI    #$0005, R1                      ; 13F9   02F9 0005
.EXEC.3FB:
        MVI@    R1,     R3                      ; 13FB   028B
.EXEC.3FC:
        SUBI    #$0001, R3                      ; 13FC   033B 0001
.EXEC.3FE:
        BLT     .EXEC.35C                       ; 13FE   0225 00A3

.EXEC.400:
        MVO@    R3,     R1                      ; 1400   024B
.EXEC.401:
        MVI     G_011B, R0                      ; 1401   0280 011B
.EXEC.403:
        BEQ     .EXEC.496                       ; 1403   0204 0091

.EXEC.405:
        ANDI    #$000F, R3                      ; 1405   03BB 000F
.EXEC.407:
        BNEQ    .EXEC.35C                       ; 1407   022C 00AC

.EXEC.409:
        MVII    #$013B, R2                      ; 1409   02BA 013B
.EXEC.40B:
        ADDR    R0,     R2                      ; 140B   00C2
.EXEC.40C:
        XOR@    R2,     R3                      ; 140C   03D3
.EXEC.40D:
        BEQ     .EXEC.35C                       ; 140D   0224 00B2

.EXEC.40F:
        INCR    R1                              ; 140F   0009
.EXEC.410:
        MVI@    R1,     R2                      ; 1410   028A
.EXEC.411:
        J       .EXEC.9B9                       ; 1411   0004 0318 01B9

.EXEC.414:
        MVI     G_0111, R0                      ; 1414   0280 0111
.EXEC.416:
        SLR     R0,     2                       ; 1416   0064
.EXEC.417:
        ADDI    #$0002, R0                      ; 1417   02F8 0002
.EXEC.419:
        CLRR    R1                              ; 1419   01C9
.EXEC.41A:
        B       .EXEC.423                       ; 141A   0200 0007

.EXEC.41C:
        MVII    #$0001, R1                      ; 141C   02B9 0001
.EXEC.41E:
        CMPI    #$0003, R0                      ; 141E   0378 0003
.EXEC.420:
        BGT     .EXEC.423                       ; 1420   020E 0001

.EXEC.422:
        SLL     R1,     1                       ; 1422   0049
.EXEC.423:
        PSHR    R5                              ; 1423   0275
.EXEC.424:
        PSHR    R1                              ; 1424   0271
.EXEC.425:
        ANDI    #$0006, R0                      ; 1425   03B8 0006

.EXEC.427:
        JSR     R5,     .EXEC.43F               ; 1427   0004 0114 003F

.EXEC.42A:
        PSHR    R3                              ; 142A   0273
.EXEC.42B:
        PSHR    R1                              ; 142B   0271
.EXEC.42C:
        INCR    R0                              ; 142C   0008

.EXEC.42D:
        JSR     R5,     .EXEC.43F               ; 142D   0004 0114 003F

.EXEC.430:
        DECR    R0                              ; 1430   0010
.EXEC.431:
        SARC    R1,     1                       ; 1431   0079
.EXEC.432:
        RLC     R0,     1                       ; 1432   0050
.EXEC.433:
        PULR    R1                              ; 1433   02B1
.EXEC.434:
        SARC    R1,     1                       ; 1434   0079
.EXEC.435:
        RLC     R0,     1                       ; 1435   0050
.EXEC.436:
        PULR    R2                              ; 1436   02B2
.EXEC.437:
        PULR    R1                              ; 1437   02B1
.EXEC.438:
        MVII    #$0111, R5                      ; 1438   02BD 0111
.EXEC.43A:
        MVO@    R0,     R5                      ; 143A   0268
.EXEC.43B:
        MVO@    R2,     R5                      ; 143B   026A
.EXEC.43C:
        MVO@    R3,     R5                      ; 143C   026B
.EXEC.43D:
        MVO@    R1,     R5                      ; 143D   0269
.EXEC.43E:
        PULR    R7                              ; 143E   02B7
.EXEC.43F:
        PSHR    R5                              ; 143F   0275
.EXEC.440:
        CLRR    R3                              ; 1440   01DB
.EXEC.441:
        CMP     G_0104, R0                      ; 1441   0340 0104
.EXEC.443:
        BGE     .EXEC.225                       ; 1443   022D 021F

.EXEC.445:
        JSR     R5,     .EXEC.76C               ; 1445   0004 0114 036C

.EXEC.448:
        MVI@    R1,     R4                      ; 1448   028C
.EXEC.449:
        INCR    R1                              ; 1449   0009
.EXEC.44A:
        MVI@    R1,     R2                      ; 144A   028A
.EXEC.44B:
        TSTR    R2                              ; 144B   0092
.EXEC.44C:
        BEQ     .EXEC.225                       ; 144C   0224 0228

.EXEC.44E:
        ADDI    #$0004, R1                      ; 144E   02F9 0004
.EXEC.450:
        ADDI    #$0004, R2                      ; 1450   02FA 0004
.EXEC.452:
        MVI@    R1,     R3                      ; 1452   028B
.EXEC.453:
        SAR     R3,     2                       ; 1453   006F
.EXEC.454:
        ANDI    #$00FC, R3                      ; 1454   03BB 00FC
.EXEC.456:
        CMPI    #$00FC, R3                      ; 1456   037B 00FC
.EXEC.458:
        BEQ     .EXEC.45F                       ; 1458   0204 0005

.EXEC.45A:
        SWAP    R3,     1                       ; 145A   0043
.EXEC.45B:
        ADD@    R1,     R3                      ; 145B   02CB
.EXEC.45C:
        BNC     .EXEC.468                       ; 145C   0209 000A

.EXEC.45E:
        INCR    R7                              ; 145E   000F
.EXEC.45F:
        MVI@    R1,     R3                      ; 145F   028B
.EXEC.460:
        INCR    R3                              ; 1460   000B
.EXEC.461:
        MOVR    R3,     R5                      ; 1461   009D
.EXEC.462:
        ANDI    #$000F, R5                      ; 1462   03BD 000F
.EXEC.464:
        CMP@    R2,     R5                      ; 1464   0355
.EXEC.465:
        BNEQ    .EXEC.468                       ; 1465   020C 0001

.EXEC.467:
        XORR    R5,     R3                      ; 1467   01EB
.EXEC.468:
        MVO@    R3,     R1                      ; 1468   024B
.EXEC.469:
        ANDI    #$000F, R3                      ; 1469   03BB 000F
.EXEC.46B:
        CLRC                                    ; 146B   0006
.EXEC.46C:
        ANDI    #$0040, R4                      ; 146C   03BC 0040
.EXEC.46E:
        BEQ     .EXEC.472                       ; 146E   0204 0002

.EXEC.470:
        SLL     R3,     1                       ; 1470   004B
.EXEC.471:
        SETC                                    ; 1471   0007
.EXEC.472:
        RLC     R1,     1                       ; 1472   0051
.EXEC.473:
        INCR    R2                              ; 1473   000A
.EXEC.474:
        ADD@    R2,     R3                      ; 1474   02D3
.EXEC.475:
        INCR    R3                              ; 1475   000B
.EXEC.476:
        PULR    R7                              ; 1476   02B7
.EXEC.477:
        PSHR    R2                              ; 1477   0272
.EXEC.478:
        MOVR    R0,     R2                      ; 1478   0082
.EXEC.479:
        BEQ     .EXEC.494                       ; 1479   0204 0019

.EXEC.47B:
        ANDI    #$00FF, R2                      ; 147B   03BA 00FF
.EXEC.47D:
        XORR    R2,     R0                      ; 147D   01D0
.EXEC.47E:
        SWAP    R2,     1                       ; 147E   0042
.EXEC.47F:
        ADD     G_0115, R7                      ; 147F   02C7 0115
.EXEC.481:
        SAR     R0,     2                       ; 1481   006C
.EXEC.482:
        SAR     R2,     2                       ; 1482   006E
.EXEC.483:
        SAR     R0,     2                       ; 1483   006C
.EXEC.484:
        SAR     R2,     2                       ; 1484   006E
.EXEC.485:
        SAR     R0,     2                       ; 1485   006C
.EXEC.486:
        ADDR    R0,     R1                      ; 1486   00C1
.EXEC.487:
        SAR     R2,     2                       ; 1487   006E
.EXEC.488:
        ADD@    R6,     R2                      ; 1488   02F2
.EXEC.489:
        MOVR    R5,     R7                      ; 1489   00AF
.EXEC.48A:
        SAR     R0,     2                       ; 148A   006C
.EXEC.48B:
        SAR     R2,     2                       ; 148B   006E
.EXEC.48C:
        NOP                                     ; 148C   0034
.EXEC.48D:
        SAR     R0,     2                       ; 148D   006C
.EXEC.48E:
        SAR     R2,     2                       ; 148E   006E
.EXEC.48F:
        SAR     R0,     2                       ; 148F   006C
.EXEC.490:
        SAR     R2,     2                       ; 1490   006E
.EXEC.491:
        SAR     R0,     1                       ; 1491   0068
.EXEC.492:
        ADDR    R0,     R1                      ; 1492   00C1
.EXEC.493:
        SAR     R2,     1                       ; 1493   006A
.EXEC.494:
        ADD@    R6,     R2                      ; 1494   02F2
.EXEC.495:
        MOVR    R5,     R7                      ; 1495   00AF
.EXEC.496:
        PSHR    R5                              ; 1496   0275
.EXEC.497:
        ADDI    #$0002, R4                      ; 1497   02FC 0002
.EXEC.499:
        SDBD                                    ; 1499   0001
.EXEC.49A:
        MVI@    R4,     R1                      ; 149A   02A1
.EXEC.49B:
        MVO     R1,     G_031C                  ; 149B   0241 031C

.EXEC.49D:
        JSR     R5,     .EXEC.98D               ; 149D   0004 0118 018D

.EXEC.4A0:
        PULR    R5                              ; 14A0   02B5
.EXEC.4A1:
        MVI     G_031B, R1                      ; 14A1   0281 031B
.EXEC.4A3:
        INCR    R1                              ; 14A3   0009
.EXEC.4A4:
        MVI@    R1,     R4                      ; 14A4   028C
.EXEC.4A5:
        DECR    R1                              ; 14A5   0011
.EXEC.4A6:
        TSTR    R4                              ; 14A6   00A4
.EXEC.4A7:
        BEQ     .EXEC.35C                       ; 14A7   0224 014C

.EXEC.4A9:
        MVI     G_031C, R4                      ; 14A9   0284 031C
.EXEC.4AB:
        TSTR    R4                              ; 14AB   00A4
.EXEC.4AC:
        BEQ     .EXEC.35C                       ; 14AC   0224 0151

.EXEC.4AE:
        MVI     G_011B, R0                      ; 14AE   0280 011B
.EXEC.4B0:
        MOVR    R4,     R7                      ; 14B0   00A7
.EXEC.4B1:
        PSHR    R4                              ; 14B1   0274
.EXEC.4B2:
        MVII    #$0019, R4                      ; 14B2   02BC 0019
.EXEC.4B4:
        MVO     R4,     G_011E                  ; 14B4   0244 011E
.EXEC.4B6:
        PULR    R7                              ; 14B6   02B7
.EXEC.4B7:
        MVII    #$00FF, R1                      ; 14B7   02B9 00FF
.EXEC.4B9:
        MVI@    R2,     R0                      ; 14B9   0290
.EXEC.4BA:
        SWAP    R0,     1                       ; 14BA   0040
.EXEC.4BB:
        XOR@    R3,     R0                      ; 14BB   03D8
.EXEC.4BC:
        COMR    R0                              ; 14BC   0018
.EXEC.4BD:
        BNEQ    .EXEC.4B7                       ; 14BD   022C 0007

.EXEC.4BF:
        DECR    R1                              ; 14BF   0011
.EXEC.4C0:
        BNEQ    .EXEC.4B9                       ; 14C0   022C 0008

.EXEC.4C2:
        MOVR    R5,     R7                      ; 14C2   00AF
.EXEC.4C3:
        PSHR    R5                              ; 14C3   0275
.EXEC.4C4:
        PSHR    R0                              ; 14C4   0270
.EXEC.4C5:
        PSHR    R1                              ; 14C5   0271
.EXEC.4C6:
        MVII    #$01FE, R2                      ; 14C6   02BA 01FE
.EXEC.4C8:
        MVII    #$01FF, R3                      ; 14C8   02BB 01FF

.EXEC.4CA:
        JSR     R5,     .EXEC.4B7               ; 14CA   0004 0114 00B7

.EXEC.4CD:
        INCR    R0                              ; 14CD   0008

.EXEC.4CE:
        JSR     R5,     X_RAND1                 ; 14CE   0004 0114 027D

.EXEC.4D1:
        MVI@    R2,     R0                      ; 14D1   0290
.EXEC.4D2:
        SWAP    R0,     1                       ; 14D2   0040
.EXEC.4D3:
        XOR@    R3,     R0                      ; 14D3   03D8
.EXEC.4D4:
        COMR    R0                              ; 14D4   0018
.EXEC.4D5:
        BEQ     .EXEC.4CD                       ; 14D5   0224 0009

.EXEC.4D7:
        MVII    #$01FF, R0                      ; 14D7   02B8 01FF
.EXEC.4D9:
        DECR    R0                              ; 14D9   0010
.EXEC.4DA:
        BNEQ    .EXEC.4D9                       ; 14DA   022C 0002

.EXEC.4DC:
        MVI@    R2,     R0                      ; 14DC   0290
.EXEC.4DD:
        SWAP    R0,     1                       ; 14DD   0040
.EXEC.4DE:
        XOR@    R3,     R0                      ; 14DE   03D8
.EXEC.4DF:
        COMR    R0                              ; 14DF   0018
.EXEC.4E0:
        PSHR    R0                              ; 14E0   0270

.EXEC.4E1:
        JSR     R5,     .EXEC.4B7               ; 14E1   0004 0114 00B7

.EXEC.4E4:
        PULR    R5                              ; 14E4   02B5
.EXEC.4E5:
        PULR    R1                              ; 14E5   02B1
.EXEC.4E6:
        PULR    R0                              ; 14E6   02B0
.EXEC.4E7:
        B       .EXEC.4B2                       ; 14E7   0220 0036

.EXEC.4E9:
        DECLE   $0001                           ; 14E9   0001
.EXEC.4EA:
        XORI    #$03FE, R7                      ; 14EA   03FF 03FE
.EXEC.4EC:
        CLRC                                    ; 14EC   0006
.EXEC.4ED:
        XORI    #$0004, R5                      ; 14ED   03FD 0004
.EXEC.4EF:
        INCR    R0                              ; 14EF   0008
.EXEC.4F0:
        HLT                                     ; 14F0   0000
.EXEC.4F1:
        PSHR    R5                              ; 14F1   0275
.EXEC.4F2:
        MVII    #$005A, R1                      ; 14F2   02B9 005A
.EXEC.4F4:
        CMP     .PSG0.rgt_hand,R1               ; 14F4   0341 01FE
.EXEC.4F6:
        BEQ     .EXEC.507                       ; 14F6   0204 000F

.EXEC.4F8:
        CMP     .PSG0.lft_hand,R1               ; 14F8   0341 01FF
.EXEC.4FA:
        BEQ     .EXEC.507                       ; 14FA   0204 000B

.EXEC.4FC:
        MVII    #$011D, R4                      ; 14FC   02BC 011D
.EXEC.4FE:
        MOVR    R4,     R5                      ; 14FE   00A5
.EXEC.4FF:
        SDBD                                    ; 14FF   0001
.EXEC.500:
        MVI@    R4,     R0                      ; 1500   02A0
.EXEC.501:
        DECR    R0                              ; 1501   0010
.EXEC.502:
        MVO@    R0,     R5                      ; 1502   0268
.EXEC.503:
        SWAP    R0,     1                       ; 1503   0040
.EXEC.504:
        MVO@    R0,     R5                      ; 1504   0268
.EXEC.505:
        BNEQ    .EXEC.523                       ; 1505   020C 001C

.EXEC.507:
        MVII    #$0080, R0                      ; 1507   02B8 0080
.EXEC.509:
        MVO     R0,     G_0102                  ; 1509   0240 0102
.EXEC.50B:
        MVII    #$01FB, R4                      ; 150B   02BC 01FB
.EXEC.50D:
        MOVR    R4,     R5                      ; 150D   00A5
.EXEC.50E:
        CLRR    R3                              ; 150E   01DB
.EXEC.50F:
        MVI@    R4,     R0                      ; 150F   02A0
.EXEC.510:
        MVO@    R3,     R5                      ; 1510   026B
.EXEC.511:
        MVI@    R4,     R1                      ; 1511   02A1
.EXEC.512:
        MVO@    R3,     R5                      ; 1512   026B
.EXEC.513:
        MVI@    R4,     R2                      ; 1513   02A2
.EXEC.514:
        MVO@    R3,     R5                      ; 1514   026B
.EXEC.515:
        PSHR    R2                              ; 1515   0272

.EXEC.516:
        JSR     R5,     .EXEC.4C3               ; 1516   0004 0114 00C3

.EXEC.519:
        PULR    R2                              ; 1519   02B2
.EXEC.51A:
        MVII    #$01FB, R5                      ; 151A   02BD 01FB
.EXEC.51C:
        MVO@    R0,     R5                      ; 151C   0268
.EXEC.51D:
        MVO@    R1,     R5                      ; 151D   0269
.EXEC.51E:
        MVO@    R2,     R5                      ; 151E   026A
.EXEC.51F:
        MVII    #$00A0, R0                      ; 151F   02B8 00A0
.EXEC.521:
        MVO     R0,     G_0102                  ; 1521   0240 0102
.EXEC.523:
        MVII    #$011F, R1                      ; 1523   02B9 011F
.EXEC.525:
        MVI     .PSG0.lft_hand,R2               ; 1525   0282 01FF

.EXEC.527:
        JSR     R5,     .EXEC.52F               ; 1527   0004 0114 012F

.EXEC.52A:
        MVII    #$0120, R1                      ; 152A   02B9 0120
.EXEC.52C:
        MVI     .PSG0.rgt_hand,R2               ; 152C   0282 01FE
.EXEC.52E:
        INCR    R7                              ; 152E   000F
.EXEC.52F:
        PSHR    R5                              ; 152F   0275
.EXEC.530:
        XORI    #$00FF, R2                      ; 1530   03FA 00FF
.EXEC.532:
        CLRR    R0                              ; 1532   01C0
.EXEC.533:
        MOVR    R1,     R3                      ; 1533   008B
.EXEC.534:
        ADDI    #$0004, R3                      ; 1534   02FB 0004
.EXEC.536:
        CMP@    R3,     R2                      ; 1536   035A
.EXEC.537:
        MVO@    R2,     R3                      ; 1537   025A
.EXEC.538:
        BNEQ    .EXEC.54B                       ; 1538   020C 0011

.EXEC.53A:
        MOVR    R2,     R3                      ; 153A   0093
.EXEC.53B:
        ANDI    #$001F, R3                      ; 153B   03BB 001F
.EXEC.53D:
        SLR     R2,     2                       ; 153D   0066
.EXEC.53E:
        SLR     R2,     2                       ; 153E   0066
.EXEC.53F:
        SLR     R2,     1                       ; 153F   0062
.EXEC.540:
        ADDR    R7,     R2                      ; 1540   00FA
.EXEC.541:
        SUBI    #$0058, R2                      ; 1541   033A 0058
.EXEC.543:
        MVI@    R2,     R0                      ; 1543   0290

.EXEC.544:
        JSR     R5,     X_EXT_SIGN_LO           ; 1544   0004 0114 0268

.EXEC.547:
        CMPI    #$0001, R0                      ; 1547   0378 0001
.EXEC.549:
        BGT     .EXEC.568                       ; 1549   020E 001D

.EXEC.54B:
        MOVR    R1,     R2                      ; 154B   008A
.EXEC.54C:
        ADDI    #$0002, R2                      ; 154C   02FA 0002
.EXEC.54E:
        MVI@    R2,     R4                      ; 154E   0294
.EXEC.54F:
        TSTR    R4                              ; 154F   00A4
.EXEC.550:
        BEQ     .EXEC.561                       ; 1550   0204 000F

.EXEC.552:
        PSHR    R0                              ; 1552   0270
.EXEC.553:
        PSHR    R1                              ; 1553   0271
.EXEC.554:
        PSHR    R3                              ; 1554   0273
.EXEC.555:
        CLRR    R0                              ; 1555   01C0
.EXEC.556:
        MVO@    R0,     R2                      ; 1556   0250
.EXEC.557:
        DECR    R0                              ; 1557   0010
.EXEC.558:
        ADDR    R4,     R4                      ; 1558   00E4
.EXEC.559:
        ADDI    #$0002, R4                      ; 1559   02FC 0002

.EXEC.55B:
        JSR     R5,     .EXEC.5EB               ; 155B   0004 0114 01EB

.EXEC.55E:
        PULR    R3                              ; 155E   02B3
.EXEC.55F:
        PULR    R1                              ; 155F   02B1
.EXEC.560:
        PULR    R0                              ; 1560   02B0
.EXEC.561:
        MOVR    R0,     R4                      ; 1561   0084
.EXEC.562:
        BEQ     .EXEC.5AC                       ; 1562   0204 0048
.EXEC.564:
        BMI     .EXEC.5BB                       ; 1564   020B 0055
.EXEC.566:
        B       .EXEC.590                       ; 1566   0200 0028

.EXEC.568:
        PSHR    R3                              ; 1568   0273
.EXEC.569:
        PSHR    R1                              ; 1569   0271
.EXEC.56A:
        MOVR    R0,     R4                      ; 156A   0084
.EXEC.56B:
        SUBI    #$0002, R0                      ; 156B   0338 0002
.EXEC.56D:
        SLR     R0,     1                       ; 156D   0060
.EXEC.56E:
        ADDI    #$0002, R1                      ; 156E   02F9 0002
.EXEC.570:
        ADD     G_035D, R4                      ; 1570   02C4 035D
.EXEC.572:
        CMP@    R1,     R0                      ; 1572   0348
.EXEC.573:
        MVO@    R0,     R1                      ; 1573   0248
.EXEC.574:
        SDBD                                    ; 1574   0001
.EXEC.575:
        MVI@    R4,     R2                      ; 1575   02A2
.EXEC.576:
        BEQ     .EXEC.588                       ; 1576   0204 0010

.EXEC.578:
        JSR     R5,     X_READ_ROM_HDR          ; 1578   0004 0110 00AB

.EXEC.57B:
        INCR    R4                              ; 157B   000C
.EXEC.57C:
        MOVR    R5,     R3                      ; 157C   00AB
.EXEC.57D:
        SLR     R3,     2                       ; 157D   0067
.EXEC.57E:
        SARC    R3,     1                       ; 157E   007B
.EXEC.57F:
        DECR    R0                              ; 157F   0010
.EXEC.580:
        BNEQ    .EXEC.57E                       ; 1580   022C 0003

.EXEC.582:
        JSR     R5,     .EXEC.605               ; 1582   0004 0114 0205

.EXEC.585:
        MVII    #$0001, R0                      ; 1585   02B8 0001
.EXEC.587:
        INCR    R7                              ; 1587   000F
.EXEC.588:
        CLRR    R0                              ; 1588   01C0
.EXEC.589:
        PULR    R1                              ; 1589   02B1
.EXEC.58A:
        PSHR    R1                              ; 158A   0271

.EXEC.58B:
        JSR     R5,     .EXEC.5EF               ; 158B   0004 0114 01EF

.EXEC.58E:
        PULR    R1                              ; 158E   02B1
.EXEC.58F:
        PULR    R3                              ; 158F   02B3
.EXEC.590:
        MVII    #$000F, R0                      ; 1590   02B8 000F
.EXEC.592:
        CLRR    R4                              ; 1592   01E4

.EXEC.593:
        JSR     R5,     .EXEC.5A6               ; 1593   0004 0114 01A6

.EXEC.596:
        DECR    R2                              ; 1596   0012
.EXEC.597:
        DECR    R3                              ; 1597   0013
.EXEC.598:
        DIS                                     ; 1598   0003
.EXEC.599:
        DECLE   $0001                           ; 1599   0001
.EXEC.59A:
        DECR    R1                              ; 159A   0011
.EXEC.59B:
        COMR    R1                              ; 159B   0019
.EXEC.59C:
        INCR    R1                              ; 159C   0009
.EXEC.59D:
        INCR    R0                              ; 159D   0008
.EXEC.59E:
        COMR    R0                              ; 159E   0018
.EXEC.59F:
        COMR    R4                              ; 159F   001C
.EXEC.5A0:
        INCR    R4                              ; 15A0   000C

.EXEC.5A1:
        JSR     R4,     .EXEC.416               ; 15A1   0004 0014 0016

.EXEC.5A4:
        CLRC                                    ; 15A4   0006
.EXEC.5A5:
        EIS                                     ; 15A5   0002
.EXEC.5A6:
        CMP@    R5,     R3                      ; 15A6   036B
.EXEC.5A7:
        BEQ     .EXEC.5DC                       ; 15A7   0204 0033

.EXEC.5A9:
        DECR    R0                              ; 15A9   0010
.EXEC.5AA:
        BPL     .EXEC.5A6                       ; 15AA   0223 0005

.EXEC.5AC:
        MVI@    R1,     R0                      ; 15AC   0288
.EXEC.5AD:
        MOVR    R0,     R2                      ; 15AD   0082
.EXEC.5AE:
        ANDI    #$00BF, R2                      ; 15AE   03BA 00BF
.EXEC.5B0:
        XORI    #$0040, R2                      ; 15B0   03FA 0040
.EXEC.5B2:
        MVO@    R2,     R1                      ; 15B2   024A
.EXEC.5B3:
        ANDI    #$00C0, R0                      ; 15B3   03B8 00C0
.EXEC.5B5:
        BNEQ    .EXEC.4B6                       ; 15B5   022C 0100

.EXEC.5B7:
        DECR    R0                              ; 15B7   0010
.EXEC.5B8:
        CLRR    R4                              ; 15B8   01E4
.EXEC.5B9:
        B       .EXEC.5EA                       ; 15B9   0200 002F

.EXEC.5BB:
        INCR    R4                              ; 15BB   000C
.EXEC.5BC:
        MOVR    R3,     R5                      ; 15BC   009D
.EXEC.5BD:
        ANDI    #$000F, R3                      ; 15BD   03BB 000F
.EXEC.5BF:
        BEQ     .EXEC.5AC                       ; 15BF   0224 0014

.EXEC.5C1:
        XORR    R3,     R5                      ; 15C1   01DD
.EXEC.5C2:
        BNEQ    .EXEC.5AC                       ; 15C2   022C 0017

.EXEC.5C4:
        ADDI    #$0003, R4                      ; 15C4   02FC 0003
.EXEC.5C6:
        SARC    R3,     1                       ; 15C6   007B
.EXEC.5C7:
        BNC     .EXEC.5C4                       ; 15C7   0229 0004
.EXEC.5C9:
        BNEQ    .EXEC.5AC                       ; 15C9   022C 001E

.EXEC.5CB:
        MOVR    R4,     R0                      ; 15CB   00A0
.EXEC.5CC:
        CMPI    #$000B, R0                      ; 15CC   0378 000B
.EXEC.5CE:
        BEQ     .EXEC.5D4                       ; 15CE   0204 0004
.EXEC.5D0:
        BMI     .EXEC.5D6                       ; 15D0   020B 0004

.EXEC.5D2:
        ADDI    #$000A, R0                      ; 15D2   02F8 000A
.EXEC.5D4:
        SUBI    #$000B, R0                      ; 15D4   0338 000B
.EXEC.5D6:
        ANDI    #$007F, R0                      ; 15D6   03B8 007F
.EXEC.5D8:
        XORI    #$0080, R0                      ; 15D8   03F8 0080
.EXEC.5DA:
        MVII    #$0002, R4                      ; 15DA   02BC 0002
.EXEC.5DC:
        CMP@    R1,     R0                      ; 15DC   0348
.EXEC.5DD:
        BEQ     .EXEC.4B6                       ; 15DD   0224 0128

.EXEC.5DF:
        MVO@    R0,     R1                      ; 15DF   0248
.EXEC.5E0:
        PSHR    R1                              ; 15E0   0271
.EXEC.5E1:
        PSHR    R4                              ; 15E1   0274

.EXEC.5E2:
        JSR     R5,     .EXEC.5F9               ; 15E2   0004 0114 01F9

.EXEC.5E5:
        PULR    R4                              ; 15E5   02B4
.EXEC.5E6:
        PULR    R1                              ; 15E6   02B1
.EXEC.5E7:
        MVI@    R1,     R0                      ; 15E7   0288
.EXEC.5E8:
        ANDI    #$007F, R0                      ; 15E8   03B8 007F
.EXEC.5EA:
        PULR    R5                              ; 15EA   02B5
.EXEC.5EB:
        ADD     G_035D, R4                      ; 15EB   02C4 035D
.EXEC.5ED:
        SDBD                                    ; 15ED   0001
.EXEC.5EE:
        MVI@    R4,     R2                      ; 15EE   02A2

.EXEC.5EF:
        JSR     R4,     .EXEC.4B1               ; 15EF   0004 0014 00B1

.EXEC.5F2:
        TSTR    R2                              ; 15F2   0092
.EXEC.5F3:
        BNEQ    .EXEC.5F6                       ; 15F3   020C 0001

.EXEC.5F5:
        MOVR    R5,     R7                      ; 15F5   00AF
.EXEC.5F6:
        SUBI    #$011F, R1                      ; 15F6   0339 011F
.EXEC.5F8:
        MOVR    R2,     R7                      ; 15F8   0097
.EXEC.5F9:
        PSHR    R5                              ; 15F9   0275

.EXEC.5FA:
        JSR     R5,     X_READ_ROM_HDR          ; 15FA   0004 0110 00AB

.EXEC.5FD:
        INCR    R4                              ; 15FD   000C
.EXEC.5FE:
        MOVR    R5,     R1                      ; 15FE   00A9
.EXEC.5FF:
        PULR    R5                              ; 15FF   02B5
.EXEC.600:
        SARC    R1,     1                       ; 1600   0079
.EXEC.601:
        SWAP    R0,     2                       ; 1601   0044
.EXEC.602:
        BPL     .EXEC.605                       ; 1602   0203 0001

.EXEC.604:
        SARC    R1,     1                       ; 1604   0079
.EXEC.605:
        BNC     .EXEC.5F5                       ; 1605   0229 0011

.EXEC.607:
        JSR     R4,     X_SFX_OK                ; 1607   0004 001C 02AD

.EXEC.60A:
        PSHR    R5                              ; 160A   0275

.EXEC.60B:
        JSR     R5,     X_PLAY_SFX1             ; 160B   0004 0118 03BB

.EXEC.60E:
        XOR@    R5,     R1                      ; 160E   03E9
.EXEC.60F:
        DECLE   $0005                           ; 160F   0005
.EXEC.610:
        INCR    R4                              ; 1610   000C
.EXEC.611:
        TSTR    R0                              ; 1611   0080
.EXEC.612:
        ADCR    R3                              ; 1612   002B
.EXEC.613:
        SWAP    R0,     1                       ; 1613   0040
.EXEC.614:
        COMR    R0                              ; 1614   0018
.EXEC.615:
        INCR    R3                              ; 1615   000B
.EXEC.616:
        SUBR    R5,     R3                      ; 1616   012B
.EXEC.617:
        XOR@    R1,     R7                      ; 1617   03CF
.EXEC.618:
        HLT                                     ; 1618   0000
.EXEC.619:
        COMR    R0                              ; 1619   0018
.EXEC.61A:
        ADCR    R5                              ; 161A   002D
.EXEC.61B:
        RSWD    R3                              ; 161B   003B
.EXEC.61C:
        SWAP    R0,     1                       ; 161C   0040
.EXEC.61D:
        RSWD    R3                              ; 161D   003B
.EXEC.61E:
        ADCR    R5                              ; 161E   002D
.EXEC.61F:
        COMR    R0                              ; 161F   0018
.EXEC.620:
        HLT                                     ; 1620   0000
.EXEC.621:
        XOR@    R5,     R0                      ; 1621   03E8
.EXEC.622:
        XOR@    R2,     R3                      ; 1622   03D3
.EXEC.623:
        XOR     G_03C0, R5                      ; 1623   03C5 03C0
.EXEC.625:
        XOR     G_03D3, R5                      ; 1625   03C5 03D3
.EXEC.627:
        XOR@    R5,     R0                      ; 1627   03E8
.EXEC.628:
        MVI@    R5,     R0                      ; 1628   02A8
.EXEC.629:
        PSHR    R5                              ; 1629   0275
.EXEC.62A:
        PSHR    R2                              ; 162A   0272

.EXEC.62B:
        JSR     R5,     .EXEC.637               ; 162B   0004 0114 0237

.EXEC.62E:
        PSHR    R2                              ; 162E   0272

.EXEC.62F:
        JSR     R5,     .EXEC.63D               ; 162F   0004 0114 023D

.EXEC.632:
        PULR    R0                              ; 1632   02B0
.EXEC.633:
        MOVR    R2,     R1                      ; 1633   0091
.EXEC.634:
        PULR    R2                              ; 1634   02B2
.EXEC.635:
        B       X_PACK_BYTES.1                  ; 1635   0200 0119

.EXEC.637:
        PSHR    R5                              ; 1637   0275
.EXEC.638:
        PSHR    R1                              ; 1638   0271
.EXEC.639:
        ADDI    #$0004, R1                      ; 1639   02F9 0004
.EXEC.63B:
        B       .EXEC.641                       ; 163B   0200 0004

.EXEC.63D:
        PSHR    R5                              ; 163D   0275
.EXEC.63E:
        PSHR    R1                              ; 163E   0271
.EXEC.63F:
        ADDI    #$0008, R1                      ; 163F   02F9 0008
.EXEC.641:
        PSHR    R0                              ; 1641   0270
.EXEC.642:
        TSTR    R0                              ; 1642   0080
.EXEC.643:
        BPL     .EXEC.648                       ; 1643   0203 0003

.EXEC.645:
        ADDI    #$0008, R1                      ; 1645   02F9 0008
.EXEC.647:
        NEGR    R0                              ; 1647   0020
.EXEC.648:
        ANDI    #$000F, R1                      ; 1648   03B9 000F
.EXEC.64A:
        SDBD                                    ; 164A   0001
.EXEC.64B:
        ADDI    #$1618, R1                      ; 164B   02F9 0018 0016
.EXEC.64E:
        MVI@    R1,     R1                      ; 164E   0289
.EXEC.64F:
        SWAP    R1,     1                       ; 164F   0041
.EXEC.650:
        SAR     R1,     2                       ; 1650   006D
.EXEC.651:
        SAR     R1,     2                       ; 1651   006D
.EXEC.652:
        CLRR    R2                              ; 1652   01D2
.EXEC.653:
        SAR     R1,     2                       ; 1653   006D
.EXEC.654:
        SAR     R1,     2                       ; 1654   006D
.EXEC.655:
        SARC    R0,     1                       ; 1655   0078
.EXEC.656:
        BNC     .EXEC.659                       ; 1656   0209 0001

.EXEC.658:
        ADDR    R1,     R2                      ; 1658   00CA
.EXEC.659:
        SLL     R1,     1                       ; 1659   0049
.EXEC.65A:
        TSTR    R0                              ; 165A   0080
.EXEC.65B:
        BNEQ    .EXEC.655                       ; 165B   022C 0007

.EXEC.65D:
        SLL     R2,     2                       ; 165D   004E
.EXEC.65E:
        SLL     R2,     1                       ; 165E   004A
.EXEC.65F:
        ADDI    #$0080, R2                      ; 165F   02FA 0080
.EXEC.661:
        SAR     R2,     2                       ; 1661   006E
.EXEC.662:
        SAR     R2,     2                       ; 1662   006E
.EXEC.663:
        SAR     R2,     2                       ; 1663   006E
.EXEC.664:
        SAR     R2,     2                       ; 1664   006E
.EXEC.665:
        PULR    R0                              ; 1665   02B0
.EXEC.666:
        PULR    R1                              ; 1666   02B1
.EXEC.667:
        PULR    R7                              ; 1667   02B7
X_EXT_SIGN_LO:
        SWAP    R0,     1                       ; 1668   0040
X_EXT_SIGN_HI:
        PSHR    R5                              ; 1669   0275
.EXEC.66A:
        SAR     R0,     2                       ; 166A   006C
.EXEC.66B:
        NOP                                     ; 166B   0034
.EXEC.66C:
        SAR     R0,     2                       ; 166C   006C
.EXEC.66D:
        SAR     R0,     2                       ; 166D   006C
.EXEC.66E:
        SAR     R0,     2                       ; 166E   006C
.EXEC.66F:
        PULR    R7                              ; 166F   02B7
X_CLAMP:
        CMP@    R5,     R0                      ; 1670   0368
.EXEC.671:
        BLT     .EXEC.679                       ; 1671   0205 0006

.EXEC.673:
        CMP@    R5,     R0                      ; 1673   0368
.EXEC.674:
        BLE     .EXEC.678                       ; 1674   0206 0002

.EXEC.676:
        DECR    R5                              ; 1676   0015
.EXEC.677:
        MVI@    R5,     R0                      ; 1677   02A8
.EXEC.678:
        MOVR    R5,     R7                      ; 1678   00AF
.EXEC.679:
        DECR    R5                              ; 1679   0015
.EXEC.67A:
        MVI@    R5,     R0                      ; 167A   02A8
.EXEC.67B:
        INCR    R5                              ; 167B   000D
.EXEC.67C:
        MOVR    R5,     R7                      ; 167C   00AF
X_RAND1:
        PSHR    R5                              ; 167D   0275
.EXEC.67E:
        MOVR    R0,     R5                      ; 167E   0085
.EXEC.67F:
        BEQ     .EXEC.7D4                       ; 167F   0204 0153

.EXEC.681:
        PSHR    R1                              ; 1681   0271
.EXEC.682:
        PSHR    R2                              ; 1682   0272
.EXEC.683:
        CLRR    R2                              ; 1683   01D2
.EXEC.684:
        MVI     G_035E, R0                      ; 1684   0280 035E
.EXEC.686:
        SLL     R0,     2                       ; 1686   004C
.EXEC.687:
        SLL     R0,     2                       ; 1687   004C
.EXEC.688:
        MOVR    R0,     R1                      ; 1688   0081
.EXEC.689:
        XOR     G_035E, R0                      ; 1689   03C0 035E
.EXEC.68B:
        SWAP    R1,     1                       ; 168B   0041
.EXEC.68C:
        SLL     R1,     1                       ; 168C   0049
.EXEC.68D:
        XORR    R1,     R0                      ; 168D   01C8
.EXEC.68E:
        SLL     R1,     2                       ; 168E   004D
.EXEC.68F:
        XORR    R1,     R0                      ; 168F   01C8
.EXEC.690:
        RLC     R0,     1                       ; 1690   0050
.EXEC.691:
        MVI     G_035E, R0                      ; 1691   0280 035E
.EXEC.693:
        RLC     R0,     1                       ; 1693   0050
.EXEC.694:
        MVO     R0,     G_035E                  ; 1694   0240 035E
.EXEC.696:
        SETC                                    ; 1696   0007
.EXEC.697:
        RLC     R2,     1                       ; 1697   0052
.EXEC.698:
        DECR    R5                              ; 1698   0015
.EXEC.699:
        BNEQ    .EXEC.686                       ; 1699   022C 0014

.EXEC.69B:
        ANDR    R2,     R0                      ; 169B   0190
.EXEC.69C:
        B       .EXEC.7D2                       ; 169C   0200 0134

X_RAND2:
        PSHR    R5                              ; 169E   0275
.EXEC.69F:
        PSHR    R1                              ; 169F   0271
.EXEC.6A0:
        PSHR    R2                              ; 16A0   0272
.EXEC.6A1:
        MOVR    R0,     R1                      ; 16A1   0081
.EXEC.6A2:
        BEQ     .EXEC.7D2                       ; 16A2   0204 012E

.EXEC.6A4:
        CLRR    R2                              ; 16A4   01D2
.EXEC.6A5:
        INCR    R2                              ; 16A5   000A
.EXEC.6A6:
        SLR     R0,     1                       ; 16A6   0060
.EXEC.6A7:
        BNEQ    .EXEC.6A5                       ; 16A7   022C 0003

.EXEC.6A9:
        MOVR    R2,     R0                      ; 16A9   0090

.EXEC.6AA:
        JSR     R5,     X_RAND1                 ; 16AA   0004 0114 027D

.EXEC.6AD:
        CMPR    R1,     R0                      ; 16AD   0148
.EXEC.6AE:
        BGE     .EXEC.6A9                       ; 16AE   022D 0006
.EXEC.6B0:
        B       .EXEC.7D2                       ; 16B0   0200 0120

X_INIT_MOB:
        MVII    #$0001, R0                      ; 16B2   02B8 0001
X_INIT_MOBS:
        PSHR    R5                              ; 16B4   0275

.EXEC.6B5:
        JSR     R5,     .EXEC.7C1               ; 16B5   0004 0114 03C1

.EXEC.6B8:
        MOVR    R1,     R4                      ; 16B8   008C
.EXEC.6B9:
        MOVR    R2,     R5                      ; 16B9   0095
.EXEC.6BA:
        MOVR    R0,     R2                      ; 16BA   0082
.EXEC.6BB:
        MOVR    R5,     R1                      ; 16BB   00A9

.EXEC.6BC:
        JSR     R5,     .EXEC.992               ; 16BC   0004 0118 0192
.EXEC.6BF:
        JSR     R5,     .EXEC.6D5               ; 16BF   0004 0114 02D5

.EXEC.6C2:
        MOVR    R1,     R5                      ; 16C2   008D
.EXEC.6C3:
        MVII    #$0008, R3                      ; 16C3   02BB 0008
.EXEC.6C5:
        SDBD                                    ; 16C5   0001
.EXEC.6C6:
        MVI@    R4,     R1                      ; 16C6   02A1
.EXEC.6C7:
        MVO@    R1,     R5                      ; 16C7   0269
.EXEC.6C8:
        DECR    R3                              ; 16C8   0013
.EXEC.6C9:
        BNEQ    .EXEC.6C5                       ; 16C9   022C 0005

.EXEC.6CB:
        DECR    R2                              ; 16CB   0012
.EXEC.6CC:
        BNEQ    .EXEC.6BB                       ; 16CC   022C 0012

.EXEC.6CE:
        PULR    R7                              ; 16CE   02B7
.EXEC.6CF:
        PSHR    R5                              ; 16CF   0275

.EXEC.6D0:
        JSR     R5,     X_CLR_BIT               ; 16D0   0004 0114 02E6

.EXEC.6D3:
        SUBR    R3,     R2                      ; 16D3   011A
.EXEC.6D4:
        PULR    R7                              ; 16D4   02B7
.EXEC.6D5:
        PSHR    R5                              ; 16D5   0275

.EXEC.6D6:
        JSR     R5,     X_SET_BIT               ; 16D6   0004 0114 02DB

.EXEC.6D9:
        SUBR    R3,     R2                      ; 16D9   011A
.EXEC.6DA:
        PULR    R7                              ; 16DA   02B7
X_SET_BIT:
        PSHR    R0                              ; 16DB   0270
.EXEC.6DC:
        PSHR    R1                              ; 16DC   0271
.EXEC.6DD:
        MVI@    R5,     R1                      ; 16DD   02A9
.EXEC.6DE:
        PSHR    R5                              ; 16DE   0275

.EXEC.6DF:
        JSR     R5,     X_POW2                  ; 16DF   0004 0114 0345

.EXEC.6E2:
        COMR    R0                              ; 16E2   0018
.EXEC.6E3:
        AND@    R1,     R0                      ; 16E3   0388
.EXEC.6E4:
        B       .EXEC.6F1                       ; 16E4   0200 000B

X_CLR_BIT:
        PSHR    R0                              ; 16E6   0270
.EXEC.6E7:
        PSHR    R1                              ; 16E7   0271
.EXEC.6E8:
        MVI@    R5,     R1                      ; 16E8   02A9
.EXEC.6E9:
        PSHR    R5                              ; 16E9   0275

.EXEC.6EA:
        JSR     R5,     X_POW2                  ; 16EA   0004 0114 0345

.EXEC.6ED:
        MOVR    R0,     R5                      ; 16ED   0085
.EXEC.6EE:
        COMR    R0                              ; 16EE   0018
.EXEC.6EF:
        AND@    R1,     R0                      ; 16EF   0388
.EXEC.6F0:
        XORR    R5,     R0                      ; 16F0   01E8
.EXEC.6F1:
        MVO@    R0,     R1                      ; 16F1   0248
.EXEC.6F2:
        PULR    R5                              ; 16F2   02B5
.EXEC.6F3:
        PULR    R1                              ; 16F3   02B1
.EXEC.6F4:
        PULR    R0                              ; 16F4   02B0
.EXEC.6F5:
        PSHR    R5                              ; 16F5   0275
.EXEC.6F6:
        PULR    R7                              ; 16F6   02B7
.EXEC.6F7:
        PSHR    R5                              ; 16F7   0275
.EXEC.6F8:
        PSHR    R2                              ; 16F8   0272

.EXEC.6F9:
        JSR     R5,     .EXEC.777               ; 16F9   0004 0114 0377

.EXEC.6FC:
        PULR    R5                              ; 16FC   02B5
.EXEC.6FD:
        PSHR    R5                              ; 16FD   0275
.EXEC.6FE:
        MOVR    R5,     R0                      ; 16FE   00A8
.EXEC.6FF:
        ANDI    #$00FF, R5                      ; 16FF   03BD 00FF
.EXEC.701:
        XORR    R5,     R0                      ; 1701   01E8
.EXEC.702:
        SWAP    R0,     1                       ; 1702   0040
.EXEC.703:
        SUBR    R0,     R2                      ; 1703   0102
.EXEC.704:
        BPL     .EXEC.707                       ; 1704   0203 0001

.EXEC.706:
        NEGR    R2                              ; 1706   0022
.EXEC.707:
        SUBR    R5,     R3                      ; 1707   012B
.EXEC.708:
        BPL     .EXEC.70B                       ; 1708   0203 0001

.EXEC.70A:
        NEGR    R3                              ; 170A   0023
.EXEC.70B:
        PULR    R0                              ; 170B   02B0
.EXEC.70C:
        PSHR    R1                              ; 170C   0271
.EXEC.70D:
        B       .EXEC.722                       ; 170D   0200 0013

.EXEC.70F:
        PSHR    R5                              ; 170F   0275
.EXEC.710:
        MOVR    R3,     R0                      ; 1710   0098

.EXEC.711:
        JSR     R5,     .EXEC.777               ; 1711   0004 0114 0377

.EXEC.714:
        PSHR    R1                              ; 1714   0271
.EXEC.715:
        PSHR    R2                              ; 1715   0272
.EXEC.716:
        PSHR    R3                              ; 1716   0273

.EXEC.717:
        JSR     R5,     .EXEC.772               ; 1717   0004 0114 0372

.EXEC.71A:
        SUB@    R6,     R3                      ; 171A   0333
.EXEC.71B:
        BPL     .EXEC.71E                       ; 171B   0203 0001

.EXEC.71D:
        NEGR    R3                              ; 171D   0023
.EXEC.71E:
        SUB@    R6,     R2                      ; 171E   0332
.EXEC.71F:
        BPL     .EXEC.722                       ; 171F   0203 0001

.EXEC.721:
        NEGR    R2                              ; 1721   0022
.EXEC.722:
        MOVR    R4,     R1                      ; 1722   00A1
.EXEC.723:
        ANDI    #$00FF, R4                      ; 1723   03BC 00FF
.EXEC.725:
        XORR    R4,     R1                      ; 1725   01E1
.EXEC.726:
        SWAP    R1,     1                       ; 1726   0041
.EXEC.727:
        SUBR    R2,     R1                      ; 1727   0111
.EXEC.728:
        BNC     .EXEC.72B                       ; 1728   0209 0001

.EXEC.72A:
        SUBR    R3,     R4                      ; 172A   011C
.EXEC.72B:
        MOVR    R1,     R5                      ; 172B   008D
.EXEC.72C:
        PULR    R1                              ; 172C   02B1
.EXEC.72D:
        MOVR    R0,     R2                      ; 172D   0082
.EXEC.72E:
        MOVR    R0,     R3                      ; 172E   0083
.EXEC.72F:
        PULR    R7                              ; 172F   02B7
.EXEC.730:
        PSHR    R5                              ; 1730   0275
.EXEC.731:
        MOVR    R1,     R5                      ; 1731   008D
.EXEC.732:
        MVI@    R4,     R1                      ; 1732   02A1
.EXEC.733:
        MVO@    R1,     R5                      ; 1733   0269
.EXEC.734:
        DECR    R0                              ; 1734   0010
.EXEC.735:
        BNEQ    .EXEC.732                       ; 1735   022C 0004

.EXEC.737:
        PULR    R7                              ; 1737   02B7
X_FILL_ZERO:
        PSHR    R5                              ; 1738   0275
.EXEC.739:
        CLRR    R5                              ; 1739   01ED
.EXEC.73A:
        PSHR    R0                              ; 173A   0270
.EXEC.73B:
        MVO@    R5,     R4                      ; 173B   0265
.EXEC.73C:
        DECR    R0                              ; 173C   0010
.EXEC.73D:
        BNEQ    .EXEC.73B                       ; 173D   022C 0003

.EXEC.73F:
        PULR    R0                              ; 173F   02B0
.EXEC.740:
        PULR    R7                              ; 1740   02B7
X_FILL_MEM:
        PSHR    R5                              ; 1741   0275
.EXEC.742:
        MOVR    R1,     R5                      ; 1742   008D
.EXEC.743:
        B       .EXEC.73A                       ; 1743   0220 000A

X_POW2:
        PSHR    R5                              ; 1745   0275
.EXEC.746:
        MOVR    R0,     R5                      ; 1746   0085
.EXEC.747:
        MVII    #$0001, R0                      ; 1747   02B8 0001
.EXEC.749:
        INCR    R7                              ; 1749   000F
.EXEC.74A:
        SLL     R0,     1                       ; 174A   0048
.EXEC.74B:
        DECR    R5                              ; 174B   0015
.EXEC.74C:
        BPL     .EXEC.74A                       ; 174C   0223 0003

.EXEC.74E:
        PULR    R7                              ; 174E   02B7
X_PACK_BYTES:
        PSHR    R5                              ; 174F   0275
X_PACK_BYTES.1:
        ANDI    #$00FF, R0                      ; 1750   03B8 00FF
.EXEC.752:
        SWAP    R0,     1                       ; 1752   0040
.EXEC.753:
        ANDI    #$00FF, R1                      ; 1753   03B9 00FF
.EXEC.755:
        XORR    R1,     R0                      ; 1755   01C8
.EXEC.756:
        PULR    R7                              ; 1756   02B7
X_UNPK_BYTES:
        PSHR    R5                              ; 1757   0275
X_UNPK_BYTES.1:
        PSHR    R0                              ; 1758   0270

.EXEC.759:
        JSR     R5,     X_EXT_SIGN_LO           ; 1759   0004 0114 0268

.EXEC.75C:
        MOVR    R0,     R1                      ; 175C   0081
.EXEC.75D:
        PULR    R0                              ; 175D   02B0
.EXEC.75E:
        B       .EXEC.66A                       ; 175E   0220 00F5

.EXEC.760:
        PSHR    R5                              ; 1760   0275
.EXEC.761:
        INCR    R1                              ; 1761   0009
.EXEC.762:
        MVI@    R1,     R0                      ; 1762   0288
.EXEC.763:
        DECR    R1                              ; 1763   0011
.EXEC.764:
        TSTR    R0                              ; 1764   0080
.EXEC.765:
        PULR    R7                              ; 1765   02B7
.EXEC.766:
        MOVR    R1,     R0                      ; 1766   0088
.EXEC.767:
        SUBI    #$031D, R0                      ; 1767   0338 031D
.EXEC.769:
        SLR     R0,     2                       ; 1769   0064
.EXEC.76A:
        SLR     R0,     1                       ; 176A   0060
.EXEC.76B:
        MOVR    R5,     R7                      ; 176B   00AF
.EXEC.76C:
        MOVR    R0,     R1                      ; 176C   0081
.EXEC.76D:
        SLL     R1,     2                       ; 176D   004D
.EXEC.76E:
        SLL     R1,     1                       ; 176E   0049
.EXEC.76F:
        ADDI    #$031D, R1                      ; 176F   02F9 031D
.EXEC.771:
        MOVR    R5,     R7                      ; 1771   00AF
.EXEC.772:
        PSHR    R5                              ; 1772   0275

.EXEC.773:
        JSR     R5,     .EXEC.76C               ; 1773   0004 0114 036C

.EXEC.776:
        INCR    R7                              ; 1776   000F
.EXEC.777:
        PSHR    R5                              ; 1777   0275
.EXEC.778:
        MOVR    R1,     R5                      ; 1778   008D
.EXEC.779:
        ADDI    #$0002, R5                      ; 1779   02FD 0002
.EXEC.77B:
        MVI@    R5,     R2                      ; 177B   02AA
.EXEC.77C:
        SWAP    R2,     1                       ; 177C   0042
.EXEC.77D:
        ANDI    #$00FF, R2                      ; 177D   03BA 00FF
.EXEC.77F:
        MVI@    R5,     R3                      ; 177F   02AB
.EXEC.780:
        SWAP    R3,     1                       ; 1780   0043
.EXEC.781:
        ANDI    #$00FF, R3                      ; 1781   03BB 00FF
.EXEC.783:
        PULR    R7                              ; 1783   02B7
.EXEC.784:
        MVI@    R4,     R0                      ; 1784   02A0
.EXEC.785:
        SWAP    R0,     1                       ; 1785   0040
.EXEC.786:
        ANDI    #$00FF, R0                      ; 1786   03B8 00FF
.EXEC.788:
        MVI@    R4,     R1                      ; 1788   02A1
.EXEC.789:
        SWAP    R1,     1                       ; 1789   0041
.EXEC.78A:
        ANDI    #$00FF, R1                      ; 178A   03B9 00FF
.EXEC.78C:
        PSHR    R5                              ; 178C   0275
.EXEC.78D:
        PSHR    R0                              ; 178D   0270
.EXEC.78E:
        SUBR    R2,     R0                      ; 178E   0110
.EXEC.78F:
        NEGR    R0                              ; 178F   0020
.EXEC.790:
        PSHR    R0                              ; 1790   0270
.EXEC.791:
        PSHR    R1                              ; 1791   0271

.EXEC.792:
        JSR     R5,     X_SQUARE                ; 1792   0004 011C 01DB

.EXEC.795:
        PULR    R0                              ; 1795   02B0
.EXEC.796:
        MOVR    R0,     R4                      ; 1796   0084
.EXEC.797:
        SUBR    R3,     R0                      ; 1797   0118
.EXEC.798:
        NEGR    R0                              ; 1798   0020
.EXEC.799:
        PSHR    R0                              ; 1799   0270
.EXEC.79A:
        PSHR    R2                              ; 179A   0272

.EXEC.79B:
        JSR     R5,     X_SQUARE                ; 179B   0004 011C 01DB

.EXEC.79E:
        ADD@    R6,     R2                      ; 179E   02F2
.EXEC.79F:
        PULR    R1                              ; 179F   02B1
.EXEC.7A0:
        PULR    R0                              ; 17A0   02B0
.EXEC.7A1:
        PULR    R3                              ; 17A1   02B3
.EXEC.7A2:
        PULR    R7                              ; 17A2   02B7
.EXEC.7A3:
        PSHR    R5                              ; 17A3   0275

.EXEC.7A4:
        JSR     R5,     .EXEC.784               ; 17A4   0004 0114 0384

.EXEC.7A7:
        MOVR    R0,     R3                      ; 17A7   0083
.EXEC.7A8:
        MOVR    R1,     R4                      ; 17A8   008C
.EXEC.7A9:
        MOVR    R2,     R1                      ; 17A9   0091
.EXEC.7AA:
        PULR    R5                              ; 17AA   02B5
.EXEC.7AB:
        J       X_SQRT                          ; 17AB   0004 031C 0223

.EXEC.7AE:
        INCR    R1                              ; 17AE   0009
.EXEC.7AF:
        CLRR    R0                              ; 17AF   01C0
.EXEC.7B0:
        MVO@    R0,     R1                      ; 17B0   0248
.EXEC.7B1:
        DECR    R1                              ; 17B1   0011
.EXEC.7B2:
        MOVR    R5,     R7                      ; 17B2   00AF
.EXEC.7B3:
        PSHR    R5                              ; 17B3   0275
.EXEC.7B4:
        MVII    #$0007, R2                      ; 17B4   02BA 0007
.EXEC.7B6:
        MOVR    R2,     R0                      ; 17B6   0090

.EXEC.7B7:
        JSR     R5,     .EXEC.76C               ; 17B7   0004 0114 036C
.EXEC.7BA:
        JSR     R5,     .EXEC.7AE               ; 17BA   0004 0114 03AE

.EXEC.7BD:
        DECR    R2                              ; 17BD   0012
.EXEC.7BE:
        BPL     .EXEC.7B6                       ; 17BE   0223 0009

.EXEC.7C0:
        PULR    R7                              ; 17C0   02B7
.EXEC.7C1:
        PSHR    R1                              ; 17C1   0271
.EXEC.7C2:
        PSHR    R2                              ; 17C2   0272
.EXEC.7C3:
        PSHR    R3                              ; 17C3   0273
.EXEC.7C4:
        PSHR    R4                              ; 17C4   0274
.EXEC.7C5:
        SDBD                                    ; 17C5   0001
.EXEC.7C6:
        MVII    #$17D0, R4                      ; 17C6   02BC 00D0 0017
.EXEC.7C9:
        PSHR    R4                              ; 17C9   0274
.EXEC.7CA:
        PSHR    R5                              ; 17CA   0275
.EXEC.7CB:
        MOVR    R6,     R5                      ; 17CB   00B5
.EXEC.7CC:
        SUBI    #$0003, R5                      ; 17CC   033D 0003
.EXEC.7CE:
        MVI@    R5,     R4                      ; 17CE   02AC
.EXEC.7CF:
        PULR    R7                              ; 17CF   02B7
.EXEC.7D0:
        PULR    R4                              ; 17D0   02B4
.EXEC.7D1:
        PULR    R3                              ; 17D1   02B3
.EXEC.7D2:
        PULR    R2                              ; 17D2   02B2
.EXEC.7D3:
        PULR    R1                              ; 17D3   02B1
.EXEC.7D4:
        PULR    R7                              ; 17D4   02B7
.EXEC.7D5:
        PSHR    R5                              ; 17D5   0275

.EXEC.7D6:
        JSR     R5,     X_READ_ROM_HDR          ; 17D6   0004 0110 00AB

.EXEC.7D9:
        EIS                                     ; 17D9   0002
.EXEC.7DA:
        MVII    #$0125, R4                      ; 17DA   02BC 0125
.EXEC.7DC:
        SDBD                                    ; 17DC   0001
.EXEC.7DD:
        MVI@    R5,     R0                      ; 17DD   02A8
.EXEC.7DE:
        SDBD                                    ; 17DE   0001
.EXEC.7DF:
        MVI@    R5,     R3                      ; 17DF   02AB
.EXEC.7E0:
        TSTR    R0                              ; 17E0   0080
.EXEC.7E1:
        BEQ     .EXEC.81D                       ; 17E1   0204 003A

.EXEC.7E3:
        MOVR    R4,     R2                      ; 17E3   00A2
.EXEC.7E4:
        SDBD                                    ; 17E4   0001
.EXEC.7E5:
        MVI@    R4,     R1                      ; 17E5   02A1
.EXEC.7E6:
        SUBI    #$0001, R1                      ; 17E6   0339 0001
.EXEC.7E8:
        BLT     .EXEC.7DC                       ; 17E8   0225 000D

.EXEC.7EA:
        MOVR    R2,     R4                      ; 17EA   0094
.EXEC.7EB:
        MVO@    R1,     R4                      ; 17EB   0261
.EXEC.7EC:
        SWAP    R1,     1                       ; 17EC   0041
.EXEC.7ED:
        MVO@    R1,     R4                      ; 17ED   0261
.EXEC.7EE:
        BNEQ    .EXEC.7DC                       ; 17EE   022C 0013

.EXEC.7F0:
        MOVR    R2,     R4                      ; 17F0   0094
.EXEC.7F1:
        MVO@    R3,     R4                      ; 17F1   0263
.EXEC.7F2:
        SWAP    R3,     1                       ; 17F2   0043
.EXEC.7F3:
        MVO@    R3,     R4                      ; 17F3   0263
.EXEC.7F4:
        PSHR    R5                              ; 17F4   0275
.EXEC.7F5:
        MOVR    R7,     R5                      ; 17F5   00BD
.EXEC.7F6:
        ADDI    #$0004, R5                      ; 17F6   02FD 0004
.EXEC.7F8:
        PSHR    R4                              ; 17F8   0274
.EXEC.7F9:
        MOVR    R0,     R7                      ; 17F9   0087
.EXEC.7FA:
        PULR    R4                              ; 17FA   02B4
.EXEC.7FB:
        PULR    R5                              ; 17FB   02B5
.EXEC.7FC:
        B       .EXEC.7DC                       ; 17FC   0220 0021

.EXEC.7FE:
        PSHR    R5                              ; 17FE   0275

.EXEC.7FF:
        JSR     R5,     X_READ_ROM_HDR          ; 17FF   0004 0110 00AB

.EXEC.802:
        EIS                                     ; 1802   0002
.EXEC.803:
        MVII    #$0125, R4                      ; 1803   02BC 0125
.EXEC.805:
        SDBD                                    ; 1805   0001
.EXEC.806:
        MVI@    R5,     R0                      ; 1806   02A8
.EXEC.807:
        TSTR    R0                              ; 1807   0080
.EXEC.808:
        BEQ     .EXEC.81D                       ; 1808   0204 0013

.EXEC.80A:
        SDBD                                    ; 180A   0001
.EXEC.80B:
        MVI@    R5,     R0                      ; 180B   02A8
.EXEC.80C:
        MVO@    R0,     R4                      ; 180C   0260
.EXEC.80D:
        SWAP    R0,     1                       ; 180D   0040
.EXEC.80E:
        MVO@    R0,     R4                      ; 180E   0260
.EXEC.80F:
        B       .EXEC.805                       ; 180F   0220 000B

.EXEC.811:
        PSHR    R5                              ; 1811   0275
.EXEC.812:
        PSHR    R4                              ; 1812   0274

.EXEC.813:
        JSR     R5,     X_READ_ROM_HDR          ; 1813   0004 0110 00AB

.EXEC.816:
        EIS                                     ; 1816   0002
.EXEC.817:
        PULR    R4                              ; 1817   02B4
.EXEC.818:
        SUBR    R5,     R1                      ; 1818   0129
.EXEC.819:
        SAR     R1,     1                       ; 1819   0069
.EXEC.81A:
        ADDI    #$0125, R1                      ; 181A   02F9 0125
.EXEC.81C:
        MOVR    R1,     R5                      ; 181C   008D
.EXEC.81D:
        PULR    R7                              ; 181D   02B7
.EXEC.81E:
        PSHR    R5                              ; 181E   0275
.EXEC.81F:
        PSHR    R1                              ; 181F   0271
.EXEC.820:
        PSHR    R2                              ; 1820   0272
.EXEC.821:
        MOVR    R1,     R5                      ; 1821   008D
.EXEC.822:
        SDBD                                    ; 1822   0001
.EXEC.823:
        MVI@    R5,     R0                      ; 1823   02A8
.EXEC.824:
        SDBD                                    ; 1824   0001
.EXEC.825:
        MVI@    R5,     R2                      ; 1825   02AA
.EXEC.826:
        SLL     R2,     1                       ; 1826   004A
.EXEC.827:
        SLR     R2,     1                       ; 1827   0062

.EXEC.828:
        JSR     R5,     .EXEC.811               ; 1828   0004 0118 0011

.EXEC.82B:
        MVO@    R2,     R5                      ; 182B   026A
.EXEC.82C:
        SWAP    R2,     1                       ; 182C   0042
.EXEC.82D:
        MVO@    R2,     R5                      ; 182D   026A
.EXEC.82E:
        PULR    R2                              ; 182E   02B2
.EXEC.82F:
        PULR    R1                              ; 182F   02B1
.EXEC.830:
        PULR    R7                              ; 1830   02B7
.EXEC.831:
        PSHR    R5                              ; 1831   0275
.EXEC.832:
        PSHR    R1                              ; 1832   0271

.EXEC.833:
        JSR     R5,     .EXEC.811               ; 1833   0004 0118 0011

.EXEC.836:
        B       .EXEC.84D                       ; 1836   0200 0015

X_TIMER_STOP:
        PSHR    R5                              ; 1838   0275
.EXEC.839:
        PSHR    R1                              ; 1839   0271

.EXEC.83A:
        JSR     R5,     .EXEC.811               ; 183A   0004 0118 0011

.EXEC.83D:
        SDBD                                    ; 183D   0001
.EXEC.83E:
        MVI@    R5,     R0                      ; 183E   02A8
.EXEC.83F:
        SLL     R0,     1                       ; 183F   0048
.EXEC.840:
        SETC                                    ; 1840   0007
.EXEC.841:
        RRC     R0,     1                       ; 1841   0070
.EXEC.842:
        B       .EXEC.84D                       ; 1842   0200 0009

X_TIMER_START:
        PSHR    R5                              ; 1844   0275
.EXEC.845:
        PSHR    R1                              ; 1845   0271

.EXEC.846:
        JSR     R5,     .EXEC.811               ; 1846   0004 0118 0011

.EXEC.849:
        SDBD                                    ; 1849   0001
.EXEC.84A:
        MVI@    R5,     R0                      ; 184A   02A8
.EXEC.84B:
        SLL     R0,     1                       ; 184B   0048
.EXEC.84C:
        SLR     R0,     1                       ; 184C   0060
.EXEC.84D:
        MVO@    R0,     R1                      ; 184D   0248
.EXEC.84E:
        INCR    R1                              ; 184E   0009
.EXEC.84F:
        SWAP    R0,     1                       ; 184F   0040
.EXEC.850:
        MVO@    R0,     R1                      ; 1850   0248
.EXEC.851:
        PULR    R1                              ; 1851   02B1
.EXEC.852:
        PULR    R7                              ; 1852   02B7
.EXEC.853:
        PSHR    R5                              ; 1853   0275
.EXEC.854:
        PSHR    R1                              ; 1854   0271
.EXEC.855:
        PSHR    R4                              ; 1855   0274
.EXEC.856:
        MOVR    R3,     R5                      ; 1856   009D
.EXEC.857:
        MVO@    R5,     R4                      ; 1857   0265
.EXEC.858:
        MVI     G_0105, R1                      ; 1858   0281 0105
.EXEC.85A:
        RRC     R1,     1                       ; 185A   0071
.EXEC.85B:
        BC      .EXEC.861                       ; 185B   0201 0004

.EXEC.85D:
        SDBD                                    ; 185D   0001
.EXEC.85E:
        ANDI    #$DFFF, R5                      ; 185E   03BD 00FF 00DF
.EXEC.861:
        DECR    R0                              ; 1861   0010
.EXEC.862:
        BNEQ    .EXEC.857                       ; 1862   022C 000C

.EXEC.864:
        PULR    R4                              ; 1864   02B4
.EXEC.865:
        PULR    R1                              ; 1865   02B1
.EXEC.866:
        PULR    R7                              ; 1866   02B7
X_PRINT_R1:
        PSHR    R5                              ; 1867   0275
.EXEC.868:
        SETC                                    ; 1868   0007
.EXEC.869:
        MOVR    R1,     R5                      ; 1869   008D
.EXEC.86A:
        B       .EXEC.87C                       ; 186A   0200 0010

X_PRPAD_R1:
        PSHR    R5                              ; 186C   0275
.EXEC.86D:
        SETC                                    ; 186D   0007
.EXEC.86E:
        MOVR    R1,     R5                      ; 186E   008D
.EXEC.86F:
        B       .EXEC.872                       ; 186F   0200 0001

X_PRPAD_R5:
        CLRC                                    ; 1871   0006
.EXEC.872:
        SLL     R3,     1                       ; 1872   004B
.EXEC.873:
        RRC     R3,     1                       ; 1873   0073
.EXEC.874:
        PSHR    R5                              ; 1874   0275

.EXEC.875:
        JSR     R5,     .EXEC.853               ; 1875   0004 0118 0053

.EXEC.878:
        PULR    R5                              ; 1878   02B5
.EXEC.879:
        B       .EXEC.87E                       ; 1879   0200 0003

X_PRINT_R5:
        CLRC                                    ; 187B   0006
.EXEC.87C:
        SLL     R3,     1                       ; 187C   004B
.EXEC.87D:
        RRC     R3,     1                       ; 187D   0073
.EXEC.87E:
        PSHR    R3                              ; 187E   0273
.EXEC.87F:
        MVI@    R5,     R0                      ; 187F   02A8
.EXEC.880:
        ANDI    #$007F, R0                      ; 1880   03B8 007F
.EXEC.882:
        BNEQ    .EXEC.889                       ; 1882   020C 0005

.EXEC.884:
        TSTR    R3                              ; 1884   009B
.EXEC.885:
        PULR    R3                              ; 1885   02B3
.EXEC.886:
        BMI     .EXEC.8FE                       ; 1886   020B 0076

.EXEC.888:
        MOVR    R5,     R7                      ; 1888   00AF
.EXEC.889:
        SUBI    #$0020, R0                      ; 1889   0338 0020
.EXEC.88B:
        SLL     R0,     2                       ; 188B   004C
.EXEC.88C:
        SLL     R0,     1                       ; 188C   0048
.EXEC.88D:
        XORR    R3,     R0                      ; 188D   01D8
.EXEC.88E:
        MVO@    R0,     R4                      ; 188E   0260
.EXEC.88F:
        MVI     G_0105, R0                      ; 188F   0280 0105
.EXEC.891:
        RRC     R0,     1                       ; 1891   0070
.EXEC.892:
        BC      .EXEC.87F                       ; 1892   0221 0014

.EXEC.894:
        SDBD                                    ; 1894   0001
.EXEC.895:
        ANDI    #$DFFF, R3                      ; 1895   03BB 00FF 00DF
.EXEC.898:
        B       .EXEC.87F                       ; 1898   0220 001A

.EXEC.89A:
        DECLE   $0001                           ; 189A   0001
.EXEC.89B:
        INCR    R2                              ; 189B   000A
.EXEC.89C:
        SLR     R0,     2                       ; 189C   0064
.EXEC.89D:
        XOR@    R5,     R0                      ; 189D   03E8
X_PRNUM_LFT:
        PSHR    R5                              ; 189E   0275
.EXEC.89F:
        PSHR    R0                              ; 189F   0270
.EXEC.8A0:
        MOVR    R1,     R0                      ; 18A0   0088

.EXEC.8A1:
        JSR     R5,     .EXEC.853               ; 18A1   0004 0118 0053

.EXEC.8A4:
        PULR    R0                              ; 18A4   02B0

.EXEC.8A5:
        JSR     R5,     .EXEC.7C1               ; 18A5   0004 0114 03C1

.EXEC.8A8:
        SLL     R3,     1                       ; 18A8   004B
.EXEC.8A9:
        SETC                                    ; 18A9   0007
.EXEC.8AA:
        RRC     R3,     1                       ; 18AA   0073
.EXEC.8AB:
        B       .EXEC.8C9                       ; 18AB   0200 001C

X_PRNUM_ZRO:
        PSHR    R5                              ; 18AD   0275

.EXEC.8AE:
        JSR     R5,     .EXEC.7C1               ; 18AE   0004 0114 03C1

.EXEC.8B1:
        MVII    #$0080, R2                      ; 18B1   02BA 0080
.EXEC.8B3:
        XORR    R3,     R2                      ; 18B3   01DA
.EXEC.8B4:
        B       .EXEC.8CA                       ; 18B4   0200 0014

.EXEC.8B6:
        PSHR    R5                              ; 18B6   0275
.EXEC.8B7:
        PSHR    R0                              ; 18B7   0270
.EXEC.8B8:
        MVI     G_0105, R0                      ; 18B8   0280 0105
.EXEC.8BA:
        RRC     R0,     1                       ; 18BA   0070
.EXEC.8BB:
        BC      .EXEC.8C3                       ; 18BB   0201 0006

.EXEC.8BD:
        SDBD                                    ; 18BD   0001
.EXEC.8BE:
        MVII    #$DFFF, R5                      ; 18BE   02BD 00FF 00DF
.EXEC.8C1:
        ANDR    R5,     R3                      ; 18C1   01AB
.EXEC.8C2:
        ANDR    R5,     R2                      ; 18C2   01AA
.EXEC.8C3:
        PULR    R0                              ; 18C3   02B0
.EXEC.8C4:
        PULR    R7                              ; 18C4   02B7
X_PRNUM_RGT:
        PSHR    R5                              ; 18C5   0275

.EXEC.8C6:
        JSR     R5,     .EXEC.7C1               ; 18C6   0004 0114 03C1

.EXEC.8C9:
        MOVR    R3,     R2                      ; 18C9   009A
.EXEC.8CA:
        TSTR    R0                              ; 18CA   0080
.EXEC.8CB:
        BPL     .EXEC.8D6                       ; 18CB   0203 0009

.EXEC.8CD:
        NEGR    R0                              ; 18CD   0020
.EXEC.8CE:
        DECR    R1                              ; 18CE   0011
.EXEC.8CF:
        MVII    #$0068, R5                      ; 18CF   02BD 0068
.EXEC.8D1:
        XORR    R3,     R5                      ; 18D1   01DD
.EXEC.8D2:
        MVO@    R5,     R4                      ; 18D2   0265

.EXEC.8D3:
        JSR     R5,     .EXEC.8B6               ; 18D3   0004 0118 00B6

.EXEC.8D6:
        ADDR    R7,     R1                      ; 18D6   00F9
.EXEC.8D7:
        SUBI    #$003E, R1                      ; 18D7   0339 003E
.EXEC.8D9:
        MVI@    R1,     R5                      ; 18D9   028D
.EXEC.8DA:
        CMPR    R5,     R0                      ; 18DA   0168
.EXEC.8DB:
        BPL     .EXEC.8EA                       ; 18DB   0203 000D

.EXEC.8DD:
        DECR    R5                              ; 18DD   0015
.EXEC.8DE:
        BEQ     .EXEC.8EA                       ; 18DE   0204 000A

.EXEC.8E0:
        TSTR    R3                              ; 18E0   009B
.EXEC.8E1:
        BMI     .EXEC.8E7                       ; 18E1   020B 0004

.EXEC.8E3:
        MVO@    R2,     R4                      ; 18E3   0262

.EXEC.8E4:
        JSR     R5,     .EXEC.8B6               ; 18E4   0004 0118 00B6

.EXEC.8E7:
        DECR    R1                              ; 18E7   0011
.EXEC.8E8:
        B       .EXEC.8D9                       ; 18E8   0220 0010

.EXEC.8EA:
        MVII    #$0080, R2                      ; 18EA   02BA 0080
.EXEC.8EC:
        SUB@    R1,     R0                      ; 18EC   0308
.EXEC.8ED:
        BMI     .EXEC.8F3                       ; 18ED   020B 0004

.EXEC.8EF:
        ADDI    #$0008, R2                      ; 18EF   02FA 0008
.EXEC.8F1:
        B       .EXEC.8EC                       ; 18F1   0220 0006

.EXEC.8F3:
        ADD@    R1,     R0                      ; 18F3   02C8
.EXEC.8F4:
        XORR    R3,     R2                      ; 18F4   01DA
.EXEC.8F5:
        MVO@    R2,     R4                      ; 18F5   0262

.EXEC.8F6:
        JSR     R5,     .EXEC.8B6               ; 18F6   0004 0118 00B6

.EXEC.8F9:
        MVI@    R1,     R2                      ; 18F9   028A
.EXEC.8FA:
        DECR    R1                              ; 18FA   0011
.EXEC.8FB:
        DECR    R2                              ; 18FB   0012
.EXEC.8FC:
        BNEQ    .EXEC.8EA                       ; 18FC   022C 0013

.EXEC.8FE:
        PULR    R7                              ; 18FE   02B7

X_GETNUM:
        JSR     R4,     .EXEC.910               ; 18FF   0004 0018 0110

.EXEC.902:
        HLT                                     ; 1902   0000
.EXEC.903:
        HLT                                     ; 1903   0000
.EXEC.904:
        SLL     R0,     2                       ; 1904   004C
.EXEC.905:
        COMR    R1                              ; 1905   0019
.EXEC.906:
        HLT                                     ; 1906   0000
.EXEC.907:
        HLT                                     ; 1907   0000
.EXEC.908:
        HLT                                     ; 1908   0000
.EXEC.909:
        HLT                                     ; 1909   0000
.EXEC.90A:
        HLT                                     ; 190A   0000
.EXEC.90B:
        HLT                                     ; 190B   0000
.EXEC.90C:
        HLT                                     ; 190C   0000
.EXEC.90D:
        HLT                                     ; 190D   0000
.EXEC.90E:
        HLT                                     ; 190E   0000
.EXEC.90F:
        HLT                                     ; 190F   0000
.EXEC.910:
        MVO     R4,     G_035D                  ; 1910   0244 035D
.EXEC.912:
        MVII    #$0131, R4                      ; 1912   02BC 0131
.EXEC.914:
        MVO@    R2,     R4                      ; 1914   0262
.EXEC.915:
        SUBI    #$0200, R1                      ; 1915   0339 0200
.EXEC.917:
        MVO@    R1,     R4                      ; 1917   0261
.EXEC.918:
        MVO@    R0,     R4                      ; 1918   0260
.EXEC.919:
        ADDI    #$0003, R4                      ; 1919   02FC 0003
.EXEC.91B:
        MVO@    R5,     R4                      ; 191B   0265
.EXEC.91C:
        MOVR    R5,     R0                      ; 191C   00A8
.EXEC.91D:
        SWAP    R0,     1                       ; 191D   0040
.EXEC.91E:
        MVO@    R0,     R4                      ; 191E   0260
.EXEC.91F:
        MVO@    R3,     R4                      ; 191F   0263
.EXEC.920:
        SWAP    R3,     1                       ; 1920   0043
.EXEC.921:
        MVO@    R3,     R4                      ; 1921   0263
.EXEC.922:
        MVII    #$0132, R4                      ; 1922   02BC 0132
.EXEC.924:
        MVI@    R4,     R1                      ; 1924   02A1
.EXEC.925:
        ADDI    #$0200, R1                      ; 1925   02F9 0200
.EXEC.927:
        MVI@    R4,     R0                      ; 1927   02A0
.EXEC.928:
        CLRR    R5                              ; 1928   01ED
.EXEC.929:
        MVO@    R5,     R4                      ; 1929   0265
.EXEC.92A:
        MVO@    R5,     R4                      ; 192A   0265
.EXEC.92B:
        MVO@    R5,     R4                      ; 192B   0265
.EXEC.92C:
        ADDI    #$0002, R4                      ; 192C   02FC 0002
.EXEC.92E:
        SDBD                                    ; 192E   0001
.EXEC.92F:
        XOR@    R4,     R5                      ; 192F   03E5
.EXEC.930:
        MVO@    R5,     R1                      ; 1930   024D
.EXEC.931:
        DECR    R1                              ; 1931   0011
.EXEC.932:
        DECR    R0                              ; 1932   0010
.EXEC.933:
        BNEQ    .EXEC.930                       ; 1933   022C 0004

.EXEC.935:
        PULR    R7                              ; 1935   02B7
.EXEC.936:
        PSHR    R5                              ; 1936   0275
.EXEC.937:
        MVI     G_0149, R0                      ; 1937   0280 0149
.EXEC.939:
        TSTR    R0                              ; 1939   0080
.EXEC.93A:
        BEQ     .EXEC.8FE                       ; 193A   0224 003D

.EXEC.93C:
        MVI     G_035F, R0                      ; 193C   0280 035F
.EXEC.93E:
        SDBD                                    ; 193E   0001
.EXEC.93F:
        SUBI    #$160A, R0                      ; 193F   0338 000A 0016
.EXEC.942:
        BMI     .EXEC.8FE                       ; 1942   022B 0045

.EXEC.944:
        CMPI    #$0014, R0                      ; 1944   0378 0014
.EXEC.946:
        BGT     .EXEC.8FE                       ; 1946   022E 0049

.EXEC.948:
        JSR     R5,     X_PLAY_RAZZ2            ; 1948   0004 011C 02BD

.EXEC.94B:
        PULR    R7                              ; 194B   02B7
.EXEC.94C:
        PSHR    R5                              ; 194C   0275
.EXEC.94D:
        CMP     G_0131, R1                      ; 194D   0341 0131
.EXEC.94F:
        BNEQ    .EXEC.8FE                       ; 194F   022C 0052

.EXEC.951:
        CMPI    #$000A, R0                      ; 1951   0378 000A
.EXEC.953:
        BEQ     .EXEC.922                       ; 1953   0224 0032

.EXEC.955:
        MVII    #$0134, R5                      ; 1955   02BD 0134
.EXEC.957:
        MVI@    R5,     R2                      ; 1957   02AA
.EXEC.958:
        CMPI    #$000B, R0                      ; 1958   0378 000B
.EXEC.95A:
        BNEQ    .EXEC.967                       ; 195A   020C 000B

.EXEC.95C:
        MOVR    R7,     R0                      ; 195C   00B8
.EXEC.95D:
        SUBI    #$0057, R0                      ; 195D   0338 0057
.EXEC.95F:
        MVI     G_035D, R3                      ; 195F   0283 035D
.EXEC.961:
        MVO     R0,     G_035D                  ; 1961   0240 035D
.EXEC.963:
        SDBD                                    ; 1963   0001
.EXEC.964:
        MVI@    R5,     R0                      ; 1964   02A8
.EXEC.965:
        SDBD                                    ; 1965   0001
.EXEC.966:
        MVI@    R5,     R7                      ; 1966   02AF
.EXEC.967:
        MVII    #$0133, R5                      ; 1967   02BD 0133
.EXEC.969:
        CMP@    R5,     R2                      ; 1969   036A
.EXEC.96A:
        BEQ     .EXEC.937                       ; 196A   0224 0034

.EXEC.96C:
        INCR    R2                              ; 196C   000A
.EXEC.96D:
        MVO@    R2,     R5                      ; 196D   026A
.EXEC.96E:
        MOVR    R5,     R4                      ; 196E   00AC
.EXEC.96F:
        SDBD                                    ; 196F   0001
.EXEC.970:
        MVI@    R5,     R1                      ; 1970   02A9
.EXEC.971:
        SLL     R1,     1                       ; 1971   0049
.EXEC.972:
        PSHR    R1                              ; 1972   0271
.EXEC.973:
        SLL     R1,     2                       ; 1973   004D
.EXEC.974:
        ADD@    R6,     R1                      ; 1974   02F1
.EXEC.975:
        ADDR    R0,     R1                      ; 1975   00C1
.EXEC.976:
        MVO@    R1,     R4                      ; 1976   0261
.EXEC.977:
        SWAP    R1,     1                       ; 1977   0041
.EXEC.978:
        MVO@    R1,     R4                      ; 1978   0261
.EXEC.979:
        MVI     G_0132, R1                      ; 1979   0281 0132
.EXEC.97B:
        ADDI    #$0200, R1                      ; 197B   02F9 0200
.EXEC.97D:
        SLL     R0,     2                       ; 197D   004C
.EXEC.97E:
        SLL     R0,     1                       ; 197E   0048
.EXEC.97F:
        ADDI    #$0080, R0                      ; 197F   02F8 0080
.EXEC.981:
        ADDI    #$0002, R5                      ; 1981   02FD 0002
.EXEC.983:
        SDBD                                    ; 1983   0001
.EXEC.984:
        XOR@    R5,     R0                      ; 1984   03E8
.EXEC.985:
        MVI@    R1,     R3                      ; 1985   028B
.EXEC.986:
        MVO@    R0,     R1                      ; 1986   0248
.EXEC.987:
        MOVR    R3,     R0                      ; 1987   0098
.EXEC.988:
        DECR    R1                              ; 1988   0011
.EXEC.989:
        DECR    R2                              ; 1989   0012
.EXEC.98A:
        BNEQ    .EXEC.985                       ; 198A   022C 0006

.EXEC.98C:
        PULR    R7                              ; 198C   02B7
.EXEC.98D:
        PSHR    R5                              ; 198D   0275

.EXEC.98E:
        JSR     R5,     .EXEC.76C               ; 198E   0004 0114 036C

.EXEC.991:
        INCR    R7                              ; 1991   000F
.EXEC.992:
        PSHR    R5                              ; 1992   0275

.EXEC.993:
        JSR     R5,     .EXEC.766               ; 1993   0004 0114 0366

.EXEC.996:
        PSHR    R1                              ; 1996   0271
.EXEC.997:
        ADDI    #$0006, R1                      ; 1997   02F9 0006
.EXEC.999:
        CLRR    R5                              ; 1999   01ED
.EXEC.99A:
        MVO@    R5,     R1                      ; 199A   024D
.EXEC.99B:
        MOVR    R0,     R1                      ; 199B   0081
.EXEC.99C:
        ADDI    #$013B, R1                      ; 199C   02F9 013B
.EXEC.99E:
        MVO@    R5,     R1                      ; 199E   024D
.EXEC.99F:
        PULR    R1                              ; 199F   02B1
.EXEC.9A0:
        PULR    R7                              ; 19A0   02B7
.EXEC.9A1:
        SETC                                    ; 19A1   0007
.EXEC.9A2:
        INCR    R7                              ; 19A2   000F
.EXEC.9A3:
        CLRC                                    ; 19A3   0006
.EXEC.9A4:
        RLC     R3,     1                       ; 19A4   0053
.EXEC.9A5:
        PSHR    R5                              ; 19A5   0275
.EXEC.9A6:
        B       .EXEC.9C1                       ; 19A6   0200 0019

.EXEC.9A8:
        PSHR    R5                              ; 19A8   0275

.EXEC.9A9:
        JSR     R5,     .EXEC.766               ; 19A9   0004 0114 0366

.EXEC.9AC:
        INCR    R7                              ; 19AC   000F
.EXEC.9AD:
        PSHR    R5                              ; 19AD   0275

.EXEC.9AE:
        JSR     R5,     .EXEC.76C               ; 19AE   0004 0114 036C

.EXEC.9B1:
        MOVR    R0,     R5                      ; 19B1   0085
.EXEC.9B2:
        ADDI    #$013B, R5                      ; 19B2   02FD 013B
.EXEC.9B4:
        MVO@    R3,     R5                      ; 19B4   026B
.EXEC.9B5:
        ADDI    #$0007, R1                      ; 19B5   02F9 0007
.EXEC.9B7:
        MVO@    R2,     R1                      ; 19B7   024A
.EXEC.9B8:
        PULR    R5                              ; 19B8   02B5
.EXEC.9B9:
        SETC                                    ; 19B9   0007
.EXEC.9BA:
        INCR    R7                              ; 19BA   000F
.EXEC.9BB:
        CLRC                                    ; 19BB   0006
.EXEC.9BC:
        PSHR    R5                              ; 19BC   0275
.EXEC.9BD:
        RLC     R3,     1                       ; 19BD   0053

.EXEC.9BE:
        JSR     R5,     .EXEC.76C               ; 19BE   0004 0114 036C
.EXEC.9C1:
        JSR     R5,     .EXEC.7C1               ; 19C1   0004 0114 03C1

.EXEC.9C4:
        ADDI    #$0002, R1                      ; 19C4   02F9 0002
.EXEC.9C6:
        MOVR    R1,     R4                      ; 19C6   008C
.EXEC.9C7:
        PSHR    R4                              ; 19C7   0274
.EXEC.9C8:
        PSHR    R3                              ; 19C8   0273
.EXEC.9C9:
        MOVR    R2,     R3                      ; 19C9   0093
.EXEC.9CA:
        ANDI    #$00FF, R3                      ; 19CA   03BB 00FF
.EXEC.9CC:
        XORR    R3,     R2                      ; 19CC   01DA
.EXEC.9CD:
        SWAP    R2,     1                       ; 19CD   0042

.EXEC.9CE:
        JSR     R5,     .EXEC.7A3               ; 19CE   0004 0114 03A3

.EXEC.9D1:
        PULR    R1                              ; 19D1   02B1
.EXEC.9D2:
        MOVR    R3,     R0                      ; 19D2   0098
.EXEC.9D3:
        BPL     .EXEC.9D6                       ; 19D3   0203 0001

.EXEC.9D5:
        NEGR    R3                              ; 19D5   0023
.EXEC.9D6:
        ADDR    R3,     R3                      ; 19D6   00DB
.EXEC.9D7:
        SARC    R1,     1                       ; 19D7   0079
.EXEC.9D8:
        SLL     R1,     1                       ; 19D8   0049
.EXEC.9D9:
        RLC     R3,     1                       ; 19D9   0053
.EXEC.9DA:
        PSHR    R3                              ; 19DA   0273
.EXEC.9DB:
        PSHR    R1                              ; 19DB   0271
.EXEC.9DC:
        MOVR    R2,     R3                      ; 19DC   0093

.EXEC.9DD:
        JSR     R5,     X_MPY                   ; 19DD   0004 011C 01DC

.EXEC.9E0:
        PULR    R1                              ; 19E0   02B1
.EXEC.9E1:
        PULR    R5                              ; 19E1   02B5
.EXEC.9E2:
        MOVR    R4,     R0                      ; 19E2   00A0
.EXEC.9E3:
        BPL     .EXEC.9E6                       ; 19E3   0203 0001

.EXEC.9E5:
        NEGR    R4                              ; 19E5   0024
.EXEC.9E6:
        ADDR    R4,     R4                      ; 19E6   00E4
.EXEC.9E7:
        ADDR    R4,     R4                      ; 19E7   00E4
.EXEC.9E8:
        CMPR    R5,     R4                      ; 19E8   016C
.EXEC.9E9:
        BLT     .EXEC.9F0                       ; 19E9   0205 0005

.EXEC.9EB:
        ANDI    #$0001, R5                      ; 19EB   03BD 0001
.EXEC.9ED:
        XORR    R4,     R5                      ; 19ED   01E5
.EXEC.9EE:
        XORI    #$0002, R5                      ; 19EE   03FD 0002
.EXEC.9F0:
        PSHR    R5                              ; 19F0   0275
.EXEC.9F1:
        MOVR    R2,     R4                      ; 19F1   0094

.EXEC.9F2:
        JSR     R5,     X_MPY                   ; 19F2   0004 011C 01DC

.EXEC.9F5:
        MOVR    R2,     R1                      ; 19F5   0091
.EXEC.9F6:
        MOVR    R3,     R2                      ; 19F6   009A

.EXEC.9F7:
        JSR     R5,     X_DIVR                  ; 19F7   0004 011C 01F8

.EXEC.9FA:
        MOVR    R3,     R2                      ; 19FA   009A
.EXEC.9FB:
        MOVR    R0,     R3                      ; 19FB   0083
.EXEC.9FC:
        MOVR    R4,     R1                      ; 19FC   00A1

.EXEC.9FD:
        JSR     R5,     X_DIVR                  ; 19FD   0004 011C 01F8

.EXEC.A00:
        ANDI    #$00FF, R3                      ; 1A00   03BB 00FF
.EXEC.A02:
        ANDI    #$00FF, R0                      ; 1A02   03B8 00FF
.EXEC.A04:
        SWAP    R0,     1                       ; 1A04   0040
.EXEC.A05:
        XORR    R3,     R0                      ; 1A05   01D8
.EXEC.A06:
        PULR    R3                              ; 1A06   02B3
.EXEC.A07:
        PULR    R4                              ; 1A07   02B4
.EXEC.A08:
        ADDI    #$0002, R4                      ; 1A08   02FC 0002
.EXEC.A0A:
        MVO@    R0,     R4                      ; 1A0A   0260
.EXEC.A0B:
        SARC    R3,     1                       ; 1A0B   007B
.EXEC.A0C:
        BNC     .EXEC.9A0                       ; 1A0C   0229 006D

.EXEC.A0E:
        CLRR    R1                              ; 1A0E   01C9
.EXEC.A0F:
        CLRR    R2                              ; 1A0F   01D2

.EXEC.A10:
        JSR     R5,     .EXEC.477               ; 1A10   0004 0114 0077

.EXEC.A13:
        SARC    R3,     1                       ; 1A13   007B
.EXEC.A14:
        BC      .EXEC.A17                       ; 1A14   0201 0001

.EXEC.A16:
        MOVR    R1,     R2                      ; 1A16   008A
.EXEC.A17:
        TSTR    R2                              ; 1A17   0092
.EXEC.A18:
        BPL     .EXEC.A1B                       ; 1A18   0203 0001

.EXEC.A1A:
        NEGR    R2                              ; 1A1A   0022
.EXEC.A1B:
        MOVR    R3,     R1                      ; 1A1B   0099
.EXEC.A1C:
        SWAP    R1,     1                       ; 1A1C   0041
.EXEC.A1D:
        SLR     R1,     1                       ; 1A1D   0061
.EXEC.A1E:
        SLR     R2,     1                       ; 1A1E   0062

.EXEC.A1F:
        JSR     R5,     X_DIVR                  ; 1A1F   0004 011C 01F8

.EXEC.A22:
        TSTR    R0                              ; 1A22   0080
.EXEC.A23:
        BNEQ    .EXEC.A28                       ; 1A23   020C 0003

.EXEC.A25:
        DECR    R4                              ; 1A25   0014
.EXEC.A26:
        MVO@    R0,     R4                      ; 1A26   0260
.EXEC.A27:
        INCR    R0                              ; 1A27   0008
.EXEC.A28:
        INCR    R4                              ; 1A28   000C
.EXEC.A29:
        MVO@    R0,     R4                      ; 1A29   0260
.EXEC.A2A:
        MOVR    R4,     R1                      ; 1A2A   00A1

.EXEC.A2B:
        JSR     R5,     .EXEC.766               ; 1A2B   0004 0114 0366

.EXEC.A2E:
        PULR    R7                              ; 1A2E   02B7
.EXEC.A2F:
        PSHR    R5                              ; 1A2F   0275
.EXEC.A30:
        PSHR    R2                              ; 1A30   0272
.EXEC.A31:
        CLRR    R5                              ; 1A31   01ED
.EXEC.A32:
        NEGR    R1                              ; 1A32   0021
.EXEC.A33:
        BGE     .EXEC.A39                       ; 1A33   020D 0004

.EXEC.A35:
        ADDI    #$0008, R5                      ; 1A35   02FD 0008
.EXEC.A37:
        NEGR    R0                              ; 1A37   0020
.EXEC.A38:
        NEGR    R1                              ; 1A38   0021
.EXEC.A39:
        TSTR    R0                              ; 1A39   0080
.EXEC.A3A:
        BGE     .EXEC.A42                       ; 1A3A   020D 0006

.EXEC.A3C:
        MOVR    R1,     R2                      ; 1A3C   008A
.EXEC.A3D:
        NEGR    R0                              ; 1A3D   0020
.EXEC.A3E:
        MOVR    R0,     R1                      ; 1A3E   0081
.EXEC.A3F:
        MOVR    R2,     R0                      ; 1A3F   0090
.EXEC.A40:
        ADDI    #$0004, R5                      ; 1A40   02FD 0004
.EXEC.A42:
        MOVR    R1,     R2                      ; 1A42   008A
.EXEC.A43:
        SLL     R2,     2                       ; 1A43   004E
.EXEC.A44:
        CMPR    R2,     R0                      ; 1A44   0150
.EXEC.A45:
        BGT     .EXEC.A59                       ; 1A45   020E 0012

.EXEC.A47:
        INCR    R5                              ; 1A47   000D
.EXEC.A48:
        MOVR    R0,     R2                      ; 1A48   0082
.EXEC.A49:
        SUBR    R1,     R2                      ; 1A49   010A
.EXEC.A4A:
        SLL     R2,     2                       ; 1A4A   004E
.EXEC.A4B:
        CMPR    R2,     R0                      ; 1A4B   0150
.EXEC.A4C:
        BLE     .EXEC.A59                       ; 1A4C   0206 000B

.EXEC.A4E:
        INCR    R5                              ; 1A4E   000D
.EXEC.A4F:
        NEGR    R2                              ; 1A4F   0022
.EXEC.A50:
        CMPR    R2,     R1                      ; 1A50   0151
.EXEC.A51:
        BGT     .EXEC.A59                       ; 1A51   020E 0006

.EXEC.A53:
        INCR    R5                              ; 1A53   000D
.EXEC.A54:
        SLL     R0,     2                       ; 1A54   004C
.EXEC.A55:
        CMPR    R0,     R1                      ; 1A55   0141
.EXEC.A56:
        BLE     .EXEC.A59                       ; 1A56   0206 0001

.EXEC.A58:
        INCR    R5                              ; 1A58   000D
.EXEC.A59:
        MOVR    R5,     R1                      ; 1A59   00A9
.EXEC.A5A:
        ANDI    #$000F, R1                      ; 1A5A   03B9 000F
.EXEC.A5C:
        PULR    R2                              ; 1A5C   02B2
.EXEC.A5D:
        PULR    R7                              ; 1A5D   02B7
.EXEC.A5E:
        PSHR    R5                              ; 1A5E   0275
.EXEC.A5F:
        MOVR    R1,     R5                      ; 1A5F   008D
.EXEC.A60:
        INCR    R7                              ; 1A60   000F
.EXEC.A61:
        MVI@    R5,     R0                      ; 1A61   02A8
.EXEC.A62:
        MVO     R5,     G_0143                  ; 1A62   0245 0143
.EXEC.A64:
        MOVR    R5,     R1                      ; 1A64   00A9
.EXEC.A65:
        SWAP    R1,     1                       ; 1A65   0041
.EXEC.A66:
        MVO     R1,     G_0144                  ; 1A66   0241 0144

.EXEC.A68:
        JSR     R5,     X_READ_ROM_HDR          ; 1A68   0004 0110 00AB

.EXEC.A6B:
        EIS                                     ; 1A6B   0002
.EXEC.A6C:
        MOVR    R5,     R1                      ; 1A6C   00A9
.EXEC.A6D:
        PULR    R5                              ; 1A6D   02B5
.EXEC.A6E:
        J       .EXEC.831                       ; 1A6E   0004 0318 0031

.EXEC.A71:
        PSHR    R5                              ; 1A71   0275
.EXEC.A72:
        MVII    #$0143, R5                      ; 1A72   02BD 0143
.EXEC.A74:
        SDBD                                    ; 1A74   0001
.EXEC.A75:
        MVI@    R5,     R7                      ; 1A75   02AF
.EXEC.A76:
        CMP     G_0146, R3                      ; 1A76   0343 0146
.EXEC.A78:
        BLT     .EXEC.A93                       ; 1A78   0205 0019
.EXEC.A7A:
        BGT     .EXEC.A80                       ; 1A7A   020E 0004

.EXEC.A7C:
        RRC     R3,     1                       ; 1A7C   0073
.EXEC.A7D:
        BC      .EXEC.A93                       ; 1A7D   0201 0014

.EXEC.A7F:
        RLC     R3,     1                       ; 1A7F   0053
.EXEC.A80:
        MVO     R3,     G_0146                  ; 1A80   0243 0146
.EXEC.A82:
        MOVR    R4,     R7                      ; 1A82   00A7
.EXEC.A83:
        PSHR    R5                              ; 1A83   0275
.EXEC.A84:
        PSHR    R0                              ; 1A84   0270
.EXEC.A85:
        PSHR    R1                              ; 1A85   0271
.EXEC.A86:
        MVII    #$01F0, R4                      ; 1A86   02BC 01F0
.EXEC.A88:
        MVII    #$000E, R0                      ; 1A88   02B8 000E

.EXEC.A8A:
        JSR     R5,     X_FILL_ZERO             ; 1A8A   0004 0114 0338

.EXEC.A8D:
        MVII    #$0038, R0                      ; 1A8D   02B8 0038
.EXEC.A8F:
        MVO     R0,     .PSG0.chan_enable       ; 1A8F   0240 01F8
.EXEC.A91:
        PULR    R1                              ; 1A91   02B1
.EXEC.A92:
        PULR    R0                              ; 1A92   02B0
.EXEC.A93:
        PULR    R7                              ; 1A93   02B7
.EXEC.A94:
        MVII    #$0002, R4                      ; 1A94   02BC 0002
.EXEC.A96:
        MVO     R4,     G_0148                  ; 1A96   0244 0148
.EXEC.A98:
        MVO     R5,     G_035F                  ; 1A98   0245 035F

.EXEC.A9A:
        JSR     R5,     .EXEC.A83               ; 1A9A   0004 0118 0283

.EXEC.A9D:
        MVO     R0,     G_0149                  ; 1A9D   0240 0149
.EXEC.A9F:
        CLRR    R0                              ; 1A9F   01C0
.EXEC.AA0:
        MVO     R0,     G_0145                  ; 1AA0   0240 0145
.EXEC.AA2:
        PULR    R7                              ; 1AA2   02B7
.EXEC.AA3:
        SUBI    #$0003, R6                      ; 1AA3   033E 0003

.EXEC.AA5:
        JSR     R5,     .EXEC.A83               ; 1AA5   0004 0118 0283

X_HUSH:
        MVII    #$00FF, R0                      ; 1AA8   02B8 00FF
.EXEC.AAA:
        MVO     R0,     G_0145                  ; 1AAA   0240 0145
.EXEC.AAC:
        PULR    R7                              ; 1AAC   02B7
.EXEC.AAD:
        MVI     G_0145, R0                      ; 1AAD   0280 0145
.EXEC.AAF:
        DECR    R0                              ; 1AAF   0010
.EXEC.AB0:
        BMI     .EXEC.ABC                       ; 1AB0   020B 000A

.EXEC.AB2:
        PSHR    R5                              ; 1AB2   0275
.EXEC.AB3:
        CLRR    R0                              ; 1AB3   01C0
.EXEC.AB4:
        MVO     R0,     G_0145                  ; 1AB4   0240 0145
.EXEC.AB6:
        MVO     R0,     G_0149                  ; 1AB6   0240 0149
.EXEC.AB8:
        MVO     R0,     G_0146                  ; 1AB8   0240 0146
.EXEC.ABA:
        MVI     G_035F, R7                      ; 1ABA   0287 035F
.EXEC.ABC:
        MOVR    R5,     R7                      ; 1ABC   00AF
X_PLAY_NOTE:
        MVII    #$0148, R1                      ; 1ABD   02B9 0148
.EXEC.ABF:
        MVI@    R1,     R0                      ; 1ABF   0288
.EXEC.AC0:
        DECR    R0                              ; 1AC0   0010
.EXEC.AC1:
        MVO@    R0,     R1                      ; 1AC1   0248
.EXEC.AC2:
        BNEQ    .EXEC.ABC                       ; 1AC2   022C 0007

.EXEC.AC4:
        MVI     G_0147, R2                      ; 1AC4   0282 0147
.EXEC.AC6:
        MVO@    R2,     R1                      ; 1AC6   024A
.EXEC.AC7:
        XOR     G_0145, R0                      ; 1AC7   03C0 0145
.EXEC.AC9:
        BNEQ    .EXEC.ABC                       ; 1AC9   022C 000E

.EXEC.ACB:
        PSHR    R5                              ; 1ACB   0275
.EXEC.ACC:
        ADD     G_0149, R7                      ; 1ACC   02C7 0149
.EXEC.ACE:
        MVO@    R0,     R1                      ; 1ACE   0248
.EXEC.ACF:
        PULR    R7                              ; 1ACF   02B7
.EXEC.AD0:
        B       .EXEC.B2B                       ; 1AD0   0200 0059
.EXEC.AD2:
        B       .EXEC.B52                       ; 1AD2   0200 007E
.EXEC.AD4:
        B       .EXEC.B61                       ; 1AD4   0200 008B
.EXEC.AD6:
        B       .EXEC.B72                       ; 1AD6   0200 009A
.EXEC.AD8:
        B       .EXEC.B99                       ; 1AD8   0200 00BF
.EXEC.ADA:
        B       .EXEC.BFE                       ; 1ADA   0200 0122

.EXEC.ADC:
        SLLC    R1,     2                       ; 1ADC   005D
.EXEC.ADD:
        INCR    R5                              ; 1ADD   000D
.EXEC.ADE:
        MOVR    R3,     R4                      ; 1ADE   009C
.EXEC.ADF:
        INCR    R4                              ; 1ADF   000C
.EXEC.AE0:
        ADDR    R4,     R7                      ; 1AE0   00E7
.EXEC.AE1:
        INCR    R3                              ; 1AE1   000B
.EXEC.AE2:
        RSWD    R4                              ; 1AE2   003C
.EXEC.AE3:
        INCR    R3                              ; 1AE3   000B
.EXEC.AE4:
        TSTR    R3                              ; 1AE4   009B
.EXEC.AE5:
        INCR    R2                              ; 1AE5   000A
.EXEC.AE6:
        DIS                                     ; 1AE6   0003
.EXEC.AE7:
        INCR    R2                              ; 1AE7   000A
.EXEC.AE8:
        RRC     R2,     1                       ; 1AE8   0072
.EXEC.AE9:
        INCR    R1                              ; 1AE9   0009
.EXEC.AEA:
        ADDR    R5,     R3                      ; 1AEA   00EB
.EXEC.AEB:
        INCR    R0                              ; 1AEB   0008
.EXEC.AEC:
        SAR     R3,     1                       ; 1AEC   006B
.EXEC.AED:
        INCR    R0                              ; 1AED   0008
.EXEC.AEE:
        ADDR    R6,     R2                      ; 1AEE   00F2
.EXEC.AEF:
        SETC                                    ; 1AEF   0007
.EXEC.AF0:
        SARC    R3,     2                       ; 1AF0   007F
.EXEC.AF1:
        SETC                                    ; 1AF1   0007
.EXEC.AF2:
        DECR    R4                              ; 1AF2   0014
.EXEC.AF3:
        SETC                                    ; 1AF3   0007
.EXEC.AF4:
        PSHR    R5                              ; 1AF4   0275
.EXEC.AF5:
        PSHR    R3                              ; 1AF5   0273
.EXEC.AF6:
        PSHR    R4                              ; 1AF6   0274
.EXEC.AF7:
        CLRR    R1                              ; 1AF7   01C9
.EXEC.AF8:
        MVI     G_035F, R5                      ; 1AF8   0285 035F
.EXEC.AFA:
        MVI@    R5,     R3                      ; 1AFA   02AB
.EXEC.AFB:
        MVO     R5,     G_035F                  ; 1AFB   0245 035F
.EXEC.AFD:
        TSTR    R3                              ; 1AFD   009B
.EXEC.AFE:
        BEQ     .EXEC.AA3                       ; 1AFE   0224 005C

.EXEC.B00:
        SARC    R3,     2                       ; 1B00   007F
.EXEC.B01:
        RLC     R1,     2                       ; 1B01   0055
.EXEC.B02:
        SARC    R3,     1                       ; 1B02   007B
.EXEC.B03:
        RLC     R1,     1                       ; 1B03   0051
.EXEC.B04:
        CLRR    R2                              ; 1B04   01D2
.EXEC.B05:
        SARC    R3,     1                       ; 1B05   007B
.EXEC.B06:
        RLC     R2,     1                       ; 1B06   0052
.EXEC.B07:
        CMPI    #$003F, R3                      ; 1B07   037B 003F
.EXEC.B09:
        BEQ     .EXEC.AF8                       ; 1B09   0224 0012

.EXEC.B0B:
        INCR    R1                              ; 1B0B   0009
.EXEC.B0C:
        SLL     R1,     2                       ; 1B0C   004D
.EXEC.B0D:
        MOVR    R3,     R0                      ; 1B0D   0098
.EXEC.B0E:
        BEQ     .EXEC.B24                       ; 1B0E   0204 0014

.EXEC.B10:
        CLRR    R4                              ; 1B10   01E4
.EXEC.B11:
        MVII    #$000C, R5                      ; 1B11   02BD 000C
.EXEC.B13:
        INCR    R4                              ; 1B13   000C
.EXEC.B14:
        SUBR    R5,     R3                      ; 1B14   012B
.EXEC.B15:
        BPL     .EXEC.B13                       ; 1B15   0223 0003

.EXEC.B17:
        ADDR    R3,     R5                      ; 1B17   00DD
.EXEC.B18:
        ADDR    R5,     R5                      ; 1B18   00ED
.EXEC.B19:
        ADDR    R7,     R5                      ; 1B19   00FD
.EXEC.B1A:
        SUBI    #$003E, R5                      ; 1B1A   033D 003E
.EXEC.B1C:
        SDBD                                    ; 1B1C   0001
.EXEC.B1D:
        MVI@    R5,     R0                      ; 1B1D   02A8
.EXEC.B1E:
        SLR     R0,     1                       ; 1B1E   0060
.EXEC.B1F:
        DECR    R4                              ; 1B1F   0014
.EXEC.B20:
        BNEQ    .EXEC.B1E                       ; 1B20   022C 0003

.EXEC.B22:
        INCR    R0                              ; 1B22   0008
.EXEC.B23:
        SLR     R0,     1                       ; 1B23   0060
.EXEC.B24:
        PULR    R4                              ; 1B24   02B4
.EXEC.B25:
        PULR    R3                              ; 1B25   02B3
.EXEC.B26:
        PULR    R7                              ; 1B26   02B7
X_PLAY_MUS1:
        MVII    #$0002, R0                      ; 1B27   02B8 0002
.EXEC.B29:
        B       .EXEC.A94                       ; 1B29   0220 0096

.EXEC.B2B:
        JSR     R5,     .EXEC.AF4               ; 1B2B   0004 0118 02F4

.EXEC.B2E:
        TSTR    R2                              ; 1B2E   0092
.EXEC.B2F:
        BEQ     .EXEC.B37                       ; 1B2F   0204 0006

.EXEC.B31:
        SUBI    #$0002, R1                      ; 1B31   0339 0002
.EXEC.B33:
        MVII    #$0004, R5                      ; 1B33   02BD 0004
.EXEC.B35:
        MVO     R5,     G_0149                  ; 1B35   0245 0149

.EXEC.B37:
        JSR     R5,     .EXEC.BAE               ; 1B37   0004 0118 03AE

.EXEC.B3A:
        MVII    #$01F0, R5                      ; 1B3A   02BD 01F0
.EXEC.B3C:
        MVO@    R0,     R5                      ; 1B3C   0268
.EXEC.B3D:
        MVO@    R0,     R5                      ; 1B3D   0268
.EXEC.B3E:
        MVO@    R0,     R5                      ; 1B3E   0268
.EXEC.B3F:
        CLRR    R2                              ; 1B3F   01D2
.EXEC.B40:
        MVO@    R2,     R5                      ; 1B40   026A
.EXEC.B41:
        SWAP    R0,     1                       ; 1B41   0040
.EXEC.B42:
        MVO@    R0,     R5                      ; 1B42   0268
.EXEC.B43:
        MVO@    R0,     R5                      ; 1B43   0268
.EXEC.B44:
        MVO@    R0,     R5                      ; 1B44   0268
.EXEC.B45:
        CLRR    R2                              ; 1B45   01D2
.EXEC.B46:
        MVO@    R2,     R5                      ; 1B46   026A
.EXEC.B47:
        ADDI    #$0003, R5                      ; 1B47   02FD 0003
.EXEC.B49:
        TSTR    R0                              ; 1B49   0080
.EXEC.B4A:
        BEQ     .EXEC.B4E                       ; 1B4A   0204 0002

.EXEC.B4C:
        MVII    #$000F, R0                      ; 1B4C   02B8 000F
.EXEC.B4E:
        MVO@    R0,     R5                      ; 1B4E   0268
.EXEC.B4F:
        MVO@    R0,     R5                      ; 1B4F   0268
.EXEC.B50:
        MVO@    R0,     R5                      ; 1B50   0268
.EXEC.B51:
        PULR    R7                              ; 1B51   02B7

.EXEC.B52:
        JSR     R5,     .EXEC.A83               ; 1B52   0004 0118 0283

.EXEC.B55:
        MVII    #$0002, R1                      ; 1B55   02B9 0002

.EXEC.B57:
        JSR     R5,     .EXEC.BAE               ; 1B57   0004 0118 03AE

.EXEC.B5A:
        MVO     R1,     G_0149                  ; 1B5A   0241 0149
.EXEC.B5C:
        PULR    R7                              ; 1B5C   02B7
X_PLAY_MUS2:
        MVII    #$0006, R0                      ; 1B5D   02B8 0006
.EXEC.B5F:
        B       .EXEC.A94                       ; 1B5F   0220 00CC

.EXEC.B61:
        JSR     R5,     .EXEC.AF4               ; 1B61   0004 0118 02F4

.EXEC.B64:
        TSTR    R2                              ; 1B64   0092
.EXEC.B65:
        BEQ     .EXEC.B6D                       ; 1B65   0204 0006

.EXEC.B67:
        SUBI    #$0002, R1                      ; 1B67   0339 0002
.EXEC.B69:
        MVII    #$0008, R5                      ; 1B69   02BD 0008
.EXEC.B6B:
        MVO     R5,     G_0149                  ; 1B6B   0245 0149

.EXEC.B6D:
        JSR     R5,     .EXEC.B7F               ; 1B6D   0004 0118 037F

.EXEC.B70:
        B       .EXEC.B45                       ; 1B70   0220 002C

.EXEC.B72:
        JSR     R5,     .EXEC.A83               ; 1B72   0004 0118 0283

.EXEC.B75:
        MVII    #$0002, R1                      ; 1B75   02B9 0002

.EXEC.B77:
        JSR     R5,     .EXEC.BAE               ; 1B77   0004 0118 03AE

.EXEC.B7A:
        MVII    #$0006, R1                      ; 1B7A   02B9 0006
.EXEC.B7C:
        MVO     R1,     G_0149                  ; 1B7C   0241 0149
.EXEC.B7E:
        PULR    R7                              ; 1B7E   02B7
.EXEC.B7F:
        PSHR    R5                              ; 1B7F   0275

.EXEC.B80:
        JSR     R5,     .EXEC.BAE               ; 1B80   0004 0118 03AE

.EXEC.B83:
        MVII    #$01F0, R5                      ; 1B83   02BD 01F0
.EXEC.B85:
        MVO@    R0,     R5                      ; 1B85   0268
.EXEC.B86:
        SLR     R0,     1                       ; 1B86   0060
.EXEC.B87:
        MVO@    R0,     R5                      ; 1B87   0268
.EXEC.B88:
        SLR     R0,     1                       ; 1B88   0060
.EXEC.B89:
        MVO@    R0,     R5                      ; 1B89   0268
.EXEC.B8A:
        CLRR    R2                              ; 1B8A   01D2
.EXEC.B8B:
        MVO@    R2,     R5                      ; 1B8B   026A
.EXEC.B8C:
        SLL     R0,     2                       ; 1B8C   004C
.EXEC.B8D:
        SWAP    R0,     1                       ; 1B8D   0040
.EXEC.B8E:
        MVO@    R0,     R5                      ; 1B8E   0268
.EXEC.B8F:
        NOP                                     ; 1B8F   0034
.EXEC.B90:
        SLR     R0,     1                       ; 1B90   0060
.EXEC.B91:
        MVO@    R0,     R5                      ; 1B91   0268
.EXEC.B92:
        SLR     R0,     1                       ; 1B92   0060
.EXEC.B93:
        MVO@    R0,     R5                      ; 1B93   0268
.EXEC.B94:
        PULR    R7                              ; 1B94   02B7
X_PLAY_MUS3:
        MVII    #$000A, R0                      ; 1B95   02B8 000A
.EXEC.B97:
        B       .EXEC.A94                       ; 1B97   0220 0104

.EXEC.B99:
        JSR     R5,     .EXEC.AF4               ; 1B99   0004 0118 02F4
.EXEC.B9C:
        JSR     R5,     .EXEC.B7F               ; 1B9C   0004 0118 037F

.EXEC.B9F:
        MVII    #$0020, R1                      ; 1B9F   02B9 0020
.EXEC.BA1:
        MVO@    R1,     R5                      ; 1BA1   0269
.EXEC.BA2:
        ADDI    #$0002, R5                      ; 1BA2   02FD 0002
.EXEC.BA4:
        MVO@    R2,     R5                      ; 1BA4   026A
.EXEC.BA5:
        TSTR    R0                              ; 1BA5   0080
.EXEC.BA6:
        BEQ     .EXEC.BAA                       ; 1BA6   0204 0002

.EXEC.BA8:
        MVII    #$003F, R0                      ; 1BA8   02B8 003F
.EXEC.BAA:
        MVO@    R0,     R5                      ; 1BAA   0268
.EXEC.BAB:
        MVO@    R0,     R5                      ; 1BAB   0268
.EXEC.BAC:
        MVO@    R0,     R5                      ; 1BAC   0268
.EXEC.BAD:
        PULR    R7                              ; 1BAD   02B7
.EXEC.BAE:
        PSHR    R5                              ; 1BAE   0275
.EXEC.BAF:
        PSHR    R0                              ; 1BAF   0270
.EXEC.BB0:
        MVI     G_0147, R5                      ; 1BB0   0285 0147
.EXEC.BB2:
        CLRR    R0                              ; 1BB2   01C0
.EXEC.BB3:
        ADDR    R1,     R0                      ; 1BB3   00C8
.EXEC.BB4:
        DECR    R5                              ; 1BB4   0015
.EXEC.BB5:
        BNEQ    .EXEC.BB3                       ; 1BB5   022C 0003

.EXEC.BB7:
        MVO     R0,     G_0148                  ; 1BB7   0240 0148
.EXEC.BB9:
        PULR    R0                              ; 1BB9   02B0
.EXEC.BBA:
        PULR    R7                              ; 1BBA   02B7
X_PLAY_SFX1:
        MVII    #$0080, R3                      ; 1BBB   02BB 0080
.EXEC.BBD:
        INCR    R7                              ; 1BBD   000F
X_PLAY_SFX2:
        MVI@    R5,     R3                      ; 1BBE   02AB

.EXEC.BBF:
        JSR     R4,     .EXEC.A76               ; 1BBF   0004 0018 0276

.EXEC.BC2:
        MVII    #$0002, R4                      ; 1BC2   02BC 0002
.EXEC.BC4:
        MVO     R4,     G_0148                  ; 1BC4   0244 0148
.EXEC.BC6:
        MVO     R5,     G_035F                  ; 1BC6   0245 035F
.EXEC.BC8:
        DECR    R4                              ; 1BC8   0014
.EXEC.BC9:
        MVO     R0,     G_0159                  ; 1BC9   0240 0159
.EXEC.BCB:
        MVO     R4,     G_014A                  ; 1BCB   0244 014A
.EXEC.BCD:
        MVII    #$000A, R0                      ; 1BCD   02B8 000A
.EXEC.BCF:
        MVII    #$014B, R4                      ; 1BCF   02BC 014B

.EXEC.BD1:
        JSR     R5,     X_FILL_ZERO             ; 1BD1   0004 0114 0338

.EXEC.BD4:
        MVII    #$000C, R0                      ; 1BD4   02B8 000C
.EXEC.BD6:
        B       .EXEC.A9D                       ; 1BD6   0220 013A

.EXEC.BD8:
        HLT                                     ; 1BD8   0000
.EXEC.BD9:
        EIS                                     ; 1BD9   0002
.EXEC.BDA:
        DECLE   $0004                           ; 1BDA   0004
.EXEC.BDB:
        INCR    R3                              ; 1BDB   000B
.EXEC.BDC:
        COMR    R2                              ; 1BDC   001A
.EXEC.BDD:
        RSWD    R3                              ; 1BDD   003B
.EXEC.BDE:
        SARC    R0,     1                       ; 1BDE   0078
.EXEC.BDF:
        ADDR    R6,     R5                      ; 1BDF   00F5
.EXEC.BE0:
        SETC                                    ; 1BE0   0007
.EXEC.BE1:
        HLT                                     ; 1BE1   0000
.EXEC.BE2:
        SETC                                    ; 1BE2   0007
.EXEC.BE3:
        INCR    R1                              ; 1BE3   0009
.EXEC.BE4:
        INCR    R4                              ; 1BE4   000C
.EXEC.BE5:
        DECR    R2                              ; 1BE5   0012
.EXEC.BE6:
        DECR    R3                              ; 1BE6   0013
.EXEC.BE7:
        HLT                                     ; 1BE7   0000
.EXEC.BE8:
        SUBR    R2,     R0                      ; 1BE8   0110
.EXEC.BE9:
        ADCR    R7                              ; 1BE9   002F
.EXEC.BEA:
        TSTR    R4                              ; 1BEA   00A4
.EXEC.BEB:
        ADDR    R5,     R0                      ; 1BEB   00E8
.EXEC.BEC:
        ADDR    R0,     R4                      ; 1BEC   00C4
.EXEC.BED:
        SUBR    R6,     R7                      ; 1BED   0137
.EXEC.BEE:
        CMPR    R1,     R5                      ; 1BEE   014D
.EXEC.BEF:
        CMPR    R5,     R6                      ; 1BEF   016E
.EXEC.BF0:
        ADDR    R0,     R1                      ; 1BF0   00C1
.EXEC.BF1:
        CMPR    R0,     R3                      ; 1BF1   0143
.EXEC.BF2:
        SWAP    R3,     1                       ; 1BF2   0043
.EXEC.BF3:
        RRC     R2,     2                       ; 1BF3   0076
.EXEC.BF4:
        ADDR    R1,     R7                      ; 1BF4   00CF
.EXEC.BF5:
        ADDR    R3,     R5                      ; 1BF5   00DD
.EXEC.BF6:
        CMPR    R4,     R2                      ; 1BF6   0162
.EXEC.BF7:
        MOVR    R6,     R0                      ; 1BF7   00B0
.EXEC.BF8:
        SUBR    R4,     R7                      ; 1BF8   0127
.EXEC.BF9:
        ADDR    R1,     R3                      ; 1BF9   00CB
.EXEC.BFA:
        CMPR    R0,     R2                      ; 1BFA   0142
.EXEC.BFB:
        SUBR    R7,     R4                      ; 1BFB   013C
.EXEC.BFC:
        SUBR    R5,     R1                      ; 1BFC   0129
.EXEC.BFD:
        SUBR    R4,     R3                      ; 1BFD   0123
.EXEC.BFE:
        MVII    #$01F0, R3                      ; 1BFE   02BB 01F0
.EXEC.C00:
        MVII    #$014B, R4                      ; 1C00   02BC 014B
.EXEC.C02:
        MVI@    R4,     R0                      ; 1C02   02A0
.EXEC.C03:
        MVI@    R4,     R1                      ; 1C03   02A1
.EXEC.C04:
        ADDR    R1,     R0                      ; 1C04   00C8
.EXEC.C05:
        NEGR    R1                              ; 1C05   0021
.EXEC.C06:
        DECR    R4                              ; 1C06   0014
.EXEC.C07:
        MVO@    R1,     R4                      ; 1C07   0261

.EXEC.C08:
        JSR     R5,     X_EXT_SIGN_LO           ; 1C08   0004 0114 0268

.EXEC.C0B:
        BEQ     .EXEC.C15                       ; 1C0B   0204 0008

.EXEC.C0D:
        ADD@    R3,     R0                      ; 1C0D   02D8
.EXEC.C0E:
        MVO@    R0,     R3                      ; 1C0E   0258
.EXEC.C0F:
        MOVR    R3,     R2                      ; 1C0F   009A
.EXEC.C10:
        ADDI    #$0004, R2                      ; 1C10   02FA 0004
.EXEC.C12:
        SWAP    R0,     1                       ; 1C12   0040
.EXEC.C13:
        ADD@    R2,     R0                      ; 1C13   02D0
.EXEC.C14:
        MVO@    R0,     R2                      ; 1C14   0250
.EXEC.C15:
        INCR    R3                              ; 1C15   000B
.EXEC.C16:
        CMPI    #$0151, R4                      ; 1C16   037C 0151
.EXEC.C18:
        BNEQ    .EXEC.C02                       ; 1C18   022C 0017

.EXEC.C1A:
        MVII    #$0155, R2                      ; 1C1A   02BA 0155
.EXEC.C1C:
        MVI@    R4,     R0                      ; 1C1C   02A0

.EXEC.C1D:
        JSR     R5,     X_EXT_SIGN_LO           ; 1C1D   0004 0114 0268

.EXEC.C20:
        ADD@    R2,     R0                      ; 1C20   02D0

.EXEC.C21:
        JSR     R5,     X_CLAMP                 ; 1C21   0004 0114 0270
.EXEC.C24:
        DECLE   $0004                           ; 1C24   0004
.EXEC.C25:
        SARC    R3,     2                       ; 1C25   007F
.EXEC.C26:
        MVO@    R0,     R2                      ; 1C26   0250
.EXEC.C27:
        SLR     R0,     2                       ; 1C27   0064
.EXEC.C28:
        ADDI    #$0006, R3                      ; 1C28   02FB 0006
.EXEC.C2A:
        MVO@    R0,     R3                      ; 1C2A   0258
.EXEC.C2B:
        INCR    R3                              ; 1C2B   000B
.EXEC.C2C:
        INCR    R2                              ; 1C2C   000A
.EXEC.C2D:
        INCR    R3                              ; 1C2D   000B
.EXEC.C2E:
        MVI@    R4,     R0                      ; 1C2E   02A0
.EXEC.C2F:
        TSTR    R0                              ; 1C2F   0080
.EXEC.C30:
        BEQ     .EXEC.C39                       ; 1C30   0204 0007

.EXEC.C32:
        ADD@    R2,     R0                      ; 1C32   02D0
.EXEC.C33:
        MVO@    R0,     R2                      ; 1C33   0250
.EXEC.C34:
        SLR     R0,     2                       ; 1C34   0064
.EXEC.C35:
        SLR     R0,     1                       ; 1C35   0060
.EXEC.C36:
        ANDI    #$000F, R0                      ; 1C36   03B8 000F
.EXEC.C38:
        MVO@    R0,     R3                      ; 1C38   0258
.EXEC.C39:
        CMPI    #$0155, R4                      ; 1C39   037C 0155
.EXEC.C3B:
        BNEQ    .EXEC.C2C                       ; 1C3B   022C 0010

.EXEC.C3D:
        MVI     G_014A, R0                      ; 1C3D   0280 014A
.EXEC.C3F:
        DECR    R0                              ; 1C3F   0010
.EXEC.C40:
        MVO     R0,     G_014A                  ; 1C40   0240 014A
.EXEC.C42:
        BNEQ    .EXEC.A93                       ; 1C42   022C 01B0

.EXEC.C44:
        MVI     G_035F, R4                      ; 1C44   0284 035F
.EXEC.C46:
        MOVR    R7,     R5                      ; 1C46   00BD
.EXEC.C47:
        DECR    R5                              ; 1C47   0015
.EXEC.C48:
        PSHR    R5                              ; 1C48   0275
.EXEC.C49:
        MVI@    R4,     R0                      ; 1C49   02A0
.EXEC.C4A:
        CLRR    R1                              ; 1C4A   01C9
.EXEC.C4B:
        SUBI    #$006E, R5                      ; 1C4B   033D 006E
.EXEC.C4D:
        MOVR    R5,     R2                      ; 1C4D   00AA
.EXEC.C4E:
        ADDI    #$0006, R2                      ; 1C4E   02FA 0006
.EXEC.C50:
        INCR    R2                              ; 1C50   000A
.EXEC.C51:
        SARC    R0,     1                       ; 1C51   0078
.EXEC.C52:
        RLC     R1,     1                       ; 1C52   0051
.EXEC.C53:
        CMP@    R5,     R1                      ; 1C53   0369
.EXEC.C54:
        BGE     .EXEC.C50                       ; 1C54   022D 0005

.EXEC.C56:
        SUBI    #$0002, R5                      ; 1C56   033D 0002
.EXEC.C58:
        SUB@    R5,     R1                      ; 1C58   0329
.EXEC.C59:
        DECR    R5                              ; 1C59   0015
.EXEC.C5A:
        SUB@    R5,     R1                      ; 1C5A   0329
.EXEC.C5B:
        ADD@    R2,     R2                      ; 1C5B   02D2
.EXEC.C5C:
        ADDR    R1,     R2                      ; 1C5C   00CA
.EXEC.C5D:
        MVII    #$01F0, R3                      ; 1C5D   02BB 01F0
.EXEC.C5F:
        ADD@    R2,     R7                      ; 1C5F   02D7
.EXEC.C60:
        CLRR    R2                              ; 1C60   01D2
.EXEC.C61:
        SARC    R0,     2                       ; 1C61   007C
.EXEC.C62:
        RLC     R2,     2                       ; 1C62   0056
.EXEC.C63:
        MVI@    R4,     R1                      ; 1C63   02A1
.EXEC.C64:
        ADDR    R2,     R3                      ; 1C64   00D3
.EXEC.C65:
        MVO@    R1,     R3                      ; 1C65   0259
.EXEC.C66:
        ADDI    #$0004, R3                      ; 1C66   02FB 0004
.EXEC.C68:
        SLL     R1,     2                       ; 1C68   004D
.EXEC.C69:
        SLL     R1,     2                       ; 1C69   004D
.EXEC.C6A:
        SLL     R1,     2                       ; 1C6A   004D
.EXEC.C6B:
        SLLC    R1,     2                       ; 1C6B   005D
.EXEC.C6C:
        RLC     R0,     2                       ; 1C6C   0054
.EXEC.C6D:
        MOVR    R0,     R1                      ; 1C6D   0081
.EXEC.C6E:
        SLR     R1,     2                       ; 1C6E   0065
.EXEC.C6F:
        SLR     R1,     2                       ; 1C6F   0065
.EXEC.C70:
        MVO@    R0,     R3                      ; 1C70   0258
.EXEC.C71:
        CMPI    #$0003, R2                      ; 1C71   037A 0003
.EXEC.C73:
        BEQ     .EXEC.C89                       ; 1C73   0204 0014

.EXEC.C75:
        CLRR    R0                              ; 1C75   01C0
.EXEC.C76:
        MOVR    R2,     R5                      ; 1C76   0095
.EXEC.C77:
        ADDR    R5,     R5                      ; 1C77   00ED
.EXEC.C78:
        ADDI    #$014B, R5                      ; 1C78   02FD 014B
.EXEC.C7A:
        MVO@    R0,     R5                      ; 1C7A   0268
.EXEC.C7B:
        MVO@    R0,     R5                      ; 1C7B   0268
.EXEC.C7C:
        MOVR    R1,     R0                      ; 1C7C   0088
.EXEC.C7D:
        BEQ     .EXEC.A93                       ; 1C7D   0224 01EB

.EXEC.C7F:
        SUBR    R2,     R3                      ; 1C7F   0113
.EXEC.C80:
        ADDI    #$0007, R3                      ; 1C80   02FB 0007
.EXEC.C82:
        DECR    R1                              ; 1C82   0011
.EXEC.C83:
        BNEQ    .EXEC.D4D                       ; 1C83   020C 00C8

.EXEC.C85:
        MVII    #$0030, R0                      ; 1C85   02B8 0030
.EXEC.C87:
        B       .EXEC.D4D                       ; 1C87   0200 00C4

.EXEC.C89:
        ADDI    #$0003, R3                      ; 1C89   02FB 0003
.EXEC.C8B:
        MVI@    R3,     R0                      ; 1C8B   0298
.EXEC.C8C:
        MVO@    R0,     R3                      ; 1C8C   0258
.EXEC.C8D:
        MVO@    R0,     R3                      ; 1C8D   0258
.EXEC.C8E:
        PULR    R7                              ; 1C8E   02B7
.EXEC.C8F:
        MVI@    R4,     R1                      ; 1C8F   02A1
.EXEC.C90:
        CLRR    R2                              ; 1C90   01D2
.EXEC.C91:
        SARC    R1,     2                       ; 1C91   007D
.EXEC.C92:
        RLC     R2,     2                       ; 1C92   0056
.EXEC.C93:
        MVII    #$014B, R5                      ; 1C93   02BD 014B
.EXEC.C95:
        CMPI    #$0003, R2                      ; 1C95   037A 0003
.EXEC.C97:
        BNEQ    .EXEC.C9E                       ; 1C97   020C 0005

.EXEC.C99:
        MVO@    R1,     R5                      ; 1C99   0269
.EXEC.C9A:
        MVO@    R0,     R5                      ; 1C9A   0268
.EXEC.C9B:
        MVO@    R1,     R5                      ; 1C9B   0269
.EXEC.C9C:
        MVO@    R0,     R5                      ; 1C9C   0268
.EXEC.C9D:
        CLRR    R2                              ; 1C9D   01D2
.EXEC.C9E:
        ADDR    R2,     R5                      ; 1C9E   00D5
.EXEC.C9F:
        ADDR    R2,     R5                      ; 1C9F   00D5
.EXEC.CA0:
        MVO@    R1,     R5                      ; 1CA0   0269
.EXEC.CA1:
        MVO@    R0,     R5                      ; 1CA1   0268
.EXEC.CA2:
        PULR    R7                              ; 1CA2   02B7

.EXEC.CA3:
        JSR     R5,     .EXEC.CC2               ; 1CA3   0004 011C 00C2

.EXEC.CA6:
        MVI@    R3,     R5                      ; 1CA6   029D
.EXEC.CA7:
        ADDI    #$0004, R3                      ; 1CA7   02FB 0004
.EXEC.CA9:
        MVI@    R3,     R1                      ; 1CA9   0299
.EXEC.CAA:
        ANDI    #$000F, R1                      ; 1CAA   03B9 000F
.EXEC.CAC:
        SWAP    R1,     1                       ; 1CAC   0041
.EXEC.CAD:
        XORR    R5,     R1                      ; 1CAD   01E9

.EXEC.CAE:
        JSR     R5,     .EXEC.CEC               ; 1CAE   0004 011C 00EC

.EXEC.CB1:
        SWAP    R1,     1                       ; 1CB1   0041
.EXEC.CB2:
        MVO@    R1,     R3                      ; 1CB2   0259
.EXEC.CB3:
        SUBI    #$0004, R3                      ; 1CB3   033B 0004
.EXEC.CB5:
        SWAP    R1,     1                       ; 1CB5   0041
.EXEC.CB6:
        MVO@    R1,     R3                      ; 1CB6   0259
.EXEC.CB7:
        INCR    R3                              ; 1CB7   000B
.EXEC.CB8:
        CMPI    #$01F3, R3                      ; 1CB8   037B 01F3
.EXEC.CBA:
        BNEQ    .EXEC.CA6                       ; 1CBA   022C 0015

.EXEC.CBC:
        PULR    R7                              ; 1CBC   02B7
.EXEC.CBD:
        SWAP    R1,     1                       ; 1CBD   0041
.EXEC.CBE:
        SAR     R1,     2                       ; 1CBE   006D
.EXEC.CBF:
        SAR     R1,     2                       ; 1CBF   006D
.EXEC.CC0:
        SAR     R1,     2                       ; 1CC0   006D
.EXEC.CC1:
        SAR     R1,     2                       ; 1CC1   006D
.EXEC.CC2:
        INCR    R0                              ; 1CC2   0008
.EXEC.CC3:
        ADDR    R0,     R0                      ; 1CC3   00C0
.EXEC.CC4:
        MVO     R5,     G_035F                  ; 1CC4   0245 035F
.EXEC.CC6:
        MOVR    R0,     R2                      ; 1CC6   0082
.EXEC.CC7:
        MOVR    R2,     R0                      ; 1CC7   0090
.EXEC.CC8:
        CLRR    R5                              ; 1CC8   01ED
.EXEC.CC9:
        INCR    R5                              ; 1CC9   000D
.EXEC.CCA:
        SLR     R0,     1                       ; 1CCA   0060
.EXEC.CCB:
        BNEQ    .EXEC.CC9                       ; 1CCB   022C 0003

.EXEC.CCD:
        MOVR    R5,     R0                      ; 1CCD   00A8

.EXEC.CCE:
        JSR     R5,     X_RAND1                 ; 1CCE   0004 0114 027D

.EXEC.CD1:
        CMPR    R2,     R0                      ; 1CD1   0150
.EXEC.CD2:
        BGE     .EXEC.CC7                       ; 1CD2   022D 000C

.EXEC.CD4:
        MVI     G_035F, R7                      ; 1CD4   0287 035F

.EXEC.CD6:
        JSR     R5,     .EXEC.CC2               ; 1CD6   0004 011C 00C2

.EXEC.CD9:
        MVII    #$014B, R3                      ; 1CD9   02BB 014B
.EXEC.CDB:
        MVI@    R3,     R1                      ; 1CDB   0299
.EXEC.CDC:
        SWAP    R1,     1                       ; 1CDC   0041
.EXEC.CDD:
        SAR     R1,     2                       ; 1CDD   006D
.EXEC.CDE:
        SAR     R1,     2                       ; 1CDE   006D
.EXEC.CDF:
        SAR     R1,     2                       ; 1CDF   006D
.EXEC.CE0:
        SAR     R1,     2                       ; 1CE0   006D

.EXEC.CE1:
        JSR     R5,     .EXEC.CEC               ; 1CE1   0004 011C 00EC

.EXEC.CE4:
        MVO@    R1,     R3                      ; 1CE4   0259
.EXEC.CE5:
        ADDI    #$0002, R3                      ; 1CE5   02FB 0002
.EXEC.CE7:
        CMPI    #$0151, R3                      ; 1CE7   037B 0151
.EXEC.CE9:
        BNEQ    .EXEC.CDB                       ; 1CE9   022C 000F

.EXEC.CEB:
        PULR    R7                              ; 1CEB   02B7
.EXEC.CEC:
        PSHR    R5                              ; 1CEC   0275
.EXEC.CED:
        MOVR    R0,     R2                      ; 1CED   0082
.EXEC.CEE:
        MOVR    R1,     R5                      ; 1CEE   008D
.EXEC.CEF:
        CLRR    R1                              ; 1CEF   01C9
.EXEC.CF0:
        SARC    R2,     1                       ; 1CF0   007A
.EXEC.CF1:
        BNC     .EXEC.CF6                       ; 1CF1   0209 0003

.EXEC.CF3:
        NEGR    R5                              ; 1CF3   0025
.EXEC.CF4:
        INCR    R7                              ; 1CF4   000F
.EXEC.CF5:
        ADDR    R5,     R1                      ; 1CF5   00E9
.EXEC.CF6:
        DECR    R2                              ; 1CF6   0012
.EXEC.CF7:
        BPL     .EXEC.CF5                       ; 1CF7   0223 0003

.EXEC.CF9:
        MOVR    R0,     R2                      ; 1CF9   0082
.EXEC.CFA:
        SARC    R2,     1                       ; 1CFA   007A
.EXEC.CFB:
        BNC     .EXEC.CFE                       ; 1CFB   0209 0001

.EXEC.CFD:
        NEGR    R5                              ; 1CFD   0025
.EXEC.CFE:
        SAR     R1,     2                       ; 1CFE   006D
.EXEC.CFF:
        SAR     R1,     2                       ; 1CFF   006D
.EXEC.D00:
        INCR    R1                              ; 1D00   0009
.EXEC.D01:
        SAR     R1,     1                       ; 1D01   0069
.EXEC.D02:
        ADDR    R5,     R1                      ; 1D02   00E9
.EXEC.D03:
        PULR    R7                              ; 1D03   02B7
.EXEC.D04:
        ADDI    #$0008, R3                      ; 1D04   02FB 0008
.EXEC.D06:
        MVO@    R0,     R3                      ; 1D06   0258
.EXEC.D07:
        MOVR    R0,     R1                      ; 1D07   0081
.EXEC.D08:
        SLR     R1,     2                       ; 1D08   0065
.EXEC.D09:
        SLR     R1,     1                       ; 1D09   0061
.EXEC.D0A:
        ANDR    R1,     R0                      ; 1D0A   0188
.EXEC.D0B:
        CLRR    R1                              ; 1D0B   01C9
.EXEC.D0C:
        ADDI    #$0002, R3                      ; 1D0C   02FB 0002
.EXEC.D0E:
        B       .EXEC.D14                       ; 1D0E   0200 0004

.EXEC.D10:
        ADDI    #$000A, R3                      ; 1D10   02FB 000A
.EXEC.D12:
        MVII    #$0030, R1                      ; 1D12   02B9 0030
.EXEC.D14:
        MVII    #$0151, R2                      ; 1D14   02BA 0151
.EXEC.D16:
        CLRR    R5                              ; 1D16   01ED
.EXEC.D17:
        INCR    R2                              ; 1D17   000A
.EXEC.D18:
        INCR    R3                              ; 1D18   000B
.EXEC.D19:
        SARC    R0,     1                       ; 1D19   0078
.EXEC.D1A:
        BNC     .EXEC.D1E                       ; 1D1A   0209 0002

.EXEC.D1C:
        MVO@    R1,     R3                      ; 1D1C   0259
.EXEC.D1D:
        MVO@    R5,     R2                      ; 1D1D   0255
.EXEC.D1E:
        BNEQ    .EXEC.D17                       ; 1D1E   022C 0008

.EXEC.D20:
        PULR    R7                              ; 1D20   02B7
.EXEC.D21:
        MVO     R0,     .PSG0.envelope          ; 1D21   0240 01FA
.EXEC.D23:
        PULR    R7                              ; 1D23   02B7
.EXEC.D24:
        MVO     R0,     .PSG0.noise             ; 1D24   0240 01F9
.EXEC.D26:
        SLL     R0,     2                       ; 1D26   004C
.EXEC.D27:
        MVO     R0,     G_0155                  ; 1D27   0240 0155
.EXEC.D29:
        CLRR    R0                              ; 1D29   01C0
.EXEC.D2A:
        INCR    R7                              ; 1D2A   000F
.EXEC.D2B:
        MVI@    R4,     R0                      ; 1D2B   02A0
.EXEC.D2C:
        MVO     R0,     G_0151                  ; 1D2C   0240 0151
.EXEC.D2E:
        PULR    R7                              ; 1D2E   02B7
.EXEC.D2F:
        MVI     G_0155, R1                      ; 1D2F   0281 0155

.EXEC.D31:
        JSR     R5,     .EXEC.CC2               ; 1D31   0004 011C 00C2
.EXEC.D34:
        JSR     R5,     .EXEC.CEC               ; 1D34   0004 011C 00EC

.EXEC.D37:
        MVO     R1,     G_0155                  ; 1D37   0241 0155
.EXEC.D39:
        SLR     R1,     2                       ; 1D39   0065
.EXEC.D3A:
        MVO     R1,     .PSG0.noise             ; 1D3A   0241 01F9
.EXEC.D3C:
        PULR    R7                              ; 1D3C   02B7
.EXEC.D3D:
        MVI     G_0151, R1                      ; 1D3D   0281 0151

.EXEC.D3F:
        JSR     R5,     .EXEC.CBD               ; 1D3F   0004 011C 00BD
.EXEC.D42:
        JSR     R5,     .EXEC.CEC               ; 1D42   0004 011C 00EC

.EXEC.D45:
        MVO     R1,     G_0151                  ; 1D45   0241 0151
.EXEC.D47:
        PULR    R7                              ; 1D47   02B7
.EXEC.D48:
        ADDI    #$000B, R3                      ; 1D48   02FB 000B
.EXEC.D4A:
        CLRR    R2                              ; 1D4A   01D2
.EXEC.D4B:
        SARC    R0,     2                       ; 1D4B   007C
.EXEC.D4C:
        RLC     R2,     2                       ; 1D4C   0056
.EXEC.D4D:
        CLRR    R1                              ; 1D4D   01C9
.EXEC.D4E:
        CMPI    #$0003, R2                      ; 1D4E   037A 0003
.EXEC.D50:
        BNEQ    .EXEC.D54                       ; 1D50   020C 0002

.EXEC.D52:
        INCR    R1                              ; 1D52   0009
.EXEC.D53:
        CLRR    R2                              ; 1D53   01D2
.EXEC.D54:
        ADDR    R2,     R3                      ; 1D54   00D3
.EXEC.D55:
        MOVR    R3,     R5                      ; 1D55   009D
.EXEC.D56:
        MVO@    R0,     R5                      ; 1D56   0268
.EXEC.D57:
        TSTR    R1                              ; 1D57   0089
.EXEC.D58:
        BEQ     .EXEC.D5C                       ; 1D58   0204 0002

.EXEC.D5A:
        MVO@    R0,     R5                      ; 1D5A   0268
.EXEC.D5B:
        MVO@    R0,     R5                      ; 1D5B   0268
.EXEC.D5C:
        MVII    #$0156, R5                      ; 1D5C   02BD 0156
.EXEC.D5E:
        ADDR    R2,     R5                      ; 1D5E   00D5
.EXEC.D5F:
        SLL     R0,     2                       ; 1D5F   004C
.EXEC.D60:
        SLL     R0,     1                       ; 1D60   0048
.EXEC.D61:
        ADDI    #$0152, R2                      ; 1D61   02FA 0152
.EXEC.D63:
        CLRR    R3                              ; 1D63   01DB
.EXEC.D64:
        MVO@    R0,     R5                      ; 1D64   0268
.EXEC.D65:
        MVO@    R3,     R2                      ; 1D65   0253
.EXEC.D66:
        TSTR    R1                              ; 1D66   0089
.EXEC.D67:
        BEQ     .EXEC.A93                       ; 1D67   0224 02D5

.EXEC.D69:
        MVO@    R0,     R5                      ; 1D69   0268
.EXEC.D6A:
        MVO@    R0,     R5                      ; 1D6A   0268
.EXEC.D6B:
        INCR    R2                              ; 1D6B   000A
.EXEC.D6C:
        MVO@    R3,     R2                      ; 1D6C   0253
.EXEC.D6D:
        INCR    R2                              ; 1D6D   000A
.EXEC.D6E:
        MVO@    R3,     R2                      ; 1D6E   0253
.EXEC.D6F:
        PULR    R7                              ; 1D6F   02B7
.EXEC.D70:
        CLRR    R2                              ; 1D70   01D2
.EXEC.D71:
        SARC    R0,     2                       ; 1D71   007C
.EXEC.D72:
        RLC     R2,     2                       ; 1D72   0056
.EXEC.D73:
        SWAP    R0,     1                       ; 1D73   0040
.EXEC.D74:
        MVII    #$0152, R5                      ; 1D74   02BD 0152
.EXEC.D76:
        SLL     R0,     2                       ; 1D76   004C
.EXEC.D77:
        SAR     R0,     2                       ; 1D77   006C
.EXEC.D78:
        SWAP    R0,     1                       ; 1D78   0040
.EXEC.D79:
        CMPI    #$0003, R2                      ; 1D79   037A 0003
.EXEC.D7B:
        BNEQ    .EXEC.D80                       ; 1D7B   020C 0003

.EXEC.D7D:
        MVO@    R0,     R5                      ; 1D7D   0268
.EXEC.D7E:
        MVO@    R0,     R5                      ; 1D7E   0268
.EXEC.D7F:
        INCR    R7                              ; 1D7F   000F
.EXEC.D80:
        ADDR    R2,     R5                      ; 1D80   00D5
.EXEC.D81:
        MVO@    R0,     R5                      ; 1D81   0268
.EXEC.D82:
        PULR    R7                              ; 1D82   02B7
.EXEC.D83:
        INCR    R0                              ; 1D83   0008
.EXEC.D84:
        MVO     R0,     G_0147                  ; 1D84   0240 0147
.EXEC.D86:
        PULR    R7                              ; 1D86   02B7
.EXEC.D87:
        SDBD                                    ; 1D87   0001
.EXEC.D88:
        MVI@    R4,     R7                      ; 1D88   02A7
.EXEC.D89:
        PULR    R5                              ; 1D89   02B5
.EXEC.D8A:
        RRC     R0,     2                       ; 1D8A   0074
.EXEC.D8B:
        BNOV    .EXEC.D91                       ; 1D8B   020A 0004

.EXEC.D8D:
        SDBD                                    ; 1D8D   0001
.EXEC.D8E:
        MVII    #$1A93, R4                      ; 1D8E   02BC 0093 001A
.EXEC.D91:
        MVO     R4,     G_035F                  ; 1D91   0244 035F
.EXEC.D93:
        BNC     .EXEC.AA5                       ; 1D93   0229 02EF
.EXEC.D95:
        B       X_HUSH                          ; 1D95   0220 02EE

.EXEC.D97:
        CLRR    R3                              ; 1D97   01DB
.EXEC.D98:
        SARC    R0,     2                       ; 1D98   007C
.EXEC.D99:
        RLC     R3,     2                       ; 1D99   0057
.EXEC.D9A:
        B       .EXEC.D9E                       ; 1D9A   0200 0002

.EXEC.D9C:
        MOVR    R0,     R3                      ; 1D9C   0083
.EXEC.D9D:
        MVI@    R4,     R0                      ; 1D9D   02A0
.EXEC.D9E:
        ADDI    #$0159, R3                      ; 1D9E   02FB 0159
.EXEC.DA0:
        MVO@    R0,     R3                      ; 1DA0   0258
.EXEC.DA1:
        PULR    R7                              ; 1DA1   02B7
.EXEC.DA2:
        MVI@    R4,     R0                      ; 1DA2   02A0
.EXEC.DA3:
        INCR    R0                              ; 1DA3   0008
.EXEC.DA4:
        TSTR    R0                              ; 1DA4   0080
.EXEC.DA5:
        BEQ     .EXEC.A93                       ; 1DA5   0224 0313

.EXEC.DA7:
        MVO     R0,     G_014A                  ; 1DA7   0240 014A
.EXEC.DA9:
        MVO     R4,     G_035F                  ; 1DA9   0244 035F
.EXEC.DAB:
        PULR    R5                              ; 1DAB   02B5
.EXEC.DAC:
        PULR    R7                              ; 1DAC   02B7
.EXEC.DAD:
        MVI@    R4,     R1                      ; 1DAD   02A1
.EXEC.DAE:
        CLRR    R2                              ; 1DAE   01D2
.EXEC.DAF:
        SARC    R1,     2                       ; 1DAF   007D
.EXEC.DB0:
        RLC     R2,     2                       ; 1DB0   0056
.EXEC.DB1:
        ADDI    #$0159, R2                      ; 1DB1   02FA 0159
.EXEC.DB3:
        MVI@    R2,     R5                      ; 1DB3   0295
.EXEC.DB4:
        DECR    R5                              ; 1DB4   0015
.EXEC.DB5:
        BMI     .EXEC.DBA                       ; 1DB5   020B 0003

.EXEC.DB7:
        MVO@    R5,     R2                      ; 1DB7   0255
.EXEC.DB8:
        BEQ     .EXEC.DA4                       ; 1DB8   0224 0015

.EXEC.DBA:
        SWAP    R1,     1                       ; 1DBA   0041
.EXEC.DBB:
        SAR     R1,     2                       ; 1DBB   006D
.EXEC.DBC:
        SAR     R1,     2                       ; 1DBC   006D
.EXEC.DBD:
        SAR     R1,     2                       ; 1DBD   006D
.EXEC.DBE:
        SAR     R1,     2                       ; 1DBE   006D
.EXEC.DBF:
        ADDR    R1,     R4                      ; 1DBF   00CC
.EXEC.DC0:
        B       .EXEC.DA4                       ; 1DC0   0220 001D

.EXEC.DC2:
        MVI@    R4,     R1                      ; 1DC2   02A1
.EXEC.DC3:
        SARC    R1,     2                       ; 1DC3   007D
.EXEC.DC4:
        RLC     R0,     2                       ; 1DC4   0054
.EXEC.DC5:
        SARC    R1,     1                       ; 1DC5   0079
.EXEC.DC6:
        RLC     R0,     1                       ; 1DC6   0050
.EXEC.DC7:
        INCR    R0                              ; 1DC7   0008

.EXEC.DC8:
        JSR     R5,     .EXEC.CC4               ; 1DC8   0004 011C 00C4

.EXEC.DCB:
        ADDR    R1,     R0                      ; 1DCB   00C8
.EXEC.DCC:
        B       .EXEC.DA4                       ; 1DCC   0220 0029

.EXEC.DCE:
        MVI@    R4,     R1                      ; 1DCE   02A1
.EXEC.DCF:
        CLRR    R3                              ; 1DCF   01DB
.EXEC.DD0:
        SARC    R1,     2                       ; 1DD0   007D
.EXEC.DD1:
        RLC     R3,     2                       ; 1DD1   0057
.EXEC.DD2:
        SARC    R1,     2                       ; 1DD2   007D
.EXEC.DD3:
        RLC     R0,     2                       ; 1DD3   0054
.EXEC.DD4:
        INCR    R0                              ; 1DD4   0008

.EXEC.DD5:
        JSR     R5,     .EXEC.CC4               ; 1DD5   0004 011C 00C4

.EXEC.DD8:
        ADDR    R1,     R0                      ; 1DD8   00C8
.EXEC.DD9:
        B       .EXEC.D9E                       ; 1DD9   0220 003C

X_SQUARE:
        MOVR    R0,     R1                      ; 1DDB   0081
X_MPY:
        PSHR    R3                              ; 1DDC   0273
.EXEC.DDD:
        CLRR    R3                              ; 1DDD   01DB
.EXEC.DDE:
        CLRR    R2                              ; 1DDE   01D2
.EXEC.DDF:
        TSTR    R0                              ; 1DDF   0080
.EXEC.DE0:
        BPL     .EXEC.DE4                       ; 1DE0   0203 0002

.EXEC.DE2:
        NEGR    R0                              ; 1DE2   0020
.EXEC.DE3:
        INCR    R3                              ; 1DE3   000B
.EXEC.DE4:
        TSTR    R1                              ; 1DE4   0089
.EXEC.DE5:
        BPL     .EXEC.DE9                       ; 1DE5   0203 0002

.EXEC.DE7:
        NEGR    R1                              ; 1DE7   0021
.EXEC.DE8:
        INCR    R3                              ; 1DE8   000B
.EXEC.DE9:
        B       .EXEC.DED                       ; 1DE9   0200 0002

.EXEC.DEB:
        ADDR    R0,     R2                      ; 1DEB   00C2
.EXEC.DEC:
        SLL     R0,     1                       ; 1DEC   0048
.EXEC.DED:
        SARC    R1,     1                       ; 1DED   0079
.EXEC.DEE:
        BC      .EXEC.DEB                       ; 1DEE   0221 0004
.EXEC.DF0:
        BNEQ    .EXEC.DEC                       ; 1DF0   022C 0005

.EXEC.DF2:
        SARC    R3,     1                       ; 1DF2   007B
.EXEC.DF3:
        BNC     .EXEC.DF6                       ; 1DF3   0209 0001

.EXEC.DF5:
        NEGR    R2                              ; 1DF5   0022
.EXEC.DF6:
        PULR    R3                              ; 1DF6   02B3
.EXEC.DF7:
        MOVR    R5,     R7                      ; 1DF7   00AF
X_DIVR:
        MOVR    R2,     R0                      ; 1DF8   0090
.EXEC.DF9:
        SARC    R0,     1                       ; 1DF9   0078
.EXEC.DFA:
        ADDR    R0,     R1                      ; 1DFA   00C1
X_DIV:
        PSHR    R3                              ; 1DFB   0273
.EXEC.DFC:
        CLRR    R0                              ; 1DFC   01C0
.EXEC.DFD:
        MVII    #$0001, R3                      ; 1DFD   02BB 0001
.EXEC.DFF:
        TSTR    R2                              ; 1DFF   0092
.EXEC.E00:
        BEQ     .EXEC.E21                       ; 1E00   0204 001F
.EXEC.E02:
        BPL     .EXEC.E06                       ; 1E02   0203 0002

.EXEC.E04:
        NEGR    R2                              ; 1E04   0022
.EXEC.E05:
        INCR    R0                              ; 1E05   0008
.EXEC.E06:
        INCR    R7                              ; 1E06   000F
.EXEC.E07:
        SLL     R3,     1                       ; 1E07   004B
.EXEC.E08:
        SLLC    R2,     1                       ; 1E08   005A
.EXEC.E09:
        BNC     .EXEC.E07                       ; 1E09   0229 0003

.EXEC.E0B:
        RRC     R2,     1                       ; 1E0B   0072
.EXEC.E0C:
        TSTR    R1                              ; 1E0C   0089
.EXEC.E0D:
        BPL     .EXEC.E11                       ; 1E0D   0203 0002

.EXEC.E0F:
        NEGR    R1                              ; 1E0F   0021
.EXEC.E10:
        INCR    R0                              ; 1E10   0008
.EXEC.E11:
        SARC    R0,     1                       ; 1E11   0078
.EXEC.E12:
        RRC     R3,     1                       ; 1E12   0073
.EXEC.E13:
        CLRR    R0                              ; 1E13   01C0
.EXEC.E14:
        SLR     R2,     1                       ; 1E14   0062
.EXEC.E15:
        CMPR    R2,     R1                      ; 1E15   0151
.EXEC.E16:
        BLT     .EXEC.E1A                       ; 1E16   0205 0002

.EXEC.E18:
        SUBR    R2,     R1                      ; 1E18   0111
.EXEC.E19:
        SETC                                    ; 1E19   0007
.EXEC.E1A:
        RLC     R0,     1                       ; 1E1A   0050
.EXEC.E1B:
        SARC    R3,     1                       ; 1E1B   007B
.EXEC.E1C:
        BNC     .EXEC.E14                       ; 1E1C   0229 0009
.EXEC.E1E:
        BEQ     .EXEC.E21                       ; 1E1E   0204 0001

.EXEC.E20:
        NEGR    R0                              ; 1E20   0020
.EXEC.E21:
        PULR    R3                              ; 1E21   02B3
.EXEC.E22:
        MOVR    R5,     R7                      ; 1E22   00AF
X_SQRT:
        PSHR    R5                              ; 1E23   0275
.EXEC.E24:
        MOVR    R1,     R2                      ; 1E24   008A
.EXEC.E25:
        SLR     R2,     1                       ; 1E25   0062
.EXEC.E26:
        PSHR    R2                              ; 1E26   0272
.EXEC.E27:
        PSHR    R1                              ; 1E27   0271

.EXEC.E28:
        JSR     R5,     X_DIVR                  ; 1E28   0004 011C 01F8

.EXEC.E2B:
        PULR    R1                              ; 1E2B   02B1
.EXEC.E2C:
        PULR    R2                              ; 1E2C   02B2
.EXEC.E2D:
        ADDR    R0,     R2                      ; 1E2D   00C2
.EXEC.E2E:
        SLR     R2,     1                       ; 1E2E   0062
.EXEC.E2F:
        SUBR    R2,     R0                      ; 1E2F   0110
.EXEC.E30:
        BPL     .EXEC.E33                       ; 1E30   0203 0001

.EXEC.E32:
        NEGR    R0                              ; 1E32   0020
.EXEC.E33:
        CMPI    #$0002, R0                      ; 1E33   0378 0002
.EXEC.E35:
        BPL     .EXEC.E26                       ; 1E35   0223 0010

.EXEC.E37:
        PULR    R7                              ; 1E37   02B7
.EXEC.E38:
        PSHR    R5                              ; 1E38   0275
.EXEC.E39:
        MVII    #$00F0, R0                      ; 1E39   02B8 00F0
.EXEC.E3B:
        MVII    #$0200, R4                      ; 1E3B   02BC 0200

.EXEC.E3D:
        JSR     R5,     X_FILL_ZERO             ; 1E3D   0004 0114 0338

.EXEC.E40:
        MVII    #$0216, R4                      ; 1E40   02BC 0216
.EXEC.E42:
        SDBD                                    ; 1E42   0001
.EXEC.E43:
        MVII    #$052F, R0                      ; 1E43   02B8 002F 0005
.EXEC.E46:
        MVO@    R0,     R4                      ; 1E46   0260
.EXEC.E47:
        INCR    R4                              ; 1E47   000C
.EXEC.E48:
        CMPI    #$021E, R4                      ; 1E48   037C 021E
.EXEC.E4A:
        BNEQ    .EXEC.E4F                       ; 1E4A   020C 0003

.EXEC.E4C:
        INCR    R4                              ; 1E4C   000C
.EXEC.E4D:
        SUBI    #$0008, R0                      ; 1E4D   0338 0008
.EXEC.E4F:
        DECR    R0                              ; 1E4F   0010
.EXEC.E50:
        CMPI    #$0227, R4                      ; 1E50   037C 0227
.EXEC.E52:
        BNEQ    .EXEC.E46                       ; 1E52   022C 000D

.EXEC.E54:
        MVII    #$0082, R0                      ; 1E54   02B8 0082
.EXEC.E56:
        MVO     R0,     G_0102                  ; 1E56   0240 0102
.EXEC.E58:
        EIS                                     ; 1E58   0002
.EXEC.E59:
        CMP     G_0102, R0                      ; 1E59   0340 0102
.EXEC.E5B:
        BEQ     .EXEC.E59                       ; 1E5B   0224 0003

.EXEC.E5D:
        MVII    #$0007, R3                      ; 1E5D   02BB 0007

.EXEC.E5F:
        JSR     R5,     X_READ_ROM_HDR          ; 1E5F   0004 0110 00AB

.EXEC.E62:
        INCR    R2                              ; 1E62   000A
.EXEC.E63:
        PSHR    R4                              ; 1E63   0274
.EXEC.E64:
        MVI@    R5,     R0                      ; 1E64   02A8
.EXEC.E65:
        PSHR    R5                              ; 1E65   0275
.EXEC.E66:
        MVII    #$0002, R1                      ; 1E66   02B9 0002
.EXEC.E68:
        MVII    #$02D2, R4                      ; 1E68   02BC 02D2

.EXEC.E6A:
        JSR     R5,     X_PRNUM_RGT             ; 1E6A   0004 0118 00C5

.EXEC.E6D:
        PULR    R4                              ; 1E6D   02B4
.EXEC.E6E:
        MOVR    R4,     R1                      ; 1E6E   00A1
.EXEC.E6F:
        SDBD                                    ; 1E6F   0001
.EXEC.E70:
        MVII    #$052D, R2                      ; 1E70   02BA 002D 0005
.EXEC.E73:
        DECR    R2                              ; 1E73   0012
.EXEC.E74:
        MVI@    R4,     R0                      ; 1E74   02A0
.EXEC.E75:
        TSTR    R0                              ; 1E75   0080
.EXEC.E76:
        BNEQ    .EXEC.E73                       ; 1E76   022C 0004

.EXEC.E78:
        SLR     R2,     1                       ; 1E78   0062
.EXEC.E79:
        MOVR    R2,     R4                      ; 1E79   0094

.EXEC.E7A:
        JSR     R5,     X_PRINT_R1              ; 1E7A   0004 0118 0067

.EXEC.E7D:
        PULR    R1                              ; 1E7D   02B1
.EXEC.E7E:
        MVI@    R1,     R1                      ; 1E7E   0289
.EXEC.E7F:
        SWAP    R1,     2                       ; 1E7F   0045
.EXEC.E80:
        BPL     .EXEC.E87                       ; 1E80   0203 0005

.EXEC.E82:
        MOVR    R5,     R4                      ; 1E82   00AC
.EXEC.E83:
        MOVR    R7,     R5                      ; 1E83   00BD
.EXEC.E84:
        ADDI    #$0003, R5                      ; 1E84   02FD 0003
.EXEC.E86:
        MOVR    R4,     R7                      ; 1E86   00A7

.EXEC.E87:
        JSRE    R5,     .EXEC.4C3               ; 1E87   0004 0115 00C3

.EXEC.E8A:
        DIS                                     ; 1E8A   0003
.EXEC.E8B:
        MOVR    R5,     R1                      ; 1E8B   00A9
.EXEC.E8C:
        ANDI    #$00FF, R1                      ; 1E8C   03B9 00FF
.EXEC.E8E:
        BNEQ    .EXEC.E92                       ; 1E8E   020C 0002

.EXEC.E90:
        XORR    R5,     R1                      ; 1E90   01E9
.EXEC.E91:
        SWAP    R1,     1                       ; 1E91   0041
.EXEC.E92:
        MOVR    R1,     R2                      ; 1E92   008A
.EXEC.E93:
        ANDI    #$001F, R1                      ; 1E93   03B9 001F
.EXEC.E95:
        DECR    R1                              ; 1E95   0011
.EXEC.E96:
        MVII    #$0003, R0                      ; 1E96   02B8 0003
.EXEC.E98:
        BNEQ    .EXEC.EAA                       ; 1E98   020C 0010

.EXEC.E9A:
        SLL     R0,     1                       ; 1E9A   0048
.EXEC.E9B:
        SLR     R2,     2                       ; 1E9B   0066
.EXEC.E9C:
        SLR     R2,     2                       ; 1E9C   0066
.EXEC.E9D:
        SARC    R2,     2                       ; 1E9D   007E
.EXEC.E9E:
        BOV     .EXEC.EA8                       ; 1E9E   0202 0008

.EXEC.EA0:
        DECR    R0                              ; 1EA0   0010
.EXEC.EA1:
        SARC    R2,     1                       ; 1EA1   007A
.EXEC.EA2:
        BC      .EXEC.EA8                       ; 1EA2   0201 0004

.EXEC.EA4:
        DECR    R0                              ; 1EA4   0010
.EXEC.EA5:
        SARC    R2,     1                       ; 1EA5   007A
.EXEC.EA6:
        BNC     .EXEC.E95                       ; 1EA6   0229 0012
.EXEC.EA8:
        BNEQ    .EXEC.E95                       ; 1EA8   022C 0014

.EXEC.EAA:
        MVO     R0,     G_0103                  ; 1EAA   0240 0103
.EXEC.EAC:
        PULR    R7                              ; 1EAC   02B7
X_SFX_OK:
        MVI     G_0149, R1                      ; 1EAD   0281 0149
.EXEC.EAF:
        TSTR    R1                              ; 1EAF   0089
.EXEC.EB0:
        BNEQ    .EXEC.EB3                       ; 1EB0   020C 0001

.EXEC.EB2:
        MOVR    R4,     R7                      ; 1EB2   00A7
.EXEC.EB3:
        MOVR    R5,     R7                      ; 1EB3   00AF
X_STOP_SFX:
        PSHR    R5                              ; 1EB4   0275

.EXEC.EB5:
        JSR     R5,     X_PLAY_SFX2             ; 1EB5   0004 0118 03BE

.EXEC.EB8:
        ADDR    R7,     R7                      ; 1EB8   00FF
.EXEC.EB9:
        ADD@    R1,     R7                      ; 1EB9   02CF

X_PLAY_RAZZ1:
        JSR     R4,     X_SFX_OK                ; 1EBA   0004 001C 02AD

X_PLAY_RAZZ2:
        MVII    #$0005, R0                      ; 1EBD   02B8 0005
.EXEC.EBF:
        B       X_PLAY_RAZZ4                    ; 1EBF   0200 0003

X_PLAY_RAZZ3:
        JSR     R4,     X_SFX_OK                ; 1EC1   0004 001C 02AD

X_PLAY_RAZZ4:
        PSHR    R5                              ; 1EC4   0275

X_PLAY_RAZZ5:
        JSR     R5,     X_PLAY_SFX1             ; 1EC5   0004 0118 03BB

.EXEC.EC8:
        SWAP    R0,     1                       ; 1EC8   0040
.EXEC.EC9:
        COMR    R0                              ; 1EC9   0018
.EXEC.ECA:
        SLL     R0,     1                       ; 1ECA   0048
.EXEC.ECB:
        GSWD    R0                              ; 1ECB   0030
.EXEC.ECC:
        SWAP    R0,     2                       ; 1ECC   0044
.EXEC.ECD:
        SLR     R0,     1                       ; 1ECD   0060
.EXEC.ECE:
        INCR    R4                              ; 1ECE   000C
.EXEC.ECF:
        GSWD    R3                              ; 1ECF   0033
.EXEC.ED0:
        AND@    R1,     R1                      ; 1ED0   0389
.EXEC.ED1:
        BMI     .EXEC.F96                       ; 1ED1   020B 00C3

.EXEC.ED3:
        XORI    #$02CF, R0                      ; 1ED3   03F8 02CF
X_PLAY_CHEER1:
        PSHR    R5                              ; 1ED5   0275

X_PLAY_CHEER2:
        JSR     R5,     X_PLAY_SFX1             ; 1ED6   0004 0118 03BB
.EXEC.ED9:
        DECLE   $0279                           ; 1ED9   0279
.EXEC.EDA:
        XOR@    R5,     R5                      ; 1EDA   03ED
.EXEC.EDB:
        SUBR    R0,     R5                      ; 1EDB   0105
.EXEC.EDC:
        ANDR    R4,     R5                      ; 1EDC   01A5
.EXEC.EDD:
        SLR     R2,     1                       ; 1EDD   0062
.EXEC.EDE:
        SAR     R2,     1                       ; 1EDE   006A
.EXEC.EDF:
        XORR    R5,     R3                      ; 1EDF   01EB
.EXEC.EE0:
        EIS                                     ; 1EE0   0002
.EXEC.EE1:
        INCR    R2                              ; 1EE1   000A
.EXEC.EE2:
        INCR    R7                              ; 1EE2   000F
.EXEC.EE3:
        XORI    #$008F, R7                      ; 1EE3   03FF 008F
.EXEC.EE5:
        DECR    R3                              ; 1EE5   0013
.EXEC.EE6:
        INCR    R7                              ; 1EE6   000F
.EXEC.EE7:
        HLT                                     ; 1EE7   0000
.EXEC.EE8:
        DECR    R3                              ; 1EE8   0013
.EXEC.EE9:
        COMR    R1                              ; 1EE9   0019
.EXEC.EEA:
        DIS                                     ; 1EEA   0003
.EXEC.EEB:
        SLR     R1,     1                       ; 1EEB   0061
.EXEC.EEC:
        ADD@    R5,     R1                      ; 1EEC   02E9
.EXEC.EED:
        MVI     G_0050, R0                      ; 1EED   0280 0050
.EXEC.EEF:
        CMPR    R3,     R3                      ; 1EEF   015B
.EXEC.EF0:
        DECLE   $0001                           ; 1EF0   0001
.EXEC.EF1:
        XORI    #$03EB, R0                      ; 1EF1   03F8 03EB
.EXEC.EF3:
        DECR    R3                              ; 1EF3   0013
.EXEC.EF4:
        ADCR    R6                              ; 1EF4   002E
.EXEC.EF5:
        NEGR    R3                              ; 1EF5   0023
.EXEC.EF6:
        DECR    R6                              ; 1EF6   0016
.EXEC.EF7:
        DECLE   $0001                           ; 1EF7   0001
.EXEC.EF8:
        INCR    R4                              ; 1EF8   000C
.EXEC.EF9:
        CMPR    R5,     R3                      ; 1EF9   016B
.EXEC.EFA:
        DECLE   $0001                           ; 1EFA   0001
.EXEC.EFB:
        XOR@    R6,     R4                      ; 1EFB   03F4
.EXEC.EFC:
        ADDR    R0,     R3                      ; 1EFC   00C3
.EXEC.EFD:
        XOR@    R4,     R6                      ; 1EFD   03E6
.EXEC.EFE:
        DECLE   $0001                           ; 1EFE   0001
.EXEC.EFF:
        INCR    R0                              ; 1EFF   0008
.EXEC.F00:
        XOR@    R5,     R3                      ; 1F00   03EB
.EXEC.F01:
        ADDI    #$0157, R1                      ; 1F01   02F9 0157
.EXEC.F03:
        ADCR    R6                              ; 1F03   002E
.EXEC.F04:
        DECR    R3                              ; 1F04   0013
.EXEC.F05:
        COMR    R1                              ; 1F05   0019
.EXEC.F06:
        DIS                                     ; 1F06   0003
.EXEC.F07:
        NEGR    R5                              ; 1F07   0025
.EXEC.F08:
        ADD@    R1,     R1                      ; 1F08   02C9
.EXEC.F09:
        MVI     .BTAB.00,R0                     ; 1F09   0280 0200
.EXEC.F0B:
        SUB@    R1,     R0                      ; 1F0B   0308
.EXEC.F0C:
        MVO     R0,     G_03EB                  ; 1F0C   0240 03EB
.EXEC.F0E:
        ADDI    #$0097, R1                      ; 1F0E   02F9 0097
.EXEC.F10:
        SWAP    R0,     1                       ; 1F10   0040
.EXEC.F11:
        DIS                                     ; 1F11   0003
.EXEC.F12:
        CMP@    R2,     R4                      ; 1F12   0354
.EXEC.F13:
        XOR@    R6,     R2                      ; 1F13   03F2
.EXEC.F14:
        XORI    #$000F, R2                      ; 1F14   03FA 000F
.EXEC.F16:
        EIS                                     ; 1F16   0002
.EXEC.F17:
        MOVR    R1,     R7                      ; 1F17   008F
.EXEC.F18:
        NEGR    R7                              ; 1F18   0027
.EXEC.F19:
        XORI    #$03CF, R1                      ; 1F19   03F9 03CF
X_PLAY_WHST1:
        MVII    #$000E, R0                      ; 1F1B   02B8 000E
.EXEC.F1D:
        PSHR    R5                              ; 1F1D   0275

X_PLAY_WHST2:
        JSR     R5,     X_PLAY_SFX1             ; 1F1E   0004 0118 03BB

.EXEC.F21:
        AND@    R1,     R1                      ; 1F21   0389
X_PLAY_WHST3:
        CMP     .STIC.CS.0,R0                   ; 1F22   0340 0028
.EXEC.F24:
        CMP@    R1,     R0                      ; 1F24   0348
.EXEC.F25:
        ADCR    R1                              ; 1F25   0029
.EXEC.F26:
        CMP     .STIC.CS.2,R4                   ; 1F26   0344 002A
.EXEC.F28:
        SAR     R3,     1                       ; 1F28   006B
.EXEC.F29:
        ADD     .STIC.HDLY,R0                   ; 1F29   02C0 0030
.EXEC.F2B:
        ADD@    R6,     R5                      ; 1F2B   02F5
.EXEC.F2C:
        NEGR    R3                              ; 1F2C   0023
.EXEC.F2D:
        XOR@    R2,     R0                      ; 1F2D   03D0
.EXEC.F2E:
        ADD@    R1,     R7                      ; 1F2E   02CF
X_DO_GRAM_INIT:
        PSHR    R5                              ; 1F2F   0275

.EXEC.F30:
        JSR     R5,     X_READ_ROM_HDR          ; 1F30   0004 0110 00AB

.EXEC.F33:
        INCR    R0                              ; 1F33   0008
.EXEC.F34:
        INCR    R7                              ; 1F34   000F
X_NEW_GRAM_INIT:
        PSHR    R4                              ; 1F35   0274
.EXEC.F36:
        PSHR    R5                              ; 1F36   0275
.EXEC.F37:
        SDBD                                    ; 1F37   0001
.EXEC.F38:
        MVII    #$36DF, R3                      ; 1F38   02BB 00DF 0036
.EXEC.F3B:
        MOVR    R3,     R4                      ; 1F3B   009C
.EXEC.F3C:
        ADDI    #$003A, R4                      ; 1F3C   02FC 003A
.EXEC.F3E:
        MVII    #$0200, R5                      ; 1F3E   02BD 0200
.EXEC.F40:
        MVI@    R3,     R0                      ; 1F40   0298
.EXEC.F41:
        INCR    R3                              ; 1F41   000B
.EXEC.F42:
        MVII    #$0004, R2                      ; 1F42   02BA 0004
.EXEC.F44:
        MVI@    R4,     R1                      ; 1F44   02A1
.EXEC.F45:
        SWAP    R1,     1                       ; 1F45   0041
.EXEC.F46:
        SARC    R0,     2                       ; 1F46   007C
.EXEC.F47:
        RRC     R1,     2                       ; 1F47   0075
.EXEC.F48:
        SLR     R1,     2                       ; 1F48   0065
.EXEC.F49:
        SLR     R1,     2                       ; 1F49   0065
.EXEC.F4A:
        SLR     R1,     2                       ; 1F4A   0065
.EXEC.F4B:
        MVO@    R1,     R5                      ; 1F4B   0269
.EXEC.F4C:
        DECR    R2                              ; 1F4C   0012
.EXEC.F4D:
        BNEQ    .EXEC.F44                       ; 1F4D   022C 000A

.EXEC.F4F:
        CMPI    #$02E7, R5                      ; 1F4F   037D 02E7
.EXEC.F51:
        BLT     .EXEC.F40                       ; 1F51   0225 0012

.EXEC.F53:
        PULR    R5                              ; 1F53   02B5
.EXEC.F54:
        MVI@    R5,     R0                      ; 1F54   02A8
.EXEC.F55:
        MOVR    R5,     R3                      ; 1F55   00AB
.EXEC.F56:
        SDBD                                    ; 1F56   0001
.EXEC.F57:
        MVII    #$3800, R5                      ; 1F57   02BD 0000 0038
.EXEC.F5A:
        MOVR    R7,     R1                      ; 1F5A   00B9
.EXEC.F5B:
        DECR    R1                              ; 1F5B   0011
.EXEC.F5C:
        PSHR    R1                              ; 1F5C   0271
.EXEC.F5D:
        MVI@    R3,     R1                      ; 1F5D   0299
.EXEC.F5E:
        INCR    R3                              ; 1F5E   000B
.EXEC.F5F:
        SARC    R1,     1                       ; 1F5F   0079
.EXEC.F60:
        CLRR    R2                              ; 1F60   01D2
.EXEC.F61:
        BNC     .EXEC.F65                       ; 1F61   0209 0002

.EXEC.F63:
        MVI@    R3,     R2                      ; 1F63   029A
.EXEC.F64:
        INCR    R3                              ; 1F64   000B
.EXEC.F65:
        PSHR    R0                              ; 1F65   0270
.EXEC.F66:
        PSHR    R5                              ; 1F66   0275
.EXEC.F67:
        PSHR    R3                              ; 1F67   0273
.EXEC.F68:
        MVII    #$02E8, R4                      ; 1F68   02BC 02E8
.EXEC.F6A:
        SARC    R2,     1                       ; 1F6A   007A
.EXEC.F6B:
        BNC     .EXEC.F6F                       ; 1F6B   0209 0002

.EXEC.F6D:
        MVII    #$0213, R7                      ; 1F6D   02BF 0213
.EXEC.F6F:
        SARC    R2,     1                       ; 1F6F   007A
.EXEC.F70:
        BC      .EXEC.FB1                       ; 1F70   0201 003F

.EXEC.F72:
        SARC    R2,     1                       ; 1F72   007A
.EXEC.F73:
        BNC     .EXEC.F79                       ; 1F73   0209 0004

.EXEC.F75:
        CLRR    R3                              ; 1F75   01DB
.EXEC.F76:
        SWAP    R2,     1                       ; 1F76   0042
.EXEC.F77:
        MVII    #$0200, R7                      ; 1F77   02BF 0200

.EXEC.F79:
        JSR     R5,     .BTAB.D3                ; 1F79   0004 0100 02D3

.EXEC.F7C:
        SDBD                                    ; 1F7C   0001
.EXEC.F7D:
        MVII    #$3000, R4                      ; 1F7D   02BC 0000 0030
.EXEC.F80:
        SARC    R2,     1                       ; 1F80   007A
.EXEC.F81:
        BC      .EXEC.F92                       ; 1F81   0201 000F

.EXEC.F83:
        JSR     R5,     X_READ_ROM_HDR          ; 1F83   0004 0110 00AB

.EXEC.F86:
        CLRC                                    ; 1F86   0006
.EXEC.F87:
        MOVR    R5,     R4                      ; 1F87   00AC
.EXEC.F88:
        MOVR    R2,     R0                      ; 1F88   0090
.EXEC.F89:
        ANDI    #$0002, R0                      ; 1F89   03B8 0002
.EXEC.F8B:
        BEQ     .EXEC.F92                       ; 1F8B   0204 0005

.EXEC.F8D:
        XORR    R0,     R2                      ; 1F8D   01C2
.EXEC.F8E:
        SDBD                                    ; 1F8E   0001
.EXEC.F8F:
        MVII    #$3800, R4                      ; 1F8F   02BC 0000 0038
.EXEC.F92:
        SWAP    R1,     1                       ; 1F92   0041
.EXEC.F93:
        SLL     R1,     2                       ; 1F93   004D
.EXEC.F94:
        SARC    R2,     2                       ; 1F94   007E
.EXEC.F95:
        RRC     R1,     2                       ; 1F95   0075
.EXEC.F96:
        SWAP    R1,     1                       ; 1F96   0041
.EXEC.F97:
        MVI     .BTAB.E6,R0                     ; 1F97   0280 02E6
.EXEC.F99:
        ADDR    R0,     R1                      ; 1F99   00C1
.EXEC.F9A:
        SUBR    R0,     R2                      ; 1F9A   0102
.EXEC.F9B:
        BEQ     .EXEC.FA3                       ; 1F9B   0204 0006

.EXEC.F9D:
        PULR    R2                              ; 1F9D   02B2
.EXEC.F9E:
        SUBI    #$0002, R2                      ; 1F9E   033A 0002
.EXEC.FA0:
        PSHR    R2                              ; 1FA0   0272
.EXEC.FA1:
        MOVR    R0,     R2                      ; 1FA1   0082
.EXEC.FA2:
        INCR    R2                              ; 1FA2   000A
.EXEC.FA3:
        MVO     R2,     .BTAB.E6                ; 1FA3   0242 02E6
.EXEC.FA5:
        SLL     R1,     2                       ; 1FA5   004D
.EXEC.FA6:
        ADDR    R1,     R1                      ; 1FA6   00C9
.EXEC.FA7:
        ADDR    R1,     R4                      ; 1FA7   00CC
.EXEC.FA8:
        MVII    #$02E8, R1                      ; 1FA8   02B9 02E8
.EXEC.FAA:
        MVII    #$0008, R0                      ; 1FAA   02B8 0008

.EXEC.FAC:
        JSR     R5,     .EXEC.730               ; 1FAC   0004 0114 0330

.EXEC.FAF:
        MVII    #$0247, R7                      ; 1FAF   02BF 0247
.EXEC.FB1:
        MOVR    R1,     R0                      ; 1FB1   0088
.EXEC.FB2:
        ANDI    #$0080, R0                      ; 1FB2   03B8 0080
.EXEC.FB4:
        XORR    R0,     R1                      ; 1FB4   01C1
.EXEC.FB5:
        SARC    R2,     1                       ; 1FB5   007A
.EXEC.FB6:
        RLC     R0,     1                       ; 1FB6   0050
.EXEC.FB7:
        CLRR    R3                              ; 1FB7   01DB
.EXEC.FB8:
        SARC    R2,     2                       ; 1FB8   007E
.EXEC.FB9:
        RLC     R3,     2                       ; 1FB9   0057
.EXEC.FBA:
        SARC    R2,     1                       ; 1FBA   007A
.EXEC.FBB:
        RLC     R3,     1                       ; 1FBB   0053
.EXEC.FBC:
        SARC    R0,     1                       ; 1FBC   0078
.EXEC.FBD:
        RLC     R2,     1                       ; 1FBD   0052
.EXEC.FBE:
        SLL     R0,     2                       ; 1FBE   004C
.EXEC.FBF:
        SWAP    R0,     1                       ; 1FBF   0040
.EXEC.FC0:
        TSTR    R3                              ; 1FC0   009B
.EXEC.FC1:
        BNEQ    .EXEC.FC6                       ; 1FC1   020C 0003

.EXEC.FC3:
        MOVR    R0,     R3                      ; 1FC3   0083
.EXEC.FC4:
        SLL     R3,     2                       ; 1FC4   004F
.EXEC.FC5:
        CLRR    R0                              ; 1FC5   01C0
.EXEC.FC6:
        PSHR    R0                              ; 1FC6   0270
.EXEC.FC7:
        PSHR    R3                              ; 1FC7   0273

.EXEC.FC8:
        JSR     R5,     .BTAB.C3                ; 1FC8   0004 0100 02C3

.EXEC.FCB:
        PULR    R5                              ; 1FCB   02B5
.EXEC.FCC:
        MVII    #$0200, R0                      ; 1FCC   02B8 0200
.EXEC.FCE:
        SLR     R0,     1                       ; 1FCE   0060
.EXEC.FCF:
        DECR    R5                              ; 1FCF   0015
.EXEC.FD0:
        BPL     .EXEC.FCE                       ; 1FD0   0223 0003

.EXEC.FD2:
        SWAP    R2,     1                       ; 1FD2   0042
.EXEC.FD3:
        SLL     R1,     2                       ; 1FD3   004D
.EXEC.FD4:
        XORR    R2,     R1                      ; 1FD4   01D1
.EXEC.FD5:
        XOR@    R6,     R1                      ; 1FD5   03F1
.EXEC.FD6:
        SLL     R1,     2                       ; 1FD6   004D
.EXEC.FD7:
        SLL     R1,     2                       ; 1FD7   004D

.EXEC.FD8:
        JSR     R5,     .BTAB.DC                ; 1FD8   0004 0100 02DC

.EXEC.FDB:
        SLLC    R1,     1                       ; 1FDB   0059
.EXEC.FDC:
        BNC     .EXEC.FD8                       ; 1FDC   0229 0005

.EXEC.FDE:
        SLLC    R1,     1                       ; 1FDE   0059
.EXEC.FDF:
        BNC     .EXEC.FEE                       ; 1FDF   0209 000D

.EXEC.FE1:
        SLR     R0,     1                       ; 1FE1   0060
.EXEC.FE2:
        BNEQ    .EXEC.FE6                       ; 1FE2   020C 0002

.EXEC.FE4:
        MVII    #$0100, R0                      ; 1FE4   02B8 0100

.EXEC.FE6:
        JSR     R5,     .BTAB.DC                ; 1FE6   0004 0100 02DC

.EXEC.FE9:
        SLLC    R1,     1                       ; 1FE9   0059
.EXEC.FEA:
        BNC     .EXEC.FE1                       ; 1FEA   0229 000A
.EXEC.FEC:
        B       .EXEC.FD8                       ; 1FEC   0220 0015

.EXEC.FEE:
        SLL     R0,     1                       ; 1FEE   0048
.EXEC.FEF:
        ANDI    #$01FF, R0                      ; 1FEF   03B8 01FF
.EXEC.FF1:
        BNEQ    .EXEC.FF4                       ; 1FF1   020C 0001

.EXEC.FF3:
        INCR    R0                              ; 1FF3   0008

.EXEC.FF4:
        JSR     R5,     .BTAB.DC                ; 1FF4   0004 0100 02DC

.EXEC.FF7:
        SLLC    R1,     1                       ; 1FF7   0059
.EXEC.FF8:
        BNC     .EXEC.FEE                       ; 1FF8   0229 000B
.EXEC.FFA:
        B       .EXEC.FD8                       ; 1FFA   0220 0023

.EXEC.FFC:
        HLT                                     ; 1FFC   0000
.EXEC.FFD:
        HLT                                     ; 1FFD   0000
.EXEC.FFE:
        HLT                                     ; 1FFE   0000
.EXEC.FFF:
        HLT                                     ; 1FFF   0000
;; ======================================================================== ;;
;;  Branch cross-reference
;; ------------------------------------------------------------------------ ;;
;;  Target      Target of
;; ======================================================================== ;;
