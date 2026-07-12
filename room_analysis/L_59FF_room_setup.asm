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
