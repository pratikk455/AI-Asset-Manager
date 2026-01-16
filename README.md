# AI Asset Manager

An intelligent investment management platform powered by AI agents that provides comprehensive portfolio analysis, risk assessment, and investment research capabilities.

## 🌟 Features

### 📊 Portfolio Management
- **Position Monitoring**: Real-time tracking of portfolio positions and performance
- **Rebalancing Agent**: Automated portfolio rebalancing recommendations
- **Portfolio Manager**: Comprehensive portfolio oversight and optimization

### 🔍 Research & Analysis
- **Fundamentals Agent**: Deep dive into company financials and metrics
- **Valuation Agent**: Advanced valuation models and fair price estimates
- **Moat Analysis**: Competitive advantage and business moat evaluation
- **Sentiment Analysis**: Market sentiment tracking and news analysis
- **Thesis Writer**: AI-generated investment theses
- **Screener**: Custom stock screening based on multiple criteria

### 🎯 Discovery & Scouting
- **Thematic Scout**: Identify emerging themes and trends
- **Disruption Scout**: Spot disruptive companies and technologies
- **Smart Money Scout**: Track institutional investor movements
- **Emerging Leaders**: Discover up-and-coming market leaders

### ⚠️ Risk Management
- **VaR Calculation**: Value at Risk analysis
- **Monte Carlo Simulation**: Probabilistic portfolio outcome modeling
- **Stress Testing**: Portfolio resilience under various market scenarios
- **Correlation Analysis**: Inter-asset correlation tracking

### 📈 Performance Analytics
- **Attribution Analysis**: Performance attribution and breakdown
- **Benchmark Tracking**: Compare performance against market benchmarks

### 💬 Conversational AI
- **Intent Interpreter**: Natural language understanding for investment queries
- **Chat Interface**: Interactive conversations about your portfolio

## 🏗️ Architecture

### Backend (`/backend`)
- **FastAPI** REST API with modular route structure
- **Agent-based architecture** for specialized investment tasks
- **MongoDB** for data persistence
- **Google Gemini** for AI-powered analysis
- **Celery** for scheduled tasks and background jobs

### Frontend (`/frontend`)
- **Next.js** with TypeScript
- Modern React components
- Responsive design with Tailwind CSS

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB
- Google Gemini API Key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file with:
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=your_mongodb_connection_string
```

4. Start the server:
```bash
./start_server.sh
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📡 API Endpoints

- `/api/analyze` - Stock and portfolio analysis
- `/api/chat` - Conversational AI interface
- `/api/discover` - Discovery and scouting operations
- `/api/portfolio` - Portfolio management
- `/api/risk` - Risk assessment and reporting
- `/api/funds` - Fund information and tracking

## 🧪 Testing

Run the test suites:

```bash
# Test Gemini integration
python backend/test_gemini.py

# Test analysis pipeline
python backend/test_analysis.py

# Test portfolio operations
python backend/test_portfolio.py

# Test full workflow
python backend/test_full_flow.py
```

## 🗂️ Project Structure

```
.
├── backend/
│   ├── agents/          # AI agent implementations
│   │   ├── conversation/
│   │   ├── performance/
│   │   ├── portfolio/
│   │   ├── research/
│   │   ├── risk/
│   │   └── scouts/
│   ├── api/            # FastAPI application
│   │   └── routes/
│   ├── config/         # Configuration
│   ├── database/       # Database connections
│   ├── llm/           # LLM client integrations
│   ├── models/        # Data models
│   ├── orchestrator/  # Pipeline orchestration
│   └── scheduler/     # Background jobs
└── frontend/
    └── src/
        ├── app/       # Next.js pages
        ├── components/
        ├── lib/
        └── types/
```

## 🤖 Agent System

The platform uses specialized AI agents for different tasks:

- **Base Agent**: Foundation class with common LLM interactions
- **Research Agents**: Fundamental analysis, valuation, sentiment
- **Portfolio Agents**: Position monitoring, rebalancing, PM decisions
- **Risk Agents**: VaR, Monte Carlo, stress testing, correlation
- **Scout Agents**: Thematic trends, disruption, smart money tracking
- **Performance Agents**: Attribution analysis, benchmark tracking
- **Conversation Agents**: Intent interpretation and chat

## 🔄 Orchestration Pipelines

- **Analysis Pipeline**: Coordinates comprehensive stock analysis
- **Risk Pipeline**: Runs full risk assessment workflows
- **Scout Pipeline**: Executes discovery and screening operations

## 📅 Scheduled Jobs

- **Daily Jobs**: Position monitoring, sentiment updates, alert checks
- **Weekly Jobs**: Portfolio rebalancing, performance reports, risk assessments

## 🛠️ Technologies Used

**Backend:**
- FastAPI
- Google Gemini AI
- MongoDB
- Celery
- yfinance
- pandas, numpy

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

## 📝 License

This project is private and proprietary.

## 👤 Author

**Pratik Shrestha**
- GitHub: [@pratikk455](https://github.com/pratikk455)

## 🤝 Contributing

This is a private project. Contributions are by invitation only.

---

Built with ❤️ for intelligent investing
