import pytest

from lexer import Lexer, LexerException, Token, TokenType


# Тестовые данные для проверки различных токенов
TEST_DATA = [
    # Идентификаторы
    {
        "input": "игрок_1",
        "expected": [
            Token(TokenType.IDENTIFIER, "игрок_1", 0),
            Token(TokenType.EOF, None, 7),
        ],
    },
    # Переменные
    {
        "input": "X",
        "expected": [
            Token(TokenType.VARIABLE, "X", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    # Команды
    {
        "input": "load",
        "expected": [
            Token(TokenType.COMMAND, "load", 0),
            Token(TokenType.EOF, None, 4),
        ],
    },
    # Строки
    {
        "input": '"тестовая строка"',
        "expected": [
            Token(TokenType.STRING, "тестовая строка", 0),
            Token(TokenType.EOF, None, 17),
        ],
    },
    # Числа
    {
        "input": "123",
        "expected": [
            Token(TokenType.NUMBER, 123, 0),
            Token(TokenType.EOF, None, 3),
        ],
    },
    {
        "input": "12.34",
        "expected": [
            Token(TokenType.NUMBER, 12.34, 0),
            Token(TokenType.EOF, None, 5),
        ],
    },
    # Логические операторы
    {
        "input": "&",
        "expected": [
            Token(TokenType.AND, "&", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "|",
        "expected": [
            Token(TokenType.OR, "|", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "!",
        "expected": [
            Token(TokenType.NOT, "!", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "->",
        "expected": [
            Token(TokenType.IMPLIES, "->", 0),
            Token(TokenType.EOF, None, 2),
        ],
    },
    {
        "input": "==",
        "expected": [
            Token(TokenType.EQ, "==", 0),
            Token(TokenType.EOF, None, 2),
        ],
    },
    {
        "input": "<->",
        "expected": [
            Token(TokenType.EQUIVALENCE, "<->", 0),
            Token(TokenType.EOF, None, 3),
        ],
    },
    # Арифметические операторы
    {
        "input": "+",
        "expected": [
            Token(TokenType.PLUS, "+", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "-",
        "expected": [
            Token(TokenType.MINUS, "-", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "*",
        "expected": [
            Token(TokenType.MULTIPLY, "*", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "/",
        "expected": [
            Token(TokenType.DIVIDE, "/", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    # Операторы сравнения
    {
        "input": ">",
        "expected": [
            Token(TokenType.GT, ">", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "<",
        "expected": [
            Token(TokenType.LT, "<", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": ">=",
        "expected": [
            Token(TokenType.GTE, ">=", 0),
            Token(TokenType.EOF, None, 2),
        ],
    },
    {
        "input": "<=",
        "expected": [
            Token(TokenType.LTE, "<=", 0),
            Token(TokenType.EOF, None, 2),
        ],
    },
    {
        "input": "!=",
        "expected": [
            Token(TokenType.NEQ, "!=", 0),
            Token(TokenType.EOF, None, 2),
        ],
    },
    # Разделители
    {
        "input": "(",
        "expected": [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": ")",
        "expected": [
            Token(TokenType.RPAREN, ")", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": ",",
        "expected": [
            Token(TokenType.COMMA, ",", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    {
        "input": "?",
        "expected": [
            Token(TokenType.QUESTION, "?", 0),
            Token(TokenType.EOF, None, 1),
        ],
    },
    # Комплексные выражения
    {
        "input": "игрок_1_уровень_10 -> игрок_1_победитель",
        "expected": [
            Token(TokenType.IDENTIFIER, "игрок_1_уровень_10", 0),
            Token(TokenType.IMPLIES, "->", 19),
            Token(TokenType.IDENTIFIER, "игрок_1_победитель", 22),
            Token(TokenType.EOF, None, 40),
        ],
    },
    {
        "input": "уровень(игрок(X), 2)",
        "expected": [
            Token(TokenType.IDENTIFIER, "уровень", 0),
            Token(TokenType.LPAREN, "(", 7),
            Token(TokenType.IDENTIFIER, "игрок", 8),
            Token(TokenType.LPAREN, "(", 13),
            Token(TokenType.VARIABLE, "X", 14),
            Token(TokenType.RPAREN, ")", 15),
            Token(TokenType.COMMA, ",", 16),
            Token(TokenType.NUMBER, 2, 18),
            Token(TokenType.RPAREN, ")", 19),
            Token(TokenType.EOF, None, 20),
        ],
    },
]


@pytest.mark.parametrize(
    ("input", "expected"),
    [(test["input"], test["expected"]) for test in TEST_DATA],
)
def test_lexer_normal(input: str, expected: list[Token]):
    lexer = Lexer()
    result = lexer.tokenize(input)
    assert result == expected


# Тестовые данные для проверки ошибок
ERROR_TEST_DATA = [
    {
        "input": '"незакрытая строка',
        "error": "Незакрытая строка",
    },
    {
        "input": '/* незакрытый комментарий',
        "error": "Незакрытый блочный комментарий",
    },
    {
        "input": '@',
        "error": "Неожиданный символ: @",
    },
]


@pytest.mark.parametrize(
    ("input", "error"),
    [(test["input"], test["error"]) for test in ERROR_TEST_DATA],
)
def test_lexer_error(input: str, error: str):
    lexer = Lexer()
    with pytest.raises(LexerException) as exc_info:
        lexer.tokenize(input)
    
    assert error in str(exc_info.value)
