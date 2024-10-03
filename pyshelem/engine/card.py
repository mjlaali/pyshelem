from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Card:
    suit: int
    rank: int

    # 2 will be mapped to rank=0
    rank_score: ClassVar[dict[int, int]] = {
        (5 - 2): 5,  # 5
        (10 - 2): 10,  # 10
        12: 10,  # Ace
    }

    def get_point(self, joker_suit: int):
        if self.suit == joker_suit:
            # red joker = 20, black joker = 10
            return 20 if self.rank > 0 else 10
        return self.rank_score.get(self.rank, 0)


class Deck:
    def __init__(self):
        self.cards = {}
        for si, s in enumerate(("S", "H", "D", "C")):
            for ri, r in enumerate(
                ("2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A")
            ):
                self.cards[f"{r}{s}"] = Card(si, ri)

        self.cards["2J"] = Card(4, 0)
        self.cards["AJ"] = Card(4, 1)

    def __getitem__(self, item: str) -> Card:
        return self.cards[item]
