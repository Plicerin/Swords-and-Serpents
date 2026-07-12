#include <stdio.h>
#include <time.h>

char *mon[12] =
{
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
};

int main()
{
    struct tm *ltm;
    time_t ltime;

    time(&ltime);
    ltm = localtime(&ltime);

    printf(" S16 \"     %02d-%.3s-%04d    \"\n",
            ltm->tm_mday, mon[ltm->tm_mon], ltm->tm_year + 1900);

    return 0;
}

