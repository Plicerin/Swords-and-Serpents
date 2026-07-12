#include "config.h"
#include "crc16.h"
#include "icartrom.h"

icartrom_t icart;

uint_8 buf[65536 + 52];
char lbuf[1024];

int main()
{
    FILE *f;
    int err;
    int ckaddr = -1, sum, addr;

    if ((err = icartrom_readfile("bin/sdk1600_spacepat.rom", &icart)) < 0)
    {
        fprintf(stderr, "Error %d decoding bin/sdk1600_spacepat.rom\n", err);
        exit(1);
    }

    if ((f = fopen("bin/spacepat.sym", "r")) == NULL)
    {
        perror("fopen()");
        fprintf(stderr, "Could not open bin/spacepat.sym for reading\n");
    }

    while (fgets(lbuf, 1023, f))
    {
        if (!strncmp(lbuf + 9, "CKSUM", 5))
        {
            if (ckaddr != -1)
            {
                fprintf(stderr, 
                        "Two instances of CKSUM in bin/spacepat.sym!\n");
                exit(1);
            }
            sscanf(lbuf, "%x", &ckaddr);
        }
    }

    fclose(f);

    if (ckaddr == -1)
    {
        fprintf(stderr, "Could not find CKSUM in bin/spacepat.sym!\n");
        exit(1);
    }

    icart.image[ckaddr] = 0;

    sum = 0;
    for (addr = 0x5000; addr < 0x7000; addr += 2)
    {
        sum += icart.image[addr + 0];
        sum -= icart.image[addr + 1];
    }
    for (addr = 0xD000; addr < 0xE000; addr += 2)
    {
        sum += icart.image[addr + 0];
        sum -= icart.image[addr + 1];
    }
    for (addr = 0xF000; addr < 0x10000; addr += 2)
    {
        sum += icart.image[addr + 0];
        sum -= icart.image[addr + 1];
    }

    icart.image[ckaddr] = ckaddr & 1 ? sum : -sum;

    if ((err = icartrom_writefile("bin/sdk1600_spacepat.rom",
                                  &icart, CC3_STD)) < 0)
    {
        fprintf(stderr, "Error %d while writing bin/sdk1600_spacepat.rom", err);
        exit(1);
    }

    return 0;
}
