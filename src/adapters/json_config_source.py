import json
from core.ports import ConfigSource
from core.types import ConfigVO, Position


class JsonConfigSource:
    def __init__(self, config_json: str = "{}"):
        self.config_json = config_json

    def load_config(self) -> ConfigVO:
        data = json.loads(self.config_json)
        bw = data.get("board_width", 20)
        bh = data.get("board_height", 20)
        pc = data.get("player_count", 4)
        sp = data.get("starting_positions", {
            "0": {"row": 0, "col": 0},
            "1": {"row": 0, "col": bw - 1},
            "2": {"row": bh - 1, "col": bw - 1},
            "3": {"row": bh - 1, "col": 0},
        })
        return ConfigVO(
            board_width=bw,
            board_height=bh,
            player_count=pc,
            starting_positions={
                int(k): Position(v["row"], v["col"]) for k, v in sp.items()
            }
        )