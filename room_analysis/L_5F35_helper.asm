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

