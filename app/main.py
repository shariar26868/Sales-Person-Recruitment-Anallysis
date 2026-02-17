from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import mongodb
from app.routes import salesperson, company, meeting, conversation

# Create FastAPI app
app = FastAPI(
    title="AI Sales Training Platform",
    description="Multi-agent AI conversation platform for sales training",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Startup & Shutdown events
# -------------------------

@app.on_event("startup")
async def startup_db():
    await mongodb.connect_db()

    # Diagnostic: log how many active meetings the API can see in the configured DB
    try:
        from app.config.database import get_meeting_collection
        active_count = await get_meeting_collection().count_documents({"status": "active"})
        print(f"🔎 Active meetings visible to API: {active_count}")
    except Exception as _:
        print("🔎 Could not query meetings on startup")

    print("🚀 AI Sales Training Platform started")

@app.on_event("shutdown")
async def shutdown_db():
    await mongodb.close_db()
    print("🛑 AI Sales Training Platform stopped")

# -------------------------
# Health checks
# -------------------------

@app.get("/")
async def root():
    return {
        "message": "AI Sales Training Platform API",
        "status": "running",
        "version": "1.0.0",
    }

@app.get("/health")
async def health_check():
    # Include active meetings count so you can verify the API is pointed at the right DB
    active_meetings = None
    try:
        from app.config.database import get_meeting_collection
        active_meetings = await get_meeting_collection().count_documents({"status": "active"})
    except Exception:
        active_meetings = None

    return {
        "status": "healthy",
        "database": "connected",
        "active_meetings": active_meetings,
    }

# -------------------------
# API Routes
# -------------------------

app.include_router(salesperson.router, prefix="/salespersons", tags=["Salesperson"])
app.include_router(company.router, prefix="/companies", tags=["Company"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meeting"])
app.include_router(conversation.router, prefix="/conversations", tags=["Conversation"])