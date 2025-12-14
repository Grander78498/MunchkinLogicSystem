from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class LexerException(Exception):
    """Custom exception for lexer errors"""
    def __init__(self, message: str, line: int = None, column: int = None, position: int = None):
        self.message = message
        self.line = line
        self.column = column
        self.position = position
        if line is not None and column is not None:
            super().__init__(f"{message} (line {line}, column {column})")
        else:
            super().__init__(message)


class TokenType(str, Enum):
    # Идентификаторы и литералы
    IDENTIFIER = "identifier"      # игрок_1, монстр
    VARIABLE = "variable"          # X, Y, Z (начинаются с большой буквы)
    STRING = "string"              # "текст в кавычках"
    NUMBER = "number"              # 1, 2, 3.14
    
    # Логические операторы
    AND = "AND"                    # & или *
    OR = "OR"                      # | или +
    NOT = "NOT"                    # !
    IMPLIES = "IMPLIES"            # ->
    EQUIVALENCE = "EQUIVALENCE"    # == или <->
    
    # Арифметические операторы
    PLUS = "PLUS"                  # +
    MINUS = "MINUS"                # -
    MULTIPLY = "MULTIPLY"          # *
    DIVIDE = "DIVIDE"              # /
    
    # Операторы сравнения
    GT = "GT"                      # >
    LT = "LT"                      # <
    GTE = "GTE"                    # >=
    LTE = "LTE"                    # <=
    EQ = "EQ"                      # ==
    NEQ = "NEQ"                    # !=
    
    # Разделители и специальные символы
    LPAREN = "LPAREN"              # (
    RPAREN = "RPAREN"              # )
    COMMA = "COMMA"                # ,
    QUESTION = "QUESTION"          # ?
    
    # Команды
    COMMAND = "COMMAND"            # load, get, remove, help
    
    # Служебные
    COMMENT = "COMMENT"            # комментарии
    EOL = "EOL"                    # конец строки
    EOF = "EOF"                    # конец файла


@dataclass
class Token:
    type: TokenType
    value: Any
    position: int


class Lexer:
    def __init__(self):
        # Определение ключевых слов команд
        self.commands = {"load", "get", "remove", "help"}
        
        # Определение однострочных операторов
        self.single_char_operators = {
            '&': TokenType.AND,
            '|': TokenType.OR,
            '!': TokenType.NOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            ',': TokenType.COMMA,
            '?': TokenType.QUESTION,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '<': TokenType.LT,
            '>': TokenType.GT,
        }
        
        # Определение многосимвольных операторов (в порядке убывания длины)
        self.multi_char_operators = {
            '->': TokenType.IMPLIES,
            '<->': TokenType.EQUIVALENCE,
            '>=': TokenType.GTE,
            '<=': TokenType.LTE,
            '==': TokenType.EQ,
            '!=': TokenType.NEQ,
        }

    def tokenize(self, text: str) -> list[Token]:
        """Токенизация всего текста"""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        tokens = []
        
        while self.pos < len(self.text):
            # Пропуск пробелов
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Комментарии
            if self.peek_ahead(2) == '//':
                self.skip_line_comment()
                continue
            if self.peek_ahead(2) == '/*':
                self.skip_block_comment()
                continue
            
            # Числа
            if self.current_char.isdigit():
                tokens.append(self.parse_number())
                continue
            
            # Строки
            if self.current_char == '"':
                tokens.append(self.parse_string())
                continue
            
            # Идентификаторы и переменные
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.parse_identifier_or_variable())
                continue
            
            # Операторы и специальные символы
            token = self.parse_operator()
            if token:
                tokens.append(token)
                continue
            
            # Неизвестный символ
            raise LexerException(
                f"Неожиданный символ: {self.current_char}",
                self.line,
                self.column,
                self.pos
            )
        
        tokens.append(Token(TokenType.EOF, None, self.pos))
        return tokens

    @property
    def current_char(self) -> Optional[str]:
        """Текущий символ"""
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def peek_ahead(self, n: int) -> str:
        """Просмотр следующих n символов"""
        end = min(self.pos + n, len(self.text))
        return self.text[self.pos:end]

    def advance(self, step: int = 1):
        """Переход к следующему символу"""
        for _ in range(step):
            if self.pos < len(self.text):
                if self.text[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def skip_whitespace(self):
        """Пропуск пробельных символов"""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_line_comment(self):
        """Пропуск однострочного комментария"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        # Пропускаем //
        self.advance(2)
        
        # Пропускаем до конца строки
        while self.current_char and self.current_char != '\n':
            self.advance()
        
        # Создаем токен комментария
        comment_text = self.text[start_pos:self.pos]
        token = Token(TokenType.COMMENT, comment_text, start_pos)
        return token

    def skip_block_comment(self):
        """Пропуск блочного комментария"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        # Пропускаем /*
        self.advance(2)
        
        # Ищем */
        while self.current_char:
            if self.peek_ahead(2) == '*/':
                self.advance(2)
                break
            self.advance()
        else:
            raise LexerException(
                "Незакрытый блочный комментарий",
                start_line,
                start_column,
                start_pos
            )
        
        # Создаем токен комментария
        comment_text = self.text[start_pos:self.pos]
        token = Token(TokenType.COMMENT, comment_text, start_pos)
        return token

    def parse_number(self) -> Token:
        """Парсинг числа"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        # Целая часть
        while self.current_char and self.current_char.isdigit():
            self.advance()
        
        # Дробная часть
        if self.current_char == '.' and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
            self.advance()  # точка
            while self.current_char and self.current_char.isdigit():
                self.advance()
        
        number_str = self.text[start_pos:self.pos]
        try:
            if '.' in number_str:
                value = float(number_str)
            else:
                value = int(number_str)
        except ValueError:
            raise LexerException(
                f"Некорректное число: {number_str}",
                start_line,
                start_column,
                start_pos
            )
        
        return Token(TokenType.NUMBER, value, start_pos)

    def parse_string(self) -> Token:
        """Парсинг строки в кавычках"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        # Пропускаем открывающую кавычку
        self.advance()
        
        string_chars = []
        while self.current_char and self.current_char != '"':
            if self.current_char == '\n':
                raise LexerException(
                    "Незакрытая строка",
                    start_line,
                    start_column,
                    start_pos
                )
            string_chars.append(self.current_char)
            self.advance()
        
        if not self.current_char:
            raise LexerException(
                "Незакрытая строка",
                start_line,
                start_column,
                start_pos
            )
        
        # Пропускаем закрывающую кавычку
        self.advance()
        
        value = "".join(string_chars)
        return Token(TokenType.STRING, value, start_pos)

    def parse_identifier_or_variable(self) -> Token:
        """Парсинг идентификатора или переменной"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        chars = []
        while self.current_char and (self.current_char.isalnum() or self.current_char in '_.'):
            chars.append(self.current_char)
            self.advance()
        
        identifier = "".join(chars)
        
        # Проверяем, является ли это командой
        if identifier in self.commands:
            return Token(TokenType.COMMAND, identifier, start_pos)
        
        # Проверяем, является ли это переменной (начинается с большой буквы)
        if identifier[0].isupper():
            return Token(TokenType.VARIABLE, identifier, start_pos)
        else:
            return Token(TokenType.IDENTIFIER, identifier, start_pos)

    def parse_operator(self) -> Optional[Token]:
        """Парсинг оператора"""
        start_pos = self.pos
        start_line = self.line
        start_column = self.column
        
        # Проверяем многосимвольные операторы (в порядке убывания длины)
        for op in self.multi_char_operators:
            if self.peek_ahead(len(op)) == op:
                token_type = self.multi_char_operators[op]
                self.advance(len(op))
                return Token(token_type, op, start_pos)
        
        # Проверяем односимвольные операторы
        if self.current_char in self.single_char_operators:
            token_type = self.single_char_operators[self.current_char]
            op = self.current_char
            self.advance()
            return Token(token_type, op, start_pos)
        
        return None

    def tokenize_line(self, text: str):
        """Совместимость с предыдущей версией - токенизация одной строки"""
        self.current_pos = 0
        self.text = text
        if self.text:
            self.current_char = self.text[0]
        else:
            self.current_char = None
        self.tokens = []

        while self.current_char is not None:
            self.token_pos = self.current_pos
            if self.current_char.isalpha():
                self.parse_identifier()
            elif self.current_char == '"':
                self.advance()
                self.parse_identifier(skip_spaces=True)
                if self.current_char != '"':
                    raise LexerException("Незакрытая строка")
            elif self.current_char == ".":
                self.tokens.append(
                    Token(
                        type=TokenType.DOT,
                        value=self.current_char,
                        position=self.token_pos,
                    )
                )
                self.advance()

        eol_token = Token(type=TokenType.EOL, value=None, position=self.current_pos)
        self.tokens.append(eol_token)
        return self.tokens

    def parse_identifier(self, skip_spaces: bool = False):
        """Совместимость с предыдущей версией"""
        self.current_value = []
        while self.current_char and (
            skip_spaces or self.current_char.isalnum() or self.current_char == "_"
        ):
            self.current_value.append(self.current_char)
            self.advance()

        new_token = Token(
            type=TokenType.IDENTIFIER,
            value="".join(self.current_value),
            position=self.token_pos,
        )
        self.tokens.append(new_token)
