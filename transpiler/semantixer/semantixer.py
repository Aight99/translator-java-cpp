from nltk.tree import Tree

from transpiler.base import TranspilerError
from transpiler.constants import KEYWORDS, Label


class SemanticError(TranspilerError):
    pass


def is_correct_name(name):
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
        for subtree in tree:
            if subtree.label() == Label.FUNC_DECL:
                self.__save_func(subtree)
            elif subtree.label() == Label.MAIN_FUNC:
                self.main_func = Function(subtree)

        func_analyzer = FunctionAnalyzer(self.func_list)
        for func in self.func_list:
            result = result and func_analyzer.is_correct(func)

        return result and func_analyzer.is_correct(self.main_func)

    def __save_func(self, tree):
        func = Function(tree)
        self.func_list.append(func)


class Function:
    def __init__(self, tree):
        self.tree = tree
        self.id = self.__find_id()
        self.type = self.__find_type()
        self.params = self.__find_params(tree)
        self.code = self.__find_code()

    def __find_id(self):
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
        params = {}
        for subtree in tree:
            if subtree.label() == Label.FUNC_PARAMS:
                param_id = subtree[1, 0].value
                param_type = subtree[0, 0].value
                assert is_correct_name(param_id), f'Использовано ключевое слово для идентификатора {param_id} {subtree}'
                params[param_id] = param_type
                return params | self.__find_params(subtree)
        return params

    def __find_code(self):
        for subtree in self.tree:
            if subtree.label() == Label.CODE_BLOCK:
                return subtree

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id \
            and self.type == other.type \
            and self.params == other.params

    def __str__(self):
        return f'Function: {self.id}\nType: {self.type}\nParameters: {self.params}\n'


class FunctionAnalyzer:
    def __init__(self, func_list):
        # 0 for global scope variables
        # 1 for nested if/for/while/until
        # 2 for subnested and so on
        self.current_scope = 0
        self.func_list = func_list
        self.vars_dict = {}

    def is_correct(self, func: Function):
        result = True
        self.vars_dict[self.current_scope] = func.params
        return self.__is_correct_code(func.code)

    def __is_correct_code(self, tree: Tree):
        result = True
        for subtree in tree:
            if type(subtree) == Tree:
                if subtree.label() == Label.VAR_DECL:
                    var_id = subtree[1, 0]
                    var_type = subtree[0, 0]
                    assert is_correct_name(var_id), f'Использовано ключевое слово для идентификатора {var_id} {subtree}'
                    self.__save_var(var_id, var_type)
                result = result and self.__is_correct_code(subtree)
        return result

    def __save_var(self, var_type, var_id):
        scoped_vars = self.vars_dict.get(self.current_scope)
        scoped_vars[var_type] = var_id
        self.vars_dict[self.current_scope] = scoped_vars
