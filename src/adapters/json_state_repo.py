import json
from core.ports import StateRepository
from core.memento import Memento
from core.types import ConfigVO, Position


class JsonStateRepo:
    def save(self, memento: Memento) -> str:
        return json.dumps({
            "config": {
                "board_width": memento.config.board_width,
                "board_height": memento.config.board_height,
                "player_count": memento.config.player_count,
                "starting_positions": {
                    str(pid): {"row": pos.row, "col": pos.col}
                    for pid, pos in memento.config.starting_positions.items()
                }
            },
            "board_state": [[cell for cell in row] for row in memento.board_state],
            "current_player_id": memento.current_player_id,
            "remaining_pieces": [
                (player_id, list(pieces))
                for player_id, pieces in memento.remaining_pieces
            ],
            "consecutive_passes": memento.consecutive_passes,
            "is_first_move": [
                (player_id, flag)
                for player_id, flag in memento.is_first_move
            ],
        })

    def restore(self, data: str) -> Memento:
        parsed = json.loads(data)
        config_data = parsed["config"]
        config = ConfigVO(
            board_width=config_data["board_width"],
            board_height=config_data["board_height"],
            player_count=config_data["player_count"],
            starting_positions={
                int(pid): Position(pos["row"], pos["col"])
                for pid, pos in config_data["starting_positions"].items()
            }
        )
        board_state = tuple(
            tuple(cell for cell in row)
            for row in parsed["board_state"]
        )
        remaining_pieces = tuple(
            (item[0], tuple(item[1]))
            for item in parsed["remaining_pieces"]
        )
        is_first_move = tuple(
            (item[0], item[1])
            for item in parsed["is_first_move"]
        )
        return Memento(
            config=config,
            board_state=board_state,
            current_player_id=parsed["current_player_id"],
            remaining_pieces=remaining_pieces,
            consecutive_passes=parsed["consecutive_passes"],
            is_first_move=is_first_move,
        )