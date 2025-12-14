import pytest

from lexer import Lexer, LexerException, Token, TokenType


TEST_DATA = [
    {
        "input": "игрок_1",
        "expected": [
            Token(TokenType.IDENTIFIER, "игрок_1", 0),
            Token(TokenType.EOL, None, 7),
        ],
    },
    {"input": '"абоба', "error": LexerException("Незакрытая строка", 0)},
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
    {
        "input": "a <-> b",
        "expected": [
            Token(TokenType.IDENTIFIER, "a", 0),
            Token(TokenType.EQUIVALENCE, "<->", 2),
            Token(TokenType.IDENTIFIER, "b", 6),
            Token(TokenType.EOL, None, 7),
        ],
    },
    {
        "input": "?(a & b)",
        "expected": [
            Token(TokenType.QUESTION, "?", 0),
            Token(TokenType.LPAREN, "(", 1),
            Token(TokenType.IDENTIFIER, "a", 2),
            Token(TokenType.AND, "&", 4),
            Token(TokenType.IDENTIFIER, "b", 6),
            Token(TokenType.RPAREN, ")", 7),
            Token(TokenType.EOL, None, 8),
        ],
    },
    {
        "input": '"уровень игрока 1 равен 10"',
        "expected": [
            Token(TokenType.IDENTIFIER, "уровень игрока 1 равен 10", 0),
            Token(TokenType.EOL, None, 27),
        ],
    },
]


@pytest.mark.parametrize(
    ("input", "expected"),
    [(test["input"], test["expected"]) for test in TEST_DATA if "expected" in test],
)
def test_lexer_normal(input: str, expected: list[Token]):
    lexer = Lexer()
    result = lexer.tokenize_line(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "error"),
    [(test["input"], test["error"]) for test in TEST_DATA if "error" in test],
)
def test_lexer_errors(input: str, error: LexerException):
    lexer = Lexer()
    with pytest.raises(LexerException) as exc_info:
        lexer.tokenize_line(input)
    
    # Проверяем тип ошибки и позицию
    assert isinstance(exc_info.value, type(error))
    if error.position is not None:
        assert exc_info.value.position == error.position
