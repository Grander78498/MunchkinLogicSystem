import os
import sys

from models import (
    Predicate,
    Conjunction,
    Disjunction,
    Implication,
    Equivalence,
    Negation,
    CNF,
    Operation,
    Disjunct,
    Variable,
)

# Импортируем базу знаний
from knowledge_base import KnowledgeBase


class EngineError(Exception): ...


class LogicalEngine:
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.kb = knowledge_base or KnowledgeBase()
        self.axioms: list[Disjunct] = []

    def load_axioms_from_kb(self):
        """Загрузить аксиомы из базы знаний в движок"""
        self.axioms.clear()
        for axiom in self.kb.get_all_axioms():
            cnf = self.to_cnf(axiom.expression, output=False)
            if cnf.children:
                self.axioms.extend(cnf.children)

    def load_statements_from_kb(self):
        """Загрузить высказывания из базы знаний в движок как единичные дизъюнкты"""
        for statement in self.kb.get_all_statements():
            # Создаем единичный дизъюнкт из высказывания
            variable = Variable(statement.name)
            disjunct = Disjunct(predicates=[variable])
            self.axioms.append(disjunct)

    def add_axiom(self, operation: Operation) -> list[Disjunct]:
        cnf = self.to_cnf(operation, output=True)
        if cnf.children:
            self.axioms.extend(cnf.children)
        return cnf.children

    def resolution_method(self, operation: Operation):
        # Загружаем аксиомы и высказывания из базы знаний перед началом
        self.load_axioms_from_kb()
        self.load_statements_from_kb()
        
        for i in range(len(self.axioms)):
            print(f"({i + 1}) {self.axioms[i]}")

        cnf = self.to_cnf(Negation(operation), output=True)

        if cnf.children:
            print("Новые дизъюнкты")
            for i in range(len(cnf.children)):
                print(f"({len(self.axioms) + i + 1}) {cnf.children[i]}")
            print()

            i = 0
            new_axioms = cnf.children
            visited = []
            while i < len(self.axioms) + len(new_axioms):
                if i >= len(self.axioms):
                    i_axiom = new_axioms[i - len(self.axioms)]
                else:
                    i_axiom = self.axioms[i]
                j = 0
                while j < len(new_axioms):
                    if (i, j) in visited:
                        j += 1
                        continue
                    visited.append((i, j))
                    j_axiom = new_axioms[j]
                    resolve, has_contrary = i_axiom.add_predicate(j_axiom)
                    if has_contrary:
                        first_str = f"({i + 1}) {i_axiom}"
                        second_str = f"({len(self.axioms) + j + 1}) {j_axiom}"
                        max_len = max(len(first_str), len(second_str))
                        if len(first_str) == max_len:
                            first_str += " |"
                            second_str += " " * (max_len - len(second_str)) + " |"
                        else:
                            second_str += " |"
                            first_str += " " * (max_len - len(first_str)) + " |"
                        print(first_str)
                        if len(resolve.children) == 0:
                            print(
                                " " * max_len
                                + f" |--> Пустой дизъюнкт - теорема доказана."
                            )
                        else:
                            new_axioms.append(resolve)
                            visited.append((i, len(new_axioms) - 1))
                            print(
                                " " * max_len
                                + f" |--> ({len(self.axioms) + len(new_axioms)}) {resolve}"
                            )

                        print(second_str)
                        print("\n\n")
                        if len(resolve.children) == 0:
                            return
                    j += 1
                i += 1
            print("Не удалось образовать пустой дизъюнкт, теорема не доказана")

    @staticmethod
    def remove_equivalences(operation: Operation | Predicate) -> Operation | Predicate:
        if type(operation) is Equivalence:
            new_children = (
                LogicalEngine.remove_equivalences(operation.children[0]),
                LogicalEngine.remove_equivalences(operation.children[1]),
            )
            return Conjunction(
                (
                    Disjunction((Negation(new_children[0]), new_children[1])),
                    Disjunction((new_children[0], Negation(new_children[1]))),
                )
            )
        elif type(operation) in (Conjunction, Disjunction, Negation, Implication):
            new_children = tuple(
                LogicalEngine.remove_equivalences(child) for child in operation.children
            )
            return type(operation)(new_children)
        elif isinstance(operation, Predicate):
            return operation

    @staticmethod
    def remove_implications(operation: Operation | Predicate) -> Operation | Predicate:
        if type(operation) is Implication:
            new_children = (
                Negation(LogicalEngine.remove_implications(operation.children[0])),
                LogicalEngine.remove_implications(operation.children[1]),
            )
            return Disjunction(new_children)
        elif type(operation) in (Conjunction, Disjunction, Negation, Equivalence):
            new_children = tuple(
                LogicalEngine.remove_implications(child) for child in operation.children
            )
            return type(operation)(new_children)
        elif isinstance(operation, Predicate):
            return operation

    @staticmethod
    def remove_double_negations(
        operation: Operation | Predicate,
    ) -> Operation | Predicate:
        if type(operation) is Negation and type(operation.child) is Negation:
            return LogicalEngine.remove_double_negations(operation.child.child)
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.remove_double_negations(child)
                for child in operation.children
            )
            return type(operation)(new_children)
        elif isinstance(operation, Predicate):
            return operation

    @staticmethod
    def apply_de_morgan(operation: Operation | Predicate) -> Operation | Predicate:
        if type(operation) is Negation:
            if type(operation.child) in (Conjunction, Disjunction):
                new_children = tuple(
                    LogicalEngine.apply_de_morgan(Negation(child))
                    for child in operation.child.children
                )
                if type(operation.child) is Conjunction:
                    return Disjunction(new_children)
                elif type(operation.child) is Disjunction:
                    return Conjunction(new_children)
            elif type(operation.child) is Negation:
                return LogicalEngine.apply_de_morgan(operation.child.child)
            else:
                new_child = LogicalEngine.apply_de_morgan(operation.child)
                return Negation(new_child)
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.apply_de_morgan(child) for child in operation.children
            )
            return type(operation)(new_children)
        elif isinstance(operation, Predicate):
            return operation

    @staticmethod
    def group_conjunctions(operation: Operation | Predicate) -> Operation | Predicate:
        if type(operation) is Disjunction:
            first_child, second_child = operation.children
            if type(first_child) is Conjunction:
                return Conjunction(
                    (
                        LogicalEngine.group_conjunctions(
                            Disjunction(
                                (
                                    LogicalEngine.group_conjunctions(second_child),
                                    LogicalEngine.group_conjunctions(
                                        first_child.children[0]
                                    ),
                                )
                            )
                        ),
                        LogicalEngine.group_conjunctions(
                            Disjunction(
                                (
                                    LogicalEngine.group_conjunctions(second_child),
                                    LogicalEngine.group_conjunctions(
                                        first_child.children[1]
                                    ),
                                )
                            )
                        ),
                    )
                )
            elif type(second_child) is Conjunction:
                return Conjunction(
                    (
                        LogicalEngine.group_conjunctions(
                            Disjunction(
                                (
                                    LogicalEngine.group_conjunctions(first_child),
                                    LogicalEngine.group_conjunctions(
                                        second_child.children[0]
                                    ),
                                )
                            )
                        ),
                        LogicalEngine.group_conjunctions(
                            Disjunction(
                                (
                                    LogicalEngine.group_conjunctions(first_child),
                                    LogicalEngine.group_conjunctions(
                                        second_child.children[1]
                                    ),
                                )
                            )
                        ),
                    )
                )
            else:
                processed_first = LogicalEngine.group_conjunctions(first_child)
                processed_second = LogicalEngine.group_conjunctions(second_child)
                disjunction = Disjunction((processed_first, processed_second))
                if (
                    type(processed_first) is Conjunction
                    or type(processed_second) is Conjunction
                ):
                    return LogicalEngine.group_conjunctions(disjunction)
                return disjunction
        elif isinstance(operation, Operation):
            new_children = tuple(
                LogicalEngine.group_conjunctions(child) for child in operation.children
            )
            return type(operation)(new_children)
        elif isinstance(operation, Predicate):
            return operation

    @staticmethod
    def to_cnf(
        operation: Operation | Predicate, output: bool = False
    ) -> CNF | Predicate:
        if not output:
            devnull = open(os.devnull, "w")
            stdout = devnull
        else:
            stdout = sys.stdout
        print("============", file=stdout)
        print(f"Исходное выражение: {operation}", file=stdout)
        operation = LogicalEngine.remove_equivalences(operation)
        operation = LogicalEngine.remove_implications(operation)
        operation = LogicalEngine.remove_double_negations(operation)
        print(
            f"После избавления от эквиваленций, импликаций и двойных отрицаний: {operation}",
            file=stdout,
        )
        operation = LogicalEngine.apply_de_morgan(operation)
        print(f"После применения законов де Моргана: {operation}", file=stdout)
        operation = LogicalEngine.group_conjunctions(operation)
        print(f"После группировки конъюнкций: {operation}", file=stdout)
        cnf = CNF(operation)
        print(f"КНФ: {cnf}", file=stdout)
        cnf.simplify()
        print(f"Упрощённая КНФ: {cnf}", file=stdout)
        print("============\n", file=stdout)

        if not output:
            devnull.close()
        return cnf
