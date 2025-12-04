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
    {
        "input": "игрок_1.",
        "expected": [
            Token(TokenType.IDENTIFIER, "игрок_1", 0),
            Token(TokenType.DOT, ".", 7),
            Token(TokenType.EOL, None, 8),
        ],
    },
    {"input": '"абоба', "error": LexerException("Незакрытая строка")},
]


@pytest.mark.parametrize(
    ("input", "expected"),
    [(test["input"], test["expected"]) for test in TEST_DATA if "expected" in test],
)
def test_lexer_normal(input: str, expected: list[Token]):
    lexer = Lexer()
    result = lexer.tokenize_line(input)
    assert result == expected


# @pytest.mark.parametrize(
#     ('input', 'error'),
#     [(test['input'], test['error']) for test in TEST_DATA if 'error' in test]
# )
# def test_lexer_error(input: str, error: LexerException):
#     lexer = Lexer()
#     with pytest.raises(LexerException) as exc_info:
#         lexer.tokenize_line(input)

#     assert str(exc_info.value) == f'{error.message} (line {error.line}, column {error.column})' and \
#            exc_info.value.position == error.position and \
#            exc_info.value.line == error.line and \
#            exc_info.value.column == error.column
