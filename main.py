import ply.lex as lex


reserved = {
    'length': 'lengthm',
    'for': 'forl',
    'return': 'return',
    'def': 'defid',
    'var': 'varid',
    'vector': 'vectorid',
    'int': 'intid',
    'if': 'ifid',
    'else': 'elseid',
    'str': 'strid',
    'exit': 'exitm',
    'print': 'printm',
    'scan': 'scanm',
    'list': 'listm',
    'null': 'nullid',
    'to': 'toid',
    'while': 'whileid'
}
x = {
    '<=': 'eqles',
    '>=': 'eqgrt',
    '==': 'equals',
    '!=': 'noteq'
}
tokens = (
    'number',
    'plus',
    'rparen',
    'lparen',
    'defid',
    'equal',
    'varid',
    'sc',
    'lc',
    'rc',
    'intid',
    'vectorid',
    'lb',
    'rb',
    'iden',
    'forl',
    'lengthm',
    'return',
    'strid',
    'ifid',
    'elseid',
    'less',
    'great',
    'exitm',
    'printm',
    'scanm',
    'listm',
    'comment',
    'minus',
    'divide',
    'multiplier',
    'nullid',
    'toid',
    'string',
    'not',
    'and',
    'or',
    'remain',
    'qmark',
    'whileid',
    'noteq',
    'equals',
    'eqgrt',
    'eqles',
    'kama',
    'ddot'
)

t_ddot = r'\:'
t_kama = r'\,'
t_qmark = r'\?'
t_remain = r'\%'
t_or = r'\|\|'
t_and = r'\&\&'
t_string = r'(\' [^\'\n]* [\'] | ["]  [^"\n]* ["])'
t_multiplier = r'\*'
t_divide = r'\/'
t_minus = r'\-'
t_lb = r'\['
t_rb = r'\]'
t_rc = r'\}'
t_lc = r'\{'
t_sc = r'\;'
t_plus = r'\+'
t_lparen = r'\('
t_rparen = r'\)'


def t_comment(t):
    r'\#.*$'
    pass


def t_number(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_not(t):
    r'[!] [=]{0,1}'
    t.type = x.get(t.value, 'equal')
    return t


def t_equal(t):
    r'[=] [=]{0,1}'
    t.type = x.get(t.value, 'equal')
    return t


def t_great(t):
    r'[>] [=]{0,1}'
    t.type = x.get(t.value, 'great')
    return t


def t_less(t):
    r'[<][=]{0,1}'
    t.type = x.get(t.value, 'less')
    return t


def t_iden(t):
    r'[a-zA-Z_]([a-z] | [A-Z] | \_ | [0-9])*'
    t.type = reserved.get(t.value, 'iden')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
    asp = t.value[0]
    i = 2
    while True:
        next_char = t.lexer.lexdata[t.lexer.lexpos]
        if next_char == ' ' or next_char == ';' or next_char == "\n":
            print("Illegal token \"" + asp[0:i - 2] + "\" in line " + t.lineno.__str__())
            break
        asp += t.value[i - 1]
        i = i + 1
        t.lexer.skip(1)


lexer = lex.lex()
file1 = open("test.txt", "r")
data = file1.readlines()
file1.close()

for i in range(0, len(data)):
    data1 = data[i]
    lexer.input(data1)
    while True:
        tok = lexer.token()
        if not tok:
            break
        #print(tok.value)
