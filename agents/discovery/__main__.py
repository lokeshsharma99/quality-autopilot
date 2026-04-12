"""Run Discovery Agent standalone: python -m agents.discovery"""

from agents.discovery.agent import discovery

if __name__ == "__main__":
    discovery.cli_app(markdown=True)
