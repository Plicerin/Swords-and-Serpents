;;==========================================================================;;
;; Joe Zbiciak's Tag-Along Todd 2, with Voice!                              ;;
;; Copyright 2002, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;* ======================================================================== *;
;*  TO BUILD IN BIN+CFG FORMAT:                                             *;
;*      as1600 -o tagalong2v.bin -l tagalong2v.lst tagalong2v.asm           *;
;*                                                                          *;
;*  TO BUILD IN ROM FORMAT:                                                 *;
;*      as1600 -o tagalong2v.rom -l tagalong2v.lst tagalong2v.asm           *;
;* ======================================================================== *;
 CFGVAR "name" = "SDK-1600 Tag-Along Todd #2 Voice, CP-1600X Extensions"
 CFGVAR "short_name" = "Tag-Along Todd #2v"
 CFGVAR "author" = "Joe Zbiciak"
 CFGVAR "year" = 2019
 CFGVAR "license" = "GPLv2+"
 CFGVAR "desc" = "Second iter of Tag-Along Todd, w/ fancy title screen & voice."
 CFGVAR "publisher" = "SDK-1600"
 CFGVAR "jlp" = 1   ; JLP required for CP-1600X extended ISA.

            ROMW    16              ; Use 16-bit ROM

;------------------------------------------------------------------------------
; Include system information
;------------------------------------------------------------------------------
            INCLUDE "../library/gimini.asm"     ; System offsets, etc.
            INCLUDE "../library/resrom.asm"     ; RESROM indices
            INCLUDE "../library/jlp_accel.asm"  ; JLP accelerators.
            INCLUDE "../macro/cp1600x.mac"      ; CP-1600X Extended ISA.

;------------------------------------------------------------------------------
; Global constants and configuration.
;------------------------------------------------------------------------------
TSKQM       EQU     $7              ; Task queue is 8 entries large
MAXTSK      EQU     2               ; Only one task
CAN         EQU     258 * 8 + C_DGR ; The can you're trying to collect
ARROW       EQU     259 * 8 + C_YEL ; The arrow for the menu.

PH_TITLE    EQU     43
PH_LETSPLAY EQU     44
PH_GAMEOVER EQU     45
PH_FINALSCO EQU     46


;------------------------------------------------------------------------------
; Allocate 8-bit variables in Scratch RAM
;------------------------------------------------------------------------------
SCRATCH     ORG     $100, $100, "-RWBN"

ISRVEC      RMB     2               ; Always at $100 / $101

            ; Task-oriented 8-bit variables
TSKQHD      RMB     1               ; Task queue head
TSKQTL      RMB     1               ; Task queue tail
TSKDQ       RMB     2*(TSKQM+1)     ; Task data queue
TSKACT      RMB     1               ; Number of active tasks

            ; Hand-controller 8-bit variables
SH_TMP      RMB     1               ; Temp storage.
SH_LR0      RMB     3               ;\
SH_FL0      EQU     SH_LR0 + 1      ; |-- Three bytes for left controller
SH_LV0      EQU     SH_LR0 + 2      ;/
SH_LR1      RMB     3               ;\
SH_FL1      EQU     SH_LR1 + 1      ; |-- Three bytes for right controller
SH_LV1      EQU     SH_LR1 + 2      ;/

            ; Misc other stuff
GAME_LEN    RMB     1               ; Length of game in seconds
TIMELEFT    RMB     1               ; Time left in game.
SCORE       RMB     1               ; Score
NUM_CANS    RMB     1               ; Number of cans still onscreen.
M_ROW       RMB     1               ; menu row for arrow

            ; Intellivoice-specific variables
IV.QH       RMB     1               ; Intellivoice: phrase queue head
IV.QT       RMB     1               ; Intellivoice: phrase queue tail
IV.Q        RMB     8               ; Intellivoice: phrase queue
IV.FLEN     RMB     1               ; Intellivoice: FIFO'd data length

_SCRATCH    EQU     $               ; end of scratch area



;------------------------------------------------------------------------------
; Allocate 16-bit variables in System RAM 
;------------------------------------------------------------------------------
SYSTEM      ORG     $2F0, $2F0, "-RWBN"
STACK       RMB     32              ; Reserve 32 words for the stack

            ; Task-oriented 16-bit variables
TSKQ        RMB     (TSKQM + 1)     ; Task queue
TSKTBL      RMB     (MAXTSK * 4)    ; Timer task table

            ; Hand-controller 16-bit variables
SHDISP      RMB     1               ; ScanHand dispatch

            ; STIC shadow
STICSH      RMB     24              ; Room for X, Y, and A regs only.

            ; Misc other stuff
PLYR        PROC     
@@TXV       RMB     1               ; Target X velocity (8.8 fixed)
@@XV        RMB     1               ; X velocity        (8.8 fixed)
@@XP        RMB     1               ; X position        (8.8 fixed)
@@TYV       RMB     1               ; Target Y velocity (8.8 fixed)
@@YV        RMB     1               ; Y velocity        (8.8 fixed)
@@YP        RMB     1               ; Y position        (8.8 fixed)
            ENDP

TODD        PROC                    ; TODD's STATS
@@TXV       RMB     1               ; Target X velocity
@@XV        RMB     1               ; X velocity
@@XP        RMB     1               ; X position
@@TYV       RMB     1               ; Target Y velocity
@@YV        RMB     1               ; Y velocity
@@YP        RMB     1               ; Y position
            ENDP

MOB_BUSY    RMB     1               ; If non-zero, disables MOB updates

; Hijack some CP-1600X registers for commonly used variables.
; NOTE:  Bugs in as1600's macro implementation prevent using these names
; directly.  Sad.
;    
; SKILL     => X8   ; Skill level [1 - 9]
; DURATION  => X9   ; Game duration [1 - 9]
; INIT_VEL  => XA   ; Initial velocity
; TODD_VEL  => XB   ; Todd's velocity (game difficulty)

            ; Intellivoice-specific variables
IV.FPTR     RMB     1               ; Intellivoice: FIFO'd data pointer
IV.PPTR     RMB     1               ; Intellivoice: Phrase pointer

_SYSTEM     EQU     $               ; end of system area


;------------------------------------------------------------------------------
; EXEC-friendly ROM header.
;------------------------------------------------------------------------------
            ORG     $5000           ; Use default memory map
ROMHDR:     BIDECLE ZERO            ; MOB picture base   (points to NULL list)
            BIDECLE ZERO            ; Process table      (points to NULL list)
            BIDECLE MAIN            ; Program start address
            BIDECLE ZERO            ; Bkgnd picture base (points to NULL list)
            BIDECLE ONES            ; GRAM pictures      (points to NULL list)
            BIDECLE TITLE           ; Cartridge title/date
            DECLE   $03C0           ; No ECS title, run code after title,
                                    ; ... no clicks
ZERO:       DECLE   $0000           ; Screen border control
            DECLE   $0000           ; 0 = color stack, 1 = f/b mode
ONES:       DECLE   C_BLU, C_BLU    ; Initial color stack 0 and 1: Blue
            DECLE   C_BLU, C_BLU    ; Initial color stack 2 and 3: Blue
            DECLE   C_BLU           ; Initial border color: Blue
;------------------------------------------------------------------------------


;; ======================================================================== ;;
;;  TITLE  -- Display our modified title screen & copyright date.           ;;
;; ======================================================================== ;;
TITLE:      STRING  119, "Tag-Along Todd #2a CP-1600X", 0

;; ======================================================================== ;;
;;  MAIN:  Here's our main program code.                                    ;;
;; ======================================================================== ;;
MAIN:       PROC
            DIS
            MVII    #STACK, R6      ; Set up our stack

            MVII    #$25D,  R1      ;\
            MVII    #$102,  R4      ; |-- Clear all of memory
            CALL    FILLZERO        ;/

            MVO     PC,     MOB_BUSY; Disable MOBs for now.

            CALL    IV_INIT         ; Initialize Intellivoice (if present)

            MVII    #INITISR, R0    ;\    Do GRAM initialization in ISR.
            MVO     R0,     ISRVEC  ; |__ INITISR will the point to the 
            SWAP    R0              ; |   regular ISR when it's done.
            MVO     R0,     ISRVEC+1;/    
          
            EIS
@@gameloop: 
            CALL    TSCREEN         ; Show title screen
            CALL    RUNQ

            CALL    MENU            ; Get information
            CALL    RUNQ

            CALL    GAME            ; Run the game
            CALL    RUNQ

            CALL    GAMEOVER        ; Game over!
            CALL    RUNQ

            B       @@gameloop
            ENDP

;; ======================================================================== ;;
;;  HEXIT   Dispatch table that just calls SCHEDEXIT for everything.        ;;
;; ======================================================================== ;;
HEXIT       PROC
            DECLE   EXITPRESS
            DECLE   EXITPRESS
            DECLE   EXITPRESS
            ENDP

;; ======================================================================== ;;
;;  EXITPRESS -- Schedule an exit only when a key is pressed, not released. ;;
;; ======================================================================== ;;
EXITPRESS   PROC
            SWAP    R2,     2       ; test bit 7 of R2
            BPL     SCHEDEXIT       ; if clear, schedule the exit
            JR      R5              ; if set, ignore the keypress.
            ENDP

;; ======================================================================== ;;
;;  TSCREEN -- Title screen.                                                ;;
;; ======================================================================== ;;
TSCREEN     PROC
            PSHR    R5

            CALL    CLRSCR

            CALL    PRINT.FLS
            DECLE   C_BLU, $200 + 1*20 + 2
                    ;01234567890123456789
            STRING    ">>> SDK-1600 <<<  "
            STRING  "      presents",0

            CALL    PRINT.FLS
            DECLE   C_DGR, $200 + 6*20 + 2
                    ;01234567890123456789
            STRING    "Tag-Along Todd 2",0

            CALL    PRINT.FLS
            DECLE   C_BLK, $200 + 10*20 + 3
                    ;01234567890123456789
            STRING     "Copyright 2002", 0

            CALL    IV_PLAYW
            DECLE   PH_TITLE   

            CLRR    R0
            MVO     R0,     TSKACT      ; No active tasks

            MVII    #HEXIT, R0
            MVO     R0,     SHDISP      ; Any controller input -> Exit screen

            MVO     PC,     MOB_BUSY    ; Disable MOB updates

            MVII    #STICSH, R4         ;\
            MVII    #24,    R1          ; |-- Clear away the MOBs
            CALL    FILLZERO            ;/

            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  M_HAND  Dispatch table for menu.                                        ;;
;; ======================================================================== ;;
M_HAND      PROC
            DECLE   M_DIGIT     ; Keypad dispatch
            DECLE   0           ; Action-button dispatch -> disabled
            DECLE   M_DISC      ; DISC dispatch
            ENDP

;; ======================================================================== ;;
;;  MENU    Display a menu onscreen.                                        ;;
;; ======================================================================== ;;
MENU        PROC
            PSHR    R5

            CALL    CLRSCR

            ;; ------------------------------------------------------------ ;;
            ;;  Display the menu screen.                                    ;;
            ;; ------------------------------------------------------------ ;;
            CALL    PRINT.FLS
            DECLE   C_DGR,  $200 + 2*20 + 1
                    ;01234567890123456789
            STRING  "Skill level [1-9]:", 0

            CALL    PRINT.FLS
            DECLE   C_DGR,  $200 + 5*20 + 1
                    ;01234567890123456789
            STRING  "Duration    [1-9]:", 0

            CALL    PRINT.FLS
            DECLE   C_BLU,  $200 + 3*20 + 9 
            STRING  "5", 0

            CALL    PRINT.FLS
            DECLE   C_BLU,  $200 + 6*20 + 9 
            STRING  "5", 0

            CALL    PRINT.FLS
            DECLE   C_BLU,  $200 + 9*20 + 8 
            STRING  "Go!", 0

            ;; ------------------------------------------------------------ ;;
            ;;  Set the defaults.                                           ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$A000, R0
            MVO     R0,     XA
            MVII    #50,    R0
            MVO     R0,     GAME_LEN
            MVII    #5,     R0
            MVO     R0,     X8
            MVO     R0,     X9

            MVII    #3*20,  R0
            MVO     R0,     M_ROW

            ;; ------------------------------------------------------------ ;;
            ;;  Set the dispatch and menu animate task.                     ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #M_HAND,R0
            MVO     R0,     SHDISP

            CALL    STARTTASK           ;\
            DECLE   0                   ; |__ Blink the little arrow
            DECLE   M_BLINK             ; |
            DECLE   30,     30          ;/
            
            MVII    #1,     R0
            MVO     R0,     TSKACT
            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  M_DIGIT -- Enter a digit on the current menu row.                       ;;
;;             Pressing enter moves to next row, or if at last, starts game ;;
;; ======================================================================== ;;
M_DIGIT     PROC
            ANDI    #$FF,   R2          ; ignore controller #.
            CMPI    #$80,   R2
            BLT     @@press             ; ignore release events.
@@leave:    JR      R5

@@press:    TSTR    R2
            BEQ     @@leave             ; ignore 'zero'
            CMPI    #10,    R2
            BEQ     @@leave             ; ignore 'clear'
            BLT     @@digit

            ;; ------------------------------------------------------------ ;;
            ;;  Handle the [Enter] key:  Move to next row in menu, or if    ;;
            ;;  on last row of menu, start the game.                        ;;
            ;; ------------------------------------------------------------ ;;
@@enter:    MVI     M_ROW,  R4
            ADDI    #$200 + 12, R4
            CLRR    R0
            MVO@    R0,     R4          ; Clear arrow from current row

            MVI     M_ROW,  R1
            ADDI    #3*20,  R1          ; move to next row
            CMPI    #9*20,  R1          ; were we on last row?
            BGT     SCHEDEXIT           ; Enter on last row starts game. 

            MVO     R1,     M_ROW
            ADDI    #$200 + 12, R1
            MVII    #ARROW, R0
            MVO@    R0,     R1          ; Put arrow on current row
            JR      R5

            ;; ------------------------------------------------------------ ;;
            ;;  Handle digits [1] through [9].                              ;;
            ;; ------------------------------------------------------------ ;;
@@digit:    MVI     M_ROW,  R4
            CMPI    #6*20,  R4
            BGT     @@leave             ; Ignore digits when in last row
            BEQ     @@update_duration

            ;; ------------------------------------------------------------ ;;
            ;;  If we are on the top row, the input updates skill level.    ;;
            ;; ------------------------------------------------------------ ;;
            MVO     R2,     X8
            ROL     X8, 13, XA 
            B       @@disp

            ;; ------------------------------------------------------------ ;;
            ;;  If we are on the middle row, the input updates the game     ;;
            ;;  duration.                                                   ;;
            ;; ------------------------------------------------------------ ;;
@@update_duration:
            MVO     R2,     X9
            MPYUU   X9, 10, X0
            MVI     X0,     R0
            MVO     R0,     GAME_LEN  ; Game length = 10 seconds * digit.

            ;; ------------------------------------------------------------ ;;
            ;;  Either way, if we're on the upper two rows, show the digit. ;;
            ;; ------------------------------------------------------------ ;;
@@disp:     ADDI    #$200+9,R4          ; offset to digit position in row.
            SHL3    R2, 3,  X0          ; move digit to card field in word
            MVII    #$80 + C_BLU, R1    ; add offset for '0', make digit blue
            ADD     X0,     R1
            MVO@    R1,     R4          ; show it.
            
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  M_DISC  -- Move the selection arrow between menu rows.                  ;;
;; ======================================================================== ;;
M_DISC      PROC
            ANDI    #$FF,   R2          ; ignore controller #.
            CMPI    #$80,   R2
            BLT     @@press             ; ignore release events.
@@leave:    JR      R5
@@press:
            MVI     M_ROW,  R0          ; Get menu row
            MOVR    R0,     R1          ; save old position

            CMPI    #2,     R2
            BLT     @@leave             ; Ignore 'east' (directions 0, 1)
            CMPI    #13,    R2
            BGT     @@leave             ; Ignore 'east' (directions 14, 15)
            CMPI    #5,     R2
            BLE     @@move_up           ; Directions 2 - 5:  Move up
            CMPI    #10,    R2
            BLT     @@leave             ; Ignore 'west' (directions 6 - 9)

        
@@move_dn:  ADDI    #3*20,  R0          ; Move down to next item
            CMPI    #9*20,  R0          ; Is it past the end?
            BGT     @@leave             ; Yes:  Ignore the input
            MVO     R0,     M_ROW       ; No:   Save the update

            ADDI    #$200 + 12, R1      ;\    Move to old arrow's position
            CLRR    R0                  ; |-- and clear the old arrow
            MVO@    R0,     R1          ;/
                                      
            ADDI    #3*20,  R1          ;\    Move to new arrow's position
            MVII    #ARROW, R0          ; |-- and draw the new arrow.
            MVO@    R0,     R1          ;/
            JR      R5                  ; return.
                                      
@@move_up   SUBI    #3*20,  R0          ; Move up to prev item
            CMPI    #3*20,  R0          ; Is it past the top
            BLT     @@leave             ; Yes:  Ignore the input
            MVO     R0,     M_ROW       ; No:   Save the update
                                      
            ADDI    #$200 + 12, R1      ;\    Move to old arrow's position
            CLRR    R0                  ; |-- and clear the old arrow
            MVO@    R0,     R1          ;/
                                      
            SUBI    #3*20,  R1          ;\    Move to new arrow's position
            MVII    #ARROW, R0          ; |-- and draw the new arrow.     
            MVO@    R0,     R1          ;/                                
            JR      R5                  ; return.                         
            
            ENDP

;; ======================================================================== ;;
;;  M_BLINK -- Blink the arrow on the menu.                                 ;;
;; ======================================================================== ;;
M_BLINK     PROC
            MVI     M_ROW,  R1          ; Get menu row
            ADDI    #$200 + 12, R1      ; Offset to arrow position
            MVII    #ARROW, R2          ;\
            XOR@    R1,     R2          ; |-- Toggle the arrow on and off.
            MVO@    R2,     R1          ;/
            JR      R5                  ; return.
            ENDP

;; ======================================================================== ;;
;;  GAMEOVER -- Game-over screen.                                           ;;
;; ======================================================================== ;;
GAMEOVER    PROC
            PSHR    R5

            ;; ------------------------------------------------------------ ;;
            ;;  Say "Game Over!"                                            ;;
            ;; ------------------------------------------------------------ ;;
            CALL    IV_PLAY
            DECLE   PH_GAMEOVER

            ;; ------------------------------------------------------------ ;;
            ;;  Make a long 'ding'.                                         ;;
            ;;  Channel A Period = $0200     Channel A Volume = Envelope    ;;
            ;;  Envelope Period  = $3FFF     Envelope type = 0000           ;;
            ;;  Enables = Tone only on A, B, C.                             ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$02,   R1
            MVO     R1,     PSG0.chn_a_hi
            MVII    #$38,   R1
            MVO     R1,     PSG0.chan_enable
            MVO     R1,     PSG0.chn_a_vol
            MVII    #$FF,   R1
            MVO     R1,     PSG0.envlp_lo
            MVII    #$3F,   R1
            MVO     R1,     PSG0.envlp_hi
            CLRR    R1
            MVO     R1,     PSG0.chn_a_lo
            MVO     R1,     PSG0.envelope

            ;; ------------------------------------------------------------ ;;
            ;;  Show the "Game Over!" message.  Also show the skill level   ;;
            ;;  and game duration, in case the player wants to make a       ;;
            ;;  screen-shot.                                                ;;
            ;; ------------------------------------------------------------ ;;
            CALL    PRINT.FLS
            DECLE   C_RED, $200 + 4*20 + 4
                    ;01234567890123456789
            STRING      " GAME OVER! ",0

            CALL    PRINT.FLS
            DECLE   C_BLU, $200 + 6*20 + 5
                    ;01234567890123456789
            STRING       " Skill:  ", 0

            SHL3    X8,  3,  X1
            MVI     &X1($80 + C_DGR), R0
            MVO@    R0,     R4

            CALL    PRINT.FLS
            DECLE   C_BLU, $200 + 7*20 + 4
                    ;01234567890123456789
            STRING      " Length:  ", 0

            SHL3    X9,  3,  X1
            MVI     &X1($80 + C_DGR), R0
            MVO@    R0,     R4


            ;; ------------------------------------------------------------ ;;
            ;;  Force the MOBs to not update.  Clear them from the screen.  ;;
            ;; ------------------------------------------------------------ ;;
            MVO     PC,     MOB_BUSY

            MVII    #STICSH, R4
            MVII    #24,    R1
            CALL    FILLZERO

            ;; ------------------------------------------------------------ ;;
            ;;  Say "Final score"                                           ;;
            ;; ------------------------------------------------------------ ;;
            CALL    IV_PLAY
            DECLE   PH_FINALSCO 

            MVI     SCORE,  R0
            CALL    IV_SAYNUM16

            ;; ------------------------------------------------------------ ;;
            ;;  Disable hand controllers for now, but schedule them to be   ;;
            ;;  set up in 2 seconds.  When they do get set up, pressing     ;;
            ;;  any key will go back to the menu.  This task is a one-shot. ;;
            ;; ------------------------------------------------------------ ;;
            CALL    STARTTASK
            DECLE   0
            DECLE   @@set_hexit
            DECLE   241,    241     ; Set up HEXIT as dispatch after 1 second

            CLRR    R0
            MVO     R0,     SHDISP  ; Until then, drop all controller input

            MVII    #1,     R0
            MVO     R0,     TSKACT

            PULR    PC              ; return to "RUNQ".


            ;; ------------------------------------------------------------ ;;
            ;;  This will get called in 1 second to set up the hand-        ;;
            ;;  controller dispatch.  The HEXIT dispatch will cause any     ;;
            ;;  keypress input to exit "GAME OVER" mode and go to the menu. ;;
            ;; ------------------------------------------------------------ ;;
@@set_hexit:
            MVII    #HEXIT, R0
            MVO     R0,     SHDISP
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  GAME -- Set up the game state.                                          ;;
;; ======================================================================== ;;
GAME        PROC
            PSHR    R5

            ;; ------------------------------------------------------------ ;;
            ;;  Set up the display.                                         ;;
            ;; ------------------------------------------------------------ ;;
            CALL    CLRSCR

            MVII    #$2000, R0
            MVO     R0,     $200 + 11*20    ; Bottom row is blue
            
            CALL    PRINT.FLS
            DECLE   C_YEL,  $200 + 11*20 + 1
                    ;01234567890123456789
            STRING   "Time:     Cans:    ",0

            MVII    #$80 + C_WHT, R0
            MVO     R0,     $200 + 11*20 + 18   ; 0 in 'score'

            ;; ------------------------------------------------------------ ;;
            ;;  Set up our hand-controller dispatch.                        ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #HAND,  R0      ;\__ Set up scanhand dispatch table
            MVO     R0,     SHDISP  ;/

            ;; ------------------------------------------------------------ ;;
            ;;  Set up Todd's AI.                                           ;;
            ;; ------------------------------------------------------------ ;;
            CALL    STARTTASK
            DECLE   0
            DECLE   TODDTASK
            DECLE   120, 40         ; 3Hz (three times a second)

            ;; ------------------------------------------------------------ ;;
            ;;  Set up round timer.                                         ;;
            ;; ------------------------------------------------------------ ;;
            CALL    STARTTASK
            DECLE   1
            DECLE   GAMETIME
            DECLE   2, 120

            MVI     GAME_LEN, R0
            INCR    R0
            MVO     R0,     TIMELEFT


            ;; ------------------------------------------------------------ ;;
            ;;  Reset info for you and Todd.                                ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #PLYR,  R4
            MVII    #12,    R1
            CALL    FILLZERO

            ;; ------------------------------------------------------------ ;;
            ;;  Put you and Todd onscreen.                                  ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$0010, R0
            MVO     R0,     PLYR.XP
            MVO     R0,     PLYR.YP

            MVII    #$009B, R0
            MVO     R0,     TODD.XP
            MVII    #$0055, R0
            MVO     R0,     TODD.YP

            ADD3    XA, 0,  XB          ; Move INIT_VEL to TODD_VEL

            ;; ------------------------------------------------------------ ;;
            ;;  Randomly display a dozen goodies.                           ;;
            ;; ------------------------------------------------------------ ;;
            CALL    DISPDOZ

            ;; ------------------------------------------------------------ ;;
            ;;  Enable MOBs.                                                ;;
            ;; ------------------------------------------------------------ ;;
            CLRR    R0
            MVO     R0,     MOB_BUSY

            ;; ------------------------------------------------------------ ;;
            ;;  Reset our score                                             ;;
            ;; ------------------------------------------------------------ ;;
            MVO     R0,     SCORE

            ;; ------------------------------------------------------------ ;;
            ;;  Todd says "Lets Play!"                                      ;;
            ;; ------------------------------------------------------------ ;;
            CALL    IV_PLAY
            DECLE   PH_LETSPLAY

            CALL    IV_PLAY
            DECLE   RESROM.pa2

            CALL    IV_WAIT

            ;; ------------------------------------------------------------ ;;
            ;;  Start all the tasks only after Todd is done speaking.       ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #2,     R0
            MVO     R0,     TSKACT

            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  DISPDOZ  -- Display a dozen goodies.                                    ;;
;; ======================================================================== ;;
DISPDOZ     PROC
            PSHR    R5

            MVII    #CAN,   R2          ; Value to write to display pop can.
            MVII    #12,    R1          ; dozen == 12.  :-)
            MVO     R1,     NUM_CANS    ; Re-initialize our can counter.
            MVO     R1,     X4

            ADD3x   R1, 220 - 12, X1    ; X1 = 220
;           MVII    #220,   R3
;           MVO     R3,     X1

@@gloop:    ; Generate a random number 0..219
            MVI     JLP.rand,       R0  ; Get a 16-bit random value
            MPYUU   R0,     X1,     X2  ; X2:X1 = rand * 220
            
            CMP     @X3($200), R2       ; Already a can there?
            BEQ     @@gloop             ; Yes:  Pick somewhere else.

            MVO     R2,     @X3($200)   ; No:  Put a can there
            DECBNZ  X4,     @@gloop     

            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  GAMETIME -- The game timer.  Counts down remaining time in game.        ;;
;; ======================================================================== ;;
GAMETIME    PROC

            ;; ------------------------------------------------------------ ;;
            ;;  Todd gradually gets faster.                                 ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$0100, R0
            ADDFX   R0, XB, XB

            ;; ------------------------------------------------------------ ;;
            ;;  Count down the timer.                                       ;;
            ;; ------------------------------------------------------------ ;;
            MVI     TIMELEFT, R0
            DECR    R0
            BMI     SCHEDEXIT           ; Game is over if timer expires.
            MVO     R0,     TIMELEFT

            ;; ------------------------------------------------------------ ;;
            ;;  Make a short 'ding'.                                        ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$40,   R1
            MVO     R1,     PSG0.chn_a_lo
            CLRR    R1
            MVO     R1,     PSG0.chn_a_hi
            MVII    #$38,   R1
            MVO     R1,     PSG0.chan_enable
            MVO     R1,     PSG0.chn_a_vol
            MVII    #$3F,   R1
            MVO     R1,     PSG0.envlp_lo
            CLRR    R1
            MVO     R1,     PSG0.envlp_hi
            MVO     R1,     PSG0.envelope
            
            ;; ------------------------------------------------------------ ;;
            ;;  Display 2-digit clock.  Time-left is still in R0.           ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #3,     R2          ; 2-digit field
            MVII    #C_WHT, R3      
            MVII    #$200+11*20+7, R4   ; Where to put time.
            B       DEC16A

            ENDP

;; ======================================================================== ;;
;;  SINTBL  -- Sine table.  sin(disc_dir) * 511                             ;;
;; ======================================================================== ;;
SINTBL      PROC
            DECLE   $0000
            DECLE   $00C3
            DECLE   $0169
            DECLE   $01D8
            DECLE   $01FF
            DECLE   $01D8
            DECLE   $0169
            DECLE   $00C3
            DECLE   $0000
            DECLE   $FF3D
            DECLE   $FE97
            DECLE   $FE28
            DECLE   $FE01
            DECLE   $FE28
            DECLE   $FE97
            DECLE   $FF3D
            ; Extra 4 entries for COS
            DECLE   $0000
            DECLE   $00C3
            DECLE   $0169
            DECLE   $01D8
            ENDP

;; ======================================================================== ;;
;;  HAND    Dispatch table.                                                 ;;
;; ======================================================================== ;;
HAND        PROC
            DECLE   HIT_KEYPAD
            DECLE   HIT_ACTION
            DECLE   HIT_DISC
            ENDP

;; ======================================================================== ;;
;;  HIT_KEYPAD -- Someone hit a key on a keypad.                            ;;
;; ======================================================================== ;;
HIT_KEYPAD  PROC
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  HIT_ACTION -- Someone hit a key on a keypad.                            ;;
;; ======================================================================== ;;
HIT_ACTION  PROC
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  HIT_DISC   -- Someone hit a key on a keypad.                            ;;
;; ======================================================================== ;;
HIT_DISC    PROC
            PSHR    R5

            CLRR    R0

            ANDI    #$FF,   R2      ; Ignore controller number
            CMPI    #$80,   R2
            BLT     @@pressed

            MVO     R0,     PLYR.TXV
            MVO     R0,     PLYR.TYV
            PULR    PC

@@pressed:  
            MVO     R2,     X1
            SUB     @X1(SINTBL), R0     ; Look up Y vel in sine table
            SARC    R0                  ; slow down a bit
            SWAP    R0                  ; fixed point
            MVO     R0,     PLYR.TYV

            MVI     @X1(SINTBL + 4), R0 ; Look up X vel in sine table
            SARC    R0                  ; slow down a bit
            SWAP    R0                  ; fixed point
            MVO     R0,     PLYR.TXV

            PULR    PC

            ENDP

;; ======================================================================== ;;
;;  TODDTASK   -- Todd wants to find you!                                   ;;
;; ======================================================================== ;;
TODDTASK    PROC
            
            ;; ------------------------------------------------------------ ;;
            ;;  This is really simple:  Todd will pick one of 8 directions  ;;
            ;;  to walk in to try to move towards you.  He picks this only  ;;
            ;;  based on whether you're left/right or above/below him.      ;;
            ;;                                                              ;;
            ;;  Todd's aiming is imprecise:  The aiming algorithm looks     ;;
            ;;  at the X and Y deltas after dividing coordinates by 4, and  ;;
            ;;  treats the coordinates as equal if they're within +/-1 of   ;;
            ;;  each other.                                                 ;;
            ;; ------------------------------------------------------------ ;;
            MVII        #$FF,       R0
            MVO         R0,         X3  ; Needed for BOUND below

            MVI         PLYR.XP,    R0
            DIVFXU      R0,   4,    X0
            MVI         TODD.XP,    R0
            DIVFXU      R0,   4,    X1

            NOP                         ; to be optimized later

            CMPLTFXU    X0,   X1,   X0  ; -1 if Player left of Todd
            BOUNDU      X3,    1,   X0  ; make into +/-01.00 fixed point
            SUBABSFXU   X0,   X1,   X2  ; Magnitude of X difference
            CMPGTFXU&   X2,    1,   X0  ; Zero out if not enough difference
                                        ; X0 is now -01.00, 00.00 or +01.00 
            NOP                         ; to be optimized later
            MPYFXSS     XB,   X0,   X0  ; Apply sgn() to velocity
            MVI         X0,         R0
            MVO         R0,   TODD.TXV  ; Set Todd's target X velocity
            
            MVI         PLYR.YP,    R0
            DIVFXU      R0,    4,   X0
            MVI         TODD.YP,    R0
            DIVFXU      R0,    4,   X1

            NOP                         ; to be optimized later

            CMPLTFXU    X0,   X1,   X0  ; -1 if Player above Todd
            BOUNDU      X3,    1,   X0  ; make into +/-01.00 fixed point
            SUBABSFXU   X0,   X1,   X2  ; Magnitude of Y difference
            CMPGTFXU&   X2,    1,   X0  ; Zero out if not enough difference
            NOP                         ; to be optimized later
                                        ; X0 is now -01.00, 00.00 or +01.00 
            MPYFXSS     XB,   X0,   X0  ; Apply sgn() to velocity
            MVI         X0,         R0
            MVO         R0,   TODD.TYV  ; Set Todd's target Y velocity
            JR          R5
            ENDP

;; ======================================================================== ;;
;;  MOB_UPDATE -- This updates the player's and Todd's position and vel.    ;;
;; ======================================================================== ;;
MOB_UPDATE  PROC
            PSHR    R5

            ;; Set up +/-01.00 bounds
            MVII    #$00FF, R0
            MVO     R0,     X4          ; For $01/$FF bounds check

            ;; Set up X/Y bounds
            MVII    #$0009, R0
            MVO     R0,     X5          ; X/Y lower bound
            MVII    #$009F, R0
            MVO     R0,     X6          ; X lower bound (unsigned)
            MVII    #$0057, R0
            MVO     R0,     X7          ; Y lower bound (unsigned)

            ;; ------------------------------------------------------------ ;;
            ;;  Call the velocity/position update for PLYR X/Y, TODD X/Y.   ;;
            ;;  This code relies on PLYR and TODD being next to each other  ;;
            ;;  in memory, and @@update advancing R4 through them.          ;;.
            ;; ------------------------------------------------------------ ;;
            MVII    #PLYR,      R4
            CALL    @@update
            DMOV    X6,   X7,   X6      ; Swap X6/X7  (X/Y upper bounds)
            CALL    @@update
            DMOV    X6,   X7,   X6      ; Swap X6/X7  (X/Y upper bounds)
            CALL    @@update
            DMOV    X6,   X7,   X6      ; Swap X6/X7  (X/Y upper bounds)
            CALL    @@update

            ;; ------------------------------------------------------------ ;;
            ;;  Merge our position with our MOB registers.                  ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #@@mobr,    R4      ; MOB information template
            MVII    #STICSH,    R5

            MVI     PLYR.XP,    R0      ;\
            ANDI    #$00FF,     R0      ; |- Player X position
            XOR@    R4,         R0      ; |
            MVO@    R0,         R5      ;/

            MVI     TODD.XP,    R0      ;\
            ANDI    #$00FF,     R0      ; |- Todd X position
            XOR@    R4,         R0      ; |
            MVO@    R0,         R5      ;/

            ADDI    #6,         R5
            
            MVI     PLYR.YP,    R0      ;\
            ANDI    #$007F,     R0      ; |- Player Y position
            XOR@    R4,         R0      ; |
            MVO@    R0,         R5      ;/

            MVI     TODD.YP,    R0      ;\
            ANDI    #$007F,     R0      ; |- Todd Y position
            XOR@    R4,         R0      ; |
            MVO@    R0,         R5      ;/

            ADDI    #6,         R5

            MVI@    R4,         R0      ; \_ Player's A register
            MVO@    R0,         R5      ; /
            MVI@    R4,         R0      ; \_ Todd's A register
            MVO@    R0,         R5      ; /                     

            CLRR    R0
            MVO     R0,         MOB_BUSY

            ;; ------------------------------------------------------------ ;;
            ;;  See if we're on a pop can.                                  ;;
            ;; ------------------------------------------------------------ ;;
            MVI     PLYR.YP,R1      ;\
            ANDI    #$00FF, R1      ; |
            SHRU3   R1, 2,  X0      ; |
            SUB3    X0, 1,  X0      ; |- Generate row offset from Y coord.
            AND3    X0, -2, X0      ; |  ((y_coord - 4) / 8) * 20
            MPY16   X0, 10, X0      ;/

            MVI     PLYR.XP,R1      ;\
            ANDI    #$00FF, R1      ; |
            SHRU3   R1, 2,  X1      ; |_ Generate col offset from X coord.
            SUB3    X1, 1,  X1      ; |  (x_coord - 4) / 8
            SHRU3   X1, 1,  X1      ;/ 

            ADD3    X1, X0, X0      ; Convert into screen offset.

            MVI     @X0($200), R1   ; Index into the screen
            XORI    #CAN,   R1      ; A pop can here?
            BNEQ    @@no_can

            MVO     R1, @X0($200)   ; Yes:  Clear it.

            MVI     SCORE,  R0
            INCR    R0
            MVO     R0,     SCORE   ; Add 1 to score

            MVII    #$200+11*20+16, R4
            MVII    #$2,    R2      ; 3-digit field
            MVII    #C_WHT, R3      ; no leading zeros, score in white
            CALL    DEC16           ; Show updated score

            MVI     NUM_CANS, R0    ;\
            DECR    R0              ; |-- Decrement remaining can count
            MVO     R0, NUM_CANS    ;/
            BNEQ    @@some_left
            CALL    DISPDOZ         ; Display another dozen if we run out.
@@some_left:
@@no_can:

            ;; ------------------------------------------------------------ ;;
            ;;  See if Todd's caught us.  He's caught us if our coords are  ;;
            ;;  both within 4 pixels of each other.  This tight tolerance   ;;
            ;;  allows us to brush past Todd and not get caught.  :-)       ;;
            ;; ------------------------------------------------------------ ;;
            MVI         PLYR.XP,R0
            MVO         R0,     X0
            MVI         TODD.XP,R0
            SUBABSFX    R0, X0, X0
            CMPLTFXU    X0,  4, X1  ; Less than 4... caught?
            
            MVI         PLYR.YP,R0
            MVO         R0,     X0
            MVI         TODD.YP,R0
            SUBABSFX    R0, X0, X0
            CMPLTFXU&   X0,  4, X1  ; Also less than 4... caught!

            TSTBNZ      X1, @@caught
            PULR        PC

@@caught:
            PULR        R5
            B           SCHEDEXIT   ; If Todd catches up to us, it's gameover

            ;; ------------------------------------------------------------ ;;
            ;;  Bits to copy into MOB registers.                            ;;
            ;; ------------------------------------------------------------ ;;
@@mobr      DECLE   STIC.mobx_visb      ; make player visible
            DECLE   STIC.mobx_visb      ; make Todd visible

            DECLE   STIC.moby_yres      ; make player 8x16 MOB
            DECLE   STIC.moby_yres      ; make Todd 8x16 MOB

            DECLE   STIC.moba_fg1 + STIC.moba_gram + 0*8    ; Player is blue
            DECLE   STIC.moba_fg2 + STIC.moba_gram + 0*8    ; Todd is red

            ;; ------------------------------------------------------------ ;;
            ;;  Update the target velocity and position for one of the      ;;
            ;;  player coordinates.  Expects X5/X6 to hold the display      ;;
            ;;  bounds for the current position.                            ;;
            ;; ------------------------------------------------------------ ;;
@@update:
            MVI@        R4,         R0  ; Target Velocity
            MVI@        R4,         R1  ; \_ Velocity
            MVO         R1,         X0  ; /

            SUBFX       R0,   X0,   X1  ; Velocity difference

            CMPLTFX     X1,    0,   X2  ; \_ +/- 01.00 based on sign of
            BOUNDU      X4,    1,   X2  ; /  difference

            MVII        #$0300,     R1  ; Round away from zero (00.03)
            MPYFXSS     R1,   X2,   X2  ; +/- 00.03 based on sign of diff
            ADDFX       X1,   X2,   X1  ; Add rounding term
            DIVFXS      X1,    4,   X1  ; Divide by 04.00

            ADDFX       X1,   X0,   X0  ; Add rounded diff to velocity
            MVI         X0,         R0  ; Updated velocity

            MVI@        R4,         R1
            ADDFX       R1,   X0,   X0  ; Updated position
            BOUNDFXU    X5,   X6,   X0  ; Clamp to screen
            MVI         X0,         R1  ; Updated position

            SUBI        #2,         R4
            MVO@        R0,         R4  ; Save updated velocity
            MVO@        R1,         R4  ; Save updated position
            JR          R5

            ENDP
    

;; ======================================================================== ;;
;;  ISR -- Just keep the screen on, and copy the STIC shadow over.          ;;
;; ======================================================================== ;;
ISR         PROC

            ;; ------------------------------------------------------------ ;;
            ;;  Basics:  Update color stack and video enable.               ;;
            ;; ------------------------------------------------------------ ;;
            MVO     R0,     STIC.viden  ; Enable display
            MVI     STIC.mode, R0       ; ...in color-stack mode

            MVII    #C_GRY, R0          ;\___ Set main display to grey
            MVO     R0,     STIC.cs0    ;/
            MVII    #C_BLU, R0
            MVO     R0,     STIC.cs1    ;\___ Set border, bottom to blue
            MVO     R0,     STIC.bord   ;/

            ;; ------------------------------------------------------------ ;;
            ;;  Update STIC shadow and queue updates for MOB velocities.    ;;
            ;; ------------------------------------------------------------ ;;

            CALL    MEMCPY              ;\__ Copy over the STIC shadow.
            DECLE   $0000, STICSH, 24   ;/

            MVI     MOB_BUSY, R0        ; Skip MOB updates if told to.
            TSTR    R0
            BNEQ    @@no_mobs
            MVO     PC,     MOB_BUSY

            MVII    #MOB_UPDATE, R0
            JSRD    R5,   QTASK     ; Note JSRD:  Must disable ints for QTASK!
@@no_mobs:  

            ;; ------------------------------------------------------------ ;;
            ;;  Feed the Intellivoice.                                      ;;
            ;; ------------------------------------------------------------ ;;
            CALL    IV_ISR

            ;; ------------------------------------------------------------ ;;
            ;;  Update timer-based tasks and return via stock interrupt     ;;
            ;;  return code.                                                ;;
            ;; ------------------------------------------------------------ ;;
            MVII    #$1014, R5          ; return from interrupt address.
            B       DOTIMER             ; Update timer-based tasks.
            ENDP

;; ======================================================================== ;;
;;  INITISR -- Copy our GRAM image over, and then do the plain ISR.         ;;
;; ======================================================================== ;;
INITISR     PROC
            PSHR    R5

            CALL    MEMUNPK
            DECLE   $3800, GRAMIMG, GRAMIMG.end - GRAMIMG

            MVII    #ISR,   R0
            MVO     R0,     ISRVEC
            SWAP    R0
            MVO     R0,     ISRVEC + 1

            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  GRAMIMG -- Arrow pictures and other graphics to load into GRAM.         ;;
;;  These are stored two bytes-per-word.  Use MEMUNPK to load into GRAM.    ;;
;; ======================================================================== ;;
GRAMIMG     PROC

@@person:   ; Crappy person graphic.   (2 cards)
            ; ...#.... 0
            ; ..###... 1
            ; ..###... 2
            ; ...#.... 3
            ; ...#.... 4
            ; .#####.. 5
            ; #.###.#. 6
            ; #.###.#. 7
            ; #.###.#. 8
            ; #.###.#. 9
            ; ..###... A
            ; ..#.#... B
            ; ..#.#... C
            ; ..#.#... D
            ; ..#.#... E
            ; .##.##.. F
            DECLE   %0011100000010000 ;10
            DECLE   %0001000000111000 ;32
            DECLE   %0111110000010000 ;54
            DECLE   %1011101010111010 ;76
            DECLE   %1011101010111010 ;98
            DECLE   %0010100000111000 ;BA
            DECLE   %0010100000101000 ;DC
            DECLE   %0110110000101000 ;FE

@@can:      ; Pop Can graphic
            ; ........ 0
            ; ........ 1
            ; .###.... 2
            ; #...#... 3
            ; .#####.. 4
            ; ..#####. 5
            ; ...###.. 6
            ; ........ 7
            DECLE   %0000000000000000 ;10
            DECLE   %1000100001110000 ;32
            DECLE   %0011111001111100 ;54
            DECLE   %0000000000011100 ;76

@@arrow:    ; Arrow graphic
            ; ........ 0
            ; ........ 1
            ; ..##.... 2
            ; .##..... 3
            ; ######## 4
            ; .##..... 5
            ; ..##.... 6
            ; ........ 7
            DECLE   %0000000000000000 ; 10
            DECLE   %0110000000110000 ; 32
            DECLE   %0110000011111111 ; 54
            DECLE   %0000000000110000 ; 76

@@end:      
            ENDP

;; ======================================================================== ;;
;;  IV_PHRASE_TBL -- These are phrases that will be spoken.                 ;;
;; ======================================================================== ;;
IV_PHRASE_TBL PROC
            DECLE       PHRASE.title
            DECLE       PHRASE.letsplay
            DECLE       PHRASE.gameover
            DECLE       PHRASE.finalscor
            ENDP

PHRASE      PROC
@@title     DECLE       _JH, _OW, RESROM.pa2
            DECLE       _ZZ, RESROM.pa1, _BB1, _EY, _CH, _EH, _KK1, RESROM.pa2
            DECLE       _PP, _RR1, _IY, _ZZ, _ZH, _EH, _NN1, _TT1, _SS, _SS
            DECLE       RESROM.pa2
            DECLE       _TT2, _AX, _GG3, RESROM.pa1
            DECLE       _AX, _LL, _AO, _NG1, _GG2, RESROM.pa2
            DECLE       _TT2, _AO, _AO, RESROM.pa1, _DD1, RESROM.pa2
            DECLE       _TT2, _UW2, RESROM.pa2
            DECLE       0

@@letsplay  DECLE       _LL, _EH, _EH, RESROM.pa1, _TT2, _SS, RESROM.pa2
            DECLE       _PP, _LL, _EH, _EY, RESROM.pa2
            DECLE       0

@@gameover  DECLE       RESROM.pa5
            DECLE       _GG3, _EY, _MM, RESROM.pa2
            DECLE       _OW, _VV, _ER1, RESROM.pa5
            DECLE       0

@@finalscor DECLE       _FF, _AY, _NN2, _AX, _LL, RESROM.pa2
            DECLE       _SS, _SS, RESROM.pa1, _KK3, _OR, RESROM.pa3
            DECLE       0
            ENDP


;; ======================================================================== ;;
;;  RAND                                                                    ;;
;;      Returns random bits in R0.                                          ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;      R0 -- Number of bits desired (1..15)                                ;;
;;      R5 -- Return address                                                ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- N random bits.                                                ;;
;;      R1, R2, R3, R4 -- Saved and restored                                ;;
;;      X0 .. XD -- preserved                                               ;;
;;      XE, XF -- trashed.                                                  ;;
;;      R5 -- trashed.                                                      ;;
;; ======================================================================== ;;
RAND        PROC
            MVO     R0,     XF
            MVI     JLP.rand,       R0
            SHLU3   R0,     XF,     XE          ; shifts into XF:XE
            MVI     XF,     R0
            JR      R5
            ENDP

;; ======================================================================== ;;
;;  LIBRARY INCLUDES                                                        ;;
;; ======================================================================== ;;
            INCLUDE "../library/print.asm"      ; PRINT.xxx routines
            INCLUDE "../library/fillmem.asm"    ; CLRSCR/FILLZERO/FILLMEM
            INCLUDE "../library/memcpy.asm"     ; MEMCPY
            INCLUDE "../library/memunpk.asm"    ; MEMUNPK
            INCLUDE "dec16_cp1600x.asm"         ; DEC16
            INCLUDE "../task/scanhand.asm"      ; SCANHAND
            INCLUDE "../task/timer.asm"         ; Timer-based task stuff
            INCLUDE "../task/taskq.asm"         ; RUNQ/QTASK
            INCLUDE "../library/ivoice.asm"     ; IV_xxx routines.
            INCLUDE "../library/saynum16.asm"   ; IV_SAYNUM16
            INCLUDE "../library/al2.asm"        ; AL2 allophone library.

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
;*                   Copyright (c) 2002, Joseph Zbiciak                     *;
;* ======================================================================== *;
