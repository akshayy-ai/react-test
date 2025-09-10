from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from document_processor import DocumentProcessor
from rag_system import RAGSystem
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
load_dotenv()

app = FastAPI(title="RAG Document QA System", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
doc_processor = DocumentProcessor()
rag_system = RAGSystem()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "RAG Document QA System is running!"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt', '.md')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save uploaded file
        file_content = await file.read()
        file_path = doc_processor.save_uploaded_file(file_content, file.filename)
        
        # Process document
        documents = doc_processor.load_document(file_path)
        vectorstore = doc_processor.process_documents(documents)
        
        # Set vector store in RAG system
        rag_system.set_vectorstore(vectorstore)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return {
            "message": f"Document '{file.filename}' uploaded and processed successfully",
            "document_chunks": len(documents),
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about the uploaded document"""
    try:
        result = rag_system.ask_question(request.question)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
