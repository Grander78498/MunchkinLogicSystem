import sys
from typing import List
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from ast_transformer import ASTTransformer, ASTTransformerException
from engine import LogicalEngine
from commands import CommandProcessor, CommandException
from models import Operation, Predicate


class REPLError(Exception):
    """Исключение REPL"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class REPL:
    """REPL-интерфейс для языка SHLDN"""
    
    def __init__(self):
        self.engine = LogicalEngine()
        self.command_processor = CommandProcessor()
        self.lexer = Lexer()
        self.parser = Parser([])
        self.transformer = ASTTransformer()
        
    def run(self):
        """Запуск REPL"""
        print("SHLDN Логический Интерпретатор")
        print("Введите 'help' для получения справки, 'quit' или 'exit' для выхода.")
        print()
        
        while True:
            try:
                # Получаем ввод от пользователя
                user_input = input("SHLDN> ").strip()
                
                # Проверяем команды выхода
                if user_input.lower() in ('quit', 'exit'):
                    print("До свидания!")
                    break
                
                # Пропускаем пустой ввод
                if not user_input:
                    continue
                
                # Обрабатываем ввод
                self.process_input(user_input)
                
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
            except EOFError:
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def process_input(self, user_input: str):
        """Обработка ввода пользователя"""
        try:
            # Токенизация
            tokens = self.lexer.tokenize(user_input)
            
            # Парсинг
            self.parser = Parser(tokens)
            ast_nodes = self.parser.parse()
            
            # Обработка каждого узла AST
            for node in ast_nodes:
                if node.__class__.__name__ == "CommandNode":
                    # Обработка команд
                    try:
                        result = self.command_processor.execute(
                            self.engine,
                            node.command,
                            node.args
                        )
                        print(result)
                    except CommandException as e:
                        print(f"Ошибка команды: {e}")
                    except Exception as e:
                        print(f"Неожиданная ошибка при выполнении команды: {e}")
                elif node.__class__.__name__ == "TheoremNode":
                    # Обработка теорем
                    try:
                        operation = self.transformer.transform(node)
                        print(f"Доказательство: {operation}")
                        self.engine.resolution_method_with_unification(operation)
                    except Exception as e:
                        print(f"Ошибка при доказательстве теоремы: {e}")
                elif node.__class__.__name__ == "AxiomNode":
                    # Обработка аксиом
                    try:
                        operation = self.transformer.transform(node)
                        added_axioms = self.engine.add_axiom(operation)
                        if added_axioms:
                            print(f"Аксиома добавлена. Номера новых дизъюнктов: {[len(self.engine.axioms) - len(added_axioms) + 1 + i for i in range(len(added_axioms))]}")
                        else:
                            print("Аксиома добавлена.")
                    except Exception as e:
                        print(f"Ошибка при добавлении аксиомы: {e}")
                else:
                    # Обработка других выражений (высказываний, предикатов и т.д.)
                    try:
                        operation = self.transformer.transform(node)
                        if isinstance(operation, (Operation, Predicate)):
                            added_axioms = self.engine.add_axiom(operation)
                            if added_axioms:
                                print(f"Выражение добавлено как аксиома. Номера новых дизъюнктов: {[len(self.engine.axioms) - len(added_axioms) + 1 + i for i in range(len(added_axioms))]}")
                            else:
                                print("Выражение добавлено как аксиома.")
                        else:
                            print(f"Результат: {operation}")
                    except Exception as e:
                        print(f"Ошибка при обработке выражения: {e}")
                        
        except LexerException as e:
            print(f"Ошибка лексического анализа: {e}")
        except ParserException as e:
            print(f"Ошибка синтаксического анализа: {e}")
        except ASTTransformerException as e:
            print(f"Ошибка преобразования AST: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка обработки ввода: {e}")


def main():
    """Основная функция"""
    repl = REPL()
    repl.run()


if __name__ == "__main__":
    main()