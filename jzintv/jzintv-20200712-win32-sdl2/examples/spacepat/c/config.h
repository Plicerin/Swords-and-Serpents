/*
 * ============================================================================
 *  Title:    Project-Wide Config
 *  Author:   J. Zbiciak
 *  $Id: config.h,v 1.14 2001/11/02 02:00:02 im14u2c Exp $
 * ============================================================================
 *  _BIG_ENDIAN         -- Host machine is big endian
 *  _LITTLE_ENDIAN      -- Host machine is little endian
 * ============================================================================
 *
 * ============================================================================
 */

#ifndef _CONFIG_H
#define _CONFIG_H


/*
 * ============================================================================
 *  If you get an error here, define BYTE_BE or BYTE_LE as is required for 
 *  your host machine!  You can do that in your Makefile by adding it to
 *  CFLAGS, or by uncommenting the appropriate #define below.
 * ============================================================================
 */

/* #define BYTE_BE */  /* Uncomment for big endian    */
/* #define BYTE_LE */  /* Uncomment for little endian */

#if !defined(BYTE_BE) && !defined(BYTE_LE)

#  if defined(__BIG_ENDIAN__)
#    define BYTE_BE
#  endif

#  if defined(__LITTLE_ENDIAN__)
#    define BYTE_LE
#  endif

#  if !(defined(BYTE_BE) || defined(BYTE_LE)) && \
       (defined(sparc)   || defined(__sparc)    || defined(__sparc__)   || \
        defined(sparc64) || defined(__sparc64)  || defined(__sparc64__) || \
        defined(ppc)     || defined(__ppc)      || defined(__ppc__)     || \
        defined(ppc64)   || defined(__ppc64)    || defined(__ppc64__)   || \
        defined(POWERPC) || defined(__POWERPC)  || defined(__POWERPC__))
#    define BYTE_BE    
#  endif

#  if !(defined(BYTE_BE) || defined(BYTE_LE)) && \
       (defined(i386)    || defined(__i386)     || defined(__i386__)    || \
        defined(x86_64)  || defined(__x86_64)   || defined(__x86_64__)  || \
        defined(amd64)   || defined(__amd64)    || defined(__amd64__)   || \
        defined(ia64)    || defined(__ia64)     || defined(__ia64__)    || \
        defined(alpha)   || defined(__alpha)    || defined(__alpha__)) 
#    define BYTE_LE
#  endif

#  if !defined(BYTE_BE) && !defined(BYTE_LE)
#    include <endian.h>
#    ifndef __BYTE_ORDER
#      error Please manually set your machine endian in 'config.h'
#    endif
#    if __BYTE_ORDER==4321
#      define BYTE_BE
#    endif
#    if __BYTE_ORDER==1234
#      define BYTE_LE
#    endif
#    if !defined(BYTE_BE) && !defined(BYTE_LE)
#      error Cannot determine target endian.  See 'config.h' for details.
#    endif
#  endif

#endif

#if defined(BYTE_BE) && defined(BYTE_LE)
#  error Both BYTE_BE and BYTE_LE defined.  Pick only 1!
#endif

#if !defined(BYTE_BE) && !defined(BYTE_LE)
#  error One of BYTE_BE or BYTE_LE must be defined.
#endif

/* --------------------------------------------------------------------- */
/*  BFE         -- Builds a `B'it`F'ield structure in the correct order  */
/*                 as required for the host machine's `E'ndian.          */
/* --------------------------------------------------------------------- */

#ifdef BYTE_BE
#  define BFE(x,y) y; x
#else /* BYTE_LE */
#  define BFE(x,y) x; y
#endif


/*
 * ============================================================================
 *  If we're using GCC/EGCS, suppress some silly compiler warnings.
 * ============================================================================
 */

#ifdef __GNUC__
# define UNUSED __attribute__ ((unused))
# define GNU_RESTRICT
#else
# define UNUSED
#endif

/*
 * ============================================================================
 *  If our compiler supports 'inline', enable it here.
 * ============================================================================
 */
#if defined(GNUC) || defined(_TMS320C6X)
# define INLINE inline
#else
# define INLINE
#endif

/*
 * ============================================================================
 *  Target-specific types, according to size.
 * ============================================================================
 */
#ifdef _TMS320C6X
typedef unsigned char       uint_8;
typedef unsigned short      uint_16;
typedef unsigned int        uint_32;
typedef unsigned long       uint_64;    /* Note:  Really only 40 bits.  */

typedef signed   char       sint_8;
typedef signed   short      sint_16;
typedef signed   int        sint_32;
typedef signed   long       sint_64;    /* Note:  Really only 40 bits.  */
#else
typedef unsigned char       uint_8;
typedef unsigned short      uint_16;
typedef unsigned int        uint_32;
typedef unsigned long long  uint_64;

typedef signed   char       sint_8;
typedef signed   short      sint_16;
typedef signed   int        sint_32;
typedef signed   long long  sint_64;
#endif

typedef volatile uint_8     v_uint_8;
typedef volatile uint_16    v_uint_16;
typedef volatile uint_32    v_uint_32;
typedef volatile uint_64    v_uint_64;

typedef volatile sint_8     v_sint_8;
typedef volatile sint_16    v_sint_16;
typedef volatile sint_32    v_sint_32;
typedef volatile sint_64    v_sint_64;


/*
 * ============================================================================
 *  Target-specific library compatibility issues
 * ============================================================================
 */

#if defined (__APPLE__) && defined(__MACH__) && !defined(macosx)
# define macosx
#endif

#ifdef linux
# define USE_STRCASECMP
# define DEFAULT_ROM_PATH ".:=../rom:/usr/local/share/jzintv/rom"
# define HAS_LINK
#endif

#ifdef SOLARIS
/*# define NO_SNPRINTF*/
# define NO_GETOPT_LONG
# define NO_INOUT
# define USE_STRCASECMP
# define DEFAULT_ROM_PATH ".:=../rom:/usr/local/share/jzintv/rom"
# define HAS_LINK
#endif

#ifdef WIN32
# define NO_GETTIMEOFDAY
/*# define NO_SNPRINTF*/
# define NO_GETOPT_LONG
# define NOGETOPT
# define NO_SETUID
# define NO_NANOSLEEP
# define NO_RAND48
# define NO_FCNTL
# define USE_MKTEMP
# define NEED_INOUT
# define DEFAULT_ROM_PATH ".;=..\\rom"
# define PATH_SEP '\\'
# define PATH_COMPONENT_SEP ";"
#endif

#ifdef macintosh
# define NO_GETTIMEOFDAY
# define NO_STRDUP
# define NO_SYS_TIME_H
# define NO_SDL_DELAY
# define NO_SETUID
# define NO_NANOSLEEP
# define NO_RAND48
# define NO_INOUT
# define NO_STRICMP /* ? */
# define NO_FCNTL
# define DEFAULT_ROM_PATH "."
# define PATH_SEP ':'
# define PATH_COMPONENT_SEP ";"
#endif

#ifdef macosx
# define NO_RAND48
# define NO_INOUT
# define NO_GETOPT_LONG
# define NOGETOPT
# define USE_STRCASECMP /* ? */
# define DEFAULT_ROM_PATH ".:=../rom"
# define HAS_LINK
#endif

#ifdef __FreeBSD__
# define NO_INOUT
# define USE_STRCASECMP
# define DEFAULT_ROM_PATH ".:=../rom:/usr/local/share/jzintv/rom"
# define HAS_LINK
#endif

#ifdef _TMS320C6X
# define NO_GETTIMEOFDAY
# define NO_STRDUP
# define NO_SYS_TIME_H
# define NO_UNISTD_H
# define NO_GETOPT_LONG
# define NO_SETUID
# define NO_NANOSLEEP
# define NO_RAND48
# define NO_INOUT
# define NO_STRICMP
# define HAVE_RESTRICT
# define NO_FCNTL
# ifndef CLK_TCK
#  define CLK_TCK 200000000 /* Assume 200MHz C6201 device */
# endif
# define DEFAULT_ROM_PATH "."
# define FULLSC_START_DLY   (0)
#endif

#ifdef GP2X
# define FULLSC_START_DLY   (0)
#endif


/*
 * ============================================================================
 *  Clean up per-arch configs w/ some defaults.
 * ============================================================================
 */

#ifndef PATH_SEP
# define PATH_SEP '/'
#endif

#ifndef PATH_COMPONENT_SEP 
# define PATH_COMPONENT_SEP ":"
#endif

#ifndef DEFAULT_ROM_PATH
# define DEFAULT_ROM_PATH NULL
#endif

#ifndef FULLSC_START_DLY
# define FULLSC_START_DLY (500)
#endif

/*
 * ============================================================================
 *  CGC support configuration
 * ============================================================================
 */

#if defined(WIN32)
#define CGC_SUPPORTED
#define CGC_DLL
#endif

#if defined(linux)
#define CGC_SUPPORTED
#define CGC_THREAD
#endif

/*
 * ============================================================================
 *  Standard #includes that almost everyone needs
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <assert.h>
#include <limits.h>
#include <errno.h>
#include <math.h>

#ifndef NO_SYS_TIME_H
# include <sys/time.h>
#endif

#ifndef NO_UNISTD_H
# include <unistd.h>
#endif

#ifdef _TMS320C6X           /* This seems to be TI-specific.    */
# include <file.h>
#endif

#ifdef linux
# include <sys/io.h>
#endif


#ifdef USE_STRCASECMP
# define stricmp strcasecmp
#endif

#ifndef NO_FCNTL
# include <fcntl.h>
#endif

#ifndef M_PI
# ifdef PI
#  define M_PI PI
# else
#  define M_PI (3.14159265358979323846)
# endif
#endif


/*
 * ============================================================================
 *  If this compiler implements the C99 'restrict' keyword, then enable it.
 * ============================================================================
 */
#ifdef HAVE_RESTRICT
# define RESTRICT restrict
#endif

#ifdef GNU_RESTRICT
# define RESTRICT __restrict__
#endif

#ifndef RESTRICT
# define RESTRICT
#endif

/*
 * ============================================================================
 *  Allow exposing "local" symbols by using LOCAL instead of static
 * ============================================================================
 */
#ifndef LOCAL
# define LOCAL static
#endif

/*
 * ============================================================================
 *  Include the "platform library" to handle missing functions
 * ============================================================================
 */



/*
 * ============================================================================
 *  Version number
 * ============================================================================
 */

#ifndef JZINTV_VERSION_MAJOR
# define JZINTV_VERSION_MAJOR (0)
#endif

#ifndef JZINTV_VERSION_MINOR
# define JZINTV_VERSION_MINOR (0)
#endif

#define JZINTV_VERSION ((JZINTV_VERSION_MAJOR << 8) | JZINTV_VERSION_MINOR)

#endif /* CONFIG_H */

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
/*                 Copyright (c) 1998-2006, Joseph Zbiciak                  */
/* ======================================================================== */
