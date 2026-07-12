/* ======================================================================== */
/*  Decodes a .ROM file and then dumps out information about it.            */
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
/*                 Copyright (c) 1998-2001, Joseph Zbiciak                  */
/* ======================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "icartrom.h"

/* ======================================================================== */
/*  These are errors that can be reported by the Intellicart routines.      */
/* ======================================================================== */
char *errors[] =
{
    "No Error",
    "Bad Arguments",
    "Bad ROM Header",
    "CRC-16 Error in ROM Segments",
    "Bad ROM Segment Address Range",
    "Bad ROM Fine-Address Range",   
    "CRC-16 Error in Enable Tables",
    "Unknown Error"
};

icartrom_t the_icart;

uint_8  *rom_img;

/* ======================================================================== */
/*  SHOW_RANGES                                                             */
/*  Shows a list of ranges of addresses represented by a bit-vector.        */
/* ======================================================================== */
void show_ranges(uint_32 *bv)
{
    int lo, hi, i;

    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of set bits.                  */
    /* -------------------------------------------------------------------- */
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && (1 & (bv[idx] >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                printf("    $%.4X - $%.4X (%d pages)\n",
                        lo << 8, (hi << 8) + 0xFF, (hi - lo + 1));
            }
            hi = lo = -1;
        }
    }
}

/* ======================================================================== */
/*  WRITE_MAPPINGS                                                          */
/*  Writes the [mappings] section of a .CFG file, based on the icartrom.    */
/* ======================================================================== */
int write_mappings(FILE *fr, FILE *fc, icartrom_t *icart, int ofs)
{
    int lo, hi, i, j;

    /* -------------------------------------------------------------------- */
    /*  Make sure at least one page is both 'preload' and 'readable'.       */
    /*  If there are none, then don't output a [mapping] section.           */
    /* -------------------------------------------------------------------- */
    for (i = 0; i < 8; i++)
        if (icart->preload[i] & icart->readable[i])
            break;
    if (i == 8)
        return 0;

    fprintf(fc, "[mapping]\r\n");

    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of pages that are both        */
    /*  readable and preloaded.                                             */
    /* -------------------------------------------------------------------- */
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && 
            (1 & ((icart->preload [idx] & 
                   icart->readable[idx]) >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                lo <<= 8;
                hi = (hi << 8) + 0x100;
                fprintf(fc, "$%.4X - $%.4X = $%.4X\r\n", 
                        ofs, ofs + hi - lo - 1, lo);
                for (j = lo; j < hi; j++)
                {
                    fputc(icart->image[j] >> 8,   fr);
                    fputc(icart->image[j] & 0xFF, fr);
                }
                ofs += hi - lo;
            }
            hi = lo = -1;
        }
    }

    return ofs;
}

/* ======================================================================== */
/*  WRITE_PRELOADS                                                          */
/*  Writes the [preload] section of a .CFG, which addresses ranges of       */
/*  address that are preloaded, but not readable.                           */
/* ======================================================================== */
int write_preloads(FILE *fr, FILE *fc, icartrom_t *icart, int ofs)
{
    int lo, hi, i, j;

    /* -------------------------------------------------------------------- */
    /*  Make sure at least one page is both 'preload' and 'not readable'.   */
    /*  If there are none, then don't output a [preload] section.           */
    /* -------------------------------------------------------------------- */
    for (i = 0; i < 8; i++)
        if (icart->preload[i] & ~icart->readable[i])
            break;
    if (i == 8)
        return 0;

    fprintf(fc, "[preload]\r\n");

    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of pages that are both        */
    /*  preloaded and not-readable.                                         */
    /* -------------------------------------------------------------------- */
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && 
            (1 & (( icart->preload [idx] & 
                   ~icart->readable[idx]) >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                lo <<= 8;
                hi = (hi << 8) + 0x100;
                fprintf(fc, "$%.4X - $%.4X = $%.4X\r\n", 
                        ofs, ofs + hi - lo - 1, lo);
                for (j = lo; j < hi; j++)
                {
                    fputc(icart->image[j] >> 8,   fr);
                    fputc(icart->image[j] & 0xFF, fr);
                }
                ofs += hi - lo;
            }
            hi = lo = -1;
        }
    }
    return ofs;
}

/* ======================================================================== */
/*  WRITE_BANKSW                                                            */
/*  Writes the [bankswitch] section.  These are sections marked for         */
/*  Intellicart-style bankswitching.                                        */
/* ======================================================================== */
void write_banksw(FILE *fc, icartrom_t *icart)
{
    int lo, hi, i;

    /* -------------------------------------------------------------------- */
    /*  Make sure at least one page is 'bankswitched'.                      */
    /*  If there are none, then don't output a [preload] section.           */
    /* -------------------------------------------------------------------- */
    for (i = 0; i < 8; i++)
        if (icart->dobanksw[i])
            break;
    if (i == 8)
        return;

    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of pages that are banksw.     */
    /* -------------------------------------------------------------------- */
    fprintf(fc, "[bankswitch]\r\n");
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && (1 & (icart->dobanksw[idx] >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                fprintf(fc, "$%.4X - $%.4X\r\n",
                        lo << 8, (hi << 8) + 0xFF);
            }
            hi = lo = -1;
        }
    }
}

/* ======================================================================== */
/*  WRITE_BANKSW                                                            */
/*  Writes the [memattr] section.  These are sections marked as RAM.        */
/* ======================================================================== */
void write_memattr(FILE *fc, icartrom_t *icart)
{
    int lo, hi, i;

    /* -------------------------------------------------------------------- */
    /*  Make sure at least one page is 'writable.'                          */
    /*  If there are none, then don't output a [preload] section.           */
    /* -------------------------------------------------------------------- */
    for (i = 0; i < 8; i++)
        if (icart->writable[i])
            break;
    if (i == 8)
        return;

    fprintf(fc, "[memattr]\r\n");
    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of pages that are writable    */
    /*  but not narrow.  These are RAM 16 spans.                            */
    /* -------------------------------------------------------------------- */
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && 
            (1 & (( icart->writable [idx] & 
                   ~icart->narrow   [idx]) >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                fprintf(fc, "$%.4X - $%.4X = RAM 16\r\n",
                        lo << 8, (hi << 8) + 0xFF);
            }
            hi = lo = -1;
        }
    }
    /* -------------------------------------------------------------------- */
    /*  Iterate over all 256 256-decle pages, with a little slop at both    */
    /*  ends of the spectrum.  Look for spans of pages that are writable    */
    /*  and also narrow.  These are RAM 8 spans.                            */
    /* -------------------------------------------------------------------- */
    for (i = 0, lo = hi = -1; i <= 256; i++)
    {
        int idx, shf;

        idx = i >> 5;
        shf = i & 31;
        if (i < 256 && 
            (1 & (( icart->writable [idx] & 
                    icart->narrow   [idx]) >> shf)))
        {
            hi = i;
            if (lo == -1) { lo = i; }
        } else
        {
            if (lo != -1)
            {
                fprintf(fc, "$%.4X - $%.4X = RAM 8\r\n",
                        lo << 8, (hi << 8) + 0xFF);
            }
            hi = lo = -1;
        }
    }
}

/* ======================================================================== */
/*  MAIN                                                                    */
/*  This is the main program.  The action happens here.                     */
/* ======================================================================== */
int main(int argc, char *argv[])
{
    int show_rom = 1, len, decoded;
    FILE *f;

    if (argc < 2 || argc > 3)
    {
usage:
        fprintf(stderr, "usage: rom2bin [-] foo.rom\n");
        exit(1);
    }

    if (argv[1][0] == '0')
    {
        show_rom = 1;
        argc--;
        argv++;
        if (argc < 2) goto usage;
    }

    f = fopen(argv[1], "rb");
    
    if (!f)
    {
        perror("fopen()");
        fprintf(stderr, "Couldn't open '%s' for reading\n", argv[1]);
        exit(1);
    }

    fseek(f, 0, SEEK_END);
    if ((len = ftell(f)) < 0)
    {
        fprintf(stderr, "Error seeking\n");
        exit(1);
    }
    rewind(f);

    if ((rom_img = malloc(len)) == NULL)
    {
        fprintf(stderr, "Out of memory\n");
        exit(1);
    }

    fread(rom_img, 1, len, f);
    fclose(f);

    icartrom_init(&the_icart);
    decoded = icartrom_decode(&the_icart, rom_img, 0);
    free(rom_img);

    if (decoded < 0)
    {
        if (decoded < -6) decoded = -7;

        fprintf(stderr, "Decoding error: %s\n", errors[-decoded]);
        exit(1);
    }

    printf("Decoded %d of %d bytes\n", decoded, len);

    printf("Preloaded memory ranges:\n");
    show_ranges(the_icart.preload);

    printf("Readable memory ranges:\n");
    show_ranges(the_icart.readable);

    printf("Writeable memory ranges:\n");
    show_ranges(the_icart.writable);

    printf("Narrow (8-bit wide) memory ranges:\n");
    show_ranges(the_icart.narrow);

    printf("Bank-switched memory ranges:\n");
    show_ranges(the_icart.dobanksw);

    if (show_rom)
    {   
        FILE *fr, *fc;
        char rom_name[1024], cfg_name[1024];
        char *s;
        int ofs = 0;

        strncpy(rom_name, argv[1], 1020);
        rom_name[1020] = 0;
        s = strstr(rom_name, ".rom");
        if (!s) s = rom_name + strlen(rom_name);

        strcpy(s, ".cfg");
        strcpy(cfg_name, rom_name);
        strcpy(s, ".bin");

        printf("Config file: %s\nROM file:    %s\n", cfg_name, rom_name);
        fc = fopen(cfg_name, "wb");
        fr = fopen(rom_name, "wb");
        if (!fc || !fr) 
        {
            fprintf(stderr, "Can't open output files.\n");
            exit(1);
        }


        ofs = write_mappings(fr, fc, &the_icart, ofs);
        ofs = write_preloads(fr, fc, &the_icart, ofs);

        write_memattr(fc, &the_icart);
        write_banksw (fc, &the_icart);

        fclose(fr);
        fclose(fc);
    }


    return 0;
}

/* ======================================================================== */
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
/* ======================================================================== */
/*                 Copyright (c) 1998-2001, Joseph Zbiciak                  */
/* ======================================================================== */
