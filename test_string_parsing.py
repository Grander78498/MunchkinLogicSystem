#!/usr/bin/env python3
"""
Тест для проверки обработки строк в кавычках
"""

from lexer import Lexer
from parser import Parser
from models import Variable


def test_string_parsing():
    """Тест обработки строк в кавычках"""
    print("Тест обработки строк в кавычках...")
    
    # Тест 1: Строка с пробелами
    lexer = Lexer()
    tokens = lexer.tokenize_line('"уровень игрока 1 равен 10"')
    
    print(f"  Токены: {tokens}")
    
    # Должен быть один токен идентификатора и EOL
    assert len(tokens) == 2
    assert tokens[0].type.name == "IDENTIFIER"
    assert tokens[0].value == "уровень игрока 1 равен 10"
    assert tokens[1].type.name == "EOL"
    
    print("  ✓ Строка с пробелами обработана корректно")
    
    # Тест 2: Парсинг строки как переменной
    parser = Parser(tokens)
    result = parser.parse()
    
    print(f"  Результат парсинга: {result}")
    
    assert isinstance(result, Variable)
    assert result.name == "уровень игрока 1 равен 10"
    
    print("  ✓ Строка корректно преобразована в переменную")
    
    # Тест 3: Проверка обработки незакрытой строки
    try:
        tokens = lexer.tokenize_line('"незакрытая строка')
        print("  ✗ Незакрытая строка не вызвала ошибку")
        return False
    except Exception as e:
        print(f"  ✓ Незакрытая строка корректно вызвала ошибку: {e}")
    
    return True


def main():
    """Основная функция тестирования"""
    print("Запуск теста обработки строк в кавычках")
    print("=" * 50)
    
    success = test_string_parsing()
    
    print("=" * 50)
    if success:
        print("Тест обработки строк в кавычках пройден!")
    else:
        print("Тест обработки строк в кавычках не пройден.")


if __name__ == "__main__":
    main()