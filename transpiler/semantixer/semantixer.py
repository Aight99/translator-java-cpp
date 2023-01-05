from enum import IntEnum
from nltk.tree import Tree

from transpiler.base import TranspilerError, Token
from transpiler.constants import KEYWORDS, Label, FUNCTIONS


class SemanticError(TranspilerError):
    pass


def is_correct_name(name):
    if type(name) == Token:
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
            assert new_func != func, f'Функция {new_func.id} уже была объявлена ранее'
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
                func_id = subtree[0].value
                assert is_correct_name(func_id), f'Использовано ключевое слово для идентификатора {func_id} {subtree}'
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
                param_id = subtree[1, 0]
                param_type = subtree[0, 0]
                assert is_correct_name(param_id), f'Использовано ключевое слово для идентификатора {param_id} {subtree}'
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

    def is_correct(self, func: Function):
        self.vars_dict[self.current_scope] = func.params
        self.returns_dict[self.current_scope] = False
        self.func = func

        result = self.__is_correct_code(func.code)
        if func.type != Type.NONE:
            assert self.returns_dict[0] == True, f'Отсутствует выражение с return для функции {func.id}'
        return result

    def __is_correct_code(self, tree: Tree):
        result = True
        for subtree in tree:
            if type(subtree) == Tree:
                match subtree.label():
                    case Label.INSTRUCTION:
                        assert self.returns_dict[self.current_scope] != True, f'Недостижимый фрагмент кода'

                    case Label.ASSIGNMENT:
                        tree_parts = [tree for tree in subtree]
                        var_id = subtree[0, 0]
                        var_type = self.__get_id_type(var_id)
                        if len(tree_parts) == 3:
                            assign = subtree[1]
                            assert var_type != Type.NONE, f'Переменная {var_id} не объявлена в окружении {self.current_scope}'
                            if assign.label() != Label.ASSIGN:
                                assert var_type != Type.BOOLEAN, f'Присваивание с операцией недопустимо для типа {var_type.name}'
                            expr = subtree[2, 0]
                            self.__check_expr(var_type, expr)
                        else:
                            assert var_type != Type.BOOLEAN, f'Инкремент и декремент недопустим для типа {var_type.name}'
                            assert self.__get_var(var_id).is_initialized, f'Переменная {var_id} не инициализирована'

                    case Label.VAR_DECL:
                        var_id = subtree[1, 0]
                        var_type = subtree[0, 0]
                        assert is_correct_name(
                            var_id), f'Использовано ключевое слово для идентификатора {var_id} {subtree}'
                        self.__save_var(var_id, var_type)
                        if len([elem for elem in subtree]) > 2:
                            var = self.__get_var(var_id)
                            var.init()
                            var_type = var.type
                            expr = subtree[3, 0]
                            self.__check_expr(var_type, expr)

                        for key, value in self.vars_dict.items():
                            print(key)
                            for var in value:
                                print(var)

                    case Label.FUNC_CALL:
                        self.__check_func_call(subtree)

                    case Label.FUNC_RETURN:
                        func_type = self.func.type
                        assert func_type != Type.NONE, f'Функция {self.func.id} не может возвращать значения'
                        self.returns_dict[self.current_scope] = True
                        expr = subtree[1, 0]
                        self.__check_expr(func_type, expr)

                    case Label.LBRACKET_CURLY:
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
        for var_exists in self.vars_dict[self.current_scope]:
            if var_exists == var:
                is_var_exists = True
        assert not is_var_exists, f'Переменная {var} уже объявлена'
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
                    var_id = label_tree[0]
                    id_type = self.__get_id_type(var_id)
                    assert self.__get_var(var_id).is_initialized, f'Переменная {var_id} не инициализирована'
                    assert id_type != Type.NONE, f'Переменная {var_id} не объявлена в окружении {self.current_scope}'
                    assert id_type != Type.BOOLEAN, f'Переменная {var_id} типа boolean не может участвовать в математическом выражении'
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
        func_id = tree[0, 0].value
        expressions = self.__get_func_call_params_expressions(tree)
        functions = [func for func in self.func_list if func.id == func_id and len(func.params) == len(expressions)]
        return functions[0].type

    def __check_expr(self, needed_type, expr):
        match expr.label():
            case Label.LOGICAL_EXPR:
                assert needed_type == Type.BOOLEAN, f'Возвращаемое значение не соответствует требуемому типу {needed_type.name}'
            case Label.MATH_EXPR:
                assert needed_type >= self.__get_math_expr_type(
                    expr), f'Возвращаемое значение не соответствует требуемому типу {needed_type.name}'
            case Label.CHAR:
                assert needed_type >= Type.CHAR, f'Возвращаемое значение не соответствует требуемому типу {needed_type.name}'
            case Label.ID:
                assert needed_type >= self.__get_id_type(
                    expr[0]), f'Возвращаемое значение не соответствует требуемому типу {needed_type.name}'
            case Label.FUNC_CALL:
                self.__check_func_call(expr)
                assert needed_type >= self.__get_func_type(
                    expr), f'Возвращаемое значение не соответствует требуемому типу {needed_type.name}'

    def __check_func_call(self, tree):
        func_id = tree[0, 0].value
        expressions = self.__get_func_call_params_expressions(tree)
        functions = [func for func in self.func_list if func.id == func_id and len(func.params) == len(expressions)]
        assert functions != [] or func_id in FUNCTIONS, f'Функция {func_id} не объявлена'
        for param, expr in zip(functions[0].params, expressions):
            self.__check_expr(param.type, expr)
