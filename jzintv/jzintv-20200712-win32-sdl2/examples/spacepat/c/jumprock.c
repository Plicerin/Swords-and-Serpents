/* Figures out minimum jump height to clear the various rocks for various
 * pixel offsets.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/*
 *          BUGGY GRAPHIC:
 *
 *       0123456789ABCDEFGHIJ
 *    -8    ##   ====        8-
 *    -7    ## ==            7-
 *    -6    ##===            6-
 *    -5   ==============    5-
 *    -4 =============###### 4-
 *    -3 ===##==##==##===    3-
 *    -2   =##==##==##=      2-
 *    -1    ##  ##  ##       1-
 *     0                     0
 *       0123456789ABCDEFGHI 
 *
 */


/*
 *
 *     How do we define offsets relative to the buggy?
 *
 *     card_x0 = (buggy_x >> 3) - 1
 *     card_x1 = card_x0 + 1;
 *     card_x2 = card_x0 + 2;
 *     card_x3 = card_x0 + 3;
 *
 *     ofs0    =  8 - (buggy_x & 7) - (ground & 7);
 *     ofs1    = 16 - (buggy_x & 7) - (ground & 7);
 *     ofs2    = 24 - (buggy_x & 7) - (ground & 7);
 *     ofs3    = 32 - (buggy_x & 7) - (ground & 7);
 *
 */

       /*  n  o  y  x */
char card[12][8][8][8];

void parse_rockcrat(void)
{
    FILE *f;
    int n, o, y, x, b;
    char buf[256], *s;

    f = fopen("rockcrat.asm", "r");
    if (!f) { perror("fopen(rockcrat.asm)"); exit(1); }

    n = 0;
    o = 0;
    y = 0;
    while (fgets(buf, 256, f) != NULL)
    {
        if (NULL != (s = strstr(buf, "DECLE   $")))
        {
            sscanf(s + 9, "%x", &b);
            for(x = 0; x < 8; x++)
                card[n][o][y][x] = 1 & (b >> (7 - x));

            y++;

            for(x = 0; x < 8; x++)
                card[n][o][y][x] = 1 & (b >> (15 - x));

            y++;
        }

        if (y == 8)
        {
            y = 0;

            n++;
            if (n == 12)
            {
                n = 0;
                o++;
            }
        }

        if (o > 7) 
            break;
    }

#ifdef DEBUG_PRC
    for (n = 0; n < 7; n++)
    {
        printf("Card #%d\n", n);
        for (y = 0; y < 8; y++)
        {
            for (o = 0; o < 8; o++)
            {
                for (x = 0; x < 8; x++)
                    putchar(card[n][o][y][x] ? '#' : '.');
                putchar(' ');
            }
            putchar('\n');
        }
        putchar('\n');
    }
#endif

    fclose(f);
}

        /*n  o  y   x */
char rock[5][8][8][32];

void assemble_rocks()
{
    int x, y, n, nn, xx, o;
    int xofs[12] = { 0, 8, 0, 8, 0, 8, 16, 0, 8, 0, 8, 16 };
    int newn[12] = { 0, 0, 1, 1, 2, 2, 2,  3, 3, 4, 4, 4  };

    memset((void *)rock, 0, sizeof(rock));

    for (n = 0; n < 12; n++)
    {
        nn = newn[n];
        for (o = 0; o < 7; o++)
            for (y = 0; y < 8; y++)
                for (x = 0; x < 8; x++)
                {
                    xx = xofs[n] + x;
                    rock[nn][o][y][xx] = card[n][o][y][x];
                }
    }

#ifdef DEBUG_ARK
    for (n = 0; n < 3; n++)
    {
        printf("Rock #%d\n", n);
        for (y = 0; y < 8; y++)
        {
            for (x = 0; x < 32; x++)
                putchar(rock[n][0][y][x] ? '#' : '.');
            putchar('\n');
        }
        putchar('\n');
    }
#endif
}


/*
 * Now convolve the buggy with the rocks to figure out the minimum height
 * of the buggy relative to each of the three rocks for all 32 possible 
 * relative offsets.
 *
 * Offset analysis:
 *
 *
 *                      ##   ====          
 *                      ## ==              
 *                      ##===              
 *                     ==============      
 *                   =============######   
 *                   ===##==##==##===      
 *                     =##==##==##=        
 *                      ##  ##  ##         
 *
 *   000000000011111111112222222222233333
 *   012345678901234567890123456789012345
 *   |###############                   |###############
 *   |###############                   |###############
 *   |###############                   |###############
 *
 * Notice that there are 34 offsets (1 through 24) that cause at least 1
 * column of a 16-pixel rock to overlap with our 19-pixel buggy.  Icky.
 *
 *                      ##   ====          
 *                      ## ==              
 *                      ##===              
 *                     ==============      
 *                   =============######   
 *                   ===##==##==##===      
 *                     =##==##==##=        
 *                      ##  ##  ##         
 *
 *           0000000000111111111122222222
 *           0123456789012345678901234567
 *           |#######                   |#######
 *           |#######                   |#######
 *           |#######                   |#######
 *
 * For 8-pixel rocks, it's not so bad.  We only have 26 offsets we overlap
 * by. 
 *
 * ASIDE:  You know what, I don't really need the 8 different offset pictures 
 * to do this calculation.  :-)  I do all the calculation for offset 0, 
 * and then in the game, I'll subtract the actual offset from the buggy's
 * X position.
 */

int get_pixel(int n, int x, int y)
{
    int mx = n == 2 ? 24 : 16;

    if (x < 0 || x >= mx) return 0;
    if (y < 0 || y >= 8)  return 0;
    return rock[n][0][y][x];
}

/*           | | | |#|#| | | |=|=|=|=| | | | | | | |   
 *           | | | |#|#| |=|=| | | | | | | | | | | |   
 *           | | | |#|#|=|=|=| | | | | | | | | | | |   
 *           | | |=|=|=|=|=|=|=|=|=|=|=|=|=|=| | | |   
 *           |=|=|=|=|=|=|=|=|=|=|=|=|=|#|#|#|#|#|#|   
 *           |=|=|=|#|#|=|=|#|#|=|=|#|#|=|=|=| | | |   
 *           | | |=|#|#|=|=|#|#|=|=|#|#|=| | | | | |   
 *           | | | |#|#| | |#|#| | |#|#| | | | | | |   
 *           | | | | | | | | | | | | | | | | | | | |
 */
int bbot[32]={2,2,1,0,0,1,1,0,0,1,1,0,0,1,2,2,3,3,3,9,9,9,9,9,9,9,9,9,9,9,9,9};

int min_ht[5][35];

void convolve(void)
{
    int o, n, mx, x, y, bx, by;

    for (n = 0; n < 3; n++)
    {
        mx = n == 2 ? 16 : 8;
        for (o = 0; o < 35; o++)
        {
            for (x = 0; x < mx; x++)
            {
                bx = x - 16 + o;
                for (y = 7; y >= 0; y--)
                    if (rock[n][0][7 - y][x + 8])
                        break;


                by = bx <  0 ? 0 :
                     bx > 19 ? 0 : (y - bbot[bx] + 1);

#ifdef DEBUG_CNV
printf("Rock %d, X=%-2d, Y=%-3d, bx=%-3d, by=%-2d\n", n, x, y, bx, by);
#endif

                if (by < 0) by = 0;

                if (by > min_ht[n][o])
                    min_ht[n][o] = by;
            }
        }
    }
    for (n = 3; n < 5; n++)
    {
        mx = n == 4 ? 16 : 8;
        for (o = 0; o < 35; o++)
        {
            for (x = 0; x < mx; x++)
            {
                bx = x - 16 + o;
                for (y = 7; y >= 0; y--)
                    if (rock[n][0][7 - y][x + 8])
                        break;


                by = bx <  0 ? 0 :
                     bx > 19 ? 0 : 
                     y == 7 || bbot[bx] > 0 ? 0 : 1;

#ifdef DEBUG_CNV2
printf("Rock %d, X=%-2d, Y=%-3d, bx=%-3d, by=%-2d\n", n, x, y, bx, by);
#endif

                if (by < 0) by = 0;

                if (by > min_ht[n][o])
                    min_ht[n][o] = by;
            }
        }
    }
}

void print_table(void)
{
    int i;
    int n;

    const char *lbl[5] = 
    {
        "@@rock1",
        "@@rock2",
        "@@rock3",
        "@@crat1",
        "@@crat2",
    };
    const char *name[5] = 
    {
        "Rock #1",
        "Rock #2",
        "Rock #3",
        "Crat #1",
        "Crat #2",
    };

    printf(";; Minimum Jump Height Table\n");
    printf("MJHTBL  PROC\n");
   

    for (n = 0; n < 5; n++)
    {
        printf("        ;; %s\n", name[n]); 

        printf("        DECLE   ");
        for (i = 0; i < 8; i++)
            printf("%3d%s", 0,
                    i == 7 ? "  ; Padding\n":", ");


        if (n == 2 || n == 4)
        {
            printf("        DECLE   ");
            for (i = 0; i < 8; i++)
                printf("%3d%s", min_ht[n][i]*32, 
                        i == 7 ? "  ; -16 thru -9\n":", ");
        }

        printf("        DECLE   ");
        for (i = 8; i < 16; i++)
            printf("%3d%s", min_ht[n][i]*32, 
                    i == 15 ? "  ;  -8 thru -1\n": ", ");

        printf("%s DECLE   ", lbl[n]);
        for (i = 16; i < 24; i++)
            printf("%3d%s", min_ht[n][i]*32, 
                    i == 23 ? "  ;   0 thru  7\n": ", ");

        printf("        DECLE   ");
        for (i = 24; i < 32; i++)
            printf("%3d%s", min_ht[n][i]*32, 
                    i == 31 ? "  ;   8 thru 15\n": ", ");

        printf("        DECLE   ");
        for (i = 32; i < 36; i++)
            printf("%3d%s", min_ht[n][i]*32, 
                    i == 35 ? "                      ;  16 thru 19\n" : ", ");
    }
    printf("        DECLE   ");
    for (i = 0; i < 8; i++)
        printf("%3d%s", 0,
                i == 7 ? "  ; Padding\n":", ");
    printf("        ENDP\n");
}

main()
{
    parse_rockcrat();
    assemble_rocks();
    convolve();
    print_table();
    return 0;
}
