import ply.lex as lex

# Lista de tokens
tokens = [
    "IDENT",
    "NUM_INT",
    "NUM_REAL",
    "STRING_LITERAL",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "ASSIGN",
    "COMMA",
    "SEMI",
    "COLON",
    "EQUAL",
    "NOT_EQUAL",
    "LT",
    "LE",
    "GE",
    "GT",
    "LPAREN",
    "RPAREN",
    "LBRACK",
    "LBRACK2",
    "RBRACK",
    "RBRACK2",
    "POINTER",
    "AT",
    "DOT",
    "DOTDOT",
    "LCURLY",
    "RCURLY",
    # Keywords como tokens explícitos
    "AND",
    "ARRAY",
    "BEGIN",
    "BOOLEAN",
    "CASE",
    "CHAR",
    "CHR",
    "CONST",
    "DIV",
    "DO",
    "DOWNTO",
    "ELSE",
    "END",
    "EXTERNAL",
    "FILE",
    "FOR",
    "FUNCTION",
    "GOTO",
    "IF",
    "IN",
    "INTEGER",
    "LABEL",
    "MOD",
    "NIL",
    "NOT",
    "OF",
    "OR",
    "PACKED",
    "PROCEDURE",
    "PROGRAM",
    "REAL",
    "RECORD",
    "REPEAT",
    "SET",
    "THEN",
    "TO",
    "TYPE",
    "UNTIL",
    "VAR",
    "WHILE",
    "WITH",
    "UNIT",
    "INTERFACE",
    "STRING",
    "IMPLEMENTATION",
    "TRUE",
    "FALSE",
]

# Regras para operadores e pontuação
t_PLUS = r"\+"
t_MINUS = r"-"
t_STAR = r"\*"
t_SLASH = r"/"
t_ASSIGN = r":="
t_COMMA = r","
t_SEMI = r";"
t_COLON = r":"
t_EQUAL = r"="
t_NOT_EQUAL = r"<>"
t_LT = r"<"
t_LE = r"<="
t_GE = r">="
t_GT = r">"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACK = r"\["
t_LBRACK2 = r"\(\."
t_RBRACK = r"\]"
t_RBRACK2 = r"\.\)"
t_POINTER = r"\^"
t_AT = r"@"
t_DOT = r"\."
t_DOTDOT = r"\.\."
t_LCURLY = r"{"
t_RCURLY = r"}"


# Palavras reservadas (cada uma com sua função)
def t_AND(t):
    r"and"
    return t


def t_ARRAY(t):
    r"array"
    return t


def t_BEGIN(t):
    r"begin"
    return t


def t_BOOLEAN(t):
    r"boolean"
    return t


def t_CASE(t):
    r"case"
    return t


def t_CHAR(t):
    r"char"
    return t


def t_CHR(t):
    r"chr"
    return t


def t_CONST(t):
    r"const"
    return t


def t_DIV(t):
    r"div"
    return t

def t_DOWNTO(t):
    r"downto"
    return t

def t_DO(t):
    r"do"
    return t

def t_ELSE(t):
    r"else"
    return t


def t_END(t):
    r"end"
    return t


def t_EXTERNAL(t):
    r"external"
    return t


def t_FILE(t):
    r"file"
    return t


def t_FOR(t):
    r"for"
    return t


def t_FUNCTION(t):
    r"function"
    return t


def t_GOTO(t):
    r"goto"
    return t


def t_IF(t):
    r"if"
    return t


def t_INTEGER(t):
    r"integer"
    return t


def t_IN(t):
    r"in"
    return t


def t_LABEL(t):
    r"label"
    return t


def t_MOD(t):
    r"mod"
    return t


def t_NIL(t):
    r"nil"
    return t


def t_NOT(t):
    r"not"
    return t


def t_OF(t):
    r"of"
    return t


def t_OR(t):
    r"or"
    return t


def t_PACKED(t):
    r"packed"
    return t


def t_PROCEDURE(t):
    r"procedure"
    return t


def t_PROGRAM(t):
    r"program"
    return t


def t_REAL(t):
    r"real"
    return t


def t_RECORD(t):
    r"record"
    return t


def t_REPEAT(t):
    r"repeat"
    return t


def t_SET(t):
    r"set"
    return t


def t_THEN(t):
    r"then"
    return t


def t_TO(t):
    r"to"
    return t


def t_TYPE(t):
    r"type"
    return t


def t_UNTIL(t):
    r"until"
    return t


def t_VAR(t):
    r"var"
    return t


def t_WHILE(t):
    r"while"
    return t


def t_WITH(t):
    r"with"
    return t


def t_UNIT(t):
    r"unit"
    return t


def t_INTERFACE(t):
    r"interface"
    return t


def t_STRING(t):
    r"string"
    return t


def t_IMPLEMENTATION(t):
    r"implementation"
    return t


def t_TRUE(t):
    r"true"
    return t


def t_FALSE(t):
    r"false"
    return t


# Identificadores
def t_IDENT(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    return t


# Números
def t_NUM_REAL(t):
    r"(\d+\.\d+([Ee][+-]?\d+)?)|(\d+[Ee][+-]?\d+)"
    try:
        t.value = float(t.value)
    except ValueError:
        print(f"Float value too large: {t.value}")
        t.value = 0
    return t


def t_NUM_INT(t):
    r"\d+"
    try:
        t.value = int(t.value)
    except ValueError:
        print(f"Integer value too large: {t.value}")
        t.value = 0
    return t


# Strings
def t_STRING_LITERAL(t):
    r"'(''|[^'])*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t


# Comentários
def t_COMMENT_1(t):
    r"\(\*.*?\*\)"
    t.lexer.lineno += t.value.count("\n")
    pass


def t_COMMENT_2(t):
    r"{.*?}"
    t.lexer.lineno += t.value.count("\n")
    pass


# Contador de linhas
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Espaços e tabulação ignorados
t_ignore = " \t\r"


# Erros
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


# Constrói o lexer
lexer = lex.lex()


# For testing the lexer
if __name__ == "__main__":
    data = """
    program Test;

    procedure Greet;
    begin
        writeln('Hello from a procedure!');
    end;

    begin
        Greet;
    end.

    """

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    for tok in lexer:
        print(tok)
