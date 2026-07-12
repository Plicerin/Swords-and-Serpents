;;==========================================================================;;
;;  Useful Routines                                                         ;;
;;  Copyright 1999-2002, Joe Zbiciak.                                       ;;
;;                                                                          ;;
;;  This file contains a number of useful routines that you're welcome      ;;
;;  to use in your own software.  Please keep in mind that these routines   ;;
;;  are licensed under the GNU General Public License, and so if you plan   ;;
;;  to distribute a program which incorporates these routines, it too must  ;;
;;  be distributed under the GNU General Public License.                    ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  P16.xxx       Prints a string packed by S16                             ;;
;;                                                                          ;;
;;  P16.R         Ptr to string in R0, format in R1, location in R4.        ;;
;;  P16.S         String follows CALL.  Format in R1, location in R4.       ;;
;;  P16.LS        Location and string itself follows CALL.  Format in R1.   ;;
;;  P16.FLS       Format, location, and string itself follows CALL          ;;
;;  P16.P         Ptr to string follows CALL.  Format in R1, loc. in R4.    ;;
;;  P16.LP        Location and ptr to string follows CALL.  Format in R1.   ;;
;;  P16.FLP       Format, location, and ptr to string follows CALL          ;;
;;                                                                          ;;
;;  P16 alone is an alias for P16.FLS.                                      ;;
;;                                                                          ;;
;;  INPUTS for P16.R:                                                       ;;
;;      R0 -- Pointer to ASCIIZ string                                      ;;
;;      R1 -- Screen format word                                            ;;
;;      R4 -- Pointer to display location                                   ;;
;;      R5 -- Return address                                                ;;
;;                                                                          ;;
;;  INPUTS for P16.S:                                                       ;;
;;      R1 -- Screen format word                                            ;;
;;      R4 -- Pointer to display location                                   ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              String                      n DECLEs (NUL terminated)       ;;
;;                                                                          ;;
;;  INPUTS for P16.LS:                                                      ;;
;;      R1 -- Screen format word                                            ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              Ptr to display location     1 DECLE                         ;;
;;              String                      n DECLEs (NUL terminated)       ;;
;;                                                                          ;;
;;  INPUTS for P16.FLS:                                                     ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              Screen format word          1 DECLE                         ;;
;;              Ptr to display location     1 DECLE                         ;;
;;              String                      n DECLEs (NUL terminated)       ;;
;;                                                                          ;;
;;  INPUTS for P16.P:                                                       ;;
;;      R1 -- Screen format word                                            ;;
;;      R4 -- Pointer to display location                                   ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              Pointer to ASCIIZ string    1 DECLE                         ;;
;;                                                                          ;;
;;  INPUTS for P16.LP:                                                      ;;
;;      R1 -- Screen format word                                            ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              Ptr to display location     1 DECLE                         ;;
;;              Pointer to ASCIIZ string    1 DECLE                         ;;
;;                                                                          ;;
;;  INPUTS for P16.FLP:                                                     ;;
;;      R5 -- Invocation record, followed by return code.                   ;;
;;              Screen format word          1 DECLE                         ;;
;;              Location                    1 DECLE                         ;;
;;              Pointer to ASCIIZ string    1 DECLE                         ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- Trashed                                                       ;;
;;      R1 -- Same as screen format word, EXCEPT Bit 15 is cleared.         ;;
;;      R4 -- Points to display location just after displayed string.       ;;
;;      R5 -- Points just past end of source string in memory.              ;;
;;      R2 and R3 are not modified.                                         ;;
;;                                                                          ;;
;;  NOTES                                                                   ;;
;;      ASCIIZ strings are ASCII strings that are terminated with a         ;;
;;      single NUL character.  Although it was originally intended for use  ;;
;;      with ASCII strings, this routine does allow for characters outside  ;;
;;      the normal range of ASCII characters as well.  This can be useful   ;;
;;      for displaying graphic characters within a string.                  ;;
;;                                                                          ;;
;;      The card # displayed for a given character in the string is given   ;;
;;      by the following formula:                                           ;;
;;                                                                          ;;
;;          (character_number - 32) + (format_word SHR 3) = card_number.    ;;
;;                                                                          ;;
;;      To display a single character from GRAM, for instance, just         ;;
;;      insert a word whose value is "GRAM_picture_number + 288" in your    ;;
;;      string.                                                             ;;
;;                                                                          ;;
;;      You can use PRINT to display entire strings of characters in        ;;
;;      alternate fonts (such as a font loaded in GRAM) as well.  To do     ;;
;;      this, merely add the appropriate offset to the format_word.         ;;
;;      The correct offset depends on what characters are in your font      ;;
;;      and where your font begins in GRAM.                                 ;;
;;                                                                          ;;
;;      For example, suppose your font only contains uppercase alphabetic   ;;
;;      characters, and is loaded in GRAM positions 10 through 35.  That    ;;
;;      is, the picture for 'A' is in GRAM position #10, and 'Z' is in      ;;
;;      GRAM position #35.  We want 'A' to map to GRAM position #10.        ;;
;;      GRAM position #10 is equivalent to card #266.  The ASCII value for  ;;
;;      'A' is 65.  Using the relationship given above, we have:            ;;
;;                                                                          ;;
;;          (character_number - 32) + (format_word SHR 3) = card_number.    ;;
;;          (        65       - 32) + (format_word SHR 3) = 266             ;;
;;                                                                          ;;
;;      Solving this, we get:                                               ;;
;;                                                                          ;;
;;          format_word SHR 3 = 233                                         ;;
;;          format_word       = 233 SHL 3                                   ;;
;;                                                                          ;;
;;      So, to display this particular GRAM font, we must add 233 SHL 3     ;;
;;      to our format word.  (We can still set other bits in the format     ;;
;;      word to control its color, etc.)                                    ;;
;; ======================================================================== ;;
P16     PROC
@@FLS:  MVI@    R5,     R1      ; Load format word from invoc. record
@@LS:   MVI@    R5,     R4      ; Load ptr to display loc from invoc record
        B       @@S             ; Continue w/ string pointer in R5.

@@FLP:  MVI@    R5,     R1      ; Load ptr to string from invoc. record
@@LP:   MVI@    R5,     R4      ; Load format word from invoc. record
@@P:    MVI@    R5,     R0      ; Load ptr to display loc from invoc record

@@R:    PSHR    R5              ; Save return address if string ptr is in R0
        MOVR    R0,     R5      ; Use auto-incr pointer for reading string
        SETC                    ; Flag:  C==1 means ret addr is on stack
        INCR    PC              ; Skip the CLRC.

@@S     CLRC                    ; Flag:  C==0 means return after string.

        PSHR    R2
        MVI@    R5,     R2      ; \
        ANDI    #$7F8,  R2      ;  |_ Get string length from first word
        SLR     R2,     2       ;  |
        SLR     R2,     1       ; /

        SLL     R1,     1       ; \__ Hide the flag in MSB of screen fmt word
        RRC     R1,     1       ; /

@@loop  
        DECR    R5              ; \
        MVI@    R5,     R0      ; Get character to display
        SWAP    R0              ; \_ unpack hi-half character
        ANDI    #$7F8,  R0      ; /

        CMPI    #$600,  R0
        BNC     @@a
        ADDI    #$200,  R0
@@a
        ADDR    R1,     R0      ; \_ Merge format word and write to display
        MVO@    R0,     R4      ; /
        DECR    R2              ; \_ Are we done yet?
        BMI     @@done          ; /

        MVI@    R5,     R0      ; Get character to display
        ANDI    #$7F8,  R0      ; -- unpack lo-half character

        CMPI    #$600,  R0
        BNC     @@b
        ADDI    #$200,  R0
@@b

        ADDR    R1,     R0      ; \_ Merge format word and write to display
        MVO@    R0,     R4      ; /
        DECR    R2              ; \_ Are we done yet?
        BPL     @@loop          ; /
@@done:
        PULR    R2
        SLLC    R1,     1       ; Get "return-to-stack" flag from MSB
        SLR     R1,     1       ; Restore screen fmt word, clearing MSB.
        ADCR    PC              ; Conditionally skip JR R5 if return-to-stack
        JR      R5              ; Return to R5 if flag was clear
        PULR    PC              ; Return to saved address if flag was set.
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
;*                Copyright (c) 1999-2002, Joseph Zbiciak                   *;
;* ======================================================================== *;
