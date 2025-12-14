import pytest
from knowledge_base import KnowledgeBase, Statement, Axiom
from models import Variable, Conjunction, Implication


def test_kb_creation():
    """Тест создания базы знаний"""
    kb = KnowledgeBase()
    assert len(kb.statements) == 0
    assert len(kb.axioms) == 0


def test_add_statement():
    """Тест добавления высказывания"""
    kb = KnowledgeBase()
    
    # Добавляем высказывание
    stmt = kb.add_statement("игрок_1", "Первый игрок")
    
    # Проверяем, что оно добавилось
    assert isinstance(stmt, Statement)
    assert stmt.id == 1
    assert stmt.name == "игрок_1"
    assert stmt.description == "Первый игрок"
    
    # Проверяем, что оно доступно по имени
    retrieved = kb.get_statement("игрок_1")
    assert retrieved is not None
    assert retrieved.id == stmt.id
    assert retrieved.name == stmt.name
    
    # Проверяем, что при повторном добавлении возвращается тот же объект
    same_stmt = kb.add_statement("игрок_1")
    assert same_stmt.id == stmt.id


def test_add_axiom():
    """Тест добавления аксиомы"""
    kb = KnowledgeBase()
    
    # Создаем выражение для аксиомы
    expr = Implication((
        Conjunction((Variable("a"), Variable("b"))),
        Variable("c")
    ))
    
    # Добавляем аксиому
    axiom = kb.add_axiom(expr, "Если a и b, то c")
    
    # Проверяем, что она добавилась
    assert isinstance(axiom, Axiom)
    assert axiom.id == 1
    assert str(axiom.expression) == str(expr)
    assert axiom.description == "Если a и b, то c"
    
    # Проверяем, что она доступна по ID
    retrieved = kb.get_axiom(1)
    assert retrieved is not None
    assert retrieved.id == axiom.id
    assert str(retrieved.expression) == str(axiom.expression)


def test_remove_axiom():
    """Тест удаления аксиомы"""
    kb = KnowledgeBase()
    
    # Добавляем аксиому
    expr = Variable("a")
    axiom = kb.add_axiom(expr)
    
    # Удаляем аксиому
    result = kb.remove_axiom(axiom.id)
    assert result is True
    
    # Проверяем, что она удалена
    retrieved = kb.get_axiom(axiom.id)
    assert retrieved is None
    
    # Проверяем, что при попытке удалить несуществующую аксиому возвращается False
    result = kb.remove_axiom(999)
    assert result is False


def test_get_all_statements():
    """Тест получения всех высказываний"""
    kb = KnowledgeBase()
    
    # Добавляем несколько высказываний
    stmt1 = kb.add_statement("a")
    stmt2 = kb.add_statement("b")
    stmt3 = kb.add_statement("c")
    
    # Получаем все высказывания
    statements = kb.get_all_statements()
    
    # Проверяем, что они в правильном порядке
    assert len(statements) == 3
    assert statements[0].id == stmt1.id
    assert statements[1].id == stmt2.id
    assert statements[2].id == stmt3.id


def test_get_all_axioms():
    """Тест получения всех аксиом"""
    kb = KnowledgeBase()
    
    # Добавляем несколько аксиом
    expr1 = Variable("a")
    expr2 = Variable("b")
    expr3 = Variable("c")
    
    axiom1 = kb.add_axiom(expr1)
    axiom2 = kb.add_axiom(expr2)
    axiom3 = kb.add_axiom(expr3)
    
    # Получаем все аксиомы
    axioms = kb.get_all_axioms()
    
    # Проверяем, что они все есть
    assert len(axioms) == 3
    assert axiom1 in axioms
    assert axiom2 in axioms
    assert axiom3 in axioms


def test_clear():
    """Тест очистки базы знаний"""
    kb = KnowledgeBase()
    
    # Добавляем данные
    kb.add_statement("a")
    kb.add_axiom(Variable("b"))
    
    # Очищаем базу знаний
    kb.clear()
    
    # Проверяем, что она пуста
    assert len(kb.statements) == 0
    assert len(kb.axioms) == 0
    
    # Проверяем, что ID сброшены
    stmt = kb.add_statement("new")
    axiom = kb.add_axiom(Variable("new_axiom"))
    
    assert stmt.id == 1
    assert axiom.id == 1