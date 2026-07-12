;;==========================================================================;; 
;; Joe Zbiciak's Space Patrol for Intellivision.                            ;;
;; Copyright 2006, Joe Zbiciak, intvnut AT gmail.com.                       ;;
;; http://spatula-city.org/~im14u2c/intv/                                   ;;
;;==========================================================================;;

;;==========================================================================;;
;;  UPSPA     Updates sprite allocations within each MOB group.             ;;
;;==========================================================================;;
UPSPA   PROC

        ;;------------------------------------------------------------------;;
        ;;  Recalc GP1ACT, GP2ACT.                                          ;;
        ;;------------------------------------------------------------------;;

        MVII    #SPAT,  R4          ;   8 Point to sprite attribute table
        MVII    #3,     R3          ;   8 We reuse this 4 times.
                                    ;----
                                    ;  16

        ; totally abuse the fact bit 1 is always 0
        MVI@    R4,     R0          ;   8
        ADD@    R4,     R0          ;   8
        ADD@    R4,     R0          ;   8
        MVI@    R4,     R1          ;   8
        ADD@    R4,     R1          ;   8
        ANDR    R3,     R0          ;   6
        ANDR    R3,     R1          ;   6
        ADDR    R0,     R1          ;   6
        MVO     R1,     GP1ACT      ;  11
                                    ;----
                                    ;  69

        MVI@    R4,     R0          ;   8
        ADD@    R4,     R0          ;   8
        ADD@    R4,     R0          ;   8
        MVI@    R4,     R1          ;   8
        ADD@    R4,     R1          ;   8
        ADD@    R4,     R1          ;   8
        ANDR    R3,     R0          ;   6
        ANDR    R3,     R1          ;   6
        ADDR    R0,     R1          ;   6
        AND@    R4,     R3          ;   8
        ADDR    R3,     R1          ;   6
        MVO     R1,     GP2ACT      ;  11
                                    ;----
                                    ;  91
                                    ;  16 (carried forward)
                                    ;  69 (carried forward)
                                    ;----
                                    ; 176


        ;;------------------------------------------------------------------;;
        ;;  Allocate active objects to actual MOBs.                         ;;
        ;;                                                                  ;;
        ;;  Objects are divided into two groups.  Group 1 objects are the   ;;
        ;;  "bad guy" objects, and Group 2 objects are the bullets.  Each   ;;
        ;;  group gets 3 MOBs by default.  If one of the groups has fewer   ;;
        ;;  than 3 active sprites, then the other group may use the left-   ;;
        ;;  over MOBs.                                                      ;;
        ;;                                                                  ;;
        ;;  The reason we divide up the objects into two groups like this   ;;
        ;;  is that we typically have between 1 and 3 creeps (but as many   ;;
        ;;  as 5 in rare circumstances).  In contrast, we typically have    ;;
        ;;  around 3 to 5 bullets in the air, with up to 7 being in flight. ;;
        ;;  The creeps are more susceptible to multiplexing artifacts than  ;;
        ;;  the bullets, so we want to give them preference when muxing     ;;
        ;;  MOBs.  This arrangement ends up working out pretty well.        ;;
        ;;                                                                  ;;
        ;;  Addendum:  If the level marker is onscreen, it steals from      ;;
        ;;  Group 2.  The level marker always gets a MOB.                   ;;
        ;;------------------------------------------------------------------;;
@@spa:
        MVII    #3,     R0          ;   8 R0 is Group 1's MOB allocation
        CLRR    R3                  ;   6 Used for resetting MUX counter
        CLRR    R1                  ;   6
        CMP     LMCNT,  R1          ;  10 Is level marker active?
        BEQ     @@no_level_marker   ; 9/7
        DECR    R1                  ;   6
                                    ;----
                                    ;  43
                                    ; 176
                                    ;----
                                    ; 219

@@no_level_marker:
        ADDR    R0,     R1          ;   6 R1 is Group 2's MOB allocation
                                    ;     (2 if level marker active, 3 
                                    ;     otherwise.)

        MOVR    R0,     R2          ;   6
        SUB     GP1ACT, R2          ;  10 3 or more active in Group 1?
        BMI     @@gp1full           ; 7/9 Yes -- go straight to Group 2
        ADDR    R2,     R1          ;   6 No -- add extra to Group 2's MOBs
        MVI     GP1ACT, R0          ;  10 Clamp Group 1 to actual # of active
        MVO     R3,     GP1CNT      ;  10 Reset MUX counter.

        MVI     GP2ACT, R2          ;  10 Get # of active in Group 2
        CMPR    R2,     R1          ;   6 Fewer MOBs than active?
        BLT     @@spadone           ; 7/9 Yes -- done allocating
        MOVR    R2,     R1          ;   6 No -- Clamp to number of active
        MVO     R3,     GP2CNT      ;  10 Reset MUX counter.
        B       @@spadone           ;   9 Done allocating
                                    ;----
                                    ; 103 (only last branch taken)
                                    ;  31 (if jumping to gp1full)
        

@@gp1full:
        MOVR    R1,     R2          ;   6
        SUB     GP2ACT, R2          ;  10 More sprites than MOBs in group 2?
        BMI     @@spadone           ; 7/9 Yes -- done allocating
        ADDR    R2,     R0          ;   6 No -- add extra to Group 1's MOBs
        MVI     GP2ACT, R1          ;  10 Clamp Group 2 to actual # of active
        MVO     R3,     GP2CNT      ;  10 Reset MUX counter.

        MVI     GP1ACT, R2          ;  10 Get # of active in Group 1
        CMPR    R2,     R0          ;   6 Fewer MOBs than active?
        BLT     @@spadone           ; 7/9 Yes -- done allocating
        MOVR    R2,     R0          ;   6 No -- Clamp to number of active
        MVO     R3,     GP1CNT      ;  10 Reset MUX counter.
;       B       @@spadone           ;.... Done allocating
                                    ;----
                                    ;  88 (fall thru)
                                    ;  31 (carried forward)
                                    ;----
                                    ; 119

@@spadone:
        MVO     R0,     GP1MOB      ;  11 
        MVO     R1,     GP2MOB      ;  11
        JR      R5                  ;   7
                                    ;----
                                    ;  29
                                    ; 219 (carried forward)
                                    ; 119 (carried forward)
                                    ;  12 (call overhead)
                                    ;----
                                    ; 379

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
