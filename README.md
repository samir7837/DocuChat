# DocuChat

A modern AI-powered PDF chatbot built with Django, React, and LangGraph, featuring graph-based reasoning without traditional vector databases.

## Architecture

### Backend (Django + DRF)
- **PDF Processing**: Semantic chunking using pypdf/pdfplumber without embeddings
- **LangGraph Workflow**: State-based reasoning for context selection and answer generation
- **REST APIs**: Stateless endpoints with internal state management per session

### Frontend (React + Bootstrap)
- ChatGPT-style interface with sidebar for documents and history
- Drag-and-drop PDF upload
- Streaming responses and typing indicators
- Clean black and white design

### LangGraph Workflow
```
START → Context Condenser → Question Router → Answer Generator → Safety Validator → END
                                      ↓ (not answerable)
                                   END
```

## Key Features
- **Graph-Based Reasoning**: Uses LangGraph for dynamic context selection via LLM reasoning
- **Document-Aware**: Maintains page numbers, sections, and structure
- **Hallucination Prevention**: Multi-stage validation ensures answers come only from PDFs
- **No Vector DB**: Innovative approach using message-passing and state transitions

## Tech Stack
- Django 5.2.10, Django REST Framework
- React 19.2.0, Bootstrap 5 (Black & White Theme)
- LangChain, LangGraph
- OpenRouter API (for GPT-4o-mini)
- pypdf, pdfplumber

## API Endpoints
- `POST /api/upload/` - Upload PDF files
- `POST /api/session/` - Create chat session with document IDs
- `POST /api/chat/{session_id}/` - Send message and get response

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenRouter API key (get from https://openrouter.ai/keys)

### Backend Setup
1. Navigate to backend directory: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install pypdf pdfplumber langgraph openai python-dotenv djangorestframework`
5. Create `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
6. Run migrations: `python manage.py migrate`
7. Start server: `python manage.py runserver` (runs on http://localhost:8000)

### Frontend Setup
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev` (runs on http://localhost:5177)

## Usage
1. Open http://localhost:5177 in your browser
2. Upload PDF documents using the sidebar
3. Click "Start Chat Session" to begin
4. Ask questions about your documents
5. View chat history and document list in the sidebar

## Resume Highlights
- Implemented stateful graph-based AI reasoning using LangGraph
- Built document parsing pipeline with semantic chunking
- Developed RESTful APIs with internal workflow management
- Created modern React UI with Bootstrap styling
- Integrated OpenRouter API for LLM capabilities
- Created responsive React UI with real-time chat functionality
- Ensured data integrity through multi-stage validation