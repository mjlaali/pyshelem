from __future__ import annotations

import random
from dataclasses import dataclass, field
from functools import total_ordering
from typing import ClassVar


@total_ordering
@dataclass(frozen=True)
class Card:
    suit: int
    rank: int
    idx: int | None = field(default=None, compare=False, hash=False)
    str_value: str | None = field(default=None, compare=False, hash=False)

    # 2 will be mapped to rank=0
    rank_score: ClassVar[dict[int, int]] = {
        (5 - 2): 5,  # 5
        (10 - 2): 10,  # 10
        12: 10,  # Ace
    }

    joker_suit: ClassVar[int] = 4

    @property
    def point(self):
        if self.suit == Card.joker_suit:
            # red joker = 20, black joker = 10
            return 20 if self.rank > 0 else 10
        return self.rank_score.get(self.rank, 0)

    def __eq__(self, other: Card) -> bool:
        return not (self < other) and not (other < self)

    def __lt__(self, other: Card) -> bool:
        return self.suit < other.suit or (
            self.suit == other.suit and self.rank < other.rank
        )


class Deck:
    def __init__(self, with_joker: bool = True):
        self.cards = {}
        self.pad_idx = pad_idx = 0
        self.cards[pad_idx] = self.cards["PAD"] = Card(-1, -1, pad_idx)

        idx = pad_idx + 1
        for si, s in enumerate(("S", "H", "D", "C")):
            for ri, r in enumerate(
                ("2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A")
            ):
                str_value = f"{r}{s}"
                self.cards[idx] = self.cards[str_value] = Card(si, ri, idx, str_value)
                idx += 1

        if with_joker:
            str_value = "2J"
            self.cards[idx] = self.cards[str_value] = Card(4, 0, idx, str_value)
            idx += 1
            str_value = "AJ"
            self.cards[idx] = self.cards[str_value] = Card(4, 1, idx, str_value)
            idx += 1

        self.len = idx
        self._shuffle_card = [self[i] for i in range(self.pad_idx, self.len)]

    def __getitem__(self, item: str | int) -> Card:
        return self.cards[item]

    @property
    def pad_card(self) -> Card:
        return self.cards["PAD"]

    def shuffle_card(self) -> None:
        random.shuffle(self._shuffle_card)

    @property
    def deck_cards(self):
        return self._shuffle_card

    @deck_cards.setter
    def deck_cards(self, cards: list[Card]):
        self._shuffle_card = cards

    def parse_cards(self, str_cards: str) -> list[Card]:
        cards = [self[str_cards[s : s + 2]] for s in range(0, len(str_cards), 2)]
        if len(set(cards)) != len(cards):
            raise ValueError(f"There is duplicate in cards: {cards}")
        return cards

    def __len__(self):
        return self.len
