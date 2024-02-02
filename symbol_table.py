builtin_method = ['scan', 'print', 'list', 'length', 'exit']


class Symbol(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<{name}>'.format(name=self.name)


class VariableSymbol(Symbol):

    def __init__(self, type, name, assigned):
        super(VariableSymbol, self).__init__(name)
        self.type = type
        self.assigned = assigned
        self.register = None

    def set_register(self, register):
        self.register = register


class VectorSymbol(Symbol):
    def __init__(self, name, length):
        super(VectorSymbol, self).__init__(name)
        self.length = length
        self.type = 'vector'


class FunctionSymbol(Symbol):
    redefined = False

    def __init__(self, rettype, name, params):
        super(FunctionSymbol, self).__init__(name)
        self.rettype = rettype
        self.params = params

    def __str__(self):
        return '<{name} : {rettype}({params})>'.format(name=self.name, rettype=self.rettype, params=self.params)


class SymbolTable(object):

    def __init__(self, parent, function):
        self.parent = parent
        self.function = function
        self.table = dict()

    def put(self, symbol):
        if not symbol.name in self.table:
            self.table[symbol.name] = symbol
            return True
        return False

    def mark_as_defined(self, key):
        self.table[key].redefined = True

    def get(self, name, current_scope=False):
        symbol = self.table.get(name)
        if symbol is not None:
            return symbol
        elif not current_scope and self.getParent() is not None:
            return self.getParent().get(name)
        return symbol

    def getTable(self):
        return self.table

    def getParent(self):
        return self.parent

    def print_symbols(self):
        for key in self.table:
            print(key, self.table[key])
