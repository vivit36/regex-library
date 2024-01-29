from graph_dfa import *
from syntax_tree import *


class MyLib:
    def __init__(self):
        self.str_regex_lst = list()
        self.dfa_regex_lst = list()

    def compile_regex(self, enter_str, mode=0):
        def check_valid_str(reg_str):
            prev_lit = ""
            stack = list()
            for el in reg_str:
                if (el == '(' or el == '[' or el == '{') and prev_lit != '\\':
                    stack.append(el)
                if prev_lit == '*' and (el == '*' or el == '{'):
                    return False
                if prev_lit == '|' and (el == '*' or el == '{'):
                    return False
                if prev_lit == "" and (el == '*' or el == '{'):
                    return False
                if prev_lit == '}' and el == '*':
                    return False
                if el == ')' or el == ']' or el == '}':
                    if len(stack) == 0:
                        return False
                    else:
                        tmp = stack.pop()
                        if el == ')' and tmp != '(' or el == '}' and tmp != '{' or el == ']' and tmp != '[':
                            return False
                prev_lit = el
            return True

        if check_valid_str(enter_str) is False:
            return False
        else:
            sint_tree = STree()
            sint_tree.create_tree(enter_str)
            sint_tree.make_all_set()
            if mode != 0:
                sint_tree.visualization()

            dfa = Graph()
            dfa.create_dfa(sint_tree)
            if mode != 0:
                dfa.visualization()

            self.str_regex_lst.append(enter_str)
            self.dfa_regex_lst.append(dfa)
        return True

    def print_all_regex(self):
        print("*--------------------------------------------------------*")
        print("*             Compiled regular expressions               *")
        print("*--------------------------------------------------------*")
        if len(self.str_regex_lst) == 0:
            print("You don't have compiled regular expressions")
        else:
            for i in range(len(self.str_regex_lst)):
                print(f"{i + 1}: {self.str_regex_lst[i]}")
        print("*--------------------------------------------------------*")

    def findall(self, big_str, regex_num):
        index_lst = list()
        begin = 0
        flag = False
        while begin < len(big_str):
            length = 1
            while begin + length < len(big_str) + 1:
                if self.dfa_regex_lst[regex_num - 1].check_regex(big_str[begin:begin + length]):
                    index_lst.append((begin, length))
                    begin = begin + length
                    flag = True
                    break
                length += 1
            if flag is False:
                begin += 1
            else:
                flag = False

        return index_lst

    def difference(self, num1, num2):
        dif_dfa = self.dfa_regex_lst[num1 - 1].difference_with_dfa(self.dfa_regex_lst[num2 - 1])
        dif_dfa.visualization()
        self.dfa_regex_lst.append(dif_dfa)
        self.str_regex_lst.append(f"Difference between \"{self.str_regex_lst[num1 - 1]}\" and \"{self.str_regex_lst[num2 - 1]}\"")


    def addition(self, num):
        add_dfa = self.dfa_regex_lst[num - 1].addition_to_dfa()
        self.dfa_regex_lst.append(add_dfa)
        self.str_regex_lst.append("Addition to: " + self.str_regex_lst[num - 1])
        add_dfa.visualization()

    def dfa_to_regex(self):
        num = int(input("Please choose regex: "))
        print(f"{num}: {self.str_regex_lst[num - 1]}")
        print(self.dfa_regex_lst[num - 1].dfa_to_regex())

    def menu(self):
        while True:
            print("*--------------------------------------------------------*")
            print("*                       Menu                             *")
            print("*--------------------------------------------------------*")
            print("* If you want to compile regex - enter 1                 *")
            print("* If you want to print all compiled regexes - enter 2    *")
            print("* If you want to check your string - enter 3             *")
            print("* If you want to use findall - enter 4                   *")
            print("* If you want to use regex difference - enter 5          *")
            print("* If you want to use regex addition - enter 6            *")
            print("* If you want to use dfa_to_regex - enter 7              *")
            print("* If you want to test - enter 8                          *")
            print("* If you want to exit - enter 0                          *")
            print("*--------------------------------------------------------*")

            answer = int(input("Enter your choice: "))

            if answer == 1:
                mode = input("Do you want to visualize? (y/n): ")
                mode = 1 if mode == 'y' else 0
                enter_str = input("Please enter your regular expression: ")
                if self.compile_regex(enter_str, mode) is False:
                    print("Your regular expression contains syntax errors!")

            elif answer == 2:
                self.print_all_regex()

            elif answer == 3:
                reg_str = input("Please enter your string: ")
                num = int(input("Please choose regex: "))
                print(f"{num}: {self.str_regex_lst[num - 1]}")
                if self.dfa_regex_lst[num - 1].check_regex(reg_str):
                    print("Match!")
                else:
                    print("No match!")

            elif answer == 4:
                def out_yellow(text):
                    print(f"\033[33m{text}", end='')

                def out_plain(text):
                    print(f"\033[0m{text}", end='')

                big_str = input("Please enter your string: ")
                num = int(input("Please choose regex: "))
                index_lst = self.findall(big_str, num)
                if len(index_lst) == 0:
                    print("No matches")
                else:
                    st = 0
                    for el in index_lst:
                        out_plain(big_str[st:el[0]])
                        out_yellow(big_str[el[0]:el[0] + el[1]])
                        st = el[0] + el[1]

                    print(f"\033[0m")
                    for i in range(len(index_lst)):
                        begin = index_lst[i][0]
                        length = index_lst[i][1]
                        print(f"Match {i + 1}: {big_str[begin:begin + length]} {index_lst[i]}")

            elif answer == 5:
                num1 = int(input("Please choose regex #1: "))
                num2 = int(input("Please choose regex #2: "))
                print(f"{num1}: {self.str_regex_lst[num1 - 1]}")
                print(f"{num2}: {self.str_regex_lst[num2 - 1]}")
                self.difference(num1, num2)

            elif answer == 6:
                num = int(input("Please choose regex: "))
                print(f"{num}: {self.str_regex_lst[num - 1]}")
                self.addition(num)

            elif answer == 7:
                self.dfa_to_regex()
            elif answer == 8:
                self.test_prog()
            elif answer == 0:
                break

    def test_prog(self):
        reg_exs = ["a|b|c|\\|",
                   "abcde\\*mnk",
                   "(q|w)(r|\\{)*",
                   "PlayGame(Dota|#)",
                   "((+7)|7|8)(([0123456789]){10})",
                   "@([ABCDEFGHIJKLMNOPQRSTUVWXYZZabcdefghijklmnopqrstuvwxyz0123456789]*)"
                   ]

        for regex in reg_exs:
            self.compile_regex(regex)

        input_str = [
            ["a", "b", "c", "|", '*'],
            ["abcde*mnk", "abcdemnk"],
            ["qr", "wr", "q{", "w{", "q{{{{{{{{{"],
            ["PlayGameDota", "PlayGame", "PlayGameCS"],
            ["+79283108720", "89283108720", "79280075382", "+7928245678", "8928928989899"],
            ["@vivit36", "@IIKSmephi", "@nagibator228", "pasha", "@PROIT4chainik", "@ironman@%$#%@$"]

        ]

        for i, regex in enumerate(reg_exs):
            print("*--------------------------------------------------------*")
            print(f"Regex: {regex}")
            print("*--------------------------------------------------------*")
            for inp_str in input_str[i]:
                print(f"{inp_str}: {self.dfa_regex_lst[i].check_regex(inp_str)}")
