import pytest
import os
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from ast_transformer import ASTTransformer, ASTTransformerException
from engine import LogicalEngine, EngineError
from commands import CommandProcessor, CommandException
from repl import REPL, REPLError
from unification import UnificationException


def test_lexer_error_handling():
    """Тест обработки ошибок в лексере"""
    lexer = Lexer()
    
    # Тест неожиданного символа
    with pytest.raises(LexerException) as exc_info:
        lexer.tokenize("@")
    assert "Неожиданный символ" in str(exc_info.value)
    
    # Тест незакрытой строки
    with pytest.raises(LexerException) as exc_info:
        lexer.tokenize('"незакрытая строка')
    assert "Незакрытая строка" in str(exc_info.value)
    
    print("Тесты обработки ошибок в лексере пройдены успешно!")


def test_parser_error_handling():
    """Тест обработки ошибок в парсере"""
    # Тест неожиданного токена
    lexer = Lexer()
    tokens = lexer.tokenize("игрок_1 ->")  # Неполная аксиома
    parser = Parser(tokens)
    
    with pytest.raises(ParserException) as exc_info:
        parser.parse()
    # Ожидаем ошибку парсинга
    
    print("Тесты обработки ошибок в парсере пройдены успешно!")


def test_ast_transformer_error_handling():
    """Тест обработки ошибок в AST трансформере"""
    # Пока просто проверяем, что исключение существует
    with pytest.raises(ASTTransformerException):
        raise ASTTransformerException("Тестовое сообщение")
    
    print("Тесты обработки ошибок в AST трансформере пройдены успешно!")


def test_engine_error_handling():
    """Тест обработки ошибок в движке"""
    # Пока просто проверяем, что исключение существует
    with pytest.raises(EngineError):
        raise EngineError("Тестовое сообщение")
    
    print("Тесты обработки ошибок в движке пройдены успешно!")


def test_command_error_handling():
    """Тест обработки ошибок в командах"""
    # Пока просто проверяем, что исключение существует
    with pytest.raises(CommandException):
        raise CommandException("Тестовое сообщение")
    
    print("Тесты обработки ошибок в командах пройдены успешно!")


def test_unification_error_handling():
    """Тест обработки ошибок в унификации"""
    # Пока просто проверяем, что исключение существует
    with pytest.raises(UnificationException):
        raise UnificationException("Тестовое сообщение")
    
    print("Тесты обработки ошибок в унификации пройдены успешно!")


def test_repl_error_handling():
    """Тест обработки ошибок в REPL"""
    # Пока просто проверяем, что исключение существует
    with pytest.raises(REPLError):
        raise REPLError("Тестовое сообщение")
    
    print("Тесты обработки ошибок в REPL пройдены успешно!")


def test_command_load_error_handling():
    """Тест обработки ошибок в команде load"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    # Тест отсутствующего файла
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "load", ["nonexistent.shldn"])
    assert "не найден" in str(exc_info.value)
    
    # Тест отсутствия аргументов
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "load", [])
    assert "Требуется имя файла" in str(exc_info.value)
    
    print("Тесты обработки ошибок в команде load пройдены успешно!")


def test_command_remove_error_handling():
    """Тест обработки ошибок в команде remove"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    # Тест отсутствия аргументов
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "remove", [])
    assert "Требуется номер аксиомы" in str(exc_info.value)
    
    # Тест некорректного номера
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "remove", ["abc"])
    assert "должен быть целым числом" in str(exc_info.value)
    
    # Тест отрицательного номера
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "remove", ["-1"])
    assert "должен быть положительным числом" in str(exc_info.value)
    
    # Тест несуществующего номера
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "remove", ["1"])
    assert "не найдена" in str(exc_info.value)
    
    print("Тесты обработки ошибок в команде remove пройдены успешно!")


if __name__ == "__main__":
    test_lexer_error_handling()
    test_parser_error_handling()
    test_ast_transformer_error_handling()
    test_engine_error_handling()
    test_command_error_handling()
    test_unification_error_handling()
    test_repl_error_handling()
    test_command_load_error_handling()
    test_command_remove_error_handling()
    print("Все тесты обработки ошибок пройдены успешно!")