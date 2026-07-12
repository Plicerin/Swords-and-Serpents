WINDEX  PROC
        DECLE   MOON_B, MOON_C
        DECLE   MARS_B, MARS_C
        DECLE   PLUT_B, PLUT_C
        DECLE   MERC_B, MERC_C
        ENDP

MOON_B  PROC
;        INCLUDE  "genasm/demolvl.asm"
        INCLUDE  "genasm/beg_a_e.asm"
        INCLUDE  "genasm/beg_f_j.asm"
        INCLUDE  "genasm/beg_k_o.asm"
        INCLUDE  "genasm/beg_p_t.asm"
        INCLUDE  "genasm/beg_u_z.asm"

        DECLE   0
        ENDP

MOON_C  PROC
        INCLUDE  "genasm/chl_a_e.asm"
        INCLUDE  "genasm/chl_f_j.asm"
        INCLUDE  "genasm/chl_k_o.asm"
        INCLUDE  "genasm/chl_p_t.asm"
        INCLUDE  "genasm/chl_u_z.asm"

        DECLE   0
        ENDP

MARS_B  PROC
        INCLUDE  "genasm/mab_a_e.asm"
        INCLUDE  "genasm/mab_f_j.asm"
        INCLUDE  "genasm/mab_k_o.asm"
        INCLUDE  "genasm/mab_p_t.asm"
        INCLUDE  "genasm/mab_u_z.asm"

        DECLE   0
        ENDP

MARS_C  PROC
        INCLUDE  "genasm/mac_a_e.asm"
        INCLUDE  "genasm/mac_f_j.asm"
        INCLUDE  "genasm/mac_k_o.asm"
        INCLUDE  "genasm/mac_p_t.asm"
        INCLUDE  "genasm/mac_u_z.asm"

        DECLE   0
        ENDP

MERC_B  PROC
        INCLUDE  "genasm/hgb_a_e.asm"
        INCLUDE  "genasm/hgb_f_j.asm"
        INCLUDE  "genasm/hgb_k_o.asm"
        INCLUDE  "genasm/hgb_p_t.asm"
        INCLUDE  "genasm/hgb_u_z.asm"

        DECLE   0
        ENDP

MERC_C  PROC
        INCLUDE  "genasm/hgc_a_e.asm"
        INCLUDE  "genasm/hgc_f_j.asm"
        INCLUDE  "genasm/hgc_k_o.asm"
        INCLUDE  "genasm/hgc_p_t.asm"
        INCLUDE  "genasm/hgc_u_z.asm"

        DECLE   0
        ENDP

PLUT_B  PROC
        INCLUDE  "genasm/plb_a_e.asm"
        INCLUDE  "genasm/plb_f_j.asm"
        INCLUDE  "genasm/plb_k_o.asm"
        INCLUDE  "genasm/plb_p_t.asm"
        INCLUDE  "genasm/plb_u_z.asm"

        DECLE   0
        ENDP

;; Pluto Champ needs to be last due to cheesy CRAT6 test in gameover.asm
PLUT_C  PROC
        INCLUDE  "genasm/plc_a_e.asm"
        INCLUDE  "genasm/plc_f_j.asm"
        INCLUDE  "genasm/plc_k_o.asm"
        INCLUDE  "genasm/plc_p_t.asm"
        INCLUDE  "genasm/plc_u_z.asm"

        DECLE   0
        ENDP
