import sys
import ply.lex as lex

# List of tokens
tokens = ('COMMENT','SELECT', 'WHERE', 'LIMIT','VAR', 'DOT', 'LBRACE', 'RBRACE', 'STRING', 'NUMBER', 'KEYWORD', 'PREFIXED_IDENTIFIER')

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_DOT = r'\.'

def t_COMMENT(t):
    r'\#.*'
    return t

def t_SELECT(t):
    r'(?i)SELECT'
    return t

def t_WHERE(t):
    r'(?i)WHERE'
    return t

def t_LIMIT(t):
    r'(?i)LIMIT'
    return t

def t_VAR(t):
    r'\?[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_STRING(t):
    r'"([^"\\]*(\\.[^"\\]*)*)"(@[a-zA-Z]+)?'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_PREFIXED_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_-]*:[a-zA-Z_][a-zA-Z0-9_-]*'
    return t

def t_KEYWORD(t):
    r'(?i)\ba\b(?![:a-zA-Z0-9_-])'
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Not valid SPARQL '{t.value[0]}'")
    t.lexer.skip(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        content = f.read()

    lexer = lex.lex()
    lexer.input(content)
    for token in lexer:
        print(token)

if __name__ == '__main__':
    main()