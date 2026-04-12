"""Run the Architect agent standalone."""

from agents.architect.agent import architect

if __name__ == "__main__":
    architect.cli_app(stream=True)
