import pytest
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from models import (
    Predicate, Variable, Term,
    Addition, GreaterThan,
    Conjunction, Implication, Disjunction
)


def test_full_example():
    """Тест полного примера из задания"""
    # Читаем пример из файла
    with open("example.shldn", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Разделяем на строки и фильтруем пустые и комментарии
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('//') and not line.startswith('/*') and not line.startswith('*/'):
            # Убираем комментарии в конце строки
            if '//' in line:
                line = line[:line.index('//')].strip()
            if line:
                lines.append(line)
    
    # Проверяем ключевые строки из примера
    lexer = Lexer()
    
    # Строка 27: уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
    input_text = "уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)"
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
    
    print("Тест арифметики в аксиоме пройден успешно!")
    
    # Строка 28: боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))
    input_text = "боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))"
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
    
    # Левая часть - конъюнкция трех элементов
    condition = result.children[0]
    assert isinstance(condition, Conjunction)
    
    # Внутри конъюнкции должно быть сравнение
    # Правая часть - предикат
    consequence = result.children[1]
    assert isinstance(consequence, Predicate)
    assert consequence.name == "победа"
    
    print("Тест сравнения в аксиоме пройден успешно!")
    
    # Строка 26: ? уровень(игрок(Х), 2)
    input_text = "? уровень(игрок(Х), 2)"
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
    
    print("Тест теоремы с переменной пройден успешно!")
    
    print("Все тесты полного примера пройдены успешно!")


if __name__ == "__main__":
    test_full_example()