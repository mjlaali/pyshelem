from __future__ import annotations
from dataclasses import dataclass

from pyshelem.engine.card import Deck
from pyshelem.engine.game import Shelem, ShelemPlayer


@dataclass
class Simulator:
    shelem: Shelem

    @classmethod
    def parse(cls, str_game: str) -> Simulator:
        game_id, first_player_idx, p0_id, p1_id, p2_id, p3_id, cards, events = (
            str_game.split(",")
        )
        with_joker = len(cards) == 54 * 2
        deck = Deck(with_joker=with_joker)
        deck_cards = deck.parse_cards(cards)

        return Simulator(
            Shelem(
                pad_card=deck.pad_card,
                player_cards=list(
                    set(deck_cards[i * 12 : (i + 1) * 12]) for i in range(4)
                ),
                left_over_cards=set(deck_cards[4 * 12 :]),
                players=(ShelemPlayer() for i in range(4)),
                starting_player=first_player_idx,
            )
        )
