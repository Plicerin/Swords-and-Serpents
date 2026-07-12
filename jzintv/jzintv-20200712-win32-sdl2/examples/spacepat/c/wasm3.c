/* ======================================================================== */
/*  World assembler for Lunar MP.                                           */
/*  This is my THIRD(!) attempt at a world encoding.                        */
/*                                                                          */
/*  Syntax:                                                                 */
/*      [loc] LABEL 'label_name'  -- Align to word and emit asm label.      */
/*      loc CUE num         -- Cue creeps with cue 'num'   1 unit           */
/*      loc CUE 'label'     -- Cue creeps with cue 'label' 1 unit           */
/*      loc ROCK1           -- Small rock                  2 units          */
/*      loc ROCK2           -- Medium rock                 2 units          */
/*      loc ROCK3           -- Large rock                  3 units          */
/*      loc CRAT1           -- Small crater                2 units          */
/*      loc CRAT2           -- Large crater                3 units          */
/*      loc FILLTO          -- Fill up to but not including 'loc'           */
/*      loc LEVEL 'char'    -- Cue a level marker          1 unit           */
/*      loc CAUTION num     -- Cue a caution light         1 unit           */
/*      loc EXIT num        -- Tell some creeps to exit    1 unit           */
/*      loc EXIT 'label'    -- Tell some creeps to exit    1 unit           */
/*                                                                          */
/*                                                                          */
/*  Numbers are all in decimal.  See design notes below for details.        */
/*  Blank lines are ignored.  Anything after a # mark is ignored.           */
/*  Whitespace is compressed, and everything outside quotes is case-        */
/*  insensitive.  (Note, whitespace isn't really allowed in quotes,         */
/*  though I don't really check for it.)                                    */
/*                                                                          */
/*  Although the objects allow specifying a location, the assembler         */
/*  requires you to state the objects in monotonically increasing order.    */
/*  All objects (including cues) have an implicit width that must be        */
/*  taken into account when specifying object location.  No two objects     */
/*  may be co-located.  This includes cues which have a minimum width       */
/*  of 1 (to stagger the processing burden).                                */
/* ======================================================================== */

/* ======================================================================== */ 
/*  WORLD DATA encoding format -- design ramblings.                         */
/*                                                                          */
/*  The world data format is really quite simple:                           */
/*                                                                          */
/*      Bits 0..7    Encoded object/cue number.                             */
/*      Bits 8..14   Delay until next word is processed.                    */
/*      Bit  15      Object or cue?  0 == object, 1 == cue.                 */
/*                                                                          */
/*  For objects, the lower 8 bits are an index into the tables RCS1/RCS2.   */
/*  For cues, the lower 8 bits are an index into the SPAWNS table.  (The    */
/*  details of the SPAWNS table TBD.)                                       */
/*                                                                          */
/*  This format is a much simpler format than previous attempts.  Why?      */
/*  I noticed that the compression ratio achieved by the more clever        */
/*  encodings was pretty lackluster (about 20% for attempt #2), and the     */
/*  work required to decode it was non-trivial.  At the very least, there   */
/*  was too much state to carry around.  With this scheme, the only state   */
/*  required is a pointer to the current word, and a down-counter.  :-)     */
/* ======================================================================== */ 


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>


#define Q(x) #x
#define X(x) x

#define MAX_LEVEL (4096)
#define FL_NOP (0)
#define FL_OBJ (1)
#define FL_CUE (2)

#define CMD_BLANK (7)

typedef struct 
{
    char          *label;
    char          *cuelbl;
    unsigned char  flag;
    unsigned short count;
    int            object;
} level_t;

FILE *f_out;


int cur_pos   = 0;
int last_pos  = 0;
level_t level[MAX_LEVEL];


/* ======================================================================== */ 
/*  MOVE_TO -- Add blanks to the run of blanks.  This doesn't actually      */
/*               emit any blanks until something non-blank is emitted.      */
/* ======================================================================== */ 
void move_to(int new_loc)
{
    if (new_loc < 0 || new_loc >= MAX_LEVEL)
    {
        fprintf(stderr, "ERROR:  Location %d must be in the range 0 to %d\n",
                new_loc, MAX_LEVEL);
        exit(1);
    }
    cur_pos = new_loc;
    if (cur_pos > last_pos)
        last_pos = cur_pos;
}

/* ======================================================================== */ 
/*  CMD_LABEL -- Record a location as needing a label.                      */
/* ======================================================================== */ 
void cmd_label(char *label)
{
    char *lbl_copy;

    if (level[cur_pos].label != NULL)
    {
        fprintf(stderr, "ERROR:  Attempt to add '%s' as label to '%d',\n" 
                        "        which already has label '%s'\n",
                        label, cur_pos, level[cur_pos].label);
        exit(1);
    }

    lbl_copy = strdup(label);
    if (!lbl_copy)
    {
        fprintf(stderr, "ERROR:  Out of memory in strdup.  Buy some more.\n");
        exit(1);
    }
    level[cur_pos].label = lbl_copy;
}


/* ======================================================================== */ 
/*  CMD_CUE  -- Cue some creeps.                                            */
/* ======================================================================== */ 
void cmd_cue(int cue)
{
    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add CUE to occupied location %d!\n",
                cur_pos);
        exit(1);
    }

    level[cur_pos].cuelbl = NULL;
    level[cur_pos].object = cue;
    level[cur_pos].flag   = FL_CUE;
    level[cur_pos].count  = 1;

    move_to(cur_pos + 1);
}

/* ======================================================================== */ 
/*  CMD_CUELBL -- cue, via label (preferred)                                */
/* ======================================================================== */ 
void cmd_cuelbl(char *cue)
{
    char *lbl_copy;

    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add CUE to occupied location %d!\n",
                cur_pos);
        exit(1);
    }

    lbl_copy = strdup(cue);
    if (!lbl_copy)
    {
        fprintf(stderr, "ERROR:  Out of memory in strdup.  Buy some more.\n");
        exit(1);
    }

    level[cur_pos].cuelbl = lbl_copy;
    level[cur_pos].object = 0;
    level[cur_pos].flag   = FL_CUE;
    level[cur_pos].count  = 1;

    move_to(cur_pos + 1);
}

/* ======================================================================== */ 
/*  CMD_EXIT -- Cue some creeps to leave                                    */
/* ======================================================================== */ 
void cmd_exit(int cue)
{
    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add EXIT to occupied location %d!\n",
                cur_pos);
        exit(1);
    }

    level[cur_pos].cuelbl = NULL;
    level[cur_pos].object = cue + 256;
    level[cur_pos].flag   = FL_CUE;
    level[cur_pos].count  = 1;

    move_to(cur_pos + 1);
}

/* ======================================================================== */ 
/*  CMD_EXITLBL -- exit, via label (preferred)                              */
/* ======================================================================== */ 
void cmd_exitlbl(char *cue)
{
    char *lbl_copy;

    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add EXIT to occupied location %d!\n",
                cur_pos);
        exit(1);
    }

    lbl_copy = strdup(cue);
    if (!lbl_copy)
    {
        fprintf(stderr, "ERROR:  Out of memory in strdup.  Buy some more.\n");
        exit(1);
    }

    level[cur_pos].cuelbl = lbl_copy;
    level[cur_pos].object = 256;
    level[cur_pos].flag   = FL_CUE;
    level[cur_pos].count  = 1;

    move_to(cur_pos + 1);
}

char *cmd_name[9] =
{
    "ROCK1",
    "ROCK2",
    "ROCK3",
    "CRAT1",
    "CRAT2",
    "CRAT3",
    "CRAT4",
    "BLANK",
    "CUE",
};

char *cmd_lbl[15] =
{
    "@@rock1",
    "@@rock2",
    "@@rock3",
    "@@crat1",
    "@@crat2",
    "@@crat3",
    "@@crat4",
    "@@blank",
    "@@cue",
    "@@level",
    "@@caut0",
    "@@caut1",
    "@@caut2",
    "@@caut3",
    "@@exit", 
};

int cmd_width[14] = { 2, 2, 3, 2, 3, 5, 5, 1, 1, 1, 1, 1, 1 };

/* ======================================================================== */ 
/*  CMD_OBJECT -- Put an object into the level                              */
/* ======================================================================== */ 
void cmd_object(int n)
{
    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add %s to occupied location %d!\n",
                cmd_name[n], cur_pos);
        exit(1);
    }

    level[cur_pos].object = n;
    level[cur_pos].flag   = FL_OBJ;

    move_to(cur_pos + cmd_width[n]);
}

/* ======================================================================== */ 
/*  CMD_LEVEL  -- Put an end-of-level marker cue into the level data        */
/* ======================================================================== */ 
void cmd_level(int n)
{
    if (level[cur_pos].flag != FL_NOP)
    {
        fprintf(stderr, "ERROR:  Trying to add LEVEL to occupied location %d!\n",
                cur_pos);
        exit(1);
    }

    if      (n >= 'A' && n <= 'Z') n = n - 'A';
    else if (n >= 'a' && n <= 'z') n = n - 'a' + 0x20;

    level[cur_pos].object = n + 32;
    level[cur_pos].flag   = FL_OBJ;

    move_to(cur_pos + 1);
}

/* ======================================================================== */ 
/*  CANONICALIZE -- Canonicalizes an input line.                            */
/* ======================================================================== */ 
int canonicalize(char *buf)
{
    char *s1, *s2;
    int in_quote = 0;

    /* Kill any comments or newlines. */
    if ((s1 = strchr(buf, '#' )) != NULL) *s1 = 0;
    if ((s1 = strchr(buf, '\r')) != NULL) *s1 = 0;
    if ((s1 = strchr(buf, '\n')) != NULL) *s1 = 0;

    /* Kill leading whitespace. */
    s1 = s2 = buf;

    while (*s1 && isspace(*s1)) s1++;

    if (!*s1) { buf[0] = 0; return 0; }

    /* Compress remaining whitespace */
    while (*s1)
    {
        while (!isspace(*s1))
            *s2++ = *s1++;

        *s2++ = ' ';  /* compressed whitespace */

        if (!*s1)
            break;

        while (isspace(*s1))
            s1++;
    }

    *s2 = 0;

    if (s2 == buf)
        return 0;
    

    /* Re-scan, uppercasing anything lowercase */
    s1 = buf;
    while (*s1)
    {
        if (*s1 == '\'')
            in_quote ^= 1;

        if (!in_quote && isalpha(*s1))
            *s1 = toupper(*s1);

        s1++;
    }

    return s1 - buf;
}

#define MAX_WORD (64)

char word1[MAX_WORD];
char word2[MAX_WORD];
char label[MAX_WORD];
int  num1, num2;

/* ======================================================================== */ 
/*  PARSE -- Pull a line apart into words.                                  */
/* ======================================================================== */ 
int parse(char *buf)
{
    char *s1, *s2;
    int len, lbl, word;

    word1[0] = word2[0] = label[0] = 0;
    num1 = num2 = -1;
    word = 0;
    lbl  = 0;

    if (!canonicalize(buf))
        return 0;

    s1 = buf;

    while (*s1)
    {
        if (*s1 == ' ')
        {
            s1++;
            continue;
        }
        if (isalpha(*s1))
        {
            if (word == 2)
            {
                printf("PARSE ERROR: too many words at %s\n", s1);
                return -1; /* too many words */
            }
            s2 = word == 0 ? word1 : word2;
            word++;

            for (len = 0; len < MAX_WORD-1 && *s1 && isalnum(*s1); len++)
                *s2++ = *s1++;
            *s2++ = 0;

            if (*s1) s1++;
            continue;
        }

        if (*s1 == '\'')
        {
            if (lbl == 1)
            {
                printf("PARSE ERROR: too many labels at %s\n", s1);
                return -1; /* too many labels */
            }

            lbl = 1;

            s1++;
            s2 = label;
            for (len = 0; len < MAX_WORD-1 && *s1 && *s1 != '\''; len++)
                *s2++ = *s1++;
            *s2++ = 0;

            if (*s1 != '\'')
            {
                printf("PARSE ERROR: bad label syntax\n");
                return -1; /* bad label syntax */
            }
            s1++;
            continue;
        }

        if (isdigit(*s1))
        {
            if      (num1 < 0) num1 = atoi(s1);
            else if (num2 < 0) num2 = atoi(s1);
            else 
            {
                printf("PARSE ERROR: too many numbers at %s\n", s1);
                return -1; /* too many numbers */
            }

            while (*s1 && isdigit(*s1))
                s1++;
            continue;
        }

        printf("PARSE ERROR:  unexpected character '%c'\n", *s1);
        return -1;
    }

    return 1;
}


char * keyword[] =
{
    "ROCK1",   /*  0 */
    "ROCK2",   /*  1 */
    "ROCK3",   /*  2 */
    "CRAT1",   /*  3 */
    "CRAT2",   /*  4 */
    "FILLTO",  /*  5 */
    "CUE",     /*  6 */
    "LABEL",   /*  7 */
    "LEVEL",   /*  8 */
    "CAUTION", /*  9 */
    "EXIT",    /* 10 */
    "CRAT3",   /* 11 */
    "CRAT4",   /* 12 */
};



#define NUM_KEYWORD (sizeof(keyword) / sizeof(char *))

/* ======================================================================== */ 
/*  HANDLE_LINE -- Parse the line, and if it's not empty, execute it.       */
/* ======================================================================== */ 
void handle_line(char *buf)
{
    int i, cmd;

    i = parse(buf);

    if (i < 0)
    {
        printf("PARSE ERROR: \"%s\"\n", buf);
        exit(1);
    }

    if (!i)
        return;

    cmd = -1;
    for (i = 0; i < NUM_KEYWORD; i++)
        if (!strcmp(keyword[i], word1))
        {
            cmd = i;
            break;
        }

    if (num1 >= 0)
        move_to(num1);

    /* Check for location argument / required first argument */
    switch (cmd)
    {
        case 0: case 1: case 2: case 3: case 4:  /* ROCKn, CRATn */
        case 5:  /* FILLTO  */
        case 11: case 12:
        {
            if (num1 < 0)
            {
                fprintf(stderr, "ERROR: Location required for %s.", 
                        keyword[cmd]);
                exit(1);
            }

            break;
        }
        case 6:   /* CUE     */
        case 10:  /* EXIT    */
        {
            if (num1 < 0)
            {
                fprintf(stderr, "ERROR: Location required for %s.", 
                        keyword[cmd]);
                exit(1);
            }
            if ((num2 < 0) == (label[0] == 0))
            {
                fprintf(stderr, "ERROR: %s requires number or label, "
                        "but not both\n", keyword[cmd]);
                exit(1);
            }
            break;
        }
        case 9:  /* CAUTION */
        {
            if (num1 < 0)
            {
                fprintf(stderr, "ERROR: Location required for %s.", 
                        keyword[cmd]);
                exit(1);
            }
            if (num2 < 0 || num2 > 3)
            {
                fprintf(stderr, "ERROR: Caution requires number from 0 to 2\n");
                exit(1);
            }
            break;
        }

        case 7: /* LABEL */
        case 8: /* LEVEL */
        {
            if (label[0] == 0)
            {
                printf("No label with LABEL/LEVEL directive\n");
                exit(1);
            }

            if (cmd == 8 && 
                (label[1] != 0 ||
                 !((label[0] >= 'A' && label[0] <= 'Z') ||
                   (label[0] >= 'a' && label[0] <= 'z'))
                 )
                )
            {
                printf("Label must be single alpha char for LEVEL directive\n");
                exit(1);
            }


            break;
        }

        default:
            break;
    }


    /* Actually process the command. */
    switch (cmd)
    {
        case 0: case 1: case 2: case 3: case 4:  /* ROCKn, CRATn */
        {
            cmd_object(cmd);
            break;
        }
        case 11: case 12:  /* CRAT3/4 */
        {
            cmd_object(cmd - 6);
            break;
        }

        case 9:
        {
            cmd_object(num2 + 10);
            break;
        }

        case 5: /* FILLTO */
        {
            break;
        }

        case 6: /* CUE */
        {
            if (label[0] != 0)
            {
                cmd_cuelbl(label);
                break;
            }

            if (num2 < 0 || num2 > 127)
            {
                printf("Numeric argument %d out of range for CUE\n", num1);
                exit(1);
            }

            cmd_cue(num2);
            break;
        }


        case 10: /* EXIT */
        {
            if (label[0] != 0)
            {
                cmd_exitlbl(label);
                break;
            }

            if (num2 < 0 || num2 > 31)
            {
                printf("Numeric argument %d out of range for EXIT\n", num1);
                exit(1);
            }

            cmd_exit(num2);
            break;
        }


        case 7: /* LABEL */
        {
            cmd_label(label);
            break;
        }

        case 8:
        {
            cmd_level(label[0]);
            break;
        }

        default:
        {
            printf("Unknown command '%s'\nInput: '%s'\n", word1, buf);
            exit(1);
            break;
        }
    }
}

/* ======================================================================== */ 
/*  GENERATE_LEVEL                                                          */
/* ======================================================================== */ 
void generate_level(void)
{
    int i, j, run;
    int cmd = CMD_BLANK, cue = 0;  /* BLANK */
    int tot_words = 0;
    int tot_cmds  = 0;
    int tot_objs  = 0;
    int tot_count = 0;
    char *lbl = level[0].label;
    char *cuelbl = level[0].cuelbl;

    if (level[0].flag == FL_NOP)
    {
        cmd = CMD_BLANK;
        cue = 0;
    } else if (level[0].flag == FL_OBJ)
    {
        cmd = level[0].object;
    } else
    {
        cmd = 1000;
        cue = level[0].object;
        cuelbl = level[0].cuelbl;
    }

    run = 1;

    /* -------------------------------------------------------------------- */
    /*  Pass 1:  Trace through level[] and run-length encode.               */
    /* -------------------------------------------------------------------- */
    for (i = 1, j = 0; i <= last_pos; i++)
    {
        if (i != (last_pos) && 
            level[i].flag  == FL_NOP &&
            level[i].label == NULL)
        {
            run++;
            continue;
        }

        if (cmd != 1000)
        {
            level[j].flag   = FL_OBJ;
            level[j].object = cmd;
            level[j].count  = run;
            level[j].label  = lbl;
            tot_objs++;
        } else
        {
            level[j].flag   = FL_CUE;
            level[j].object = cue;
            level[j].cuelbl = cuelbl;
            level[j].count  = run;
            level[j].label  = lbl;
            tot_cmds++;
        }

        run = 1;
        j++;
        lbl = level[i].label;
        if (level[i].flag == FL_OBJ)
        {
            cmd = level[i].object;
        } else if (level[i].flag == FL_CUE)
        {
            cmd    = 1000;
            cue    = level[i].object;
            cuelbl = level[i].cuelbl;
        } else
        {
            cmd = CMD_BLANK;
        }

    }

    if (cmd != 1000)
    {
        level[j].flag   = FL_OBJ;
        level[j].object = cmd;
        level[j].count  = run;
        level[j].label  = lbl;
        tot_objs++;
    } else
    {
        level[j].flag   = FL_CUE;
        level[j].cuelbl = cuelbl;
        level[j].object = cue;
        level[j].count  = run;
        level[j].label  = lbl;
        tot_cmds++;
    }

    tot_words = ++j;


    fprintf(f_out, 
            ";; ====================================="
            "=================================== ;;\n"
            "    IF (DEFINED @@rock1) = 0\n"
            "@@rock1 EQU     ((RCS1.rock1 - RCS1 + 1) SHL 8)\n"
            "@@rock2 EQU     ((RCS1.rock2 - RCS1 + 1) SHL 8)\n"
            "@@rock3 EQU     ((RCS1.rock3 - RCS1 + 1) SHL 8)\n"
            "@@crat1 EQU     ((RCS1.crat1 - RCS1 + 1) SHL 8)\n"
            "@@crat2 EQU     ((RCS1.crat2 - RCS1 + 1) SHL 8)\n"
            "@@crat3 EQU     ((RCS1.crat3 - RCS1 + 1) SHL 8)\n"
            "@@crat4 EQU     ((RCS1.crat4 - RCS1 + 1) SHL 8)\n"
            "@@blank EQU     ((RCS1.blank - RCS1 + 1) SHL 8)\n"
            "@@caut0 EQU     $1C00\n"
            "@@caut1 EQU     $1D00\n"
            "@@caut2 EQU     $1E00\n"
            "@@caut3 EQU     $1F00\n"
            "@@level EQU     $2000\n"
            "@@exit  EQU     $6000\n"
            "@@cue   EQU     $8000\n"
            "    ENDI\n"
            ";; ====================================="
            "=================================== ;;\n");

    /* -------------------------------------------------------------------- */
    /*  Pass 2:  Emit the run-length encoded data.                          */
    /* -------------------------------------------------------------------- */
    for (i = 0; i < tot_words; i++)
    {
        if (level[i].label)
            fprintf(f_out, "%s:\n", level[i].label);

        if (level[i].flag == FL_CUE && level[i].object < 256)
        {
            if (level[i].cuelbl == NULL)
            {
                fprintf(f_out, "    DECLE   %-8s + (%3d - 1) + (%3d SHL 8)     "
                        "; $%.4X %4d  CUE %d\n",
                        cmd_lbl[8], level[i].count, level[i].object,
                        i, tot_count, level[i].object);
            } else if (level[i].cuelbl != NULL)
            {
                fprintf(f_out, "    DECLE   %-8s + (%3d - 1) + CUE.%-12s"
                        "; $%.4X %4d  CUE '%s'\n",
                        cmd_lbl[8], level[i].count, level[i].cuelbl,
                        i, tot_count, level[i].cuelbl);
            }
        } else if (level[i].flag == FL_CUE && level[i].object >= 256)
        {
            if (level[i].cuelbl == NULL)
            {
                fprintf(f_out, "    DECLE   %-8s + (%3d - 1) + (%3d SHL 8)     "
                        "; $%.4X %4d  EXIT %d\n",
                        cmd_lbl[14], level[i].count, level[i].object - 256,
                        i, tot_count, level[i].object - 256);
            } else if (level[i].cuelbl != NULL)
            {
                fprintf(f_out, "    DECLE   %-8s + (%3d - 1) + EXIT.%-11s"
                        "; $%.4X %4d  EXIT '%s'\n",
                        cmd_lbl[14], level[i].count, level[i].cuelbl,
                        i, tot_count, level[i].cuelbl);
            }
        }
        if (level[i].flag == FL_OBJ && level[i].object < 10)
        {
            fprintf(f_out, "    DECLE   %-8s + (%3d - 1)                   "
                    "; $%.4X %4d  %s\n",
                    cmd_lbl[level[i].object], level[i].count, 
                    i, tot_count, cmd_name[level[i].object]);
        }
        if (level[i].flag == FL_OBJ && 
            level[i].object < 32 &&
            level[i].object >= 10)
             
        {
            fprintf(f_out, "    DECLE   %-8s + (%3d - 1)                   "
                    "; $%.4X %4d  CAUTION %d\n",
                    cmd_lbl[level[i].object], level[i].count, 
                    i, tot_count, level[i].object - 10);
        }
        if (level[i].flag == FL_OBJ && level[i].object >= 32)
        {
            fprintf(f_out, "    DECLE   %-8s + (%3d - 1) + (%3d SHL 8)     "
                    "; $%.4X %4d  LEVEL '%c'\n",
                    cmd_lbl[9], level[i].count, level[i].object - 32,
                    i, tot_count, 
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz"[level[i].object - 32]);
        }

        if (level[i].flag == FL_NOP)
        {
            fprintf(stderr, "ERROR: FL_NOP in pass 2?\n");
            exit(1);
        }

        tot_count += level[i].count;
    }

    fprintf(f_out, "                                                   "
                   ";       %4d  END\n", tot_count);
        
    /* -------------------------------------------------------------------- */
    /*  Print summary information.                                          */
    /* -------------------------------------------------------------------- */
#if 0
    printf( ";; ====================================="
            "=================================== ;;\n"
            ";;  SUMMARY\n"
            ";;      TOTAL COMMANDS       %8d\n"
            ";;      TOTAL OBJECTS        %8d\n"
            ";;      TOTAL WORDS          %8d\n"
            ";; ====================================="
            "=================================== ;;\n",
            tot_cmds, tot_objs, tot_words);
#endif
    fprintf(f_out, 
            "\n\n"
            ";; ====================================="
            "=================================== ;;\n"
            ";;  SUMMARY\n"
            ";;      TOTAL COMMANDS       %8d\n"
            ";;      TOTAL OBJECTS        %8d\n"
            ";;      TOTAL WORDS          %8d\n"
            ";; ====================================="
            "=================================== ;;\n",
            tot_cmds, tot_objs, tot_words);
}

/* ======================================================================== */ 
/*  MAIN -- where it all happens                                            */
/*                                                                          */
/*  Usage:  wasm outfile infile [infile [infile [...]]]                     */
/* ======================================================================== */ 
int main(int argc, char *argv[])
{
    FILE *f_in;
    int i;
    char buf[1024];

    if (argc < 3)
    {
        printf("Usage: wasm outfile infile [infile [infile [...]]]\n");
        exit(1);
    }


    for (i = 2; i < argc; i++)
    {
        printf("Processing '%s'\n", argv[i]);
        f_in = fopen(argv[i], "r");
        if (!f_in)
        {
            printf("could not open '%s' for reading\n", argv[i]);
            exit(1);
        }

        while (fgets(buf, 1024, f_in) != NULL)
        {
            handle_line(buf);
        }

        fclose(f_in);
    }




    f_out = fopen(argv[1], "w");
    if (!f_out)
    {
        printf("could not open '%s' for writing\n", argv[1]);
        exit(1);
    }


    generate_level();

    fclose(f_out);
    

    return 0;
}

