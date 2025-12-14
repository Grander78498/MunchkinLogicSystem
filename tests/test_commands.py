import pytest
import os
from lexer import Lexer
from parser import Parser
from ast_transformer import ASTTransformer
from engine import LogicalEngine
from commands import CommandProcessor, CommandException


def test_parse_command_with_subcommand():
    """Тест парсинга команды с подкомандой"""
    input_text = "get axioms"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна команда
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "CommandNode"
    
    command_node = ast_nodes[0]
    assert command_node.command == "get"
    assert command_node.args == ["axioms"]


def test_parse_command_with_file():
    """Тест парсинга команды с файлом"""
    input_text = "load example.shldn"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна команда
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "CommandNode"
    
    command_node = ast_nodes[0]
    assert command_node.command == "load"
    assert command_node.args == ["example.shldn"]


def test_parse_command_with_number():
    """Тест парсинга команды с числом"""
    input_text = "remove 1"
    
    lexer = Lexer()
    tokens = lexer.tokenize(input_text)
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    
    # Должна быть одна команда
    assert len(ast_nodes) == 1
    assert ast_nodes[0].__class__.__name__ == "CommandNode"
    
    command_node = ast_nodes[0]
    assert command_node.command == "remove"
    assert command_node.args == ["1"]


def test_command_processor_help():
    """Тест команды помощи"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    result = processor.execute(engine, "help", [])
    assert "Справка по языку SHLDN" in result
    assert "load <файл>" in result
    assert "get axioms" in result


def test_command_processor_get_axioms_empty():
    """Тест команды get axioms с пустой базой"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    result = processor.execute(engine, "get", ["axioms"])
    assert "Нет аксиом в базе знаний" in result


def test_command_processor_remove_empty():
    """Тест команды remove с пустой базой"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "remove", ["1"])
    
    assert "Аксиома с номером 1 не найдена" in str(exc_info.value)


def test_command_processor_load_nonexistent():
    """Тест команды load с несуществующим файлом"""
    engine = LogicalEngine()
    processor = CommandProcessor()
    
    with pytest.raises(CommandException) as exc_info:
        processor.execute(engine, "load", ["nonexistent.shldn"])
    
    assert "Файл 'nonexistent.shldn' не найден" in str(exc_info.value)


if __name__ == "__main__":
    test_parse_command_with_subcommand()
    test_parse_command_with_file()
    test_parse_command_with_number()
    test_command_processor_help()
    test_command_processor_get_axioms_empty()
    test_command_processor_remove_empty()
    test_command_processor_load_nonexistent()
    print("Все тесты команд пройдены успешно!")