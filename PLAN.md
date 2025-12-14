
# План завершения реализации практической работы №1 ПСППР

## Анализ текущего состояния проекта

### ✅ Что уже реализовано:

1. **Модели данных** ([`models.py`](models.py)):
   - [`Predicate`](models.py:11), [`Variable`](models.py:50), [`Term`](models.py:55) - базовые предикаты и переменные
   - [`Operation`](models.py:60) - базовый класс для операций
   - [`Conjunction`](models.py:94) (конъюнкция `*`)
   - [`Disjunction`](models.py:89) (дизъюнкция `+`)
   - [`Negation`](models.py:99) (отрицание `!`)
   - [`Implication`](models.py:125) (импликация `->`)
   - [`Equivalence`](models.py:130) (эквиваленция `<->`)
   - [`Disjunct`](models.py:135) - дизъюнкт (элемент КНФ)
   - [`CNF`](models.py:230) - конъюнктивная нормальная форма

2. **Логический движок** ([`engine.py`](engine.py)):
   - [`LogicalEngine`](engine.py:20) - основной класс движка
   - [`add_axiom()`](engine.py:24) - добавление аксиом
   - [`resolution_method()`](engine.py:30) - метод резолюций для доказательства теорем
   - [`to_cnf()`](engine.py:239) - преобразование в КНФ
   - Реализованы законы Булевой алгебры:
     - [`remove_equivalences()`](engine.py:91) - устранение эквиваленций
     - [`remove_implications()`](engine.py:112) - устранение импликаций
     - [`remove_double_negations()`](engine.py:128) - устранение двойных отрицаний
     - [`apply_de_morgan()`](engine.py:143) - законы де Моргана
     - [`group_conjunctions()`](engine.py:168) - дистрибутивность

3. **Лексер** ([`lexer.py`](lexer.py)):
   - [`Lexer`](lexer.py:28) - базовый лексер
   - [`TokenType`](lexer.py:10) - типы токенов
   - [`tokenize_line()`](lexer.py:39) - токенизация строки
   - Поддержка идентификаторов и строк в кавычках

4. **Тесты**:
   - [`tests/test_engine.py`](tests/test_engine.py) - тесты для движка
   - [`tests/test_lexer.py`](tests/test_lexer.py) - тесты для лексера

### ❌ Что нужно реализовать:

## Детальный план реализации

### Фаза 1: Расширение лексера и создание парсера

#### 1.1 Доработка лексера ([`lexer.py`](lexer.py))

**Задача**: Расширить лексер для поддержки всех операторов и конструкций языка

**Что добавить**:
- Токены для операторов:
  - `&` или `*` → [`TokenType.AND`](lexer.py:15)
  - `|` или `+` → [`TokenType.OR`](lexer.py:14)
  - `!` → [`TokenType.NOT`](lexer.py:16)
  - `->` → [`TokenType.IMPLIES`](lexer.py:17)
  - `<->` → [`TokenType.EQUIVALENCE`](lexer.py:18)
- Токены для скобок: `(`, `)`
- Токен для вопросительного знака: `?`
- Обработка комментариев:
  - Однострочные `//`
  - Многострочные `/* */`
- Пропуск пробелов и табуляций

**Пример синтаксиса**:
```python
# Входная строка
"игрок_1_уровень_10 -> игрок_1_победитель"

# Ожидаемые токены
[
    Token(IDENTIFIER, "игрок_1_уровень_10", 0),
    Token(IMPLIES, "->", 19),
    Token(IDENTIFIER, "игрок_1_победитель", 22),
    Token(EOL, None, 40)
]
```

#### 1.2 Создание парсера (`parser.py`)

**Задача**: Создать парсер, преобразующий токены в AST (Abstract Syntax Tree)

**Архитектура парсера**:
```python
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Operation | Predicate:
        """Главный метод парсинга"""
        return self.parse_expression()
    
    def parse_expression(self) -> Operation | Predicate:
        """Парсинг выражения с учётом приоритета операторов"""
        # Приоритет (от низкого к высокому):
        # 1. <-> (эквиваленция)
        # 2. -> (импликация)
        # 3. | или + (дизъюнкция)
        # 4. & или * (конъюнкция)
        # 5. ! (отрицание)
        # 6. () (скобки)
        # 7. идентификаторы
```

**Методы парсера**:
- `parse_equivalence()` - парсинг эквиваленции (самый низкий приоритет)
- `parse_implication()` - парсинг импликации
- `parse_disjunction()` - парсинг дизъюнкции
- `parse_conjunction()` - парсинг конъюнкции
- `parse_negation()` - парсинг отрицания
- `parse_primary()` - парсинг базовых элементов (переменные, скобки)

**Обработка ошибок**:
```python
class ParserException(Exception):
    def __init__(self, message: str, position: int):
        self.message = message
        self.position = position
        super().__init__(f"Ошибка парсинга на позиции {position}: {message}")
```

### Фаза 2: Система управления базой знаний

#### 2.1 Создание класса базы знаний (`knowledge_base.py`)

**Задача**: Создать систему для хранения и управления высказываниями и аксиомами

**Архитектура**:
```python
from dataclasses import dataclass
from typing import Optional
from models import Operation, Predicate

@dataclass
class Statement:
    """Высказывание в алфавите"""
    id: int
    name: str
    description: Optional[str] = None

@dataclass
class Axiom:
    """Аксиома (дизъюнкт Хорна)"""
    id: int
    expression: Operation
    description: Optional[str] = None
    
    def __str__(self):
        return f"({self.id}) {self.expression}"

class KnowledgeBase:
    """База знаний"""
    
    def __init__(self):
        self.statements: dict[str, Statement] = {}
        self.axioms: list[Axiom] = []
        self._next_statement_id = 1
        self._next_axiom_id = 1
    
    def add_statement(self, name: str, description: str = None) -> Statement:
        """Добавить высказывание в алфавит"""
        if name in self.statements:
            return self.statements[name]
        
        statement = Statement(
            id=self._next_statement_id,
            name=name,
            description=description
        )
        self.statements[name] = statement
        self._next_statement_id += 1
        return statement
    
    def add_axiom(self, expression: Operation, description: str = None) -> Axiom:
        """Добавить аксиому"""
        axiom = Axiom(
            id=self._next_axiom_id,
            expression=expression,
            description=description
        )
        self.axioms.append(axiom)
        self._next_axiom_id += 1
        return axiom
    
    def remove_axiom(self, axiom_id: int) -> bool:
        """Удалить аксиому по ID"""
        for i, axiom in enumerate(self.axioms):
            if axiom.id == axiom_id:
                self.axioms.pop(i)
                return True
        return False
    
    def get_all_statements(self) -> list[Statement]:
        """Получить все высказывания"""
        return list(self.statements.values())
    
    def get_all_axioms(self) -> list[Axiom]:
        """Получить все аксиомы"""
        return self.axioms
    
    def clear(self):
        """Очистить базу знаний"""
        self.statements.clear()
        self.axioms.clear()
        self._next_statement_id = 1
        self._next_axiom_id = 1
```

#### 2.2 Интеграция с движком

**Задача**: Связать базу знаний с логическим движком

Модифицировать [`LogicalEngine`](engine.py:20):
```python
class LogicalEngine:
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.kb = knowledge_base or KnowledgeBase()
        self.axioms: list[Disjunct] = []
    
    def load_axioms_from_kb(self):
        """Загрузить аксиомы из базы знаний"""
        self.axioms.clear()
        for axiom in self.kb.get_all_axioms():
            self.add_axiom(axiom.expression)
```

### Фаза 3: Консольный REPL-интерфейс

#### 3.1 Создание REPL (`repl.py`)

**Задача**: Создать интерактивный консольный интерфейс

**Архитектура**:
```python
class REPL:
    """Read-Eval-Print Loop для логического языка"""
    
    def __init__(self):
        self.engine = LogicalEngine()
        self.kb = self.engine.kb
        self.lexer = Lexer()
        self.parser = Parser([])
        self.running = True
    
    def run(self):
        """Запустить REPL"""
        self.print_welcome()
        
        while self.running:
            try:
                line = input(">>> ").strip()
                if not line:
                    continue
                
                self.process_line(line)
                
            except KeyboardInterrupt:
                print("\nИспользуйте 'exit' для выхода")
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def process_line(self, line: str):
        """Обработать строку ввода"""
        # Пропустить комментарии
        if line.startswith("//"):
            return
        
        # Обработать команды
        if line.startswith("help"):
            self.cmd_help()
        elif line.startswith("load "):
            self.cmd_load(line[5:].strip())
        elif line.startswith("get"):
            self.cmd_get()
        elif line.startswith("remove "):
            self.cmd_remove(line[7:].strip())
        elif line.startswith("clear"):
            self.cmd_clear()
        elif line.startswith("exit") or line.startswith("quit"):
            self.cmd_exit()
        elif line.startswith("?"):
            # Теорема
            self.process_theorem(line[1:].strip())
        else:
            # Высказывание или аксиома
            self.process_statement_or_axiom(line)
```

#### 3.2 Реализация команд

**3.2.1 Команда `help`**

```python
def cmd_help(self):
    """Вывести справку"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              СПРАВКА ПО ЛОГИЧЕСКОМУ ЯЗЫКУ                        ║
╚══════════════════════════════════════════════════════════════════╝

СИНТАКСИС:
  Операторы:
    &  или  *     - конъюнкция (И)
    |  или  +     - дизъюнкция (ИЛИ)
    !             - отрицание (НЕ)
    ->            - импликация (ЕСЛИ...ТО)
    <->           - эквиваленция (ТОГДА И ТОЛЬКО ТОГДА)
    ()            - скобки для группировки
    
  Идентификаторы:
    - Могут содержать буквы, цифры и подчёркивания
    - Примеры: игрок_1, монстр_дракон, уровень_10
    
  Строки в кавычках:
    - Для идентификаторов с пробелами
    - Пример: "игрок 2 имеет уровень 1"

КОМАНДЫ:
  help                    - показать эту справку
  get                     - показать все высказывания и аксиомы
  remove <id>             - удалить аксиому по ID
  load <файл>             - загрузить файл с высказываниями и аксиомами
  clear                   - очистить базу знаний
  exit / quit             - выйти из программы

ИСПОЛЬЗОВАНИЕ:
  1. Добавление высказывания (элемента алфавита):
     >>> игрок_1
     >>> монстр_дракон
     >>> "игрок имеет уровень 10"
  
  2. Добавление аксиомы (должна содержать ->):
     >>> игрок_1_уровень_10 -> игрок_1_победитель
     >>> a & b -> c
     >>> !x | y -> z
  
  3. Проверка теоремы (начинается с ?):
     >>> ? игрок_1_победитель
     >>> ? a -> c

ПРИМЕРЫ:
  >>> игрок_1
  Добавлено высказывание: игрок_1
  
  >>> игрок_1_уровень_10 -> игрок_1_победитель
  Добавлена аксиома (1): игрок_1_уровень_10 -> игрок_1_победитель
  
  >>> ? игрок_1_победитель
  Проверка теоремы: игрок_1_победитель
  [вывод процесса доказательства]

КОММЕНТАРИИ:
  // однострочный комментарий
  /* многострочный
     комментарий */

ПРАВИЛА ВЫВОДА:
  Реализовано правило резолюций для доказательства теорем.
  Программа автоматически преобразует выражения в КНФ и применяет
  метод резолюций для поиска противоречия.

ЗАКОНЫ БУЛЕВОЙ АЛГЕБРЫ:
  - Устранение эквиваленций: A <-> B ≡ (A -> B) & (B -> A)
  - Устранение импликаций: A -> B ≡ !A | B
  - Законы де Моргана: !(A & B) ≡ !A | !B, !(A | B) ≡ !A & !B
  - Двойное отрицание: !!A ≡ A
  - Дистрибутивность: A | (B & C) ≡ (A | B) & (A | C)
    """)
```

**3.2.2 Команда `get`**

```python
def cmd_get(self):
    """Показать все высказывания и аксиомы"""
    print("\n" + "="*70)
    print("БАЗА ЗНАНИЙ")
    print("="*70)
    
    # Высказывания
    statements = self.kb.get_all_statements()
    if statements:
        print("\nВЫСКАЗЫВАНИЯ (Алфавит A):")
        for stmt in statements:
            desc = f" - {stmt.description}" if stmt.description else ""
            print(f"  [{stmt.id}] {stmt.name}{desc}")
    else:
        print("\nВЫСКАЗЫВАНИЯ: нет")
    
    # Аксиомы
    axioms = self.kb.get_all_axioms()
    if axioms:
        print("\nАКСИОМЫ (Ak - дизъюнкты Хорна):")
        for axiom in axioms:
            desc = f" - {axiom.description}" if axiom.description else ""
            print(f"  ({axiom.id}) {axiom.expression}{desc}")
    else:
        print("\nАКСИОМЫ: нет")
    
    print("="*70 + "\n")
```

**3.2.3 Команда `remove`**

```python
def cmd_remove(self, arg: str):
    """Удалить аксиому по ID"""
    try:
        axiom_id = int(arg)
        if self.kb.remove_axiom(axiom_id):
            print(f"✓ Аксиома ({axiom_id}) удалена")
            # Перезагрузить аксиомы в движок
            self.engine.load_axioms_from_kb()
        else:
            print(f"✗ Аксиома с ID {axiom_id} не найдена")
    except ValueError:
        print("✗ Ошибка: ID должен быть числом")
```

**3.2.4 Команда `load`**

```python
def cmd_load(self, filename: str):
    """Загрузить файл"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Загрузка файла: {filename}")
        
        in_multiline_comment = False
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Обработка многострочных комментариев
            if "/*" in line:
                in_multiline_comment = True
            if "*/" in line:
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue
            
            # Пропустить пустые строки и комментарии
            if not line or line.startswith("//"):
                continue
            
            try:
                self.process_line(line)
            except Exception as e:
                print(f"  Строка {line_num}: Ошибка - {e}")
        
        print(f"✓ Файл загружен")
        
    except FileNotFoundError:
        print(f"✗ Файл не найден: {filename}")
    except Exception as e:
        print(f"✗ Ошибка при загрузке файла: {e}")
```

**3.2.5 Команда `clear`**

```python
def cmd_clear(self):
    """Очистить базу знаний"""
    self.kb.clear()
    self.engine.axioms.clear()
    print("✓ База знаний очищена")
```

**3.2.6 Команда `exit`**

```python
def cmd_exit(self):
    """Выйти из программы"""
    print("До свидания!")
    self.running = False
```

#### 3.3 Обработка высказываний, аксиом и теорем

**3.3.1 Обработка высказываний и аксиом**

```python
def process_statement_or_axiom(self, line: str):
    """Обработать высказывание или аксиому"""
    try:
        # Токенизация
        tokens = self.lexer.tokenize_line(line)
        
        # Парсинг
        self.parser.tokens = tokens
        self.parser.current = 0
        expression = self.parser.parse()
        
        # Определить, это высказывание или аксиома
        if self.is_axiom(expression):
            # Это аксиома (содержит ->)
            axiom = self.kb.add_axiom(expression)
            print(f"✓ Добавлена аксиома ({axiom.id}): {axiom.expression}")
            
            # Добавить в движок
            self.engine.add_axiom(expression)
        else:
            # Это высказывание
            if isinstance(expression, Predicate):
                stmt = self.kb.add_statement(expression.name)
                print(f"✓ Добавлено высказывание [{stmt.id}]: {stmt.name}")
            else:
                print("✗ Высказывание должно быть простым идентификатором")
    
    except LexerException as e:
        print(f"✗ Ошибка лексера: {e}")
    except ParserException as e:
        print(f"✗ Ошибка парсера: {e}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def is_axiom(self, expression: Operation | Predicate) -> bool:
    """Проверить, является ли выражение аксиомой"""
    # Аксиома должна содержать импликацию на верхнем уровне
    # или быть сложным выражением
    return isinstance(expression, (Implication, Conjunction, Disjunction))
```

**3.3.2 Обработка теорем**

```python
def process_theorem(self, line: str):
    """Проверить теорему"""
    try:
        print(f"\n{'='*70}")
        print(f"ПРОВЕРКА ТЕОРЕМЫ: {line}")
        print(f"{'='*70}\n")
        
        # Токенизация и парсинг
        tokens = self.lexer.tokenize_line(line)
        self.parser.tokens = tokens
        self.parser.current = 0
        expression = self.parser.parse()
        
        # Загрузить аксиомы из базы знаний
        self.engine.load_axioms_from_kb()
        
        # Применить метод резолюций
        print("Аксиомы в базе знаний:")
        self.engine.resolution_method(expression)
        
        print(f"\n{'='*70}\n")
        
    except LexerException as e:
        print(f"✗ Ошибка лексера: {e}")
    except ParserException as e:
        print(f"✗ Ошибка парсера: {e}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
```

### Фаза 4: Обработка исключений

#### 4.1 Создание иерархии исключений (`exceptions.py`)

```python
class LogicLanguageException(Exception):
    """Базовое исключение для логического языка"""
    pass

class LexerException(LogicLanguageException):
    """Исключение лексера"""
    def __init__(self, message: str, position: int = None):
        self.position = position
        if position is not None:
            super().__init__(f"Ошибка на позиции {position}: {message}")
        else:
            super().__init__(message)

class ParserException(LogicLanguageException):
    """Исключение парсера"""
    def __init__(self, message: str, token: Token = None):
        self.token = token
        if token:
            super().__init__(
                f"Ошибка парсинга на позиции {token.position}: {message}"
            )
        else:
            super().__init__(message)

class KnowledgeBaseException(LogicLanguageException):
    """Исключение базы знаний"""
    pass

class EngineException(LogicLanguageException):
    """Исключение движка"""
    pass
```

#### 4.2 Обработка ошибок в REPL

```python
def run(self):
    """Запустить REPL с обработкой ошибок"""
    self.print_welcome()
    
    while self.running:
        try:
            line = input(">>> ").strip()
            if not line:
                continue
            
            self.process_line(line)
            
        except KeyboardInterrupt:
            print("\n⚠ Прервано. Используйте 'exit' для выхода")
        except LexerException as e:
            print(f"✗ Ошибка лексера: {e}")
        except ParserException as e:
            print(f"✗ Ошибка парсера: {e}")
        except KnowledgeBaseException as e:
            print(f"✗ Ошибка базы знаний: {e}")
        except EngineException as e:
            print(f"✗ Ошибка движка: {e}")
        except Exception as e:
            print(f"✗ Неожиданная ошибка: {e}")
            import traceback
            traceback.print_exc()
```

### Фаза 5: Подготовка проблемных ситуаций

#### 5.1 Создание файлов с примерами

**Файл `examples/situation1.shldn` - Нормальная ситуация**

```
// Ситуация 1: Нормальная логика игры Манчкин
// Все условия соблюдены, логика работает корректно

// Высказывания (алфавит)
игрок_1
игрок_2
монстр_дракон
игрок_1_уровень_10
игрок_1_победитель
игрок_2_уровень_5
игрок_2_сила_10
монстр_сила_14
игрок_2_победил

// Аксиомы (правила игры)
игрок_1_уровень_10 -> игрок_1_победитель
игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 -> игрок_2_победил

// Теоремы для проверки
? игрок_1_победитель
? игрок_2_победил
```

**Файл `examples/situation2.shldn` - Установка целевого значения**

```
// Ситуация 2: Проверка достижимости целевого состояния
// Устанавливаем значение, к которому должна прийти модель

// Высказывания
игрок_вор
игрок_волшебник
игрок_может_сбрасывать

// Аксиомы
игрок_вор | игрок_волшебник -> игрок_может_сбрасывать

// Устанавливаем целевое состояние
игрок_вор

// Проверяем, достигается ли целевое состояние
? игрок_может_сбрасывать
```

**Файл `examples/situation3.shldn` - Противоречивые условия**

```
// Ситуация 3: Противоречивые условия
// Проверка корректности модели при нарушении логики

// Высказывания
игрок_жив
игрок_мёртв
игрок_может_атаковать

// Аксиомы (противоречивые)
игрок_жив -> игрок_может_атаковать
игрок_мёртв -> !игрок_может_атаковать

// Устанавливаем противоречие
игрок_жив
игрок_мёртв

// Проверяем, что происходит
? игрок_может_атаковать
```

#### 5.2 Создание скрипта для демонстрации (`demo.py`)

```python
#!/usr/bin/env python3
"""
Демонстрация работы логического языка на трёх проблемных ситуациях
"""

from repl import REPL

def run_demo():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         ДЕМОНСТРАЦИЯ ЛОГИЧЕСКОГО ЯЗЫКА ПРОГРАММИРОВАНИЯ          ║
║                  Практическая работа №1 ПСППР                    ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    situations = [
        ("examples/situation1.shldn", "Нормальная ситуация"),
        ("examples/situation2.shldn", "Установка целевого значения"),
        ("examples/situation3.shldn", "Противоречивые условия"),
    ]
    
    for i, (filename, description) in enumerate(situations, 1):
        print(f"\n{'='*70}")
        print(f"СИТУАЦИЯ {i}: {description}")
        print(f"{'='*70}\n")
        
        repl = REPL()
        repl.cmd_load(filename)
        
        input("\nНажмите Enter для продолжения...")
    
    print("\n✓ Демонстрация завершена")

if __name__ == "__main__":
    run_demo()
```

### Фаза 6: Документация и тестирование

#### 6.1 Обновление README.md

```markdown
# MunchkinLogic

Логический язык программирования на основе исчисления высказываний с полнофункциональным лексером и парсером.

## Описание

Реализация собственного логического языка программирования для практической работы №1 по дисциплине "Проектирование систем поддержки принятия решений".

### Возможности

- ✅ Полный набор логических