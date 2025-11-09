import logging
from typing import Sequence

import lexer
from lexer import Lexer, LexerException


COLORS = {
    'DEBUG': '\033[36m',  # Cyan
    'INFO': '\033[32m',   # Green
    'WARNING': '\033[33m', # Yellow
    'ERROR': '\033[31m',   # Red
    'CRITICAL': '\033[1;31m', # Bold Red
    'RESET': '\033[0m'     # Сброс цвета
}


class EngineError(Exception):
    ...


class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelname in COLORS:
            levelname = record.levelname
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['RESET']}"
        return super().format(record)
    

class Variable:
    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        return type(other) is Variable and self.value == other.value
    
    def __str__(self):
        return f'Variable({self.value})'
    
    def __repr__(self):
        return str(self)


class Operation:
    def __init__(self, op: str, children: Sequence["Operation"]):
        self.op = op
        self.children = children

    def __eq__(self, other):
        return type(self) is type(other) \
               and (self.children == other.children
                    or reversed(self.children) == other.children)
    
    def __str__(self):
        return f'{self.op}({",".join(str(child) for child in self.children)})'
    
    def __repr__(self):
        return str(self)


class Disjunction(Operation):
    def __init__(self, children: Sequence[Operation | Variable]):
        super().__init__(lexer.TokenType.OR.value, children)


class Conjunction(Operation):
    def __init__(self, children: Sequence[Operation | Variable]):
        super().__init__(lexer.TokenType.AND.value, children)


class Negation(Operation):
    def __init__(self, children: Operation | Variable | Sequence[Operation | Variable]):
        if isinstance(children, (Operation, Variable)):
            self.child = children
            super().__init__(lexer.TokenType.NOT.value, (children,))
        else:
            self.child = children[0]
            super().__init__(lexer.TokenType.NOT.value, children)
            

class Implication(Operation):
    def __init__(self, children: Sequence[Operation | Variable]):
        super().__init__(lexer.TokenType.IMPLIES.value, children)


class Equivalence(Operation):
    def __init__(self, children: Sequence[Operation | Variable]):
        super().__init__(lexer.TokenType.EQUIVALENCE.value, children)


class Disjunct(Disjunction):
    def __init__(self, operation: Operation):
        children = list(operation.children)
        i = 0
        while i < len(children):
            if type(children[i]) is Disjunction:
                disjunct = children.pop(i)
                children.append(disjunct.children[0])
                children.append(disjunct.children[1])
            else:
                i += 1
        super().__init__(children)

    def __eq__(self, other: "Disjunct"):
        for child in self.children:
            if child not in other.children:
                return False
        return True


class CNF(Conjunction):
    def __init__(self, operation: Operation):
        children = list(operation.children)
        i = 0
        while i < len(children):
            if type(children[i]) is Conjunction:
                conjunct = children.pop(i)
                children.append(conjunct.children[0])
                children.append(conjunct.children[1])
            elif type(children[i]) is Disjunction:
                children[i] = Disjunct(children[i])
                i += 1
            else:
                i += 1
        super().__init__(children)

    def __eq__(self, other: "CNF"):
        for child in self.children:
            if child not in other.children:
                return False
        return True


class LogicalEngine:
    def __init__(self, level = logging.INFO,
                       text: str | None = None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        formatter = ColorFormatter('%(asctime)s - %(levelname)s - '
                                   '%(funcName)s(): %(lineno)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        self.lexer = Lexer(text=text)

    def parse_line(self):
        try:
            tokens = self.lexer.tokenize()
            self.logger.info('%s', tokens)
        except LexerException as e:
            self.logger.error('%s', e)

    @staticmethod
    def remove_equivalences(operation: Operation | Variable) -> Operation | Variable:
        if type(operation) is Equivalence:
            new_children = (
                LogicalEngine.remove_equivalences(operation.children[0]),
                LogicalEngine.remove_equivalences(operation.children[1])
            )
            return Conjunction((
                Disjunction((
                    Negation(new_children[0]),
                    new_children[1]
                )),
                Disjunction((
                    new_children[0],
                    Negation(new_children[1])
                ))
            ))
        elif type(operation) in (Conjunction, Disjunction, Negation, Implication):
            new_children = tuple(
                LogicalEngine.remove_equivalences(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif type(operation) is Variable:
            return operation

    @staticmethod
    def remove_implications(operation: Operation | Variable) -> Operation | Variable:
        if type(operation) is Implication:
            new_children = (
                Negation(
                    LogicalEngine.remove_implications(operation.children[0])
                ),
                LogicalEngine.remove_implications(operation.children[1])
            )
            return Disjunction(new_children)
        elif type(operation) in (Conjunction, Disjunction, Negation, Equivalence):
            new_children = tuple(
                LogicalEngine.remove_implications(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif type(operation) is Variable:
            return operation
        
    @staticmethod
    def remove_double_negations(operation: Operation | Variable) -> Operation | Variable:
        if type(operation) is Negation and \
            type(operation.child) is Negation:
            return LogicalEngine.remove_double_negations(operation.child.child)
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.remove_double_negations(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif type(operation) is Variable:
            return operation
        
    @staticmethod
    def apply_de_morgan(operation: Operation | Variable) -> Operation | Variable:
        if type(operation) is Negation:
            if type(operation.child) in (Conjunction, Disjunction):
                new_children = tuple(
                    LogicalEngine.apply_de_morgan(
                        Negation(child)
                    ) for child in operation.child.children
                )
                if type(operation.child) is Conjunction:
                    return Disjunction(new_children)
                elif type(operation.child) is Disjunction:
                    return Conjunction(new_children)
            elif type(operation.child) is Negation:
                return LogicalEngine.apply_de_morgan(
                    operation.child.child
                )
            else:
                new_child = LogicalEngine.apply_de_morgan(
                    operation.child
                )
                return Negation(new_child)
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.apply_de_morgan(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif type(operation) is Variable:
            return operation
        
    @staticmethod
    def group_conjunctions(operation: Operation | Variable) -> Operation | Variable:
        if type(operation) is Disjunction:
            first_child, second_child = operation.children
            if type(first_child) is Conjunction:
                return Conjunction((
                    LogicalEngine.group_conjunctions(
                        Disjunction((
                            LogicalEngine.group_conjunctions(second_child),
                            LogicalEngine.group_conjunctions(first_child.children[0])
                        ))
                    ),
                    LogicalEngine.group_conjunctions(
                        Disjunction((
                            LogicalEngine.group_conjunctions(second_child),
                            LogicalEngine.group_conjunctions(first_child.children[1])
                        ))
                    ),
                ))
            elif type(second_child) is Conjunction:
                return Conjunction((
                    LogicalEngine.group_conjunctions(
                        Disjunction((
                            LogicalEngine.group_conjunctions(first_child),
                            LogicalEngine.group_conjunctions(second_child.children[0])
                        ))
                    ),
                    LogicalEngine.group_conjunctions(
                        Disjunction((
                            LogicalEngine.group_conjunctions(first_child),
                            LogicalEngine.group_conjunctions(second_child.children[1])
                        ))
                    ),
                ))
            else:
                processed_first = LogicalEngine.group_conjunctions(first_child)
                processed_second = LogicalEngine.group_conjunctions(second_child)
                disjunction = Disjunction((
                    processed_first, processed_second
                ))
                if type(processed_first) is Conjunction or type(processed_second) is Conjunction:
                    return LogicalEngine.group_conjunctions(
                        disjunction
                    )
                return disjunction
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.group_conjunctions(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif type(operation) is Variable:
            return operation
        
    @staticmethod
    def to_cnf(operation: Operation | Variable) -> CNF | Variable:
        operation = LogicalEngine.remove_equivalences(operation)
        operation = LogicalEngine.remove_implications(operation)
        operation = LogicalEngine.remove_double_negations(operation)
        operation = LogicalEngine.apply_de_morgan(operation)
        operation = LogicalEngine.group_conjunctions(operation)
        return CNF(operation)
