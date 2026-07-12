exprlist    EQU     0,1,2,3,4,5
            DECLE   exprlist        ; Should emit 5
            DECLE   exprlist[0,5]   ; Should emit 0,1,2,3,4,5
            DECLE   exprlist[5,0]   ; Should emit 5,4,3,2,1,0

            DECLE (1,2,3,4)[3]
            IF  (1,2,3,4)[3] = 4
                ; This branch should be taken
                DECLE   $ABCD
            ELSE
                ERR "This should not happen
            ENDI

            ; exprlist[1,4] should also be 1,2,3,4... so we should get the
            ; same outcome as above.
            DECLE (exprlist[1,4])[3]
            IF  (exprlist[1,4])[3] = 4
                ; This branch should be taken
                DECLE   $ABCD
            ELSE
                ERR "This should not happen
            ENDI

            DECLE   ("ABCD")[0]     ; Should output $41
            DECLE   ("ABCD")[1]     ; Should output $42
            DECLE   ("ABCD")[2]     ; Should output $43
            DECLE   ("ABCD")[3]     ; Should output $44

two_d[0]    EQU     0,1,2,3,4
two_d[1]    EQU     5,6,7
two_d[2]    EQU     8,9

            DECLE   two_d           ; Should output 2
            DECLE   two_d[0]        ; Should output 4
            DECLE   two_d[1]        ; Should output 2
            DECLE   two_d[2]        ; Should output 1
            DECLE   two_d[0][4]     ; Should output 4
            DECLE   two_d[1][2,0]   ; Should output 7,6,5

            ; We can also take exprlist slices.
            DECLE   (0,1,2,3,4,5,6,7,8,9)[7,3]  ; Outputs: 7,6,5,4,3
            DECLE   ("Hello World!")[0,5]       ; Outputs "Hello "
            DECLE   ("Hello World!")[6,10]      ; Outputs "World!"

