import unittest
from unittest.mock import MagicMock

from pyshelem.engine.card import Deck
from pyshelem.engine.simulator import Simulator, Parser

str_cards = (
    "3S5S4S7D6H4H7SKCAS4C6C9C2D5D3DJDJS8H4DJC2HKD8CQSXDQC9"
    "SXS9HAH6SXH7CKSAC5C7H5H6D2S8D3HQDJH9D8SADQH2CKH3CXC"
)
deck = Deck(with_joker=len(str_cards) == 54 * 2)

betting_round = "*D*E*F*G******"
discard_cards = ("2C", "3C", "XC", "2S")
str_discard_cards = "".join(discard_cards)
plays = "JH4H2H9HQH6H8HAH6S8SASJS7DKDXD6D2D5CQD4CKH3S8CXH7H4S5D9S5H6C4D7CAD7S3DQC9D9CJDXSQSKS3H5S8DKCJCAC"
other_events = f"E{str_discard_cards}{plays}"
str_game = f"259,0,233,253,266,264,{str_cards},{betting_round}_{other_events}"


class TestParser(unittest.TestCase):
    def test_set_player_cards(self) -> None:
        parser = Parser()
        parser.set_player_cards(str_cards)

        cards = deck.parse_cards(str_cards)
        self.assertEquals(set(cards[0:12]), parser.player_cards[0])
        self.assertEquals(set(cards[48:]), parser.left_over_cards)

    def test_betting_round(self) -> None:
        parser = Parser()
        parser.set_betting(betting=betting_round, first_player_idx=0)

        self.assertEquals(parser.bidding_winner, 3)

        player_bids = [[vale] for vale in (110, 115, 120, 125)]

        self.assertEquals(parser.player_bids, player_bids)

    def test_discard_cards(self) -> None:
        parser = Parser()
        parser.set_discard_cards(str_discard_cards, deck, 3)
        expected = [[] for _ in range(4)]
        expected[3] = [deck[card] for card in discard_cards]

        self.assertEquals(expected, parser.discard_cards)

    def test_set_other_events(self) -> None:
        parser = Parser()
        parser.deck = MagicMock()
        parser.bidding_winner = 3
        parser.set_discard_cards = MagicMock(return_value=parser)
        parser.set_plays = MagicMock(return_value=parser)
        parser.set_other_events(other_events=other_events)

        parser.set_discard_cards.assert_called_once_with(
            str_discard_cards, parser.deck, parser.bidding_winner
        )
        parser.set_plays.assert_called_once_with(plays, parser.deck)

    def test_set_plays(self) -> None:
        parser = Parser()
        players_play = ["JH", "4H", "2H", "9H", "QH", "6H", "8H", "AH"]

        str_plays = "".join(players_play)

        parser.set_plays(str_plays, deck)
        expected_plays = [
            [deck[players_play[i]], deck[players_play[i + 4]]] for i in range(4)
        ]
        self.assertEquals(parser.player_plays, expected_plays)


class TestSimulator(unittest.TestCase):
    def test_read_game(self) -> None:
        simulator = Simulator(str_game)
        self.assertIsNotNone(simulator.shelem)
