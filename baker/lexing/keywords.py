# c 2025-01-04
# m 2025-01-09

ASSIGN_OPS:  tuple[str] = '=', '+=', '-=', '*=', '/=', '%='
BINARY_OPS:  tuple[str] = '+', '-', '*', '/', '%'
COMPARE_OPS: tuple[str] = '==', '<', '>', '<=', '>=', '!='
POSTFIX_OPS: tuple[str] = '++', '--'
PREFIX_OPS:  tuple[str] = '+', '-',
OPERATORS:   tuple[str] = ASSIGN_OPS + BINARY_OPS + COMPARE_OPS + POSTFIX_OPS + PREFIX_OPS

LOWERCASE:                str = 'abdecfghijklmnopqrstuvwxyz'
UPPERCASE:                str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBER_START_SYMBOLS:     str = '0123456789'
NUMBER_SYMBOLS:           str = NUMBER_START_SYMBOLS + "'."
IDENTIFIER_START_SYMBOLS: str = LOWERCASE + UPPERCASE + '_'
IDENTIFIER_SYMBOLS:       str = NUMBER_START_SYMBOLS + IDENTIFIER_START_SYMBOLS
OPERATOR_SYMBOLS:         str = '%*-+=/'
PUNCTUATOR_SYMBOLS:       str = r'{}[]();,'

PRIMARY_KEYWORDS:     tuple[str] = 'cast', 'error', 'false', 'handle', 'is', 'null', 'return', 'true', 'with'
PRIMITIVE_KEYWORDS:   tuple[str] = 'base', 'bool', 'dec', 'flt', 'int', 'str', 'void'
CONTAINER_KEYWORDS:   tuple[str] = 'arr', 'dict'
TYPE_KEYWORDS:        tuple[str] = PRIMITIVE_KEYWORDS + CONTAINER_KEYWORDS
FUNCTION_KEYWORDS:    tuple[str] = 'assert', 'input', 'print', 'super'
DEFINABLE_KEYWORDS:   tuple[str] = 'class', 'enum', 'namespace', 'struct'
MODIFIER_KEYWORDS:    tuple[str] = 'const', 'final', 'fixed', 'override', 'static'
LOGIC_KEYWORDS:       tuple[str] = 'and', 'nand', 'nor', 'not', 'nox', 'or', 'xor'
CONDITIONAL_KEYWORDS: tuple[str] = 'break', 'case', 'continue', 'do', 'else', 'for', 'if', 'switch', 'while'
KEYWORDS:             tuple[str] = PRIMARY_KEYWORDS + TYPE_KEYWORDS + FUNCTION_KEYWORDS + DEFINABLE_KEYWORDS + MODIFIER_KEYWORDS + LOGIC_KEYWORDS + CONDITIONAL_KEYWORDS

# NUMBER_REGEX: str = r'^(?!\.)[0-9]+(?:\.[0-9]+d?)?(?:e[0-9]+)?(?<![e\.])$|0b[01]+(?<![^01])$|0x[0-9a-fA-F]+(?<![^0-9a-fA-F])$'
FIXED_NUMBER_REGEX: str = r'/(?:dec|int|str)[0-9]*(?:[0-9]*)$'
