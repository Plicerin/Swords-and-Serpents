/* ======================================================================== */
/*  CRC-16 routines                                     J. Zbiciak, 2001    */
/* ------------------------------------------------------------------------ */
/*  This program is free software; you can redistribute it and/or modify    */
/*  it under the terms of the GNU General Public License as published by    */
/*  the Free Software Foundation; either version 2 of the License, or       */
/*  (at your option) any later version.                                     */
/*                                                                          */
/*  This program is distributed in the hope that it will be useful,         */
/*  but WITHOUT ANY WARRANTY; without even the implied warranty of          */
/*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       */
/*  General Public License for more details.                                */
/*                                                                          */
/*  You should have received a copy of the GNU General Public License       */
/*  along with this program; if not, write to the Free Software             */
/*  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.               */
/* ------------------------------------------------------------------------ */
/*                 Copyright (c) 2001-+Inf, Joseph Zbiciak                  */
/* ======================================================================== */

#ifndef CRC_16_H_
#define CRC_16_H_ 1

/* ======================================================================== */
/*  CRC16_TBL    -- Lookup table used for the CRC-16 code.                  */
/* ======================================================================== */
extern const uint_16 crc16_tbl[256];

/* ======================================================================== */
/*  CRC16_UPDATE -- Updates a 16-bit CRC using the lookup table above.      */
/*                  Note:  The 16-bit CRC is set up as a left-shifting      */
/*                  CRC with no inversions.                                 */
/*                                                                          */
/*                  All-caps version is a macro for stuff that can use it.  */
/* ======================================================================== */
uint_16 crc16_update(uint_16 crc, uint_8 data);
#define CRC16_UPDATE(crc, d) (((crc) << 8) ^ crc16_tbl[((crc) >> 8) ^ (d)])

/* ======================================================================== */
/*  CRC16_BLOCK  -- Updates a 16-bit CRC on a block of 8-bit data.          */
/*                  Note:  The 16-bit CRC is set up as a left-shifting      */
/*                  CRC with no inversions.                                 */
/* ======================================================================== */
uint_16 crc16_block(uint_16 crc, uint_8 *data, int len);

#endif
/* ======================================================================== */
/*                 Copyright (c) 2001-+Inf, Joseph Zbiciak                  */
/* ======================================================================== */
