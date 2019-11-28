import tkinter as tk
from tkinter import filedialog
from typing import List, Set, Dict, Tuple, Optional
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QUrl
import datetime
import sys


# Remember to pass the definition/method, not the return value!
# Remember to pass the definition/method, not the return value!

class Ui(QtWidgets.QDialog):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('InterfaceTP1.ui', self)

        self.show()


app = QtWidgets.QApplication(sys.argv)
window = Ui()

FBSource = window.findChild(QtWidgets.QLineEdit, 'BFLineEdit')
RBSource = window.findChild(QtWidgets.QLineEdit, 'BRLineEdit')


def set_fact_base_file():
    file_name = filedialog.askopenfilename()
    FBSource.setText(file_name)


def set_rule_base_file():
    file_name = filedialog.askopenfilename()
    RBSource.setText(file_name)


FBButton = window.findChild(QtWidgets.QPushButton, 'BFButton')

RBButton = window.findChild(QtWidgets.QPushButton, 'BRButton')

exec_button = window.findChild(QtWidgets.QPushButton, 'executionButton')

forward_chaining_button = window.findChild(QtWidgets.QRadioButton, 'chainageAvantRadioButton')

backward_chaining_button = window.findChild(QtWidgets.QRadioButton, 'ChainageArriereRadioButton')

goal = window.findChild(QtWidgets.QCheckBox, 'goalCheckBox')

goal_name = window.findChild(QtWidgets.QLineEdit, 'goalName')
goal_value = window.findChild(QtWidgets.QLineEdit, 'goalValue')

ResultsTextEdit = window.findChild(QtWidgets.QTextEdit, 'ResultsTextEdit')


class Fact:
    name: str
    value: str
    flag: int

    def get_fact(self):
        return {self.name: self.value}

    def __init__(self, name, value, flag=-1):
        self.name = name
        self.value = value
        self.flag = flag

    def __repr__(self):
        return self.name + " = " + self.value

    def to_string(self):
        return self.name + " = " + self.value + " concluded from rule number : " + str(self.flag) + "\n"

    def to_premise(self):
        return Premise(name=self.name, value=self.value, operand="=")


def compare_facts(fact1: Fact, fact2: Fact) -> bool:
    if fact1.name == fact2.name and fact1.value == fact2.value:
        return True
    return False


def extract_facts(fb_file) -> dict:
    facts = {}
    f = open(fb_file, "r")
    if f.mode == 'r':
        lines = f.readlines()
        for line in lines:
            if line == "\n" or line == "":
                break
            line = line.split("\n")[0]
            key = line.split(" =")[0].strip()
            value = line.split("= ")[1].strip()
            fact = Fact(key, value)
            facts[fact.name] = fact.value
        return facts
    else:
        return {}


class Premise:
    name: str
    value: str
    operand: str

    def compare_to_fact(self, fact: Fact) -> bool:
        if self.name != fact.name:
            return False
        return eval(self.value + self.operand + fact.value)

    def __init__(self, name, value, operand):
        self.name = name
        self.value = value
        self.operand = operand

    def __str__(self):
        return self.name + self.operand + self.value


class Rule:
    conclusion: Fact
    premises: List[Premise]
    active: bool

    def __init__(self, conclusion, premises):
        self.conclusion = conclusion
        self.premises = premises
        self.active = True

    def deactivate(self):
        self.active = False

    def to_string(self):
        return self.premises + " = " + self.value + " concluded from rule number : " + str(self.flag) + "\n"


def extract_conclusion(line) -> Fact:
    line = line.split(" alors ")[1].split("\n")[0]
    conclusion = line.split(" = ")
    return Fact(conclusion[0].strip(), conclusion[1].strip())


def extract_premise(operand, premise) -> Premise:
    name = premise.split(' ' + operand + ' ')[0].strip()
    value = premise.split(' ' + operand + ' ')[1].strip()
    return Premise(name=name, operand=operand, value=value)


def extract_premises(line) -> List[Premise]:
    line = line.split("si ")[1].split(" alors ")[0]
    premises = line.split(" et ")
    result = []
    for premise in premises:
        if premise.find(' >= ') != -1:
            result.append(extract_premise('>=', premise))
        elif premise.find(' <= ') != -1:
            result.append(extract_premise('<=', premise))
        elif premise.find(' < ') != -1:
            result.append(extract_premise('<', premise))
        elif premise.find(" > ") != -1:
            result.append(extract_premise(">", premise))
        elif premise.find(' = ') != -1:
            result.append(extract_premise('=', premise))
        elif premise.find(' != ') != -1:
            result.append(extract_premise('!=', premise))
    return result


def extract_rules(file) -> List[Rule]:
    f = open(file, "r")
    if f.mode == 'r':
        lines = f.readlines()
        rules: list[Rule] = []
        for line in lines:
            if line == "\n" or line == "":
                break
            conclusion = extract_conclusion(line)
            premises = extract_premises(line)
            rules.append(Rule(conclusion=conclusion, premises=premises))
        return rules
    return []


def test_premise(premise: Premise, fact_base: dict) -> bool:
    if premise.name in fact_base:
        if premise.operand == "=":
            return eval(premise.value + "==" + fact_base[premise.name])
        return eval(premise.value + premise.operand + fact_base[premise.name])
    return False


def test_premises(premises: List[Premise], fact_base: dict) -> bool:
    test = True
    for premise in premises:

        if test_premise(premise, fact_base):
            continue
        else:
            test = False
            break
    return test


def forward_chaining_filter(rule_base: List[Rule], fact_base: dict):
    filtered_rule_base = []
    index = 1
    for rule in rule_base:
        if rule.active and test_premises(rule.premises, fact_base) and test_premise(rule.conclusion.to_premise(),
                                                                                    fact_base=fact_base) is False:
            filtered_rule_base.append([rule, index])
        index += 1
    return filtered_rule_base


def rule_choice(filtered_rule_base) -> tuple:
    return filtered_rule_base[0][0], filtered_rule_base[0][1]


def forward_chaining(rule_base: List[Rule], fact_base: dict) -> List[Fact]:
    test = True
    resulting_facts: List[Fact] = []
    while test:
        filtered_rule_base = forward_chaining_filter(rule_base, fact_base)
        test = False
        while filtered_rule_base:
            (rule, index) = rule_choice(filtered_rule_base)
            rule.deactivate()
            try:
                del (filtered_rule_base[0])
            except IndexError:
                print("An exception occurred")
            conclusion = rule.conclusion
            if conclusion.name in fact_base and fact_base[conclusion.name] != conclusion.value:
                raise Exception('contradiction in fact base and rule conclusion')
            else:
                resulting_facts.append(Fact(name=conclusion.name, value=conclusion.value, flag=index))
                fact_base[conclusion.name] = conclusion.value
                test = True
    return resulting_facts


def forward_chaining_with_goal(rule_base: List[Rule], fact_base: dict, goal: Fact) -> (
        bool, List[Rule]):
    activated_rules = []
    test = True
    while test:
        filtered_fact_base = forward_chaining_filter(rule_base, fact_base)
        test = False
        while filtered_fact_base:
            (rule, index) = rule_choice(filtered_fact_base)
            rule.deactivate()
            try:
                del (filtered_fact_base[0])
            except IndexError:
                print("An exception occurred")
            conclusion = rule.conclusion
            if conclusion.name in fact_base and fact_base[conclusion.name] != conclusion.value:
                raise Exception('contradiction in fact base and rule conclusion')
            else:
                fact_base[conclusion.name] = conclusion.value
                activated_rules.append(rule)

                if compare_facts(conclusion, goal):
                    return True, activated_rules
                fact_base[conclusion.name] = conclusion.value
                test = True
    return False, activated_rules


def view_fact_base(fact_base: dict):
    print(fact_base)


def view_rule_base(rule_base):
    for rule in rule_base:
        print(rule.conclusion.name + " = " + rule.conclusion.value, end=" <- ")
        index = 0
        for premise in rule.premises:
            index += 1
            if index == len(rule.premises):
                print(premise.name + " " + premise.operand + " " + premise.value, end=".")
            else:
                print(premise.name + " " + premise.operand + " " + premise.value, end=", ")
        print("\n")


def rule_base_to_string(rule_base) -> str:
    message: str = ""
    for rule in rule_base:
        message += rule.conclusion.name + " = " + rule.conclusion.value + " <- "
        index = 0
        for premise in rule.premises:
            index += 1
            if index == len(rule.premises):
                message += premise.name + " " + premise.operand + " " + premise.value + '.'
            else:
                message += premise.name + " " + premise.operand + " " + premise.value + ','
        message += "\n"
    return message


root = tk.Tk()
root.withdraw()

file = open("log.txt", "a+")


def log_forward_chaining_with_goal(message, result, goal_to_find):
    file.write("            goal is " + goal_to_find.name + " = " + goal_to_find.value + "\n")
    message = message.split("\n")
    file.write("            " + message[0] + "\n")
    file.write("            " + message[1] + "\n")
    result = result.split("\n")
    for res in result:
        file.write("                " + res + "\n")
    file.write("\n")
    file.flush()


def log_forward_chaining_without_goal(list_fact):
    file.write("            conclusions found are" + "\n")

    for fact in list_fact:
        file.write("                " + fact.to_string())
    file.write("\n")
    file.flush()


def menu():
    global file
    file.close()
    file = open("log.txt", "a+")
    fact_base_file = FBSource.text()
    rule_base_file = RBSource.text()
    print(rule_base_file)
    rule_base = extract_rules(rule_base_file)
    fact_base = extract_facts(fact_base_file)
    file.write("--- execution :" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " :\n")
    file.flush()
    if forward_chaining_button.isChecked():
        file.write("    --chainnage avant--\n")
        if goal.isChecked():
            file.write("        -avec but-\n")
            global goal_name
            goal_name_text = goal_name.text()
            global goal_value
            goal_value_text = goal_value.text()
            goal_to_find = Fact(name=goal_name_text, value=goal_value_text)
            status, list_fact = forward_chaining_with_goal(rule_base, fact_base, goal_to_find)
            message = ""
            if status:
                message = "Goal found !!\nrules applied are : \n"
            else:
                message = "Goal not found !!\nrules applied are : \n"
            ResultsTextEdit.setText(message)
            ResultsTextEdit.append(rule_base_to_string(list_fact))
            file.flush()
            log_forward_chaining_with_goal(message, rule_base_to_string(list_fact), goal_to_find)
            file.flush()
        else:
            file.write("        -sans but-\n")
            list_fact = forward_chaining(rule_base, fact_base)
            ResultsTextEdit.setText("")
            for fact in list_fact:
                ResultsTextEdit.append(fact.to_string())
            log_forward_chaining_without_goal(list_fact)
    file.close()


FBButton.clicked.connect(set_fact_base_file)
RBButton.clicked.connect(set_rule_base_file)
exec_button.clicked.connect(menu)
forward_chaining_button.setChecked(True)
enable_goal = False

goal_name.setReadOnly(True)
goal_value.setReadOnly(True)


def alter_enable_goal():
    global enable_goal
    if enable_goal:
        goal_value.setReadOnly(True)
        goal_name.setReadOnly(True)
    else:
        goal_value.setReadOnly(False)
        goal_name.setText("")
        goal_name.setReadOnly(False)
        goal_value.setText("")
    enable_goal = 1 - enable_goal


goal.toggled.connect(alter_enable_goal)

app.exec_()
