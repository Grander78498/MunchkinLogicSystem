import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from models import (
    Predicate, Variable, Term,
    Addition, Subtraction, Multiplication, Division,
    GreaterThan, LessThan, GreaterThanOrEqual, LessThanOrEqual, Equal, NotEqual,
    Conjunction, Disjunction, Negation, Implication
)


def test_transform_arithmetic_addition():
    """Тест преобразования сложения"""
    lexer = Lexer()
    tokens = lexer.tokenize("Y + Z")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Addition)
    assert isinstance(result.children[0], Predicate)  # Y
    assert isinstance(result.children[1], Predicate)  # Z
    assert result.children[0].name == "Y"
    assert result.children[1].name == "Z"


def test_transform_arithmetic_subtraction():
    """Тест преобразования вычитания"""
    lexer = Lexer()
    tokens = lexer.tokenize("A - B")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Subtraction)
    assert isinstance(result.children[0], Predicate)  # A
    assert isinstance(result.children[1], Predicate)  # B
    assert result.children[0].name == "A"
    assert result.children[1].name == "B"


def test_transform_arithmetic_multiplication():
    """Тест преобразования умножения"""
    lexer = Lexer()
    tokens = lexer.tokenize("X * Y")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Multiplication)
    assert isinstance(result.children[0], Predicate)  # X
    assert isinstance(result.children[1], Predicate)  # Y
    assert result.children[0].name == "X"
    assert result.children[1].name == "Y"


def test_transform_arithmetic_division():
    """Тест преобразования деления"""
    lexer = Lexer()
    tokens = lexer.tokenize("A / B")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Division)
    assert isinstance(result.children[0], Predicate)  # A
    assert isinstance(result.children[1], Predicate)  # B
    assert result.children[0].name == "A"
    assert result.children[1].name == "B"


def test_transform_comparison_greater_than():
    """Тест преобразования сравнения больше"""
    lexer = Lexer()
    tokens = lexer.tokenize("X > Y")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, GreaterThan)
    assert isinstance(result.children[0], Predicate)  # X
    assert isinstance(result.children[1], Predicate)  # Y
    assert result.children[0].name == "X"
    assert result.children[1].name == "Y"


def test_transform_comparison_less_than():
    """Тест преобразования сравнения меньше"""
    lexer = Lexer()
    tokens = lexer.tokenize("A < B")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, LessThan)
    assert isinstance(result.children[0], Predicate)  # A
    assert isinstance(result.children[1], Predicate)  # B
    assert result.children[0].name == "A"
    assert result.children[1].name == "B"


def test_transform_comparison_greater_than_or_equal():
    """Тест преобразования сравнения больше или равно"""
    lexer = Lexer()
    tokens = lexer.tokenize("X >= Y")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, GreaterThanOrEqual)
    assert isinstance(result.children[0], Predicate)  # X
    assert isinstance(result.children[1], Predicate)  # Y
    assert result.children[0].name == "X"
    assert result.children[1].name == "Y"


def test_transform_comparison_less_than_or_equal():
    """Тест преобразования сравнения меньше или равно"""
    lexer = Lexer()
    tokens = lexer.tokenize("A <= B")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, LessThanOrEqual)
    assert isinstance(result.children[0], Predicate)  # A
    assert isinstance(result.children[1], Predicate)  # B
    assert result.children[0].name == "A"
    assert result.children[1].name == "B"


def test_transform_comparison_equal():
    """Тест преобразования сравнения равно"""
    lexer = Lexer()
    tokens = lexer.tokenize("X == Y")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Equal)
    assert isinstance(result.children[0], Predicate)  # X
    assert isinstance(result.children[1], Predicate)  # Y
    assert result.children[0].name == "X"
    assert result.children[1].name == "Y"


def test_transform_comparison_not_equal():
    """Тест преобразования сравнения не равно"""
    lexer = Lexer()
    tokens = lexer.tokenize("A != B")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, NotEqual)
    assert isinstance(result.children[0], Predicate)  # A
    assert isinstance(result.children[1], Predicate)  # B
    assert result.children[0].name == "A"
    assert result.children[1].name == "B"


def test_transform_complex_arithmetic_expression():
    """Тест преобразования сложного арифметического выражения"""
    lexer = Lexer()
    tokens = lexer.tokenize("Y + Z")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    # Проверяем сложение
    assert isinstance(result, Addition)
    assert isinstance(result.children[0], Predicate)  # Y
    assert isinstance(result.children[1], Predicate)  # Z
    assert result.children[0].name == "Y"
    assert result.children[1].name == "Z"


def test_transform_arithmetic_in_predicate():
    """Тест преобразования арифметики в предикате"""
    lexer = Lexer()
    tokens = lexer.tokenize("Y + Z")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    # Проверяем арифметическое выражение
    assert isinstance(result, Addition)
    assert isinstance(result.children[0], Predicate)  # Y
    assert isinstance(result.children[1], Predicate)  # Z
    assert result.children[0].name == "Y"
    assert result.children[1].name == "Z"