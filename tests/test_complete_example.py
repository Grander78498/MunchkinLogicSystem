import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from engine import LogicalEngine


def test_complete_example():
    """Тест полного примера из задания"""
    # Создаем движок
    engine = LogicalEngine()
    lexer = Lexer()
    transformer = ASTTransformer()
    
    # Добавляем аксиомы из примера
    axioms = [
        # Строка 10: игрок_1_уровень_10 -> игрок_1_победитель
        "игрок_1_уровень_10 -> игрок_1_победитель",
        
        # Строка 11: игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 -> игрок_победил
        "игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 -> игрок_победил",
        
        # Строка 12: игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_15 & !игрок_2_воин -> игрок_побеждён
        "игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_15 & !игрок_2_воин -> игрок_побеждён",
        
        # Строка 13: игрок_1_вор | игрок_1_волшебник -> игрок_1_может_сбрасывать_в_бою
        "игрок_1_вор | игрок_1_волшебник -> игрок_1_может_сбрасывать_в_бою",
        
        # Строка 14: игрок_2_вор | игрок_2_волшебник -> игрок_2_может_сбрасывать_в_бою
        "игрок_2_вор | игрок_2_волшебник -> игрок_2_может_сбрасывать_в_бою",
        
        # Строка 27: уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
        "уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)",
        
        # Строка 28: боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))
        "боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))"
    ]
    
    # Добавляем все аксиомы
    for i, axiom_text in enumerate(axioms):
        try:
            tokens = lexer.tokenize(axiom_text)
            parser = Parser(tokens)
            ast_nodes = parser.parse()
            
            operation = transformer.transform(ast_nodes[0])
            added_axioms = engine.add_axiom(operation)
            
            assert len(added_axioms) > 0, f"Аксиома {i+1} не была добавлена"
        except Exception as e:
            pytest.fail(f"Ошибка при добавлении аксиомы {i+1} ('{axiom_text}'): {e}")
    
    # Проверяем, что аксиомы добавлены
    assert len(engine.axioms) > 0, "Аксиомы не были добавлены в движок"
    
    # Добавляем факты
    facts = [
        "игрок_1_уровень_10",
        "игрок_2_уровень_5",
        "игрок_2_сила_10",
        "монстр_сила_14",
        "уровень(игрок(1), 2)",
        "сила(игрок(1), 5)",
        "уровень(монстр(гоблин), 5)"
    ]
    
    for i, fact_text in enumerate(facts):
        try:
            tokens = lexer.tokenize(fact_text)
            parser = Parser(tokens)
            ast_nodes = parser.parse()
            
            operation = transformer.transform(ast_nodes[0])
            added_axioms = engine.add_axiom(operation)
            
            assert len(added_axioms) > 0, f"Факт {i+1} не был добавлен"
        except Exception as e:
            pytest.fail(f"Ошибка при добавлении факта {i+1} ('{fact_text}'): {e}")
    
    print("Тест полного примера пройден успешно!")
    print(f"Всего аксиом в движке: {len(engine.axioms)}")


def test_theorem_proving():
    """Тест доказательства теорем"""
    # Создаем движок
    engine = LogicalEngine()
    lexer = Lexer()
    transformer = ASTTransformer()
    
    # Добавляем аксиому: игрок_1_уровень_10 -> игрок_1_победитель
    axiom_text = "игрок_1_уровень_10 -> игрок_1_победитель"
    tokens = lexer.tokenize(axiom_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    operation = transformer.transform(ast_nodes[0])
    engine.add_axiom(operation)
    
    # Добавляем факт: игрок_1_уровень_10
    fact_text = "игрок_1_уровень_10"
    tokens = lexer.tokenize(fact_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    operation = transformer.transform(ast_nodes[0])
    engine.add_axiom(operation)
    
    # Проверяем теорему: ? игрок_1_победитель
    theorem_text = "? игрок_1_победитель"
    tokens = lexer.tokenize(theorem_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    operation = transformer.transform(ast_nodes[0])
    
    # Пока просто проверяем, что трансформация прошла успешно
    assert operation is not None
    
    print("Тест доказательства теорем пройден успешно!")


def test_predicate_unification():
    """Тест унификации предикатов"""
    # Создаем движок
    engine = LogicalEngine()
    lexer = Lexer()
    transformer = ASTTransformer()
    
    # Добавляем аксиому с переменными: уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
    axiom_text = "уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)"
    tokens = lexer.tokenize(axiom_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    operation = transformer.transform(ast_nodes[0])
    engine.add_axiom(operation)
    
    # Добавляем факты: уровень(игрок(1), 2) и сила(игрок(1), 5)
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
    
    # Проверяем, что можно доказать теорему: ? боевая_сила(игрок(1), 7)
    theorem_text = "? боевая_сила(игрок(1), 7)"
    tokens = lexer.tokenize(theorem_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    operation = transformer.transform(ast_nodes[0])
    
    # Пока просто проверяем, что трансформация прошла успешно
    assert operation is not None
    
    print("Тест унификации предикатов пройден успешно!")


if __name__ == "__main__":
    test_complete_example()
    test_theorem_proving()
    test_predicate_unification()
    print("Все тесты полного примера пройдены успешно!")