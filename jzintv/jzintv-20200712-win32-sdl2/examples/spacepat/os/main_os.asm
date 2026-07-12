;;==========================================================================;;
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Main ISR, Main loop, task functions, initialization, etc.                ;;
;; Copyright 2007, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  TITLE / START                                                           ;;
;;                                                                          ;;
;;  This contains the title string and the startup code.  We pre-empt the   ;;
;;  EXEC's initialization sequence by setting the "Special Copyright" bit   ;;
;;  in location $500C.  This causes the code at 'START' to run before the   ;;
;;  built-in title screen is completely displayed.                          ;;
;;                                                                          ;;
;;  The Startup code does very little.  Mainly, it sets the Interrupt       ;;
;;  Service Routine vector to point to our _real_ initialization routine,   ;;
;;  INIT.  This is done because we can only get to GRAM and STIC registers  ;;
;;  during the vertical retrace, and vertical retrace is signaled by an     ;;
;;  interrupt.  (Actually, we can have access to GRAM/STIC for longer       ;;
;;  if we don't hit the STIC 'handshake' at location $20, but then the      ;;
;;  display blanks.  During INIT, the display does blank briefly.)          ;;
;;==========================================================================;;
TITLE:  BYTE    107, "Space Patrol", 0
        ; Intercept/preempt EXEC initialization and just do our own.
        ; We call no EXEC routines in this game.
START:  PROC

        ;; ---------------------------------------------------------------- ;;
        ;;  Built-in Self Test:  ROM should sum to 0.                       ;;
        ;; ---------------------------------------------------------------- ;;
        SETISR  BISTISR
        JSRE    R5,     CLRSCR

        MVII    #(1 SHL(15-5))+(1 SHL(15-6))+(1 SHL(15-$D))+(1 SHL(15-$F)), R1
        CLRR    R5
        CLRR    R2
@@bist: SLLC    R1
        BC      @@do4k
        BEQ     @@done
        ADDI    #$1000, R5
        B       @@bist
@@do4k  MVII    #$0800, R0
@@bloop ADD@    R5,     R2
        SUB@    R5,     R2
        DECR    R0
        BNEQ    @@bloop
        B       @@bist

@@done  TSTR    R2
        BEQ     @@pass


        CALL    P16.FLS
        DECLE   C_YEL, disp_ptr(6, 5)
        S16     "FAIL "

        MOVR    R2,     R0
        JSRE    R5,     PRNUM16.bfw
        DECLE   C_WHT, 5

        MVII    #C_RED, R0
        MVO     R0,     TMP

        DECR    PC              ; spin on failure

@@pass: MVII    #STACK, R6

        ;; ---------------------------------------------------------------- ;;
        ;;  Initialize memory                                               ;;
        ;; ---------------------------------------------------------------- ;;
        CALL    FILLZERO.lp
        DECLE   STACK-$2F0, $2F0 ; $2F0...$STACK. 

        MVII    #$1FE,  R4
        SDBD
        MVI@    R4,     R0
    MVO R0, $1000
        CMPI    #$BEBE, R0
        BNEQ    @@x
        MVII    #.-CNAME,R0
        MVO     R0,     NN
@@x

        ;; ---------------------------------------------------------------- ;;
        ;;  Game initialization.                                            ;;
        ;; ---------------------------------------------------------------- ;;
        SETISR  INITISR
        JSRE    R5,     CLRSCR
        DECR    PC

        ENDP


;;==========================================================================;;
;;  INIT                                                                    ;;
;;  Initializes the ISR, etc.  Gets everything ready to run.                ;;
;;  This is called via the ISR dispatcher, so it's safe to bang GRAM from   ;;
;;  here, too.                                                              ;;
;;                                                                          ;;
;;   -- Zero out memory to get started                                      ;;
;;   -- Set up variables that need to be set up here and there              ;;
;;   -- Set up GRAM image                                                   ;;
;;   -- Drop into the main game state-machine.                              ;;
;;==========================================================================;;
INITISR PROC
        DIS

        MVII    #$38,   R2
        MVO     R2,     $1F8

;@@1:    DIS
        MVII    #STACK, R6      ; Reset the stack pointer

        CALL    FILLZERO.lp
        DECLE   $40             ; $00...$3F. (The STIC)
        DECLE   0               ; Prepare to zero all system RAM, PSG0,& STIC.

        MVI     COLSTK, R1      ; Force display to color-stack mode

        SETISR  MISCISR         ; Point ISR vector to our ISR
        ; Ok, everything's ready to roll now.
        ; Load up our initial font and drop into the game loop
        JSRE    R5,     LOADFONT
        DECLE   FONT

        B       GAMELOOP

        ENDP

;;==========================================================================;;
;;  LOADFONT -- Load a compressed FONT into GRAM.                           ;;
;;                                                                          ;;
;;  Font data is broken up into spans of characters that are copied         ;;
;;  into GRAM.  Each span is defined as follows.                            ;;
;;                                                                          ;;
;;    Span Header:  2 numbers in 1 DECLE                                    ;;
;;        bit 6..0, bit 15:  Skip Length (in bytes of GRAM memory)          ;;
;;        bit 14..7:         Span Length (in bytes of GRAM memory)          ;;
;;    Span Data -- Span Length / 2 words                                    ;;
;;                                                                          ;;
;;  Span data is encoded with two bytes in each 16-bit word.  The lower     ;;
;;  byte is stored to the lower address, and the upper byte to the next     ;;
;;  address after it.                                                       ;;
;;                                                                          ;;
;;  The font is terminated with a span of length 0.                         ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;  R5 -- Points to word (1 decle in 16-bit ROM) containing ptr to font     ;;
;;        info.  Code returns after this word.                              ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;  R0, R1, R4, R5 trashed.                                                 ;;
;;  GRAM is updated according to the font specification.                    ;;
;;                                                                          ;;
;;==========================================================================;;
LOADFONT PROC
        MVI@    R5,     R2              ; get font pointer
@@1     PSHR    R5

        MVII    #$100,  R4
        SDBD
        MVI@    R4,     R1

        SETISR  @@isr
        DECR    PC                      ; let ISR take over.

@@isr:
        DIS
        SUBI    #8,     R6
        MVO     R1,     $100            ; \
        SWAP    R1                      ;  |- restore old ISR
        MVO     R1,     $101            ; /

        MOVR    R2,     R5              ; get font pointer
        MVII    #GRAM,  R4              ; Point R4 at GRAM

@@gramloop:
        MVI@    R5,     R0              ; Get skip & span len. (in GRAM bytes)
        TSTR    R0                      ; Quit if skip/span == 0.
        BEQ     @@gramdone

        MOVR    R0,     R1
        ANDI    #$7F8,  R0              ; Extract span length.
        XORR    R0,     R1              ; Clear away span bits from word
        SWAP    R1                      ; Extrack skip value.
        ADDR    R1,     R4              ; Skip our output pointer.
        SLR     R0,     1               ; Divide count by 2.

@@charloop:
        MVI@    R5,     R1              ; Get two bytes
        MVO@    R1,     R4              ; Put the first byte
        SWAP    R1                      ; Put the other byte into position
        MVO@    R1,     R4              ; Put the second byte
        DECR    R0                      ; Sheesh, do I have to spell this out?
        BNEQ    @@charloop              ; inner loop
        B       @@gramloop              ; outer loop

@@gramdone:
        EIS
        PULR    PC
        ENDP

UPSND   PROC
        PSHR    R5

        ;; ---------------------------------------------------------------- ;;
        ;;  Update sound streams.  All sound streams update at 60Hz.        ;;
        ;; ---------------------------------------------------------------- ;;
        ; Update music
        CALL    PLAY_SONG       ; Arnauld's tracker

        ; Play any queued sound effects from running the engine2
        MVI     SFXQ,   R1
        TSTR    R1
        BEQ     @@nosfx
        CLRR    R0
        MVO     R0,     SFXQ
        CALL    DOPLAYSFX
@@nosfx:

        ; Update sfx
        CALL    UPSFX           ; Update the sound stream

        PULR    PC
        ENDP

;;==========================================================================;;
;;  MISCISR                                                                 ;;
;;  This is the main interrupt service routine.  It has to perform the      ;;
;;  following tasks:                                                        ;;
;;                                                                          ;;
;;   -- Run any miscellaneous "pre-VBLANK" task requested by main program.  ;;
;;   -- Hit the vertical blank handshake to keep screen enabled.            ;;
;;   -- Update any active sound streams.                                    ;;
;;   -- Drain and pixels queued up in the Pixel Queue.                      ;;
;;   -- Count down task timers and schedule tasks when timers expire.       ;;
;;   -- Count down the 'busy-wait' timer if it is set.                      ;;
;;   -- Detect a "Pause" request and pause the game if needed.              ;;
;;                                                                          ;;
;;  Our code does not rely on any EXEC routines at all, except the ISR      ;;
;;  dispatch routine which saves and restores all the registers.  (On a     ;;
;;  real Intellivision, we have no choice.  On an emulator, that routine    ;;
;;  can be replaced with a separate non-EXEC routine which performs a       ;;
;;  similar dispatch, if we want to distribute this program without an      ;;
;;  EXEC ROM image but with an emulator.)                                   ;;
;;                                                                          ;;
;;==========================================================================;;
BISTISR MVI     TMP,    R0
        MVO     R0,     $28
        MVO     R0,     $2C
MISCISR PROC
        MVO     R0,     $20
@@1:

@@wtimer:
        ;; ---------------------------------------------------------------- ;;
        ;;  Count down the wait-timer, if there is one.                     ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     WTIMER, R5
        DECR    R5
        BMI     @@expired
        MVO     R5,     WTIMER
@@expired:

        ;; ---------------------------------------------------------------- ;;
        ;;  Other misc periodic stuff.                                      ;;
        ;; ---------------------------------------------------------------- ;;
        MVI     TICK,   R0      ; Increment global tick counter
        INCR    R0
        MVO     R0,     TICK

        B       ISRRET

        ENDP

;;==========================================================================;;
;;  WAIT                                                                    ;;
;;  Busy-waits for the number of ticks specified after call, or in R0.      ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;  R0 -- Number of ticks to wait (WAIT.1)                                  ;;
;;  R5 -- Return address                                                    ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;  R0 -- cleared                                                           ;;
;;==========================================================================;;
WAIT1   MVII    #1,     R0
        INCR    PC
WAIT    PROC
        MVI@    R5,     R0
@@1     MVO     R0,     WTIMER
        CLRR    R0
@@loop:
        CMP     WTIMER, R0
        BNEQ    @@loop
        JR      R5
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
;*                   Copyright (c) 2007, Joseph Zbiciak                     *;
;* ======================================================================== *;
