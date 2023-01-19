import nltk
from nltk.tree import Tree


class Generator:
    def __init__(self):
        self.code = ''

    def _formatize_token(self, token, tab_num):
        formatized_token = token
        match token:
            # tokens with line break after
            case ';' | '}':
                formatized_token = token + '\n'
                for i in range(tab_num):
                    formatized_token += '    '
            # tokens with line break before and after
            case '{':
                formatized_token = '\n'
                for i in range(tab_num - 1):
                    formatized_token += '    '
                formatized_token += token + '\n'
                for i in range(tab_num):
                    formatized_token += '    '
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
            case 'int' | 'float' | 'double' | 'char' | ',' | 'return' | 'while' | 'for' | 'if':
                formatized_token = token + ' '
            # tokens with a space before and after
            case '<' | '>' | '<=' | '>=' | '==' | '!=' | \
                 '||' | '&&' | \
                 '+' | '-' | '*' | '/' | '%' | '=' | \
                 '+=' | '-=' | '*=' | '/=' | '%=':
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
        i = 0
        for subtree in func_tree.subtrees():
            if subtree.label() == '<function_params>':
                for leaf in subtree.leaves():
                    params_string += self._formatize_token(str(leaf), 0)
                break
            elif subtree.label() == '<func_declaration>' and i > 0:
                break
            i = i + 1
        return params_string

    def __get_func_code(self, func_tree: nltk.Tree):
        func_name = ''
        bracket_stack = []
        tab_stack = ['']
        func_code_string = '    '
        for subtree in func_tree.subtrees():
            if subtree.label() == '<code_block>':
                leaves = subtree.leaves()
                for i in range(len(leaves)):
                    leaf = leaves[i]
                    leaf_value = str(leaf)
                    # if token is '{' then add tab
                    if leaf_value == '{':
                        tab_stack.append('')
                    # if next token is '}' pop tab
                    elif i + 1 < len(leaves) and str(leaves[i+1]) == '}':
                        if len(tab_stack) > 0:
                            tab_stack.pop()
                    # if token is last pop tab (stack will be empty)
                    elif i + 1 == len(leaves):
                        tab_stack.pop()
                    match func_name:
                        # if token in println
                        case 'print':
                            # if token is inside println
                            if len(bracket_stack) > 0:
                                if leaf_value == '(':
                                    bracket_stack.append('')
                                elif leaf_value == ')':
                                    bracket_stack.pop()
                                if len(bracket_stack) > 0:
                                    func_code_string += self._formatize_token(leaf_value, len(tab_stack))
                            # if token is the start or end of println
                            else:
                                if leaf_value == '(':
                                    bracket_stack.append('')
                                    func_code_string += ' << '
                                elif leaf_value == ';':
                                    func_name = ''
                                    func_code_string += ' << "\\n"' + self._formatize_token(leaf_value, len(tab_stack))
                        # if token in for loop (to fix line-break after ';')
                        case 'for':
                            # if token is inside for loop
                            if len(bracket_stack) > 0:
                                if leaf_value == '(':
                                    bracket_stack.append('')
                                    func_code_string += '('
                                elif leaf_value == ')':
                                    bracket_stack.pop()
                                    func_code_string += ')'
                                elif leaf_value == ';':
                                    func_code_string += '; '
                                else:
                                    func_code_string += self._formatize_token(leaf_value, len(tab_stack))
                            # if token is the start or end of for loop
                            else:
                                if leaf_value == '(':
                                    bracket_stack.append('')
                                elif leaf_value == '{':
                                    func_name = ''
                                func_code_string += self._formatize_token(leaf_value, len(tab_stack))
                        case _:
                            if leaf_value == 'System.out.println':
                                func_name = 'print'
                            elif leaf_value == 'for':
                                func_name = 'for'
                            func_code_string += self._formatize_token(leaf_value, len(tab_stack))
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
