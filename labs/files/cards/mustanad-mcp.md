# mustanad-mcp

A Model Context Protocol server that lets an AI assistant search and read documents in a document store.

- Licence: GNU Affero General Public License v3.0 (AGPL-3.0-only), file `LICENSE`
- The server ships connectors for two open-source document stores. Other stores need a connector you write.
- Typical deployment: the server runs inside your network; staff reach it through an assistant in their browser.

## Writing your own connector

Add a module under `connectors/` and register it in `server.py`. Connectors are part of the Program.
