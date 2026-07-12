;; ======================================================================== ;;
;;  JLP Flash "Save Game" support                                           ;;
;;                                                                          ;;
;;  Low-level routines:                                                     ;;
;;                                                                          ;;
;;  JF.INIT  -- Initializes System RAM with JLP Flash subroutines.          ;;
;;  JF.CMD   -- Executes a JLP Flash command.                               ;;
;;                                                                          ;;
;;  The low-level routines provide raw access to JLP's flash.  Ordinarily   ;;
;;  you will not need these, unless you want to erase all storage or        ;;
;;  implement your own save/load routines.                                  ;;
;;                                                                          ;;
;;  Requires the game to declare a region of 4 words in System RAM at the   ;;
;;  label JF.SYSRAM.  Also requires the stack to reside in System RAM, and  ;;
;;  13 words of stack space.  (5 words for JF.CMD + 8 for ISR.)             ;;
;;                                                                          ;;
;;  High-level routines:                                                    ;;
;;                                                                          ;;
;;  JF.LOAD  -- Loads a 94-word game record from JLP Flash, if any.         ;;
;;  JF.SAVE  -- Saves a 94-word game record to JLP Flash.                   ;;
;;                                                                          ;;
;;  The high-level routines use JLP's flash storage to save game state in   ;;
;;  a record that holds up to 94 words.  From the game's point of view,     ;;
;;  only the most recent record is kept.                                    ;;
;;                                                                          ;;
;;  JF.SAVE requires the information initialized by JF.LOAD.  Most games    ;;
;;  will call JF.INIT and JF.LOAD initially to get saved state, and then    ;;
;;  JF.SAVE to update saved state.  If you ever manually update/erase       ;;
;;  saved state with calls to JF.CMD, call JF.LOAD again to reinitialize.   ;;
;;                                                                          ;;
;;  These routines require an additional 3 words of Cart RAM to maintain    ;;
;;  their internal state.  Programs should declare a 3-word area starting   ;;
;;  for the additional state at the symbol JF.INFO.                         ;;
;;                                                                          ;;
;;  The program must also provide a 96 word working buffer named JF.BUF     ;;
;;  for saving and loading data.  The last 94 words (starting at JF.BUF+2)  ;;
;;  hold the game's data.                                                   ;;
;; ======================================================================== ;;

JF.first    EQU         $8023
JF.last     EQU         $8024
JF.addr     EQU         $8025
JF.row      EQU         $8026

;; ======================================================================== ;;
;;  JF.INIT  -- Initializes System RAM with JLP Flash subroutines.          ;;
;;                                                                          ;;
;;  Call this before calling any flash save/load routines.  Modifies no     ;;
;;  registers.                                                              ;;
;; ======================================================================== ;;

JF.INIT     PROC
            PSHR    R5
            MVII    #$248,  R5          ;   @@code:  MVO@ R0, R1
            MVO     R5,     JF.SYSRAM+0 ; 
            MVII    #$2CF,  R5          ;   @@loop:  ADD@ R1, PC
            MVO     R5,     JF.SYSRAM+1 ;
            MVII    #$252,  R5          ;   @@isr:   MVO@ R2, R2
            MVO     R5,     JF.SYSRAM+2 ;
            MVII    #$0AF,  R5          ;            JR   R5
            MVO     R5,     JF.SYSRAM+3 ;
            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  JF.CMD   -- Executes a JLP Flash command.                               ;;
;;                                                                          ;;
;;  INPUT                                                                   ;;
;;      R0  Row number to operate on                                        ;;
;;      R1  Address to copy to/from in JLP RAM                              ;;
;;      @R5 Command to invoke:                                              ;;
;;                                                                          ;;
;;            JF.read  -- Copy JLP RAM to Flash                             ;;
;;            JF.write -- Copy Flash to JLP RAM                             ;;
;;            JF.erase -- Erase flash sector (ignores address in R1)        ;;
;;                                                                          ;;
;;  OUTPUT                                                                  ;;
;;      Requested flash command executed, provided the arguments are        ;;
;;      valid.  Note that JLP does not have a way to report errors.         ;;
;;      Flash commands can take >20ms.                                      ;;
;;                                                                          ;;
;;      R5 points to return address.  R0 .. R4 unmodified.                  ;;
;;                                                                          ;;
;;      Note:  The display remains enabled during flash commands.  If the   ;;
;;      display is currently blanked, calling this routine may cause it to  ;;
;;      un-blank.  To let the display blank during a flash command, write   ;;
;;      $34 (NOP) into JF.SYSRAM+2 prior to calling.  To restore default    ;;
;;      behavior (display active), write $252 into JF.SYSRAM+2 or call      ;;
;;      JF.INIT again.                                                      ;;
;; ======================================================================== ;;
JF.CMD      PROC
            PSHR    R0
            PSHR    R1
            PSHR    R2

            DIS
            MVO     R1,     JF.addr     ; \_ Write command arguments to JLP.
            MVO     R0,     JF.row      ; /
                                        
            MVI@    R5,     R1          
            PSHR    R5                  
                                        
            MOVR    R1,     R5          
            MVI@    R5,     R1          ; Get command address.
            MVI@    R5,     R0          ; Get unlock word.
                                        
            MVII    #$100,  R5          ; \
            SDBD                        ;  |_ Save old ISR on stack.
            MVI@    R5,     R2          ;  |
            PSHR    R2                  ; /
           
            MVII    #JF.SYSRAM + 2, R2  ; \
            MVO     R2,     $100        ;  |_ Set up new ISR in RAM.
            SWAP    R2                  ;  |
            MVO     R2,     $101        ; / 
           
            MVII    #$20,   R2          ; Used by ISR to keep screen on
            JSRE    R5,     JF.SYSRAM    ; Invoke the command
           
            PULR    R2                  ; \
            MVO     R2,     $100        ;  |_ Restore old ISR from stack.
            SWAP    R2                  ;  |
            MVO     R2,     $101        ; / 

            PULR    R5                  ; Return
            PULR    R2
            PULR    R1
            PULR    R0
            JR      R5

@@write:    DECLE   $802D,  $C0DE       ; Copy JLP RAM to flash row  
@@read:     DECLE   $802E,  $DEC0       ; Copy flash row to JLP RAM  
@@erase:    DECLE   $802F,  $BEEF       ; Erase flash sector 

            ENDP

JF.write    EQU     JF.CMD.write
JF.read     EQU     JF.CMD.read
JF.erase    EQU     JF.CMD.erase

            ; These must be contiguous, in this order.
JF.brow     EQU     JF.info + 0
JF.bseq     EQU     JF.info + 1     ; two words
JF.base     EQU     JF.info + 3

;; ======================================================================== ;;
;;  JF.LOAD  -- Loads a 94-word game record from JLP Flash, if any.         ;;
;;                                                                          ;;
;;  Note:  You must call JF.INIT before calling this routine.               ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      No inputs required.                                                 ;;
;;                                                                          ;;
;;  OUTPUTS                                                                 ;;
;;      R0 - R5 trashed.                                                    ;;
;;      C = 0 if data was present and loaded.                               ;;
;;      C = 1 if no data was present.  JF.BUF is zeroed.                    ;;
;;      JF.info is initialized for subsequent calls to JF.SAVE.             ;;
;;                                                                          ;;
;; ======================================================================== ;;
JF.LOAD     PROC
            PSHR    R5
            ; Set up the base row for all flash activities.  
            ; The reference code copies this out of JF.first, to make
            ; it easier to extend later by changing the value of 
            ; FL_INFO.base.  FL_INFO.base must be a multiple of 8.
            MVI     JF.first,       R0  ; 
            MVO     R0,   JF.base       ; Save base row

            ; Initialize the best row and sequence number 
            MVII    #$FFFF,         R1
            MVII    #JF.brow,       R2
            MOVR    R2,             R4
            MVO@    R1,             R4  ; FL.brow = -1 (no best)
            COMR    R1
            MVO@    R1,             R4  ; \_ FL.bseq = 00000000
            MVO@    R1,             R4  ; / 

            ; Register allocation for @@__scan_loop:
            ;   R4:  JF.BUF, scratch
            ;   R3:  Rows remaining (32 downto 1)
            ;   R2:  JF.info
            ;   R1:  scratch
            ;   R0:  Flash sector number
            MVII    #32,            R3
            MVI     JF.base,        R0  ; get base row of our pool
@@__scan_loop:  
            MVII    #JF.BUF,        R1  ; \
            CALL    JF.CMD              ;  |- Read row R0 into FL_BUF
            DECLE   JF.read             ; /

            MVII    #JF.BUF,        R4
            MVI@    R4,             R1  ; \
            CMPI    #$FFFF,         R1  ;  |- skip row if MSW of row is FFFF
            BEQ     @@__next_row        ; /

            MOVR    R2,             R5  ; \_ R5 = &FL_INFO.bseq
            INCR    R5                  ; /

            CMP@    R5,             R1  ; Better than current best?
            BNC     @@__next_row        ; Smaller:  Nope.
            MVI@    R4,             R1  ; Load the LSW into R1
            BNEQ    @@__new_best        ; Bigger:   Yep

            CMP@    R5,             R1  ; MSW the same, so check LSW
            BNC     @@__next_row        ; Smaller:  Nope
            ; assume "equal to" can't happen.
@@__new_best:   
            MOVR    R2,             R5  ; R5 = &FL.brow
            MVI     JF.BUF + 0,     R4
            MVO@    R0,             R5  ; JF.brow = this row
            MVO@    R4,             R5  ; JF.bseq[0]  (MSW)
            MVO@    R1,             R5  ; JF.bseq[1]  (LSW)
@@__next_row:   
            INCR    R0                  ; \
            DECR    R3                  ;  |- Check up to 32 flash rows
            BNEQ    @@__scan_loop       ; /

            MVI@    R2,             R0  ; \   (FL_INFO.brow)
            TSTR    R0                  ;  |- Did we find any saved 
            BMI     @@__no_data         ; /   data in flash?

            MVII    #JF.BUF,        R1  ; \
            CALL    JF.CMD              ;  |- Read 'best' row into JF.BUF
            DECLE   JF.read             ; /   

            ; Program's data now available at JF.BUF + 2.
@@__leave:  CLRC                        ; C = 0: Data was loaded.
            PULR    PC                  ; Return to the caller.

            ; No saved data found.  Initialize buffer to default value.
@@__no_data:    
            MVI     JF.base,        R0  ; \   Set "best row" to end of this
            ADDI    #31,            R0  ;  |- flash pool so that the next
            MVO@    R0,             R2  ; /   write goes to first row.

            ; NOTE:  The following loop merely zeros the buffer. 
            ; Put different code here if your program requires it.
            MVII    #JF.BUF,        R4
            MVII    #96,            R1
            CLRR    R0
@@__zero:   MVO@    R0,             R4
            DECR    R1
            BNEQ    @@__zero

            SETC                        ; C = 1: No data loaded. Zeroed buf.
            PULR    PC
            ENDP

;; ======================================================================== ;;
;;  JF.SAVE  -- Saves a 94-word game record to JLP Flash.                   ;;
;;                                                                          ;;
;;  Note:  You must call JF.LOAD at least once before calling JF.SAVE.      ;;
;;                                                                          ;;
;;  INPUTS                                                                  ;;
;;      JF.BUF+2 through JF.BUF+95 contains the data to store.              ;;
;;                                                                          ;;
;;  OUTPUTS                                                                 ;;
;;      R0 - R5 trashed.                                                    ;;
;;      JF.info is updated for subsequent calls to JF.SAVE.                 ;;
;; ======================================================================== ;;
FL_SAVE     PROC
            PSHR    R5

            ; Increment to next row in pool, modulo 32
            MVI     JF.brow,    R0      ; Get absolute row number
            SUB     JF.base,    R0      ; Subtract off the base row
            INCR    R0                  ; \_ Next row, modulo 32
            ANDI    #31,        R0      ; /
            ADD     JF.base,    R0      ; Add back the base row
            MVO     R0,   JF.brow       ; Store updated row

            ; If we moved into the first row of a sector, erase the sector
            MOVR    R0,         R1
            ANDI    #7,         R1
            BNEQ    @@__no_erase

            CALL    JF.CMD
            DECLE   JF.erase
@@__no_erase:
            ; Increment sequence number for this record
            MVI     JF.bseq+0,  R2      ; MSW if sequence number
            MVI     JF.bseq+1,  R1      ; LSW if sequence number

            ADDI    #1,         R1      ; Increment the sequence number
            ADCR    R2

            MVO     R2, JF.bseq+0
            MVO     R1, JF.bseq+1

            ; Insert sequence number in FL_BUF
            MVO     R2, JF.BUF + 0
            MVO     R1, JF.BUF + 1

            ; Now copy this into the row # that's in R0
            MVII    #JF.BUF,    R1
            CALL    JF.CMD
            DECLE   JF.write

@@__leave:  PULR    PC
            ENDP
