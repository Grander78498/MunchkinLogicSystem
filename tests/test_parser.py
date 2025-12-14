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
    ("a -> b -> c", Implication((Variable("a"), Implication((Variable("b"), Variable("c")))))),
    ("a | b & c", Disjunction((Variable("a"), Conjunction((Variable("b"), Variable("c")))))),
    ("!a & !b", Conjunction((Negation(Variable("a")), Negation(Variable("b"))))),
]


@pytest.mark.parametrize(("input", "expected"), TEST_DATA)
def test_parser(input: str, expected):
    result = parse_expression(input)
    assert str(result) == str(expected)


ERROR_TEST_DATA = [
    ("", "Пустое выражение"),
    ("a &", "конец выражения"),
    ("(a & b", "Ожидалась закрывающая скобка"),
    ("a & & b", "Неожиданный токен"),
]


@pytest.mark.parametrize(("input", "error_message"), ERROR_TEST_DATA)
def test_parser_errors(input: str, error_message: str):
    with pytest.raises(ParserException) as exc_info:
        parse_expression(input)
    
    assert error_message in str(exc_info.value)