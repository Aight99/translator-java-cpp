from collections import defaultdict
from nltk.tree import Tree


class SyntaxAnalyzerError(Exception):

    def __init__(self, line, message="syntax error at line "):
        self.line = line
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} {self.line}'


class Rule:
    """
    lhs -> rhs
    rhs = [...]
    """

    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs

    def __eq__(self, other):
        if type(other) is Rule:
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __getitem__(self, i):
        return self.rhs[i]

    def __len__(self):
        return len(self.rhs)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.lhs + ' -> ' + ' '.join(self.rhs)


class Grammar:

    def __init__(self):
        self.rules = defaultdict(list)

    def add(self, rule):
        self.rules[rule.lhs].append(rule)

    @staticmethod
    def load_grammar(fpath):
        grammar = Grammar()
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    continue
                entries = line.split('->')
                lhs = entries[0].strip()
                for rhs in entries[1].split(' | '):
                    grammar.add(Rule(lhs, rhs.strip().split()))
        return grammar

    @staticmethod
    def get_starting_non_terminal():
        return '<program>'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        start = self.get_starting_non_terminal()
        s = [str(r) for r in self.rules[start]]

        for nt, rule_list in self.rules.items():
            if nt == start:
                continue
            s += [str(r) for r in rule_list]
        return '\n'.join(s)

    # Returns the rules for a given Non-terminal.
    def __getitem__(self, nt):
        return self.rules[nt]

    def is_terminal(self, symbol):
        return len(self.rules[symbol]) == 0

    def is_tag(self, symbol):
        if not self.is_terminal(symbol):
            return all(self.is_terminal(s) for r in self.rules[symbol] for s in r.rhs)
        return False


class EarleyState:

    START = '<START>'

    def __init__(self, rule, dot=0, sent_pos=0, chart_pos=0, back_pointers=None):
        if back_pointers is None:
            back_pointers = []
        self.rule = rule
        self.dot_position = dot
        self.sentence_position = sent_pos
        self.chart_index = chart_pos
        self.back_pointers = back_pointers

    def __eq__(self, other):
        if type(other) is EarleyState:
            return self.rule == other.rule and self.dot_position == other.dot_position and \
                   self.sentence_position == other.sentence_position
        return False

    def __len__(self):
        return len(self.rule)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        def str_helper(state):
            return ('(' + state.rule.lhs + ' -> ' +
                    ' '.join(state.rule.rhs[:state.dot_position] + ['*'] +
                             state.rule.rhs[state.dot_position:]) +
                    (', [%d, %d])' % (state.sentence_position, state.chart_index)))

        return (str_helper(self) +
                ' (' + ', '.join(str_helper(s) for s in self.back_pointers) + ')')

    def next_to_parse(self):
        if self.dot_position < len(self):
            return self.rule[self.dot_position]

    def is_complete(self):
        return len(self) == self.dot_position

    @staticmethod
    def init():
        return EarleyState(Rule(EarleyState.START, [Grammar.get_starting_non_terminal()]))


class ChartEntry:

    def __init__(self, states):
        self.states = states

    def __iter__(self):
        return iter(self.states)

    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join(str(s) for s in self.states)

    def add(self, state):
        if state not in self.states:
            self.states.append(state)


class Chart:

    def __init__(self, entries):
        self.entries = entries

    def __getitem__(self, i):
        return self.entries[i]

    def __len__(self):
        return len(self.entries)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n\n'.join([("Chart[%d]:\n" % i) + str(entry) for i, entry in
                            enumerate(self.entries)])

    @staticmethod
    def init(length):
        return Chart([(ChartEntry([]) if i > 0 else ChartEntry([EarleyState.init()])) for i in range(length)])


class EarleyParse:

    def __init__(self, tokens, grammar):
        self.grammar = grammar
        self.words = tokens
        self.chart = Chart.init(len(self.words) + 1)
        self.current_token_index = 0

    def predictor(self, state, pos):
        for rule in self.grammar[state.next_to_parse()]:
            self.chart[pos].add(EarleyState(rule, dot=0, sent_pos=state.chart_index, chart_pos=state.chart_index))

    def scanner(self, state, pos):
        if state.chart_index < len(self.words):
            word = str(self.words[state.chart_index].tag)
            if any((word in r) for r in self.grammar[state.next_to_parse()]):
                self.chart[pos + 1].add(EarleyState(Rule(state.next_to_parse(), [word]),
                                                    dot=1, sent_pos=state.chart_index,
                                                    chart_pos=(state.chart_index + 1)))

    def completer(self, state, pos):
        for prev_state in self.chart[state.sentence_position]:
            if prev_state.next_to_parse() == state.rule.lhs:
                self.chart[pos].add(EarleyState(prev_state.rule,
                                                dot=(prev_state.dot_position + 1),
                                                sent_pos=prev_state.sentence_position,
                                                chart_pos=pos,
                                                back_pointers=(prev_state.back_pointers + [state])))

    def __try_find_error(self):
        for i, chart in enumerate(self.chart):
            if len(chart) == 0:
                raise SyntaxAnalyzerError(self.words[i - 1].line)
                # print(f"Ошибка где-то около {self.words[i - 1].line}")
                # break

    def __parse(self):
        for i in range(len(self.chart)):
            for state in self.chart[i]:
                if not state.is_complete():
                    if self.grammar.is_tag(state.next_to_parse()):
                        self.scanner(state, i)
                    else:
                        self.predictor(state, i)
                else:
                    self.completer(state, i)

    def get_parse_tree(self):
        def build_tree(tree_state):
            if self.grammar.is_tag(tree_state.rule.lhs):
                self.current_token_index += 1
                return Tree(tree_state.rule.lhs, [self.words[self.current_token_index - 1]])
            return Tree(tree_state.rule.lhs,
                        [build_tree(s) for s in tree_state.back_pointers])

        self.__parse()
        start = Grammar.get_starting_non_terminal()
        for state in self.chart[-1]:
            if state.is_complete() and state.rule.lhs == start \
                    and state.sentence_position == 0 and state.chart_index == len(self.words):
                return build_tree(state)
        self.__try_find_error()
        return None
