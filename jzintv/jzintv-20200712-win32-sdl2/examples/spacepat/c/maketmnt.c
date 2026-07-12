#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned mntn[16];

int main()
{
    char buf[128];
    int r, c, cc;
    int i;
    unsigned bits, byte, word;

    r = 0;
    while (fgets(buf, 128, stdin))
    {
        for (c = 0; c < 32; c++)
            if (buf[c] == '#')
                mntn[r] |= 1 << c;
        r++;
        if (r == 16) break;
    }

    
    printf("TOPMOUNT    PROC\n");

    for (i = 0; i < 8; i++)
    {
        printf("            ; alignment #%d\n", i);
        for (c = 0; c < 32; c += 8)
        {
            printf("            ; columns %2d .. %2d\n", c, c+7);
            for (r = 0; r < 16; r++)
            {
                bits = ((mntn[r] << i) | (i ? (mntn[r] >> (32 - i)) : 0)) >> c;
                for (cc = byte = 0; cc < 8; cc++)
                {
                    byte = (byte << 1) | (1 & (bits >> (7 - cc)));
                    buf[cc] = ".#"[byte & 1];
		}
		buf[8] = 0;
                
                word = (0xFF & (word >> 8)) | (byte << 8);
                if (r & 1)
                    printf("            DECLE   $%.4X   ; %s\n", word, buf);
		else
                    printf(";           - - -           ; %s\n",       buf);
            }
        }
    }
    printf("            ENDP\n");

    return 0;
}
