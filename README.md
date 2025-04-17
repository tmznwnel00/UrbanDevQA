# Urban Development QnA

## References

* [Anthropic - Building MCP with LLMs](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms)
* [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
* [MCP Servers](https://github.com/modelcontextprotocol/servers)

## Requirements

```
uv, python >= 3.11 
```

* uv: An extremely fast Python package and project manager, written in Rust. - https://docs.astral.sh/uv/guides/projects/

## Installation

Install the following dependencies:

```bash
$ uv venv
$ uv sync
``` 

## .env File

It will be helpful to create a `.env` file in the root directory of the project. This file will contain your API keys and other environment variables.

```python
OPENAI_API_KEY="[your_openai_api_key]"
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="[your_langsmith_api_key]"
LANGSMITH_PROJECT="[your_langsmith_project]"
```

* Langsmith is a tool for tracking and analyzing the performance of your LLM applications. It provides a way to log inputs, outputs, and metadata about your LLM calls, which can be useful for debugging and improving your models.
* https://www.langchain.com/langsmith