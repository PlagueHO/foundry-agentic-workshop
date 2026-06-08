# Synthetic Data Generator

A small, extensible Python package that generates **realistic but entirely
fictional** synthetic datasets for the Microsoft Foundry agentic workshop. It is
powered by the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
and Azure OpenAI.

Two scenarios (`retail-product` and `retail-policy`) are **search-index-ready**:
they emit flat documents with an `id` / `title` / `content` triplet plus a
`contentVector` embedding, so the workshop's Foundry IQ knowledge source can run
hybrid (keyword + vector) search out of the box.

## How it works

```text
CLI ──▶ DataGeneratorTool (prompt + post-process)
            │
            ▼
       DataGenerator (engine)
            │  Microsoft Agent Framework
            ├─▶ OpenAIChatCompletionClient ──▶ record text
            └─▶ OpenAIEmbeddingClient      ──▶ contentVector (index-ready tools)
```

- Each scenario is a `DataGeneratorTool` subclass that owns its prompt and
  post-processing logic, with zero coupling to Azure or I/O.
- The `DataGenerator` engine runs an Agent Framework `Agent` per record,
  optionally embeds the content, and persists results.

## Prerequisites

- Python 3.13 or later.
- An Azure OpenAI resource with a **chat** deployment, and (for index-ready
  scenarios) a **text embedding** deployment (for example
  `text-embedding-3-small`).
- Authentication via the Azure CLI (`az login`) or an API key.

## Install

From this folder (`tools/python`):

```bash
python -m pip install -e .
```

## Configuration

Connection settings can be passed as CLI flags or environment variables:

| Setting | CLI flag | Environment variable |
| --- | --- | --- |
| Endpoint | `--azure-openai-endpoint` | `AZURE_OPENAI_ENDPOINT` |
| Chat deployment | `--azure-openai-deployment` | `AZURE_OPENAI_DEPLOYMENT` |
| API version | `--azure-openai-api-version` | `AZURE_OPENAI_API_VERSION` |
| API key (optional) | `--azure-openai-api-key` | `AZURE_OPENAI_API_KEY` |
| Embedding deployment | `--embedding-deployment` | `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` |

When no API key is supplied the engine authenticates with `AzureCliCredential`.

## Usage

Generate a single aggregated JSON Lines file (recommended for search indexing):

```bash
python -m data_generator \
  --scenario retail-product \
  --count 100 \
  --industry supermarket \
  --output-format json \
  --out-file ../../shared/data/retail-products.jsonl
```

Generate the matching policy documents:

```bash
python -m data_generator \
  --scenario retail-policy \
  --count 20 \
  --industry supermarket \
  --output-format json \
  --out-file ../../shared/data/retail-policies.jsonl
```

Generate per-record files for any generic scenario:

```bash
python -m data_generator \
  --scenario tech-support \
  --count 50 \
  --output-format yaml \
  --out-dir ./sample-data/tech-support
```

Either `--out-dir` (per-record files) or `--out-file` (aggregated JSON Lines)
must be supplied.

## Scenarios

Index-ready (emit `contentVector`, require an embedding deployment):

| Scenario | Description |
| --- | --- |
| `retail-product` | Retail catalogue items for hybrid product search. |
| `retail-policy` | Store policies (returns, refunds, shipping, warranty). |

Generic (per-record files):

| Scenario | Description |
| --- | --- |
| `customer-support-chat-log` | Customer support chat transcripts. |
| `ecommerce-order-history` | E-commerce order histories. |
| `financial-transaction` | Financial transaction records. |
| `healthcare-clinical-policy` | Clinical policy documents. |
| `healthcare-record` | Synthetic patient records. |
| `hr-employee-record` | HR employee records. |
| `insurance-claim` | Insurance claim records. |
| `it-service-desk-ticket` | IT service-desk tickets. |
| `legal-contract` | Legal contract documents. |
| `manufacturing-maintenance-log` | Equipment maintenance logs. |
| `tech-support` | Technical support cases. |
| `tech-support-sop` | Support standard operating procedures. |
| `travel-booking` | Travel booking records. |

## Extending

Add a new scenario by creating a `DataGeneratorTool` subclass in
`src/data_generator/tools/`, importing it in that package's `__init__.py`, and
setting a unique `name`. To make it search-index-ready, override
`embedding_input` to return the text to embed; the engine handles the rest.
