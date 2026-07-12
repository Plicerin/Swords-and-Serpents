NN          SCRATCH 1
.           DECLE   . +  8, $5449
            DECLE   . + 11, $3348
            DECLE   . + 15, $6449
            DECLE   . + 18, $2247
            S16     "MILD"
            S16     "MEDIUM"
            S16     "HOT\x0F"; $14F, 0, 
            S16     "HABANERO\x0F"; $14F, 0

SHOW        PROC
            MVI     NN,     R0
            TSTR    R0
            BEQ     @@leave

            MVI     COURSE, R1

            MVII    #$980 + C_TAN, R0
            CMPI    #6,     R1
            BLT     @@a
            DECR    R0
@@a

            MVII    #disp_ptr(2, 9), R4
            MVO@    R0,     R4
            ADDI    #24,    R0
            MVO@    R0,     R4

            MVII    #$988 + C_TAN, R0
            CMPI    #4,     R1
            BLT     @@b
            DECR    R0
@@b

            MVII    #disp_ptr(3, 9), R4
            MVO@    R0,     R4
            ADDI    #24,    R0
            MVO@    R0,     R4

            MVII    #disp_ptr(4,10), R4
            MVII    #$990 + C_TAN, R0
            CMPI    #2,     R1
            BLT     @@c
            DECR    R0
@@c
            MVO@    R0,     R4

@@leave     JR      R5
            ENDP

