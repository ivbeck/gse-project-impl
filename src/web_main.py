from adapters.web_orchestrator import create_web_orchestrator
from adapters.web_player_adapter import WebPlayerAdapter
from adapters.web_presentation_adapter import WebPresentationAdapter
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
from bootstrap import create_game
import uvicorn

def run_web(mode: str = "classic"):
    config_json = DUO_CONFIG_JSON if mode == "duo" else "{}"
    config = JsonConfigSource(config_json).load_config()
    session = create_game(config)
    player = WebPlayerAdapter()
    presenter = WebPresentationAdapter(session)
    app = create_web_orchestrator(session, player, presenter)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_web()