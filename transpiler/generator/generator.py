import nltk
from nltk.tree import Tree


class Generator:
    def __init__(self):
        self.code = ''

    def _formatize_token(self, token):
        formatized_token = token
        match token:
            # tokens with line break after
            case ';' | '}':
                formatized_token = token + '\n'
            # tokens with line break before and after
            case '{':
                formatized_token = '\n' + token + '\n'
            # Java print token to C++ print
            case 'System.out.println':
                formatized_token = 'std::cout'
            # Java max token to C++ max
            case 'Math.max':
                formatized_token = 'std::max'
            # Java min token to C++ min
            case 'Math.min':
                formatized_token = 'std::min'
            # Java boolean token to C++ bool
            case 'boolean':
                formatized_token = 'bool '
            # tokens with a space after
            case 'int' | 'float' | 'double' | 'char' | ',':
                formatized_token = token + ' '
            # tokens with a space before and after
            case '<' | '>' | '<=' | '<=' | '==' | '!=' | \
                 '||' | '&&' | \
                 '+' | '-' | '*' | '/' | '%' | '=':
                formatized_token = ' ' + token + ' '
            # all other tokens
        return formatized_token

    def __get_func_return_type(self, func_tree: nltk.Tree):
        for subtree in func_tree.subtrees():
            if subtree.label() == '<func_return_type>':
                return str(subtree.leaves()[0])

    def __get_func_id(self, func_tree: nltk.Tree):
        for subtree in func_tree.subtrees():
            if subtree.label() == '<id>':
                return str(subtree.leaves()[0])

    def __get_func_params(self, func_tree: nltk.Tree):
        params_string = ''
        for subtree in func_tree.subtrees():
            if subtree.label() == '<function_params>':
                for leaf in subtree.leaves():
                    params_string += self._formatize_token(str(leaf))
                break
        return params_string

    def __get_func_code(self, func_tree: nltk.Tree):
        func_name = ''
        func_in_print = False
        func_code_string = ''
        for subtree in func_tree.subtrees():
            if subtree.label() == '<code_block>':
                for leaf in subtree.leaves():
                    leaf_value = str(leaf)
                    match func_name:
                        case 'print':
                            if not func_in_print:
                                if leaf_value != '(' and leaf_value != ',' and leaf_value != ')' \
                                        and leaf_value != 'Math.max' and leaf_value != 'Math.min':
                                    func_code_string += ' << ' + leaf_value + ''
                                elif leaf_value == ')':
                                    func_code_string += ' << "\\n"'
                                    func_name = ''
                                elif leaf_value == 'Math.max':
                                    func_code_string += ' << ' + 'std::max'
                                    func_in_print = True
                                elif leaf_value == 'Math.min':
                                    func_code_string += ' << ' + 'std::min'
                                    func_in_print = True
                            else:
                                if leaf_value == ')':
                                    func_in_print = False
                                func_code_string += self._formatize_token(leaf_value)
                        case _:
                            if leaf_value == 'System.out.println':
                                func_name = 'print'
                            func_code_string += self._formatize_token(leaf_value)
                return func_code_string

    def __generate_main(self, main_tree: nltk.Tree):
        func_string = 'void main(int argc, char *argv[])\n'
        func_string += '{\n'
        func_string += self.__get_func_code(main_tree)
        func_string += '}\n'
        return func_string

    def __generate_function(self, func_tree: nltk.Tree):
        func_string = ''
        func_string += self.__get_func_return_type(func_tree) + ' '
        func_string += self.__get_func_id(func_tree)
        func_string += '(' + self.__get_func_params(func_tree) + ')\n'
        func_string += '{\n'
        func_string += self.__get_func_code(func_tree)
        func_string += '}\n'
        return func_string

    def generate_code(self, tree: nltk.Tree):
        self.code += '#include <iostream>\n\n'
        for subtree in tree:
            if subtree.label() == '<func_declaration>':
                for func_subtree in subtree.subtrees():
                    if func_subtree.label() == '<func_declaration>':
                        self.code += self.__generate_function(func_subtree) + '\n'
            elif subtree.label() == '<main_func>':
                self.code += self.__generate_main(subtree)
        return self.code
