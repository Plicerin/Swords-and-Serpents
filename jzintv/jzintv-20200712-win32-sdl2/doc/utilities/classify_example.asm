CLASS.ABSOLUTE  EQU (-1)
CLASS.SET       EQU (-2)
CLASS.EQU       EQU (-3)
CLASS.STRING    EQU (-4)
CLASS.FEATURE   EQU (-5)
CLASS.RESERVED  EQU (-6)
CLASS.EMPTY     EQU (-7)
CLASS.UNUSED    EQU (-8)
CLASS.UNKNOWN   EQU (-9)
CLASS.UNDEFINED EQU (-10000)

MACRO   WHAT a
    LISTING "code"
    IF CLASSIFY(%a%) = CLASS.ABSOLUTE
        SMSG    "%a% is an ASBOLUTE expression"
    ELSE
    IF CLASSIFY(%a%) = CLASS.SET
        SMSG    "%a% is a symbol defined by SET"
    ELSE
    IF CLASSIFY(%a%) = CLASS.EQU
        SMSG    "%a% is a symbol defined by EQU"
    ELSE
    IF CLASSIFY(%a%) = CLASS.STRING
        SMSG    $('"', %a%, '"', " is a STRING")
    ELSE
    IF CLASSIFY(%a%) = CLASS.FEATURE
        SMSG    "%a% is the name of a FEATURE"
    ELSE
    IF CLASSIFY(%a%) = CLASS.RESERVED
        SMSG    "%a% is a RESERVED word"
    ELSE
    IF CLASSIFY(%a%) = CLASS.EMPTY
        SMSG    "EMPTY argument?"
    ELSE
    IF CLASSIFY(%a%) = CLASS.UNUSED
        ERR     "%a% is UNUSED type.  (This shouldn't happen)"
    ELSE
    IF CLASSIFY(%a%) = CLASS.UNKNOWN
        ERR     "%a% is UNKNOWN type.  (This shouldn't happen)"
    ELSE
    IF CLASSIFY(%a%) = CLASS.UNDEFINED
        SMSG    "%a% is an UNDEFINED expression"
    ELSE
    IF CLASSIFY(%a%) >= 0 AND CLASSIFY(%a%) <= 7
        SMSG    $("%a% corresponds to register R", '0' + CLASSIFY(%a%))
    ELSE
        ERR     "CLASSIFY(%a%) returned an unexpected value"
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    ENDI
    LISTING "prev"
ENDM

set_label:      SET 0
equ_label:      EQU 0

rev_label:
                WHAT rev_label
                WHAT rev_label + 42
label0:         WHAT label0
label1:         WHAT label1 + 42
                WHAT fwd_label
                WHAT fwd_label + 42
fwd_label:      WHAT set_label
                WHAT equ_label
                WHAT set_label + equ_label
                WHAT 42
                WHAT 42 + 69
                WHAT CLASSIFY
                WHAT "string"
                WHAT AND
                WHAT MVO@   ; Counterintutive result: Returns UNDEFINED
                WHAT MACRO  ; Returns FEATURE
                WHAT ENDM   ; Returns FEATURE
                WHAT R0
                WHAT R1
                WHAT R2
                WHAT R3
                WHAT R4
                WHAT R5
                WHAT R6
                WHAT R7
                WHAT SP
                WHAT PC

;; The above should print out the following at assembly time:
;;
;; rev_label is an ASBOLUTE expression
;; rev_label + 42 is an ASBOLUTE expression
;; label0 is an ASBOLUTE expression
;; label1 + 42 is an ASBOLUTE expression
;; fwd_label is an UNDEFINED expression
;; fwd_label + 42 is an UNDEFINED expression
;; set_label is a symbol defined by SET
;; equ_label is a symbol defined by EQU
;; set_label + equ_label is an ASBOLUTE expression
;; 42 is an ASBOLUTE expression
;; 42 + 69 is an ASBOLUTE expression
;; CLASSIFY is a RESERVED word
;; "string" is a STRING
;; AND is a RESERVED word
;; MVO@ is an UNDEFINED expression
;; MACRO is the name of a FEATURE
;; ENDM is the name of a FEATURE
;; R0 corresponds to register R0
;; R1 corresponds to register R1
;; R2 corresponds to register R2
;; R3 corresponds to register R3
;; R4 corresponds to register R4
;; R5 corresponds to register R5
;; R6 corresponds to register R6
;; R7 corresponds to register R7
;; SP corresponds to register R6
;; PC corresponds to register R7
