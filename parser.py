from dataclasses import dataclass
from typing import Optional, Union, List
from lexer import Token, TokenType, Lexer


class ParserException(Exception):
    """Исключение парсера"""
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"[позиция {token.position}] {message}")
        else:
            super().__init__(message)


@dataclass
class ASTNode:
    """Базовый класс для узлов AST"""
    position: int


@dataclass
class PropositionNode(ASTNode):
    """Высказывание"""
    position: int
    name: str


@dataclass
class PredicateNode(ASTNode):
    """Предикат с аргументами"""
    position: int
    name: str
    args: List[ASTNode]


@dataclass
class VariableNode(ASTNode):
    """Переменная (терм)"""
    position: int
    name: str


@dataclass
class NumberNode(ASTNode):
    """Числовой литерал"""
    position: int
    value: Union[int, float]


@dataclass
class StringNode(ASTNode):
    """Строковый литерал"""
    position: int
    value: str


@dataclass
class BinaryOpNode(ASTNode):
    """Бинарная операция"""
    position: int
    op: str
    left: ASTNode
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    """Унарная операция"""
    position: int
    op: str
    operand: ASTNode


@dataclass
class AxiomNode(ASTNode):
    """Аксиома (импликация)"""
    position: int
    condition: ASTNode
    consequence: ASTNode


@dataclass
class TheoremNode(ASTNode):
    """Теорема (запрос)"""
    position: int
    expression: ASTNode


@dataclass
class CommandNode(ASTNode):
    """Команда"""
    position: int
    command: str
    args: List[str]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def advance(self):
        """Переход к следующему токену"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def expect(self, token_type: TokenType) -> Token:
        """Проверка типа текущего токена"""
        if not self.current_token:
            raise ParserException(f"Ожидался {token_type}, но достигнут конец файла")
        
        if self.current_token.type != token_type:
            raise ParserException(
                f"Ожидался {token_type}, получен {self.current_token.type}",
                self.current_token
            )
        token = self.current_token
        self.advance()
        return token

    def peek(self, token_type: TokenType) -> bool:
        """Проверка типа следующего токена без продвижения"""
        return self.current_token and self.current_token.type == token_type

    def parse(self) -> List[ASTNode]:
        """Парсинг программы"""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Пропуск комментариев
            if self.current_token.type == TokenType.COMMENT:
                self.advance()
                continue
            
            # Пропуск EOL
            if self.current_token.type == TokenType.EOL:
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_statement(self) -> Optional[ASTNode]:
        """Парсинг одного выражения"""
        if not self.current_token:
            return None

        # Теорема
        if self.current_token.type == TokenType.QUESTION:
            return self.parse_theorem()
        
        # Команда
        if self.current_token.type == TokenType.COMMAND:
            return self.parse_command()
        
        # Сохраняем позицию для возможной аксиомы
        start_pos = self.pos
        
        # Выражение (может быть аксиомой или высказыванием)
        expr = self.parse_expression()
        
        # Проверка на аксиому (содержит -> на верхнем уровне)
        if isinstance(expr, BinaryOpNode) and expr.op == "->":
            # Это аксиома
            return AxiomNode(expr.position, expr.left, expr.right)
        
        return expr

    def parse_theorem(self) -> TheoremNode:
        """Парсинг теоремы"""
        token = self.expect(TokenType.QUESTION)
        expression = self.parse_expression()
        return TheoremNode(token.position, expression)

    def parse_command(self) -> CommandNode:
        """Парсинг команды"""
        token = self.expect(TokenType.COMMAND)
        command = token.value
        args = []
        
        # Собираем аргументы команды до точки
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type in (TokenType.STRING, TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.VARIABLE):
                args.append(str(self.current_token.value))
                self.advance()
            else:
                raise ParserException(
                    f"Недопустимый аргумент команды: {self.current_token.type}",
                    self.current_token
                )
        
        return CommandNode(token.position, command, args)

    def parse_expression(self) -> ASTNode:
        """Парсинг выражения (точка входа для выражений)"""
        return self.parse_equivalence()

    def parse_equivalence(self) -> ASTNode:
        """Парсинг эквиваленции (==, <->)"""
        left = self.parse_implication()
        
        while self.current_token and self.current_token.type == TokenType.EQUIVALENCE:
            op = self.current_token.value
            self.advance()
            right = self.parse_implication()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left

    def parse_implication(self) -> ASTNode:
        """Парсинг импликации (->)"""
        left = self.parse_disjunction()
        
        while self.current_token and self.current_token.type == TokenType.IMPLIES:
            op = self.current_token.value
            self.advance()
            right = self.parse_disjunction()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left

    def parse_disjunction(self) -> ASTNode:
        """Парсинг дизъюнкции (|, +)"""
        left = self.parse_conjunction()
        
        while self.current_token and self.current_token.type in (TokenType.OR, TokenType.PLUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_conjunction()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left

    def parse_conjunction(self) -> ASTNode:
        """Парсинг конъюнкции (&, *)"""
        left = self.parse_negation()
        
        while self.current_token and self.current_token.type in (TokenType.AND, TokenType.MULTIPLY):
            op = self.current_token.value
            self.advance()
            right = self.parse_negation()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left

    def parse_negation(self) -> ASTNode:
        """Парсинг отрицания (!)"""
        if self.current_token and self.current_token.type == TokenType.NOT:
            op = self.current_token.value
            token = self.current_token
            self.advance()
            operand = self.parse_negation()
            return UnaryOpNode(token.position, op, operand)
        
        return self.parse_arithmetic()
    
    def parse_arithmetic(self) -> ASTNode:
        """Парсинг арифметических выражений"""
        return self.parse_additive()
    
    def parse_additive(self) -> ASTNode:
        """Парсинг сложения и вычитания"""
        left = self.parse_multiplicative()
        
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Парсинг умножения и деления"""
        left = self.parse_comparison()
        
        while self.current_token and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Парсинг операций сравнения"""
        left = self.parse_primary()
        
        while self.current_token and self.current_token.type in (TokenType.GT, TokenType.LT, TokenType.GTE, TokenType.LTE, TokenType.EQ, TokenType.NEQ):
            op = self.current_token.value
            self.advance()
            right = self.parse_primary()
            left = BinaryOpNode(left.position, op, left, right)
        
        return left

    def parse_primary(self) -> ASTNode:
        """Парсинг первичных выражений"""
        if not self.current_token:
            raise ParserException("Неожиданный конец файла")

        token = self.current_token
        
        # Предикат или идентификатор
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            # Проверяем, является ли это предикатом (если следующий токен - открывающая скобка)
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                return self.parse_predicate(token.value, token.position)
            else:
                return PropositionNode(token.position, token.value)
        
        # Переменная
        elif token.type == TokenType.VARIABLE:
            self.advance()
            return VariableNode(token.position, token.value)
        
        # Число
        elif token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.position, token.value)
        
        # Строка
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.position, token.value)
        
        # Группировка скобками
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        else:
            raise ParserException(
                f"Неожиданный токен: {token.type}",
                token
            )
    
    def parse_arithmetic_expression(self) -> ASTNode:
        """Парсинг арифметических выражений (для использования внутри предикатов)"""
        return self.parse_additive()

    def parse_predicate(self, name: str, position: int) -> PredicateNode:
        """Парсинг предиката с аргументами"""
        self.expect(TokenType.LPAREN)
        args = []
        
        # Парсинг аргументов
        if not (self.current_token and self.current_token.type == TokenType.RPAREN):
            while True:
                arg = self.parse_arithmetic_expression()
                args.append(arg)
                
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token and self.current_token.type == TokenType.RPAREN:
                    break
                else:
                    raise ParserException(
                        f"Ожидалась запятая или закрывающая скобка, получено {self.current_token.type if self.current_token else 'конец файла'}",
                        self.current_token
                    )
        
        self.expect(TokenType.RPAREN)
        return PredicateNode(position, name, args)