import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from engine import LogicalEngine


def test_problematic_axiom():
    """Тест проблемной аксиомы"""
    # Тест выражения: боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))
    input_text = "боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))"
    
    print(f"Тестируем выражение: {input_text}")
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    
    # Выведем токены для отладки
    print("Токены:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.type} = '{token.value}' (позиция {token.position})")
    
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    print(f"Количество AST узлов: {len(ast_nodes)}")
    for i, node in enumerate(ast_nodes):
        print(f"  Узел {i}: {node.__class__.__name__}")
        if hasattr(node, 'op'):
            print(f"    Операция: {node.op}")
        if hasattr(node, 'condition'):
            print(f"    Условие: {node.condition.__class__.__name__}")
        if hasattr(node, 'consequence'):
            print(f"    Следствие: {node.consequence.__class__.__name__}")
    
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "AxiomNode"
    
    # Преобразуем в модели
    transformer = ASTTransformer()
    result = transformer.transform(ast_nodes[0])
    
    print(f"Результат трансформации: {result}")
    print(f"Тип результата: {type(result)}")
    
    # Попробуем добавить в движок
    engine = LogicalEngine()
    try:
        added_axioms = engine.add_axiom(result)
        print(f"Аксиома добавлена успешно. Количество новых дизъюнктов: {len(added_axioms)}")
    except Exception as e:
        print(f"Ошибка при добавлении аксиомы в движок: {e}")
        raise
    
    print("Тест проблемной аксиомы пройден успешно!")


if __name__ == "__main__":
    test_problematic_axiom()
    print("Тест проблемной аксиомы пройден успешно!")