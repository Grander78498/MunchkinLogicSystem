import pytest
from repl import REPL
from engine import LogicalEngine
from commands import CommandProcessor


def test_repl_initialization():
    """Тест инициализации REPL"""
    repl = REPL()
    
    assert isinstance(repl.engine, LogicalEngine)
    assert isinstance(repl.command_processor, CommandProcessor)
    assert repl.lexer is not None
    assert repl.parser is not None
    assert repl.transformer is not None


def test_repl_process_help_command():
    """Тест обработки команды помощи в REPL"""
    repl = REPL()
    
    # Перехватываем вывод
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        repl.process_input("help")
        output = captured_output.getvalue()
        assert "Справка по языку SHLDN" in output
        assert "load <файл>" in output
    finally:
        sys.stdout = sys.__stdout__


def test_repl_process_get_axioms_command():
    """Тест обработки команды get axioms в REPL"""
    repl = REPL()
    
    # Перехватываем вывод
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        repl.process_input("get axioms")
        output = captured_output.getvalue()
        assert "Нет аксиом в базе знаний" in output
    finally:
        sys.stdout = sys.__stdout__


def test_repl_process_invalid_command():
    """Тест обработки невалидной команды в REPL"""
    repl = REPL()

    # Перехватываем вывод
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        repl.process_input("invalid_command")
        output = captured_output.getvalue()
        # Теперь невалидные команды обрабатываются как выражения, что является корректным поведением
        assert "Выражение добавлено как аксиома" in output
    finally:
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    test_repl_initialization()
    test_repl_process_help_command()
    test_repl_process_get_axioms_command()
    test_repl_process_invalid_command()
    print("Все тесты REPL пройдены успешно!")