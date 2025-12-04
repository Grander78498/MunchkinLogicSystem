from engine import LogicalEngine
from models import (
    Conjunction,
    Disjunction,
    Implication,
    Equivalence,
    Negation,
    CNF,
    Disjunct,
    Variable,
    Predicate,
)


def first(engine: LogicalEngine):
    engine.add_axiom(Implication((Variable("a"), Variable("b"))))
    engine.add_axiom(Implication((Variable("b"), Variable("c"))))
    engine.resolution_method(Implication((Variable("a"), Variable("c"))))


def second(engine: LogicalEngine):
    engine.add_axiom(Implication((Variable("S"), Variable("F"))))
    engine.add_axiom(
        Implication(
            (
                Variable("F"),
                Conjunction(
                    (
                        Conjunction((Negation(Variable("G")), Negation(Variable("D")))),
                        Negation(Variable("E")),
                    )
                ),
            )
        )
    )
    engine.add_axiom(
        Implication(
            (Negation(Variable("F")), Conjunction((Variable("D"), Variable("E"))))
        )
    )
    engine.add_axiom(Implication((Negation(Variable("D")), Negation(Variable("E")))))

    engine.resolution_method(
        Implication(
            (Conjunction((Negation(Variable("S")), Variable("D"))), Variable("E"))
        )
    )


def third(engine: LogicalEngine):
    axioms = engine.add_axiom(Disjunction((Variable("A"), Variable("C"))))
    resolve, _ = axioms[0].add_predicate(
        Disjunct(predicates=(Variable("B"), Negation(Variable("C"))))
    )
    print(resolve)


def main():
    engine = LogicalEngine()
    # first(engine)
    second(engine)
    # third(engine)


if __name__ == "__main__":
    main()
