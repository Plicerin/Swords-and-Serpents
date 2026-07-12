/* ======================================================================== */
/*  Saucer Control Table Compiler                                           */
/* ======================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_MMR (256)
#define MAX_VEL (256)
#define MAX_SCP (256)

/* movement range table */
typedef struct mmr_t
{
    int min;
    int max;
    int cnt;
    int vel[MAX_VEL];
    int dst[MAX_VEL];
    int tic[MAX_VEL];
} mmr_t;

/* top level of the saucer control program */
typedef struct scp_t
{
    int min_dly;
    int dly_mag;
    int dxt_num;
    int dyt_num;

} scp_t;


int max_scp = 0, cur_scp = 0;
int max_dxt = 0, cur_dxt = 0;
int max_dyt = 0, cur_dyt = 0;

scp_t scp[MAX_SCP];
mmr_t dxt[MAX_MMR], dyt[MAX_MMR];


char *file = NULL;
int line_no = 0;
char orig[1024];
char line[1024];

/* ======================================================================== */
/*  CANONICALIZE_LINE   -- Delete whitespace, strip comments, capitalize    */
/* ======================================================================== */
void canonicalize_line(void)
{
    char *s1, *s2;

    s1 = s2 = line;

    strcpy(orig, line);

    while (*s2)
    {
        if (*s2 == ';' || *s2 == '#' || *s2 == '\n' || *s2 == '\r')
            break;

        if (!isspace(*s2))
        {
            if (isalpha(*s2)) *s1++ = toupper(*s2);
            else              *s1++ = *s2;
        }

        s2++;
    }
    *s1++ = ';';
    *s1 = 0;
}

/* ======================================================================== */
/*  Syntax is simple and line-oriented.                                     */
/*                                                                          */
/*      SCP <#>      -- Sets the SCP currently being defined.               */
/*      MINDLY <#>   -- Sets minimum firing delay                           */
/*      DLYMAG <#>   -- Sets the magnitude of random component of fire dly. */
/*      SETDXT       -- binds current SCP to a given DXT                    */
/*      SETDYT       -- binds current SCP to a given DYT                    */
/*                                                                          */
/*      DXT <#>      -- Sets the DXT currently being defined                */
/*      MVX sx,ex,t  -- Adds a dxt entry based on start/end and total time  */
/*      VELX vx,t    -- Adds a dxt entry based on velocity and total time.  */
/*      RNGX x1,x2   -- Sets the bounding box                               */
/*                                                                          */
/*      DYT <#>      -- Sets the DYT currently being defined.               */
/*      MVY sy,ey,t  -- Adds a dyt entry based on start/end and total time  */
/*      VELY vy,t    -- Adds a dyt entry based on velocity and total time.  */
/*      RNGY y1,y2   -- Sets the bounding box                               */
/*                                                                          */
/* ======================================================================== */

void do_scp(int new_scp)
{
    if (new_scp < 0 || new_scp >= MAX_SCP)
    {
        fprintf(stderr, "SCP must be in range %d to %d\n%s:%d>> %s\n", 
                0, MAX_SCP-1, file, line_no, orig);
        exit(1);
    }


    cur_scp = new_scp;

    if (cur_scp > max_scp)
        max_scp = cur_scp;
}


void do_mindly(int dly)
{
    if (dly < 0 || dly >= 255)
    {
        fprintf(stderr, "MINDLY must be in range %d to %d\n%s:%d>> %s\n", 
                0, 255, file, line_no, orig);
        exit(1);
    }

    scp[cur_scp].min_dly = dly;
}

void do_dlymag(int dly)
{
    if (dly < 0 || dly >= 255)
    {
        fprintf(stderr, "DLYMAG must be in range %d to %d\n%s:%d>> %s\n", 
                0, 255, file, line_no, orig);
        exit(1);
    }

    scp[cur_scp].dly_mag = dly;
}

void do_rngx(int x1, int x2)
{
    if (x2 < x1) { int t = x2; x2 = x1; x1 = t; }

    if (x1 < 0 || x1 > 159 || x2 < 0 || x2 > 159)
    {
        fprintf(stderr, "RNGY X coord must be in range %d to %d\n%s:%d>> %s\n", 
                0, 159, file, line_no, orig);
        exit(1);
    }

    dxt[cur_dxt].min = x1 * 256;
    dxt[cur_dxt].max = x2 * 256 + 255;
}

void do_rngy(int y1, int y2)
{
    if (y2 < y1) { int t = y2; y2 = y1; y1 = t; }

    if (y1 < 0 || y1 > 63 || y2 < 0 || y2 > 63)
    {
        fprintf(stderr, "RNGY Y coord must be in range %d to %d\n%s:%d>> %s\n", 
                0, 63, file, line_no, orig);
        exit(1);
    }

    dyt[cur_dyt].min = y1 * 256;
    dyt[cur_dyt].max = y2 * 256 + 255;
}

void do_setdxt(int dxt)
{
    if (dxt < 0 || dxt >= MAX_MMR)
    {
        fprintf(stderr, "SETDXT must be in range %d to %d\n%s:%d>> %s\n",
                0, MAX_MMR - 1, file, line_no, orig);
        exit(1);
    }

    if (dxt > max_dxt) max_dxt = dxt;

    scp[cur_scp].dxt_num = dxt;
}

void do_setdyt(int dyt)
{
    if (dyt < 0 || dyt >= MAX_MMR)
    {
        fprintf(stderr, "SETDYT must be in range %d to %d\n%s:%d>> %s\n",
                0, MAX_MMR - 1, file, line_no, orig);
        exit(1);
    }

    if (dyt > max_dyt) max_dyt = dyt;

    scp[cur_scp].dyt_num = dyt;
}

void do_dxt(int dxt)
{
    if (dxt < 0 || dxt >= MAX_MMR)
    {
        fprintf(stderr, "DXT must be in range %d to %d\n%s:%d>> %s\n",
                0, MAX_MMR - 1, file, line_no, orig);
        exit(1);
    }

    cur_dxt = dxt;
}

void do_dyt(int dyt)
{
    if (dyt < 0 || dyt >= MAX_MMR)
    {
        fprintf(stderr, "DYT must be in range %d to %d\n%s:%d>> %s\n",
                0, MAX_MMR - 1, file, line_no, orig);
        exit(1);
    }

    cur_dyt = dyt;
}

void insert_mmr(mmr_t *mmr, char axis, int v, int t)
{
    int idx;

    if (v > 127 || v <= 0)
    {
        fprintf(stderr,"MV%c has out-of-range velocity %d\n%s:%d>> %s\n",
                axis, v, file, line_no, orig);
        exit(1);
    }

    if (mmr->cnt >= MAX_VEL)
    {
        fprintf(stderr,"Too many D%cT entries for SCP %d\n%s:%d>> %s\n",
                axis, cur_scp, file, line_no, orig);
        exit(1);
    }

    idx = mmr->cnt++;

    mmr->vel[idx] = v;
    mmr->dst[idx] = v * t * 8;
    mmr->tic[idx] = t;
}

int calc_vel(int d, int dt)
{
    return (d * 32) / dt;  /* round down */
}

void do_mvx(int sx, int ex, int dt)
{
    int vx, dx;

    if (sx > ex) { int t = sx; sx = ex; ex = t; }

    if (sx < 0 || sx > 159 || ex < 0 || ex > 159)
    {
        fprintf(stderr, "MVX X coord must be in range %d to %d\n%s:%d>> %s\n", 
                0, 159, file, line_no, orig);
        exit(1);
    }

    if (sx == ex)
    {
        fprintf(stderr,"MVX must have different start/end coord\n%s:%d>> %s\n",
                file, line_no, orig);
        exit(1);
    }

    if (dt < 1)
    {
        fprintf(stderr,"MVX tick count must be >= 1\n%s:%d>> %s\n",
                file, line_no, orig);
        exit(1);
    }

    dx = ex - sx;
    vx = calc_vel(dx, dt);

    insert_mmr(&(dxt[cur_dxt]), 'X', vx, dt);
}

void do_mvy(int sy, int ey, int dt)
{
    int vy, dy;

    if (sy > ey) { int t = sy; sy = ey; ey = t; }

    if (sy < 0 || sy > 63 || ey < 0 || ey > 63)
    {
        fprintf(stderr, "MVY Y coord must be in range %d to %d\n%s:%d>> %s\n", 
                0, 63, file, line_no, orig);
        exit(1);
    }

    if (sy == ey)
    {
        fprintf(stderr,"MVY must have different start/end coord\n%s:%d>> %s\n",
                file, line_no, orig);
        exit(1);
    }

    if (dt < 1)
    {
        fprintf(stderr,"MVY tick count must be >= 1\n%s:%d>> %s\n",
                file, line_no, orig);
        exit(1);
    }

    dy = ey - sy;
    vy = calc_vel(dy, dt);

    insert_mmr(&(dyt[cur_dyt]), 'Y', vy, dt);
}

void do_velx(int vx, int dt)
{
    int dx;

    dx = (dt*vx + 31) >> 5;
    
    if (dx < 0 || dx > 159)
    {
        fprintf(stderr, "VELX results in out-of-range dx: %d\n%s:%d>> %s\n",
                dx, file, line_no, orig);
        exit(1);
    }
    
    insert_mmr(&(dxt[cur_dxt]), 'X', vx, dt);
}

void do_vely(int vy, int dt)
{
    int dy;

    dy = (dt*vy + 31) >> 5;
    
    if (dy < 0 || dy > 63)
    {
        fprintf(stderr, "VELY results in out-of-range dy: %d\n%s:%d>> %s\n",
                dy, file, line_no, orig);
        exit(1);
    }

    
    insert_mmr(&(dyt[cur_dyt]), 'Y', vy, dt);
}



/* ======================================================================== */
/*  HANDLE_LINE -- parses canonicalized line and dispatches to handler.     */
/* ======================================================================== */
void handle_line(void)
{
    int w, x, y;

    if (line[0] == ';')
        return;

    if      (sscanf(line,"SCP%d;",         &w)          == 1) do_scp(w);
    else if (sscanf(line,"MINDLY%d;",      &w)          == 1) do_mindly(w);
    else if (sscanf(line,"DLYMAG%d;",      &w)          == 1) do_dlymag(w);
    else if (sscanf(line,"SETDXT%d;",      &w)          == 1) do_setdxt(w);
    else if (sscanf(line,"SETDYT%d;",      &w)          == 1) do_setdyt(w);
            
    else if (sscanf(line,"DXT%d;",         &w)          == 1) do_dxt(w);
    else if (sscanf(line,"MVX%d,%d,%d;",   &w,&x,&y)    == 3) do_mvx(w,x,y);
    else if (sscanf(line,"VELX%d,%d;",     &w,&x)       == 2) do_velx(w,x);
    else if (sscanf(line,"RNGX%d,%d;",     &w,&x)       == 2) do_rngx(w,x);
            
    else if (sscanf(line,"DYT%d;",         &w)          == 1) do_dyt(w);
    else if (sscanf(line,"MVY%d,%d,%d;",   &w,&x,&y)    == 3) do_mvy(w,x,y);
    else if (sscanf(line,"VELY%d,%d;",     &w,&x)       == 2) do_vely(w,x);
    else if (sscanf(line,"RNGY%d,%d;",     &w,&x)       == 2) do_rngy(w,x);
    else
    {
        fprintf(stderr, "Could not parse this line:\n%s:%d>> %s\n", 
                file, line_no, orig);
        exit(1);
    }
}

void handle_file(FILE *f)
{
    while (fgets(line, 1024, f))
    {
        line_no++;
        canonicalize_line();
        handle_line();
    }
}

/* ======================================================================== */
/*  GENERATE_TABLES                                                         */
/*  For each Saucer Control Program, emits an entry in top-level table      */
/*  and corresponding MMR.                                                  */
/*                                                                          */
/*  SCTBL.top   Top level table which contains:                             */
/*               -- Aggressiveness (firing parameters)                      */
/*               -- Pointer to Up/Down parameter set table                  */
/*               -- Pointer to Left/Right parameter set table               */
/*                                                                          */
/*  SCTBL.dxt   Delta-X table                                               */
/*               -- Min X in 8Q8                                            */
/*               -- Max X in 8Q8                                            */
/*               -- # of entries                                            */
/*                                                                          */
/*              and then a series of entries of the form                    */
/*                                                                          */
/*               -- Rightward velocity (biased 2Q6)                         */
/*               -- Number of 30Hz ticks                                    */
/*               -- Final delta-X for this move (8.8)                       */
/*                                                                          */
/*  SCTBL.dxy   Delta-Y table                                               */
/*              Same format of Delta-X table, only on Y axis.               */
/* ======================================================================== */
void emit_toplev(FILE *fo)
{
    int i;


    fprintf(fo, "        ;; top-level SCTBL\n");
    fprintf(fo, "@@top:\n");

    for (i = 0; i <= max_scp; i++)
    {
        fprintf(fo, "@@%.2X    DECLE   $%.4X, $%.4X, @@dxt_%.2X, @@dyt_%.2X\n",
                i,
                scp[i].dly_mag, scp[i].min_dly, 
                scp[i].dxt_num, scp[i].dyt_num);
    }

    fprintf(fo, "\n");
}


void emit_mmrtbl(FILE *fo, mmr_t *mmr, int max, char axis)
{
    int i, j;
    char l_axis = tolower(axis), u_axis = toupper(axis);

    for (i = 0; i <= max; i++)
    {
        if (mmr[i].cnt == 0)
            continue;

        fprintf(fo, "        ;; D%cT table #%d\n@@d%ct_%.2X:\n", 
                u_axis, i, l_axis, i);


        fprintf(fo, "        DECLE   $%.4X, $%.4X, %d\n",
                mmr[i].min, mmr[i].max, mmr[i].cnt);

        for (j = 0; j < mmr[i].cnt; j++)
        {
            fprintf(fo, 
                    "        DECLE   ($%.2X SHL 8) + ($%.2X), $%.4X\n",
                    mmr[i].tic[j], mmr[i].vel[j], mmr[i].dst[j]);
        }
        fprintf(fo, "\n");
    }
}

void generate_tables(FILE *fo)
{
    fprintf(fo, 
            ";; Generated by SCTC\n"
            "SCTBL   PROC\n");

    emit_toplev(fo);
    emit_mmrtbl(fo, dxt, max_dxt, 'x');
    emit_mmrtbl(fo, dyt, max_dyt, 'y');

    fprintf(fo, "        ENDP\n");
}


/* ======================================================================== */
/*  MAIN -- where the action is.                                            */
/* ======================================================================== */
int main(int argc, char *argv[])
{
    int i;
    FILE *fi;

    for (i = 1; i < argc; i++)
    {
        fi = fopen(argv[i], "r");
        if (!fi)
        {
            fprintf(stderr, "ERROR:  could not open %s for reading\n",argv[i]);
            exit(1);
        }

        file = argv[i];
        line_no = 0;

        handle_file(fi);
        fclose(fi);
    }

    generate_tables(stdout);

    return 0;
}

