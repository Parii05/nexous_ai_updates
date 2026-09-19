from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import tempfile
import os

from Agents.orchestrator import orchestrator_agent
from Agents.ingestion import ingestion_agent


# =========================================================
# NEXUS API
# =========================================================

app = FastAPI(
    title="NEXUS API",
    description="Enterprise AI Intelligence Platform",
    version="1.0.0",
)


# =========================================================
# REQUEST MODEL
# =========================================================

class QueryRequest(BaseModel):
    query: str
    domain: str | None = None
    capability: str | None = None


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "NEXUS API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# =========================================================
# ASK NEXUS
# =========================================================

@app.post("/ask")
def ask_nexus(request: QueryRequest):

    query = request.query.strip()

    # -----------------------------------------------------
    # Empty question
    # -----------------------------------------------------

    if not query:
        return {
            "response": {
                "answer": "Please enter a question.",
                "agent": "orchestrator",
                "domain": request.domain,
                "capability": request.capability,
                "path": "orchestrator",
                "citations": [],
                "confidence": 0.0,
            }
        }

    # -----------------------------------------------------
    # Send question to Orchestrator
    # -----------------------------------------------------

    try:

        result = orchestrator_agent(
            question=query,
            selected_domain=request.domain,
            capability=request.capability,
        )

        return {
            "response": result
        }

    # -----------------------------------------------------
    # DEBUGGING ERROR
    # -----------------------------------------------------

    except Exception as e:

        print("\n========== NEXUS ERROR ==========")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("=================================\n")

        return {
            "response": {
                "answer": (
                    f"NEXUS backend error: "
                    f"{type(e).__name__}: {str(e)}"
                ),
                "agent": "orchestrator",
                "domain": request.domain,
                "capability": request.capability,
                "path": "error",
                "citations": [],
                "confidence": 0.0,
                "error": str(e),
            }
        }


# =========================================================
# DOCUMENT INGESTION
# =========================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    domain: str | None = Form(default=None),
):

    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:

        return {
            "detail": "No file provided."
        }


    # -----------------------------------------------------
    # Check file type
    # -----------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    supported_extensions = {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg", ".webp"}

    if extension not in supported_extensions:
        return {
            "detail": (
                "Unsupported file type. Supported: PDF, TXT, DOCX, "
                "PNG, JPG, JPEG and WEBP."
            )
        }


    temp_path = None


    try:

        # -------------------------------------------------
        # Save uploaded PDF temporarily
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name


        # -------------------------------------------------
        # Send document to Ingestion Agent
        # -------------------------------------------------

        result = ingestion_agent(
            temp_path,
            domain=domain,
        )


        # -------------------------------------------------
        # Successful ingestion
        # -------------------------------------------------

        if result.get("success"):

            return {
                "message": "Document successfully indexed.",
                "filename": file.filename,
                "agent": "ingestion",
                "status": "indexed",
                "domain": domain or "General",
                "ocr": extension in {".png", ".jpg", ".jpeg", ".webp"},
            }


        # -------------------------------------------------
        # Failed ingestion
        # -------------------------------------------------

        else:

            return {
                "detail": result.get(
                    "message",
                    "Document ingestion failed.",
                ),
                "filename": file.filename,
                "agent": "ingestion",
                "status": "failed",
            }


    # -----------------------------------------------------
    # Upload error
    # -----------------------------------------------------

    except Exception as e:

        print("\n========== INGESTION ERROR ==========")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("=====================================\n")

        return {
            "detail": str(e),
            "filename": file.filename,
            "agent": "ingestion",
            "status": "failed",
        }


    # -----------------------------------------------------
    # Always remove temporary file
    # -----------------------------------------------------

    finally:

        if temp_path and os.path.exists(temp_path):

            try:

                os.remove(temp_path)

            except OSError:

                pass