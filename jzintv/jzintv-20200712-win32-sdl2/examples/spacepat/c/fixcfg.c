#include <stdio.h>

FILE *fopenerr(char *file, char *mode)
{
    FILE *f;

    f = fopen(file, mode);

    if (!f)
    {
        perror("fopen()");
        fprintf(stderr, "Could not open '%s' with mode '%s'\n", file, mode);
        exit(1);
    }
    
    return f;
}

main()
{
    int crlf = 0;
    int c;
    FILE *f1, *f2, *f3;

    f1 = fopenerr("bin/lunar_mp.cfg", "rb");
    f2 = fopenerr("dbgmac.cfg", "rb");
    f3 = fopenerr("bin/new.cfg", "wb");

    crlf = 0;
    while ((c = fgetc(f1)) != EOF)
    {
        if (c == '\r' || c == '\n')
        {
            if (!crlf)
            {
                fputc('\r', f3);
                fputc('\n', f3);
                crlf = 1;
            } else if (c == '\n')
            {
                crlf = 0;
            }
        } else
        {
            fputc(c, f3);
        }
    }

    crlf = 0;
    while ((c = fgetc(f2)) != EOF)
    {
        if (c == '\r' || c == '\n')
        {
            if (!crlf)
            {
                fputc('\r', f3);
                fputc('\n', f3);
                crlf = 1;
            } else if (c == '\n')
            {
                crlf = 0;
            }
        } else
        {
            fputc(c, f3);
        }
    }

    fclose(f1);
    fclose(f2);
    fclose(f3);

    return 0;
}
