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

;;==========================================================================;;
;;  NOTE:  IF YOU NEED ANY OF HEX4, HEX8, HEX12, HEX4M, HEX8M or HEX12M,    ;;
;;  DO NOT USE THIS FILE.  USE "hexdisp.asm" INSTEAD.  THIS FILE AND THAT   ;;
;;  ONE CANNOT BE USED TOGETHER.                                            ;;
;;==========================================================================;;

;; ======================================================================== ;;
;;  HEX16                                                                   ;;
;;      Display a 4-digit hex number on the screen                          ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;      R0 -- Hex number                                                    ;;
;;      R1 -- Color mask / screen format word                               ;;
;;      R4 -- Screen offset                                                 ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- rotated left by 3                                             ;;
;;      R1 -- unmodified                                                    ;;
;;      R2 -- trashed                                                       ;;
;;      R3 -- zeroed                                                        ;;
;;      R4 -- points just to right of string                                ;;
;; ======================================================================== ;;
HEX16           PROC
        ; Rotate R0 left by 3, so that our digit will be in the correct
        ; position within the screen format word.
        MOVR    R0,     R3
        SLLC    R3,     2
        RLC     R0,     2       ; First, rotate by two bits...
        SLLC    R3,     1
        RLC     R0,     1       ; ... and then by one more.

        MVII    #4,     R3      ; Iterate through four digits.
@@loop:
        ; Rotate R0 left by 4, so that we can cycle through each digit
        ; one at a time.
        MOVR    R0,     R2
        SLLC    R2,     2
        RLC     R0,     2       ; First, rotate by two bits...
        SLLC    R2,     2
        RLC     R0,     2       ; ... and then by two more.

        ; Mask out a single hex digit
        MOVR    R0,     R2
        ANDI    #$78,   R2

        ; Is it A..F?  If so, add an offset so that the correct ASCII
        ; value is selected.  Otherwise do nothing special.
        CMPI    #$50,   R2      ; $50 is $A shifted left by 3.
        BLT     @@digit
        ADDI    #$38,   R2      ; If the digit >= A, add 6 << 3.
@@digit:
        ADDI    #$80,   R2      ; Generate proper GROM index.
        XORR    R1,     R2      ; Merge in the screen format word
        MVO@    R2,     R4      ; Display the digit to the screen.

        DECR    R3              ; Iterate three more times.
        BNE     @@loop

        JR      R5              ; Done!  Return.
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
