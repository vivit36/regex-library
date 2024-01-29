import copy

import graphviz


class Graph:
    class State:
        def __init__(self):
            self.type = None                # Тип состояния: Начальное, обычное, принимающее
            self.value = set()              # Множество состояния
            self.trans_dict = dict()        # Словарь с переходами, где ключ - по чему переходим, значение - состояние, куда переходим

    def __init__(self):
        self.start_state = None
        self.error_state = None
        self.state_dict = dict()

    def copy_dfa(self):
        new_dfa = Graph()

        for key, cur_state in self.state_dict.items():
            if key not in new_dfa.state_dict:
                tmp_state = Graph.State()
                tmp_state.type = copy.copy(cur_state.type)
                tmp_state.value = copy.copy(cur_state.value)
                new_dfa.state_dict[tmp_state.value] = tmp_state

        new_dfa.start_state = new_dfa.state_dict[self.start_state.value]
        new_dfa.error_state = new_dfa.state_dict[self.error_state.value]

        for key, cur_state in self.state_dict.items():
            for lit, next_state in cur_state.trans_dict.items():
                new_dfa.state_dict[key].trans_dict[lit] = new_dfa.state_dict[next_state.value]

        return new_dfa

    def visualization(self):
        # Создание dot файла для визуального представления дерева с помощью graphviz
        f = graphviz.Digraph('finite_state_machine', filename='fsm.gv')
        f.attr(rankdir='LR')
        width = 2
        height = 2

        f.attr('node', shape='circle', fixedsize='true', width=f'{width}', height=f'{height}')
        f.node("N0", style='invis')
        for cur_node in self.state_dict.values():
            pr_node = str(set(cur_node.value)) if len(cur_node.value) != 0 else '{}'
            if cur_node.type == "End":
                f.attr('node', shape='doublecircle', fixedsize='true', width=f'{width}', height=f'{height}')
                f.node(pr_node)
                f.attr('node', shape='circle', fixedsize='true', width=f'{width}', height=f'{height}')
            else:
                f.node(pr_node)

        f.edge("N0", str(set(self.start_state.value)), label="START")
        for cur_node in self.state_dict.values():
            pr_node = str(set(cur_node.value)) if len(cur_node.value) != 0 else '{}'
            for cur_edge in cur_node.trans_dict.keys():
                pr_node_2 = str(set(cur_node.trans_dict[cur_edge].value)) if len(
                    cur_node.trans_dict[cur_edge].value) != 0 else '{}'
                f.edge(pr_node, pr_node_2, label=str(cur_edge))

        f.view()

    def create_dfa(self, tree):
        queue = list()

        s0 = Graph.State()
        s0.type = "Start"
        s0.value = frozenset(tree.root.f)

        self.state_dict[s0.value] = s0
        self.start_state = s0

        queue.append(s0)

        while len(queue) != 0:
            cur_state = queue.pop(0)
            for lit in tree.lit_set:
                u = set()
                for cur_set in cur_state.value:
                    if tree.lit_dict[cur_set] == lit:
                        u.update(tree.fp_table[cur_set])

                u = frozenset(u)
                if u not in self.state_dict:
                    next_state = Graph.State()
                    next_state.value = u
                    next_state.type = "Common"
                    cur_state.trans_dict[lit] = next_state

                    self.state_dict[u] = next_state
                    queue.append(next_state)
                else:
                    cur_state.trans_dict[lit] = self.state_dict[u]

        for cur_set in self.state_dict.keys():
            if tree.dollar_pos in cur_set:
                self.state_dict[cur_set].type = "End"
            if len(cur_set) == 0:
                self.error_state = self.state_dict[cur_set]
                for el in self.state_dict.values():
                    el.trans_dict["any"] = self.state_dict[cur_set]

    def check_regex(self, reg_str):
        cur_state = self.start_state
        for lit in reg_str:
            if lit in cur_state.trans_dict:
                cur_state = cur_state.trans_dict[lit]
            else:
                cur_state = cur_state.trans_dict["any"]
                #cur_state = self.error_state
                #break

        return True if cur_state.type == "End" else False

    def dfa_to_regex(self):
        def minus_state(vertex_dict, trans):

            #del_vert_set = set()
            p = 1
            while p != -1:
                p = -1
                q = -1
                r = -1

                for q, type in vertex_dict.items():
                    if type == "Common":
                        in_cnt = 0
                        in_ind = list()
                        out_cnt = 0
                        out_ind = list()
                        for i in range(1, len(trans)):
                            if i in vertex_dict:
                                if q != i and trans[q][i] is not False:
                                    out_cnt += 1
                                    out_ind.append(i)
                                if q != i and trans[i][q] is not False:
                                    in_cnt += 1
                                    in_ind.append(i)

                        if in_cnt <= 2 and out_cnt <= 2:
                            tmp_set = set()
                            for ell in in_ind:
                                tmp_set.add(ell)
                            for ell in out_ind:
                                tmp_set.add(ell)
                            if len(tmp_set) == 2:
                                p = tmp_set.pop()
                                r = tmp_set.pop()
                                break

                if p != -1 and r != -1:
                    e = '(' + trans[p][q] + ')' if trans[p][q] is not False else False
                    f = '(' + trans[q][p] + ')' if trans[q][p] is not False else False
                    g = '(' + trans[q][q] + ')' if trans[q][q] is not False else False
                    h = '(' + trans[q][r] + ')' if trans[q][r] is not False else False
                    i = '(' + trans[r][q] + ')' if trans[r][q] is not False else False

                    del (vertex_dict[q])
                    #del_vert_set.add(q)
                    t = ""
                    if e is False or f is False:
                        t = False
                    else:
                        t = t + e
                        if g is not False:
                            t = t + g + '*'
                        t = t + f
                    if trans[p][p] is False:
                        if t is not False:
                            trans[p][p] = t
                    else:
                        if t is not False:
                            trans[p][p] = trans[p][p] + '|' + t

                    t = ""
                    if i is False or h is False:
                        t = False
                    else:
                        t = t + i
                        if g is not False:
                            t = t + g + '*'
                        t = t + h
                    if trans[r][r] is False:
                        if t is not False:
                            trans[r][r] = t
                    else:
                        if t is not False:
                            trans[r][r] = trans[r][r] + '|' + t

                    t = ""
                    if e is False or h is False:
                        t = False
                    else:
                        t = t + e
                        if g is not False:
                            t = t + g + '*'
                        t = t + h
                    if trans[p][r] is False:
                        if t is not False:
                            trans[p][r] = t
                    else:
                        if t is not False:
                            trans[p][r] = trans[p][r] + '|' + t

                    t = ""
                    if i is False or f is False:
                        t = False
                    else:
                        t = t + i
                        if g is not False:
                            t = t + g + '*'
                        t = t + f
                    if trans[r][p] is False:
                        if t is not False:
                            trans[r][p] = t
                    else:
                        if t is not False:
                            trans[r][p] = trans[r][p] + '|' + t

        special = {'|', '*', '[', ']', '{', '}'}
        vertex_dict = dict()
        res = list()
        cnt = 1
        for cur_state in self.state_dict.values():
            cur_state.num = cnt
            if self.start_state == cur_state:
                vertex_dict[cnt] = "Start"
                if cur_state.type == "End":
                    res.append('#')
            else:
                if cur_state == self.error_state and cur_state.type != "End":
                    cur_state.num = None
                    continue
                else:
                    vertex_dict[cnt] = cur_state.type
            cnt += 1

        trans = [[[] for i in range(len(vertex_dict) + 1)] for _ in range(len(vertex_dict) + 1)]
        for cur_state in self.state_dict.values():
            for lit, next_state in cur_state.trans_dict.items():
                if cur_state.num is not None and next_state.num is not None:
                    if lit == "any":
                        trans[cur_state.num][next_state.num] = ['.']
                    else:
                        if len(trans[cur_state.num][next_state.num]) == 1 and trans[cur_state.num][next_state.num][0] == '.':
                            continue
                        else:
                            trans[cur_state.num][next_state.num].append(lit if lit not in special else '\\' + lit)

        for i in range(1, len(vertex_dict) + 1):
            for j in range(1, len(vertex_dict) + 1):
                if len(trans[i][j]) > 1:
                    trans[i][j] = '(' + '|'.join(trans[i][j]) + ')'
                elif len(trans[i][j]) == 1:
                    trans[i][j] = trans[i][j][0]
                else:
                    trans[i][j] = False

        for i in range(1, len(vertex_dict) + 1):
            for j in range(1, len(vertex_dict) + 1):
                if trans[i][j] == '.':
                    tmp = list()
                    for w1 in range(1, len(vertex_dict) + 1):
                        if trans[i][w1] is not False and trans[i][w1] != '.':
                            tmp.append('^'+trans[i][w1])
                    if len(tmp) != 0:
                        trans[i][j] = '(' + '|'.join(tmp) + ')'

        minus_state(vertex_dict, trans)

        for start, start_type in vertex_dict.items():
            for end, end_type in vertex_dict.items():
                if start_type == "Start" and end_type == "End":
                    tmp_dict = dict()
                    tmp_trans = list()
                    tmp_dict = copy.copy(vertex_dict)
                    for k in tmp_dict:
                        tmp_dict[k] = "Common"
                    tmp_dict[start] = "Start"
                    tmp_dict[end] = "End"
                    if self.error_state.num in tmp_dict and tmp_dict[self.error_state.num] == "Common":
                        del(tmp_dict[self.error_state.num])

                    tmp_trans = copy.copy(trans)

                    minus_state(tmp_dict, tmp_trans)

                    t = ""
                    if tmp_trans[end][start] is False or tmp_trans[start][end] is False:
                        if tmp_trans[end][end] is False:
                            t += ""
                        else:
                            t += '(' + tmp_trans[end][end] + ')' + '*'
                    else:
                        if tmp_trans[start][start] is False:
                            t += '(' + tmp_trans[end][start] + ')' + '(' + tmp_trans[start][end] + ')'
                        else:
                            t += '(' + tmp_trans[end][start] + ')' + '(' + tmp_trans[start][start] + ')' + '(' + tmp_trans[start][end] + ')'

                        if tmp_trans[end][end] is False:
                            t = '(' + t + ')' + '*'
                        else:
                            t = '(' + t + '|' + '(' + tmp_trans[end][end] + ')' + ')' + '*'

                    x = ""
                    if tmp_trans[start][start] is False:
                        x += ""
                    else:
                        x += '(' + tmp_trans[start][start] + ')' + '*'

                    if tmp_trans[start][end] is False:
                        x = ""
                    else:
                        x += '(' + tmp_trans[start][end] + ')' + t

                    if x != "":
                        res.append(x)

        final_str = ""

        for i in range(len(res)):
            if i == len(res) - 1:
                final_str += '(' + res[i] + ')'
            else:
                final_str += '(' + res[i] + ')' + '|'

        return final_str

    def addition_to_dfa(self):
        new_dfa = self.copy_dfa()
        for cur_state in new_dfa.state_dict.values():
            if cur_state.type == "End":
                cur_state.type = "Common"
            else:
                cur_state.type = "End"

        return new_dfa

    def difference_with_dfa(self, minus_dfa):
        new_dfa = Graph()
        sec_dfa = minus_dfa.addition_to_dfa()

        for first_key, first_state in self.state_dict.items():
            for second_key, second_state in sec_dfa.state_dict.items():
                new_state = Graph.State()
                new_state.value = (copy.copy(first_key), copy.copy(second_key))

                if self.start_state == first_state and sec_dfa.start_state == second_state:
                    new_dfa.start_state = new_state
                if self.error_state == first_state and sec_dfa.error_state == second_state:
                    new_dfa.error_state = new_state

                if first_state.type == "End" and second_state.type == "End":
                    new_state.type = "End"
                else:
                    new_state.type = "Common"

                new_dfa.state_dict[(first_key, second_key)] = new_state

        for first_key, first_state in self.state_dict.items():
            for second_key, second_state in sec_dfa.state_dict.items():
                for first_lit, first_next_state in first_state.trans_dict.items():
                    for second_lit, second_next_state in second_state.trans_dict.items():
                        if first_lit == second_lit:
                            new_dfa.state_dict[(first_state.value, second_state.value)].trans_dict[first_lit] = \
                                new_dfa.state_dict[(first_next_state.value, second_next_state.value)]
                        elif first_lit == "any":
                            if second_lit not in first_state.trans_dict:
                                new_dfa.state_dict[(first_state.value, second_state.value)].trans_dict[second_lit] = \
                                    new_dfa.state_dict[(first_next_state.value, second_next_state.value)]
                        elif second_lit == "any":
                            if first_lit not in second_state.trans_dict:
                                new_dfa.state_dict[(first_state.value, second_state.value)].trans_dict[first_lit] = \
                                    new_dfa.state_dict[(first_next_state.value, second_next_state.value)]
        return new_dfa
