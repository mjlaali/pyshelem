from pyshelem.engine.card import Deck
from pyshelem.engine.simulator import Simulator


def test_init_shelem():
    str_cards = (
        "3S5S4S7D6H4H7SKCAS4C6C9C2D5D3DJDJS8H4DJC2HKD8CQSXDQC9"
        "SXS9HAH6SXH7CKSAC5C7H5H6D2S8D3HQDJH9D8SADQH2CKH3CXC"
    )
    str_game = (
        "259,0,233,253,266,264,"
        f"{str_cards},"
        "*D*E*F*G******_E2C3CXC2SJH4H2H9HQH6H8HAH6S8SASJS7DKDXD6D2"
        "D5CQD4CKH3S8CXH7H4S5D9S5H6C4D7CAD7S3DQC9D9CJDXSQSKS3H5S8DKCJCAC"
    )

    simulator = Simulator.parse(str_game)
    deck = Deck(with_joker=len(str_cards) == 54 * 2)
    cards = deck.parse_cards(str_cards)
    assert set(cards[0:12]) == simulator.shelem.player_cards[0]
    assert set(cards[48:]) == simulator.shelem.left_over_cards
