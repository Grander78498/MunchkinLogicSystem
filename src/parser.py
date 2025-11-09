from lexer import Lexer, Token, TokenType
from engine import Variable, Conjunction, Disjunction, Negation, Implication, Equivalence, Operation


class ParserException(Exception):
    def __init__(self, message: str, token: Token | None = None):
        self.message = message
        self.token = token
        super().__init__(self.message)
    
    def __str__(self):
        if self.token:
            return f"{self.message} at token {self.token} (line {self.token.line}, column {self.token.column})"
        return self.message


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens: list[Token] = []
        self.current_token_index = 0
    
    def current_token(self) -> Token | None:
        """Возвращает текущий токен"""
        if self.current_token_index >= len(self.tokens):
            return None
        return self.tokens[self.current_token_index]
    
    def peek_token(self, offset: int = 1) -> Token | None:
        """Заглядывает вперед на offset токенов"""
        pos = self.current_token_index + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]
    
    def advance(self) -> Token | None:
        """Переходит к следующему токену"""
        if self.current_token_index < len(self.tokens):
            self.current_token_index += 1
        return self.current_token()
    
    def expect(self, token_type: TokenType, error_message: str | None = None) -> Token:
        """Ожидает токен определенного типа"""
        token = self.current_token()
        if token is None:
            raise ParserException(error_message or f"Ожидался {token_type.name}, но достигнут конец файла")
        if token.type != token_type:
            raise ParserException(
                error_message or f"Ожидался {token_type.name}, но получен {token.type.name}",
                token
            )
        self.advance()
        return token
    
    def parse(self) -> list[Variable | Implication]:
        """Парсит весь текст и возвращает список высказываний и аксиом"""
        # Сначала токенизируем
        self.tokens = self.lexer.tokenize()
        self.current_token_index = 0
        
        statements = []
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            # Пропускаем комментарии (они уже обработаны лексером)
            if self.current_token().type == TokenType.EOF:
                break
            
            # Парсим высказывание, аксиому или команду
            try:
                statement = self.parse_statement()
                if statement is not None:
                    statements.append(statement)
            except ParserException:
                # Если ошибка парсинга, пропускаем и продолжаем
                # В реальном приложении можно добавить логирование
                break
        
        return statements
    
    def parse_statement(self) -> Variable | Implication | None:
        """Парсит одно высказывание или аксиому"""
        token = self.current_token()
        if token is None or token.type == TokenType.EOF:
            return None
        
        # Парсим команду (load, get, remove)
        if token.type in (TokenType.LOAD, TokenType.GET, TokenType.REMOVE):
            return self.parse_command()
        
        # Парсим выражение (высказывание, аксиома или теорема)
        expr = self.parse_expression()
        
        # Проверяем, что после выражения идет точка, вопрос или EOF
        if self.current_token() and self.current_token().type == TokenType.QUERY:
            # Теорема (выражение заканчивается на ?)
            self.advance()  # пропускаем ?
            return expr
        elif self.current_token() and self.current_token().type == TokenType.DOT:
            # Обычное высказывание или аксиома (заканчивается на .)
            self.advance()
        elif self.current_token() and self.current_token().type != TokenType.EOF:
            # Если не точка, не вопрос и не EOF, это ошибка
            raise ParserException("Ожидалась точка или вопрос после выражения", self.current_token())
        
        return expr
    
    def parse_command(self) -> None:
        """Парсит команду (load, get, remove)"""
        token = self.current_token()
        if token.type == TokenType.LOAD:
            self.advance()  # load
            # Ожидаем идентификатор (имя файла может содержать точки)
            # Имя файла может быть несколькими идентификаторами, разделенными точками
            # Читаем все идентификаторы и точки до последней точки (которая является разделителем команды)
            filename_parts = []
            while self.current_token() and self.current_token().type != TokenType.EOF:
                if self.current_token().type == TokenType.IDENTIFIER:
                    filename_parts.append(self.current_token().value)
                    self.advance()
                elif self.current_token().type == TokenType.DOT:
                    # Проверяем, является ли это последней точкой
                    peek = self.peek_token()
                    if peek and peek.type == TokenType.EOF:
                        # Это последняя точка команды
                        self.advance()
                        break
                    else:
                        # Это точка внутри имени файла
                        filename_parts.append('.')
                        self.advance()
                else:
                    break
            
            if not filename_parts:
                raise ParserException("Ожидалось имя файла после load", self.current_token())
            
            # Команды не возвращают AST, они обрабатываются отдельно
            return None
        elif token.type == TokenType.GET:
            self.advance()  # get
            self.expect(TokenType.AXIOMS, "Ожидалось 'axioms' после get")
            self.expect(TokenType.DOT, "Ожидалась точка после команды get")
            return None
        elif token.type == TokenType.REMOVE:
            self.advance()  # remove
            # Ожидаем число (номер аксиомы)
            self.expect(TokenType.NUMBER, "Ожидался номер аксиомы после remove")
            self.expect(TokenType.DOT, "Ожидалась точка после команды remove")
            return None
        return None
    
    def parse_expression(self) -> Variable | Operation:
        """Парсит выражение (эквиваленция имеет самый низкий приоритет)"""
        return self.parse_equivalence()
    
    def parse_equivalence(self) -> Variable | Operation:
        """Парсит эквиваленцию (==)"""
        left = self.parse_implication()
        
        while self.current_token() and self.current_token().type == TokenType.EQUIVALENCE:
            self.advance()  # ==
            right = self.parse_implication()
            left = Equivalence((left, right))
        
        return left
    
    def parse_implication(self) -> Variable | Operation:
        """Парсит импликацию (-->)"""
        left = self.parse_disjunction()
        
        while self.current_token() and self.current_token().type == TokenType.IMPLIES:
            self.advance()  # -->
            right = self.parse_disjunction()
            left = Implication((left, right))
        
        return left
    
    def parse_disjunction(self) -> Variable | Operation:
        """Парсит дизъюнкцию (|)"""
        left = self.parse_conjunction()
        
        while self.current_token() and self.current_token().type == TokenType.OR:
            self.advance()  # |
            right = self.parse_conjunction()
            left = Disjunction((left, right))
        
        return left
    
    def parse_conjunction(self) -> Variable | Operation:
        """Парсит конъюнкцию (&)"""
        left = self.parse_negation()
        
        while self.current_token() and self.current_token().type == TokenType.AND:
            self.advance()  # &
            right = self.parse_negation()
            left = Conjunction((left, right))
        
        return left
    
    def parse_negation(self) -> Variable | Operation:
        """Парсит отрицание (!)"""
        if self.current_token() and self.current_token().type == TokenType.NOT:
            self.advance()  # !
            operand = self.parse_negation()  # Рекурсивно для обработки !!
            return Negation(operand)
        
        return self.parse_atom()
    
    def parse_atom(self) -> Variable | Operation:
        """Парсит атом (идентификатор, строка или выражение в скобках)"""
        token = self.current_token()
        
        if token is None:
            raise ParserException("Неожиданный конец файла")
        
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Variable(token.value)
        
        if token.type == TokenType.STRING:
            self.advance()
            # Строковые литералы также представляются как Variable
            return Variable(token.value)
        
        if token.type == TokenType.LPAREN:
            self.advance()  # (
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Ожидалась закрывающая скобка")
            return expr
        
        raise ParserException(f"Неожиданный токен: {token.type.name}", token)

