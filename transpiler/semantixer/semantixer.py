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
                return subtree[0][0]

    def __find_params(self, tree):
        params = []
        for subtree in tree:
            if subtree.label() == Label.FUNC_PARAMS:
                param_id = subtree[1, 0]
                param_type = subtree[0, 0]
                assert is_correct_name(param_id), f'Использовано ключевое слово для идентификатора {param_id} {subtree}'
                param = Variable(param_id, param_type)
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
            and self.type.value == other.type.value \
            and self.params == other.params

    def __str__(self):
        return f'Function: {self.id}\nType: {self.type}\nParameters: {self.params}\n'


class Variable:
    def __init__(self, var_id, var_type):
        self.id = var_id
        self.type = var_type
        self.is_initialized = False

    def init(self):
        self.is_initialized = True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id.value == other.id.value \
            and self.type.value == other.type.value

    def __str__(self):
        return f'Variable: {self.id.value}\nType: {self.type.value}\nInitialized: {self.is_initialized}'


class FunctionAnalyzer:
    def __init__(self, func_list):
        # 0 for global scope variables
        # 1.. for nested if/for/while
        self.current_scope = 0
        self.func_list = func_list
        self.vars_dict = {}

    def is_correct(self, func: Function):
        self.vars_dict[self.current_scope] = func.params
        return self.__is_correct_code(func.code)

    def __is_correct_code(self, tree: Tree):
        result = True
        for subtree in tree:
            if type(subtree) == Tree:
                match subtree.label():
                    case Label.ASSIGNMENT:
                        var_id = subtree[0]
                        if var_id.label() != Label.ID:
                            var_id = subtree[1, 0]
                        else:
                            var_id = subtree[0, 0]
                        assert self.__is_var_exists(
                            var_id), f'Переменная {var_id} не объявлена в окружении {self.current_scope}'

                        # Проверка соответствия типов

                    case Label.VAR_DECL:
                        var_id = subtree[1, 0]
                        var_type = subtree[0, 0]
                        assert is_correct_name(
                            var_id), f'Использовано ключевое слово для идентификатора {var_id} {subtree}'
                        self.__save_var(var_id, var_type)

                        for key, var_list in self.vars_dict.items():
                            print(key)
                            for var in var_list:
                                print(var)

                        # Проверка присваивания

                    case Label.FUNC_CALL:
                        func_id = subtree[0, 0].value
                        functions = [func for func in self.func_list if func.id == func_id]
                        assert functions != [] or func_id in FUNCTIONS, f'Функция {func_id} не объявлена'
                        # func_params = self.__find_func_params(subtree)

                        # Проверять аргументы и типы

                    case Label.FUNC_RETURN:
                        pass

                    case Label.LBRACKET_CURLY:
                        self.current_scope += 1
                        self.vars_dict[self.current_scope] = {}

                    case Label.RBRACKET_CURLY:
                        self.vars_dict.pop(self.current_scope)
                        self.current_scope -= 1

                result = result and self.__is_correct_code(subtree)
        return result

    def __save_var(self, var_id, var_type):
        var = Variable(var_id, var_type)
        is_var_exists = False
        for var_exists in self.vars_dict[self.current_scope]:
            if var_exists == var:
                is_var_exists = True
        assert not is_var_exists, f'Переменная {var} уже объявлена'
        self.vars_dict[self.current_scope].append(var)

    def __is_var_exists(self, var_id):
        for scope in range(0, self.current_scope + 1):
            if var_id.value in [var_exists.id.value for var_exists in self.vars_dict[scope]]:
                return True
        return False

    # def __find_func_params(self, tree):
    #     for subtree in tree:
    #         if subtree.label() == Label.FUNC_CALL_PARAMS:
