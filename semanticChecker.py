import symbol_table
import AST




class Not_found(Exception):
    pass


class semanticChecker(object):
    def __init__(self):
        pass

    cast_var = {
        'number': 'int',
        'string': 'str',
    }

    def push_builtins_to_table(self,table : symbol_table):
        def create_list_func():
            return symbol_table.FunctionSymbol('vector', 'list', AST.ParametersList([AST.Parameter('int', 'size')]))

        def create_print_func():
            return symbol_table.FunctionSymbol('null', 'print',
                                               AST.ParametersList([AST.Parameter('str', 'int_to_print')]))

        def create_exit_func():
            return symbol_table.FunctionSymbol('int', 'exit',
                                               AST.ParametersList([AST.Parameter('int', 'int_to_return')]))

        def create_length_func():
            return symbol_table.FunctionSymbol('int', 'length',
                                               AST.ParametersList([AST.Parameter('vector', 'vector_to_count')]))

        def create_scan_func():
            return symbol_table.FunctionSymbol('int', 'scan', AST.ParametersList([]))

        table.put(create_list_func())
        table.put(create_print_func())
        table.put(create_length_func())
        table.put(create_scan_func())
        table.put(create_exit_func())

    def extract_expr_type(self, expr, table):
        expr_class_name = expr.__class__
        if expr_class_name.__name__ == 'LexToken':
            if expr.type == 'iden':
                symbol = table.get(expr.value)
                if isinstance(symbol, symbol_table.VariableSymbol) and not symbol.assigned:
                    self.handle_error(expr.lineno,
                                      '\'' + expr.value + '\' not assigned but used in a expression in function \''
                                      + table.function.name + '\'')
                if symbol:
                    if isinstance(symbol, symbol_table.VariableSymbol):
                        return symbol.type
                    elif isinstance(symbol, symbol_table.VectorSymbol):
                        return symbol.type
                else:
                    self.handle_error(expr.lineno, 'Variable \'' + expr.value +
                                      '\' not defined but used in expression in function \'' + table.function.name + '\'')
                    raise Not_found
            else:
                return self.cast_var[expr.type]
        elif expr_class_name == AST.ExprList:
            return 'vector'
        elif expr_class_name == AST.FunctionCall:
            expr.accept(table)
            funcSymbol = table.get(expr.id)
            if funcSymbol and isinstance(funcSymbol, symbol_table.FunctionSymbol):
                return funcSymbol.rettype
            else:
                raise Not_found
        elif expr_class_name == AST.Assignment:
            expr.accept(table)
        elif expr_class_name == AST.TernaryExpr:
            expr.accept(table)
        elif expr_class_name == AST.BinExpr:
            expr.accept(table)
            try:
                left_type = self.extract_expr_type(expr.left, table)
                right_type = self.extract_expr_type(expr.right, table)
                if left_type == right_type:
                    return left_type
            except Not_found:
                pass
        elif expr_class_name == AST.OperationOnList:
            expr.accept(table)
            return 'int'
        return 'unknown'

    def visit_Program(self, node, table):
        if table is None:
            table = symbol_table.SymbolTable(None, None)
        self.push_builtins_to_table(table)
        node.func.accept(table)
        if node.prog:
            table = node.prog.accept(table)
        return table

    def check_function_def_errors(self, node, parent_table, funcSymbol):
        if not parent_table.put(funcSymbol):
            if parent_table.get(node.name).redefined:
                self.handle_error(node.pos, 'Function \'' +
                                  node.name + '\' already defined')
        child_table = symbol_table.SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            for param in node.fmlparams.parameters:
                symbol = None
                if param.type == 'vector':
                    symbol = symbol_table.VectorSymbol(param.id, 1000)  # 1000 is default size for vectors
                else:
                    symbol = symbol_table.VariableSymbol(param.type, param.id, True)
                if not child_table.put(symbol):
                    self.handle_error(
                        node.pos,
                        'Parameter \'' + param.id + '\' already defined in function \'' + node.name + '\'')
        return child_table

    def visit_FunctionDef(self, node, parent_table: symbol_table.SymbolTable):
        funcSymbol = symbol_table.FunctionSymbol(node.rettype, node.name, node.fmlparams)
        child_table = self.check_function_def_errors(node, parent_table, funcSymbol)
        if node.body:
            node.body.accept(child_table)

    def visit_Body(self, node, table):
        if node.statement:
            if hasattr(node.statement, 'accept'):
                node.statement.accept(table)
        if node.body:
            node.body.accept(table)

    def visit_FunctionCall(self, node, table):
        # Searching for the called function in the symbol table
        symbol_table_search_res = table.get(node.id)
        if symbol_table_search_res is None:
            self.handle_error(node.pos, 'Function \'' +
                              node.id + '\' not defined but called')
        elif not isinstance(symbol_table_search_res, symbol_table.FunctionSymbol):
            self.handle_error(node.pos, '\'' + node.id + '\' is not a function but called as function in \'' +
                              table.function.name + '\'')
        else:
            funcSymbol = symbol_table_search_res


            params_count = len(funcSymbol.params.parameters) if funcSymbol.params else 0
            if not node.args:
                pass
            else:
                if len(node.args.exprs) != params_count:
                    self.handle_error(
                        node.pos, 'Function \'' + node.id + '\' called with wrong number of arguments. Expected ' +
                                  str(params_count) + ' but got ' + str(len(node.args.exprs)) + '.')
                else:
                    for i, expr in enumerate(node.args.exprs):
                        try:
                            param = funcSymbol.params.parameters[i]
                            arg_type = self.extract_expr_type(expr, table)
                            if arg_type != param.type:
                                self.handle_error(node.pos,
                                                  'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                                  str(len(
                                                      node.args.exprs) - i) + '. expected \'' + param.type + '\' but got \'' + arg_type + '\'')
                        except Not_found:
                            pass


    def visit_BinExpr(self, node, table):
        try:
            leftExprType = self.extract_expr_type(node.left, table)
            rightExprType = self.extract_expr_type(node.right, table)

            if leftExprType == 'vector' or rightExprType == 'vector':
                self.handle_error(node.pos, 'Vector operations not supported')

            if node.op in ('*', '/', '%', '-'):
                both_are_int = (leftExprType == 'int' and rightExprType == 'int')
                if not both_are_int:
                    self.handle_error(node.pos,
                                      'Type mismatch in binary expression. *, /, %, - can only be used with numbers')
            elif node.op == '+':
                both_are_int = (leftExprType == 'int' and rightExprType == 'int')
                both_are_str = (leftExprType == 'str' and rightExprType == 'str')
                if not both_are_int and not both_are_str:
                    self.handle_error(node.pos,
                                      'Type mismatch in binary expression. + can only be used with numbers or strings')
            else:
                pass
        except Not_found:
            pass

    def visit_VariableDecl(self, node, table):
        varSymbol = None
        if node.type == 'vector':
            try:
                if node.expr:
                    rightSideExprType = self.extract_expr_type(node.expr, table)
                    if rightSideExprType != 'vector':
                        self.handle_error(node.pos,
                                          'Type mismatch in vector declaration. Expected \'vector\' but got \''
                                          + rightSideExprType + '\'')
                        # Handling error by passing vector length as zero to show more errors
                        varSymbol = symbol_table.VectorSymbol(node.id, 0)
                    else:
                        if node.expr.__class__ == AST.ExprList:
                            exprsListNode = node.expr
                            varSymbol = symbol_table.VectorSymbol(node.id, len(exprsListNode.exprs))
                        elif node.expr.__class__ == AST.FunctionCall and node.expr.id == 'list':
                            node.expr.accept(table)
                            varSymbol = symbol_table.VectorSymbol(node.id, node.expr.args.exprs[0].value)
                else:
                    self.handle_error(node.pos, 'Vector declaration without initialization')
                    varSymbol = symbol_table.VectorSymbol(node.id, 0)
            except Not_found:
                pass
        else:
            varSymbol = symbol_table.VariableSymbol(node.type, node.id, False)

        if not table.put(varSymbol):
            self.handle_error(node.pos, 'Symbol \'' + node.id + '\' of type \''
                              + node.type + '\' already defined')

        if node.expr is not None:
            if node.type != 'vector':
                varSymbol.assigned = True
                expected_type = node.type
                try:
                    given_type = self.extract_expr_type(node.expr, table)
                    if given_type != expected_type:
                        self.handle_error(node.pos,
                                          f'Type mismatch in variable declaration. Expected \'' + expected_type
                                          + '\' but got \'' + given_type + '\'')
                except Not_found:
                    pass

    def visit_Assignment(self, node, table: symbol_table.SymbolTable):
        symbol = table.get(node.id)
        if symbol is None:
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' not defined but used in assignment in function \''
                              + table.function.name + '\'')
        else:
            try:
                if isinstance(symbol, symbol_table.VariableSymbol):
                    symbol.assigned = True
                    expected_type = symbol.type
                    given_type = self.extract_expr_type(node.expr, table)
                    if given_type != expected_type:
                        self.handle_error(node.pos, f'Type mismatch in assignment. Expected \'' + expected_type
                                          + '\' but got \'' + given_type + '\'')
                    symbol.assigned = True
                elif isinstance(symbol, symbol_table.VectorSymbol):
                    rightSideExprType = self.extract_expr_type(node.expr, table)
                    if rightSideExprType != 'vector':
                        self.handle_error(node.pos, 'Type mismatch in vector assignment. Expected \'vector\' but got \''
                                          + rightSideExprType + '\'')
                    else:
                        if node.expr.__class__ == AST.ExprList:
                            exprsListNode = node.expr
                            symbol.length = len(exprsListNode.exprs)
                        elif node.expr.__class__ == AST.FunctionCall and node.expr.id == 'list':
                            node.expr.accept(table)
                            symbol.length = node.expr.args.exprs[0].value
                else:
                    self.handle_error(node.pos, 'Can not use '
                                      + symbol.__class__.__name__ + ' \'' + symbol.name + '\' in assignment')
            except Not_found:
                pass

    def visit_VectorAssignment(self, node, table):
        try:
            index_type = self.extract_expr_type(node.index_expr, table)
            if index_type != 'int':
                self.handle_error(node.pos,
                                  'Invalid index type in vector assignment. Expected \'int\' but got \'' + index_type + '\'')

            symbol = table.get(node.id)
            if symbol is None:
                self.handle_error(node.pos,
                                  'Vector \'' + node.id + '\' not defined but used in assignment in function \'' +
                                  table.function.name + '\'')
            else:
                if not isinstance(symbol, symbol_table.VectorSymbol):
                    self.handle_error(node.pos, 'Can not use '
                                      + symbol.__class__.__name__ + ' \'' + symbol.name + '\' in vector assignment')

                else:
                    # TODO Handle the vector index out of range error
                    # if node.index_expr.__class__.__name__ == 'LexToken' and node.index_expr.type == 'int':
                    #     index_expr_value = node.index_expr.value
                    # else:
                    #     index_expr_value = 1000
                    # if symbol.length <= index_expr_value or index_expr_value < 0:
                    #     self.handle_error(node.pos, 'Index out of range in vector assignment. Vector \''
                    #                       + node.id + '\' can hold only ' + str(symbol.length) + ' values')
                    rightSideExprType = self.extract_expr_type(node.expr, table)
                    if rightSideExprType != 'int':
                        self.handle_error(node.pos,
                                          'Invalid expression type in vector assignment. Vector can hold only \'int\' values but got \''
                                          + rightSideExprType + '\'' + ' in function \'' + table.function.name + '\'')
        except Not_found:
            pass

    def visit_ReturnInstruction(self, node, table):
        try:
            expected_type = table.function.rettype
            given_return_type = self.extract_expr_type(node.expr, table)
            if expected_type != given_return_type:
                self.handle_error(node.pos, f'Type mismatch in return statement. Expected \'' + expected_type
                                  + '\' but got \'' + given_return_type + '\'')
        except Not_found:
            pass

    def visit_IfOrIfElseInstruction(self, node, table):
        def is_if_with_else():
            return node.else_statement is not None

        if node.cond.__class__ == AST.Assignment:
            self.handle_error(node.pos, 'Invalid condition type in if statement')
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.if_statement, 'accept'):
            node.if_statement.accept(table)
        if is_if_with_else():
            if hasattr(node.else_statement, 'accept'):
                node.else_statement.accept(table)

    def visit_Block(self, node, table):
        child_table = symbol_table.SymbolTable(parent=table, function=table.function)
        if hasattr(node.body, 'accept'):
            node.body.accept(child_table)

    def visit_WhileInstruction(self, node, table):
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.while_statement, 'accept'):
            node.while_statement.accept(table)

    def visit_ForInstruction(self, node, table):
        try:
            if self.extract_expr_type(node.start_expr, table) != 'int':
                self.handle_error(node.pos,
                                  'Invalid expression type in for loop start range. Expected \'int\' but got \''
                                  + self.extract_expr_type(node.start_expr, table) + '\'')
            elif self.extract_expr_type(node.end_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid expression type in for loop end range. Expected \'int\' but got \''
                                  + self.extract_expr_type(node.end_expr, table) + '\'')
            if hasattr(node.for_statement, 'accept'):
                node.for_statement.accept(table)
        except Not_found:
            pass

    def visit_OperationOnList(self, node, table):
        symbol = table.get(node.expr)
        if symbol is None:
            self.handle_error(node.pos,
                              'Vector \'' + node.expr + '\' not defined but used in operation in function \'' +
                              table.function.name + '\'')
        else:
            id_type = symbol.type
            if id_type != 'vector':
                self.handle_error(node.pos, 'Identifier \' ' + node.expr + '\' expected to be \'vector\' but got \'' + "id_type" + '\'')
            try:
                if self.extract_expr_type(node.index_expr, table) != 'int':
                    self.handle_error(node.pos,
                                      'Invalid index type for \'' + symbol.name + '\'. Expected \'int\' but got \'' + self.extract_expr_type(
                                          node.index_expr, table) + '\'')
            except Not_found:
                pass

    def visit_TernaryExpr(self, node, table):
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.first_expr, 'accept'):
            node.first_expr.accept(table)
        if hasattr(node.second_expr, 'accept'):
            node.second_expr.accept(table)

    def handle_error(self, pos, msg):
        print('Semantic error at line ' + str(pos) + ': ' + msg)
