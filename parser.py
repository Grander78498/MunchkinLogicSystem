from typing import Optional
from lexer import Token, TokenType
from models import (
    Operation, Predicate, Variable,
    Conjunction, Disjunction, Negation,
    Implication, Equivalence
)


class ParserException(Exception):
    """Исключение парсера"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.token = token
        if token:
            super().__init__(
                f"Ошибка парсинга на позиции {token.position}: {message}"
            )
        else:
            super().__init__(message)


class Parser:
    """Синтаксический анализатор логических выражений"""
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Operation | Predicate:
        """Главный метод парсинга"""
        if not self.tokens or self.tokens[0].type == TokenType.EOL:
            raise ParserException("Пустое выражение")
        
        result = self.parse_equivalence()
        
        if not self.is_at_end():
            raise ParserException(
                f"Неожиданный токен: {self.peek().value}",
                self.peek()
            )
        
        return result
    
    def parse_equivalence(self) -> Operation | Predicate:
        """Парсинг эквиваленции (самый низкий приоритет)"""
        left = self.parse_implication()
        
        if self.match(TokenType.EQUIVALENCE):
            right = self.parse_implication()
            return Equivalence((left, right))
        
        return left
    
    def parse_implication(self) -> Operation | Predicate:
        """Парсинг импликации (правая ассоциативность)"""
        left = self.parse_disjunction()
        
        if self.match(TokenType.IMPLIES):
            right = self.parse_implication()  # Рекурсивный вызов для правой ассоциативности
            return Implication((left, right))
        
        return left
    
    def parse_disjunction(self) -> Operation | Predicate:
        """Парсинг дизъюнкции"""
        left = self.parse_conjunction()
        
        while self.match(TokenType.OR):
            right = self.parse_conjunction()
            left = Disjunction((left, right))
        
        return left
    
    def parse_conjunction(self) -> Operation | Predicate:
        """Парсинг конъюнкции"""
        left = self.parse_negation()
        
        while self.match(TokenType.AND):
            right = self.parse_negation()
            left = Conjunction((left, right))
        
        return left
    
    def parse_negation(self) -> Operation | Predicate:
        """Парсинг отрицания"""
        if self.match(TokenType.NOT):
            operand = self.parse_negation()
            return Negation(operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Operation | Predicate:
        """Парсинг базовых элементов"""
        # Скобки
        if self.match(TokenType.LPAREN):
            expr = self.parse_equivalence()
            if not self.match(TokenType.RPAREN):
                raise ParserException(
                    "Ожидалась закрывающая скобка",
                    self.peek()
                )
            return expr
        
        # Идентификатор
        if self.match(TokenType.IDENTIFIER):
            name = self.previous().value
            return Variable(name)
        
        raise ParserException(
            f"Неожиданный токен: {self.peek().value if not self.is_at_end() else 'конец выражения'}",
            self.peek() if not self.is_at_end() else None
        )
    
    # Вспомогательные методы
    
    def match(self, *types: TokenType) -> bool:
        """Проверить и продвинуться, если текущий токен соответствует типу"""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type: TokenType) -> bool:
        """Проверить тип текущего токена"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self) -> Token:
        """Продвинуться к следующему токену"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        """Проверить, достигнут ли конец"""
        return self.peek().type == TokenType.EOL
    
    def peek(self) -> Token:
        """Посмотреть текущий токен"""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Получить предыдущий токен"""
        return self.tokens[self.current - 1]