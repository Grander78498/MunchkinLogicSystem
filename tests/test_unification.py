import pytest
from models import Predicate, Variable, Term
from unification import Substitution, unify, unify_list, UnificationException


def test_substitution_bind_and_lookup():
    """Тест создания подстановки и поиска значений"""
    subst = Substitution()
    subst = subst.bind("X", Predicate("a", None))
    
    assert subst.lookup("X").name == "a"
    assert subst.lookup("Y") is None


def test_substitution_apply_variable():
    """Тест применения подстановки к переменной"""
    subst = Substitution()
    subst = subst.bind("X", Predicate("a", None))
    
    var_x = Variable("X")
    result = subst.apply(var_x)
    
    assert isinstance(result, Predicate)
    assert result.name == "a"


def test_substitution_apply_predicate():
    """Тест применения подстановки к предикату с аргументами"""
    subst = Substitution()
    subst = subst.bind("X", Predicate("a", None))
    
    pred = Predicate("p", [Variable("X"), Predicate("b", None)])
    result = subst.apply(pred)
    
    assert isinstance(result, Predicate)
    assert result.name == "p"
    assert len(result.args) == 2
    assert isinstance(result.args[0], Predicate)
    assert result.args[0].name == "a"
    assert isinstance(result.args[1], Predicate)
    assert result.args[1].name == "b"


def test_substitution_compose():
    """Тест композиции подстановок"""
    subst1 = Substitution()
    subst1 = subst1.bind("X", Predicate("a", None))
    
    subst2 = Substitution()
    subst2 = subst2.bind("Y", Variable("X"))
    
    composed = subst1.compose(subst2)
    
    # После композиции Y должен быть заменен на a (через X)
    assert composed.lookup("Y").name == "a"


def test_unify_identical():
    """Тест унификации идентичных предикатов"""
    pred1 = Predicate("p", [Predicate("a", None), Predicate("b", None)])
    pred2 = Predicate("p", [Predicate("a", None), Predicate("b", None)])
    
    result = unify(pred1, pred2)
    
    assert result is not None
    assert len(result.bindings) == 0  # Нет новых связей


def test_unify_variable_with_constant():
    """Тест унификации переменной с константой"""
    pred1 = Predicate("p", [Variable("X"), Predicate("a", None)])
    pred2 = Predicate("p", [Predicate("b", None), Predicate("a", None)])
    
    result = unify(pred1, pred2)
    
    assert result is not None
    assert result.lookup("X").name == "b"


def test_unify_constant_with_variable():
    """Тест унификации константы с переменной"""
    pred1 = Predicate("p", [Predicate("a", None), Predicate("b", None)])
    pred2 = Predicate("p", [Variable("X"), Predicate("b", None)])
    
    result = unify(pred1, pred2)
    
    assert result is not None
    assert result.lookup("X").name == "a"


def test_unify_two_variables():
    """Тест унификации двух переменных"""
    pred1 = Predicate("p", [Variable("X"), Predicate("a", None)])
    pred2 = Predicate("p", [Variable("Y"), Predicate("a", None)])
    
    result = unify(pred1, pred2)
    
    assert result is not None
    # Одна переменная должна быть связана с другой
    assert (result.lookup("X") is not None) or (result.lookup("Y") is not None)


def test_unify_nested_predicates():
    """Тест унификации вложенных предикатов"""
    pred1 = Predicate("p", [Predicate("f", [Variable("X")]), Variable("Y")])
    pred2 = Predicate("p", [Predicate("f", [Predicate("a", None)]), Predicate("b", None)])
    
    result = unify(pred1, pred2)
    
    assert result is not None
    assert result.lookup("X").name == "a"
    assert result.lookup("Y").name == "b"


def test_unify_fail_different_names():
    """Тест неудачной унификации из-за разных имен"""
    pred1 = Predicate("p", [Predicate("a", None)])
    pred2 = Predicate("q", [Predicate("a", None)])
    
    result = unify(pred1, pred2)
    
    assert result is None


def test_unify_fail_different_arity():
    """Тест неудачной унификации из-за разного количества аргументов"""
    pred1 = Predicate("p", [Predicate("a", None)])
    pred2 = Predicate("p", [Predicate("a", None), Predicate("b", None)])
    
    result = unify(pred1, pred2)
    
    assert result is None


def test_occurs_check():
    """Тест проверки вхождения переменной"""
    from unification import occurs_check
    
    # X не входит в a
    assert not occurs_check("X", Predicate("a", None))
    
    # X входит в X
    assert occurs_check("X", Variable("X"))
    
    # X входит в f(X)
    assert occurs_check("X", Predicate("f", [Variable("X")]))
    
    # X не входит в f(Y)
    assert not occurs_check("X", Predicate("f", [Variable("Y")]))


def test_unify_occurs_check_fail():
    """Тест неудачной унификации из-за нарушения occurs check"""
    pred1 = Variable("X")
    pred2 = Predicate("f", [Variable("X")])
    
    result = unify(pred1, pred2)
    
    assert result is None


def test_unify_list_success():
    """Тест успешной унификации списка предикатов"""
    pred1 = Predicate("p", [Variable("X"), Predicate("a", None)])
    pred2 = Predicate("p", [Predicate("b", None), Variable("Y")])
    pred3 = Predicate("p", [Variable("Z"), Variable("W")])
    
    result = unify_list([pred1, pred2, pred3])
    
    assert result is not None
    assert result.lookup("X").name == "b"
    assert result.lookup("Y").name == "a"
    assert result.lookup("Z").name == "b"
    assert result.lookup("W").name == "a"


def test_unify_list_fail():
    """Тест неудачной унификации списка предикатов"""
    pred1 = Predicate("p", [Predicate("a", None)])
    pred2 = Predicate("p", [Predicate("b", None)])
    
    result = unify_list([pred1, pred2])
    
    assert result is None


def test_unify_list_empty():
    """Тест унификации пустого списка"""
    result = unify_list([])
    
    assert result is not None
    assert len(result.bindings) == 0


def test_unify_list_single():
    """Тест унификации списка из одного элемента"""
    pred = Predicate("p", [Variable("X"), Predicate("a", None)])
    result = unify_list([pred])
    
    assert result is not None
    assert len(result.bindings) == 0