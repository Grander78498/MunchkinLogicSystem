# Архитектура системы логического языка программирования

## Общая структура проекта

```
MunchkinLogicSystem/
├── models.py              # Модели данных (Operation, Predicate, CNF, etc.)
├── engine.py              # Логический движок (преобразования, резолюции)
├── lexer.py               # Лексический анализатор
├── parser.py              # Синтаксический анализатор (НОВЫЙ)
├── knowledge_base.py      # База знаний (НОВЫЙ)
├── exceptions.py          # Иерархия исключений (НОВЫЙ)
├── repl.py                # Консольный интерфейс (НОВЫЙ)
├── main.py                # Точка входа
├── demo.py                # Демонстрация работы (НОВЫЙ)
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py     # (НОВЫЙ)
│   ├── test_engine.py
│   └── test_kb.py         # (НОВЫЙ)
├── examples/
│   ├── situation1.shldn   # (НОВЫЙ)
│   ├── situation2.shldn   # (НОВЫЙ)
│   └── situation3.shldn   # (НОВЫЙ)
└── README.md
```

## Диаграмма компонентов

```mermaid
graph TB
    User[Пользователь] --> REPL[REPL Interface]
    
    REPL --> Lexer[Lexer]
    REPL --> Parser[Parser]
    REPL --> KB[Knowledge Base]
    REPL --> Engine[Logical Engine]
    
    Lexer --> Parser
    Parser --> Models[Models]
    
    KB --> Models
    Engine --> Models
    Engine --> KB
    
    Models --> Predicate[Predicate/Variable]
    Models --> Operations[Operations]
    Models --> CNF[CNF/Disjunct]
    
    style REPL fill:#e1f5ff
    style Lexer fill:#fff4e1
    style Parser fill:#fff4e1
    style KB fill:#e8f5e9
    style Engine fill:#f3e5f5
    style Models fill:#fce4ec
```

## Поток обработки данных

### 1. Обработка высказывания

```mermaid
sequenceDiagram
    participant U as User
    participant R as REPL
    participant L as Lexer
    participant P as Parser
    participant KB as KnowledgeBase
    
    U->>R: игрок_1
    R->>L: tokenize("игрок_1")
    L->>R: [Token(IDENTIFIER, "игрок_1")]
    R->>P: parse(tokens)
    P->>R: Variable("игрок_1")
    R->>KB: add_statement("игрок_1")
    KB->>R: Statement(id=1, name="игрок_1")
    R->>U: ✓ Добавлено высказывание [1]: игрок_1
```

### 2. Обработка аксиомы

```mermaid
sequenceDiagram
    participant U as User
    participant R as REPL
    participant L as Lexer
    participant P as Parser
    participant KB as KnowledgeBase
    participant E as Engine
    
    U->>R: a & b -> c
    R->>L: tokenize("a & b -> c")
    L->>R: [Token(ID,"a"), Token(AND), Token(ID,"b"), Token(IMPLIES), Token(ID,"c")]
    R->>P: parse(tokens)
    P->>R: Implication(Conjunction(a,b), c)
    R->>KB: add_axiom(expression)
    KB->>R: Axiom(id=1, expression=...)
    R->>E: add_axiom(expression)
    E->>E: to_cnf(expression)
    E->>R: CNF added
    R->>U: ✓ Добавлена аксиома (1): a & b -> c
```

### 3. Проверка теоремы

```mermaid
sequenceDiagram
    participant U as User
    participant R as REPL
    participant L as Lexer
    participant P as Parser
    participant E as Engine
    participant KB as KnowledgeBase
    
    U->>R: ? a -> c
    R->>L: tokenize("a -> c")
    L->>R: tokens
    R->>P: parse(tokens)
    P->>R: Implication(a, c)
    R->>E: load_axioms_from_kb()
    E->>KB: get_all_axioms()
    KB->>E: [axiom1, axiom2, ...]
    E->>E: resolution_method(theorem)
    E->>E: to_cnf(¬theorem)
    E->>E: apply_resolution()
    E->>R: proof result
    R->>U: [вывод доказательства]
```

## Архитектура парсера

### Приоритет операторов (от низкого к высокому)

```
1. <->  (эквиваленция)      - parse_equivalence()
2. ->   (импликация)         - parse_implication()
3. | +  (дизъюнкция)         - parse_disjunction()
4. & *  (конъюнкция)         - parse_conjunction()
5. !    (отрицание)          - parse_negation()
6. ()   (скобки)             - parse_primary()
7. id   (идентификаторы)     - parse_primary()
```

### Грамматика языка (EBNF)

```ebnf
expression     = equivalence ;
equivalence    = implication { "<->" implication } ;
implication    = disjunction [ "->" disjunction ] ;
disjunction    = conjunction { ("|" | "+") conjunction } ;
conjunction    = negation { ("&" | "*") negation } ;
negation       = "!" negation | primary ;
primary        = identifier | "(" expression ")" | string ;
identifier     = letter { letter | digit | "_" } ;
string         = '"' { any_char } '"' ;
```

## Структура базы знаний

```mermaid
classDiagram
    class KnowledgeBase {
        -statements: dict[str, Statement]
        -axioms: list[Axiom]
        -_next_statement_id: int
        -_next_axiom_id: int
        +add_statement(name, desc) Statement
        +add_axiom(expr, desc) Axiom
        +remove_axiom(id) bool
        +get_all_statements() list
        +get_all_axioms() list
        +clear()
    }
    
    class Statement {
        +id: int
        +name: str
        +description: str
    }
    
    class Axiom {
        +id: int
        +expression: Operation
        +description: str
    }
    
    KnowledgeBase "1" --> "*" Statement
    KnowledgeBase "1" --> "*" Axiom
    Axiom --> Operation
```

## Алгоритм метода резолюций

```mermaid
flowchart TD
    Start([Начало]) --> LoadAxioms[Загрузить аксиомы из БЗ]
    LoadAxioms --> NegateTheorem[Отрицать теорему]
    NegateTheorem --> ConvertCNF[Преобразовать в КНФ]
    ConvertCNF --> AddToAxioms[Добавить к аксиомам]
    AddToAxioms --> InitLoop[i = 0, j = 0]
    
    InitLoop --> CheckI{i < len?}
    CheckI -->|Нет| NotProved[Теорема не доказана]
    CheckI -->|Да| CheckJ{j < len?}
    
    CheckJ -->|Нет| IncI[i++]
    IncI --> CheckI
    
    CheckJ -->|Да| TryResolve[Попытка резолюции]
    TryResolve --> HasContrary{Есть противоположные литералы?}
    
    HasContrary -->|Нет| IncJ[j++]
    IncJ --> CheckJ
    
    HasContrary -->|Да| Resolve[Применить резолюцию]
    Resolve --> CheckEmpty{Пустой дизъюнкт?}
    
    CheckEmpty -->|Да| Proved[Теорема доказана!]
    CheckEmpty -->|Нет| AddNew[Добавить новый дизъюнкт]
    AddNew --> IncJ
    
    NotProved --> End([Конец])
    Proved --> End
```

## Преобразование в КНФ

```mermaid
flowchart TD
    Start([Выражение]) --> RemoveEq[Устранить эквиваленции]
    RemoveEq --> RemoveImpl[Устранить импликации]
    RemoveImpl --> RemoveDblNeg[Устранить двойные отрицания]
    RemoveDblNeg --> DeMorgan[Применить законы де Моргана]
    DeMorgan --> Distribute[Применить дистрибутивность]
    Distribute --> CreateCNF[Создать CNF]
    CreateCNF --> Simplify[Упростить]
    Simplify --> End([КНФ])
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
```

## Обработка ошибок

```mermaid
graph TD
    Error[Ошибка] --> Type{Тип ошибки}
    
    Type -->|Лексер| LexerErr[LexerException]
    Type -->|Парсер| ParserErr[ParserException]
    Type -->|БЗ| KBErr[KnowledgeBaseException]
    Type -->|Движок| EngineErr[EngineException]
    Type -->|Другое| GenErr[Exception]
    
    LexerErr --> Handle[Обработать в REPL]
    ParserErr --> Handle
    KBErr --> Handle
    EngineErr --> Handle
    GenErr --> Handle
    
    Handle --> ShowMsg[Показать сообщение пользователю]
    ShowMsg --> Continue[Продолжить работу]
    
    style Error fill:#ffebee
    style Handle fill:#fff3e0
    style Continue fill:#e8f5e9
```

## Интеграция компонентов

### LogicalEngine + KnowledgeBase

```python
class LogicalEngine:
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.kb = knowledge_base or KnowledgeBase()
        self.axioms: list[Disjunct] = []
    
    def load_axioms_from_kb(self):
        """Синхронизация с базой знаний"""
        self.axioms.clear()
        for axiom in self.kb.get_all_axioms():
            cnf = self.to_cnf(axiom.expression)
            if cnf.children:
                self.axioms.extend(cnf.children)
```

### REPL + все компоненты

```python
class REPL:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.engine = LogicalEngine(self.kb)
        self.lexer = Lexer()
        self.parser = Parser([])
    
    def process_line(self, line: str):
        # 1. Лексический анализ
        tokens = self.lexer.tokenize_line(line)
        
        # 2. Синтаксический анализ
        self.parser.tokens = tokens
        expression = self.parser.parse()
        
        # 3. Обработка в зависимости от типа
        if is_theorem:
            self.engine.resolution_method(expression)
        elif is_axiom:
            self.kb.add_axiom(expression)
            self.engine.add_axiom(expression)
        else:
            self.kb.add_statement(expression.name)
```

## Расширяемость системы

### Добавление новых операторов

1. Добавить токен в [`TokenType`](lexer.py:10)
2. Добавить обработку в [`Lexer.tokenize_line()`](lexer.py:39)
3. Добавить класс операции в [`models.py`](models.py)
4. Добавить метод парсинга в `Parser`
5. Добавить преобразование в [`LogicalEngine`](engine.py:20)

### Добавление новых команд

1. Добавить метод `cmd_<название>()` в `REPL`
2. Добавить обработку в `REPL.process_line()`
3. Обновить справку в `cmd_help()`

### Добавление новых правил вывода

1. Создать метод в [`LogicalEngine`](engine.py:20)
2. Добавить вызов в `REPL.process_theorem()`
3. Документировать в справке

## Производительность

### Оптимизации

1. **Кэширование КНФ**: Сохранять преобразованные выражения
2. **Индексация дизъюнктов**: Быстрый поиск противоположных литералов
3. **Ранняя остановка**: Прекращать резолюцию при нахождении пустого дизъюнкта
4. **Упрощение на лету**: Удалять тавтологии сразу

### Ограничения

- Максимальная длина выражения: не ограничена
- Максимальное количество аксиом: не ограничено
- Глубина вложенности скобок: не ограничена
- Время работы резолюции: экспоненциальное в худшем случае

## Тестирование

### Модульные тесты

```python
# test_lexer.py - тестирование лексера
# test_parser.py - тестирование парсера
# test_engine.py - тестирование движка
# test_kb.py - тестирование базы знаний
# test_integration.py - интеграционные тесты
```

### Покрытие тестами

- Лексер: все типы токенов, ошибки
- Парсер: все операторы, приоритеты, ошибки
- Движок: все преобразования, резолюции
- База знаний: CRUD операции
- REPL: все команды

## Безопасность

### Обработка ввода

- Валидация всех входных данных
- Защита от бесконечных циклов
- Ограничение глубины рекурсии
- Обработка некорректных файлов

### Обработка ошибок

- Все исключения перехватываются
- Понятные сообщения об ошибках
- Логирование критических ошибок
- Graceful degradation