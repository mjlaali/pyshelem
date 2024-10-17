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

    assert deck[card].point == expected_score


def test_init_deck_without_joker():
    cards = "3S5S4S7D6H4H7SKCAS4C6C9C2D5D3DJDJS8H4DJC2HKD8CQSXDQC9SXS9HAH6SXH7CKSAC5C7H5H6D2S8D3HQDJH9D8SADQH2CKH3CXC"

    assert len(cards) == 52 * 2

    deck = Deck(with_joker=False)
    deck_cards = deck.parse_cards(cards)

    assert deck_cards[0] == deck["3S"]
    assert deck_cards[1] == deck["5S"]
    assert deck_cards[-1] == deck["XC"]
    assert len(deck_cards) == 52


def test_init_deck_with_jocker():
    cards = (
        "3D4D9D5S9S6D6S6CQCJSXS5HKC2C8H2HXC2DACXDKSJH8SKH4S"
        "2J4HAHJC5C7DADKD2S8D7H4CQS9H8CASAJ7C3H3CQDJD5D9C7SQH6HXH3S"
    )

    assert len(cards) == 54 * 2

    deck = Deck(with_joker=True)
    deck_cards = deck.parse_cards(cards)

    assert deck["2J"] in deck_cards
    assert deck["AJ"] in deck_cards
