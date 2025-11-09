import pytest

from lexer import Lexer, LexerException, Token, TokenType


TEST_DATA = [
    {
        'input': 'игрок_1',
        'expected': [Token(TokenType.IDENTIFIER, 'игрок_1', 0), Token(TokenType.EOF, '', 7)]
    },
    {
        'input': 'игрок_1.',
        'expected': [
            Token(TokenType.IDENTIFIER, 'игрок_1', 0),
            Token(TokenType.DOT, '.', 7),
            Token(TokenType.EOF, '', 8)
        ]
    },
    {
        'input': '"абоба',
        'error': LexerException('Незакрытая строка', position=6, line=1, column=7)
    },
]


@pytest.mark.parametrize(
    ('input', 'expected'),
    [(test['input'], test['expected']) for test in TEST_DATA if 'expected' in test]
)
def test_lexer_normal(input: str, expected: list[Token]):
    lexer = Lexer(text=input)
    result = lexer.tokenize()
    assert result == expected


@pytest.mark.parametrize(
    ('input', 'error'),
    [(test['input'], test['error']) for test in TEST_DATA if 'error' in test]
)
def test_lexer_error(input: str, error: LexerException):
    lexer = Lexer(text=input)
    with pytest.raises(LexerException) as exc_info:
        lexer.tokenize()
    
    assert str(exc_info.value) == f'{error.message} (line {error.line}, column {error.column})' and \
           exc_info.value.position == error.position and \
           exc_info.value.line == error.line and \
           exc_info.value.column == error.column