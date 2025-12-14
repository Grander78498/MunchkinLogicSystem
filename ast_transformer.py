from typing import Union
from parser import (
    ASTNode, PropositionNode, PredicateNode, VariableNode, 
    NumberNode, StringNode, BinaryOpNode, UnaryOpNode, 
    AxiomNode, TheoremNode, CommandNode
)
from models import (
    Predicate, Variable, Term,
    Conjunction, Disjunction, Negation,
    Implication, Equivalence, Operation,
    Addition, Subtraction, Multiplication, Division,
    GreaterThan, LessThan, GreaterThanOrEqual, LessThanOrEqual, Equal, NotEqual
)


class ASTTransformerException(Exception):
    """Исключение преобразователя AST"""
    def __init__(self, message: str, node = None):
        self.message = message
        self.node = node
        if node and hasattr(node, 'position'):
            super().__init__(f"[позиция {node.position}] {message}")
        else:
            super().__init__(message)


class ASTTransformer:
    """Преобразователь AST в модели данных"""
    
    def transform(self, node: ASTNode) -> Union[Predicate, Operation]:
        """Преобразование AST-узла в модель данных"""
        if isinstance(node, PropositionNode):
            return self.transform_proposition(node)
        elif isinstance(node, PredicateNode):
            return self.transform_predicate_node(node)
        elif isinstance(node, VariableNode):
            return self.transform_variable(node)
        elif isinstance(node, NumberNode):
            # Числа преобразуем в предикаты с именем, равным значению числа
            return Predicate(str(node.value), None)
        elif isinstance(node, StringNode):
            # Строки преобразуем в предикаты с именем, равным строке
            return Predicate(node.value, None)
        elif isinstance(node, BinaryOpNode):
            return self.transform_binary_op(node)
        elif isinstance(node, UnaryOpNode):
            return self.transform_unary_op(node)
        elif isinstance(node, AxiomNode):
            return self.transform_axiom(node)
        elif isinstance(node, TheoremNode):
            return self.transform(node.expression)
        else:
            raise ASTTransformerException(f"Неподдерживаемый тип узла: {type(node)}")
    
    def transform_proposition(self, node: PropositionNode) -> Predicate:
        """Преобразование высказывания"""
        return Predicate(node.name, None)
    
    def transform_predicate_node(self, node: PredicateNode) -> Predicate:
        """Преобразование предиката с аргументами"""
        args = [self.transform(arg) for arg in node.args]
        return Predicate(node.name, args)
    
    def transform_variable(self, node: VariableNode) -> Union[Variable, Term]:
        """Преобразование переменной"""
        # В соответствии с примером, переменные, начинающиеся с большой буквы,
        # являются термами, а с маленькой - переменными
        if node.name[0].isupper():
            return Term(node.name)
        else:
            return Variable(node.name)
    
    def transform_binary_op(self, node: BinaryOpNode) -> Operation:
        """Преобразование бинарной операции"""
        left = self.transform(node.left)
        right = self.transform(node.right)
        
        # Логические операции
        if node.op == '&':
            return Conjunction((left, right))
        elif node.op == '|':
            return Disjunction((left, right))
        elif node.op == '->':
            return Implication((left, right))
        elif node.op == '<->':
            return Equivalence((left, right))
        elif node.op == '==':
            return Equal((left, right))
        
        # Арифметические операции
        elif node.op == '+':
            # Если это контекст, где + используется как дизъюнкция, создаем дизъюнкцию
            # В противном случае создаем сложение
            # Для простоты будем считать, что в контексте предикатов + это арифметика
            return Addition((left, right))
        elif node.op == '-':
            return Subtraction((left, right))
        elif node.op == '*':
            # Если это контекст, где * используется как конъюнкция, создаем конъюнкцию
            # В противном случае создаем умножение
            # Для простоты будем считать, что в контексте предикатов * это арифметика
            return Multiplication((left, right))
        elif node.op == '/':
            return Division((left, right))
        
        # Операции сравнения
        elif node.op == '>':
            return GreaterThan((left, right))
        elif node.op == '<':
            return LessThan((left, right))
        elif node.op == '>=':
            return GreaterThanOrEqual((left, right))
        elif node.op == '<=':
            return LessThanOrEqual((left, right))
        elif node.op == '!=':
            return NotEqual((left, right))
        
        else:
            raise ASTTransformerException(f"Неподдерживаемая бинарная операция: {node.op}")
    
    def transform_unary_op(self, node: UnaryOpNode) -> Operation:
        """Преобразование унарной операции"""
        operand = self.transform(node.operand)
        
        if node.op == '!':
            return Negation(operand)
        else:
            raise ASTTransformerException(f"Неподдерживаемая унарная операция: {node.op}")
    
    def transform_axiom(self, node: AxiomNode) -> Implication:
        """Преобразование аксиомы"""
        condition = self.transform(node.condition)
        consequence = self.transform(node.consequence)
        return Implication((condition, consequence))