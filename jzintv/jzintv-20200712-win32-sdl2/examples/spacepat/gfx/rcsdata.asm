RCS1    PROC
@@nosc  EQU     $8000 + (0 SHL 9)
@@sc500 EQU     $8000 + (1 SHL 9)
@@sc750 EQU     $8000 + (2 SHL 9)
@@sc1K  EQU     $8000 + (3 SHL 9)

@@rock1 DECLE   ($0800 + (RCARD + 0) * 8 + X_ROCK) + @@nosc     ; small rock
        DECLE   ($0800 + (RCARD + 1) * 8 + X_ROCK) + @@sc500    ; 
        DECLE   $0001                                           
@@rock2 DECLE   ($0800 + (RCARD + 2) * 8 + X_ROCK) + @@nosc     ; midsize rock
        DECLE   ($0800 + (RCARD + 3) * 8 + X_ROCK) + @@sc750    ; 
        DECLE   $0001                                           
@@rock3 DECLE   ($0800 + (RCARD + 4) * 8 + X_ROCK) + @@nosc     ; super rock
        DECLE   ($0800 + (RCARD + 5) * 8 + X_ROCK) + @@nosc     ; 
        DECLE   ($0800 + (RCARD + 6) * 8 + X_ROCK) + @@sc1K     ;
        DECLE   $0001                                           
@@crat1 DECLE   $0800                              + @@nosc     ; small crater
        DECLE   $0800                              + @@sc500    ; 
        DECLE   $0001                                           
@@crat3 DECLE   $0800                              + @@nosc     ; small crater
        DECLE   $0800                              + @@sc500    ; 
@@crat2 DECLE   $0800                              + @@nosc     ; large crater
        DECLE   $0800                              + @@nosc     ; 
        DECLE   $0800                              + @@sc1K     ; 
        DECLE   $0001                                           
@@crat4 DECLE   $0800                              + @@nosc     ; large crater
        DECLE   $0800                              + @@nosc     ; 
        DECLE   $0800                              + @@nosc     ; 
        DECLE   $0800                              + @@sc500    ; small crater
        DECLE   $0800                              + @@sc1K     ; 
@@blank DECLE   $0001                                          
@@cratz DECLE   $0001
        ENDP                                                   
                                                               
RCS2    PROC                                                   
@@nosc  EQU     $8000 + (0 SHL 9)
@@sc500 EQU     $8000 + (1 SHL 9)
@@sc750 EQU     $8000 + (2 SHL 9)
@@sc1K  EQU     $8000 + (3 SHL 9)

@@rock1 DECLE   GCARDx                                          ; small rock
        DECLE   GCARDx                                          ;
        DECLE   GCARDx                                          
@@rock2 DECLE   GCARDx                                          ; midsize rock
        DECLE   GCARDx                                          ;
        DECLE   GCARDx                                          
@@rock3 DECLE   GCARDx                                          ; super rock
        DECLE   GCARDx                                          ;
        DECLE   GCARDx                                          ;
        DECLE   GCARDx                                          
@@crat1 DECLE   ($1802 + (RCARD + 7) * 8)          + @@nosc     ; small crater
        DECLE   ($1802 + (RCARD + 8) * 8)          + @@nosc     ; 
        DECLE   GCARDx                                          
@@crat3 DECLE   ($1802 + (RCARD + 7) * 8)          + @@nosc     ; small crater
        DECLE   ($1802 + (RCARD + 8) * 8)          + @@nosc     ; 
@@crat2 DECLE   ($1802 + (RCARD + 9) * 8)          + @@nosc     ; super crater
        DECLE   ($1802 + (RCARD +10) * 8)          + @@nosc     ; 
        DECLE   ($1802 + (RCARD +11) * 8)          + @@nosc     ; 
        DECLE   GCARDx                                         
@@crat4 DECLE   ($1802 + (RCARD + 9) * 8)          + @@nosc     ; super crater
        DECLE   ($1802 + (RCARD +10) * 8)          + @@nosc     ; 
        DECLE   ($1802 + (RCARD +11) * 8)          + @@nosc     ; 
        DECLE   ($1802 + (RCARD + 7) * 8)          + @@nosc     ; small crater
        DECLE   ($1802 + (RCARD + 8) * 8)          + @@nosc     ; 
@@blank DECLE   GCARDx
        DECLE   0
        ENDP
