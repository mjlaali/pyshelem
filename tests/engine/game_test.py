import pytest

from pyshelem.engine.card import Card, Deck
from pyshelem.engine.game import TurnState, Validator
from pyshelem.engine.trick import Trick

deck = Deck()
validator = Validator(deck.pad_card)


@pytest.mark.parametrize(
    "turn_state,card,next_state",
    [
        pytest.param(
            TurnState(
                players_cards=(
                    {deck["AH"], deck["2C"]},
                    {deck["2H"], deck["5D"]},
                    {deck["3S"], deck["5S"]},
                    {deck["4H"], deck["6S"]},
                ),
                trick=Trick(
                    deck["AH"].suit,
                    cards=[deck["PAD"], deck["PAD"], deck["PAD"], deck["PAD"]],
                    first_player=0,
                ),
                player_valid_cards=(deck["AH"]),
                player_idx=0,
                validator=validator,
            ),
            deck["AH"],
            TurnState(
                players_cards=(
                    {deck["2C"]},
                    {deck["2H"], deck["5D"]},
                    {deck["3S"], deck["5S"]},
                    {deck["4H"], deck["6S"]},
                ),
                trick=Trick(
                    deck["AH"].suit,
                    cards=(deck["AH"], deck["PAD"], deck["PAD"], deck["PAD"]),
                    first_player=0,
                ),
                player_valid_cards={deck["2H"]},
                player_idx=1,
                validator=validator,
            ),
            id="first_player",
        ),
        pytest.param(
            TurnState(
                players_cards=(
                    {deck["2C"]},
                    {deck["2H"], deck["5D"]},
                    {deck["3S"], deck["5S"]},
                    {deck["4H"], deck["6S"]},
                ),
                trick=Trick(
                    deck["AH"].suit,
                    cards=(deck["AH"], deck["PAD"], deck["PAD"], deck["PAD"]),
                    first_player=0,
                ),
                player_valid_cards={deck["2H"]},
                player_idx=1,
                validator=validator,
            ),
            deck["2H"],
            TurnState(
                players_cards=(
                    {deck["2C"]},
                    {deck["5D"]},
                    {deck["3S"], deck["5S"]},
                    {deck["4H"], deck["6S"]},
                ),
                trick=Trick(
                    deck["AH"].suit,
                    cards=(deck["AH"], deck["2H"], deck["PAD"], deck["PAD"]),
                    first_player=0,
                ),
                player_valid_cards={deck["3S"], deck["5S"]},
                player_idx=2,
                validator=validator,
            ),
            id="second_player_no_card_with_H",
        ),
        pytest.param(
            TurnState(
                players_cards=(
                    {deck["2C"]},
                    {deck["5D"]},
                    {deck["5S"]},
                    {deck["2J"], deck["6S"]},
                ),
                trick=Trick(
                    trump_suit=deck["AH"].suit,
                    cards=(deck["AH"], deck["2H"], deck["3S"], deck["PAD"]),
                    first_player=0,
                ),
                player_valid_cards={deck["3S"], deck["5S"]},
                player_idx=3,
                validator=validator,
            ),
            deck["2J"],
            TurnState(
                players_cards=(
                    {deck["2C"]},
                    {deck["5D"]},
                    {deck["5S"]},
                    {deck["6S"]},
                ),
                trick=Trick(
                    trump_suit=deck["AH"].suit,
                    cards=(deck["PAD"], deck["PAD"], deck["PAD"], deck["PAD"]),
                    first_player=3,
                ),
                player_valid_cards={deck["6S"]},
                player_idx=3,
                validator=validator,
            ),
            id="last_player",
        ),
    ],
)
def test_turn_play(turn_state: TurnState, card: Card, next_state: TurnState):
    turn_state.played(card)

    assert turn_state == next_state
