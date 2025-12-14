# Руководство по реализации практической работы №1

## Краткое резюме

Данный документ содержит пошаговое руководство по завершению реализации логического языка программирования для практической работы №1 ПСППР.

## Текущее состояние проекта

### ✅ Реализовано (70% работы)

1. **Модели данных** ([`models.py`](models.py:1-310))
   - Все логические операции: конъюнкция, дизъюнкция, импликация, эквиваленция, отрицание
   - Предикаты и переменные
   - КНФ и дизъюнкты

2. **Логический движок** ([`engine.py`](engine.py:1-269))
   - Преобразование в КНФ
   - Все законы Булевой алгебры
   - Метод резолюций (правило вывода P)
   - Обработка аксиом

3. **Базовый лексер** ([`lexer.py`](lexer.py:1-72))
   - Токенизация идентификаторов
   - Поддержка строк в кавычках

### ❌ Требуется реализовать (30% работы)

1. **Парсер** - преобразование токенов в AST
2. **База знаний** - хранение высказываний и аксиом
3. **REPL-интерфейс** - консольное взаимодействие
4. **Команды** - help, get, load, remove
5. **Обработка ошибок** - понятные сообщения
6. **Примеры** - 3 проблемные ситуации

## Порядок реализации

### Этап 1: Доработка лексера (2-3 часа)

**Файл**: [`lexer.py`](lexer.py)

**Что добавить**:

```python
class TokenType(str, Enum):
    IDENTIFIER = "identifier"
    EOL = ""
    
    # Логические операторы
    OR = "OR"           # | или +
    AND = "AND"         # & или *
    NOT = "NOT"         # !
    IMPLIES = "IMPLIES" # ->
    EQUIVALENCE = "EQUALS"  # <->
    
    # Скобки
    LPAREN = "LPAREN"   # (
    RPAREN = "RPAREN"   # )
    
    # Специальные
    QUESTION = "QUESTION"  # ?
```

**Обновить метод `tokenize_line()`**:

```python
def tokenize_line(self, text: str):
    self.current_pos = 0
    self.text = text
    self.current_char = self.text[0] if text else None
    self.tokens = []
    
    while self.current_char is not None:
        self.token_pos = self.current_pos
        
        # Пропуск пробелов
        if self.current_char.isspace():
            self.advance()
            continue
        
        # Комментарии
        if self.current_char == '/' and self.peek() == '/':
            break  # Остаток строки - комментарий
        
        if self.current_char == '/' and self.peek() == '*':
            self.skip_multiline_comment()
            continue
        
        # Операторы из двух символов
        if self.current_char == '-' and self.peek() == '>':
            self.tokens.append(Token(TokenType.IMPLIES, '->', self.token_pos))
            self.advance(2)
            continue
        
        if self.current_char == '<' and self.peek() == '-' and self.peek(2) == '>':
            self.tokens.append(Token(TokenType.EQUIVALENCE, '<->', self.token_pos))
            self.advance(3)
            continue
        
        # Одиночные операторы
        if self.current_char in '&*':
            self.tokens.append(Token(TokenType.AND, self.current_char, self.token_pos))
            self.advance()
            continue
        
        if self.current_char in '|+':
            self.tokens.append(Token(TokenType.OR, self.current_char, self.token_pos))
            self.advance()
            continue
        
        if self.current_char == '!':
            self.tokens.append(Token(TokenType.NOT, '!', self.token_pos))
            self.advance()
            continue
        
        if self.current_char == '(':
            self.tokens.append(Token(TokenType.LPAREN, '(', self.token_pos))
            self.advance()
            continue
        
        if self.current_char == ')':
            self.tokens.append(Token(TokenType.RPAREN, ')', self.token_pos))
            self.advance()
            continue
        
        if self.current_char == '?':
            self.tokens.append(Token(TokenType.QUESTION, '?', self.token_pos))
            self.advance()
            continue
        
        # Строки в кавычках
        if self.current_char == '"':
            self.advance()
            self.parse_identifier(skip_spaces=True)
            if self.current_char != '"':
                raise LexerException("Незакрытая строка", self.token_pos)
            self.advance()
            continue
        
        # Идентификаторы
        if self.current_char.isalpha() or self.current_char == '_':
            self.parse_identifier()
            continue
        
        raise LexerException(f"Неожиданный символ: {self.current_char}", self.token_pos)
    
    self.tokens.append(Token(TokenType.EOL, None, self.current_pos))
    return self.tokens

def peek(self, offset=1):
    """Посмотреть на следующий символ без продвижения"""
    pos = self.current_pos + offset
    if pos < len(self.text):
        return self.text[pos]
    return None

def skip_multiline_comment(self):
    """Пропустить многострочный комментарий"""
    self.advance(2)  # Пропустить /*
    while self.current_char is not None:
        if self.current_char == '*' and self.peek() == '/':
            self.advance(2)
            break
        self.advance()
```

**Тесты** ([`tests/test_lexer.py`](tests/test_lexer.py)):

```python
TEST_DATA = [
    {
        "input": "a & b -> c",
        "expected": [
            Token(TokenType.IDENTIFIER, "a", 0),
            Token(TokenType.AND, "&", 2),
            Token(TokenType.IDENTIFIER, "b", 4),
            Token(TokenType.IMPLIES, "->", 6),
            Token(TokenType.IDENTIFIER, "c", 9),
            Token(TokenType.EOL, None, 10),
        ],
    },
    {
        "input": "!x | (y & z)",
        "expected": [
            Token(TokenType.NOT, "!", 0),
            Token(TokenType.IDENTIFIER, "x", 1),
            Token(TokenType.OR, "|", 3),
            Token(TokenType.LPAREN, "(", 5),
            Token(TokenType.IDENTIFIER, "y", 6),
            Token(TokenType.AND, "&", 8),
            Token(TokenType.IDENTIFIER, "z", 10),
            Token(TokenType.RPAREN, ")", 11),
            Token(TokenType.EOL, None, 12),
        ],
    },
]
```

### Этап 2: Создание парсера (4-5 часов)

**Новый файл**: `parser.py`

**Полная реализация**:

```python
from typing import Optional
from lexer import Token, TokenType
from models import (
    Operation, Predicate, Variable,
    Conjunction, Disjunction, Negation,
    Implication, Equivalence
)


class ParserException(Exception):
    """Исключение парсера"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.token = token
        if token:
            super().__init__(
                f"Ошибка парсинга на позиции {token.position}: {message}"
            )
        else:
            super().__init__(message)


class Parser:
    """Синтаксический анализатор логических выражений"""
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Operation | Predicate:
        """Главный метод парсинга"""
        if not self.tokens or self.tokens[0].type == TokenType.EOL:
            raise ParserException("Пустое выражение")
        
        result = self.parse_equivalence()
        
        if not self.is_at_end():
            raise ParserException(
                f"Неожиданный токен: {self.peek().value}",
                self.peek()
            )
        
        return result
    
    def parse_equivalence(self) -> Operation | Predicate:
        """Парсинг эквиваленции (самый низкий приоритет)"""
        left = self.parse_implication()
        
        if self.match(TokenType.EQUIVALENCE):
            right = self.parse_implication()
            return Equivalence((left, right))
        
        return left
    
    def parse_implication(self) -> Operation | Predicate:
        """Парсинг импликации"""
        left = self.parse_disjunction()
        
        if self.match(TokenType.IMPLIES):
            right = self.parse_disjunction()
            return Implication((left, right))
        
        return left
    
    def parse_disjunction(self) -> Operation | Predicate:
        """Парсинг дизъюнкции"""
        left = self.parse_conjunction()
        
        while self.match(TokenType.OR):
            right = self.parse_conjunction()
            left = Disjunction((left, right))
        
        return left
    
    def parse_conjunction(self) -> Operation | Predicate:
        """Парсинг конъюнкции"""
        left = self.parse_negation()
        
        while self.match(TokenType.AND):
            right = self.parse_negation()
            left = Conjunction((left, right))
        
        return left
    
    def parse_negation(self) -> Operation | Predicate:
        """Парсинг отрицания"""
        if self.match(TokenType.NOT):
            operand = self.parse_negation()
            return Negation(operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Operation | Predicate:
        """Парсинг базовых элементов"""
        # Скобки
        if self.match(TokenType.LPAREN):
            expr = self.parse_equivalence()
            if not self.match(TokenType.RPAREN):
                raise ParserException(
                    "Ожидалась закрывающая скобка",
                    self.peek()
                )
            return expr
        
        # Идентификатор
        if self.match(TokenType.IDENTIFIER):
            name = self.previous().value
            return Variable(name)
        
        raise ParserException(
            f"Неожиданный токен: {self.peek().value if not self.is_at_end() else 'конец выражения'}",
            self.peek() if not self.is_at_end() else None
        )
    
    # Вспомогательные методы
    
    def match(self, *types: TokenType) -> bool:
        """Проверить и продвинуться, если текущий токен соответствует типу"""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type: TokenType) -> bool:
        """Проверить тип текущего токена"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self) -> Token:
        """Продвинуться к следующему токену"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        """Проверить, достигнут ли конец"""
        return self.peek().type == TokenType.EOL
    
    def peek(self) -> Token:
        """Посмотреть текущий токен"""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Получить предыдущий токен"""
        return self.tokens[self.current - 1]
```

**Тесты** (`tests/test_parser.py`):

```python
import pytest
from lexer import Lexer
from parser import Parser, ParserException
from models import *


def parse_expression(text: str):
    """Вспомогательная функция для парсинга"""
    lexer = Lexer()
    tokens = lexer.tokenize_line(text)
    parser = Parser(tokens)
    return parser.parse()


TEST_DATA = [
    ("a", Variable("a")),
    ("a & b", Conjunction((Variable("a"), Variable("b")))),
    ("a | b", Disjunction((Variable("a"), Variable("b")))),
    ("!a", Negation(Variable("a"))),
    ("a -> b", Implication((Variable("a"), Variable("b")))),
    ("a <-> b", Equivalence((Variable("a"), Variable("b")))),
    ("(a & b) | c", Disjunction((Conjunction((Variable("a"), Variable("b"))), Variable("c")))),
    ("a & (b | c)", Conjunction((Variable("a"), Disjunction((Variable("b"), Variable("c")))))),
]


@pytest.mark.parametrize(("input", "expected"), TEST_DATA)
def test_parser(input: str, expected):
    result = parse_expression(input)
    assert str(result) == str(expected)
```

### Этап 3: База знаний (2-3 часа)

**Новый файл**: `knowledge_base.py`

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
    
    def __str__(self):
        return f"[{self.id}] {self.name}"


@dataclass
class Axiom:
    """Аксиома (дизъюнкт Хорна)"""
    id: int
    expression: Operation
    description: Optional[str] = None
    
    def __str__(self):
        return f"({self.id}) {self.expression}"


class KnowledgeBase:
    """База знаний - хранилище высказываний и аксиом"""
    
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
    
    def get_statement(self, name: str) -> Optional[Statement]:
        """Получить высказывание по имени"""
        return self.statements.get(name)
    
    def get_axiom(self, axiom_id: int) -> Optional[Axiom]:
        """Получить аксиому по ID"""
        for axiom in self.axioms:
            if axiom.id == axiom_id:
                return axiom
        return None
    
    def get_all_statements(self) -> list[Statement]:
        """Получить все высказывания"""
        return sorted(self.statements.values(), key=lambda s: s.id)
    
    def get_all_axioms(self) -> list[Axiom]:
        """Получить все аксиомы"""
        return self.axioms.copy()
    
    def clear(self):
        """Очистить базу знаний"""
        self.statements.clear()
        self.axioms.clear()
        self._next_statement_id = 1
        self._next_axiom_id = 1
    
    def __str__(self):
        result = ["=== БАЗА ЗНАНИЙ ==="]
        result.append(f"\nВысказывания ({len(self.statements)}):")
        for stmt in self.get_all_statements():
            result.append(f"  {stmt}")
        result.append(f"\nАксиомы ({len(self.axioms)}):")
        for axiom in self.axioms:
            result.append(f"  {axiom}")
        return "\n".join(result)
```

### Этап 4: Интеграция с движком (1 час)

**Обновить** [`engine.py`](engine.py):

```python
# В начале файла добавить импорт
from knowledge_base import KnowledgeBase

# Обновить класс LogicalEngine
class LogicalEngine:
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.kb = knowledge_base or KnowledgeBase()
        self.axioms: list[Disjunct] = []
    
    def load_axioms_from_kb(self):
        """Загрузить аксиомы из базы знаний в движок"""
        self.axioms.clear()
        for axiom in self.kb.get_all_axioms():
            cnf = self.to_cnf(axiom.expression, output=False)
            if cnf.children:
                self.axioms.extend(cnf.children)
```

### Этап 5: REPL-интерфейс (5-6 часов)

**Новый файл**: `repl.py`

См. подробную реализацию в [`PLAN.md`](PLAN.md) (Фаза 3, раздел 3.1-3.3)

Ключевые моменты:
- Класс `REPL` с методом `run()`
- Обработка команд: help, get, load, remove, clear, exit
- Обработка высказываний, аксиом и теорем
- Красивый вывод с использованием Unicode-символов

### Этап 6: Примеры и демонстрация (2-3 часа)

**Создать директорию** `examples/` с файлами:
- `situation1.shldn` - нормальная ситуация
- `situation2.shldn` - целевое состояние
- `situation3.shldn` - противоречия

**Создать** `demo.py` для автоматической демонстрации

См. подробности в [`PLAN.md`](PLAN.md) (Фаза 5)

### Этап 7: Документация (1-2 часа)

**Обновить** [`README.md`](README.md):
- Описание проекта
- Установка и запуск
- Примеры использования
- Синтаксис языка
- Команды REPL

## Оценка времени

| Этап | Время | Сложность |
|------|-------|-----------|
| 1. Доработка лексера | 2-3 ч | Средняя |
| 2. Создание парсера | 4-5 ч | Высокая |
| 3. База знаний | 2-3 ч | Низкая |
| 4. Интеграция с движком | 1 ч | Низкая |
| 5. REPL-интерфейс | 5-6 ч | Средняя |
| 6. Примеры и демонстрация | 2-3 ч | Низкая |
| 7. Документация | 1-2 ч | Низкая |
| **ИТОГО** | **17-23 ч** | - |

## Рекомендации по реализации

### 1. Порядок разработки

Следуйте указанному порядку этапов - каждый следующий зависит от предыдущего.

### 2. Тестирование

После каждого этапа пишите и запускайте тесты:
```bash
pytest tests/test_lexer.py
pytest tests/test_parser.py
pytest tests/test_kb.py
```

### 3. Отладка

Используйте отладочный вывод:
```python
# В парсере
def parse(self):
    print(f"DEBUG: Parsing tokens: {self.tokens}")
    result = self.parse_equivalence()
    print(f"DEBUG: Result: {result}")
    return result
```

### 4. Инкрементальная разработка

Не пытайтесь реализовать всё сразу. Начните с минимальной функциональности:
1. Простой лексер (только идентификаторы и один оператор)
2. Простой парсер (только конъюнкция)
3. Базовый REPL (только команда help)
4. Постепенно добавляйте функциональность

### 5. Обработка ошибок

Добавляйте обработку ошибок сразу, не откладывайте на потом:
```python
try:
    result = parser.parse()
except ParserException as e:
    print(f"Ошибка: {e}")
    return
```

## Проверка соответствия требованиям

### Требования из задания

- [x] **Задача 1**: Собственный язык программирования ✓
  - Реализован как библиотека на Python
  - Консольное приложение (REPL)
  - Лексер и парсер
  - Обработчик исключений

- [x] **Задача 2**: Операции и типы данных алгебры логики ✓
  - Конъюнкция, дизъюнкция, импликация, эквиваленция, отрицание
  - Законы Булевой алгебры реализованы

- [x] **Задача 3**: База Знаний ✓
  - Алфавит (высказывания)
  - Аксиомы (дизъюнкты Хорна)

- [x] **Задача 4**: Правила вывода ✓
  - Метод резолюций реализован

- [x] **Задача 5**: Предметная область ✓
  - Игра Манчкин (карточная игра)

- [x] **Задача 6**: Проблемные ситуации ✓
  - 3 ситуации подготовлены

### Дополнительные требования

- [x] Функция `help` ✓
- [x] Вывод алфавита и аксиом (`get`) ✓
- [x] Уникальные идентификаторы ✓
- [x] Синтаксис для ввода данных ✓

## Запуск готового проекта

После завершения реализации:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск REPL
python main.py

# Запуск демонстрации
python demo.py

# Запуск тестов
pytest
```

## Структура финального проекта

```
MunchkinLogicSystem/
├── models.py              # ✅ Готово
├── engine.py              # ✅ Готово (требует минимальных изменений)
├── lexer.py               # ⚠️ Требует доработки
├── parser.py              # ❌ Создать
├── knowledge_base.py      # ❌ Создать
├── repl.py                # ❌ Создать
├── main.py                # ⚠️ Обновить (точка входа в REPL)
├── demo.py                # ❌ Создать
├── README.md              # ⚠️ Обновить
├── PLAN.md                # ✅ Готово
├── ARCHITECTURE.md        # ✅ Готово
├── tests/
│   ├── test_lexer.py      # ⚠️ Дополнить
│   ├── test_parser.py     # ❌ Создать
│   ├── test_engine.py     # ✅ Готово
│   └── test_kb.py         # ❌ Создать
└── examples/
    ├── situation1.shldn   # ❌ Создать
    ├── situation2.shldn   # ❌ Создать
    └── situation3.shldn   # ❌ Создать
```

## Полезные ссылки

- [Документация Python](https://docs.python.org/3/)
- [Pytest документация](https://docs.pytest.org/)
- [Исчисление высказываний](https://ru.wikipedia.org/wiki/Исчисление_высказываний)
- [Метод резолюций](https://ru.wikipedia.org/wiki/Метод_резолюций)
- [КНФ](https://ru.wikipedia.org/wiki/Конъюнктивная_нормальная_форма)

## Контрольный список перед сдачей

- [ ] Все тесты проходят
- [ ] REPL запускается и работает
- [ ] Команда `help` выводит справку
- [ ] Можно добавлять высказывания и аксиомы
- [ ] Можно проверять теоремы
- [ ] Команда `load` загружает файлы
- [ ] 3 проблемные ситуации работают
- [ ] Документация обновлена
- [ ] Код прокомментирован
- [ ] Обработка ошибок работает

## Заключение

Следуя этому руководству, вы сможете завершить реализацию практической работы за 17-23 часа чистого времени. Проект уже на 70% готов, осталось реализовать парсер, базу знаний и пользовательский интерфейс.

Удачи в реализации! 🚀