import logging

import pytest

from engine import (
    Disjunction,
    Conjunction,
    Negation,
    Implication,
    Equivalence,
    LogicalEngine,
    Operation,
    Variable,
    CNF,
    Disjunct,
)


@pytest.fixture
def engine():
    return LogicalEngine(level=logging.CRITICAL)


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        (
            Implication((Variable("a"), Variable("b"))),
            Disjunction((Negation(Variable("a")), Variable("b"))),
        ),
        (
            Conjunction((Implication((Variable("a"), Variable("b"))), Variable("a"))),
            Conjunction(
                (Disjunction((Negation(Variable("a")), Variable("b"))), Variable("a"))
            ),
        ),
        (
            Disjunction((Implication((Variable("a"), Variable("b"))), Variable("a"))),
            Disjunction(
                (Disjunction((Negation(Variable("a")), Variable("b"))), Variable("a"))
            ),
        ),
        (
            Equivalence(
                (
                    Implication((Variable("a"), Variable("b"))),
                    Disjunction((Negation(Variable("a")), Variable("b"))),
                )
            ),
            Equivalence(
                (
                    Disjunction((Negation(Variable("a")), Variable("b"))),
                    Disjunction((Negation(Variable("a")), Variable("b"))),
                )
            ),
        ),
        (
            Implication((Implication((Variable("a"), Variable("b"))), Variable("c"))),
            Disjunction(
                (
                    Negation(Disjunction((Negation(Variable("a")), Variable("b")))),
                    Variable("c"),
                )
            ),
        ),
    ),
)
def test_remove_implications(
    input: Operation, expected: Operation, engine: LogicalEngine
):
    result = engine.remove_implications(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        # first test
        (
            Equivalence((Variable("a"), Variable("b"))),
            Conjunction(
                (
                    Disjunction((Negation(Variable("a")), Variable("b"))),
                    Disjunction((Variable("a"), Negation(Variable("b")))),
                )
            ),
        ),
        # second test
        (
            Conjunction((Equivalence((Variable("a"), Variable("b"))), Variable("a"))),
            Conjunction(
                (
                    Conjunction(
                        (
                            Disjunction((Negation(Variable("a")), Variable("b"))),
                            Disjunction((Variable("a"), Negation(Variable("b")))),
                        )
                    ),
                    Variable("a"),
                )
            ),
        ),
        # third test
        (
            Equivalence(
                (
                    Equivalence((Variable("a"), Variable("b"))),
                    Disjunction((Negation(Variable("a")), Variable("b"))),
                )
            ),
            Conjunction(
                (
                    Disjunction(
                        (
                            Negation(
                                Conjunction(
                                    (
                                        Disjunction(
                                            (Negation(Variable("a")), Variable("b"))
                                        ),
                                        Disjunction(
                                            (Variable("a"), Negation(Variable("b")))
                                        ),
                                    )
                                )
                            ),
                            Disjunction((Negation(Variable("a")), Variable("b"))),
                        )
                    ),
                    Disjunction(
                        (
                            Conjunction(
                                (
                                    Disjunction(
                                        (Negation(Variable("a")), Variable("b"))
                                    ),
                                    Disjunction(
                                        (Variable("a"), Negation(Variable("b")))
                                    ),
                                )
                            ),
                            Negation(
                                Disjunction((Negation(Variable("a")), Variable("b")))
                            ),
                        )
                    ),
                )
            ),
        ),
    ),
)
def test_remove_equivalences(
    input: Operation, expected: Operation, engine: LogicalEngine
):
    result = engine.remove_equivalences(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        (Negation(Negation(Variable("a"))), Variable("a")),
        (
            Disjunction((Negation(Negation(Variable("a"))), Variable("b"))),
            Disjunction((Variable("a"), Variable("b"))),
        ),
        (
            Negation(Negation(Disjunction((Variable("a"), Variable("b"))))),
            Disjunction((Variable("a"), Variable("b"))),
        ),
    ),
)
def test_remove_double_negations(
    input: Operation, expected: Operation, engine: LogicalEngine
):
    result = engine.remove_double_negations(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        (
            Negation(Conjunction((Variable("a"), Variable("b")))),
            Disjunction((Negation(Variable("a")), Negation(Variable("b")))),
        ),
        (
            Negation(Disjunction((Variable("a"), Variable("b")))),
            Conjunction((Negation(Variable("a")), Negation(Variable("b")))),
        ),
        (
            Negation(
                Disjunction(
                    (
                        Negation(Conjunction((Variable("a"), Variable("b")))),
                        Variable("c"),
                    )
                )
            ),
            Conjunction(
                (
                    Conjunction(
                        (
                            Variable("a"),
                            Variable("b"),
                        )
                    ),
                    Negation(Variable("c")),
                )
            ),
        ),
    ),
)
def test_apply_de_morgan(input: Operation, expected: Operation, engine: LogicalEngine):
    result = engine.apply_de_morgan(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        (
            Disjunction((Variable("a"), Conjunction((Variable("b"), Variable("c"))))),
            Conjunction(
                (
                    Disjunction((Variable("a"), Variable("b"))),
                    Disjunction((Variable("a"), Variable("c"))),
                )
            ),
        ),
        (
            Disjunction(
                (
                    Variable("a"),
                    Conjunction(
                        (Conjunction((Variable("b"), Variable("c"))), Variable("d"))
                    ),
                )
            ),
            Conjunction(
                (
                    Conjunction(
                        (
                            Disjunction((Variable("a"), Variable("b"))),
                            Disjunction((Variable("a"), Variable("c"))),
                        )
                    ),
                    Disjunction((Variable("a"), Variable("d"))),
                )
            ),
        ),
    ),
)
def test_group_conjunctions(
    input: Operation, expected: Operation, engine: LogicalEngine
):
    result = engine.group_conjunctions(input)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        (
            Implication(
                (
                    Conjunction(
                        (Variable("p"), Implication((Variable("p"), Variable("q"))))
                    ),
                    Variable("q"),
                )
            ),
            CNF(
                disjuncts=(
                    Disjunct(
                        predicates=(
                            Variable("p"),
                            Negation(Variable("p")),
                            Variable("q"),
                        )
                    ),
                    Disjunct(
                        predicates=(
                            Negation(Variable("p")),
                            Variable("q"),
                            Negation(Variable("q")),
                        )
                    ),
                )
            ),
        ),
    ),
)
def test_to_cnf(input: Operation, expected: CNF, engine: LogicalEngine):
    result = engine.to_cnf(input)
    assert result == expected
