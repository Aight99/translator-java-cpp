from enum import Enum, IntEnum
from nltk.tree import Tree

from transpiler.base import Token
from transpiler.constants import KEYWORDS, Label


class ErrorMessage(Enum):
    @staticmethod
    def func_multiple_decl(func_id):
        return f'function {func_id} already declared'

    @staticmethod
    def id_keyword(var_id):
        return f'identifier keyword used {var_id}'

    @staticmethod
    def return_not_exists(func_id):
        return f'missing expression with return for function {func_id}'

    @staticmethod
    def unreachable_code():
        return f'unreachable code snippet'

    @staticmethod
    def var_no_decl(var_id):
        return f'variable {var_id} is not declared'

    @staticmethod
    def boolean_op_assign():
        return f'assignment with operation is not allowed for type boolean'

    @staticmethod
    def boolean_increment():
        return f'increment and decrement is invalid for type boolean'

    @staticmethod
    def var_no_init(var_id):
        return f'variable  {var_id} is not initialized'

    @staticmethod
    def func_void_return(func_id):
        return f'function {func_id} cannot return values'

    @staticmethod
    def var_multiple_decl(var_id):
        return f'variable {var_id} is already declared'

    @staticmethod
    def boolean_var_math_expr(var_id):
        return f'boolean type variable {var_id} cannot participate in a mathematical expression'

    @staticmethod
    def types_not_fit(return_type, needed_type):
        return f'return value {return_type} does not match the required type {needed_type}'

    @staticmethod
    def func_no_decl(func_id):
        return f'function {func_id} is not declared'

    @staticmethod
    def func_params_mismatch(func_id):
        return f'parameters do not match the function {func_id}'


class SemanticError(Exception):
    def __init__(self, line, description, message="semantic error in string "):
        self.line = line
        self.message = message
        self.description = description
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} {self.line}: {self.description}'


def is_correct_name(name):
    if type(name) != str:
        name = name.value
    if name in KEYWORDS:
        return False
    return True


def get_tree(tree: Tree, margin=0):
    result = ''
    for subtree in tree:
        if type(subtree) == Tree:
            result += f'{"|  " * margin} {subtree.label()}\n{get_tree(subtree, margin + 1)}'
        else:
            result += f'{"|  " * margin} {subtree}\n'
    return result


class SemanticAnalyzer:
    def __init__(self):
        self.func_list = []
        self.main_func = None

    def is_correct(self, tree: Tree):
        result = True
        self.__find_func(tree)

        func_analyzer = FunctionAnalyzer(self.func_list)
        for func in self.func_list:
            result = result and func_analyzer.is_correct(func)

        return result and func_analyzer.is_correct(self.main_func)

    def __find_func(self, tree):
        for subtree in tree:
            if subtree.label() == Label.FUNC_DECL:
                self.__save_func(subtree)
                self.__find_func(subtree)
            elif subtree.label() == Label.MAIN_FUNC:
                self.main_func = Function(subtree)

    def __save_func(self, tree):
        new_func = Function(tree)
        for func in self.func_list:
            if new_func == func:
                raise SemanticError(tree[0, 0].line, ErrorMessage.func_multiple_decl(new_func.id))
        self.func_list.append(new_func)


class Type(IntEnum):
    NONE = -1
    BOOLEAN = 0
    CHAR = 1
    INT = 2
    FLOAT = 3
    DOUBLE = 4


class Function:
    def __init__(self, tree):
        self.tree = tree
        self.id = self.__find_id()
        self.type = self.__find_type()
        self.params = self.__find_params(tree)
        self.code = self.__find_code()

    def __find_id(self):
        func_id = 'main'
        for subtree in self.tree:
            if subtree.label() == Label.ID:
                func_id = subtree[0, 0].value
                if not is_correct_name(func_id):
                    raise SemanticError(subtree[0].line, ErrorMessage.id_keyword(func_id))
        return func_id

    def __find_type(self):
        for subtree in self.tree:
            if subtree.label() == Label.FUNC_TYPE:
                return get_type(subtree[0][0].value)
        return Type.NONE

    def __find_params(self, tree):
        params = []
        for subtree in tree:
            if subtree.label() == Label.FUNC_PARAMS:
                param_id = subtree[1, 0, 0]
                param_type = subtree[0, 0]
                if not is_correct_name(param_id):
                    raise SemanticError(param_id.line, ErrorMessage.id_keyword(param_id))
                param = Variable(param_id, param_type, True)
                params.append(param)
                return params + self.__find_params(subtree)
        return params

    def __find_code(self):
        for subtree in self.tree:
            if subtree.label() == Label.CODE_BLOCK:
                return subtree

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id \
            and len(self.params) == len(other.params)

    def __str__(self):
        return f'Function: {self.id}\nType: {self.type}\nParameters: {self.params}\n'


class Variable:
    def __init__(self, var_id, var_type, is_initialized=False):
        self.id = var_id
        self.type = get_type(var_type.value)
        self.is_initialized = is_initialized

    def init(self):
        self.is_initialized = True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id.value == other.id.value \
            and self.type.value == other.type.value

    def __str__(self):
        return f'Variable: {self.id.value}\nType: {self.type.value}\nInitialized: {self.is_initialized}'


def get_type(type):
    match type:
        case 'boolean':
            return Type.BOOLEAN
        case 'char':
            return Type.CHAR
        case 'int':
            return Type.INT
        case 'float':
            return Type.FLOAT
        case 'double':
            return Type.DOUBLE
        case _:
            return Type.NONE


class FunctionAnalyzer:
    def __init__(self, func_list):
        # 0 for global scope variables
        # 1+ for nested {}
        self.func = None
        self.current_scope = 0
        self.func_list = func_list
        self.vars_dict = {}
        self.returns_dict = {}
        self.is_for_loop = False

    def is_correct(self, func: Function):
        self.vars_dict[self.current_scope] = func.params
        self.returns_dict[self.current_scope] = False
        self.func = func

        result = self.__is_correct_code(func.code)
        if func.type != Type.NONE:
            if not self.returns_dict[0]:
                raise SemanticError(func.tree[0, 0].line, ErrorMessage.return_not_exists(func.id))
        return result

    def __find_token(self, tree: Tree):
        for subtree in tree:
            if type(subtree) == Token:
                return subtree
            else:
                return self.__find_token(subtree)

    def __is_correct_code(self, tree: Tree):
        result = True
        for subtree in tree:
            if type(subtree) == Tree:
                match subtree.label():
                    case Label.INSTRUCTION:
                        var_token = self.__find_token(subtree)
                        if self.returns_dict[self.current_scope]:
                            raise SemanticError(var_token.line, ErrorMessage.unreachable_code())

                    case Label.ASSIGNMENT:
                        tree_parts_num = 0
                        var_id = None
                        for tree in subtree:
                            if tree.label() == Label.ID:
                                var_id = tree[0, 0]
                            tree_parts_num += 1
                        var_type = self.__get_id_type(var_id)

                        if var_type == Type.NONE:
                            raise SemanticError(var_id.line, ErrorMessage.var_no_decl(var_id))

                        if tree_parts_num == 3:
                            assign = subtree[1]
                            if assign.label() != Label.ASSIGN:
                                if not self.__get_var(var_id).is_initialized:
                                    raise SemanticError(var_id.line, ErrorMessage.var_no_init(var_id))
                                if var_type == Type.BOOLEAN:
                                    raise SemanticError(var_id.line, ErrorMessage.boolean_op_assign())
                            expr = subtree[2, 0]
                            self.__check_expr(var_type, expr, var_id.line)

                        # Случай инкремента и декремента
                        else:
                            if var_type == Type.BOOLEAN:
                                raise SemanticError(var_id.line, ErrorMessage.boolean_increment())
                            if not self.__get_var(var_id).is_initialized:
                                raise SemanticError(var_id.line, ErrorMessage.var_no_init(var_id))

                    case Label.VAR_DECL:
                        var_id = subtree[1, 0, 0]
                        var_type = subtree[0, 0]
                        if not is_correct_name(var_id):
                            raise SemanticError(var_id.line, ErrorMessage.id_keyword(var_id))
                        self.__save_var(var_id, var_type)
                        if len([elem for elem in subtree]) > 2:
                            var = self.__get_var(var_id)
                            var.init()
                            var_type = var.type
                            expr = subtree[3, 0]
                            self.__check_expr(var_type, expr, var.id.line)

                        # for key, value in self.vars_dict.items():
                        #     print(key)
                        #     for var in value:
                        #         print(var)

                    case Label.FUNC_CALL:
                        self.__check_func_call(subtree)

                    case Label.FUNC_RETURN:
                        func_type = self.func.type
                        if func_type == Type.NONE:
                            raise SemanticError(subtree[0, 0].line, ErrorMessage.func_void_return(self.func.id))
                        self.returns_dict[self.current_scope] = True
                        expr = subtree[1, 0]
                        self.__check_expr(func_type, expr, subtree[0, 0].line)

                    case Label.FOR:
                        self.current_scope += 1
                        self.vars_dict[self.current_scope] = []
                        self.returns_dict[self.current_scope] = False
                        self.is_for_loop = True

                    case Label.LBRACKET_CURLY:
                        if self.is_for_loop:
                            self.is_for_loop = False
                        else:
                            self.current_scope += 1
                            self.vars_dict[self.current_scope] = []
                            self.returns_dict[self.current_scope] = False

                    case Label.RBRACKET_CURLY:
                        self.vars_dict.pop(self.current_scope, None)
                        self.returns_dict.pop(self.current_scope, None)
                        self.current_scope -= 1

                result = result and self.__is_correct_code(subtree)
        return result

    def __save_var(self, var_id, var_type, is_initialized=False):
        var = Variable(var_id, var_type)
        var.is_initialized = is_initialized
        is_var_exists = False
        for scope in range(self.current_scope + 1):
            for var_exists in self.vars_dict[scope]:
                if var_exists == var:
                    is_var_exists = True
        if is_var_exists:
            raise SemanticError(var_id.line, ErrorMessage.var_multiple_decl(var.id))
        self.vars_dict[self.current_scope].append(var)

    def __get_math_expr_type(self, tree):
        max_type = Type.NONE
        for subtree in tree:
            if subtree.label() == Label.MATH_EXPR:
                max_type = max(max_type, self.__get_math_expr_type(subtree))
        if max_type == Type.NONE:
            label_tree = tree[0]
            match label_tree.label():
                case Label.NUMBER:
                    type_tree = label_tree[0]
                    if type_tree.label() == Label.NUMBER_INT:
                        return Type.INT
                    else:
                        return Type.DOUBLE
                case Label.FUNC_CALL:
                    self.__check_func_call(label_tree)
                    return self.__get_func_type(label_tree)
                case Label.CHAR:
                    return Type.CHAR
                case Label.ID:
                    var_id = label_tree[0, 0]
                    id_type = self.__get_id_type(var_id)
                    if not self.__get_var(var_id).is_initialized:
                        raise SemanticError(var_id.line, ErrorMessage.var_no_init(var_id))
                    if id_type == Type.NONE:
                        raise SemanticError(var_id.line, ErrorMessage.var_no_decl(var_id))
                    if id_type == Type.BOOLEAN:
                        raise SemanticError(var_id.line, ErrorMessage.boolean_var_math_expr(var_id))
                    return id_type
        return max_type

    def __get_var(self, var_id):
        for scope in range(0, self.current_scope + 1):
            for var in self.vars_dict[scope]:
                if var_id.value == var.id.value:
                    return var
        return None

    def __get_id_type(self, var_id):
        id_type = Type.NONE
        var = self.__get_var(var_id)
        if var is not None:
            id_type = var.type
        return id_type

    def __get_func_call_params_expressions(self, tree):
        expressions = []
        for subtree in tree:
            if subtree.label() == Label.FUNC_CALL_PARAMS:
                expr = subtree[0, 0]
                expressions.append(expr)
                expressions += self.__get_func_call_params_expressions(subtree)
        return expressions

    def __get_func_type(self, tree):
        func_id = tree[0, 0, 0].value
        expressions = self.__get_func_call_params_expressions(tree)
        functions = [func for func in self.func_list if func.id == func_id and len(func.params) == len(expressions)]
        return functions[0].type

    def __check_expr(self, needed_type, expr, line):
        match expr.label():
            case Label.LOGICAL_EXPR:
                if needed_type != Type.BOOLEAN:
                    raise SemanticError(line, ErrorMessage.types_not_fit(Type.BOOLEAN.name, needed_type.name))
            case Label.MATH_EXPR:
                return_type = self.__get_math_expr_type(expr)
                if needed_type < return_type:
                    raise SemanticError(line, ErrorMessage.types_not_fit(return_type.name, needed_type.name))
            case Label.CHAR:
                if needed_type < Type.CHAR:
                    raise SemanticError(line, ErrorMessage.types_not_fit(Type.CHAR.name, needed_type.name))
            case Label.ID:
                var_id = expr[0, 0]
                return_type = self.__get_id_type(var_id)
                if not self.__get_var(var_id).is_initialized:
                    raise SemanticError(var_id.line, ErrorMessage.var_no_init(var_id))
                if needed_type < return_type:
                    raise SemanticError(line, ErrorMessage.types_not_fit(return_type.name, needed_type.name))
            case Label.FUNC_CALL:
                self.__check_func_call(expr)
                return_type = self.__get_func_type(expr)
                if needed_type < return_type:
                    raise SemanticError(line, ErrorMessage.types_not_fit(return_type.name, needed_type.name))

    def __check_func_call(self, tree):
        param_expressions = self.__get_func_call_params_expressions(tree)
        func_label = tree[0].label()
        if func_label in [Label.PRINT, Label.MAX, Label.MIN]:
            func_token = tree[0, 0]
            func_id = func_token.value
            if func_label == Label.PRINT:
                if len(param_expressions) != 1:
                    raise SemanticError(func_token.line, ErrorMessage.func_params_mismatch(func_id))
                # проверка параметров
            else:
                if len(param_expressions) != 2:
                    raise SemanticError(func_token.line, ErrorMessage.func_params_mismatch(func_id))
                # проверка параметров
        else:
            func_token = tree[0, 0, 0]
            func_id = func_token.value
            functions = [func for func in self.func_list if
                         func.id == func_id and len(func.params) == len(param_expressions)]
            if not functions:
                raise SemanticError(func_token.line, ErrorMessage.func_no_decl(func_id))
            for param, expr in zip(functions[0].params, param_expressions):
                self.__check_expr(param.type, expr, func_token.line)
