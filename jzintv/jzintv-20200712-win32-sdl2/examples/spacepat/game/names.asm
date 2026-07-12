
;; ======================================================================== ;;
;;  Course sub-names                                                        ;;
;; ======================================================================== ;;
BEGINNER    S16     " BEGINNER "
CHAMPION    S16     " CHAMPION "

;; ======================================================================== ;;
;;  CNAME   Course names, as well as where to print them.                   ;;
;; ======================================================================== ;;
CNAME       PROC 
            DECLE   @@moon, pack(packn(C_BLU, 4), disp_ofs(3, 13))
            DECLE   @@mars, pack(packn(C_RED, 4), disp_ofs(3, 13))
            DECLE   @@plut, pack(packn(C_GRN, 3), disp_ofs(3, 12))
            DECLE   @@merc, pack(packn(C_TAN, 2), disp_ofs(3, 11))
@@moon      S16     "MOON"
@@mars      S16     "MARS"
@@plut      S16     "PLUTO"
@@merc      S16     "MERCURY"
            ENDP
