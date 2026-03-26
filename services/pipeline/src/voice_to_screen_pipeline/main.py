from __future__ import annotations

import json

from .contracts import SessionConfig
from .orchestrator import PipelineOrchestrator


def main() -> None:
    config = SessionConfig(source_language="ja")
    orchestrator = PipelineOrchestrator(config=config)

    for event in orchestrator.start():
        print(json.dumps(event.to_dict()))


if __name__ == "__main__":
    main()
