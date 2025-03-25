import ply.lex as lex

tokens = ['NUM', 'ADD', 'SUB', 'MUL', 'DIV', 'PO', 'PC']

t_ADD = r'\+'
t_SUB = r'\-'
t_MUL = r'\*'
t_DIV = r'\/'
t_PO = r'\('
t_PC = r'\)'

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t\n"

def t_error(t):
    print("Invalid character:", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None

    def advance(self):
        self.token = self.lexer.token()
    
    def parse(self, expr):
        self.lexer.input(expr)
        self.advance()
        return self.expression()

    def expression(self):
        result = self.term()
        while self.token and self.token.type in ('ADD', 'SUB'):
            if self.token.type == 'ADD':
                self.advance()
                result += self.term()
            elif self.token.type == 'SUB':
                self.advance()
                result -= self.term()
        return result

    def term(self):
        result = self.factor()
        while self.token and self.token.type in ('MUL', 'DIV'):
            if self.token.type == 'MUL':
                self.advance()
                result *= self.factor()
            elif self.token.type == 'DIV':
                self.advance()
                result /= self.factor()
        return result

    def factor(self):
        if self.token.type == 'NUM':
            value = self.token.value
            self.advance()
            return value
        elif self.token.type == 'PO':
            self.advance()
            value = self.expression()
            if self.token and self.token.type == 'PC':
                self.advance()
                return value
            else:
                raise SyntaxError("Mismatched parentheses")
        else:
            raise SyntaxError("Unexpected token: " + str(self.token))

while True:
    try:
        expr = input("Enter expression: ")
        parser = Parser(lexer)
        result = parser.parse(expr)
        print("Result:", result)
    except EOFError:
        break
    except SyntaxError as e:
        print("Syntax error:", e)