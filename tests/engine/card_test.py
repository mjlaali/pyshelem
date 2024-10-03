import pytest

from pyshelem.engine.card import Card, Deck


@pytest.mark.parametrize(
    "str_card,expected_card",
    [
        pytest.param("2C", Card(3, 0), id="2C"),
        pytest.param("XD", Card(2, 8), id="XD"),
        pytest.param("AH", Card(1, 12), id="AH"),
        pytest.param("KS", Card(0, 11), id="AH"),
        pytest.param("2J", Card(4, 0), id="2J"),
        pytest.param("AJ", Card(4, 1), id="2J"),
    ],
)
def test_deck(str_card: str, expected_card: Card):
    deck = Deck()
    assert deck[str_card] == expected_card


@pytest.mark.parametrize(
    "card,expected_score",
    [
        pytest.param("2C", 0, id="2C"),
        pytest.param("5S", 5, id="5S"),
        pytest.param("XD", 10, id="XD"),
        pytest.param("AH", 10, id="AH"),
        pytest.param("2J", 10, id="2J"),
        pytest.param("AJ", 20, id="2J"),
    ],
)
def test_card_score(card: str, expected_score: int):
    deck = Deck()

    assert deck[card].get_point(4) == expected_score
