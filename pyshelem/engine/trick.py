from dataclasses import dataclass, field

from pyshelem.engine.card import Card, Deck


@dataclass(frozen=True)
class Trick:
    trump_suit: int
    cards: (Card, Card, Card, Card)
    first_player: int

    @property
    def winner(self) -> int:
        first_card_suit = self.cards[0].suit
        card_tuples = (
            (
                Card.joker_suit == card.suit,  # joker
                self.trump_suit == card.suit,  # trump
                first_card_suit == card.suit,  # same as the first suit
                card.rank,  # rank
                idx,  # player
            )
            for idx, card in enumerate(self.cards)
        )
        sorted_cards = sorted(card_tuples, reverse=True)
        return sorted_cards[0][-1]

    @property
    def point(self) -> int:
        score = 5 + sum(card.point for card in self.cards)
        return score

    @property
    def first_card(self) -> Card:
        return self.cards[self.first_player]

    def __len__(self):
        return len(self.cards)
