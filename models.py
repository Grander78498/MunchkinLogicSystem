from typing import Sequence


AND = "*"
OR = "+"
NOT = "!"
EQUALS = "<->"
IMPLIES = "->"


class Predicate:
    def __init__(self, name: str, args: Sequence["Predicate"] | None):
        self.name = name
        self.args = args

    def add_predicate(self, pred) -> "Disjunct":
        disj = Disjunct(predicates=[self])
        resolve, has_contrary = disj.add_predicate(pred)
        return resolve, has_contrary

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False

        if self.name != other.name:
            return False
        match (self.args, other.args):
            case (None, None):
                return True
            case (None, _) | (_, None):
                return False
            case _:
                for arg in self.args:
                    if arg not in other.args:
                        return False
        return True

    def __str__(self):
        if self.args is None:
            return f'"{self.name}"'
        return self.name + "(" + ", ".join(str(arg) for arg in self.args) + ")"

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return False


class Variable(Predicate):
    def __init__(self, name: str):
        super().__init__(name, None)


class Term(Variable):
    def __init__(self, name: str):
        super().__init__(name)


class Operation:
    def __init__(
        self, op: str, children: Sequence["Operation | Predicate"], priority: int
    ):
        self.op = op
        self.children = children
        self.priority = priority

    def __eq__(self, other):
        return type(self) is type(other) and (
            self.children == other.children or reversed(self.children) == other.children
        )

    def __str__(self):
        result = []
        if len(self.children) == 1:
            return str(self.children[0])

        for child in self.children:
            if isinstance(child, Operation) and child.priority >= self.priority:
                result.append(f"({child})")
            else:
                result.append(str(child))
        return f" {self.op} ".join(result)

    def __repr__(self):
        return f"{self.op}({','.join(str(child) for child in self.children)})"


class Disjunction(Operation):
    def __init__(self, children: Sequence[Operation | Predicate]):
        super().__init__(OR, children, priority=2)


class Conjunction(Operation):
    def __init__(self, children: Sequence[Operation | Predicate]):
        super().__init__(AND, children, priority=1)


class Negation(Operation):
    def __init__(
        self, children: Operation | Predicate | Sequence[Operation | Predicate]
    ):
        if isinstance(children, (Operation, Predicate)):
            self.child = children
            super().__init__(NOT, (children,), priority=0)
        else:
            self.child = children[0]
            super().__init__(NOT, children, priority=0)

    def __str__(self):
        if isinstance(self.child, Predicate):
            return f"!{self.child}"
        else:
            return f"!({self.child})"

    def __bool__(self):
        return False

    def add_predicate(self, pred) -> "Disjunct":
        disj = Disjunct(predicates=[self])
        resolve, has_contrary = disj.add_predicate(pred)
        return resolve, has_contrary


class Implication(Operation):
    def __init__(self, children: Sequence[Operation | Predicate]):
        super().__init__(IMPLIES, children, priority=3)


class Equivalence(Operation):
    def __init__(self, children: Sequence[Operation | Predicate]):
        super().__init__(EQUALS, children, priority=3)


class Disjunct(Operation):
    def __init__(
        self,
        operation: Operation | None = None,
        predicates: Sequence[Predicate] | None = None,
    ):
        if predicates is not None:
            super().__init__(OR, predicates, priority=2)
            return

        children = list(operation.children)
        i = 0
        while i < len(children):
            if type(children[i]) is Disjunction:
                disjunct = children.pop(i)
                children.append(disjunct.children[0])
                children.append(disjunct.children[1])
            else:
                i += 1

        visited = []
        for child in children:
            if child not in visited:
                visited.append(child)

        super().__init__(OR, visited, priority=2)

    def add_predicate(self, pred: "Predicate | Disjunct") -> tuple["Disjunct", bool]:
        children = []
        contrary = None
        for child in self.children:
            if contrary is not None:
                children.append(child)
                continue

            if type(pred) is not Disjunct:
                if (
                    type(child) is Negation
                    and Negation(pred) == child
                    or type(pred) is Negation
                    and Negation(child) == pred
                ):
                    contrary = child
                    continue
            else:
                for pred_child in pred.children:
                    if (
                        type(child) is Negation
                        and Negation(pred_child) == child
                        or type(pred_child) is Negation
                        and Negation(child) == pred_child
                    ):
                        contrary = child
                        break
                if contrary is not None:
                    continue
            children.append(child)

        if type(pred) is Disjunct:
            for child in pred.children:
                if (
                    contrary is None
                    or Negation(child) != contrary
                    and child != Negation(contrary)
                ):
                    children.append(child)
        return Disjunct(predicates=children), contrary is not None

    def __eq__(self, other: "Disjunct"):
        if type(other) is not Disjunct:
            if len(self.children) != 1 or self.children[0] != other:
                return False
            return True
        children, other_children = sorted(
            [self.children, other.children], key=lambda x: len(x)
        )
        for child in children:
            if child not in other_children:
                return False
        return True

    def __bool__(self):
        for i in range(len(self.children)):
            for j in range(i + 1, len(self.children)):
                i_child, j_child = self.children[i], self.children[j]
                if (
                    type(i_child) is Negation
                    and Negation(j_child) == i_child
                    or type(j_child) is Negation
                    and Negation(i_child) == j_child
                ):
                    return True
        return False


class CNF(Operation):
    def __init__(
        self,
        operation: Operation | None = None,
        disjuncts: Sequence[Operation] | None = None,
    ):
        if disjuncts is not None:
            super().__init__(AND, disjuncts, priority=1)
            return

        if type(operation) is Disjunction:
            children = [Disjunct(operation)]
            super().__init__(AND, children, priority=1)
            return

        if type(operation) in (Variable, Negation):
            super().__init__(AND, [operation], priority=1)
            return
        
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

        super().__init__(AND, children, priority=1)

    def simplify(self):
        for i in range(len(self.children)):
            for j in range(len(self.children)):
                i_child, j_child = self.children[i], self.children[j]
                if type(i_child) is Disjunct and len(i_child.children) == 1:
                    i_child = i_child.children[0]
                if type(j_child) is Disjunct and len(j_child.children) == 1:
                    j_child = j_child.children[0]
                if (
                    type(i_child) is Negation
                    and Negation(j_child) == i_child
                    or type(j_child) is Negation
                    and Negation(i_child) == j_child
                ):
                    self.children = None
                    return

        new_children = []
        for child in self.children:
            if child not in new_children:
                new_children.append(child)
        self.children = new_children

        i = 0
        while i < len(self.children):
            if bool(self.children[i]):
                self.children.pop(i)
            else:
                i += 1

    def __eq__(self, other: "CNF"):
        match (self.children, other.children):
            case (None, None):
                return True
            case (None, _) | (_, None):
                return False
            case _:
                for child in self.children:
                    if child not in other.children:
                        return False
        return True

    def __bool__(self):
        return all(self.children)

    def __str__(self):
        if self.children is None:
            return "Невыполнима"
        if len(self.children) == 0:
            return "Общезначима"
        return super().__str__()
