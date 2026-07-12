/* process the rocks and the craters. */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

unsigned rock1[8];
unsigned rock2[8];
unsigned rock3[8];
unsigned crat1[8];
unsigned crat2[8];

/* Cards 0 - 1  are rock1
 * Cards 2 - 3  are rock2
 * Cards 4 - 6  are rock3
 * Cards 7 - 8  are crat1
 * Cards 9 - 11 are crat2
 */

void read_bmp(char *n, unsigned *bmp, unsigned pad0, unsigned pad1, int width)
{
    FILE *f;
    char buf[1024], *s;
    int r = 0, i, b;
    unsigned pad = pad0;

    f = fopen(n, "r");
    if (!f) { fprintf(stderr, "Couldn't open '%s'\n", n); exit(1); }

    while (fgets(buf, 1024, f) != NULL)
    {
        s = buf;
        b = pad;
        for (i = 0; i < width; i++)
        {
            if (*s == '\n') break;
            b = (b << 1) | (*s++ == '#');
        }

        b = (b << 8) | (pad & 0xFF);
        
        bmp[r++] = b;
        if (r == 8) break;
        pad = pad1;
    }
    fclose(f);
}            

void write_bmp(unsigned *bmp, int offset, int width)
{
    int r, c, cc, w, b;
    unsigned x;
    char buf[9];

    for (c = width; c > 0; c -= 8)
        for (r = 0; r < 8; r++)
        {
            x = bmp[r] << offset;
            b = (x >> c) & 0xFF;
            w = ((w >> 8) & 0xFF) | ((b << 8) & 0xFF00);
            for (cc = 0; cc < 8; cc++)
                buf[cc] = ((b >> (7 - cc)) & 1) ? '#' : '.';

            buf[8] = 0;
            if (r & 1)
                printf("            DECLE   $%.4X   ; %s\n", w, buf);
            else
                printf(";           - - -           ; %s\n", buf);
        }
}

int main()
{
    int i;

    read_bmp("rock1", rock1,    0,  0, 8);
    read_bmp("rock2", rock2,    0,  0, 8);
    read_bmp("rock3", rock3,    0,  0, 16);
    read_bmp("crat1", crat1, 0x3E, ~0, 8);
    read_bmp("crat2", crat2, 0x3E, ~0, 16);


    printf("\n");
    printf("ROCKCRAT    PROC\n");
    printf("\n");
    for (i = 0; i < 8; i++)
    {
        printf(";---------- Offset %d\n", i);
        printf("            ; Cards 0 -  1:  Rock 1\n");
        write_bmp(rock1,  i, 16);
        printf("            ; Cards 2 -  3:  Rock 2\n");
        write_bmp(rock2,  i, 16);
        printf("            ; Cards 4 -  6:  Rock 3\n");
        write_bmp(rock3,  i, 24);
        printf("            ; Cards 7 -  8:  Crat 1\n");
        write_bmp(crat1,  i, 16);
        printf("            ; Cards 9 - 11:  Crat 2\n");
        write_bmp(crat2,  i, 24);
    }
    printf("\n");
    printf("            ENDP\n");

    return 0;
}
