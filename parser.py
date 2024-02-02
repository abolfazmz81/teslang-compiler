import ply.yacc as yacc
import AST
import semanticChecker
import symbol_table
from main import *

# yacc.YaccProduction

precedence = (
    ('left', 'minus', 'plus'),
    ('left', 'multiplier', 'divide', 'remain')
)


# Rule 1
def p_prog(p: yacc.YaccProduction):
    """prog : empty
            | func prog"""
    if len(p) == 3:
        p[0] = AST.Program(prog=p[2], func=p[1], pos=p.lineno(1) + 1 - len(data))
        # a = symbol_table.SymbolTable(None, None)
        # semanticChecker.push_builtins_to_table(table=a)
        p[0].accept(None)


# Rule 2
def p_empty(p: yacc.YaccProduction):
    """empty :"""
    pass
    p[0] = []


# Rule 3
def p_func(p: yacc.YaccProduction):
    """func : defid type iden lparen flist rparen lc body rc"""
    p[0] = AST.FunctionDef(rettype=p[2], name=p[3], params=p[5], body=p[8], pos=p.lineno(1) + 1 - len(data))


# maybe bodyless func

def p_func_rtype_error(p: yacc.YaccProduction):
    """func : defid error iden lparen flist rparen lc body rc"""
    print("missing or invalid return type for function " + p[2].value + " at line " + (
                p.lineno(1) + 1 - len(data)).__str__())
    p[0] = AST.FunctionDef(rettype='int', name=p[3], params=p[5], body=p[8], pos=p.lineno(1) + 1 - len(data))


def p_func_flist_error(p: yacc.YaccProduction):
    """func : defid type iden lparen error rparen lc body rc"""
    print("invalid arguments for function " + p[3] + "at line: " + (p.lineno(1) - len(data) + 1).__str__())
    p[0] = AST.FunctionDef(rettype=p[2], name=p[3], params=None, body=p[8], pos=p.lineno(1) + 1 - len(data))


def p_func_double_error(p: yacc.YaccProduction):
    """func : defid error iden lparen error rparen lc body rc"""
    print("invalid arguments and type for function " + p[3] + "at line: " + (p.lineno(1) - len(data) + 1).__str__())
    p[0] = AST.FunctionDef(rettype='int', name=p[3], params=None, body=p[8], pos=p.lineno(1) + 1 - len(data))


# Rule 4
def p_type(p: yacc.YaccProduction):
    """type : intid
            | strid
            | vectorid
            | nullid"""
    p[0] = p[1]


# Rule 5
def p_body(p: yacc.YaccProduction):
    """body : empty
            | stmt body"""
    if len(p) == 3:
        p[0] = AST.Body(statement=p[1], body=p[2])


# Rule 6
def p_stmt(p: yacc.YaccProduction):
    """stmt : expr sc
            | defvar sc
            | single_if
            | else_if
            | while_loop
            | for_loop
            | return_is sc
            | block
            | func """
    p[0] = p[1]


def p_return_is(p: yacc.YaccProduction):
    """return_is : return expr"""
    p[0] = AST.ReturnInstruction(expr=p[2], pos=p.lineno(1) + 1 - len(data))


def p_while_loop(p: yacc.YaccProduction):
    """while_loop : whileid lparen expr rparen stmt"""
    p[0] = AST.WhileInstruction(cond=p[3], while_statement=p[5], pos=p.lineno(1) + 1 - len(data))


def p_for_loop(p: yacc.YaccProduction):
    """for_loop : forl lparen iden equal expr toid expr rparen stmt"""
    p[0] = AST.ForInstruction(id=p[3], start_expr=p[5], end_expr=p[7], for_statement=p[9],
                              pos=p.lineno(1) + 1 - len(data))


def p_block(p: yacc.YaccProduction):
    """block : lc body rc"""
    p[0] = AST.Block(body=p[2])


def p_single_if(p: yacc.YaccProduction):
    """single_if : ifid lparen expr rparen stmt"""
    p[0] = AST.IfOrIfElseInstruction(cond=p[3], if_statement=p[5], pos=p.lineno(1) + 1 - len(data), else_statement=None)


def p_single_if_error(p: yacc.YaccProduction):
    """single_if : ifid lparen error rparen stmt"""
    print("invalid statement for if at line " + (p.lineno(1) + 1 - len(data)).__str__())


def p_else_if(p: yacc.YaccProduction):
    """else_if : ifid lparen expr rparen stmt elseid stmt"""
    p[0] = AST.IfOrIfElseInstruction(cond=p[3], if_statement=p[5], pos=p.lineno(1) + 1 - len(data), else_statement=p[7])


def p_else_if_error(p: yacc.YaccProduction):
    """else_if : ifid lparen error rparen stmt elseid stmt"""
    print("invalid statement for else if at line " + (p.lineno(1) + 1 - len(data)).__str__())


def p_while_loop_error(p: yacc.YaccProduction):
    """while_loop : whileid lparen error rparen stmt"""
    print("invalid expression for while at line " + (p.lineno(1) - len(data)).__str__())
    p[0] = AST.WhileInstruction(cond=p[3], while_statement=p[5], pos=p.lineno(1) + 1 - len(data))


def p_for_loop_error(p: yacc.YaccProduction):
    """for_loop : forl lparen iden equal error toid expr rparen stmt
            | forl lparen iden equal expr toid error rparen stmt
            | forl lparen iden equal error toid error rparen stmt"""
    print("invalid expression(s) for 'for' at line " + (p.lineno(1) + 1 - len(data)).__str__())


# Rule 7
def p_defvar(p: yacc.YaccProduction):
    """defvar : varid type iden
              | varid type iden equal expr"""
    if len(p) == 4:
        p[0] = AST.VariableDecl(id=p[3], type=p[2], pos=p.lineno(1) + 1 - len(data), expr=None)
    elif len(p) == 6:
        p[0] = AST.VariableDecl(id=p[3], type=p[2], pos=p.lineno(1) + 1 - len(data), expr=p[5])


def p_defvar_type_error(p: yacc.YaccProduction):
    """defvar : varid error iden
              | varid error iden equal expr"""
    print("invalid type for 'def var' at line " + (p.lineno(1) - len(data) + 1).__str__())
    if len(p) == 4:
        p[0] = AST.VariableDecl(id=p[3], type='int', pos=p.lineno(1) + 1 - len(data), expr=None)
    elif len(p) == 6:
        p[0] = AST.VariableDecl(id=p[3], type='int', pos=p.lineno(1) + 1 - len(data), expr=p[5])


def p_defvar_var_error(p: yacc.YaccProduction):
    """defvar : error type iden
              | error type iden equal expr"""
    print("invalid syntax for 'def var' at line " + (p.lineno(1) - len(data) + 1).__str__())
    if len(p) == 4:
        p[0] = AST.VariableDecl(id=p[3], type='int', pos=p.lineno(1) + 1 - len(data), expr=None)
    elif len(p) == 6:
        p[0] = AST.VariableDecl(id=p[3], type='int', pos=p.lineno(1) + 1 - len(data), expr=p[5])


# Rule 8
def p_flist(p: yacc.YaccProduction):
    """flist : empty
             | type iden
             | type iden kama flist"""
    if len(p) == 3:
        p[0] = AST.ParametersList(parameters=[AST.Parameter(type=p[1], id=p[2])])
    if len(p) == 5:
        p[0] = AST.ParametersList(parameters=p[4].parameters + [AST.Parameter(type=p[1], id=p[2])])


def p_flist_type_error(p: yacc.YaccProduction):
    """flist : error iden
             | error iden kama flist"""
    print("invalid type for argument list in line: " + ((p.lineno(1) + 1) - len(data)).__str__())
    p[0] = AST.ParametersList(parameters=[])


def p_flist_iden_error(p: yacc.YaccProduction):
    """flist : type error
             | type error kama flist"""
    print("invalid id for argument list in line: " + ((p.lineno(1) + 1) - len(data)).__str__())
    p[0] = AST.ParametersList(parameters=[])


def p_flist_flist_error(p: yacc.YaccProduction):
    """flist : type iden kama error"""
    print("invalid flist for argument list in line: " + ((p.lineno(1) + 1) - len(data)).__str__())
    p[0] = AST.ParametersList(parameters=[])


# Rule 9
def p_clist(p: yacc.YaccProduction):
    """clist : empty
             | expr
             | expr kama clist"""
    if len(p) == 2:
        if p[1] == []:
            exprs = []
        else:
            exprs = [p[1]]
        p[0] = AST.ExprList(exprs=exprs)
    elif len(p) == 4:
        p[0] = AST.ExprList(exprs=p[3].exprs + [p[1]])


def p_clist_kama_error(p: yacc.YaccProduction):
    """clist :  expr error clist"""
    print("invalid token in line(expected ',' instead): " + ((p.lineno(1) + 1) - len(data)).__str__())
    if len(p) == 2:
        if p[1] == []:
            exprs = []
        else:
            exprs = [p[1]]
        p[0] = AST.ExprList(exprs=exprs)
    elif len(p) == 4:
        p[0] = AST.ExprList(exprs=p[3].exprs + [p[1]])


# Rule 10
def p_expr(p: yacc.YaccProduction):
    """expr : on_list
            | expr_list
            | ternary_expr
            | not expr
            | plus expr
            | minus expr
            | binary_expr
            | string
            | builtin_methods
            | assignment
            | number
            | iden
            | func_call"""
    if len(p) == 4 or len(p) == 3:
        if p[1] == '-':
            p[2].value = -p[2].value
        elif p[1] == '!':
            if p[2].value:
                p[2].value = 0
            else:
                p[2].value = 1
        p[0] = p[2]
    else:
        if p.slice[1].type in ('number', 'iden', 'string'):
            p[0] = p.slice[1]
        else:
            p[0] = p[1]


def p_func_call(p: yacc.YaccProduction):
    """func_call : iden lparen clist rparen"""
    p[0] = AST.FunctionCall(id=p[1], args=p[3], pos=p.lineno(1) + 1 - len(data))


def p_on_list(p: yacc.YaccProduction):
    """on_list : expr lb expr rb
                | iden lb expr rb"""
    p[0] = AST.OperationOnList(expr=p[1], index_expr=p[3], pos=p.lineno(1) + 1 - len(data))


def p_expr_assignment(p: yacc.YaccProduction):
    """assignment :  iden equal expr"""
    p[0] = AST.Assignment(id=p[1], expr=p[3], pos=p.lineno(1) + 1 - len(data))


def p_expr_assignment_error(p: yacc.YaccProduction):
    """assignment :  iden error expr"""
    print("expected token or unexpected error in assignment in line: " + (
            (p.lineno(1) + 1) - len(data)).__str__() + " near token: " + p[2].value.__str__())
    p[0] = AST.Assignment(id=p[1], expr=p[3], pos=p.lineno(1) + 1 - len(data))


def p_expr_list(p: yacc.YaccProduction):
    """expr_list : lb clist rb"""
    p[0] = p[2]


def p_ternary_expr(p: yacc.YaccProduction):
    """ternary_expr : expr qmark expr ddot expr"""
    p[0] = AST.TernaryExpr(cond=p[1], first_expr=p[2], second_expr=p[3], pos=p.lineno(1) + 1 - len(data))


def p_expr_unexpected_token(p: yacc.YaccProduction):
    """ternary_expr : expr error expr ddot expr"""
    print("expected token '?' in line: " + ((p.lineno(1) + 1) - len(data)).__str__() + " near token: " + p[
        2].value.__str__())
    p[0] = AST.TernaryExpr(cond=p[1], first_expr=p[2], second_expr=p[3], pos=p.lineno(3) + 1 - len(data))


def p_binary_expr(p: yacc.YaccProduction):
    """binary_expr : expr plus expr
                   | expr minus expr
                   | expr multiplier expr
                   | expr divide expr
                   | expr remain expr
                   | expr great expr
                   | expr less expr
                   | expr equals expr
                   | expr eqgrt expr
                   | expr eqles expr
                   | expr noteq expr
                   | expr or expr
                   | expr and expr"""
    p[0] = AST.BinExpr(left=p[1], op=p[2], right=p[3], pos=p.lineno(2) + 1 - len(data))


def p_binary_unexpected_token_two(p: yacc.YaccProduction):
    """binary_expr : expr error expr"""
    print("expected token or unexpected in line: " + ((p.lineno(1) + 1) - len(data)).__str__() + " near token: " + p[
        2].value.__str__())


def p_builtin_methods(p: yacc.YaccProduction):
    """builtin_methods : scanm lparen rparen
                       | printm lparen clist rparen
                       | listm lparen clist rparen
                       | lengthm lparen clist rparen
                       | exitm lparen clist rparen"""
    if len(p) == 4:
        p[0] = AST.FunctionCall(id=p[1], args=None, pos=p.lineno(1) + 1 - len(data))
    else:
        p[0] = AST.FunctionCall(id=p[1], args=p[3], pos=p.lineno(1) + 1 - len(data))


def p_error(p: yacc.YaccProduction):
    pass


parser = yacc.yacc(start='prog')

file1 = open("test.txt", "r")
data = file1.readlines()
file1.close()
s = ''
for i in range(0, len(data)):
    data1 = data[i]
    # lexer.input(data1)
    s = s + data1

result = parser.parse(s, tracking=True)
# print(s)
print(result)
