
# План разработки логического языка программирования SHLDN

## Обзор проекта

Разработка полнофункционального логического языка программирования для поддержки исчисления высказываний (ИВ) и исчисления предикатов (ИП) на основе существующего кода.

### Текущее состояние

**Реализовано:**
- ✅ Базовые модели данных ([`models.py`](../models.py:1))
  - [`Predicate`](../models.py:11) - высказывания
  - [`Operation`](../models.py:60) - логические операции
  - [`Conjunction`](../models.py:94), [`Disjunction`](../models.py:89), [`Negation`](../models.py:99)
  - [`Implication`](../models.py:125), [`Equivalence`](../models.py:130)
  - [`CNF`](../models.py:230), [`Disjunct`](../models.py:135) - КНФ и дизъюнкты
- ✅ Логический движок ([`engine.py`](../engine.py:1))
  - [`LogicalEngine.to_cnf()`](../engine.py:240) - преобразование в КНФ
  - [`LogicalEngine.resolution_method()`](../engine.py:30) - метод резолюций
  - Законы де Моргана, удаление импликаций и эквиваленций
- ✅ Базовый лексер ([`lexer.py`](../lexer.py:1))
  - [`Lexer.tokenize_line()`](../lexer.py:40) - токенизация строк
  - Поддержка идентификаторов и строк в кавычках

**Требуется доработка:**
- ❌ Полноценный лексер для всех конструкций языка
- ❌ Парсер для построения AST
- ❌ Поддержка предикатов с аргументами
- ❌ Унификация и подстановка переменных
- ❌ Арифметические операции и сравнения
- ❌ Система команд (load, get axioms, remove, help)
- ❌ REPL-интерфейс

---

## Фаза 1: Расширение лексера

### 1.1 Анализ требований к токенам

Из [`example.shldn`](../example.shldn:1) выделяем необходимые типы токенов:

**Комментарии:**
- `//` - однострочный комментарий
- `/* */` - многострочный комментарий

**Идентификаторы:**
- `игрок_1`, `монстр_дракон` - обычные идентификаторы (начинаются с маленькой буквы)
- `X`, `Y`, `Z`, `Sx`, `Sm`, `M` - переменные/термы (начинаются с БОЛЬШОЙ буквы)
- `"игрок 2 имеет уровень 1"` - строковые литералы

**Логические операторы:**
- `&` или `*` - конъюнкция (AND)
- `|` или `+` - дизъюнкция (OR)
- `!` - отрицание (NOT)
- `->` - импликация (IMPLIES)
- `==` или `<->` - эквиваленция (EQUIVALENCE)

**Предикаты:**
- `уровень(игрок(1), 2)` - предикат с аргументами
- `()` - скобки для аргументов
- `,` - разделитель аргументов

**Арифметические операторы:**
- `+`, `-`, `*`, `/` - арифметические операции
- `>`, `<`, `>=`, `<=`, `==`, `!=` - операторы сравнения

**Специальные символы:**
- `?` - маркер теоремы/запроса
- `.` - конец выражения (для команд)
- `(`, `)` - группировка

**Команды:**
- `load` - загрузка файла
- `get axioms` - получение аксиом
- `remove` - удаление аксиомы
- `help` - справка

### 1.2 Расширение TokenType

Добавить в [`lexer.py`](../lexer.py:10):

```python
class TokenType(str, Enum):
    # Идентификаторы и литералы
    IDENTIFIER = "identifier"      # игрок_1, монстр
    VARIABLE = "variable"          # X, Y, Z (начинаются с большой буквы)
    STRING = "string"              # "текст в кавычках"
    NUMBER = "number"              # 1, 2, 3.14
    
    # Логические операторы
    AND = "AND"                    # & или *
    OR = "OR"                      # | или +
    NOT = "NOT"                    # !
    IMPLIES = "IMPLIES"            # ->
    EQUIVALENCE = "EQUIVALENCE"    # == или <->
    
    # Арифметические операторы
    PLUS = "PLUS"                  # +
    MINUS = "MINUS"                # -
    MULTIPLY = "MULTIPLY"          # *
    DIVIDE = "DIVIDE"              # /
    
    # Операторы сравнения
    GT = "GT"                      # >
    LT = "LT"                      # <
    GTE = "GTE"                    # >=
    LTE = "LTE"                    # <=
    EQ = "EQ"                      # ==
    NEQ = "NEQ"                    # !=
    
    # Разделители и специальные символы
    LPAREN = "LPAREN"              # (
    RPAREN = "RPAREN"              # )
    COMMA = "COMMA"                # ,
    QUESTION = "QUESTION"          # ?
    DOT = "DOT"                    # .
    
    # Команды
    COMMAND = "COMMAND"            # load, get, remove, help
    
    # Служебные
    COMMENT = "COMMENT"            # комментарии
    EOL = "EOL"                    # конец строки
    EOF = "EOF"                    # конец файла
```

### 1.3 Реализация методов лексера

**Методы для добавления:**

1. **`skip_whitespace()`** - пропуск пробелов и табуляции
2. **`skip_comment()`** - обработка комментариев `//` и `/* */`
3. **`parse_number()`** - парсинг чисел (целых и дробных)
4. **`parse_string()`** - парсинг строк в кавычках
5. **`parse_identifier_or_variable()`** - различение идентификаторов и переменных
6. **`parse_operator()`** - парсинг операторов (с учетом многосимвольных: `->`, `==`, `>=`)
7. **`parse_command()`** - распознавание команд

**Алгоритм токенизации:**

```python
def tokenize(self, text: str) -> list[Token]:
    self.text = text
    self.pos = 0
    self.line = 1
    self.column = 1
    tokens = []
    
    while self.pos < len(self.text):
        # Пропуск пробелов
        if self.current_char.isspace():
            self.skip_whitespace()
            continue
        
        # Комментарии
        if self.peek_ahead(2) == '//':
            self.skip_line_comment()
            continue
        if self.peek_ahead(2) == '/*':
            self.skip_block_comment()
            continue
        
        # Числа
        if self.current_char.isdigit():
            tokens.append(self.parse_number())
            continue
        
        # Строки
        if self.current_char == '"':
            tokens.append(self.parse_string())
            continue
        
        # Идентификаторы и переменные
        if self.current_char.isalpha() or self.current_char == '_':
            tokens.append(self.parse_identifier_or_variable())
            continue
        
        # Операторы и специальные символы
        token = self.parse_operator()
        if token:
            tokens.append(token)
            continue
        
        raise LexerException(f"Неожиданный символ: {self.current_char}")
    
    tokens.append(Token(TokenType.EOF, None, self.pos))
    return tokens
```

### 1.4 Обработка ошибок

Добавить информативные сообщения об ошибках с указанием позиции:

```python
class LexerException(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Ошибка лексера [{line}:{column}]: {message}")
```

---

## Фаза 2: Разработка парсера

### 2.1 Грамматика языка

Определим формальную грамматику в нотации EBNF:

```ebnf
program         ::= statement*

statement       ::= comment
                  | proposition
                  | axiom
                  | theorem
                  | predicate_def
                  | command

comment         ::= "//" text EOL
                  | "/*" text "*/"

proposition     ::= identifier EOL

axiom           ::= expression "->" expression EOL

theorem         ::= "?" expression EOL

predicate_def   ::= predicate EOL

command         ::= "load" STRING DOT
                  | "get" "axioms" DOT
                  | "remove" NUMBER DOT
                  | "help" DOT

expression      ::= equivalence

equivalence     ::= implication (("==" | "<->") implication)*

implication     ::= disjunction ("->" disjunction)*

disjunction     ::= conjunction (("|" | "+") conjunction)*

conjunction     ::= negation (("&" | "*") negation)*

negation        ::= "!" negation
                  | primary

primary         ::= predicate
                  | identifier
                  | variable
                  | "(" expression ")"
                  | STRING

predicate       ::= identifier "(" argument_list ")"

argument_list   ::= argument ("," argument)*

argument        ::= expression
                  | arithmetic_expr

arithmetic_expr ::= term (("+"|"-") term)*

term            ::= factor (("*"|"/") factor)*

factor          ::= NUMBER
                  | variable
                  | predicate
                  | "(" arithmetic_expr ")"

comparison      ::= arithmetic_expr (">" | "<" | ">=" | "<=" | "==" | "!=") arithmetic_expr

identifier      ::= [a-z_][a-zA-Z0-9_]*

variable        ::= [A-Z][a-zA-Z0-9_]*
```

### 2.2 Структура парсера

Создать новый файл `parser.py`:

```python
from dataclasses import dataclass
from typing import Optional, Union
from lexer import Token, TokenType, Lexer

class ParserException(Exception):
    """Исключение парсера"""
    pass

@dataclass
class ASTNode:
    """Базовый класс для узлов AST"""
    pass

@dataclass
class PropositionNode(ASTNode):
    """Высказывание"""
    name: str

@dataclass
class PredicateNode(ASTNode):
    """Предикат с аргументами"""
    name: str
    args: list[ASTNode]

@dataclass
class VariableNode(ASTNode):
    """Переменная (терм)"""
    name: str

@dataclass
class NumberNode(ASTNode):
    """Числовой литерал"""
    value: float

@dataclass
class BinaryOpNode(ASTNode):
    """Бинарная операция"""
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    """Унарная операция"""
    op: str
    operand: ASTNode

@dataclass
class AxiomNode(ASTNode):
    """Аксиома (импликация)"""
    condition: ASTNode
    consequence: ASTNode

@dataclass
class TheoremNode(ASTNode):
    """Теорема (запрос)"""
    expression: ASTNode

@dataclass
class CommandNode(ASTNode):
    """Команда"""
    command: str
    args: list[str]

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
    
    def advance(self):
        """Переход к следующему токену"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type: TokenType) -> Token:
        """Проверка типа текущего токена"""
        if self.current_token.type != token_type:
            raise ParserException(
                f"Ожидался {token_type}, получен {self.current_token.type}"
            )
        token = self.current_token
        self.advance()
        return token
    
    def parse(self) -> list[ASTNode]:
        """Парсинг программы"""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Парсинг одного выражения"""
        # Пропуск комментариев
        if self.current_token.type == TokenType.COMMENT:
            self.advance()
            return None
        
        # Теорема
        if self.current_token.type == TokenType.QUESTION:
            return self.parse_theorem()
        
        # Команда
        if self.current_token.type == TokenType.COMMAND:
            return self.parse_command()
        
        # Выражение (может быть аксиомой или высказыванием)
        expr = self.parse_expression()
        
        # Проверка на аксиому (содержит ->)
        if self.current_token and self.current_token.type == TokenType.IMPLIES:
            self.advance()
            consequence = self.parse_expression()
            return AxiomNode(expr, consequence)
        
        return expr
```

### 2.3 Методы парсинга выражений

Реализовать методы для каждого уровня грамматики:

1. **`parse_expression()`** - точка входа для выражений
2. **`parse_equivalence()`** - эквиваленция (==, <->)
3. **`parse_implication()`** - импликация (->)
4. **`parse_disjunction()`** - дизъюнкция (|, +)
5. **`parse_conjunction()`** - конъюнкция (&, *)
6. **`parse_negation()`** - отрицание (!)
7. **`parse_primary()`** - первичные выражения
8. **`parse_predicate()`** - предикаты с аргументами
9. **`parse_arithmetic()`** - арифметические выражения
10. **`parse_comparison()`** - операторы сравнения

### 2.4 Преобразование AST в модели

Создать `ast_transformer.py` для преобразования AST в объекты из [`models.py`](../models.py:1):

```python
from models import (
    Predicate, Variable, Term,
    Conjunction, Disjunction, Negation,
    Implication, Equivalence
)
from parser import (
    ASTNode, PredicateNode, VariableNode,
    BinaryOpNode, UnaryOpNode
)

class ASTTransformer:
    def transform(self, node: ASTNode):
        """Преобразование AST в модели данных"""
        if isinstance(node, PredicateNode):
            return self.transform_predicate(node)
        elif isinstance(node, VariableNode):
            return self.transform_variable(node)
        elif isinstance(node, BinaryOpNode):
            return self.transform_binary_op(node)
        elif isinstance(node, UnaryOpNode):
            return self.transform_unary_op(node)
        # ... остальные типы узлов
    
    def transform_predicate(self, node: PredicateNode) -> Predicate:
        args = [self.transform(arg) for arg in node.args]
        return Predicate(node.name, args)
    
    def transform_variable(self, node: VariableNode):
        # Различение переменных и термов по первой букве
        if node.name[0].isupper():
            return Term(node.name)
        return Variable(node.name)
    
    def transform_binary_op(self, node: BinaryOpNode):
        left = self.transform(node.left)
        right = self.transform(node.right)
        
        if node.op in ('&', '*'):
            return Conjunction((left, right))
        elif node.op in ('|', '+'):
            return Disjunction((left, right))
        elif node.op == '->':
            return Implication((left, right))
        elif node.op in ('==', '<->'):
            return Equivalence((left, right))
```

---

## Фаза 3: Расширение моделей данных

### 3.1 Поддержка предикатов с аргументами

Расширить класс [`Predicate`](../models.py:11) в [`models.py`](../models.py:1):

```python
class Predicate:
    def __init__(self, name: str, args: Sequence["Predicate | Term | Variable"] | None = None):
        self.name = name
        self.args = args if args else []
    
    def is_ground(self) -> bool:
        """Проверка, является ли предикат основным (без переменных)"""
        if not self.args:
            return True
        return all(
            isinstance(arg, Predicate) and arg.is_ground() 
            or not isinstance(arg, (Variable, Term))
            for arg in self.args
        )
    
    def get_variables(self) -> set[str]:
        """Получение всех переменных в предикате"""
        variables = set()
        for arg in self.args:
            if isinstance(arg, (Variable, Term)):
                variables.add(arg.name)
            elif isinstance(arg, Predicate):
                variables.update(arg.get_variables())
        return variables
```

### 3.2 Классы для термов и переменных

Уже есть базовые классы [`Variable`](../models.py:50) и [`Term`](../models.py:55), но нужно расширить:

```python
class Variable(Predicate):
    """Переменная (начинается с маленькой буквы)"""
    def __init__(self, name: str):
        super().__init__(name, None)
    
    def __hash__(self):
        return hash(('var', self.name))

class Term(Variable):
    """Терм - переменная для унификации (начинается с большой буквы)"""
    def __init__(self, name: str):
        super().__init__(name)
    
    def __hash__(self):
        return hash(('term', self.name))
```

### 3.3 Арифметические выражения

Добавить новые классы для арифметики:

```python
class ArithmeticOp(Operation):
    """Базовый класс для арифметических операций"""
    def evaluate(self, bindings: dict[str, any]) -> float:
        """Вычисление значения с учетом подстановок"""
        raise NotImplementedError

class Addition(ArithmeticOp):
    def __init__(self, left, right):
        super().__init__('+', (left, right), priority=2)
    
    def evaluate(self, bindings: dict[str, any]) -> float:
        left_val = self._eval_operand(self.children[0], bindings)
        right_val = self._eval_operand(self.children[1], bindings)
        return left_val + right_val

class Subtraction(ArithmeticOp):
    def __init__(self, left, right):
        super().__init__('-', (left, right), priority=2)
    
    def evaluate(self, bindings: dict[str, any]) -> float:
        left_val = self._eval_operand(self.children[0], bindings)
        right_val = self._eval_operand(self.children[1], bindings)
        return left_val - right_val

class Multiplication(ArithmeticOp):
    def __init__(self, left, right):
        super().__init__('*', (left, right), priority=1)
    
    def evaluate(self, bindings: dict[str, any]) -> float:
        left_val = self._eval_operand(self.children[0], bindings)
        right_val = self._eval_operand(self.children[1], bindings)
        return left_val * right_val

class Division(ArithmeticOp):
    def __init__(self, left, right):
        super().__init__('/', (left, right), priority=1)
    
    def evaluate(self, bindings: dict[str, any]) -> float:
        left_val = self._eval_operand(self.children[0], bindings)
        right_val = self._eval_operand(self.children[1], bindings)
        if right_val == 0:
            raise ValueError("Деление на ноль")
        return left_val / right_val

class Comparison(Operation):
    """Операторы сравнения"""
    def __init__(self, op: str, left, right):
        super().__init__(op, (left, right), priority=3)
    
    def evaluate(self, bindings: dict[str, any]) -> bool:
        left_val = self._eval_operand(self.children[0], bindings)
        right_val = self._eval_operand(self.children[1], bindings)
        
        if self.op == '>':
            return left_val > right_val
        elif self.op == '<':
            return left_val < right_val
        elif self.op == '>=':
            return left_val >= right_val
        elif self.op == '<=':
            return left_val <= right_val
        elif self.op == '==':
            return left_val == right_val
        elif self.op == '!=':
            return left_val != right_val
```

---

## Фаза 4: Унификация и подстановка

### 4.1 Алгоритм унификации

Создать `unification.py`:

```python
from typing import Optional
from models import Predicate, Variable, Term

class Substitution:
    """Подстановка переменных"""
    def __init__(self, bindings: dict[str, Predicate] | None = None):
        self.bindings = bindings if bindings else {}
    
    def bind(self, var: str, value: Predicate) -> "Substitution":
        """Добавление связывания"""
        new_bindings = self.bindings.copy()
        new_bindings[var] = value
        return Substitution(new_bindings)
    
    def lookup(self, var: str) -> Optional[Predicate]:
        """Поиск значения переменной"""
        return self.bindings.get(var)
    
    def apply(self, pred: Predicate) -> Predicate:
        """Применение подстановки к предикату"""
        if isinstance(pred, (Variable, Term)):
            value = self.lookup(pred.name)
            if value:
                return self.apply(value)
            return pred
        
        if pred.args:
            new_args = [self.apply(arg) for arg in pred.args]
            return Predicate(pred.name, new_args)
        
        return pred
    
    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.bindings.items()) + "}"

def occurs_check(var: str, term: Predicate) -> bool:
    """Проверка вхождения переменной в терм"""
    if isinstance(term, (Variable, Term)):
        return var == term.name
    
    if term.args:
        return any(occurs_check(var, arg) for arg in term.args)
    
    return False

def unify(x: Predicate, y: Predicate, subst: Substitution | None = None) -> Optional[Substitution]:
    """
    Алгоритм унификации Робинсона
    
    Возвращает подстановку, делающую x и y идентичными, или None
    """
    if subst is None:
        subst = Substitution()
    
    # Применяем текущую подстановку
    x = subst.apply(x)
    y = subst.apply(y)
    
    # Если одинаковые - унификация успешна
    if x == y:
        return subst
    
    # Если x - переменная
    if isinstance(x, (Variable, Term)):
        if occurs_check(x.name, y):
            return None
        return subst.bind(x.name, y)
    
    # Если y - переменная
    if isinstance(y, (Variable, Term)):
        if occurs_check(y.name, x):
            return None
        return subst.bind(y.name, x)
    
    # Если оба - предикаты
    if isinstance(x, Predicate) and isinstance(y, Predicate):
        # Имена должны совпадать
        if x.name != y.name:
            return None
        
        # Количество аргументов должно совпадать
        if len(x.args) != len(y.args):
            return None
        
        # Унифицируем аргументы попарно
        for x_arg, y_arg in zip(x.args, y.args):
            subst = unify(x_arg, y_arg, subst)
            if subst is None:
                return None
        
        return subst
    
    return None

def unify_list(predicates: list[Predicate]) -> Optional[Substitution]:
    """Унификация списка предикатов"""
    if not predicates:
        return Substitution()
    
    subst = Substitution()
    first = predicates[0]
    
    for pred in predicates[1:]:
        subst = unify(first, pred, subst)
        if subst is None:
            return None
        first = subst.apply(first)
    
    return subst
```

### 4.2 Интеграция унификации в движок

Расширить [`LogicalEngine`](../engine.py:20) в [`engine.py`](../engine.py:1):

```python
from unification import unify, Substitution

class LogicalEngine:
    def __init__(self):
        self.axioms: list[Disjunct] = []
        self.facts: list[Predicate] = []  # База фактов
    
    def add_fact(self, predicate: Predicate):
        """Добавление факта в базу знаний"""
        self.facts.append(predicate)
    
    def query(self, goal: Predicate) -> list[Substitution]:
        """
        Запрос к базе знаний
        Возвращает список подстановок, удовлетворяющих запросу
        """
        results = []
        
        # Поиск в фактах
        for fact in self.facts:
            subst = unify(goal, fact)
            if subst is not None:
                results.append(subst)
        
        # Поиск в аксиомах (правилах)
        for axiom in self.axioms:
            # Попытка унификации с головой правила
            # и доказательство тела
            # (требует реализации backward chaining)
            pass
        
        return results
    
    def backward_chaining(self, goal: Predicate, depth: int = 0, max_depth: int = 100) -> list[Substitution]:
        """
        Обратный вывод для доказательства цели
        """
        if depth > max_depth:
            return []
        
        results = []
        
        # Проверка в фактах
        for fact in self.facts:
            subst = unify(goal, fact)
            if subst:
                results.append(subst)
        
        # Проверка в правилах
        for axiom in self.axioms:
            # Если аксиома имеет вид: условие -> следствие
            # и следствие унифицируется с целью,
            # то пытаемся доказать условие
            if isinstance(axiom, Implication):
                head_subst = unify(goal, axiom.children[1])
                if head_subst:
                    # Применяем подстановку к условию
                    body = head_subst.apply(axiom.children[0])
                    # Рекурсивно доказываем условие
                    body_results = self.backward_chaining(body, depth + 1, max_depth)
                    results.extend(body_results)
        
        return results
```

---

## Фаза 5: Арифметические операции

### 5.1 Вычисление арифметических выражений

Добавить в `unification.py`:

```python
def evaluate_arithmetic(expr, bindings: dict[str, any]) -> float:
    """Вычисление арифметического выражения"""
    if isinstance(expr, (int, float)):
        return expr
    
    if isinstance(expr, (Variable, Term)):
        value = bindings.get(expr.name)
        if value is None:
            raise ValueError(f"Переменная {expr.name} не связана")
        return evaluate_arithmetic(value, bindings)
    
    if isinstance(expr, Addition):
        left = evaluate_arithmetic(expr.children[0], bindings)
        right = evaluate_arithmetic(expr.children[1], bindings)
        return left + right
    
    if isinstance(expr, Subtraction):
        left = evaluate_arithmetic(expr.children[0], bindings)
        right = evaluate_arithmetic(expr