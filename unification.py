from typing import Dict, Optional, Set
from models import Predicate, Variable, Term


class UnificationException(Exception):
    """Исключение унификации"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class Substitution:
    """Подстановка переменных"""
    
    def __init__(self, bindings: Dict[str, Predicate] = None):
        self.bindings = bindings if bindings else {}
    
    def bind(self, var_name: str, value: Predicate) -> "Substitution":
        """Создание новой подстановки с добавленной связью"""
        new_bindings = self.bindings.copy()
        new_bindings[var_name] = value
        return Substitution(new_bindings)
    
    def lookup(self, var_name: str) -> Optional[Predicate]:
        """Поиск значения переменной"""
        return self.bindings.get(var_name)
    
    def apply(self, predicate: Predicate) -> Predicate:
        """Применение подстановки к предикату"""
        # Если это переменная, пытаемся заменить её значением
        if isinstance(predicate, Variable):
            value = self.lookup(predicate.name)
            if value is not None:
                # Рекурсивно применяем подстановку к найденному значению
                return self.apply(value)
            return predicate
        
        # Если это терм, пытаемся заменить его значением
        if isinstance(predicate, Term):
            value = self.lookup(predicate.name)
            if value is not None:
                # Рекурсивно применяем подстановку к найденному значению
                return self.apply(value)
            return predicate
        
        # Если это предикат с аргументами, применяем подстановку к аргументам
        if predicate.args is not None:
            new_args = [self.apply(arg) for arg in predicate.args]
            return Predicate(predicate.name, new_args)
        
        # Если это предикат без аргументов, возвращаем его как есть
        return predicate
    
    def compose(self, other: "Substitution") -> "Substitution":
        """Композиция двух подстановок"""
        # Применяем текущую подстановку к значениям из другой подстановки
        new_bindings = {}
        for var, value in other.bindings.items():
            new_bindings[var] = self.apply(value)
        
        # Добавляем связи из текущей подстановки, которых нет в другой
        for var, value in self.bindings.items():
            if var not in new_bindings:
                new_bindings[var] = value
        
        return Substitution(new_bindings)
    
    def __str__(self):
        if not self.bindings:
            return "{}"
        bindings_str = ", ".join(f"{var}: {value}" for var, value in self.bindings.items())
        return f"{{{bindings_str}}}"
    
    def __eq__(self, other):
        if not isinstance(other, Substitution):
            return False
        return self.bindings == other.bindings


def occurs_check(var_name: str, predicate: Predicate) -> bool:
    """Проверка вхождения переменной в предикат (предотвращает бесконечные подстановки)"""
    # Если предикат - это проверяемая переменная, возврат True
    if isinstance(predicate, (Variable, Term)) and predicate.name == var_name:
        return True
    
    # Если у предиката есть аргументы, рекурсивно проверяем их
    if predicate.args is not None:
        return any(occurs_check(var_name, arg) for arg in predicate.args)
    
    return False


def unify(predicate1: Predicate, predicate2: Predicate, substitution: Substitution = None) -> Optional[Substitution]:
    """
    Алгоритм унификации Робинсона
    
    Возвращает подстановку, которая делает два предиката идентичными,
    или None, если унификация невозможна
    """
    if substitution is None:
        substitution = Substitution()
    
    try:
        # Применяем текущую подстановку к обоим предикатам
        predicate1 = substitution.apply(predicate1)
        predicate2 = substitution.apply(predicate2)
        
        # Если предикаты идентичны, унификация успешна
        if predicate1 == predicate2:
            return substitution
        
        # Если первый предикат - переменная
        if isinstance(predicate1, (Variable, Term)):
            return unify_variable(predicate1.name, predicate2, substitution)
        
        # Если второй предикат - переменная
        if isinstance(predicate2, (Variable, Term)):
            return unify_variable(predicate2.name, predicate1, substitution)
        
        # Оба предиката - составные (не переменные)
        # Проверяем, что у них одинаковые имена и количество аргументов
        if not hasattr(predicate1, 'name') or not hasattr(predicate2, 'name'):
            return None
            
        if predicate1.name != predicate2.name:
            return None
        
        # Проверяем наличие атрибута args
        if not hasattr(predicate1, 'args') or not hasattr(predicate2, 'args'):
            return None
            
        args1 = predicate1.args or []
        args2 = predicate2.args or []
        if len(args1) != len(args2):
            return None
        
        # Если у предикатов нет аргументов, они уже унифицированы
        if not predicate1.args:
            return substitution
        
        # Рекурсивно унифицируем аргументы
        for arg1, arg2 in zip(predicate1.args, predicate2.args):
            substitution = unify(arg1, arg2, substitution)
            if substitution is None:
                return None
        
        return substitution
    except Exception:
        # В случае любой ошибки возвращаем None
        return None


def unify_variable(var_name: str, predicate: Predicate, substitution: Substitution) -> Optional[Substitution]:
    """Унификация переменной с предикатом"""
    # Проверка occurs check
    if occurs_check(var_name, predicate):
        return None
    
    # Если переменная уже имеет значение, унифицируем это значение с предикатом
    var_value = substitution.lookup(var_name)
    if var_value is not None:
        return unify(var_value, predicate, substitution)
    
    # Связываем переменную с предикатом
    return substitution.bind(var_name, predicate)


def unify_list(predicates: list[Predicate]) -> Optional[Substitution]:
    """
    Унификация списка предикатов
    
    Возвращает подстановку, которая делает все предикаты идентичными,
    или None, если унификация невозможна
    """
    if not predicates:
        return Substitution()
    
    if len(predicates) == 1:
        return Substitution()
    
    # Начинаем с унификации первых двух предикатов
    substitution = unify(predicates[0], predicates[1])
    if substitution is None:
        return None
    
    # Последовательно унифицируем остальные предикаты
    for i in range(2, len(predicates)):
        # Применяем текущую подстановку к следующему предикату
        unified_pred = substitution.apply(predicates[i])
        # Унифицируем с первым предикатом (который уже унифицирован)
        first_pred = substitution.apply(predicates[0])
        next_substitution = unify(first_pred, unified_pred)
        if next_substitution is None:
            return None
        # Композиция подстановок
        substitution = substitution.compose(next_substitution)
    
    return substitution