;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2007, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  ENGINE1 -- This is the very-time-critical GRAM and STIC register update ;;
;;             stuff.  We calculate this one frame ahead so that all we do  ;;
;;             here is a bunch of high speed block copies.                  ;;
;;==========================================================================;;
ENGINE1 PROC 

        ;;------------------------------------------------------------------;;
        ;;  During-vblank stuff.  We cycle count as it's a tight fit.  When ;;
        ;;  we arrive here, we may have as little as 3500 cycles or so      ;;
        ;;  for all of our updates, since we have non-interruptible code    ;;
        ;;  elsewhere that will delay interrupts.                           ;;
        ;;------------------------------------------------------------------;;
        MVO     R0,     $20     ;  11   Enable the display
@@1:

        ;;------------------------------------------------------------------;;
        ;;  Copy over sprite "pseudo registers" from 16-bit RAM.            ;;
        ;;------------------------------------------------------------------;;
        CLRR    R5              ;   6   Point to MOB registers
        MVI     SDATP,  R4      ;  10   Point to RAM copy of MOB registers 
                                ;----
                                ;  16
                                ;  11   (from display enable)
                                ;====
                                ;  27

        REPEAT  24              ;       unrolled completely for speed
        MVI@    R4,     R0      ;   8   \_ copy STIC shadow register
        MVO@    R0,     R5      ;   9   /
        ENDR
                                ;----
                                ; 408 = 17*24
                                ;  27  (carried forward)
                                ;====
                                ; 435

        ;;------------------------------------------------------------------;;
        ;;  Record collisions with the buggy and clear its collision reg.   ;;
        ;;------------------------------------------------------------------;;
        MVII    #$0103, R0      ;   8   Magic constant
        SDBD                    ;   4   \_ sets carry if any collision
        CMP@    R5,     R0      ;  10   /  happens w/ MOB 2..7
        RLC     R1,     1       ;   6   record this collision in lsb of R0
        AND     MOBHIT, R1      ;  11   store out the collision flag
        MVO     R1,     MOBHIT  ;  11   store out the collision flag
        MVO     R0,     $18     ;  11   \_ Clear previous collisions.
        MVO     R0,     $19     ;  11   /
                                ;----
                                ;  72  
                                ; 435  (carried forward)
                                ;====
                                ; 507

        ;;------------------------------------------------------------------;;
        ;;  Copy over ground data for scrolling ground and horiz bullet.    ;;
        ;;------------------------------------------------------------------;;
        MVI     GDATA,  R0      ;  10   Pointer to ground gfx data
        MVO     R0,     GGRAM   ;  11
        MVII    #HBGRAM,R1      ;   8   Pointer to horiz bullet GRAM card
        SUB     HBROW,  R1      ;  10   Adjust for pixel row of bullet
        MVI     HBDATA, R0      ;  10   Get bullet pixel
        MVO@    R0,     R1      ;   9   Draw it.
                                ;----
                                ;  58
                                ; 507
                                ;====
                                ; 565

        
        ;;------------------------------------------------------------------;;
        ;;  Copy over rock/crater data for scrolling rocks, craters.        ;;
        ;;------------------------------------------------------------------;;
        MVI     RPTR,   R5      ;  10   Pointer to Rock/Crater gfx data
        MVII    #RGRAM, R4      ;   8
                                ;----
                                ;  18
                                ; 565
                                ;====
                                ; 583

        REPEAT  12*4            ;      unrolled completely for speed
        MVI@    R5,     R0      ;   8  \
        MVO@    R0,     R4      ;   9   |_ copy over 2 rows of card
        SWAP    R0,     1       ;   6   |
        MVO@    R0,     R4      ;   9  /
        ENDR                    ;----
                                ;1536 total for 12 card (48 iters)
                                ; 583
                                ;====
                                ;2119

        ;;------------------------------------------------------------------;;
        ;;  Update the wheels on the buggy.                                 ;;
        ;;------------------------------------------------------------------;;
        MVI     WPTR,   R4      ;  10   Pointer to wheel graphic (two words)
        MVI@    R4,     R0      ;   8   Get first word
        MVO     R0,     WGRAM   ;  11   Row 0
        SWAP    R0,     1       ;   6
        MVO     R0,     WGRAM+1 ;  11   Row 1
        MVI@    R4,     R0      ;   8   Get second word
        MVO     R0,     WGRAM+3 ;  11   Row 2
        SWAP    R0,     1       ;   6
        MVO     R0,     WGRAM+4 ;  11   Row 3
                                ;----
                                ;  82
                                ;2119
                                ;====
                                ;2201


        ;;------------------------------------------------------------------;;
        ;;  Also update the "spinner" bad-guy.                              ;;
        ;;------------------------------------------------------------------;;
        MVI     SPINCNT,R5      ;  10   Point to the spinner's frame counter

        MVII    #SGRAM, R4      ;   8   Point to spinner's GRAM entry
        ADDI    #SPIN1, R5      ;   8   Offset into spinner's animation

        MVI@    R5,     R0      ;   8   \
        MVO@    R0,     R4      ;   9    |
        SWAP    R0,     1       ;   6    |
        MVO@    R0,     R4      ;   9    |

        MVI@    R5,     R0      ;   8    |
        MVO@    R0,     R4      ;   9    |
        SWAP    R0,     1       ;   6    |
        MVO@    R0,     R4      ;   9    |-- Copy over 7 rows of 1 card

        MVI@    R5,     R0      ;   8    |
        MVO@    R0,     R4      ;   9    |
        SWAP    R0,     1       ;   6    |
        MVO@    R0,     R4      ;   9    |

        MVI@    R5,     R0      ;   8    |
        MVO@    R0,     R4      ;   9    |
;       SWAP    R0,     1       ;   -    | \__ Last row not needed
;       MVO@    R0,     R4      ;   -   /  /   
                                ;----
                                ; 139
                                ;2201
                                ;====
                                ;2340
                                        
        ;;------------------------------------------------------------------;;
        ;;  Copy over mountain data for top or middle mountain, if either.  ;;
        ;;  We avoid most conditional code here by hard-coding for 8        ;;
        ;;  cards, and relying on external code to set up our GRAM pointer  ;;
        ;;  for us.  If there's no mountain update this frame, MPTR == 0.   ;;
        ;;------------------------------------------------------------------;;
        MVI     MPTR,   R5      ;  10   Get mountain gfx data pointer
        TSTR    R5              ;   6   Is it NULL?
        BEQ     @@nomtn         ;   7   If yes, skip mountain update.
        MVI     MGOFS,  R4      ;  10   Get GRAM address for mtn gfx.
        MVI     MGRAM,  R2      ;  10   Get GRAM address for mtn gfx.
        MVII    #8,     R3      ;   8
        ANDR    R4,     R3      ;   6
        MVII    #$0030, R3      ;   8   Init circular-addressing mask
        BEQ     @@mloop_e       ; 7/9
                                ;----
                                ;  72   do odd loop
                                ;  74   do even loop
                                ;     

@@mloop_o:

        REPEAT  4               ;       unrolled completely for speed

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 0, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 1, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 2, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 3, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 4, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 5, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 6, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 7, card 0

        ANDR    R3,     R4      ;   6
        XORR    R2,     R4      ;   6

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 0, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 1, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 2, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 3, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 4, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 5, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 6, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 7, card 1

        ENDR                    ;----
                                ;1072 = (32*8 + 12) * 4

        B       @@mloop_done    ;   9
                                ;  72
                                ;----
                                ;1153

@@mloop_e:

        REPEAT  4

        ANDR    R3,     R4      ;   6
        XORR    R2,     R4      ;   6

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 0, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 1, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 2, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 3, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 4, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 5, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 6, card 0
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 7, card 0

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 0, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 1, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 2, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 3, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 4, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 5, card 1

        MVI@    R5,     R0      ;   8
        MVO@    R0,     R4      ;   9   Row 6, card 1
        SWAP    R0,     1       ;   6
        MVO@    R0,     R4      ;   9   Row 7, card 1

        ENDR                    ;----
                                ;1072 = (32*8 + 12)*4
                                ;  74
                                ;----
                                ;1146 

@@mloop_done:
                                ;1153 (Worst case: odd loop)
                                ;2340 (carried forward from above)
                                ;====
                                ;3493 
                                ; 125  Assumed overhead of reaching ENGINE
                                ;====
                                ;3618

        ;;------------------------------------------------------------------;;
        ;;  Punch line:  GRAM is available for ~3796 cycles, which means    ;;
        ;;  we can tolerate interrupts disabled for up to ~178 cycles.      ;;
        ;;------------------------------------------------------------------;;

@@nomtn:

        ;;------------------------------------------------------------------;;
        ;;  Do remainder of spinner update.                                 ;;
        ;;------------------------------------------------------------------;;
        MVI     SPINCNT,R5      ;  10   Point to the spinner's frame counter
        MOVR    R5,     R1      ;   6
        ANDI    #$80,   R1      ;   8
        ADDI    #4,     R5      ;   8   Update the frame counter
        ANDI    #31*4,  R5      ;   8   Mask away the fractional portion
        XORR    R1,     R5      ;   6
        MVO     R5,     SPINCNT ;  11   Store it back out
                                ;----
                                ;  57
                                ;3618
                                ;----
                                ;3675

        ENDP ; falls into remainder of ENGINE1 which is outside the PROC

@@foo:  
        ;;------------------------------------------------------------------;;
        ;;  Skip card oriented updates if we're not at normal game screen.  ;;
        ;;------------------------------------------------------------------;;
        MVI     EMODE,  R0      ;  10
        DECR    R0              ;   6
        BNEQ    E1.skip_card    ; 7/9
                                ;----
                                ;  23
                                   
        ;;------------------------------------------------------------------;;
        ;;  Finish constructing current frame's "state of the world."       ;;
        ;;------------------------------------------------------------------;;
        ICALL   upcrd           ;1331     Do card-oriented updates.

        ;;------------------------------------------------------------------;;
        ;;  Before we update the "state of the world", check collisions.    ;;
        ;;------------------------------------------------------------------;;
        ICALL   ckbrc           ;1000     Check for buggy/rock/crater collision
        ICALL   uphbp           ; 596     Update the horizontal bullet
                                ;----
                                ;6625

E1.skip_card: ; XXX card-update skip hack for debug screen.

        ;;------------------------------------------------------------------;;
        ;;  Remainder of engine is not safely reentrant.                    ;;
        ;;------------------------------------------------------------------;;
        DIS                     ;   4 \
        MVII    #1,     R1      ;   8  |   !!Critical Section!!
        CMP     EBSY,   R1      ;  10  |   Check our "ENGINE IS BUSY" flag,
                                ;      |-- and if we're busy, just drop a
        MVO     R1,     EBSY    ;  11  |   frame.  :-(  Not that I like that.
        BNEQ    E1.not_busy     ;   9 /
                                ;----
                                ;  48
                                ;  19
                                ;====
                                ;  67


        ADD     FDROP,  R1      ;     \    If we drop a frame, disable all
                                ;      |__ tasks for this frame by just
        MVO     R1,     FDROP   ;      |   returning Also, increment our
        JE      MISCISR.1       ;     /    frame-drop count. (debugging)

E1.not_busy:

        CLRR    R1              ;   6
        MVO     R1,     MPTR    ;  11   clear MPTR for next time.


        ;;------------------------------------------------------------------;;
        ;;  Done with very-time-sensitive vertical-blanking stuff.          ;;
        ;;  Queue up ENGINE2 and chain return via MISCISR.                  ;;
        ;;------------------------------------------------------------------;;
;;@@end:  
        MVI     DOENG,  R0      ;  10
        INCR    R0              ;   6
        MVO     R0,     DOENG   ;  11
        CMP     SDATP,  R0      ;  10
        BNC     E1.muxok        ; 7/9
        CLRR    R0              ;   6
E1.muxok
        MVO     R0,     MUXOK   ;  11   allow muxing again
        JE      MISCISR.1       ; 177   (includes return from ISR cost)
                                ;----
                                ; 255
                                ;  67 (carried forward)
                                ;6625
                                ;====
                                ;6947
        
;       ENDP


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
;*                   Copyright (c) 2007, Joseph Zbiciak                     *;
;* ======================================================================== *;
