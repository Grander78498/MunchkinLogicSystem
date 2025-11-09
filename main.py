import logging
import os
import re
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from engine import LogicalEngine, Variable, Implication


class SheldonConsole:
    def __init__(self):
        self.engine = LogicalEngine(level=logging.WARNING)
        self.axioms: list[Implication] = []
        self.facts: list[Variable] = []
        self.running = True
    
    def run(self):
        """Запускает интерактивный режим"""
        print("Sheldon Logic Language - Интерактивный режим")
        print("Введите 'help' для справки или 'exit' для выхода")
        print()
        
        while self.running:
            try:
                line = input("sheldon> ").strip()
                
                if not line:
                    continue
                
                if line.lower() == 'exit' or line.lower() == 'quit':
                    self.running = False
                    print("До свидания!")
                    break
                
                if line.lower() == 'help':
                    self.show_help()
                    continue
                
                self.process_line(line)
                
            except KeyboardInterrupt:
                print("\nДо свидания!")
                self.running = False
                break
            except EOFError:
                print("\nДо свидания!")
                self.running = False
                break
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def show_help(self):
        """Показывает справку"""
        print("""
Доступные команды:
  help              - показать эту справку
  exit/quit         - выйти из программы
  load <file>       - загрузить файл .shldn
  get axioms        - показать все аксиомы
  remove <number>   - удалить аксиому по номеру
  
Примеры запросов:
  монстр_дракон.                    - добавить факт
  игрок_1_уровень_10 --> игрок_1_победитель.  - добавить аксиому
  игрок_1_победитель?               - проверить теорему
        """)
    
    def process_line(self, line: str):
        """Обрабатывает одну строку ввода"""
        try:
            # Проверяем, является ли это командой
            parts = line.strip().lower().split()
            if parts and parts[0] in ['load', 'get', 'remove']:
                self.handle_command(line)
                return
            
            # Парсим как выражение
            lexer = Lexer(line)
            parser = Parser(lexer)
            statements = parser.parse()
            
            for statement in statements:
                if statement is None:
                    # Это команда, обрабатываем её
                    self.handle_command(line)
                elif isinstance(statement, Variable):
                    # Это факт или теорема
                    if self.is_theorem(line):
                        result = self.check_theorem(statement)
                        print(f"{'Теорема верна' if result else 'Теорема неверна'}")
                    else:
                        self.facts.append(statement)
                        print(f"Факт добавлен: {statement.value}")
                elif isinstance(statement, Implication):
                    # Это аксиома
                    self.axioms.append(statement)
                    print(f"Аксиома добавлена (#{len(self.axioms)})")
                else:
                    print(f"Выражение обработано: {statement}")
        
        except LexerException as e:
            print(f"Ошибка лексера: {e}")
        except ParserException as e:
            print(f"Ошибка парсера: {e}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def is_theorem(self, line: str) -> bool:
        """Проверяет, является ли строка теоремой (заканчивается на ?)"""
        return line.strip().endswith('?')
    
    def handle_command(self, line: str):
        """Обрабатывает команды (load, get axioms, remove)"""
        try:
            lexer = Lexer(line)
            parser = Parser(lexer)
            statements = parser.parse()
            
            # Если парсер вернул None, значит это команда
            if statements and all(s is None for s in statements):
                # Парсим команду вручную
                parts = line.strip().lower().split()
                
                if len(parts) == 0:
                    return
                
                if parts[0] == 'load':
                    # Команда load обрабатывается через парсер
                    # Но нам нужно извлечь имя файла
                    match = re.match(r'load\s+(\S+)', line, re.IGNORECASE)
                    if match:
                        filename = match.group(1).rstrip('.')
                        if not filename.endswith('.shldn'):
                            filename += '.shldn'
                        self.load_file(filename)
                    else:
                        print("Ошибка: укажите имя файла")
                
                elif parts[0] == 'get' and len(parts) > 1 and parts[1] == 'axioms':
                    self.show_axioms()
                
                elif parts[0] == 'remove':
                    # Команда remove обрабатывается через парсер
                    # Но нам нужно извлечь номер
                    match = re.match(r'remove\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        axiom_number = int(match.group(1))
                        self.remove_axiom(axiom_number)
                    else:
                        print("Ошибка: укажите номер аксиомы")
        except Exception as e:
            print(f"Ошибка при обработке команды: {e}")
    
    def load_file(self, filename: str):
        """Загружает файл .shldn"""
        if not os.path.exists(filename):
            print(f"Ошибка: файл '{filename}' не найден")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lexer = Lexer(content)
            parser = Parser(lexer)
            statements = parser.parse()
            
            loaded_facts = 0
            loaded_axioms = 0
            
            for statement in statements:
                if statement is None:
                    # Команда, пропускаем
                    continue
                elif isinstance(statement, Variable):
                    if not self.is_theorem_in_content(content, statement):
                        self.facts.append(statement)
                        loaded_facts += 1
                elif isinstance(statement, Implication):
                    self.axioms.append(statement)
                    loaded_axioms += 1
            
            print(f"Файл '{filename}' загружен: {loaded_facts} фактов, {loaded_axioms} аксиом")
        
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
    
    def is_theorem_in_content(self, content: str, statement: Variable) -> bool:
        """Проверяет, является ли statement теоремой в контексте content"""
        # Упрощенная проверка: если в строке есть запрос с этим значением
        lines = content.split('\n')
        for line in lines:
            if line.strip().endswith('?') and statement.value in line:
                return True
        return False
    
    def show_axioms(self):
        """Показывает все аксиомы"""
        if not self.axioms:
            print("Аксиом нет")
            return
        
        print(f"Всего аксиом: {len(self.axioms)}")
        for i, axiom in enumerate(self.axioms, 1):
            print(f"{i}. {axiom}")
    
    def remove_axiom(self, axiom_number: int):
        """Удаляет аксиому по номеру"""
        if axiom_number < 1 or axiom_number > len(self.axioms):
            print(f"Ошибка: аксиома с номером {axiom_number} не существует")
            return
        
        removed = self.axioms.pop(axiom_number - 1)
        print(f"Аксиома удалена: {removed}")
    
    def check_theorem(self, theorem: Variable) -> bool:
        """Проверяет теорему (упрощенная версия - проверяет только факты)"""
        # Проверяем, есть ли факт с таким значением
        for fact in self.facts:
            if fact.value == theorem.value:
                return True
        
        # Проверяем, можно ли вывести теорему из аксиом
        # Это упрощенная версия - в реальности нужен алгоритм резолюции
        return False


def main():
    console = SheldonConsole()
    console.run()


if __name__ == '__main__':
    main()
