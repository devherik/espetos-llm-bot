# Espetos LLM Bot

A sophisticated LLM-powered chatbot built with FastAPI, Google Gemini AI, and ChromaDB for intelligent conversational experiences.

## 🚀 Features

- **AI-Powered Conversations**: Leverages Google Gemini AI for natural language processing
- **Vector Database**: Uses ChromaDB for efficient similarity search and document retrieval
- **REST API**: Built with FastAPI for high-performance API endpoints
- **Modular Architecture**: Organized into distinct modules for scalability:
  - `oracle/` - Core API and AI orchestration
  - `agent/` - AI agent logic and behaviors
  - `messanger/` - Message handling and communication
  - `data_ingest/` - Data processing and ingestion pipeline

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **AI Model**: Google Gemini AI
- **Vector Database**: ChromaDB
- **SQL Database**: MariaDB with SQLAlchemy ORM
- **Language**: Python 3.12+
- **Package Manager**: UV
- **Additional Libraries**: Agno, Pydantic, Uvicorn, MariaDB Connector

## 📋 Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip
- Google Gemini API key
- MariaDB server (for data ingestion)
- MariaDB Connector/C development libraries

### System Dependencies

Install the required system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y libmariadb-dev pkg-config
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install mariadb-devel pkgconfig
# or for newer versions
sudo dnf install mariadb-devel pkgconfig
```

**macOS:**
```bash
brew install mariadb-connector-c pkg-config
```

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/devherik/espetos-llm-bot.git
   cd espetos-llm-bot
   ```

2. **Install dependencies**
   
   Using UV (recommended):
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Usage

### Running the Application

1. **Start the main application**
   ```bash
   python main.py
   ```

2. **Start the Oracle API server**
   ```bash
   cd oracle
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API documentation**
   - Open your browser and go to `http://localhost:8000/docs`
   - Interactive API documentation will be available via Swagger UI

### API Endpoints

- `GET /` - Welcome endpoint and health check
- Additional endpoints will be documented as they are implemented

## 📁 Project Structure

```
espetos-llm-bot/
├── main.py              # Main application entry point
├── pyproject.toml       # Project configuration and dependencies
├── requirements.txt     # Python dependencies
├── uv.lock             # UV lock file
├── .env                # Environment variables (not in repo)
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── agent/              # AI agent logic and behaviors
├── data_ingest/        # Data processing and ingestion
├── messenger/          # Message handling and communication
└── oracle/             # Core API and AI orchestration
    ├── __init__.py
    └── main.py         # FastAPI application
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |

## 🧪 Development

### Setting up development environment

1. **Install development dependencies**
   ```bash
   uv sync --dev
   ```

2. **Run tests** (when implemented)
   ```bash
   pytest
   ```

3. **Code formatting and linting** (when configured)
   ```bash
   black .
   flake8 .
   ```

## 📝 API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛟 Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/devherik/espetos-llm-bot/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the issue

## 🙏 Acknowledgments

- Google Gemini AI for providing the language model
- FastAPI team for the excellent web framework
- ChromaDB team for the vector database solution

---

**Note**: This project is currently in development. Features and documentation will be updated as the project evolves.