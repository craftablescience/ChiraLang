import math


class ChiraError:
    def __init__(self, message):
        self.message = message
        self.name = "Error"

    def __str__(self):
        return self.name + ": " + self.message


class ChiraSyntaxError(ChiraError):
    def __init__(self, message="Statement is invalid"):
        super().__init__(message)
        self.name = "SyntaxError"


class ChiraNoVariableFoundError(ChiraError):
    def __init__(self, variable):
        super().__init__("Could not find variable named \"" + str(variable) + "\"")
        self.name = "NoVariableFoundError"


class ChiraInvalidOperatorError(ChiraError):
    def __init__(self, operator):
        super().__init__("Invalid operator \"" + str(operator) + "\"")
        self.name = "InvalidOperatorError"


class Interpreter:
    def __init__(self, output_function):
        self.VARS: dict = {}
        self.MATH_OPERATORS: list = ["+", "-", "*", "/", "%", "**"]
        self.ASSIGNMENT_OPERATORS: list = ["=", "+=", "-=", "*=", "/=", "%=", "**="]
        self.LOGICAL_OPERATORS: list = ["==", "!=", ">", "<", ">=", "<="]
        self.TYPES: dict = {"int": int, "str": str, "float": float, "bool": bool}
        self.FUNCTIONS: list = ["print", "load", "quit"]
        self.CONTROL_FLOW: list = ["if"]
        self.OUTPUT_FUNCTION = output_function

    def variable_exists(self, name: str) -> bool:
        return name in self.VARS.keys()

    def set_variable(self, var_type: str, name: str, value) -> None:
        self.VARS[name] = {"type": var_type, "value": value}
        return value

    def get_variable(self, name: str):
        if name not in self.VARS.keys():
            return ChiraNoVariableFoundError(name)
        return self.VARS[name]["value"]

    def get_variable_type(self, name: str):
        if name not in self.VARS.keys():
            return ChiraNoVariableFoundError(name)
        return self.VARS[name]["type"]

    def parse(self, program: str) -> None:
        for line in program.split("\n"):
            for statement in line.split(";"):
                self.parse_statement(statement.strip().split(" "))

    def parse_file(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            for line in file.readlines():
                line = line.split(";")
                for statement in line:
                    self.parse_statement(statement.strip().split(" "))

    def parse_statement(self, tokens: list, return_value: bool = False):
        # 1. Empty? Skip
        # 2. Check for IFs
        # 3. Check for assignments
        # 4. Replace variables
        # 5. Logical operators
        # 6. Control flow
        # 7. Functions
        # ------------------------

        # 1
        if len(tokens) == 0:
            return None

        # 2
        for i, token in enumerate(tokens):
            if token in self.CONTROL_FLOW:
                try:
                    if token == "if":
                        if bool(self.parse_statement(tokens[i+1:i+4], True)):
                            return self.parse_statement(tokens[i+4:])
                        else:
                            del tokens[i + 1:]
                except IndexError:
                    return ChiraSyntaxError()

        # 3
        for token in tokens:
            if token in self.ASSIGNMENT_OPERATORS:
                try:
                    i = tokens.index(token)
                    if self.variable_exists(tokens[i + 1]):
                        tokens[i + 1] = self.get_variable(tokens[i + 1])
                    tokens = merge_lists(
                        (tokens[0:i - 1] if i >= 2 else None),
                        self.parse_assignment(
                            tokens[i - 2] if tokens[i] == "=" else self.get_variable_type(tokens[i - 1]),
                            tokens[i - 1],
                            tokens[i],
                            tokens[i + 1]
                        ),
                        (tokens[i + 3:] if i + 2 < len(tokens) else None)
                    )
                except IndexError:
                    return ChiraSyntaxError()

        # 4
        for i, token in enumerate(tokens):
            if self.variable_exists(token):
                tokens[i] = self.get_variable(token)

        # 5
        for token in tokens:
            if token in self.LOGICAL_OPERATORS:
                try:
                    i = tokens.index(token)
                    tokens = merge_lists((tokens[0:i - 1] if i > 1 else None),
                                         self.compare(tokens[i - 1], tokens[i], tokens[i + 1]),
                                         (tokens[i + 2:] if i + 1 < len(tokens) else None))
                except IndexError:
                    return ChiraSyntaxError()

        # 6 todo: if/else/for/while

        # 7
        for i, token in enumerate(tokens):
            if token in self.FUNCTIONS:
                try:
                    if token == "print":
                        self.output(tokens[i + 1])
                    elif token == "quit":
                        return None
                except IndexError:
                    return ChiraSyntaxError()

        if len(tokens) == 1 and return_value:
            return tokens[0]

    def parse_assignment(self, var_type: str, name: str, assignment_type: str, value):
        if assignment_type == "=":
            return self.set_variable(var_type, name, self.TYPES[var_type](value))
        elif self.variable_exists(name):
            if var_type == "bool":
                return ChiraSyntaxError("Invalid assignment type")
            if assignment_type == "+=":
                return self.set_variable(var_type, name, self.get_variable(name) + self.TYPES[var_type](value))
            elif assignment_type == "-=":
                if var_type == "str":
                    return ChiraSyntaxError("Invalid assignment type")
                return self.set_variable(var_type, name, self.get_variable(name) - self.TYPES[var_type](value))
            elif assignment_type == "*=":
                return self.set_variable(var_type, name, self.get_variable(name) * self.TYPES[var_type](value))
            elif assignment_type == "/=":
                if var_type == "str":
                    return ChiraSyntaxError("Invalid assignment type")
                return self.set_variable(var_type, name, self.get_variable(name) / self.TYPES[var_type](value))
            elif assignment_type == "**=":
                if var_type == "str":
                    return ChiraSyntaxError("Invalid assignment type")
                return self.set_variable(var_type, name, self.TYPES[var_type](math.pow(self.get_variable(name),
                                                                                       self.TYPES[var_type](value))))
        else:
            return ChiraNoVariableFoundError(name)

    @staticmethod
    def compare(var1, operator: str, var2):
        var1 = float(var1)
        var2 = float(var2)
        if operator == "==":
            return var1 == var2
        elif operator == ">":
            return var1 > var2
        elif operator == "<":
            return var1 < var2
        elif operator == ">=":
            return var1 >= var2
        elif operator == "<=":
            return var1 <= var2
        elif operator == "!=":
            return var1 != var2
        else:
            return ChiraInvalidOperatorError(operator)

    def output(self, out):
        if out is not None and out != "":
            self.OUTPUT_FUNCTION(out)


def list_to_str(lst: list) -> str:
    out: str = ""
    for i in lst:
        out += i + " "
    return out.rstrip()


def merge_lists(*lists):
    lst = []
    for item in lists:
        if item is None:
            continue
        if type(item) == list:
            lst += item
        else:
            lst.append(item)
    return lst
