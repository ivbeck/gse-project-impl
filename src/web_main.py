from adapters.web_orchestrator import create_web_orchestrator
from adapters.web_player_adapter import WebPlayerAdapter
from adapters.web_presentation_adapter import WebPresentationAdapter
from adapters.json_config_source import JsonConfigSource
from bootstrap import create_game
import uvicorn

def run_web():
    config = JsonConfigSource().load_config()
    def create_session():
        return create_game(config)

    session = create_session()
    player = WebPlayerAdapter()
    presenter = WebPresentationAdapter(session)
    app = create_web_orchestrator(session, player, presenter, session_factory=create_session)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_web()
