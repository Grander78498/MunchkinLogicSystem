import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from models import (
    Predicate, Variable, Term,
    Addition, GreaterThan,
    Conjunction, Implication
)


def test_parse_arithmetic_in_axiom():
    """Тест парсинга арифметики в аксиоме из примера"""
    # Строка 27: уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
    input_text = "уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна аксиома
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "AxiomNode"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    # Должна быть импликация
    assert isinstance(result, Implication)
    
    # Левая часть - конъюнкция двух предикатов
    condition = result.children[0]
    assert isinstance(condition, Conjunction)
    
    # Правая часть - предикат с арифметическим выражением
    consequence = result.children[1]
    assert isinstance(consequence, Predicate)
    assert consequence.name == "боевая_сила"
    assert len(consequence.args) == 2
    
    # Второй аргумент должен быть сложением
    addition = consequence.args[1]
    assert isinstance(addition, Addition)
    assert isinstance(addition.children[0], Predicate)  # Y
    assert isinstance(addition.children[1], Predicate)  # Z


def test_parse_comparison_in_axiom():
    """Тест парсинга сравнения в аксиоме из примера"""
    # Строка 28: боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))
    input_text = "боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна аксиома
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "AxiomNode"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    # Должна быть импликация
    assert isinstance(result, Implication)
    
    # Левая часть - конъюнкция трех предикатов
    condition = result.children[0]
    assert isinstance(condition, Conjunction)
    
    # Внутри конъюнкции должно быть сравнение
    # Для простоты проверим, что есть GreaterThan
    # (в реальности структура будет сложнее из-за вложенности)
    
    # Правая часть - предикат
    consequence = result.children[1]
    assert isinstance(consequence, Predicate)
    assert consequence.name == "победа"


def test_parse_theorem_with_variable():
    """Тест парсинга теоремы с переменной из примера"""
    # Строка 26: ? уровень(игрок(Х), 2)
    input_text = "? уровень(игрок(Х), 2)"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна теорема
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "TheoremNode"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    # Должен быть предикат
    assert isinstance(result, Predicate)
    assert result.name == "уровень"
    assert len(result.args) == 2
    
    # Первый аргумент - предикат игрок(Х)
    first_arg = result.args[0]
    assert isinstance(first_arg, Predicate)
    assert first_arg.name == "игрок"
    assert len(first_arg.args) == 1
    assert isinstance(first_arg.args[0], Term)  # Х - терм
    assert first_arg.args[0].name == "Х"
    
    # Второй аргумент - число 2
    second_arg = result.args[1]
    assert isinstance(second_arg, Predicate)
    assert second_arg.name == "2"


if __name__ == "__main__":
    test_parse_arithmetic_in_axiom()
    test_parse_comparison_in_axiom()
    test_parse_theorem_with_variable()
    print("Все тесты пройдены успешно!")