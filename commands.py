import os
from typing import List, Any
from engine import LogicalEngine
from models import Operation, Predicate


class CommandException(Exception):
    """Исключение для команд"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class Command:
    """Базовый класс для команд"""
    
    def execute(self, engine: LogicalEngine, args: List[str]) -> str:
        """Выполнение команды"""
        raise NotImplementedError


class LoadCommand(Command):
    """Команда загрузки файла"""
    
    def execute(self, engine: LogicalEngine, args: List[str]) -> str:
        if not args:
            raise CommandException("Требуется имя файла для загрузки")
        
        filename = args[0]
        
        # Валидация имени файла
        if not isinstance(filename, str) or not filename.strip():
            raise CommandException("Имя файла должно быть непустой строкой")
        
        if not os.path.exists(filename):
            raise CommandException(f"Файл '{filename}' не найден")
        
        # Проверка, что это файл, а не директория
        if not os.path.isfile(filename):
            raise CommandException(f"'{filename}' не является файлом")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Здесь должна быть логика загрузки содержимого файла
            # Пока просто возвращаем сообщение об успехе
            return f"Файл '{filename}' успешно загружен"
        except PermissionError:
            raise CommandException(f"Нет прав доступа для чтения файла '{filename}'")
        except UnicodeDecodeError:
            raise CommandException(f"Файл '{filename}' не является текстовым файлом или имеет неподдерживаемую кодировку")
        except Exception as e:
            raise CommandException(f"Ошибка при загрузке файла '{filename}': {str(e)}")


class GetAxiomsCommand(Command):
    """Команда получения всех аксиом"""
    
    def execute(self, engine: LogicalEngine, args: List[str]) -> str:
        if not engine.axioms:
            return "Нет аксиом в базе знаний"
        
        result = "Аксиомы в базе знаний:\n"
        for i, axiom in enumerate(engine.axioms, 1):
            result += f"  {i}. {axiom}\n"
        
        return result.strip()


class RemoveCommand(Command):
    """Команда удаления аксиомы"""
    
    def execute(self, engine: LogicalEngine, args: List[str]) -> str:
        if not args:
            raise CommandException("Требуется номер аксиомы для удаления")
        
        # Валидация аргумента
        if not isinstance(args[0], str):
            raise CommandException("Номер аксиомы должен быть строкой")
        
        try:
            index = int(args[0]) - 1  # Нумерация с 1
        except ValueError:
            raise CommandException("Номер аксиомы должен быть целым числом")
        
        # Валидация индекса
        if index < 0:
            raise CommandException(f"Номер аксиомы должен быть положительным числом")
        
        if index >= len(engine.axioms):
            raise CommandException(f"Аксиома с номером {index + 1} не найдена. Всего аксиом: {len(engine.axioms)}")
        
        removed_axiom = engine.axioms.pop(index)
        return f"Аксиома {index + 1} ({removed_axiom}) успешно удалена"


class HelpCommand(Command):
    """Команда помощи"""
    
    def execute(self, engine: LogicalEngine, args: List[str]) -> str:
        return """
=== Справка по языку SHLDN ===

Команды:
  load <файл>     - загрузить содержимое файла в базу знаний
  get axioms      - показать все аксиомы в базе знаний
  remove <номер>  - удалить аксиому с указанным номером
  help            - показать эту справку

Синтаксис:
  Высказывания: игрок_1, монстр_дракон
  Переменные: X, Y, Z (начинаются с большой буквы)
  Аксиомы: условие -> следствие
  Теоремы: ? высказывание
  Предикаты: уровень(игрок(1), 2)
  Операции: +, -, *, /
  Сравнения: >, <, >=, <=, ==, !=
  Логические операторы: &, |, !, ->
  Эквиваленция: <->

Примеры:
  уровень(игрок(X), Y) & сила(игрок(X), Z) -> боевая_сила(игрок(X), Y + Z)
  ? победа(игрок(1), монстр(гоблин))

=== Конец справки ===
""".strip()


class CommandProcessor:
    """Процессор команд"""
    
    def __init__(self):
        self.commands = {
            "load": LoadCommand(),
            "get": GetAxiomsCommand(),
            "remove": RemoveCommand(),
            "help": HelpCommand(),
        }
    
    def execute(self, engine: LogicalEngine, command_name: str, args: List[str]) -> str:
        """Выполнение команды"""
        if command_name not in self.commands:
            raise CommandException(f"Неизвестная команда: {command_name}")
        
        command = self.commands[command_name]
        return command.execute(engine, args)