;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Sound Effects and Music Data                                             ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  SFXI    Macro for generating an SFXINI (init) table entry.              ;;
;;  SFXT    Macro for generating an SFXIND (thinker) table entry.           ;;
;; ======================================================================== ;;
MACRO   SFXI    fxn, t, n, v, i, b

        DECLE   ($F AND (%b%)) OR (($1E AND (%n%)) SHL 3) OR (($FF AND (%i%)) SHL 8)
        DECLE   (($F AND (%v%)) SHL 12) OR ($FFF AND (%t%))
ENDM
MACRO   SFXT    fxn
@@%fxn% DECLE   SFX%fxn%
FX%fxn% EQU     $ - SFXIND
ENDM




;; ======================================================================== ;;
;;  SFXINI  Indirection table for SFX initializers                          ;;
;;  SFXIND  Indirection table for SFX thinkers                              ;;
;; ======================================================================== ;;
SFXINI      PROC
SFXI        BFIRE,  $03A, $000, $8, $00, $F
SFXI        SMEXP,  $888, $01E, $B, $07, $C ; MC only
SFXI        JUMP2,  $A04, $000, $D, $07, $3 ; ... ECS only or both?
SFXI        ALIEN,  $0BE, $000, $A, $00, $F
SFXI        LGEXP,  $BBB, $01E, $D, $07, $C ; MC only
SFXI        DING,   $098, $000, $D, $34, $F
SFXI        JUMP,   $0BE, $000, $C, $07, $F
SFXI        PLANT,  $55E, $000, $B, $00, $3 ; ECS only
SFXI        SAUC,   $06B, $000, $9, $00, $3 ; ECS only
SFXI        DIED,   $000, $010, $D, $20, $C ; MC only.
SFXI        SKID,   $0AA, $000, $D, $30, $C ; MC only
            ENDP

SFXIND      PROC
SFXT        BFIRE
SFXT        SMEXP
SFXT        JUMP2
SFXT        ALIEN
SFXT        LGEXP
SFXT        DING
SFXT        JUMP
SFXT        PLANT
SFXT        SAUC
SFXT        DIED
SFXT        SKID
            ENDP

;; ======================================================================== ;;
;;  SFXPLANT -- Doodle Doodle Deedle Doodle                                 ;;
;; ======================================================================== ;;
SFXPLANT    PROC
            ; Note sequence:  a, b, c, b, d, b, c, b

@@a         EQU     $2CF*2
@@b         EQU     $2A7*2
@@c         EQU     $271*2
@@d         EQU     $25D*2

            MVI@    R4,     R1
            DECR    R4
            INCR    R1
            MVO@    R1,     R4
            DECR    R4

            MOVR    R1,     R0
            ANDI    #7,     R0
            BNEQ    SFXRET

            CALL    SFXGET

            SARC    R1,     2
            SARC    R1,     1
            ANDI    #7,     R1
            BNEQ    @@ok
            MVII    #$A,    R2

@@ok        ADDI    #@@tbl, R1
            MVI@    R1,     R0

            CALL    SFXPUT.1

            ; Die if there are no plants left
            MVII    #BGMPTBL, R2
@@loop
            MVI@    R2,     R0
            CMPI    #BGI.plant0, R0
            BEQ     SFXRET
            CMPI    #BGI.plant1, R0
            BEQ     SFXRET
@@next      ADDI    #4,     R2
            CMPI    #BGMPTBL+20, R2
            BLT     @@loop
            B       SFXDIE                  ; no plants

@@tbl       DECLE   @@a, @@b, @@c, @@b, @@d, @@b, @@c, @@b
            ENDP

;; ======================================================================== ;;
;;  SFXSAUC                                                                 ;;
;; ======================================================================== ;;
SFXSAUC     PROC
            MVI@    R4,     R1
            DECR    R4

            MOVR    R1,     R2
            ANDI    #7,     R1
            ADDI    #@@tgt, R1
            MVI@    R1,     R0              ;   Get target pitch

            SUB@    R3,     R0              ;   Compare against current
            CMPI    #3,     R0              ;   \
            BGT     @@same                  ;    |_ If more than +/- 3
            CMPI    #-3,    R0              ;    |  away, keep advancing
            BLT     @@same                  ;   /   towards target.

            INCR    R2
            MVO@    R2,     R4
            DECR    R4

            ; Get louder/softer
            ADDI    #$B,    R3
            MVI@    R3,     R0
            ANDI    #4,     R1
            SUBI    #2,     R1
            SARC    R1,     1
            SUBR    R1,     R0
            MVO@    R0,     R3
            SUBI    #$B,    R3

            ; Die if there are no saucers left
            MVI     WAVE,   R0
            TSTR    R0
            BEQ     SFXDIE
            B       SFXRET

            ; R0 contains delta between target and actual
@@same      MVI     SFXSTMP, R1
            XORI    #$80,   R1
            SUBI    #$80,   R1
            SARC    R0,     2
            SARC    R0,     1
            ADDR    R1,     R0
            BMI     @@nrnd
            SARC    R0,     1
            ADCR    R0
            MVO     R0,     SFXSTMP

            SARC    R0,     1
            ADCR    R0
            B       @@doit
@@nrnd
            SARC    R0,     1
            MVO     R0,     SFXSTMP

            SARC    R0,     1
@@doit
            ADD@    R3,     R0
            MVO@    R0,     R3

            B       SFXRET

@@tgt       DECLE   $87, $AA, $8F, $B4, $87, $AA, $8F, $BE
            ENDP


;; ======================================================================== ;;
;;  SFXJUMP/SFXJUMP2                                                        ;;
;;  Rapidly descending ramp.  Tone only.                                    ;;
;; ======================================================================== ;;
SFXJUMP     PROC
            CALL    SFXGET
            MVI@    R4,     R1              ;   Get state byte
            DECR    R4
            DECR    R1                      ;   Count down
            BPL     @@novol                 ;   No expiry, no volume update
            
            DECR    R2                      ;   Decrement volume

            MVII    #6,     R1              ;   Restart counter
@@novol:
            MVO@    R1,     R4              ;   Store updated counter
            DECR    R4

            ADDI    #2,     R0              ;   Go down one period
            CMPI    #$140,  R0              ;   \_ Die at end
            BGT     SFXDIE                  ;   /
            B       SFXPUT                  ;   Update pitch/volume and leave
            ENDP

;; ======================================================================== ;;
;;  SFXSMEXP/SFXLGEXP                                                       ;;
;;  Explosions:  Enveloped noise modulated by random tones.                 ;;
;; ======================================================================== ;;
SFXSMEXP
SFXLGEXP    PROC
        
            CALL    SFXGET
            ADDI    #$0400, R0
            CMPI    #$0100, R0
            BC      SFXJUMP2.1
            MVII    #1,     R0
@@ok:       B       SFXJUMP2.1

            ENDP

;; ======================================================================== ;;
;;  SFXJUMP2                                                                ;;
;;  Second half of the JUMP sound effect -- Enveloped low constant pitch.   ;;
;; ======================================================================== ;;
SFXJUMP2    PROC
            CALL    SFXGET
@@1 
            MVI@    R4,     R1              ;   Get state byte
            DECR    R4
            DECR    R1                      ;   Count down
            BPL     @@novol                 ;   No expiry, no volume update
            MVII    #6,     R1              ;   Restart counter
            
            DECR    R2                      ;   Decr volume every 7 tics
            CMPI    #2,     R2              ;   Die when it reaches 2
            BEQ     SFXDIE
@@novol:
            MVO@    R1,     R4              ;   Store updated counter
            DECR    R4
            B       SFXPUT                  ;   Update pitch/vol and leave
            ENDP
            
;; ======================================================================== ;;
;;  SFXDIED                                                                 ;;
;;  Tank fall down go boom.  Four staccato blasts of noise that fade out.   ;;
;; ======================================================================== ;;
SFXDIED     PROC
            MVII    #$07,   R0              ; \_  Special case:  Own 
            MVO     R0,     $1F8            ; /   the entire PSG0


            MOVR    R4,     R2              ; 
            MVI@    R2,     R0              ; 
            CMPI    #7,     R0
            BLT     @@fade
            DECR    R0
            MVO@    R0,     R2

            SARC    R0,     1
            BC      SFXRET

            ADDI    #$B,    R3
            MVI@    R3,     R1
            ANDI    #$0F,   R1              ; Some PSGs set bits 6..7
            SUBI    #$B,    R3

            DECR    R1
            CMPI    #9,     R1
            BGT     @@ok
            MVII    #13,    R1
@@ok:       MVO     R1,     $1FB
            MVO     R1,     $1FC
            MVO     R1,     $1FD

            B       SFXRET

@@fade:     DECR    R0
            BPL     @@leave
            MVII    #6,     R0
            MVO@    R0,     R2

            ADDI    #$B,    R3
            MVI@    R3,     R1
            ANDI    #$0F,   R1              ; Some PSGs set bits 6..7
            SUBI    #$B,    R3

            DECR    R1
            BPL     @@ok

            MVII    #$38,   R0
            MVO     R0,     $1F8
            B       SFXDIE

@@leave     MVO@    R0,     R2
            B       SFXRET
            ENDP

;; ======================================================================== ;;
;;  SFXBFIRE                                                                ;;
;; ======================================================================== ;;
SFXBFIRE    PROC
            MVI@    R3,     R0              ;   Get pitch
            SUBI    #2,     R0              ;   Fast decreasing rate
            CMPI    #$28,   R0              ;   End after $2C
            BLT     SFXDIE              
            MVO@    R0,     R3              ;   Otherwise update
            B       SFXRET
            ENDP
            
;; ======================================================================== ;;
;;  SFXALIEN                                                                ;;
;; ======================================================================== ;;
SFXALIEN    PROC

            MVI@    R4,     R1              ;   \
            INCR    R1                      ;    |
            MOVR    R1,     R2              ;    |  Increment state byte
            ANDI    #3,     R2              ;    |  
            CMPI    #3,     R2
            ADCR    R1
@@ok:       DECR    R4                      ;    |
            MVO@    R1,     R4              ;   /
            DECR    R4

            CMPI    #80,    R1              ;   \__ Quit after 60 tics
            BGE     SFXDIE                  ;   /

            ANDI    #1,     R2              ;   \__ Update every 4 counts
            BEQ     SFXRET                  ;   /   (4 tics/2 tics)

            SLR     R1,     2               ;   Divide count by 4
            CALL    SFXGET

            MOVR    R1,     R2              ;   \ 
            ADDI    #@@vtbl,R2              ;    |- Get volume (20 steps)
            MVI@    R2,     R2              ;   / 

            ANDI    #3,     R1              ;   Alternate among 4 tones
            ADDI    #@@ttbl,R1              ;   \_  Get tone (4 tones)
            MVI@    R1,     R0              ;   / 
            B       SFXPUT

@@vtbl      DECLE   $A,$A,$A,$A,9,9,9,8,8,8,7,7,7,6,6,5,4,3,2,0
@@ttbl      DECLE   $0A0,$0BE,$0E2,$0BE
            ENDP

;; ======================================================================== ;;
;;  SFXDING                                                                 ;;
;; ======================================================================== ;;
SFXDING     PROC
            MOVR    R4,     R2
            MVI@    R2,     R0
            DECR    R0
            MVO@    R0,     R2

            SLR     R0,     2
            BEQ     SFXDIE

            ADDI    #$B,    R3
            MVO@    R0,     R3
            SUBI    #$B,    R3
            B       SFXRET
            ENDP

;; ======================================================================== ;;
;;  SFXSKID                                                                 ;;
;; ======================================================================== ;;
SFXSKID     PROC
            MVI@    R3,     R0
;           SUBI    #$40,   R0
;           ANDI    #$7F,   R0
;           ADDI    #$20,   R0
            XORI    #$33,   R0
            MVO@    R0,     R3

            MVI@    R4,     R0
            DECR    R4
            DECR    R0
            BMI     @@switch
            MVO@    R0,     R4
            DECR    R4
            B       SFXRET
@@switch:   MVII    #FXDIED,R0
            MVO     R0,     SFXQ
            B       SFXDIE
            ENDP

;* ======================================================================== *;
;*  This program is free software; you can redistribute it and/or modify    *;
;*  it under the terms of the GNU General Public License as published by    *;
;*  the Free Software Foundation; either version 2 of the License, or       *;
;*  (at your option) any later version.                                     *;
;*                                                                          *;
;*  This program is distributed in the hope that it will be useful,         *;
;*  but WITHOUT ANY WARRANTY; without even the implied warranty of          *;
;*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       *;
;*  General Public License for more details.                                *;
;*                                                                          *;
;*  You should have received a copy of the GNU General Public License       *;
;*  along with this program; if not, write to the Free Software             *;
;*  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.               *;
;* ======================================================================== *;
;*                   Copyright (c) 2006, Joseph Zbiciak                     *;
;* ======================================================================== *;
