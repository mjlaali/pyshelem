from dataclasses import dataclass

from pyshelem.engine.game import Shelem, ShelemPlayer


@dataclass
class Simulator:
    shelem: Shelem
    players: (ShelemPlayer, ShelemPlayer, ShelemPlayer, ShelemPlayer)

    def parse(self, str_game):
        str_game
