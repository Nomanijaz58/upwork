# Upwork Proposal Bot API

Production-ready FastAPI backend for an AI-powered Upwork job assistant with Vollna and n8n integration.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your MongoDB URI and other settings

# Run server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Deploy to Render

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete deployment guide.

**Quick Steps:**
1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Set environment variables in Render dashboard
5. Deploy!

## 📋 Features

- ✅ **Vollna Integration**: Webhook endpoint for Vollna job alerts
- ✅ **n8n Workflow**: Ready for n8n automation
- ✅ **Job Search**: Dynamic filtering by budget, proposals, skills, keywords
- ✅ **AI Recommendations**: AI-powered job ranking
- ✅ **AI Proposals**: Generate custom proposals with tone/length options
- ✅ **MongoDB**: Scalable database with proper indexes
- ✅ **Real-time**: Support for real-time job updates

## 📚 Documentation

- **Deployment**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Vollna Integration**: [VOLLNA_N8N_INTEGRATION.md](backend/VOLLNA_N8N_INTEGRATION.md)
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Quick Start**: [QUICK_START_VOLLNA.md](backend/QUICK_START_VOLLNA.md)

## 🔗 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/vollna/jobs` | POST | Vollna webhook |
| `/jobs/search` | POST | Filter jobs |
| `/jobs/recommend` | POST | AI recommendations |
| `/ai/generate-proposal` | POST | Generate proposal |
| `/health` | GET | Health check |

## 🔒 Environment Variables

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=upwork_proposal_bot
N8N_SHARED_SECRET=your-secret-here
OPENAI_API_KEY=your-openai-key (optional)
LOG_LEVEL=INFO
```

## 📦 Tech Stack

- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database with Motor (async driver)
- **OpenAI**: AI-powered job ranking and proposal generation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Test Vollna webhook
curl -X POST http://localhost:8000/vollna/jobs \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: your-secret" \
  -d '{"title": "Test", "description": "Test", "url": "https://upwork.com/jobs/~test"}'
```

## 📄 License

MIT
