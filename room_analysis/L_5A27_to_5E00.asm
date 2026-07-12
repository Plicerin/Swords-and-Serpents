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

        DECLE   $0058,  $0019,  $00B8,  $0020   ; 5A40   0058 0019 00B8 0020
        DECLE   $0007,  $0000,  $0028,  $005B   ; 5A44   0007 0000 0028 005B
        DECLE   $0000,  $0000,  $0000,  $0000   ; 5A48   0000 0000 0000 0000
        DECLE   $0000,  $0000,  $0000,  $0069   ; 5A4C   0000 0000 0000 0069
        DECLE   $0080,  $0040,  $0001           ; 5A50   0080 0040 0001

        NEGR    R0                              ; 5A53   0020
        SIN                                     ; 5A54   0036
        SLLC    R3,     1                       ; 5A55   005B
        HLT                                     ; 5A56   0000
        HLT                                     ; 5A57   0000
        HLT                                     ; 5A58   0000
        HLT                                     ; 5A59   0000
        INCR    R0                              ; 5A5A   0008
        HLT                                     ; 5A5B   0000
        HLT                                     ; 5A5C   0000
        MOVR    R2,     R0                      ; 5A5D   0090
        TSTR    R0                              ; 5A5E   0080
        MOVR    R4,     R0                      ; 5A5F   00A0
        TCI                                     ; 5A60   0005
        DECR    R0                              ; 5A61   0010
        SLLC    R2,     2                       ; 5A62   005E
        SLLC    R3,     1                       ; 5A63   005B
        HLT                                     ; 5A64   0000
        HLT                                     ; 5A65   0000
        HLT                                     ; 5A66   0000
        HLT                                     ; 5A67   0000
        HLT                                     ; 5A68   0000
        HLT                                     ; 5A69   0000
        HLT                                     ; 5A6A   0000
        ADDR    R4,     R0                      ; 5A6B   00E0
        HLT                                     ; 5A6C   0000
        ADDR    R0,     R0                      ; 5A6D   00C0

        JSR     R4,     .EXEC.066               ; 5A6E   0004 0010 0066

        SLLC    R3,     1                       ; 5A71   005B
        DECR    R0                              ; 5A72   0010
        HLT                                     ; 5A73   0000
        HLT                                     ; 5A74   0000
        HLT                                     ; 5A75   0000
        HLT                                     ; 5A76   0000
        HLT                                     ; 5A77   0000
        HLT                                     ; 5A78   0000
        HLT                                     ; 5A79   0000
        HLT                                     ; 5A7A   0000
        COMR    R0                              ; 5A7B   0018
        COMR    R0                              ; 5A7C   0018
        HLT                                     ; 5A7D   0000
        HLT                                     ; 5A7E   0000
        HLT                                     ; 5A7F   0000
        HLT                                     ; 5A80   0000
        HLT                                     ; 5A81   0000
        HLT                                     ; 5A82   0000
        HLT                                     ; 5A83   0000
        HLT                                     ; 5A84   0000
        HLT                                     ; 5A85   0000
        HLT                                     ; 5A86   0000
        HLT                                     ; 5A87   0000
        HLT                                     ; 5A88   0000
        HLT                                     ; 5A89   0000
        DECR    R4                              ; 5A8A   0014
        ADCR    R0                              ; 5A8B   0028
        INCR    R0                              ; 5A8C   0008
        NEGR    R4                              ; 5A8D   0024
        HLT                                     ; 5A8E   0000
        HLT                                     ; 5A8F   0000
        HLT                                     ; 5A90   0000
        HLT                                     ; 5A91   0000
        HLT                                     ; 5A92   0000
        HLT                                     ; 5A93   0000
        MOVR    R0,     R1                      ; 5A94   0081

        JSR     R4,     .ECSRAM.010             ; 5A95   0004 0040 0010

        HLT                                     ; 5A98   0000
        SWAP    R1,     1                       ; 5A99   0041
        HLT                                     ; 5A9A   0000
        TSTR    R0                              ; 5A9B   0080

        JSR     R4,     G_0040                  ; 5A9C   0004 0000 0040
        JSR     R4,     G_2000                  ; 5A9F   0004 0020 0000
        DECLE   $0001                           ; 5AA2   0001

        TSTR    R0                              ; 5AA3   0080
        SWAP    R1,     1                       ; 5AA4   0041
        TSTR    R0                              ; 5AA5   0080
        HLT                                     ; 5AA6   0000
        HLT                                     ; 5AA7   0000
        HLT                                     ; 5AA8   0000
        HLT                                     ; 5AA9   0000
        HLT                                     ; 5AAA   0000
        HLT                                     ; 5AAB   0000
        HLT                                     ; 5AAC   0000
        HLT                                     ; 5AAD   0000
        HLT                                     ; 5AAE   0000
        HLT                                     ; 5AAF   0000
        HLT                                     ; 5AB0   0000
        HLT                                     ; 5AB1   0000
        HLT                                     ; 5AB2   0000
        MOVR    R0,     R2                      ; 5AB3   0082
        HLT                                     ; 5AB4   0000
        MOVR    R3,     R1                      ; 5AB5   0099
        TSTR    R0                              ; 5AB6   0080
        MOVR    R4,     R0                      ; 5AB7   00A0
        HLT                                     ; 5AB8   0000
        NEGR    R0                              ; 5AB9   0020
        GSWD    R0                              ; 5ABA   0030
        SLLC    R3,     1                       ; 5ABB   005B
        HLT                                     ; 5ABC   0000
        HLT                                     ; 5ABD   0000
        HLT                                     ; 5ABE   0000
        HLT                                     ; 5ABF   0000
        HLT                                     ; 5AC0   0000
        HLT                                     ; 5AC1   0000
        HLT                                     ; 5AC2   0000
        ADDR    R1,     R1                      ; 5AC3   00C9
        TSTR    R0                              ; 5AC4   0080
        ADDR    R0,     R0                      ; 5AC5   00C0
        HLT                                     ; 5AC6   0000
        NEGR    R0                              ; 5AC7   0020
        SLL     R0,     1                       ; 5AC8   0048
        SLLC    R3,     1                       ; 5AC9   005B
        HLT                                     ; 5ACA   0000
        HLT                                     ; 5ACB   0000
        HLT                                     ; 5ACC   0000
        HLT                                     ; 5ACD   0000
        INCR    R0                              ; 5ACE   0008
        HLT                                     ; 5ACF   0000
        HLT                                     ; 5AD0   0000
        MOVR    R3,     R0                      ; 5AD1   0098
        TSTR    R0                              ; 5AD2   0080
        MOVR    R4,     R0                      ; 5AD3   00A0
        SETC                                    ; 5AD4   0007
        HLT                                     ; 5AD5   0000
        RRC     R2,     2                       ; 5AD6   0076
        SLLC    R3,     1                       ; 5AD7   005B
        NEGR    R0                              ; 5AD8   0020
        HLT                                     ; 5AD9   0000
        ADCR    R0                              ; 5ADA   0028
        HLT                                     ; 5ADB   0000
        HLT                                     ; 5ADC   0000
        HLT                                     ; 5ADD   0000
        HLT                                     ; 5ADE   0000
        ADDR    R0,     R1                      ; 5ADF   00C1
        TSTR    R0                              ; 5AE0   0080
        ADDR    R0,     R0                      ; 5AE1   00C0
        CLRC                                    ; 5AE2   0006
        HLT                                     ; 5AE3   0000
        MOVR    R0,     R2                      ; 5AE4   0082
        SLLC    R3,     1                       ; 5AE5   005B
        DECR    R0                              ; 5AE6   0010
        HLT                                     ; 5AE7   0000
        HLT                                     ; 5AE8   0000
        HLT                                     ; 5AE9   0000
        HLT                                     ; 5AEA   0000
        HLT                                     ; 5AEB   0000
        COMR    R0                              ; 5AEC   0018
        NEGR    R4                              ; 5AED   0024
        RSWD    R4                              ; 5AEE   003C
        SLR     R2,     2                       ; 5AEF   0066
        SLR     R2,     2                       ; 5AF0   0066
        RSWD    R4                              ; 5AF1   003C
        NEGR    R4                              ; 5AF2   0024
        COMR    R0                              ; 5AF3   0018
        HLT                                     ; 5AF4   0000
        HLT                                     ; 5AF5   0000
        HLT                                     ; 5AF6   0000
        HLT                                     ; 5AF7   0000
        HLT                                     ; 5AF8   0000
        HLT                                     ; 5AF9   0000
        HLT                                     ; 5AFA   0000
        SWAP    R2,     1                       ; 5AFB   0042
        COMR    R0                              ; 5AFC   0018
        NEGR    R4                              ; 5AFD   0024
        NEGR    R4                              ; 5AFE   0024
        SLLC    R2,     1                       ; 5AFF   005A
        SLLC    R2,     1                       ; 5B00   005A
        NEGR    R4                              ; 5B01   0024
        NEGR    R4                              ; 5B02   0024
        COMR    R0                              ; 5B03   0018
        SWAP    R2,     1                       ; 5B04   0042
        HLT                                     ; 5B05   0000
        HLT                                     ; 5B06   0000
        HLT                                     ; 5B07   0000
        HLT                                     ; 5B08   0000
        HLT                                     ; 5B09   0000
        COMR    R0                              ; 5B0A   0018
        HLT                                     ; 5B0B   0000
        SWAP    R2,     1                       ; 5B0C   0042
        HLT                                     ; 5B0D   0000
        COMR    R0                              ; 5B0E   0018
        MOVR    R7,     R5                      ; 5B0F   00BD
        MOVR    R7,     R5                      ; 5B10   00BD
        COMR    R0                              ; 5B11   0018
        HLT                                     ; 5B12   0000
        SWAP    R2,     1                       ; 5B13   0042
        HLT                                     ; 5B14   0000
        COMR    R0                              ; 5B15   0018
        HLT                                     ; 5B16   0000
        HLT                                     ; 5B17   0000
        SWAP    R2,     1                       ; 5B18   0042
        HLT                                     ; 5B19   0000
        HLT                                     ; 5B1A   0000
        MOVR    R0,     R1                      ; 5B1B   0081
        HLT                                     ; 5B1C   0000
        MOVR    R4,     R5                      ; 5B1D   00A5
        COMR    R0                              ; 5B1E   0018
        RSWD    R4                              ; 5B1F   003C
        RSWD    R4                              ; 5B20   003C
        COMR    R0                              ; 5B21   0018
        MOVR    R4,     R5                      ; 5B22   00A5
        HLT                                     ; 5B23   0000
        MOVR    R0,     R1                      ; 5B24   0081
        HLT                                     ; 5B25   0000
        HLT                                     ; 5B26   0000
        SWAP    R2,     1                       ; 5B27   0042
        SLR     R3,     2                       ; 5B28   0067
        SLLC    R1,     2                       ; 5B29   005D
        ADDR    R1,     R6                      ; 5B2A   00CE
        SLLC    R3,     1                       ; 5B2B   005B
        TCI                                     ; 5B2C   0005
        SUBR    R0,     R0                      ; 5B2D   0100
        SARC    R1,     1                       ; 5B2E   0079
        SLR     R2,     2                       ; 5B2F   0066
        ADDR    R6,     R0                      ; 5B30   00F0
        SAR     R2,     1                       ; 5B31   006A
        ADDR    R1,     R6                      ; 5B32   00CE
        SLLC    R3,     1                       ; 5B33   005B
        TCI                                     ; 5B34   0005
        HLT                                     ; 5B35   0000
        ADDR    R4,     R7                      ; 5B36   00E7

        SLLC    R1,     2                       ; 5B37   005D
        RLC     R0,     1                       ; 5B38   0050
        SLLC    R0,     2                       ; 5B39   005C
        TCI                                     ; 5B3A   0005
        ADDR    R7,     R4                      ; 5B3B   00FC
        SLR     R2,     1                       ; 5B3C   0062
        SLR     R3,     2                       ; 5B3D   0067
        SLR     R2,     1                       ; 5B3E   0062
        SLR     R3,     2                       ; 5B3F   0067
        SLR     R2,     1                       ; 5B40   0062
        SLR     R3,     2                       ; 5B41   0067
        SLR     R2,     1                       ; 5B42   0062
        SLR     R3,     2                       ; 5B43   0067
        SLR     R2,     1                       ; 5B44   0062
        SLR     R3,     2                       ; 5B45   0067
        SLR     R2,     1                       ; 5B46   0062
        SLR     R3,     2                       ; 5B47   0067
        NEGR    R4                              ; 5B48   0024
        SLLC    R1,     2                       ; 5B49   005D
        RLC     R0,     1                       ; 5B4A   0050
        SLLC    R0,     2                       ; 5B4B   005C
        TCI                                     ; 5B4C   0005
        RLC     R3,     2                       ; 5B4D   0057
        SLR     R2,     1                       ; 5B4E   0062
        SLR     R3,     2                       ; 5B4F   0067
        SLR     R2,     1                       ; 5B50   0062
        SLR     R3,     2                       ; 5B51   0067
        SLR     R2,     1                       ; 5B52   0062
        SLR     R3,     2                       ; 5B53   0067
        SLR     R2,     1                       ; 5B54   0062
        SLR     R3,     2                       ; 5B55   0067
        SLR     R2,     1                       ; 5B56   0062
        SLR     R3,     2                       ; 5B57   0067
        SLLC    R1,     1                       ; 5B58   0059
        SLLC    R1,     2                       ; 5B59   005D
        RLC     R0,     1                       ; 5B5A   0050
        SLLC    R0,     2                       ; 5B5B   005C
        TCI                                     ; 5B5C   0005
        HLT                                     ; 5B5D   0000
        ADDR    R4,     R1                      ; 5B5E   00E1
        SLLC    R1,     2                       ; 5B5F   005D
        MOVR    R4,     R0                      ; 5B60   00A0
        SLLC    R0,     2                       ; 5B61   005C
        TCI                                     ; 5B62   0005
        SUBR    R0,     R0                      ; 5B63   0100
        ADDR    R1,     R3                      ; 5B64   00CB
        SLR     R2,     2                       ; 5B65   0066
        HLT                                     ; 5B66   0000
        HLT                                     ; 5B67   0000
        ADDR    R6,     R0                      ; 5B68   00F0
        SLLC    R0,     2                       ; 5B69   005C
        DIS                                     ; 5B6A   0003
        CMP@    R2,     R1                      ; 5B6B   0351
        RSWD    R2                              ; 5B6C   003A
        SLR     R1,     1                       ; 5B6D   0061
        RSWD    R2                              ; 5B6E   003A
        SLR     R1,     1                       ; 5B6F   0061
        RSWD    R2                              ; 5B70   003A
        SLR     R1,     1                       ; 5B71   0061
        MOVR    R6,     R5                      ; 5B72   00B5
        SLR     R1,     1                       ; 5B73   0061
        ADDR    R2,     R1                      ; 5B74   00D1
        SLR     R1,     1                       ; 5B75   0061
        COMR    R7                              ; 5B76   001F

        SAR     R3,     1                       ; 5B77   006B
        ADDR    R5,     R0                      ; 5B78   00E8
        SLLC    R2,     1                       ; 5B79   005A

        JSR     R4,     G_0077                  ; 5B7A   0004 0000 0077

        SAR     R3,     1                       ; 5B7D   006B
        MOVR    R4,     R0                      ; 5B7E   00A0
        SLLC    R0,     2                       ; 5B7F   005C
        TCI                                     ; 5B80   0005
        HLT                                     ; 5B81   0000
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

        SLR     R3,     2                       ; 5B91   0067
        NEGR    R1                              ; 5B92   0021
        SAR     R1,     1                       ; 5B93   0069
        MOVR    R2,     R3                      ; 5B94   0093
        SAR     R0,     1                       ; 5B95   0068
        RRC     R0,     2                       ; 5B96   0074
        SLLC    R2,     1                       ; 5B97   005A

        JSR     R4,     G_007F                  ; 5B98   0004 0000 007F

        SLLC    R1,     2                       ; 5B9B   005D
        RRC     R0,     2                       ; 5B9C   0074
        SLLC    R2,     1                       ; 5B9D   005A

        JSR     R4,     G_004B                  ; 5B9E   0004 0000 004B

        SLLC    R1,     2                       ; 5BA1   005D
        COMR    R6                              ; 5BA2   001E
        SLLC    R0,     2                       ; 5BA3   005C
        DIS                                     ; 5BA4   0003
        MVO@    R1,     R2                      ; 5BA5   0251
        RSWD    R2                              ; 5BA6   003A
        SLR     R1,     1                       ; 5BA7   0061
        RSWD    R2                              ; 5BA8   003A
        SLR     R1,     1                       ; 5BA9   0061
        RSWD    R2                              ; 5BAA   003A
        SLR     R1,     1                       ; 5BAB   0061
        ADDR    R2,     R1                      ; 5BAC   00D1
        SLR     R1,     1                       ; 5BAD   0061
        INCR    R0                              ; 5BAE   0008
        HLT                                     ; 5BAF   0000
        INCR    R0                              ; 5BB0   0008
        XORI    #$0007, R6                      ; 5BB1   03FE 0007
        XORI    #$0003, R1                      ; 5BB3   03F9 0003
        XORI    #$0000, R0                      ; 5BB5   03F8 0000
        XORI    #$03FD, R0                      ; 5BB7   03F8 03FD
        XORI    #$03F9, R0                      ; 5BB9   03F8 03F9
        XORI    #$03F8, R1                      ; 5BBB   03F9 03F8
        XORI    #$03F8, R6                      ; 5BBD   03FE 03F8
        HLT                                     ; 5BBF   0000
        XORI    #$0002, R0                      ; 5BC0   03F8 0002
        XORI    #$0007, R1                      ; 5BC2   03F9 0007
        XORI    #$0008, R5                      ; 5BC4   03FD 0008
        HLT                                     ; 5BC6   0000
        INCR    R0                              ; 5BC7   0008
        DIS                                     ; 5BC8   0003
        INCR    R0                              ; 5BC9   0008
        SETC                                    ; 5BCA   0007
        SETC                                    ; 5BCB   0007
        INCR    R0                              ; 5BCC   0008
        EIS                                     ; 5BCD   0002
        COMR    R0                              ; 5BCE   0018
        RSWD    R4                              ; 5BCF   003C
        SARC    R2,     2                       ; 5BD0   007E
        RRC     R3,     1                       ; 5BD1   0073
        ADDR    R7,     R1                      ; 5BD2   00F9
        MOVR    R3,     R1                      ; 5BD3   0099
        TSTR    R1                              ; 5BD4   0089
        TSTR    R1                              ; 5BD5   0089
        TSTR    R1                              ; 5BD6   0089
        TSTR    R1                              ; 5BD7   0089
        MOVR    R3,     R1                      ; 5BD8   0099
        ADDR    R7,     R1                      ; 5BD9   00F9
        RRC     R3,     1                       ; 5BDA   0073
        SARC    R2,     2                       ; 5BDB   007E
        RSWD    R4                              ; 5BDC   003C
        COMR    R0                              ; 5BDD   0018
        COMR    R6                              ; 5BDE   001E
        RSWD    R6                              ; 5BDF   003E
        GSWD    R3                              ; 5BE0   0033
        SARC    R3,     1                       ; 5BE1   007B
        SARC    R1,     1                       ; 5BE2   0079
        ADDR    R5,     R0                      ; 5BE3   00E8
        TSTR    R1                              ; 5BE4   0089
        TSTR    R1                              ; 5BE5   0089
        TSTR    R1                              ; 5BE6   0089
        MOVR    R1,     R3                      ; 5BE7   008B
        MOVR    R3,     R2                      ; 5BE8   009A
        ADDR    R3,     R2                      ; 5BE9   00DA
        ADDR    R7,     R6                      ; 5BEA   00FE
        SARC    R0,     2                       ; 5BEB   007C
        SARC    R0,     2                       ; 5BEC   007C
        COMR    R4                              ; 5BED   001C
        COMR    R4                              ; 5BEE   001C
        COMR    R4                              ; 5BEF   001C
        GSWD    R2                              ; 5BF0   0032
        GSWD    R2                              ; 5BF1   0032
        SLR     R1,     1                       ; 5BF2   0061
        SLR     R1,     1                       ; 5BF3   0061
        ADDR    R6,     R1                      ; 5BF4   00F1
        MOVR    R7,     R1                      ; 5BF5   00B9
        MOVR    R1,     R3                      ; 5BF6   008B
        MOVR    R1,     R2                      ; 5BF7   008A
        MOVR    R1,     R6                      ; 5BF8   008E
        MOVR    R1,     R6                      ; 5BF9   008E
        ADDR    R0,     R4                      ; 5BFA   00C4
        SARC    R0,     2                       ; 5BFB   007C
        SARC    R0,     1                       ; 5BFC   0078
        GSWD    R0                              ; 5BFD   0030
        RSWD    R3                              ; 5BFE   003B
        RSWD    R3                              ; 5BFF   003B
        SLR     R1,     1                       ; 5C00   0061
        SLR     R1,     1                       ; 5C01   0061
        ADDR    R0,     R1                      ; 5C02   00C1
        ADDR    R0,     R3                      ; 5C03   00C3
        ADDR    R7,     R3                      ; 5C04   00FB
        ADDR    R7,     R7                      ; 5C05   00FF
        MOVR    R1,     R7                      ; 5C06   008F

        MOVR    R0,     R6                      ; 5C07   0086
        MOVR    R0,     R6                      ; 5C08   0086
        ADDR    R0,     R4                      ; 5C09   00C4
        SLR     R0,     2                       ; 5C0A   0064
        SARC    R0,     2                       ; 5C0B   007C
        RSWD    R0                              ; 5C0C   0038
        RSWD    R0                              ; 5C0D   0038
        RSWD    R4                              ; 5C0E   003C
        SARC    R2,     2                       ; 5C0F   007E
        SWAP    R2,     1                       ; 5C10   0042
        SWAP    R2,     1                       ; 5C11   0042
        ADDR    R0,     R3                      ; 5C12   00C3
        MOVR    R0,     R1                      ; 5C13   0081
        MOVR    R7,     R3                      ; 5C14   00BB
        ADDR    R7,     R7                      ; 5C15   00FF
        ADDR    R4,     R7                      ; 5C16   00E7

        DECLE   $00C3,  $00C3,  $00C3,  $0042   ; 5C17   00C3 00C3 00C3 0042
        DECLE   $007E,  $003C,  $003C,  $0000   ; 5C1B   007E 003C 003C 0000
        DECLE   $0024,  $0011,  $003A,  $00AE   ; 5C1F   0024 0011 003A 00AE
        DECLE   $007B,  $006E,  $00FE,  $007F   ; 5C23   007B 006E 00FE 007F
        DECLE   $007C,  $00FE,  $005C,  $0088   ; 5C27   007C 00FE 005C 0088
        DECLE   $0024,  $0000,  $0000,  $0000   ; 5C2B   0024 0000 0000 0000
        DECLE   $0001                           ; 5C2F   0001

        RLC     R0,     2                       ; 5C30   0054
        COMR    R6                              ; 5C31   001E
        SARC    R3,     2                       ; 5C32   007F
        ADDR    R7,     R2                      ; 5C33   00FA
        SARC    R3,     2                       ; 5C34   007F
        SARC    R3,     1                       ; 5C35   007B
        ADDR    R7,     R6                      ; 5C36   00FE
        SARC    R2,     2                       ; 5C37   007E
        TSTR    R6                              ; 5C38   00B6
        SLLC    R1,     2                       ; 5C39   005D
        NEGR    R4                              ; 5C3A   0024
        SWAP    R0,     1                       ; 5C3B   0040
        DECR    R0                              ; 5C3C   0010
        HLT                                     ; 5C3D   0000
        DECR    R0                              ; 5C3E   0010
        HLT                                     ; 5C3F   0000
        NEGR    R0                              ; 5C40   0020
        COMR    R4                              ; 5C41   001C
        SLLC    R3,     2                       ; 5C42   005F
        SARC    R2,     2                       ; 5C43   007E
        SARC    R2,     2                       ; 5C44   007E
        ADDR    R7,     R3                      ; 5C45   00FB
        SLLC    R2,     2                       ; 5C46   005E
        SARC    R3,     1                       ; 5C47   007B
        MOVR    R7,     R6                      ; 5C48   00BE
        SARC    R0,     2                       ; 5C49   007C
        MOVR    R1,     R2                      ; 5C4A   008A
        DECR    R0                              ; 5C4B   0010
        HLT                                     ; 5C4C   0000
        HLT                                     ; 5C4D   0000
        MOVR    R0,     R4                      ; 5C4E   0084
        RLC     R2,     2                       ; 5C4F   0056
        HLT                                     ; 5C50   0000
        HLT                                     ; 5C51   0000
        HLT                                     ; 5C52   0000
        HLT                                     ; 5C53   0000
        HLT                                     ; 5C54   0000
        HLT                                     ; 5C55   0000
        HLT                                     ; 5C56   0000
        ADDR    R7,     R7                      ; 5C57   00FF

        HLT                                     ; 5C58   0000
        HLT                                     ; 5C59   0000
        HLT                                     ; 5C5A   0000
        HLT                                     ; 5C5B   0000
        HLT                                     ; 5C5C   0000
        HLT                                     ; 5C5D   0000
        HLT                                     ; 5C5E   0000
        HLT                                     ; 5C5F   0000
        HLT                                     ; 5C60   0000
        HLT                                     ; 5C61   0000
        HLT                                     ; 5C62   0000
        HLT                                     ; 5C63   0000
        HLT                                     ; 5C64   0000
        CLRC                                    ; 5C65   0006
        INCR    R4                              ; 5C66   000C
        GSWD    R0                              ; 5C67   0030
        SLR     R0,     1                       ; 5C68   0060
        ADDR    R0,     R0                      ; 5C69   00C0
        HLT                                     ; 5C6A   0000
        HLT                                     ; 5C6B   0000
        HLT                                     ; 5C6C   0000
        HLT                                     ; 5C6D   0000
        HLT                                     ; 5C6E   0000
        HLT                                     ; 5C6F   0000
        HLT                                     ; 5C70   0000
        HLT                                     ; 5C71   0000
        HLT                                     ; 5C72   0000
        HLT                                     ; 5C73   0000

        JSR     R4,     G_0408                  ; 5C74   0004 0004 0008
        DECLE   $0008,  $0010,  $0010,  $0020   ; 5C77   0008 0010 0010 0020
        DECLE   $0020,  $0040,  $0040,  $0080   ; 5C7B   0020 0040 0040 0080
        DECLE   $0080,  $0000,  $0000,  $0000   ; 5C7F   0080 0000 0000 0000
        DECLE   $0000,  $0008,  $0008,  $0008   ; 5C83   0000 0008 0008 0008
        DECLE   $0008,  $0010,  $0010,  $0010   ; 5C87   0008 0010 0010 0010
        DECLE   $0010,  $0020,  $0020,  $0020   ; 5C8B   0010 0020 0020 0020
        DECLE   $0020,  $0000,  $0000,  $0010   ; 5C8F   0020 0000 0000 0010
        DECLE   $0010,  $0010,  $0010,  $0010   ; 5C93   0010 0010 0010 0010
        DECLE   $0010,  $0010,  $0010,  $0010   ; 5C97   0010 0010 0010 0010
        DECLE   $0010,  $0010,  $0010,  $0010   ; 5C9B   0010 0010 0010 0010
        DECLE   $0010,  $006D,  $003E,  $007F   ; 5C9F   0010 006D 003E 007F
        DECLE   $00F6,  $00F1,  $00D8,  $0088   ; 5CA3   00F6 00F1 00D8 0088
        DECLE   $00A8,  $00A8,  $0088,  $00D8   ; 5CA7   00A8 00A8 0088 00D8
        DECLE   $00F1,  $00F6,  $007F,  $003E   ; 5CAB   00F1 00F6 007F 003E
        DECLE   $006D,  $0002,  $0025,  $006E   ; 5CAF   006D 0002 0025 006E
        DECLE   $003F                           ; 5CB3   003F

        SARC    R0,     2                       ; 5CB4   007C
        ADDR    R6,     R4                      ; 5CB5   00F4
        MOVR    R3,     R0                      ; 5CB6   0098
        MOVR    R3,     R0                      ; 5CB7   0098
        MOVR    R5,     R0                      ; 5CB8   00A8
        MOVR    R5,     R2                      ; 5CB9   00AA
        MOVR    R1,     R5                      ; 5CBA   008D
        SARC    R2,     1                       ; 5CBB   007A
        TSTR    R7                              ; 5CBC   00BF

        COMR    R6                              ; 5CBD   001E
        NOP                                     ; 5CBE   0034
        HLT                                     ; 5CBF   0000
        TCI                                     ; 5CC0   0005
        INCR    R6                              ; 5CC1   000E
        DECR    R6                              ; 5CC2   0016
        RSWD    R6                              ; 5CC3   003E
        COMR    R4                              ; 5CC4   001C
        ADDR    R7,     R0                      ; 5CC5   00F8
        RLC     R0,     1                       ; 5CC6   0050
        MOVR    R1,     R2                      ; 5CC7   008A
        TSTR    R5                              ; 5CC8   00AD
        MOVR    R5,     R2                      ; 5CC9   00AA
        ADDR    R1,     R2                      ; 5CCA   00CA
        ADDR    R7,     R7                      ; 5CCB   00FF
        ADDR    R7,     R7                      ; 5CCC   00FF

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

        SWAP    R3,     2                       ; 5CDC   0047
        ADDR    R7,     R5                      ; 5CDD   00FD
        GSWD    R0                              ; 5CDE   0030
        HLT                                     ; 5CDF   0000
        MOVR    R4,     R5                      ; 5CE0   00A5
        SWAP    R2,     1                       ; 5CE1   0042
        SWAP    R2,     1                       ; 5CE2   0042
        ADDR    R6,     R7                      ; 5CE3   00F7
        ADDR    R6,     R7                      ; 5CE4   00F7

        ADDR    R4,     R3                      ; 5CE5   00E3
        SLR     R2,     2                       ; 5CE6   0066
        SARC    R2,     2                       ; 5CE7   007E
        ADDR    R4,     R3                      ; 5CE8   00E3
        ADDR    R4,     R3                      ; 5CE9   00E3
        ADDR    R5,     R3                      ; 5CEA   00EB
        ADDR    R5,     R3                      ; 5CEB   00EB
        ADDR    R4,     R7                      ; 5CEC   00E7

        MOVR    R7,     R5                      ; 5CED   00BD
        RSWD    R4                              ; 5CEE   003C
        RSWD    R4                              ; 5CEF   003C
        HLT                                     ; 5CF0   0000
        HLT                                     ; 5CF1   0000
        HLT                                     ; 5CF2   0000
        DECR    R0                              ; 5CF3   0010
        RSWD    R0                              ; 5CF4   0038
        DECR    R0                              ; 5CF5   0010
        HLT                                     ; 5CF6   0000
        HLT                                     ; 5CF7   0000
        HLT                                     ; 5CF8   0000
        HLT                                     ; 5CF9   0000
        INCR    R0                              ; 5CFA   0008
        DECR    R0                              ; 5CFB   0010
        RLC     R0,     2                       ; 5CFC   0054
        DECR    R0                              ; 5CFD   0010
        NEGR    R0                              ; 5CFE   0020
        HLT                                     ; 5CFF   0000
        HLT                                     ; 5D00   0000
        HLT                                     ; 5D01   0000
        ADCR    R0                              ; 5D02   0028
        TSTR    R2                              ; 5D03   0092
        SWAP    R0,     2                       ; 5D04   0044
        TSTR    R2                              ; 5D05   0092
        ADCR    R0                              ; 5D06   0028
        HLT                                     ; 5D07   0000
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

