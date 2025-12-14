import pytest

from lexer import Lexer
from parser import Parser, ParserException, PropositionNode, PredicateNode, VariableNode, NumberNode, StringNode, BinaryOpNode, UnaryOpNode, AxiomNode, TheoremNode, CommandNode


def test_parse_proposition():
    """Тест парсинга простого высказывания"""
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_1")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], PropositionNode)
    assert result[0].name == "игрок_1"


def test_parse_predicate():
    """Тест парсинга предиката"""
    lexer = Lexer()
    tokens = lexer.tokenize("уровень(игрок(1), 2)")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], PredicateNode)
    assert result[0].name == "уровень"
    assert len(result[0].args) == 2
    
    # Первый аргумент - вложенный предикат
    assert isinstance(result[0].args[0], PredicateNode)
    assert result[0].args[0].name == "игрок"
    assert len(result[0].args[0].args) == 1
    assert isinstance(result[0].args[0].args[0], NumberNode)
    assert result[0].args[0].args[0].value == 1
    
    # Второй аргумент - число
    assert isinstance(result[0].args[1], NumberNode)
    assert result[0].args[1].value == 2


def test_parse_variable():
    """Тест парсинга переменной"""
    lexer = Lexer()
    tokens = lexer.tokenize("X")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], VariableNode)
    assert result[0].name == "X"


def test_parse_string():
    """Тест парсинга строки"""
    lexer = Lexer()
    tokens = lexer.tokenize('"тестовая строка"')
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], StringNode)
    assert result[0].value == "тестовая строка"


def test_parse_number():
    """Тест парсинга числа"""
    lexer = Lexer()
    tokens = lexer.tokenize("123")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], NumberNode)
    assert result[0].value == 123


def test_parse_conjunction():
    """Тест парсинга конъюнкции"""
    lexer = Lexer()
    tokens = lexer.tokenize("a & b")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], BinaryOpNode)
    assert result[0].op == "&"
    assert isinstance(result[0].left, PropositionNode)
    assert isinstance(result[0].right, PropositionNode)
    assert result[0].left.name == "a"
    assert result[0].right.name == "b"


def test_parse_disjunction():
    """Тест парсинга дизъюнкции"""
    lexer = Lexer()
    tokens = lexer.tokenize("a | b")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], BinaryOpNode)
    assert result[0].op == "|"
    assert isinstance(result[0].left, PropositionNode)
    assert isinstance(result[0].right, PropositionNode)
    assert result[0].left.name == "a"
    assert result[0].right.name == "b"


def test_parse_implication():
    """Тест парсинга импликации"""
    lexer = Lexer()
    tokens = lexer.tokenize("a -> b")  # Импликация без скобок
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], AxiomNode)
    assert isinstance(result[0].condition, PropositionNode)
    assert isinstance(result[0].consequence, PropositionNode)
    assert result[0].condition.name == "a"
    assert result[0].consequence.name == "b"


def test_parse_negation():
    """Тест парсинга отрицания"""
    lexer = Lexer()
    tokens = lexer.tokenize("!a")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], UnaryOpNode)
    assert result[0].op == "!"
    assert isinstance(result[0].operand, PropositionNode)
    assert result[0].operand.name == "a"


def test_parse_axiom():
    """Тест парсинга аксиомы"""
    # Аксиомы должны парситься отдельно, не как часть выражения
    pass


def test_parse_theorem():
    """Тест парсинга теоремы"""
    lexer = Lexer()
    tokens = lexer.tokenize("? a")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], TheoremNode)
    assert isinstance(result[0].expression, PropositionNode)
    assert result[0].expression.name == "a"


def test_parse_command():
    """Тест парсинга команды"""
    lexer = Lexer()
    tokens = lexer.tokenize("load example.shldn")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], CommandNode)
    assert result[0].command == "load"
    assert result[0].args == ["example.shldn"]


def test_parse_complex_expression():
    """Тест парсинга сложного выражения"""
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 -> игрок_победил")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 1
    assert isinstance(result[0], AxiomNode)
    # Проверяем структуру левой части (конъюнкция)
    assert isinstance(result[0].condition, BinaryOpNode)
    assert result[0].condition.op == "&"
    # Проверяем правую часть
    assert isinstance(result[0].consequence, PropositionNode)
    assert result[0].consequence.name == "игрок_победил"


def test_parse_error():
    """Тест обработки ошибок парсинга"""
    lexer = Lexer()
    tokens = lexer.tokenize("a & & b")  # Два оператора подряд
    parser = Parser(tokens)
    
    with pytest.raises(ParserException) as exc_info:
        parser.parse()
    
    assert "Неожиданный токен" in str(exc_info.value)


def test_parse_empty():
    """Тест парсинга пустого ввода"""
    lexer = Lexer()
    tokens = lexer.tokenize("")
    parser = Parser(tokens)
    result = parser.parse()
    
    assert len(result) == 0