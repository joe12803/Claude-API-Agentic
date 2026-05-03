# Claude API Agentic Bridge (V4.0)

A powerful FastAPI-based bridge that transforms Claude 3.5 Sonnet (Web) into a fully functional Agentic model. 

## Features
- **Agentic Orchestration (V4.0)**: Automatically generates bash commands to fetch real system data, overcoming Claude's compliance refusals and "no access" hallucinations.
- **OpenAI Compatible**: Seamlessly integrates with tools like Hermes Agent, OpenAI SDKs, and more.
- **Smart Filtering**: Intercepts and replaces AI refusal messages with factual execution results.
- **Non-stream Support**: Specifically optimized for "Auxiliary title generation" in chat interfaces.

## Quick Start
1. Clone the repository.
2. Install dependencies: `pip install -r requirements-extra.txt`.
3. Configure your `session_key` in `accounts.json`.
4. Run: `python api_server.py`.

## License
MIT
