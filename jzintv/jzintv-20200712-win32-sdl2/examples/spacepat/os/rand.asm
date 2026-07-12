;; ======================================================================== ;;
;;  RAND                                                                    ;;
;;      Returns random bits in R0.                                          ;;
;;                                                                          ;;
;;  INPUTS:                                                                 ;;
;;      R5 -- Return address                                                ;;
;;      Random state in RSEED                                               ;;
;;                                                                          ;;
;;  OUTPUTS:                                                                ;;
;;      R0 -- 16 random bits.                                               ;;
;;                                                                          ;;
;;  NOTES:                                                                  ;;
;;      You are encouraged to add additional "randomness" by adding or      ;;
;;      XORing other values into RSEED.                                     ;;
;;                                                                          ;;
;;      Implementation is a Galois realization of a 16-bit LFSR with the    ;;
;;      following polynomial:                                               ;;
;;                                                                          ;;
;;          x^16 = x^15 + x^13 + x^11 + x^9 + x^8 + x^4 + x^3 + x^0         ;;
;;                                                                          ;;
;;      The random number generator is only advanced by 4 bits per call.    ;;
;;      Call twice if you need 16 truly random bits.  The generator uses    ;;
;;      a dense polynomial, so the top 12 bits will be different than the   ;;
;;      bottom 12 bits returned on the previous call.                       ;;
;;                                                                          ;;
;;      RAND also mixes in IDLE, so if its value has changed an arbitrary   ;;
;;      amount since the last call, that too can improve randomness.        ;;
;; ======================================================================== ;;
RAND        PROC
            MVI     RSEED,      R0      ;  10   Get rand seed
            XORR    R5,         R0      ;   8   XOR in caller ret address
            MVII    #$AB19,     R1      ;   8   Field polynomial
                                        ;----
                                        ;  26

            REPEAT  4
            SLLC    R0,         1       ;   6   Multiply by x^1
            ADCR    PC                  ;   7   \_ If x^16 generated, XOR in
            XORR    R1,         R0      ;   6   /  polynomial (-ve logic)
                                        ;----
                                        ;  19
            ENDR
                                        ;  76  (4 unrolled iterations)
                                        ;  26  (carried forward)
                                        ;----
                                        ; 102
        
            MVO     R0,     RSEED       ;  11
            JR      R5                  ;   7
                                        ;----
                                        ;  18
                                        ; 102
                                        ;----
                                        ; 130
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
