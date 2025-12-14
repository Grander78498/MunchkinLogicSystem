import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from engine import LogicalEngine


def test_unification_in_engine():
    """Тест унификации в движке"""
    # Создаем движок
    engine = LogicalEngine()
    
    # Добавляем аксиому: уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
    input_text = "уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    operation = transformer.transform(ast_nodes[0])
    
    # Добавляем аксиому в движок
    added_axioms = engine.add_axiom(operation)
    
    # Проверяем, что аксиома добавлена
    assert len(added_axioms) > 0
    assert len(engine.axioms) > 0
    
    print("Аксиома добавлена успешно")
    
    # Добавляем факты
    facts = [
        "уровень(игрок(1), 2)",
        "сила(игрок(1), 5)"
    ]
    
    for fact_text in facts:
        tokens = lexer.tokenize(fact_text)
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        operation = transformer.transform(ast_nodes[0])
        engine.add_axiom(operation)
    
    print("Факты добавлены успешно")
    
    # Проверяем, что все добавлено
    assert len(engine.axioms) >= 3
    
    print("Тест унификации в движке пройден успешно!")


if __name__ == "__main__":
    test_unification_in_engine()