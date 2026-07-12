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

FILLZERO.lp CLRR    R0
            INCR    PC
FILLMEM.vlp MVI@    R5,     R0
FILLMEM.lp  MVI@    R5,     R1
FILLMEM.p   MVI@    R5,     R4
            B       FILLMEM

;; ======================================================================== ;;
;;  FILLZERO                                                                ;;
;;      Fills memory with zeros                                             ;;
;;                                                                          ;;
;;  FILLMEM                                                                 ;;
;;      Fills memory with a constant                                        ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;      R0 -- Fill value (FILLMEM only)                                     ;;
;;      R1 -- Number of words to fill                                       ;;
;;      R4 -- Start of fill area                                            ;;
;;      R5 -- Return address                                                ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- Zeroed if FILLZERO, otherwise untouched.                      ;;
;;      R1 -- Zeroed                                                        ;;
;;      R4 -- Points to word after fill area                                ;;
;; ======================================================================== ;;

CLRSCR      PROC
            MVII    #$0F0,  R1
            MVII    #$200,  R4
FILLZERO    CLRR    R0              ; Start out with R0 zeroed for FILLZERO
FILLMEM     MVO@    R0,     R4      ; Store R0 out at R4, and move along
            DECR    R1              ; Keep going until our count runs out
            BNEQ    FILLMEM
            JR      R5              ; Return to the caller.
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
