# import pytest
# from lexer import Lexer, TokenType, LexerException
# from parser import Parser, ParserException
# from engine import Variable, Conjunction, Disjunction, Negation, Implication, Equivalence


# class TestLexer:
#     """Тесты для лексера"""
    
#     def test_simple_identifier(self):
#         """Тест простого идентификатора"""
#         lexer = Lexer("монстр_дракон")
#         tokens = lexer.tokenize()
#         assert len(tokens) == 2  # IDENTIFIER + EOF
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[0].value == "монстр_дракон"
    
#     def test_fact_with_dot(self):
#         """Тест факта с точкой"""
#         lexer = Lexer("монстр_дракон.")
#         tokens = lexer.tokenize()
#         assert len(tokens) == 3  # IDENTIFIER + DOT + EOF
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[1].type == TokenType.DOT
    
#     def test_theorem_with_question(self):
#         """Тест теоремы с вопросом"""
#         lexer = Lexer("игрок_1_победитель?")
#         tokens = lexer.tokenize()
#         assert len(tokens) == 3  # IDENTIFIER + QUERY + EOF
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[1].type == TokenType.QUERY
    
#     def test_operators(self):
#         """Тест операторов"""
#         lexer = Lexer("a & b | c ! d")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[1].type == TokenType.AND
#         assert tokens[2].type == TokenType.IDENTIFIER
#         assert tokens[3].type == TokenType.OR
#         assert tokens[4].type == TokenType.IDENTIFIER
#         assert tokens[5].type == TokenType.NOT
#         assert tokens[6].type == TokenType.IDENTIFIER
    
#     def test_implication(self):
#         """Тест импликации"""
#         lexer = Lexer("a --> b")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[1].type == TokenType.IMPLIES
#         assert tokens[2].type == TokenType.IDENTIFIER
    
#     def test_equivalence(self):
#         """Тест эквиваленции"""
#         lexer = Lexer("a == b")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.IDENTIFIER
#         assert tokens[1].type == TokenType.EQUIVALENCE
#         assert tokens[2].type == TokenType.IDENTIFIER
    
#     def test_string_literal(self):
#         """Тест строкового литерала"""
#         lexer = Lexer('"игрок 2 имеет уровень 1"')
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.STRING
#         assert tokens[0].value == "игрок 2 имеет уровень 1"
    
#     def test_string_with_escape(self):
#         """Тест строкового литерала с escape-последовательностями"""
#         lexer = Lexer('"игрок\\n2"')
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.STRING
#         assert tokens[0].value == "игрок\n2"
    
#     def test_complex_expression(self):
#         """Тест сложного выражения"""
#         lexer = Lexer("игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 --> игрок_победил.")
#         tokens = lexer.tokenize()
#         assert len(tokens) > 5
#         assert TokenType.AND in [t.type for t in tokens]
#         assert TokenType.IMPLIES in [t.type for t in tokens]
#         assert TokenType.DOT in [t.type for t in tokens]
    
#     def test_comment_single_line(self):
#         """Тест однострочного комментария"""
#         lexer = Lexer("a // комментарий\nb")
#         tokens = lexer.tokenize()
#         # Комментарий должен быть пропущен
#         identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
#         assert len(identifiers) == 2
#         assert identifiers[0].value == "a"
#         assert identifiers[1].value == "b"
    
#     def test_comment_multi_line(self):
#         """Тест многострочного комментария"""
#         lexer = Lexer("a /* комментарий\nна несколько строк */ b")
#         tokens = lexer.tokenize()
#         identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
#         assert len(identifiers) == 2
#         assert identifiers[0].value == "a"
#         assert identifiers[1].value == "b"
    
#     def test_commands(self):
#         """Тест команд"""
#         lexer = Lexer("load example.shldn.")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.LOAD
#         assert tokens[1].type == TokenType.IDENTIFIER
#         assert tokens[2].type == TokenType.DOT
        
#         lexer = Lexer("get axioms.")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.GET
#         assert tokens[1].type == TokenType.AXIOMS
#         assert tokens[2].type == TokenType.DOT
        
#         lexer = Lexer("remove 1.")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.REMOVE
#         assert tokens[1].type == TokenType.NUMBER
#         assert tokens[2].type == TokenType.DOT
    
#     def test_parentheses(self):
#         """Тест скобок"""
#         lexer = Lexer("(a & b)")
#         tokens = lexer.tokenize()
#         assert tokens[0].type == TokenType.LPAREN
#         assert tokens[4].type == TokenType.RPAREN
    
#     def test_lexer_exception(self):
#         """Тест исключения лексера"""
#         lexer = Lexer("@")
#         with pytest.raises(LexerException):
#             lexer.tokenize()
    
#     def test_unclosed_string(self):
#         """Тест незакрытой строки"""
#         lexer = Lexer('"незакрытая строка')
#         with pytest.raises(LexerException):
#             lexer.tokenize()


# class TestParser:
#     """Тесты для парсера"""
    
#     def test_simple_fact(self):
#         """Тест простого факта"""
#         lexer = Lexer("монстр_дракон.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Variable)
#         assert statements[0].value == "монстр_дракон"
    
#     def test_simple_theorem(self):
#         """Тест простой теоремы"""
#         lexer = Lexer("игрок_1_победитель?")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Variable)
#         assert statements[0].value == "игрок_1_победитель"
    
#     def test_simple_implication(self):
#         """Тест простой импликации"""
#         lexer = Lexer("a --> b.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Implication)
#         assert isinstance(statements[0].children[0], Variable)
#         assert isinstance(statements[0].children[1], Variable)
    
#     def test_conjunction(self):
#         """Тест конъюнкции"""
#         lexer = Lexer("a & b.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Conjunction)
#         assert len(statements[0].children) == 2
    
#     def test_disjunction(self):
#         """Тест дизъюнкции"""
#         lexer = Lexer("a | b.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Disjunction)
#         assert len(statements[0].children) == 2
    
#     def test_negation(self):
#         """Тест отрицания"""
#         lexer = Lexer("!a.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Negation)
#         assert isinstance(statements[0].child, Variable)
    
#     def test_equivalence(self):
#         """Тест эквиваленции"""
#         lexer = Lexer("a == b.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Equivalence)
#         assert len(statements[0].children) == 2
    
#     def test_complex_expression(self):
#         """Тест сложного выражения"""
#         lexer = Lexer("a & b --> c.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Implication)
#         assert isinstance(statements[0].children[0], Conjunction)
#         assert isinstance(statements[0].children[1], Variable)
    
#     def test_operator_precedence(self):
#         """Тест приоритета операторов"""
#         lexer = Lexer("a & b | c & d.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         # Должна быть дизъюнкция, где левая часть - конъюнкция, правая - конъюнкция
#         assert isinstance(statements[0], Disjunction)
#         assert isinstance(statements[0].children[0], Conjunction)
#         assert isinstance(statements[0].children[1], Conjunction)
    
#     def test_parentheses(self):
#         """Тест скобок"""
#         lexer = Lexer("(a | b) & c.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert isinstance(statements[0], Conjunction)
#         assert isinstance(statements[0].children[0], Disjunction)
#         assert isinstance(statements[0].children[1], Variable)
    
#     def test_string_literal(self):
#         """Тест строкового литерала"""
#         lexer = Lexer('"игрок 2 имеет уровень 1".')
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Variable)
#         assert statements[0].value == "игрок 2 имеет уровень 1"
    
#     def test_nested_negation(self):
#         """Тест вложенного отрицания"""
#         lexer = Lexer("!(!a).")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert isinstance(statements[0], Negation)
#         assert isinstance(statements[0].child, Negation)
    
#     def test_real_world_example(self):
#         """Тест реального примера из example.shldn"""
#         lexer = Lexer("игрок_2_уровень_5 & игрок_2_сила_10 & монстр_сила_14 --> игрок_победил.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 1
#         assert isinstance(statements[0], Implication)
#         # Левая часть должна быть конъюнкцией
#         assert isinstance(statements[0].children[0], Conjunction)
#         # Правая часть должна быть переменной
#         assert isinstance(statements[0].children[1], Variable)
    
#     def test_parser_exception(self):
#         """Тест исключения парсера"""
#         lexer = Lexer("a &")
#         parser = Parser(lexer)
#         # Парсер ловит исключения и возвращает пустой список
#         statements = parser.parse()
#         assert len(statements) == 0
    
#     def test_multiple_statements(self):
#         """Тест множественных высказываний"""
#         lexer = Lexer("a. b. c.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 3
#         assert all(isinstance(s, Variable) for s in statements)
    
#     def test_command_parsing(self):
#         """Тест парсинга команд"""
#         # Команды возвращают None, но None не добавляется в список statements
#         # (проверка if statement is not None)
#         lexer = Lexer("load example.shldn.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         # Команды не добавляются в список statements (возвращают None)
#         assert len(statements) == 0
        
#         lexer = Lexer("get axioms.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 0
        
#         lexer = Lexer("remove 1.")
#         parser = Parser(lexer)
#         statements = parser.parse()
#         assert len(statements) == 0

