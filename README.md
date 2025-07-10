# Dynamic Agentic System

A comprehensive multi-agent system for document processing, mathematical computation, and database querying using FastAPI, LangGraph, and LangChain.

## Features

- **Multi-Agent Orchestration**: Uses LangGraph to route queries between different specialized agents
- **Document RAG**: Pinecone vector store for document retrieval and search
- **Math Computation**: Pandas-based mathematical and statistical analysis
- **SQL Query Engine**: DuckDB integration for database operations
- **PDF Processing**: PyMuPDF and OCR for document text extraction
- **Persona System**: Financial, Legal, and General Assistant personas
- **Suggested Queries**: AI-powered follow-up question generation
- **FastAPI Backend**: RESTful API with automatic documentation

## Project Structure

```
dynamic_agentic_system/
├── agents/                 # Agent personas and management
│   ├── __init__.py
│   └── personas.py        # Financial, Legal, General personas
├── rag/                   # Retrieval-Augmented Generation
│   ├── __init__.py
│   └── document_store.py  # Pinecone vector store integration
├── math/                  # Mathematical computations
│   ├── __init__.py
│   ├── computation.py     # Pandas-based calculations
│   └── sql_query.py       # DuckDB database operations
├── ocr/                   # PDF processing and OCR
│   ├── __init__.py
│   └── pdf_processor.py   # PyMuPDF and Tesseract integration
├── router/                # Agent orchestration
│   ├── __init__.py
│   ├── agent_router.py    # LangGraph workflow
│   └── suggested_queries.py # Follow-up query generation
├── api/                   # FastAPI application
│   ├── __init__.py
│   └── main.py           # Main API endpoints
├── data/                  # Data storage
│   ├── docs/             # Uploaded PDF documents
│   └── stocks/           # Stock data files
├── config.py             # Configuration and environment variables
├── requirements.txt      # Python dependencies
├── env_example.txt       # Environment variables template
└── README.md            # This file
```

## Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and environment
- Tesseract OCR (optional, for enhanced PDF processing)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dynamic_agentic_system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys and configuration
   ```

5. **Install Tesseract OCR** (optional):
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

## Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=dynamic-agentic-system

# Database Configuration
DATABASE_URL=sqlite:///./data/system.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# OCR Configuration
TESSERACT_CMD_PATH=/usr/bin/tesseract

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=./data/docs
```

## Usage

### Starting the Server

```bash
cd api
python main.py
```

The server will start at `http://localhost:8000`

### API Endpoints

#### 1. Process Query
```bash
POST /query
Content-Type: application/json

{
  "query": "What are the key findings in the uploaded documents?",
  "persona_type": "financial",
  "context": "Additional context if needed"
}
```

#### 2. Upload PDF
```bash
POST /upload
Content-Type: multipart/form-data

file: [PDF file]
```

#### 3. Get Available Personas
```bash
GET /personas
```

#### 4. System Status
```bash
GET /status
```

#### 5. Document Statistics
```bash
GET /documents/stats
```

#### 6. Database Tables
```bash
GET /database/tables
```

### Example Usage

#### Financial Analysis Query
```python
import requests

# Query with financial persona
response = requests.post("http://localhost:8000/query", json={
    "query": "Analyze the stock performance data and calculate the average return",
    "persona_type": "financial"
})

print(response.json())
```

#### Document Upload and Query
```python
# Upload PDF
with open("document.pdf", "rb") as f:
    files = {"file": f}
    upload_response = requests.post("http://localhost:8000/upload", files=files)

# Query the uploaded document
query_response = requests.post("http://localhost:8000/query", json={
    "query": "What are the main points in the uploaded document?",
    "persona_type": "general"
})
```

## Agent Personas

### Financial Advisor
- Stock market analysis and investment strategies
- Financial planning and portfolio management
- Economic trends and market indicators
- Risk assessment and mitigation

### Legal Advisor
- Contract law and legal document analysis
- Corporate law and business regulations
- Intellectual property and compliance
- Risk assessment and legal implications

### General Assistant
- General knowledge and research
- Problem-solving and analysis
- Writing and communication
- Technology and tools

## Workflow

1. **Query Classification**: The system analyzes the query to determine the appropriate processing path
2. **Document Search**: Searches uploaded PDFs using vector similarity
3. **Math Computation**: Performs mathematical calculations and statistical analysis
4. **Database Query**: Executes SQL queries on available data
5. **Response Generation**: Uses the selected persona to generate a comprehensive response
6. **Query Suggestions**: Generates relevant follow-up questions

## Development

### Adding New Personas

1. Create a new persona class in `agents/personas.py`
2. Add it to the `PersonaManager` class
3. Update the `PersonaType` enum

### Adding New Computation Types

1. Extend the `MathComputation` class in `math/computation.py`
2. Add new patterns to the query classification in `router/agent_router.py`

### Adding New Database Operations

1. Extend the `SQLQueryEngine` class in `math/sql_query.py`
2. Add new table schemas and sample data

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required API keys are set in the `.env` file
2. **Pinecone Index**: The system will create the Pinecone index automatically on first run
3. **Tesseract OCR**: If OCR fails, check the Tesseract installation path in the configuration
4. **File Upload**: Ensure the upload directory exists and has proper permissions

### Logs

Check the console output for detailed error messages and system status information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository. 