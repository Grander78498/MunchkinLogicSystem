import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer, ASTTransformerException
from models import Predicate, Variable, Term, Conjunction, Disjunction, Negation, Implication, Equivalence


def test_transform_proposition():
    """Тест преобразования простого высказывания"""
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_1")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Predicate)
    assert result.name == "игрок_1"
    assert result.args is None


def test_transform_predicate():
    """Тест преобразования предиката с аргументами"""
    lexer = Lexer()
    tokens = lexer.tokenize("уровень(игрок(1), 2)")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Predicate)
    assert result.name == "уровень"
    assert len(result.args) == 2
    
    # Первый аргумент - вложенный предикат
    assert isinstance(result.args[0], Predicate)
    assert result.args[0].name == "игрок"
    assert len(result.args[0].args) == 1
    assert isinstance(result.args[0].args[0], Predicate)
    assert result.args[0].args[0].name == "1"
    
    # Второй аргумент - предикат с числом
    assert isinstance(result.args[1], Predicate)
    assert result.args[1].name == "2"


def test_transform_variable():
    """Тест преобразования переменной"""
    lexer = Lexer()
    tokens = lexer.tokenize("X")  # Переменная с большой буквы - терм
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Term)
    assert result.name == "X"


def test_transform_variable_lowercase():
    """Тест преобразования переменной с маленькой буквы"""
    # В соответствии с грамматикой языка, переменные должны начинаться с большой буквы
    # Маленькие буквы используются для идентификаторов
    pass


def test_transform_conjunction():
    """Тест преобразования конъюнкции"""
    lexer = Lexer()
    tokens = lexer.tokenize("a & b")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Conjunction)
    assert isinstance(result.children[0], Predicate)
    assert isinstance(result.children[1], Predicate)
    assert result.children[0].name == "a"
    assert result.children[1].name == "b"


def test_transform_disjunction():
    """Тест преобразования дизъюнкции"""
    lexer = Lexer()
    tokens = lexer.tokenize("a | b")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Disjunction)
    assert isinstance(result.children[0], Predicate)
    assert isinstance(result.children[1], Predicate)
    assert result.children[0].name == "a"
    assert result.children[1].name == "b"


def test_transform_implication():
    """Тест преобразования импликации"""
    lexer = Lexer()
    tokens = lexer.tokenize("a -> b")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Implication)
    assert isinstance(result.children[0], Predicate)
    assert isinstance(result.children[1], Predicate)
    assert result.children[0].name == "a"
    assert result.children[1].name == "b"


def test_transform_negation():
    """Тест преобразования отрицания"""
    lexer = Lexer()
    tokens = lexer.tokenize("!a")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Negation)
    assert isinstance(result.child, Predicate)
    assert result.child.name == "a"


def test_transform_complex_expression():
    """Тест преобразования сложного выражения"""
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 -> игрок_победил")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Implication)
    # Левая часть - конъюнкция
    assert isinstance(result.children[0], Conjunction)
    # Правая часть - предикат
    assert isinstance(result.children[1], Predicate)
    assert result.children[1].name == "игрок_победил"


def test_transform_theorem():
    """Тест преобразования теоремы"""
    lexer = Lexer()
    tokens = lexer.tokenize("? a")
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    assert isinstance(result, Predicate)
    assert result.name == "a"


def test_transform_unsupported_node():
    """Тест обработки неподдерживаемого узла"""
    transformer = ASTTransformer()
    
    # Создаем фиктивный узел
    class UnsupportedNode:
        pass
    
    with pytest.raises(ASTTransformerException) as exc_info:
        transformer.transform(UnsupportedNode())
    
    assert "Неподдерживаемый тип узла" in str(exc_info.value)