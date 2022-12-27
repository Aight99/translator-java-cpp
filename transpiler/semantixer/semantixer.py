from nltk.tree import Tree


class SemanticAnalyzer:
    def __init__(self):
        # 0 for global scope variables
        # 1 for nested if/for/while/until
        # 2 for subnested and so on
        self.current_scope = 0
        self.vars_dict = {self.current_scope: {}}

    def is_correct(self, tree: Tree):
        result = True
        for subtree in tree:
            if type(subtree) == Tree:
                if subtree.label() == '<variable_declaration>':
                    self.save_var(subtree[0, 0], subtree[1, 0])
                result = result and self.is_correct(subtree)
        return result

    def save_var(self, var_type, var_id):
        scoped_vars = self.vars_dict.get(self.current_scope)
        print(scoped_vars)
        scoped_vars[var_type] = var_id
        self.vars_dict[self.current_scope] = scoped_vars

    def get_tree_labels(self, tree: Tree, margin=0):
        result = ''
        for subtree in tree:
            if type(subtree) == Tree:
                result += f'{"|  " * margin} {subtree.label()}\n{self.get_tree_labels(subtree, margin + 1)}'
        return result
