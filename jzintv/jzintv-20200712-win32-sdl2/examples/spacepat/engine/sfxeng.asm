;; ======================================================================== ;;
;;  SFX Engine                                                              ;;
;;                                                                          ;;
;;  Sound effect updates are handled similarly to bad-guy updates.  Each    ;;
;;  active effect has a thinker associated with it to update the effect.    ;;
;;  Each effect is allocated a single PSG channel, thereby making it easy   ;;
;;  to track PSG resource allocation.                                       ;;
;;                                                                          ;;
;;  Space Patrol needs the following sounds, in order of decreasing         ;;
;;  priority:                                                               ;;
;;                                                                          ;;
;;      Jump (pri)                                                          ;;
;;      Ding                                                                ;;
;;      Fire                                                                ;;
;;      Kill Alien                                                          ;;
;;      Lg. Explosion                                                       ;;
;;      Jump (aux)                                                          ;;
;;      Sm. Explosion                                                       ;;
;;      Space Plant*                                                        ;;
;;      Alien Flight*                                                       ;;
;;                                                                          ;;
;;  [*] These are played only if ECS is attached.                           ;;
;;                                                                          ;;
;;  Note that there are two separate Jump sound effects.  The Jump effect   ;;
;;  requires two channels, one for a descending high pitch, and one for     ;;
;;  a low pitch fixed tone.  The former is a high-priority sound effect,    ;;
;;  whereas the latter can be canceled if another effect needs it.          ;;
;;                                                                          ;;
;;  When the game requests a sound effect, the engine must find a slot      ;;
;;  that is free, or the lowest priority slot that's also lower prio than   ;;
;;  the requested effect to override.                                       ;;
;;                                                                          ;;
;;  When the ECS is attached, the engine tracks four SFX slots.  When it's  ;;
;;  not attached, the engine tracks two SFX slots.  In either case, noise   ;;
;;  producing sound effects are limited to the first two slots to avoid     ;;
;;  conflict with the music's "click track."  The engine never "migrates"   ;;
;;  sounds.  Therefore, it's possible an explosion sound effect will get    ;;
;;  dropped even when a channel is available.  To minimize this, the code   ;;
;;  prefers ECS channels over master component channels when the ECS is     ;;
;;  attached.  Furthermore, some effects (plant, alien flight) should only  ;;
;;  play when the ECS is attached.                                          ;;
;;                                                                          ;;
;;  Each effect gets a single byte of status storage that it can use to     ;;
;;  track where in the effect it is.  Some effects, such as the Fire        ;;
;;  sound effect, won't need this byte.  Others can use it for sleeping     ;;
;;  or whatever between stages of the effect.                               ;;
;;                                                                          ;;
;;  Each thinker gets invoked with R3 pointing to the base of the PSG       ;;
;;  channel, and R4 pointing to the status byte for the channel.  The       ;;
;;  status bytes are stored interleaved with the thinker indices.           ;;
;;                                                                          ;;
;;  Each effect gets initialized from a record containing the following     ;;
;;  information.                                                            ;;
;;                                                                          ;;
;;   -- Volume (1 - 15, or 0 if uses envelope)                              ;;
;;   -- Tone period, or 0 if no tone                                        ;;
;;   -- Noise period / 2, or 0 if no noise                                  ;;
;;   -- Allowed channel bitmap                                              ;;
;;                                                                          ;;
;;  Format:                                                                 ;;
;;                                                                          ;;
;;    15                            8 7             4 3             0       ;;
;;   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+      ;;
;;   |     State Byte Initializer    | Noise Period  | Channel Bitmap|      ;;
;;   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+      ;;
;;                                                                          ;;
;;    15           12 11                                            0       ;;
;;   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+      ;;
;;   |  Initial Vol  |              Initial Tone Period              |      ;;
;;   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+      ;;
;;                                                                          ;;
;;  Note that thinker address could also be packed in this table, but       ;;
;;  net size savings would be minimal due to more complicated code.         ;;
;;  Also, the channel bitmap contains the ECS channels in bits 1:0 and      ;;
;;  the master component channels in bits 3:2.                              ;;
;;                                                                          ;;
;; ======================================================================== ;;


;; ======================================================================== ;;
;;  UPSFX   Called once per tick to update all active SFX.                  ;;
;; ======================================================================== ;;
UPSFX       PROC
            MVI     SFXBSY,     R0
            TSTR    R0
            BNEQ    JRR5

            MVO     R5,         BGTTMP      ;    Save return address

            MVII    #SFXTBL,    R4          ;    Thinker table
            MVII    #$0F1,      R3          ;    Utility:  Point to PSG

@@loop:     MVI@    R4,         R1          ;    \
            DECR    R1                      ;     |- 0 means no SFX
            BMI     @@next                  ;    /   non-zero is thinker #
            CMPI    #$FE,       R1          ;    Is it a disabled channel?
            BEQ     @@next                  ;    Yes: Blow this popsicle stand

            ADDI    #SFXIND,    R1          ;    \_ dispatch to thinker.
            MVI@    R1,         PC          ;    /  

SFXRET
@@next:     INCR    R4                      ;    Skip status byte
            INCR    R3
            CMPI    #$0F3,      R3
            BNEQ    @@not3
            MVII    #$1F1,      R3

@@not3      CMPI    #$1F3,      R3
            BNEQ    @@loop
            
            MVI     BGTTMP,     PC

SFXDIE      DECR    R4                      ;    Point back to sfx byte
            CLRR    R0
            MVO@    R0,         R4
            ADDI    #$B,        R3
            MVO@    R0,         R3
            SUBI    #$B,        R3
            B       @@next
            ENDP

;; ======================================================================== ;;
;;  SFXINIT Initialize the SFX structures.                                  ;;
;; ======================================================================== ;;
SFXINIT     PROC
            PSHR    R5

            MVII    #SFXTBL,    R4
            MVI     ECSOK,      R0          ; Zero if OK, 0xFFFF if not.
            MVO@    R0,         R4          ; \_ 00 means channel available
            INCR    R4
            MVO@    R0,         R4          ; /  FF means not available
            INCR    R4
            CLRR    R0
            MVO@    R0,         R4          ; \_ Master component channels
            INCR    R4
            MVO@    R0,         R4          ; /  are always available
            MVO     R0,         SFXQ

            INCR    R0

            MVII    #$1F0,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVII    #$0F0,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4

            DECR    R0

            MVII    #$1F4,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVII    #$1FB,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4

            MVII    #$0F4,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVII    #$0FB,      R4
            MVO@    R0,         R4
            MVO@    R0,         R4
            MVO@    R0,         R4

            MVII    #$37,       R0
            MVO     R0,         $0F8
            MVII    #$38,       R0
            MVO     R0,         $1F8

            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  PLAYSFX Try to play a sound effect.                                     ;;
;;          Sound effect number pointed to by R5.                           ;;
;; ======================================================================== ;;
PLAYSFX     PROC    
            PSHR    R0
            MVI@    R5,         R0
@@1:        CMP     SFXQ,       R0
            BLT     @@nope
            MVO     R0,         SFXQ
@@nope:     PULR    R0
JRR5        JR      R5
            ENDP

DOPLAYSFX   PROC
            PSHR    R5
            MVII    #1,         R0
            MVO     R0,         SFXBSY

            CMPI    #SFXSAUC,   R1
            BNEQ    @@notsauc
            MVO     R0,         SFXSTMP
@@notsauc:
        
@@again:    MOVR    R1,         R5          ; Save priority
            SLL     R1,         1           ; 
            ADDI    #SFXINI-2,  R1
            MVI@    R1,         R1          ; Get channel allocation flags
            ANDI    #$F,        R1          ; Mask away noise flags

            MVII    #$00FE,     R0          ; \_ current "best" is "none"
            CLRR    R2                      ; /  with lower-than-lowest prio
            MVII    #SFXTBL,    R3          ; Start at first ECS channel
            B       @@loop

@@skip:     BEQ     @@last
@@next:     ADDI    #2,         R3
@@loop:     SARC    R1,         1           ; Can I alloc this channel?
            BNC     @@skip
            CMP@    R3,         R5          ; Is this same effect?
            BEQ     @@restart_sfx
            CMP@    R3,         R0          ; Is this better than current?
            BLT     @@next                  ; If smaller, nope.
            MOVR    R3,         R2          ; Save ptr 
            MVI@    R3,         R0          ; Save priority
            B       @@next

@@restart_sfx:
;           CMPI    #FXSAUC,    R5          ; \_ don't restart SAUC effect
;           BEQ     @@done                  ; /
            MOVR    R3,         R2          ; Make equal channel "best"
            B       @@doit
@@last:     TSTR    R2
            BEQ     @@done                  ; No slot available for SFX
            CMPR    R0,         R5          ; Drop it if prev are higher prio
            BLT     @@done
@@doit:     MVO@    R5,         R2          ; Write SFX # to slot to alloc
            ADDR    R5,         R5
            ADDI    #SFXINI-2,  R5          ; Now point to init table again

            MVI@    R5,         R0          ; Get rest of first init word
            SWAP    R0
            INCR    R2
            MVO@    R0,         R2          ; Write initializer
            SWAP    R0

            SUBI    #SFXTBL+1,  R2          ; turn into an index
            SLL     R2,         1           ; \_ Index into channel info 
            ADDI    #SFXPSG,    R2          ; /  table
            MOVR    R2,         R4          ; More convenient register

            MVII    #$3F,       R1          ; Default channel enables:  None
            MVI@    R4,         R2          ; Get noise period address
            SLR     R0,         2
            SLR     R0,         1
            ANDI    #$1E,       R0          ; Any noise component?
            BEQ     @@no_noise
            ANDI    #$07,       R1          ; enable noise for this channel
            MVO@    R0,         R2          ; Write noise period
@@no_noise: 
            MVI@    R4,         R2          ; Get tone period address
            MVI@    R5,         R0          ; Get tone
            MOVR    R0,         R3          ; Save volume
            ANDI    #$FFF,      R0          ; Any tone component?
            BNEQ    @@tone                  ; 
            MVII    #1,         R0          ; set tone register to high pitch
            BEQ     @@no_tone
@@tone:     ANDI    #$38,       R1          ; enable tone for this channel
@@no_tone:
            MVO@    R0,         R2          ; Write tone LSBs
            ADDI    #4,         R2
            SWAP    R0
            MVO@    R0,         R2          ; Write tone MSBs
            SUBI    #4,         R2          ; Rewind pointer (*sigh*)
            
            ; At this point:
            ; R0 is junk
            ; R1 holds tone/noise enables for this channel.
            ; R2 points to LSB of tone channel
            ; R3 holds volume in bits 15:12
            ; R4 points to 3rd word of SFXPSG entry
            ; R5 points past SFXINI record

            SWAP    R3                      ; \
            ANDI    #$F0,       R3          ;  |_ Extract volume
            SLR     R3,         2           ;  |
            SLR     R3,         2           ; /
            BNEQ    @@no_env    
            MVII    #$3F,       R3          ; vol=0 means "use envelope"
@@no_env    ADDI    #$B,        R2          ; point to channel's volume reg
            MVO@    R3,         R2          ; write volume


            MVI@    R4,         R2          ; Point to channel enable
            MVI@    R4,         R0          ; Get update mask
            ANDR    R0,         R1          ; Filter out our enables
            COMR    R0
            AND@    R2,         R0          ; Keep other bits, clr this chan's
            XORR    R1,         R0          ; Merge in this chan's
            MVO@    R0,         R2          ; Write merged channel enable

@@done:     MVI     SFXQ,       R1
            TSTR    R1
            BEQ     @@leave
            CLRR    R0
            MVO     R0,         SFXQ
            J       @@again

@@leave:    CLRR    R0
            MVO     R0,         SFXBSY
            PULR    PC

            ENDP

;; ======================================================================== ;;
;;  SFXPSG  Useful lookup table for channel-to-PSG mapping.                 ;;
;; ======================================================================== ;;
SFXPSG      PROC
            DECLE   $0F9, $0F1, $0F8, %010010
            DECLE   $0F9, $0F2, $0F8, %100100
            DECLE   $1F9, $1F1, $1F8, %010010
            DECLE   $1F9, $1F2, $1F8, %100100
            ENDP

;; ======================================================================== ;;
;;  SFXGET  Get the current channel into machine registers                  ;;
;;  SFXPUT  Write machine registers to the current channel                  ;;
;; ======================================================================== ;;
SFXGET      PROC
            MVI@    R3,     R0
            ADDI    #4,     R3
            SWAP    R0
            XOR@    R3,     R0
            SWAP    R0
            ADDI    #7,     R3
            MVI@    R3,     R2
            ANDI    #$3F,   R2
            SUBI    #$B,    R3
            JR      R5
            ENDP

SFXPUT      PROC
            MVII    #SFXRET,R5
@@1         MVO@    R0,     R3
            ADDI    #4,     R3
            SWAP    R0
            MVO@    R0,     R3
            ADDI    #7,     R3
            MVO@    R2,     R3
            SUBI    #$B,    R3
            JR      R5
            ENDP
