import os
import sys
from typing import Optional

from lexer import Lexer, LexerException
from parser import Parser, ParserException
from models import Operation, Predicate, Variable, Implication
from engine import LogicalEngine, Implication, Conjunction, Disjunction
from knowledge_base import KnowledgeBase


class REPL:
    """Read-Eval-Print Loop для логического языка"""
    
    def __init__(self):
        self.kb = KnowledgeBase()
        self.engine = LogicalEngine(self.kb)
        self.lexer = Lexer()
        self.parser = Parser([])
        self.running = True
    
    def run(self):
        """Запустить REPL"""
        self.print_welcome()
        
        while self.running:
            try:
                line = input(">>> ").strip()
                if not line:
                    continue
                
                self.process_line(line)
                
            except KeyboardInterrupt:
                print("\n⚠ Прервано. Используйте 'exit' для выхода")
            except LexerException as e:
                print(f"✗ Ошибка лексера: {e}")
            except ParserException as e:
                print(f"✗ Ошибка парсера: {e}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
    
    def print_welcome(self):
        """Вывести приветствие"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║              ЛОГИЧЕСКИЙ ЯЗЫК ПРОГРАММИРОВАНИЯ                    ║
║                                                                  ║
║  Введите 'help' для получения справки по синтаксису и командам   ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def process_line(self, line: str):
        """Обработать строку ввода"""
        # Пропустить комментарии
        if line.startswith("//"):
            return
        
        # Обработать команды
        if line.startswith("help"):
            self.cmd_help()
        elif line.startswith("load "):
            self.cmd_load(line[5:].strip())
        elif line.startswith("get"):
            self.cmd_get()
        elif line.startswith("remove "):
            self.cmd_remove(line[7:].strip())
        elif line.startswith("clear"):
            self.cmd_clear()
        elif line.startswith("exit") or line.startswith("quit"):
            self.cmd_exit()
        elif line.startswith("?"):
            # Теорема
            self.process_theorem(line[1:].strip())
        else:
            # Высказывание или аксиома
            self.process_statement_or_axiom(line)
    
    def cmd_help(self):
        """Вывести справку"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║              СПРАВКА ПО ЛОГИЧЕСКОМУ ЯЗЫКУ                        ║
╚══════════════════════════════════════════════════════════════════╝

СИНТАКСИС:
  Операторы:
    &  или  *     - конъюнкция (И)
    |  или  +     - дизъюнкция (ИЛИ)
    !             - отрицание (НЕ)
    ->            - импликация (ЕСЛИ...ТО)
    <->           - эквиваленция (ТОГДА И ТОЛЬКО ТОГДА)
    ()            - скобки для группировки
    
  Идентификаторы:
    - Могут содержать буквы, цифры и подчёркивания
    - Примеры: игрок_1, монстр_дракон, уровень_10
    
  Строки в кавычках:
    - Для идентификаторов с пробелами
    - Пример: "игрок 2 имеет уровень 1"

КОМАНДЫ:
  help                    - показать эту справку
  get                     - показать все высказывания и аксиомы
  remove <id>             - удалить аксиому по ID
  load <файл>             - загрузить файл с высказываниями и аксиомами
  clear                   - очистить базу знаний
  exit / quit             - выйти из программы

ИСПОЛЬЗОВАНИЕ:
  1. Добавление высказывания (элемента алфавита):
     >>> игрок_1
     >>> монстр_дракон
     >>> "игрок имеет уровень 10"
  
  2. Добавление аксиомы (должна содержать ->):
     >>> игрок_1_уровень_10 -> игрок_1_победитель
     >>> a & b -> c
     >>> !x | y -> z
  
  3. Проверка теоремы (начинается с ?):
     >>> ? игрок_1_победитель
     >>> ? a -> c

ПРИМЕРЫ:
  >>> игрок_1
  Добавлено высказывание: игрок_1
  
  >>> игрок_1_уровень_10 -> игрок_1_победитель
  Добавлена аксиома (1): игрок_1_уровень_10 -> игрок_1_победитель
  
  >>> ? игрок_1_победитель
  Проверка теоремы: игрок_1_победитель
  [вывод процесса доказательства]

КОММЕНТАРИИ:
  // однострочный комментарий
  /* многострочный
     комментарий */

ПРАВИЛА ВЫВОДА:
  Реализовано правило резолюций для доказательства теорем.
  Программа автоматически преобразует выражения в КНФ и применяет
  метод резолюций для поиска противоречия.

ЗАКОНЫ БУЛЕВОЙ АЛГЕБРЫ:
  - Устранение эквиваленций: A <-> B ≡ (A -> B) & (B -> A)
  - Устранение импликаций: A -> B ≡ !A | B
  - Законы де Моргана: !(A & B) ≡ !A | !B, !(A | B) ≡ !A & !B
  - Двойное отрицание: !!A ≡ A
  - Дистрибутивность: A | (B & C) ≡ (A | B) & (A | C)
        """)
    
    def cmd_get(self):
        """Показать все высказывания и аксиомы"""
        print("\n" + "="*70)
        print("БАЗА ЗНАНИЙ")
        print("="*70)
        
        # Высказывания
        statements = self.kb.get_all_statements()
        if statements:
            print("\nВЫСКАЗЫВАНИЯ (Алфавит A):")
            for stmt in statements:
                desc = f" - {stmt.description}" if stmt.description else ""
                print(f"  {stmt}{desc}")
        else:
            print("\nВЫСКАЗЫВАНИЯ: нет")
        
        # Аксиомы
        axioms = self.kb.get_all_axioms()
        if axioms:
            print("\nАКСИОМЫ (Ak - дизъюнкты Хорна):")
            for axiom in axioms:
                desc = f" - {axiom.description}" if axiom.description else ""
                print(f"  {axiom}{desc}")
        else:
            print("\nАКСИОМЫ: нет")
        
        print("="*70 + "\n")
    
    def cmd_remove(self, arg: str):
        """Удалить аксиому по ID"""
        try:
            axiom_id = int(arg)
            if self.kb.remove_axiom(axiom_id):
                print(f"✓ Аксиома ({axiom_id}) удалена")
                # Перезагрузить аксиомы в движок
                self.engine.load_axioms_from_kb()
            else:
                print(f"✗ Аксиома с ID {axiom_id} не найдена")
        except ValueError:
            print("✗ Ошибка: ID должен быть числом")
    
    def cmd_load(self, filename: str):
        """Загрузить файл"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Загрузка файла: {filename}")
            
            in_multiline_comment = False
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Обработка многострочных комментариев
                if "/*" in line:
                    in_multiline_comment = True
                if "*/" in line:
                    in_multiline_comment = False
                    continue
                if in_multiline_comment:
                    continue
                
                # Пропустить пустые строки и комментарии
                if not line or line.startswith("//"):
                    continue
                
                try:
                    self.process_line(line)
                except Exception as e:
                    print(f"  Строка {line_num}: Ошибка - {e}")
            
            print(f"✓ Файл загружен")
            
        except FileNotFoundError:
            print(f"✗ Файл не найден: {filename}")
        except Exception as e:
            print(f"✗ Ошибка при загрузке файла: {e}")
    
    def cmd_clear(self):
        """Очистить базу знаний"""
        self.kb.clear()
        self.engine.axioms.clear()
        print("✓ База знаний очищена")
    
    def cmd_exit(self):
        """Выйти из программы"""
        print("До свидания!")
        self.running = False
    
    def process_statement_or_axiom(self, line: str):
        """Обработать высказывание или аксиому"""
        try:
            # Токенизация
            tokens = self.lexer.tokenize_line(line)
            
            # Парсинг
            self.parser.tokens = tokens
            self.parser.current = 0
            expression = self.parser.parse()
            
            # Определить, это высказывание или аксиома
            if self.is_axiom(expression):
                # Это аксиома (содержит ->)
                axiom = self.kb.add_axiom(expression)
                print(f"✓ Добавлена аксиома ({axiom.id}): {axiom.expression}")
                
                # Добавить в движок
                self.engine.add_axiom(expression)
            else:
                # Это высказывание
                if isinstance(expression, Variable):
                    stmt = self.kb.add_statement(expression.name)
                    print(f"✓ Добавлено высказывание [{stmt.id}]: {stmt.name}")
                    # Также добавляем высказывание в движок как аксиому
                    self.engine.add_axiom(expression)
                else:
                    print("✗ Высказывание должно быть простым идентификатором")
        
        except LexerException as e:
            print(f"✗ Ошибка лексера: {e}")
        except ParserException as e:
            print(f"✗ Ошибка парсера: {e}")
        except Exception as e:
            print(f"✗ Ошибка: {e}")
    
    def is_axiom(self, expression: Operation | Predicate) -> bool:
        """Проверить, является ли выражение аксиомой"""
        # Аксиома должна содержать импликацию на верхнем уровне
        # или быть сложным выражением
        return isinstance(expression, (Implication, Conjunction, Disjunction))
    
    def process_theorem(self, line: str):
        """Проверить теорему"""
        try:
            print(f"\n{'='*70}")
            print(f"ПРОВЕРКА ТЕОРЕМЫ: {line}")
            print(f"{'='*70}\n")
            
            # Токенизация и парсинг
            tokens = self.lexer.tokenize_line(line)
            self.parser.tokens = tokens
            self.parser.current = 0
            expression = self.parser.parse()
            
            # Загрузить аксиомы из базы знаний
            self.engine.load_axioms_from_kb()
            
            # Применить метод резолюций
            print("Аксиомы в базе знаний:")
            self.engine.resolution_method(expression)
            
            print(f"\n{'='*70}\n")
            
        except LexerException as e:
            print(f"✗ Ошибка лексера: {e}")
        except ParserException as e:
            print(f"✗ Ошибка парсера: {e}")
        except Exception as e:
            print(f"✗ Ошибка: {e}")


def main():
    """Точка входа в REPL"""
    repl = REPL()
    repl.run()


if __name__ == "__main__":
    main()