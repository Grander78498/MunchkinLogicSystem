from dataclasses import dataclass
from typing import Optional
from models import Operation, Predicate


@dataclass
class Statement:
    """Высказывание в алфавите"""
    id: int
    name: str
    description: Optional[str] = None
    
    def __str__(self):
        return f"[{self.id}] {self.name}"


@dataclass
class Axiom:
    """Аксиома (дизъюнкт Хорна)"""
    id: int
    expression: Operation
    description: Optional[str] = None
    
    def __str__(self):
        return f"({self.id}) {self.expression}"


class KnowledgeBase:
    """База знаний - хранилище высказываний и аксиом"""
    
    def __init__(self):
        self.statements: dict[str, Statement] = {}
        self.axioms: list[Axiom] = []
        self._next_statement_id = 1
        self._next_axiom_id = 1
    
    def add_statement(self, name: str, description: str = None) -> Statement:
        """Добавить высказывание в алфавит"""
        if name in self.statements:
            return self.statements[name]
        
        statement = Statement(
            id=self._next_statement_id,
            name=name,
            description=description
        )
        self.statements[name] = statement
        self._next_statement_id += 1
        return statement
    
    def add_axiom(self, expression: Operation, description: str = None) -> Axiom:
        """Добавить аксиому"""
        axiom = Axiom(
            id=self._next_axiom_id,
            expression=expression,
            description=description
        )
        self.axioms.append(axiom)
        self._next_axiom_id += 1
        return axiom
    
    def remove_axiom(self, axiom_id: int) -> bool:
        """Удалить аксиому по ID"""
        for i, axiom in enumerate(self.axioms):
            if axiom.id == axiom_id:
                self.axioms.pop(i)
                return True
        return False
    
    def get_statement(self, name: str) -> Optional[Statement]:
        """Получить высказывание по имени"""
        return self.statements.get(name)
    
    def get_axiom(self, axiom_id: int) -> Optional[Axiom]:
        """Получить аксиому по ID"""
        for axiom in self.axioms:
            if axiom.id == axiom_id:
                return axiom
        return None
    
    def get_all_statements(self) -> list[Statement]:
        """Получить все высказывания"""
        return sorted(self.statements.values(), key=lambda s: s.id)
    
    def get_all_axioms(self) -> list[Axiom]:
        """Получить все аксиомы"""
        return self.axioms.copy()
    
    def clear(self):
        """Очистить базу знаний"""
        self.statements.clear()
        self.axioms.clear()
        self._next_statement_id = 1
        self._next_axiom_id = 1
    
    def __str__(self):
        result = ["=== БАЗА ЗНАНИЙ ==="]
        result.append(f"\nВысказывания ({len(self.statements)}):")
        for stmt in self.get_all_statements():
            result.append(f"  {stmt}")
        result.append(f"\nАксиомы ({len(self.axioms)}):")
        for axiom in self.axioms:
            result.append(f"  {axiom}")
        return "\n".join(result)