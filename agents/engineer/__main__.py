"""Run the Engineer agent standalone."""

from agents.engineer.agent import engineer

if __name__ == "__main__":
    engineer.cli_app(stream=True)
