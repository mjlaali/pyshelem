from dataclasses import dataclass, field

from pyshelem.engine.card import Card


@dataclass
class Trick:
    trump_suit: int
    cards: list[Card]
    joker_suit: int = 4

    def get_winner(self) -> int:
        first_card_suit = self.cards[0].suit
        card_tuples = (
            (
                self.joker_suit == card.suit,  # joker
                self.trump_suit == card.suit,  # trump
                first_card_suit == card.suit,  # same as the first suit
                card.rank,  # rank
                idx,  # player
            )
            for idx, card in enumerate(self.cards)
        )
        sorted_cards = sorted(card_tuples, reverse=True)
        return sorted_cards[0][-1]

    def get_point(self) -> int:
        score = 5 + sum(card.get_point(self.joker_suit) for card in self.cards)
        return score
