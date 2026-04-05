#!/usr/bin/env python3
"""AAOF v2.0 Strands — AI Agent Orchestrator Framework.

Usage: python aaof.py
"""
import os
import sys
from dotenv import load_dotenv
from workflow.orchestrator import Orchestrator


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found.")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenAI API key")
        sys.exit(1)

    try:
        orchestrator = Orchestrator(config_path="config.yaml")
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n⏸️  Session paused. Run 'python aaof.py' to resume.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
