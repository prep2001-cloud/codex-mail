# Codex Mail Invoice Automation

This project implements an agentic architecture for downloading invoices from Gmail and archiving them to cloud storage. The system follows a planner+tools pattern where a large language model reasons iteratively about the best next action to achieve the goal of collecting invoices.

## Architecture Overview

```
┌───────────────────────────┐
│      Gmail Inbox          │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐       ┌──────────────────────┐
│  Orchestrator (async)     │──────▶│  Planner Agent (LLM) │
└───────┬────────┬──────────┘       └──────────────────────┘
        │        │
        │        ├─────────────┐
        │                      ▼
        │              ┌──────────────┐
        │              │Interactive   │
        │              │Browser Tool  │
        │              └──────────────┘
        │
        ├──────────────▶ Attachment Processor
        │
        ├──────────────▶ Direct URL Downloader
        │
        ├──────────────▶ Extractor Agent
        │
        └──────────────▶ Archive Agent
```

The orchestrator consumes new Gmail messages, runs deterministic attachment processing first, and then enters an iterative planning loop. During each iteration, the planner receives the current observation and returns a structured JSON action (e.g., `{ "action": "goto", "url": "https://..." }`). The orchestrator executes that action through one of the available tools, feeds the resulting observation back into the planner, and repeats until an invoice document is retrieved or the planner stops.

## Key Components

- **`mail_agent/services/gmail_client.py`** – Wraps the Gmail API with OAuth 2.0 credentials and exposes helpers for fetching messages and streaming inbox updates.
- **`mail_agent/agents/planner.py`** – An iterative large language model planner that reasons step-by-step and emits JSON actions compatible with the tools.
- **`mail_agent/tools/attachment_processor.py`** – Saves any invoice attachments bundled within the email.
- **`mail_agent/tools/web_downloader.py`** – Downloads invoices pointed to by direct URLs in the email body.
- **`mail_agent/tools/interactive_browser.py`** – Provides a Playwright-driven browser for complex multi-step website flows.
- **`mail_agent/agents/extractor.py`** – Converts invoice documents into structured metadata.
- **`mail_agent/agents/archive.py`** – Archives the invoice and metadata to Google Drive or a local folder.
- **`mail_agent/agents/orchestrator.py`** – Coordinates the overall workflow, handles logging, and stores processing outcomes.
- **`mail_agent/main.py`** – Bootstraps the system, wiring configuration, agents, and tools together.

## Running the System

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Export the required environment variables:

   ```bash
   export GMAIL_CLIENT_ID=...
   export GMAIL_CLIENT_SECRET=...
   export GMAIL_REFRESH_TOKEN=...
   export OPENAI_API_KEY=...
   export STORAGE_PROVIDER=gdrive  # or "local"
   export STORAGE_BUCKET=archive   # used when STORAGE_PROVIDER=local
   export STORAGE_ROOT_FOLDER=...  # optional Google Drive folder ID
   ```

3. Launch the orchestrator:

   ```bash
   python -m mail_agent.main
   ```

The application will poll Gmail for new unread messages and process each message to retrieve invoices automatically.
