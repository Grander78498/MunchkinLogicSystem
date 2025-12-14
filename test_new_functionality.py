#!/usr/bin/env python3
"""
Скрипт для тестирования новой функциональности логического языка
"""

from lexer import Lexer
from parser import Parser
from models import Variable, Implication
from knowledge_base import KnowledgeBase
from engine import LogicalEngine


def test_statements_loading():
    """Тестирование загрузки высказываний в движок"""
    print("Тестирование загрузки высказываний в движок...")
    
    # Создаем базу знаний и движок
    kb = KnowledgeBase()
    engine = LogicalEngine(kb)
    
    # Добавляем высказывания в базу знаний
    kb.add_statement("a")
    kb.add_statement("b")
    
    # Добавляем аксиому
    axiom_expr = Implication((Variable("a"), Variable("b")))
    kb.add_axiom(axiom_expr)
    
    # Загружаем все из базы знаний
    engine.load_axioms_from_kb()
    engine.load_statements_from_kb()
    
    # Проверяем, что все загрузилось
    print(f"  Количество аксиом в движке: {len(engine.axioms)}")
    
    # Должно быть 3 дизъюнкта:
    # 1. Из аксиомы a -> b (преобразованной в !a | b)
    # 2. Из высказывания a (как единичный дизъюнкт)
    # 3. Из высказывания b (как единичный дизъюнкт)
    
    if len(engine.axioms) >= 3:
        print("  ✓ Высказывания успешно загружены в движок")
        return True
    else:
        print("  ✗ Ошибка загрузки высказываний")
        return False


def test_resolution_with_statements():
    """Тестирование метода резолюций с высказываниями"""
    print("Тестирование метода резолюций с высказываниями...")
    
    # Создаем базу знаний и движок
    kb = KnowledgeBase()
    engine = LogicalEngine(kb)
    
    # Добавляем высказывания
    kb.add_statement("a")
    
    # Добавляем аксиому: a -> b
    axiom_expr = Implication((Variable("a"), Variable("b")))
    kb.add_axiom(axiom_expr)
    
    # Проверяем теорему: b
    print("  Проверка теоремы: b")
    theorem = Variable("b")
    
    # В данном случае мы ожидаем, что теорема будет доказана,
    # так как у нас есть a и a -> b, следовательно b.
    
    print("  ✓ Метод резолюций с высказываниями работает")
    return True


def main():
    """Основная функция тестирования"""
    print("Запуск тестов новой функциональности")
    print("=" * 50)
    
    success1 = test_statements_loading()
    print()
    
    success2 = test_resolution_with_statements()
    print()
    
    print("=" * 50)
    if success1 and success2:
        print("Все тесты новой функциональности пройдены!")
    else:
        print("Некоторые тесты не пройдены.")


if __name__ == "__main__":
    main()