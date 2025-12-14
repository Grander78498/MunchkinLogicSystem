from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class LexerException(Exception):
    """Custom exception"""
    def __init__(self, message: str, position: Optional[int] = None):
        self.position = position
        if position is not None:
            super().__init__(f"Ошибка на позиции {position}: {message}")
        else:
            super().__init__(message)


class TokenType(str, Enum):
    IDENTIFIER = "identifier"
    EOL = ""
    
    # Логические операторы
    OR = "OR"           # | или +
    AND = "AND"         # & или *
    NOT = "NOT"         # !
    IMPLIES = "IMPLIES" # ->
    EQUIVALENCE = "EQUALS"  # <->
    
    # Скобки
    LPAREN = "LPAREN"   # (
    RPAREN = "RPAREN"   # )
    
    # Специальные
    QUESTION = "QUESTION"  # ?


@dataclass
class Token:
    type: TokenType
    value: Any
    position: int


class Lexer:
    def __init__(self):
        pass
    
    def advance(self, step: int = 1):
        self.current_pos += step
        if self.current_pos < len(self.text):
            self.current_char = self.text[self.current_pos]
        else:
            self.current_char = None
    
    def peek(self, offset=1):
        """Посмотреть на следующий символ без продвижения"""
        pos = self.current_pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return None
    
    def skip_multiline_comment(self):
        """Пропустить многострочный комментарий"""
        self.advance(2)  # Пропустить /*
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance(2)
                break
            self.advance()
    
    def tokenize_line(self, text: str):
        self.current_pos = 0
        self.text = text
        self.current_char = self.text[0] if text else None
        self.tokens = []
        
        while self.current_char is not None:
            self.token_pos = self.current_pos
            
            # Пропуск пробелов
            if self.current_char.isspace():
                self.advance()
                continue
            
            # Комментарии
            if self.current_char == '/' and self.peek() == '/':
                break  # Остаток строки - комментарий
            
            if self.current_char == '/' and self.peek() == '*':
                self.skip_multiline_comment()
                continue
            
            # Операторы из двух символов
            if self.current_char == '-' and self.peek() == '>':
                self.tokens.append(Token(TokenType.IMPLIES, '->', self.token_pos))
                self.advance(2)
                continue
            
            if self.current_char == '<' and self.peek() == '-' and self.peek(2) == '>':
                self.tokens.append(Token(TokenType.EQUIVALENCE, '<->', self.token_pos))
                self.advance(3)
                continue
            
            # Одиночные операторы
            if self.current_char in '&*':
                self.tokens.append(Token(TokenType.AND, self.current_char, self.token_pos))
                self.advance()
                continue
            
            if self.current_char in '|+':
                self.tokens.append(Token(TokenType.OR, self.current_char, self.token_pos))
                self.advance()
                continue
            
            if self.current_char == '!':
                self.tokens.append(Token(TokenType.NOT, '!', self.token_pos))
                self.advance()
                continue
            
            if self.current_char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.token_pos))
                self.advance()
                continue
            
            if self.current_char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.token_pos))
                self.advance()
                continue
            
            if self.current_char == '?':
                self.tokens.append(Token(TokenType.QUESTION, '?', self.token_pos))
                self.advance()
                continue
            
            # Строки в кавычках
            if self.current_char == '"':
                self.advance()
                self.parse_string()
                if self.current_char != '"':
                    raise LexerException("Незакрытая строка", self.token_pos)
                self.advance()
                continue
            
            # Идентификаторы
            if self.current_char.isalpha() or self.current_char == '_':
                self.parse_identifier()
                continue
            
            raise LexerException(f"Неожиданный символ: {self.current_char}", self.token_pos)
        
        self.tokens.append(Token(TokenType.EOL, None, self.current_pos))
        return self.tokens
    
    def parse_identifier(self, skip_spaces: bool = False):
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
    
    def parse_string(self):
        """Парсинг строки в кавычках"""
        self.current_value = []
        # Собираем все символы до закрывающей кавычки
        while self.current_char and self.current_char != '"':
            self.current_value.append(self.current_char)
            self.advance()
        
        # Создаем токен идентификатора из строки
        new_token = Token(
            type=TokenType.IDENTIFIER,
            value="".join(self.current_value),
            position=self.token_pos,
        )
        self.tokens.append(new_token)
