
# План разработки логического языка SHLDN (Часть 2)

## Фаза 5: Арифметические операции (продолжение)

### 5.2 Интеграция арифметики в предикаты

Пример из [`example.shldn`](../example.shldn:27):
```
уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
```

Реализация:

```python
class ArithmeticPredicate(Predicate):
    """Предикат с арифметическим выражением"""
    def __init__(self, name: str, args: list, arithmetic_expr=None):
        super().__init__(name, args)
        self.arithmetic_expr = arithmetic_expr
    
    def evaluate_with_bindings(self, bindings: Substitution) -> Predicate:
        """Вычисление арифметического выражения с подстановками"""
        if self.arithmetic_expr:
            value = evaluate_arithmetic(self.arithmetic_expr, bindings.bindings)
            new_args = [bindings.apply(arg) for arg in self.args[:-1]]
            new_args.append(Predicate(str(value), None))
            return Predicate(self.name, new_args)
        return self
```

### 5.3 Операторы сравнения

Пример из [`example.shldn`](../example.shldn:28):
```
боевая_сила(игрок(X), Sx) & уровень(монстр(M), Sm) & (Sx > Sm) -> победа(игрок(X), монстр(M))
```

```python
def evaluate_comparison(comp: Comparison, bindings: Substitution) -> bool:
    """Вычисление операторов сравнения"""
    left_val = evaluate_arithmetic(comp.children[0], bindings.bindings)
    right_val = evaluate_arithmetic(comp.children[1], bindings.bindings)
    
    operators = {
        '>': lambda l, r: l > r,
        '<': lambda l, r: l < r,
        '>=': lambda l, r: l >= r,
        '<=': lambda l, r: l <= r,
        '==': lambda l, r: l == r,
        '!=': lambda l, r: l != r,
    }
    
    return operators[comp.op](left_val, right_val)
```

---

## Фаза 6: Система команд

### 6.1 Архитектура команд

Создать `commands.py`:

```python
from typing import Protocol
from engine import LogicalEngine
from parser import Parser
from lexer import Lexer

class Command(Protocol):
    """Интерфейс команды"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        """Выполнение команды"""
        ...

class LoadCommand:
    """Команда загрузки файла"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        if not args:
            return "Ошибка: не указан файл для загрузки"
        
        filename = args[0]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг и выполнение содержимого файла
            lexer = Lexer()
            tokens = lexer.tokenize(content)
            parser = Parser(tokens)
            statements = parser.parse()
            
            count = 0
            for stmt in statements:
                if isinstance(stmt, AxiomNode):
                    engine.add_axiom(transform_to_model(stmt))
                    count += 1
                elif isinstance(stmt, PredicateNode):
                    engine.add_fact(transform_to_model(stmt))
                    count += 1
            
            return f"Загружено {count} выражений из {filename}"
        except FileNotFoundError:
            return f"Ошибка: файл {filename} не найден"
        except Exception as e:
            return f"Ошибка при загрузке: {str(e)}"

class GetAxiomsCommand:
    """Команда получения всех аксиом"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        if not engine.axioms:
            return "База знаний пуста"
        
        result = ["Аксиомы в базе знаний:"]
        for i, axiom in enumerate(engine.axioms, 1):
            result.append(f"({i}) {axiom}")
        
        return "\n".join(result)

class GetFactsCommand:
    """Команда получения всех фактов"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        if not engine.facts:
            return "Нет фактов в базе знаний"
        
        result = ["Факты в базе знаний:"]
        for i, fact in enumerate(engine.facts, 1):
            result.append(f"({i}) {fact}")
        
        return "\n".join(result)

class RemoveCommand:
    """Команда удаления аксиомы"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        if not args:
            return "Ошибка: не указан номер аксиомы"
        
        try:
            index = int(args[0]) - 1
            if 0 <= index < len(engine.axioms):
                removed = engine.axioms.pop(index)
                return f"Удалена аксиома: {removed}"
            else:
                return f"Ошибка: аксиома с номером {args[0]} не существует"
        except ValueError:
            return "Ошибка: номер аксиомы должен быть числом"

class HelpCommand:
    """Команда справки"""
    def execute(self, engine: LogicalEngine, args: list[str]) -> str:
        return """
=== Справка по языку SHLDN ===

СИНТАКСИС:

Комментарии:
  // однострочный комментарий
  /* многострочный комментарий */

Высказывания:
  игрок_1
  монстр_дракон

Аксиомы (правила):
  условие -> следствие
  игрок_1_уровень_10 -> игрок_1_победитель

Логические операторы:
  & или * - конъюнкция (И)
  | или + - дизъюнкция (ИЛИ)
  ! - отрицание (НЕ)
  -> - импликация (ЕСЛИ-ТО)
  == или <-> - эквиваленция (ТОГДА И ТОЛЬКО ТОГДА)

Предикаты:
  уровень(игрок(1), 2)
  сила(игрок(X), 5)

Переменные (термы):
  X, Y, Z - начинаются с большой буквы
  Используются для унификации

Арифметические операции:
  +, -, *, / - базовые операции
  >, <, >=, <=, ==, != - сравнения
  Пример: Y + Z, Sx > Sm

Теоремы (запросы):
  ? игрок_1_победитель
  ? уровень(игрок(X), 2)

КОМАНДЫ:

  load <файл>     - загрузить файл с выражениями
  get axioms      - показать все аксиомы
  get facts       - показать все факты
  remove <номер>  - удалить аксиому по номеру
  help            - показать эту справку
  exit            - выход из программы

ПРИМЕРЫ:

1. Добавление фактов:
   уровень(игрок(1), 2)
   сила(игрок(1), 5)

2. Добавление правила:
   уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)

3. Запрос:
   ? боевая_сила(игрок(1), S)
   Результат: S = 7

4. Загрузка файла:
   load example.shldn

=== Конец справки ===
"""

class CommandRegistry:
    """Реестр команд"""
    def __init__(self):
        self.commands = {
            'load': LoadCommand(),
            'get': self._handle_get_command,
            'remove': RemoveCommand(),
            'help': HelpCommand(),
        }
    
    def _handle_get_command(self, engine: LogicalEngine, args: list[str]) -> str:
        """Обработка команды get с подкомандами"""
        if not args:
            return "Ошибка: не указана подкоманда (axioms, facts)"
        
        subcommand = args[0]
        if subcommand == 'axioms':
            return GetAxiomsCommand().execute(engine, args[1:])
        elif subcommand == 'facts':
            return GetFactsCommand().execute(engine, args[1:])
        else:
            return f"Ошибка: неизвестная подкоманда '{subcommand}'"
    
    def execute(self, command_name: str, engine: LogicalEngine, args: list[str]) -> str:
        """Выполнение команды"""
        if command_name not in self.commands:
            return f"Ошибка: неизвестная команда '{command_name}'"
        
        command = self.commands[command_name]
        if callable(command):
            return command(engine, args)
        return command.execute(engine, args)
```

---

## Фаза 7: REPL-интерфейс

### 7.1 Основной цикл REPL

Создать `repl.py`:

```python
import sys
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from engine import LogicalEngine, EngineError
from commands import CommandRegistry
from ast_transformer import ASTTransformer
from parser import AxiomNode, TheoremNode, CommandNode, PredicateNode

class REPL:
    """Read-Eval-Print Loop для языка SHLDN"""
    
    def __init__(self):
        self.engine = LogicalEngine()
        self.lexer = Lexer()
        self.commands = CommandRegistry()
        self.transformer = ASTTransformer()
        self.running = True
    
    def print_banner(self):
        """Вывод приветствия"""
        print("=" * 60)
        print("  Логический язык программирования SHLDN")
        print("  Версия 1.0")
        print("=" * 60)
        print("Введите 'help' для справки, 'exit' для выхода")
        print()
    
    def read_input(self) -> str:
        """Чтение ввода пользователя"""
        try:
            return input("shldn> ")
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            print("\nИспользуйте 'exit' для выхода")
            return ""
    
    def eval_statement(self, statement):
        """Обработка выражения"""
        try:
            if isinstance(statement, CommandNode):
                # Выполнение команды
                result = self.commands.execute(
                    statement.command,
                    self.engine,
                    statement.args
                )
                print(result)
            
            elif isinstance(statement, AxiomNode):
                # Добавление аксиомы
                axiom = self.transformer.transform(statement)
                disjuncts = self.engine.add_axiom(axiom)
                print(f"Добавлена аксиома: {axiom}")
                if disjuncts:
                    print(f"КНФ: {' * '.join(str(d) for d in disjuncts)}")
            
            elif isinstance(statement, TheoremNode):
                # Доказательство теоремы
                theorem = self.transformer.transform(statement.expression)
                print(f"\nДоказательство: {theorem}")
                print("-" * 60)
                self.engine.resolution_method(theorem)
            
            elif isinstance(statement, PredicateNode):
                # Добавление факта
                fact = self.transformer.transform(statement)
                self.engine.add_fact(fact)
                print(f"Добавлен факт: {fact}")
            
            else:
                # Обычное высказывание
                prop = self.transformer.transform(statement)
                self.engine.add_fact(prop)
                print(f"Добавлено высказывание: {prop}")
        
        except EngineError as e:
            print(f"Ошибка движка: {e}")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")
    
    def process_line(self, line: str):
        """Обработка строки ввода"""
        line = line.strip()
        
        # Пропуск пустых строк
        if not line:
            return
        
        # Команда выхода
        if line.lower() in ('exit', 'quit', 'q'):
            self.running = False
            print("До свидания!")
            return
        
        try:
            # Токенизация
            tokens = self.lexer.tokenize(line)
            
            # Парсинг
            parser = Parser(tokens)
            statements = parser.parse()
            
            # Выполнение
            for statement in statements:
                if statement:
                    self.eval_statement(statement)
        
        except LexerException as e:
            print(f"Ошибка лексера: {e}")
        except ParserException as e:
            print(f"Ошибка парсера: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Запуск REPL"""
        self.print_banner()
        
        while self.running:
            line = self.read_input()
            self.process_line(line)
    
    def run_file(self, filename: str):
        """Выполнение файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Обработка построчно
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('//'):
                    print(f"shldn> {line}")
                    self.process_line(line)
        
        except FileNotFoundError:
            print(f"Ошибка: файл {filename} не найден")
        except Exception as e:
            print(f"Ошибка при выполнении файла: {e}")

def main():
    """Точка входа"""
    repl = REPL()
    
    # Если указан файл в аргументах - выполнить его
    if len(sys.argv) > 1:
        repl.run_file(sys.argv[1])
    else:
        repl.run()

if __name__ == '__main__':
    main()
```

### 7.2 Обновление main.py

Обновить [`main.py`](../main.py:1):

```python
from repl import REPL
import sys

def main():
    repl = REPL()
    
    if len(sys.argv) > 1:
        # Режим выполнения файла
        repl.run_file(sys.argv[1])
    else:
        # Интерактивный режим
        repl.run()

if __name__ == "__main__":
    main()
```

---

## Фаза 8: Расширение логического движка

### 8.1 Поддержка исчисления предикатов

Расширить [`LogicalEngine`](../engine.py:20):

```python
class LogicalEngine:
    def __init__(self):
        self.axioms: list[Disjunct] = []
        self.facts: list[Predicate] = []
        self.rules: list[tuple[Predicate, list[Predicate]]] = []  # (голова, тело)
    
    def add_rule(self, head: Predicate, body: list[Predicate]):
        """Добавление правила (голова :- тело)"""
        self.rules.append((head, body))
    
    def query_with_unification(self, goal: Predicate) -> list[Substitution]:
        """
        Запрос с унификацией
        Возвращает все возможные подстановки
        """
        results = []
        
        # Поиск в фактах
        for fact in self.facts:
            subst = unify(goal, fact)
            if subst:
                results.append(subst)
        
        # Поиск в правилах (backward chaining)
        for head, body in self.rules:
            head_subst = unify(goal, head)
            if head_subst:
                # Доказываем тело правила
                body_results = self.prove_conjunction(body, head_subst)
                results.extend(body_results)
        
        return results
    
    def prove_conjunction(self, goals: list[Predicate], initial_subst: Substitution) -> list[Substitution]:
        """
        Доказательство конъюнкции целей
        """
        if not goals:
            return [initial_subst]
        
        first_goal = initial_subst.apply(goals[0])
        rest_goals = goals[1:]
        
        results = []
        for subst in self.query_with_unification(first_goal):
            # Объединяем подстановки
            combined_subst = self.combine_substitutions(initial_subst, subst)
            # Доказываем остальные цели
            rest_results = self.prove_conjunction(rest_goals, combined_subst)
            results.extend(rest_results)
        
        return results
    
    def combine_substitutions(self, s1: Substitution, s2: Substitution) -> Substitution:
        """Объединение двух подстановок"""
        combined = s1.bindings.copy()
        combined.update(s2.bindings)
        return Substitution(combined)
    
    def resolution_with_predicates(self, goal: Predicate):
        """
        Метод резолюций с поддержкой предикатов
        """
        print(f"Цель: {goal}")
        print("=" * 60)
        
        # Получаем все возможные подстановки
        results = self.query_with_unification(goal)
        
        if not results:
            print("Цель не может быть доказана")
            return
        
        print(f"Найдено решений: {len(results)}")
        for i, subst in enumerate(results, 1):
            print(f"\nРешение {i}:")
            if subst.bindings:
                for var, value in subst.bindings.items():
                    print(f"  {var} = {value}")
            else:
                print("  Да (без подстановок)")
```

### 8.2 Обработка арифметики в правилах

```python
def evaluate_rule_with_arithmetic(self, head: Predicate, body: list[Predicate], subst: Substitution) -> Optional[Predicate]:
    """
    Вычисление правила с арифметическими выражениями
    
    Пример: боевая_сила(игрок(X), Y + Z) при Y=2, Z=5 -> боевая_сила(игрок(X), 7)
    """
    # Применяем подстановку к голове
    new_head = subst.apply(head)
    
    # Если в голове есть арифметические выражения, вычисляем их
    if hasattr(new_head, 'args'):
        new_args = []
        for arg in new_head.args:
            if isinstance(arg, (Addition, Subtraction, Multiplication, Division)):
                value = evaluate_arithmetic(arg, subst.bindings)
                new_args.append(Predicate(str(value), None))
            else:
                new_args.append(arg)
        return Predicate(new_head.name, new_args)
    
    return new_head
```

---

## Фаза 9: Обработка ошибок и валидация

### 9.1 Иерархия исключений

Создать `exceptions.py`:

```python
class SHLDNException(Exception):
    """Базовое исключение для языка SHLDN"""
    pass

class LexerException(SHLDNException):
    """Ошибка лексического анализа"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"[{line}:{column}] {message}")

class ParserException(SHLDNException):
    """Ошибка синтаксического анализа"""
    def __init__(self, message: str, token=None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"[позиция {token.position}] {message}")
        else:
            super().__init__(message)

class UnificationException(SHLDNException):
    """Ошибка унификации"""
    pass

class EngineException(SHLDNException):
    """Ошибка логического движка"""
    pass

class ArithmeticException(SHLDNException):
    """Ошибка вычисления арифметических выражений"""
    pass
```

### 9.2 Валидация входных данных

```python
class Validator:
    """Валидатор выражений"""
    
    @staticmethod
    def validate_predicate(pred: Predicate) -> bool:
        """Проверка корректности предиката"""
        if not pred.name:
            raise ParserException("Имя предиката не может быть пустым")
        
        if pred.args:
            for arg in pred.args:
                if isinstance(arg, Predicate):
                    Validator.validate_predicate(arg)
        
        return True
    
    @staticmethod
    def validate_axiom(axiom: Implication) -> bool:
        """Проверка корректности аксиомы"""
        if len(axiom.children) != 2:
            raise ParserException("Аксиома должна иметь условие и следствие")
        
        return True
    
    @staticmethod
    def validate_variables(expr) -> set[str]:
        """Получение всех переменных в выражении"""
        variables = set()
        
        if isinstance(expr, (Variable, Term)):
            variables.add(expr.name)
        elif isinstance(expr, Predicate) and expr.args:
            for arg in expr.args:
                variables.update(Validator.validate_variables(arg))
        elif isinstance(expr, Operation):
            for child in expr.children:
                variables.update(Validator.validate_variables(child))
        
        return variables
```

---

## Фаза 10: Тестирование

### 10.1 Структура тестов

```
tests/
├── test_lexer.py          # Тесты лексера
├── test_parser.py         # Тесты парсера
├── test_unification.py    # Тесты унификации
├── test_engine.py         # Тесты логического движка
├── test_arithmetic.py     # Тесты арифметики
├── test_commands.py       # Тесты команд
└── test_integration.py    # Интеграционные тесты
```

### 10.2 Примеры тестов

**test_lexer.py:**
```python
import pytest
from lexer import Lexer, TokenType, LexerException

def test_tokenize_identifier():
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_1")
    assert len(tokens) == 2  # identifier + EOF
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "игрок_1"

def test_tokenize_variable():
    lexer = Lexer()
    tokens = lexer.tokenize("X")
    assert tokens[0].type == TokenType.VARIABLE
    assert tokens[0].value == "X"

def test_tokenize_predicate():
    lexer = Lexer()
    tokens = lexer.tokenize("уровень(игрок(1), 2)")
    # Проверка последовательности токенов
    assert tokens[0].type == TokenType.IDENTIFIER  # уровень
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.IDENTIFIER  # игрок
    # ... и т.д.

def test_tokenize_operators():
    lexer = Lexer()
    tokens = lexer.tokenize("a & b | !c -> d")
    operators = [t for t in tokens if t.type in (TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.IMPLIES)]
    assert len(operators) == 4

def test_tokenize_comment():
    lexer = Lexer()
    tokens = lexer.tokenize("// это комментарий\nигрок_1")
    # Комментарий должен быть пропущен
    assert tokens[0].type == TokenType.IDENTIFIER
```

**test_unification.py:**
```python
import pytest
from unification import unify, Substitution
from models import Predicate, Variable, Term

def test_unify_identical():
    p1 = Predicate("уровень", [Variable("игрок"), Predicate("2", None)])
    p2 = Predicate("уровень", [Variable("игрок"), Predicate("2", None)])
    result = unify(p1, p2)
    assert result is not None
    assert len(result.bindings) == 0

def test_unify_variable_with_constant():
    p1 = Predicate("уровень", [Term("X"), Predicate("2", None)])
    p2 = Predicate("уровень", [Variable("игрок"), Predicate("2", None)])
    result = unify(p1, p2)
    assert result is not None
    assert result.bindings["X"].name == "игрок"

def test_unify_nested_predicates():
    p1 = Predicate("уровень", [Predicate("игрок", [Term("X")]), Term("Y")])
    p2 = Predicate("уровень", [Predicate("игрок", [Predicate("1", None)]), Predicate("2", None)])
    result = unify(p1, p2)
    assert result is not None
    assert result.bindings["X"].name == "1"
    assert result.bindings["Y"].name == "2"

def test_unify_occurs_check():
    p1 = Term("X")
    p2 = Predicate("f", [Term("X")])
    result = unify(p1, p2)
    assert result is None  # Occurs check должен предотвратить унификацию
```

### 10.3 Интеграционные тесты

**test_integration.py:**
```python
import pytest
from repl import REPL
from io import StringIO
import sys

def test_full_scenario():
    """Тест полного сценария из example.shldn"""
    repl = REPL()
    
    # Добавление фактов
    repl.process_line("уровень(игрок(1), 2)")
    repl.process_line("сила(игрок(1), 5)")
    
    # Добавление правила
    repl.process_line("уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)")
    
    # Запрос
    output = StringIO()
    sys.stdout = output
    repl.process_line("? боевая_сила(игрок(1), S)")
    sys.stdout = sys.__stdout__
    
    result = output.getvalue()
    assert "S = 7" in result or "7" in result
```

---

## Фаза 11: Документация

### 11.1 Структура документации

```
docs/
├── README.md                  # Общее описание
├── installation.md            # Установка и настройка
├── language_reference.md      # Справочник по языку
├── examples.md                # Примеры использования
├── api_reference.md           # API документация
├── development_guide.md       # Руководство разработчика
└── architecture.md            # Архитектура системы
```

### 11.2 Примеры для документации

Создать `docs/examples.md`:

```markdown
# Примеры использования SHLDN

## Пример 1: Простые высказывания

```shldn
// Определение высказываний
игрок_1_уровень_10
игрок_1_воин

// Правило
игрок_1_уровень_10 & игрок_1_воин -> игрок_1_сильный

// Запрос
? игрок_1_сильный
```

## Пример 2: Предикаты и унификация

```shldn
// Факты
уровень(игрок(1), 10)
уровень(игрок(2), 5)
класс(игрок(1), воин)
класс(игрок(2), маг)

// Правило
уровень(игрок(X), Y) & класс(игрок(X), воин) & (Y >= 10) -> сильный(игрок(X))

// Запросы
? уровень(игрок(X), 10)  // Найти всех игроков 10 уровня
? сильный(игрок(1))      // Проверить, сильный ли игрок 1
```

## Пример 3: Арифметические операции

```shldn
// Факты
уровень(игрок(1), 5)
сила(игрок(1), 10)
уровень(монстр(гоблин), 3)

// Правило с