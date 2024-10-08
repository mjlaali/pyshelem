from __future__ import annotations

import pytest

from pyshelem.engine.card import Card, Deck
from pyshelem.engine.trick import Trick


@pytest.mark.parametrize(
    "cards,trump_suit,winner_idx",
    [
        pytest.param(
            (Card(0, 0), Card(0, 1), Card(0, 2), Card(0, 3)), 0, 3, id="same_suit"
        ),
        pytest.param(
            (Card(0, 0), Card(0, 1), Card(0, 2), Card(1, 3)), 0, 2, id="different_suit"
        ),
        pytest.param(
            (Card(0, 0), Card(2, 1), Card(0, 2), Card(1, 3)),
            2,
            1,
            id="different_suit_trump",
        ),
        pytest.param(
            (Card(0, 0), Card(2, 1), Card(2, 2), Card(1, 3)),
            2,
            2,
            id="different_two_trumps",
        ),
        pytest.param(
            (Card(4, 0), Card(2, 1), Card(2, 2), Card(1, 3)),
            2,
            0,
            id="joker",
        ),
    ],
)
def test_trick_winner(cards: tuple[Card], trump_suit: int, winner_idx: int) -> None:
    trick = Trick(trump_suit, cards, 0)
    assert trick.winner == winner_idx


deck = Deck()


@pytest.mark.parametrize(
    "cards,trump_suit,expected_point",
    [
        pytest.param(
            (deck["2C"], deck["3C"], deck["4C"], deck["6C"]), 0, 5, id="no_special_card"
        ),
        pytest.param((deck["2C"], deck["3C"], deck["4C"], deck["5C"]), 0, 10, id="5"),
        pytest.param(
            (deck["2C"], deck["3C"], deck["XC"], deck["5C"]), 0, 20, id="5,10"
        ),
        pytest.param(
            (deck["2C"], deck["AC"], deck["XC"], deck["5C"]), 0, 30, id="5,10,A"
        ),
        pytest.param(
            (deck["2J"], deck["AC"], deck["XC"], deck["5C"]), 0, 40, id="5,10,2J"
        ),
        pytest.param(
            (deck["AJ"], deck["AC"], deck["XC"], deck["5C"]), 0, 50, id="5,10,AJ"
        ),
    ],
)
def test_trick_point(cards: tuple[Card], trump_suit: int, expected_point: int) -> None:
    trick = Trick(trump_suit, cards, 0)
    assert trick.point == expected_point
