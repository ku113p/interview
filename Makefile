# Variables
PYTHON := uv run python
KERNEL_NAME := langgraph-agent
# Avoid parentheses here to prevent shell expansion issues in some environments
DISPLAY_NAME := "Python-LangGraph-Agent"

.PHONY: help install run-cli run-telegram-polling run-telegram-webhook run-mcp dev-setup jupyter clean test test-cov

install: ## Install production dependencies
	uv sync

run-cli: ## Run the CLI app (transport=cli). Usage: make run-cli -- --user-id <uuid>
	@$(PYTHON) main.py --transport cli $(filter-out run-cli --,$(MAKECMDGOALS))

run-telegram-polling: ## Run Telegram bot in polling mode
	@TELEGRAM_MODE=polling $(PYTHON) main.py --transport telegram

run-telegram-webhook: ## Run Telegram bot in webhook mode
	@TELEGRAM_MODE=webhook $(PYTHON) main.py --transport telegram

run-mcp: ## Run MCP server (Streamable HTTP)
	@$(PYTHON) mcp_server.py

%:
	@:

dev-setup: install ## Install dev deps and register Jupyter kernel
	uv add --dev ipykernel grandalf
	uv run python -m ipykernel install --user --name='$(KERNEL_NAME)' --display-name='$(DISPLAY_NAME)'
	@echo "Kernel registered successfully."

jupyter: ## Run Jupyter Lab with project context
	uv run --with jupyter jupyter lab

graph-check: ## Quick check if LangGraph visualization deps are working
	$(PYTHON) -c "import grandalf; import langchain_core; print('Visualization deps ready!')"

test: ## Run all tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v
	@echo "Coverage report saved to htmlcov/index.html"

clean: ## Remove virtual environment and cached files
	rm -rf .venv
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
