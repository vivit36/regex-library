import graphviz

# Базовый класс узла, от которого наследуются все остальные
class Node:
    def __init__(self):
        self.group_number = None    # Номер группы захвата (для узлов)
        self.number = None          # Порядковый номер литеры (для Aleaf)
        self.n = None               # N-множество
        self.f = None               # F-множество
        self.l = None               # L-множество


# Символьный узел
class ALeaf(Node):
    def __init__(self, lit):
        super().__init__()
        self.lit = lit


# Узел операции "ИЛИ"
class OrNode(Node):
    def __init__(self, first_child, second_child):
        super().__init__()
        self.first_child = first_child
        self.second_child = second_child


# Узел операции "И"
class AndNode(Node):
    def __init__(self, first_child, second_child):
        super().__init__()
        self.first_child = first_child
        self.second_child = second_child


# Узел операции "*" (замыкание Клини)
class StarNode(Node):
    def __init__(self, child):
        super().__init__()
        self.child = child


# Узел операции "[]" (символ из набора)
class SqBrNode(Node):
    def __init__(self, children, size):
        super().__init__()
        self.children = children
        self.size = size


# Узел операции "Выражение из нумерованной группы захвата" TODO
class NameGroup(Node):
    def __init__(self, number):
        super().__init__()
        self.name_group = number
        pass


class STree:
    def __init__(self):
        self.root = None               # Корень дерева
        self.graphviz_counter = 1      # Счетчик для узлов графвиза
        self.counter_for_numerate = 1  # Счетчик для нумерации
        self.fp_table = list()         # Таблица FP-множества
        self.lit_dict = dict()         # Словарь соответствия литералы и порядкового номера
        self.lit_set = set()           # Множетсво состояшие из литерал
        self.dollar_pos = None         # Порядковый номер для символа конца строки

        # self.cap_group_dict = dict()   # для групп захвата
        # self.cap_group_num = 0

    # Преобразование исходной строки в список
    def change_str(self, enter_str):
        result = list()
        i = 0
        while i != len(enter_str):
            el = enter_str[i]
            if el == '\\':
                result.append(enter_str[i:i + 2])
                i += 2
            else:
                if el == '{':
                    k = i + 1
                    num = 0
                    while enter_str[k] != '}':
                        num = num * 10 + int(enter_str[k])
                        k += 1

                    if enter_str[i - 1] != ']' and enter_str[i - 1] != ')':
                        tmp = result.pop()
                        if num != 0:
                            for t in range(num):
                                result.append(tmp)
                        i = k + 1
                    else:
                        stack = list()
                        stack.append(enter_str[i - 1])
                        t = i - 1
                        while len(stack) != 0:
                            t -= 1
                            if enter_str[t] == ')' or enter_str == ']':
                                stack.append(enter_str[t])
                            if enter_str[t] == '(' or enter_str == '[':
                                stack.pop()
                        buf = result[t:i]
                        del [result[t:i]]
                        if num != 0:
                            for t in range(num):
                                result.extend(buf)
                        i = k + 1
                else:
                    result.append(el)
                    i += 1

        return result

    # Найти ближайщие скобки
    def find_closest_brackets(self, enter_str):
        open = 0
        for i, el in enumerate(enter_str):
            if el == '(' or el == '{' or el == '[':
                open = i
                tmp = el
            elif el == ')' and tmp == '(' or el == '}' and tmp == '{' or el == ']' and tmp == '[':
                return [open, i]

        return None

    # Подсчет количества групп захвата
    def count_capture_group(self, reg_str):
        counter = -1
        for el in reg_str:
            if el == '(':
                counter += 1
        return counter

    # Преобразование регулярного выражения в синтаксическое дерево
    def create_tree(self, enter_str):
        lst = self.change_str('(' + enter_str + ')' + '$')
        up_size = self.count_capture_group(lst)
        counter = 1
        segment = self.find_closest_brackets(lst)
        while segment is not None:
            if lst[segment[0]] == '[':
                tmp = list()
                for i in range(segment[0] + 1, segment[1]):
                    tmp.append(ALeaf(lst[i]))

                lst[segment[0] + 1] = SqBrNode(tmp, len(tmp))
                del lst[segment[0] + 2:segment[1]]
                segment[1] -= len(tmp) - 1
            else:
                # Создаем все a-leaf
                for i in range(segment[0] + 1, segment[1]):
                    if i != 0 and (lst[i] == '#' and lst[i - 1] != '|'):
                        continue
                    if lst[i] != '|' and lst[i] != '*' and isinstance(lst[i], str):
                        if len(lst[i]) > 1 and lst[i][0] == "\\":
                            # lst[i] = NameGroup(int(lst[i][1:]))
                            lst[i] = ALeaf(lst[i][1])
                        else:
                            lst[i] = ALeaf(lst[i])

                # Создаем все *-node
                i = segment[0] + 1
                while i < segment[1] - 1:
                    if isinstance(lst[i], Node) and lst[i + 1] == '*':
                        del lst[i + 1]
                        lst[i] = StarNode(lst[i])
                        segment[1] -= 1
                    else:
                        i += 1

                # Создаем все .-node
                i = segment[0] + 1
                while i < segment[1] - 1:
                    if isinstance(lst[i], Node) and isinstance(lst[i + 1], Node):
                        lst[i] = AndNode(lst[i], lst[i + 1])
                        del lst[i + 1]
                        segment[1] -= 1
                    else:
                        i += 1

                # Создаем все |-node
                i = segment[0] + 1
                while i < segment[1] - 2:
                    if isinstance(lst[i], Node) and lst[i + 1] == '|' and isinstance(lst[i + 2], Node):
                        tmp = OrNode(lst[i], lst[i + 2])
                        del lst[i + 1:i + 3]
                        lst[i] = tmp
                        segment[1] -= 2
                    else:
                        i += 1

            lst[segment[0]] = lst[segment[0] + 1]
            if counter <= up_size:
                lst[segment[0]].group_number = counter
            else:
                lst[segment[0]].group_number = 0
            counter += 1
            del lst[segment[0] + 1: segment[1] + 1]
            segment = self.find_closest_brackets(lst)

        lst[1] = ALeaf(lst[1])
        lst[0] = AndNode(lst[0], lst[1])
        del lst[1]
        self.root = lst[0]

    def numerate_lit(self):
        # Нумерация a-leaf для построения F, L, FP множеств
        def numerate(cur_node, group_set):
            # if cur_node.group_number is not None:
            #     group_set.add(cur_node.group_number)

            if isinstance(cur_node, OrNode) or isinstance(cur_node, AndNode):
                numerate(cur_node.first_child, group_set)
                numerate(cur_node.second_child, group_set)
            elif isinstance(cur_node, StarNode):
                numerate(cur_node.child, group_set)
            elif isinstance(cur_node, ALeaf):
                self.lit_dict[self.counter_for_numerate] = cur_node.lit
                #self.cap_group_dict[(cur_node.lit, self.counter_for_numerate)] = group_set.copy()
                if cur_node.lit == '$':
                    self.dollar_pos = self.counter_for_numerate
                else:
                    self.lit_set.add(cur_node.lit)
                cur_node.number = self.counter_for_numerate
                self.counter_for_numerate += 1
            elif isinstance(cur_node, SqBrNode):
                for i in range(cur_node.size):
                    numerate(cur_node.children[i], group_set)
            elif isinstance(cur_node, NameGroup):
                pass #TODO

            # if cur_node.group_number is not None:
            #     group_set.remove(cur_node.group_number)

        tmp = set()
        numerate(self.root, tmp)
        self.fp_table = [set() for _ in range(self.counter_for_numerate)]

    def n_set(self):
        # Построение N-множества для каждого узла
        def recursive(cur_node):
            if isinstance(cur_node, ALeaf):
                if cur_node.lit == '#':
                    cur_node.n = True
                else:
                    cur_node.n = False
            elif isinstance(cur_node, OrNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                if cur_node.first_child.n is True or cur_node.second_child.n is True:
                    cur_node.n = True
                else:
                    cur_node.n = False
            elif isinstance(cur_node, SqBrNode):
                tmp = False
                for i in range(cur_node.size):
                    recursive(cur_node.children[i])
                    if cur_node.children[i].n is True:
                        tmp = True
                cur_node.n = tmp
            elif isinstance(cur_node, AndNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                if cur_node.first_child.n is True and cur_node.second_child.n is True:
                    cur_node.n = True
                else:
                    cur_node.n = False
            elif isinstance(cur_node, StarNode):
                recursive(cur_node.child)
                cur_node.n = True
            elif isinstance(cur_node, NameGroup):
                pass #TODO

        recursive(self.root)

    def f_set(self):
        # Построение F-множества для каждого узла
        def recursive(cur_node):
            if isinstance(cur_node, ALeaf):
                if cur_node.lit == '#':
                    cur_node.f = set()
                else:
                    cur_node.f = {cur_node.number}
            elif isinstance(cur_node, OrNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                cur_node.f = cur_node.first_child.f | cur_node.second_child.f
            elif isinstance(cur_node, SqBrNode):
                tmp_set = set()
                for i in range(cur_node.size):
                    recursive(cur_node.children[i])
                    tmp_set.update(cur_node.children[i].f)
                cur_node.f = tmp_set
            elif isinstance(cur_node, AndNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                if cur_node.first_child.n:
                    cur_node.f = cur_node.first_child.f | cur_node.second_child.f
                else:
                    cur_node.f = cur_node.first_child.f
            elif isinstance(cur_node, StarNode):
                recursive(cur_node.child)
                cur_node.f = cur_node.child.f
            elif isinstance(cur_node, NameGroup):
                pass # TODO

        recursive(self.root)

    def l_set(self):
        # Построение L-множества для каждого узла
        def recursive(cur_node):
            if isinstance(cur_node, ALeaf):
                if cur_node.lit == '#':
                    cur_node.l = set()
                else:
                    cur_node.l = {cur_node.number}
            elif isinstance(cur_node, OrNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                cur_node.l = cur_node.first_child.l | cur_node.second_child.l
            elif isinstance(cur_node, SqBrNode):
                tmp_set = set()
                for i in range(cur_node.size):
                    recursive(cur_node.children[i])
                    tmp_set.update(cur_node.children[i].l)
                cur_node.l = tmp_set
            elif isinstance(cur_node, AndNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                if cur_node.second_child.n:
                    cur_node.l = cur_node.first_child.l | cur_node.second_child.l
                else:
                    cur_node.l = cur_node.second_child.l
            elif isinstance(cur_node, StarNode):
                recursive(cur_node.child)
                cur_node.l = cur_node.child.l
            elif isinstance(cur_node, NameGroup):
                pass # TODO

        recursive(self.root)

    def fp_set(self):
        # Построение FP-множества для каждого узла
        def recursive(cur_node):
            if isinstance(cur_node, OrNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
            elif isinstance(cur_node, AndNode):
                recursive(cur_node.first_child)
                recursive(cur_node.second_child)
                for p in cur_node.first_child.l:
                    for q in cur_node.second_child.f:
                        self.fp_table[p].add(q)
            elif isinstance(cur_node, StarNode):
                recursive(cur_node.child)
                for p in cur_node.child.l:
                    for q in cur_node.child.f:
                        self.fp_table[p].add(q)
            elif isinstance(cur_node, NameGroup):
                pass # TODO

        recursive(self.root)

    def make_all_set(self):
        self.numerate_lit()
        self.n_set()
        self.f_set()
        self.l_set()
        self.fp_set()

    def visualization(self):
        # Создание dot файла для визуального представления дерева с помощью graphviz
        def format_string(mode, type, node):
            # "Красивый" узел
            if mode:
                return f"<{type}<BR /><FONT POINT-SIZE=\"10\" COLOR=\"blue\">" \
                       f"{node.group_number}</FONT><FONT POINT-SIZE=\"10\" COLOR=\"red\"><BR />" \
                       f"N={node.n} F={node.f} L={node.l}</FONT>>"
            else:
                return f"<{type}<BR /><FONT POINT-SIZE=\"10\" COLOR=\"red\">Order={node.number} N={node.n} F={node.f} L={node.l}</FONT>>"

        def recursive(cur_node):
            if isinstance(cur_node, OrNode):
                sym1 = recursive(cur_node.first_child)
                sym2 = recursive(cur_node.second_child)
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, '|', cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, '|', cur_node))
                dot.edge(cur_sym, sym1)
                dot.edge(cur_sym, sym2)
                self.graphviz_counter += 1
                return cur_sym
            elif isinstance(cur_node, ALeaf):
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, cur_node.lit, cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, cur_node.lit, cur_node))
                self.graphviz_counter += 1
                return cur_sym
            elif isinstance(cur_node, AndNode):
                sym1 = recursive(cur_node.first_child)
                sym2 = recursive(cur_node.second_child)
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, '.', cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, '.', cur_node))
                dot.edge(cur_sym, sym1)
                dot.edge(cur_sym, sym2)
                self.graphviz_counter += 1
                return cur_sym
            elif isinstance(cur_node, StarNode):
                sym1 = recursive(cur_node.child)
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, '*', cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, '*', cur_node))
                dot.edge(cur_sym, sym1)
                self.graphviz_counter += 1
                return cur_sym
            elif isinstance(cur_node, SqBrNode):
                n_lst = list()
                for i in range(cur_node.size):
                    n_lst.append(recursive(cur_node.children[i]))
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, '[]', cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, '*', cur_node))
                for i in range(cur_node.size):
                    dot.edge(cur_sym, n_lst[i])
                self.graphviz_counter += 1
                return cur_sym
            elif isinstance(cur_node, NameGroup):
                cur_sym = 'N' + str(self.graphviz_counter)
                if cur_node.group_number is not None:
                    dot.node(cur_sym, label=format_string(True, f'/{cur_node.name_group}', cur_node))
                else:
                    dot.node(cur_sym, label=format_string(False, f'/{cur_node.name_group}', cur_node))
                self.graphviz_counter += 1
                return cur_sym

        dot = graphviz.Digraph('stree', filename='stree',
                               node_attr={'color': 'lightblue2', 'style': 'filled'})
        recursive(self.root)
        dot.view()