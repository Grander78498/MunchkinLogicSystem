import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer


def test_comparison_parsing():
    """Тест парсинга операций сравнения"""
    # Тест простого сравнения
    input_text = "Sx > Sm"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "BinaryOpNode"
    assert ast_nodes[0].op == ">"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    from models import GreaterThan
    assert isinstance(result, GreaterThan)
    
    print("Тест парсинга операций сравнения пройден успешно!")


def test_comparison_in_parentheses():
    """Тест сравнения в скобках"""
    # Тест сравнения в скобках
    input_text = "(Sx > Sm)"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "BinaryOpNode"
    assert ast_nodes[0].op == ">"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    from models import GreaterThan
    assert isinstance(result, GreaterThan)
    
    print("Тест парсинга сравнения в скобках пройден успешно!")


def test_complex_expression_with_comparison():
    """Тест сложного выражения с сравнением"""
    # Тест выражения: боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm)
    input_text = "боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm)"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    assert len(ast_nodes) == 1
    # Это будет BinaryOpNode с операцией &
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    from models import Conjunction
    assert isinstance(result, Conjunction)
    
    print("Тест сложного выражения с сравнением пройден успешно!")


if __name__ == "__main__":
    test_comparison_parsing()
    test_comparison_in_parentheses()
    test_complex_expression_with_comparison()
    print("Все тесты парсинга сравнений пройдены успешно!")