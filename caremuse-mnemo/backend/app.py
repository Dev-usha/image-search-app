from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime

from memory_manager import MemoryManager
from llm_interface import LLMInterface
from medical_uploads import MedicalProcessor
from chat_logger import ChatLogger

app = FastAPI(title="CareMuse + Mnemo API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
memory_manager = MemoryManager()
llm_interface = LLMInterface()
medical_processor = MedicalProcessor()
chat_logger = ChatLogger()

# Pydantic models
class MemoryEntry(BaseModel):
    text: str
    memory_type: str = "diary"
    scope: str = "personal"
    metadata: Optional[Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    message: str
    persona: str
    user_name: Optional[str] = "User"

class ReminderEntry(BaseModel):
    text: str
    reminder_time: str
    reminder_type: str = "general"
    is_completed: bool = False

class HealthEntry(BaseModel):
    metric_type: str  # water, sleep, exercise, mood, heart_rate, blood_pressure
    value: str
    unit: Optional[str] = ""
    notes: Optional[str] = ""

class GameResult(BaseModel):
    game_type: str
    score: int
    time_taken: int
    difficulty: str = "normal"

@app.get("/")
async def root():
    return {"message": "CareMuse + Mnemo API is running"}

@app.post("/store_memory")
async def store_memory(entry: MemoryEntry):
    """Store a new memory entry"""
    try:
        memory_id = memory_manager.store_memory(
            text=entry.text,
            memory_type=entry.memory_type,
            scope=entry.scope,
            metadata=entry.metadata
        )
        return {"status": "success", "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_persona(request: ChatRequest):
    """Chat with a specific persona"""
    try:
        # Get relevant memories based on persona scope
        scope = "medical" if request.persona in ["doctor", "nurse", "therapist"] else "personal"
        relevant_memories = memory_manager.search_memories(request.message, scope=scope, limit=5)
        
        # Generate response using LLM
        response = llm_interface.generate_response(
            message=request.message,
            persona=request.persona,
            memories=relevant_memories,
            user_name=request.user_name
        )
        
        # Log the conversation
        chat_logger.log_conversation(
            persona=request.persona,
            user_message=request.message,
            ai_response=response,
            scope=scope
        )
        
        return {"response": response, "persona": request.persona}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_medical")
async def upload_medical_document(file: UploadFile = File(...)):
    """Upload and process medical documents"""
    try:
        # Process the uploaded file
        processed_data = await medical_processor.process_upload(file)
        
        # Store as medical memory
        memory_id = memory_manager.store_memory(
            text=processed_data["summary"],
            memory_type="medical_report",
            scope="medical",
            metadata={
                "filename": file.filename,
                "extracted_text": processed_data["extracted_text"],
                "file_type": processed_data["file_type"]
            }
        )
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "summary": processed_data["summary"],
            "extracted_text": processed_data["extracted_text"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_reminder")
async def add_reminder(reminder: ReminderEntry):
    """Add a new reminder"""
    try:
        memory_id = memory_manager.store_memory(
            text=f"Reminder: {reminder.text} at {reminder.reminder_time}",
            memory_type="reminder",
            scope="personal",
            metadata={
                "reminder_time": reminder.reminder_time,
                "reminder_type": reminder.reminder_type,
                "is_completed": reminder.is_completed
            }
        )
        return {"status": "success", "reminder_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log_health")
async def log_health_metric(health: HealthEntry):
    """Log health metrics"""
    try:
        memory_id = memory_manager.store_memory(
            text=f"{health.metric_type}: {health.value} {health.unit}. {health.notes}",
            memory_type="health_log",
            scope="medical",
            metadata={
                "metric_type": health.metric_type,
                "value": health.value,
                "unit": health.unit,
                "notes": health.notes
            }
        )
        return {"status": "success", "health_log_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log_game_result")
async def log_game_result(game: GameResult):
    """Log brain game results"""
    try:
        memory_id = memory_manager.store_memory(
            text=f"Completed {game.game_type} game with score {game.score} in {game.time_taken} seconds",
            memory_type="game_result",
            scope="personal",
            metadata={
                "game_type": game.game_type,
                "score": game.score,
                "time_taken": game.time_taken,
                "difficulty": game.difficulty
            }
        )
        return {"status": "success", "game_result_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_memories")
async def get_memories(
    scope: str = "personal",
    memory_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Retrieve memories with filtering"""
    try:
        memories = memory_manager.get_memories(
            scope=scope,
            memory_type=memory_type,
            limit=limit,
            offset=offset
        )
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search_memories")
async def search_memories(
    query: str,
    scope: str = "personal",
    limit: int = 10
):
    """Search memories using vector similarity"""
    try:
        memories = memory_manager.search_memories(query, scope=scope, limit=limit)
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_chat_history")
async def get_chat_history(
    persona: Optional[str] = None,
    days: int = 7,
    limit: int = 50
):
    """Get chat history with filtering"""
    try:
        history = chat_logger.get_chat_history(
            persona=persona,
            days=days,
            limit=limit
        )
        return {"chat_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_reminders")
async def get_reminders(completed: Optional[bool] = None):
    """Get reminders, optionally filtered by completion status"""
    try:
        memories = memory_manager.get_memories(
            scope="personal",
            memory_type="reminder",
            limit=100
        )
        
        if completed is not None:
            memories = [m for m in memories if m.get("metadata", {}).get("is_completed") == completed]
        
        return {"reminders": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update_reminder/{reminder_id}")
async def update_reminder(reminder_id: str, is_completed: bool):
    """Update reminder completion status"""
    try:
        success = memory_manager.update_reminder_status(reminder_id, is_completed)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_health_stats")
async def get_health_stats(metric_type: Optional[str] = None, days: int = 30):
    """Get health statistics"""
    try:
        stats = memory_manager.get_health_stats(metric_type=metric_type, days=days)
        return {"health_stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_game_stats")
async def get_game_stats(game_type: Optional[str] = None, days: int = 30):
    """Get game performance statistics"""
    try:
        stats = memory_manager.get_game_stats(game_type=game_type, days=days)
        return {"game_stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)