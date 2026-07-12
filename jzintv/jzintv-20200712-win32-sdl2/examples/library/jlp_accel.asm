;; ======================================================================== ;;
;;  JLP Accelerator symbols                                                 ;;
;; ======================================================================== ;;
JLP         PROC
@@mpyss1    EQU     $9F80       ; src1 for s16 * s16 => s32
@@mpyss2    EQU     $9F81       ; src2 for s16 * s16 => s32
@@mpysu1    EQU     $9F82       ; src1 for s16 * u16 => s32
@@mpysu2    EQU     $9F83       ; src2 for s16 * u16 => s32
@@mpyus1    EQU     $9F84       ; src1 for u16 * s16 => s32
@@mpyus2    EQU     $9F85       ; src2 for u16 * s16 => s32
@@mpyuu1    EQU     $9F86       ; src1 for u16 * u16 => u32
@@mpyuu2    EQU     $9F87       ; src2 for u16 * u16 => u32

@@divss1    EQU     $9F88       ; src1 for s16 / s16 => (s16, s16)
@@divss2    EQU     $9F89       ; src2 for s16 / s16 => (s16, s16)
@@divuu1    EQU     $9F8A       ; src1 for u16 / u16 => (u16, u16)
@@divuu2    EQU     $9F8B       ; src2 for u16 / u16 => (u16, u16)

@@prodh     EQU     $9F8F       ; Upper 16 bit of 32-bit product
@@prodl     EQU     $9F8E       ; Lower 16 bit of 32-bit product
@@quot      EQU     $9F8E       ; Quotient of divide
@@rem       EQU     $9F8F       ; Remainder of divide

@@crc_in    EQU     $9FFC       ; Data input to CRC-16
@@crc_out   EQU     $9FFD       ; CRC-16 value.  Write to initialize.
@@rand      EQU     $9FFE       ; 16-bit random number
@@zero      EQU     $9FFF       ; Read-as-zero location
            ENDP

