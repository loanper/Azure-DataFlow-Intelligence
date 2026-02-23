# Azure DataFlow Intelligence

> Automated PDF document processing pipeline using **Azure Functions**, **Azure Blob Storage**, and **Azure Document Intelligence**.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Azure Functions](https://img.shields.io/badge/Azure%20Functions-Serverless-0062AD?logo=azure-functions&logoColor=white)
![Azure Blob Storage](https://img.shields.io/badge/Azure%20Blob%20Storage-Cloud-0078D4?logo=microsoft-azure&logoColor=white)
![Document Intelligence](https://img.shields.io/badge/Document%20Intelligence-AI-FF6F00?logo=microsoft-azure&logoColor=white)

---

## Overview

This project implements a **serverless data processing pipeline** that automatically extracts tabular data from PDF documents using Azure's cognitive services.

When a PDF is uploaded to an Azure Blob Storage **input** container, an Azure Function is triggered. It sends the document to Azure Document Intelligence for layout analysis, parses the extracted table data, converts it into a structured `.csv` file, and uploads the result to an **output** container — all without any manual intervention.

### Architecture

```
┌──────────────┐       ┌──────────────────┐       ┌─────────────────────────┐
│  PDF Upload  │──────▶│  Azure Blob      │──────▶│  Azure Function         │
│  (input/)    │       │  Storage Trigger  │       │  (Blob Trigger)         │
└──────────────┘       └──────────────────┘       └───────────┬─────────────┘
                                                              │
                                                              ▼
                                                  ┌─────────────────────────┐
                                                  │  Azure Document         │
                                                  │  Intelligence API       │
                                                  │  (Layout Analysis)      │
                                                  └───────────┬─────────────┘
                                                              │
                                                              ▼
                                                  ┌─────────────────────────┐
                                                  │  Parse tables ──▶ CSV   │
                                                  │  Upload to output/      │
                                                  └─────────────────────────┘
```

## Features

- **Serverless** — No infrastructure to manage; Azure Functions scales automatically.
- **Event-driven** — Processing starts instantly when a new PDF is uploaded.
- **AI-powered extraction** — Leverages Azure Document Intelligence (Form Recognizer v2.1) to detect and extract table layouts.
- **Structured output** — Converts raw document data into clean `.csv` files ready for analytics or Power BI.

## Tech Stack

| Component | Technology |
|---|---|
| Runtime | Python 3.9+ |
| Compute | Azure Functions (Blob Trigger) |
| Storage | Azure Blob Storage (input/output containers) |
| AI Service | Azure Document Intelligence (Layout API v2.1) |
| Data Processing | Pandas, NumPy |

## Project Structure

```
.
├── function_app.py              # Main Azure Function (Blob Trigger + processing logic)
├── host.json                    # Azure Functions host configuration
├── local.settings.json.example  # Template for local settings (fill in your keys)
├── requirements.txt             # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Azure Functions Core Tools** (v4)
- An **Azure subscription** with the following resources:
  - Azure Storage Account (with `input` and `output` blob containers)
  - Azure Document Intelligence resource

### Setup

1. **Clone the repository**

   ```bash
   git clone git@github.com:loanper/Azure-DataFlow-Intelligence.git
   cd Azure-DataFlow-Intelligence
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example settings file and fill in your Azure credentials:

   ```bash
   cp local.settings.json.example local.settings.json
   ```

   Then edit `local.settings.json` with your own values:
   - `AzureWebJobsStorage` — your Storage Account connection string
   - `storageaccountloan_STORAGE` — same connection string (used by the blob trigger)
   - `DOCUMENT_INTELLIGENCE_ENDPOINT` — your Document Intelligence endpoint URL
   - `DOCUMENT_INTELLIGENCE_KEY` — your Document Intelligence API key

5. **Run locally**

   ```bash
   func start
   ```

6. **Test** — Upload a PDF to the `input` container using [Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/). The function will process it and output a `.csv` file in the `output` container.

## How It Works

1. A PDF file is uploaded to the `input` blob container.
2. The **Blob Trigger** fires and reads the PDF content.
3. The function sends the PDF to the **Azure Document Intelligence Layout API**.
4. After analysis, the response containing detected tables is parsed.
5. Table data is converted into a **Pandas DataFrame** and exported as `.csv`.
6. The resulting `.csv` is uploaded to the `output` blob container.

## Security

- All secrets (API keys, connection strings) are stored in `local.settings.json`, which is **excluded from version control** via `.gitignore`.
- A `local.settings.json.example` template is provided for reference.
- For production deployments, consider using [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/) to manage secrets securely.

## License

This project is for educational purposes (ECE Paris — M1 Engineering, Cloud Computing module).

---

*Built with Azure cloud services as part of a hands-on cloud computing lab.*
