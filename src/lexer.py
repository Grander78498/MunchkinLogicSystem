from enum import Enum


class LexerException(Exception):
    def __init__(self, message: str, position: int | None = None, line: int | None = None, column: int | None = None):
        self.message = message
        self.position = position
        self.line = line
        self.column = column
        super().__init__(self.message)
    
    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"{self.message} (line {self.line}, column {self.column})"
        elif self.position is not None:
            return f"{self.message} (position {self.position})"
        return self.message


class TokenType(Enum):
    # Логические операторы
    AND = "AND"                    # &
    OR = "OR"                      # |
    NOT = "NOT"                    # !
    IMPLIES = "IMPLIES"            # -->
    EQUIVALENCE = "EQUIVALENCE"    # ==
    
    # Разделители
    DOT = "DOT"                    # . (конец высказывания/аксиомы)
    QUERY = "QUERY"                # ? (теорема)
    
    # Скобки
    LPAREN = "LPAREN"              # (
    RPAREN = "RPAREN"              # )
    
    # Идентификаторы и литералы
    IDENTIFIER = "IDENTIFIER"      # атом (идентификатор)
    STRING = "STRING"              # строковый литерал в двойных кавычках
    
    # Команды
    LOAD = "LOAD"                  # загрузить файл
    GET = "GET"                    # вывести аксиомы
    REMOVE = "REMOVE"              # удалить аксиому
    DUMP = "DUMP"                  # выгрузить базу знаний в файл
    
    # Числа (для команды remove)
    NUMBER = "NUMBER"              # числовой литерал
    
    # EOF
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, value: str, position: int, line: int = 1, column: int = 1):
        self.type = type
        self.value = value
        self.position = position
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', pos={self.position}, line={self.line}, col={self.column})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


class Lexer:
    def __init__(self, text: str | None = None):
        self.text = text
        self.current_position = 0
        self.current_line = 1
        self.current_column = 1
        self.tokens = []
        
        # Ключевые слова
        self.keywords = {
            'load': TokenType.LOAD,
            'get': TokenType.GET,
            'remove': TokenType.REMOVE,
            'dump': TokenType.DUMP, 
        }
    
    def current_char(self) -> str | None:
        """Возвращает текущий символ или None если достигнут конец"""
        if self.text is None or self.current_position >= len(self.text):
            return None
        return self.text[self.current_position]
    
    def peek_char(self, offset: int = 1) -> str | None:
        """Заглядывает вперед на offset символов"""
        if self.text is None:
            return None
        pos = self.current_position + offset
        if pos >= len(self.text):
            return None
        return self.text[pos]
    
    def advance(self) -> str | None:
        """Переходит к следующему символу"""
        if self.text is None or self.current_position >= len(self.text):
            return None
        
        char = self.text[self.current_position]
        self.current_position += 1
        
        # Отслеживаем позицию для отладки
        if char == '\n':
            self.current_line += 1
            self.current_column = 1
        else:
            self.current_column += 1
        
        return char
    
    def skip_whitespace(self):
        """Пропускает пробельные символы"""
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def skip_comment(self):
        """Пропускает комментарии (// однострочные или /* */ многострочные)"""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Однострочный комментарий
            self.advance()  # /
            self.advance()  # /
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Многострочный комментарий
            self.advance()  # /
            self.advance()  # *
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                self.advance()
            else:
                # Если вышли из цикла, значит EOF
                raise LexerException("Незакрытый многострочный комментарий", 
                                    self.current_position, 
                                    self.current_line, 
                                    self.current_column)
    
    def read_number(self) -> str:
        """Читает числовой литерал"""
        result = ""
        while self.current_char() and self.current_char().isdigit():
            result += self.current_char()
            self.advance()
        return result
    
    def read_string(self) -> str:
        """Читает строковый литерал в двойных кавычках"""
        if self.current_char() != '"':
            raise LexerException("Ожидалась двойная кавычка", 
                               self.current_position, 
                               self.current_line, 
                               self.current_column)
        
        self.advance()  # Пропускаем открывающую кавычку
        result = ""
        
        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()
                # Обработка escape-последовательностей
                if self.current_char() == 'n':
                    result += '\n'
                elif self.current_char() == 't':
                    result += '\t'
                elif self.current_char() == '\\':
                    result += '\\'
                elif self.current_char() == '"':
                    result += '"'
                else:
                    result += '\\' + (self.current_char() or '')
            else:
                result += self.current_char()
            self.advance()
        
        if self.current_char() != '"':
            raise LexerException("Незакрытая строка", 
                               self.current_position, 
                               self.current_line, 
                               self.current_column)
        
        self.advance()  # Пропускаем закрывающую кавычку
        return result
    
    def read_identifier(self) -> str:
        """Читает идентификатор (атом)"""
        result = ""
        # Идентификатор начинается с буквы или подчеркивания, может содержать буквы, цифры, подчеркивания
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            result += self.current_char()
            self.advance()
        return result
    
    def tokenize(self) -> list[Token]:
        """Основной метод токенизации"""
        if self.text is None:
            return []
        
        if len(self.text) == 0:
            self.tokens.append(Token(TokenType.EOF, '', 0, 1, 1))
            return self.tokens
        
        self.current_position = 0
        self.current_line = 1
        self.current_column = 1
        self.tokens = []
        
        while self.current_position < len(self.text):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            start_position = self.current_position
            start_line = self.current_line
            start_column = self.current_column
            
            char = self.current_char()
            
            # Комментарии
            if char == '/' and (self.peek_char() == '/' or self.peek_char() == '*'):
                try:
                    self.skip_comment()
                except LexerException as e:
                    raise e
                continue
            
            # Строковые литералы
            if char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, start_position, start_line, start_column))
                continue
            
            # Числовые литералы
            if char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, start_position, start_line, start_column))
                continue
            
            # Идентификаторы
            if char.isalpha() or char == '_':
                value = self.read_identifier()
                # Проверяем, является ли это ключевым словом
                token_type = self.keywords.get(value.lower())
                if token_type:
                    self.tokens.append(Token(token_type, value, start_position, start_line, start_column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, value, start_position, start_line, start_column))
                continue
            
            # Операторы и символы
            if char == '&':
                self.advance()
                self.tokens.append(Token(TokenType.AND, '&', start_position, start_line, start_column))
            elif char == '|':
                self.advance()
                self.tokens.append(Token(TokenType.OR, '|', start_position, start_line, start_column))
            elif char == '!':
                self.advance()
                self.tokens.append(Token(TokenType.NOT, '!', start_position, start_line, start_column))
            elif char == '-':
                if self.peek_char() == '-' and self.peek_char(2) == '>':
                    self.advance()  # -
                    self.advance()  # -
                    self.advance()  # >
                    self.tokens.append(Token(TokenType.IMPLIES, '-->', start_position, start_line, start_column))
                else:
                    raise LexerException(f"Неожиданный символ: '{char}'", 
                                       start_position, 
                                       start_line, 
                                       start_column)
            elif char == '=':
                if self.peek_char() == '=':
                    self.advance()  # =
                    self.advance()  # =
                    self.tokens.append(Token(TokenType.EQUIVALENCE, '==', start_position, start_line, start_column))
                else:
                    raise LexerException(f"Неожиданный символ: '{char}'", 
                                       start_position, 
                                       start_line, 
                                       start_column)
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_position, start_line, start_column))
            elif char == '?':
                self.advance()
                self.tokens.append(Token(TokenType.QUERY, '?', start_position, start_line, start_column))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_position, start_line, start_column))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_position, start_line, start_column))
            else:
                raise LexerException(f"Неожиданный символ: '{char}'", 
                                   start_position, 
                                   start_line, 
                                   start_column)
        
        # Добавляем EOF токен
        self.tokens.append(Token(TokenType.EOF, '', len(self.text), self.current_line, self.current_column))
        
        return self.tokens
