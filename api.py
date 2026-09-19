from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from dotenv import dotenv_values

_env_values = dotenv_values(Path(__file__).resolve().parent / ".env")
for key, value in (_env_values or {}).items():
    if value is not None and key not in os.environ:
        os.environ[key] = value

from Agents.orchestrator import orchestrator_agent
from Agents.ingestion import ingestion_agent
from Agents.domain_config import DOMAIN_REGISTRY
from Agents.domain_intelligence import run_domain_action
from Agents.domain_dashboard import run_domain_dashboard
from rag import list_document_records


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


class DomainActionRequest(BaseModel):
    domain: str
    action: str


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
        raise HTTPException(status_code=400, detail="No file provided.")


    # -----------------------------------------------------
    # Check file type
    # -----------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    supported_extensions = {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg", ".webp"}

    if extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. Supported: PDF, TXT, DOCX, "
                "PNG, JPG, JPEG and WEBP. Legacy .doc files are not supported."
            ),
        )

    if domain and domain not in DOMAIN_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown NEXUS domain: {domain}")


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
            source_name=file.filename,
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
                "document_id": result.get("document_id"),
                "chunk_count": result.get("chunk_count", 0),
                "lifecycle": ["Uploading", "Processing"] +
                    (["OCR"] if result.get("ocr") else []) +
                    ["Embedding", "Indexed", "Ready"],
            }


        # -------------------------------------------------
        # Failed ingestion
        # -------------------------------------------------

        else:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": result.get("message", "Document ingestion failed."),
                    "filename": file.filename,
                    "agent": "ingestion",
                    "status": "failed",
                    "domain": domain or "General",
                },
            )


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


# =========================================================
# DOCUMENT LIBRARY
# =========================================================

@app.get("/documents")
def documents(domain: str | None = None):
    if domain and domain not in DOMAIN_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown NEXUS domain: {domain}")

    try:
        records = list_document_records(domain=domain)
        return {
            "documents": records,
            "domain": domain or "General",
            "count": len(records),
        }
    except Exception as e:
        print("\n========== DOCUMENT LIBRARY ERROR ==========")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("============================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load document library: {str(e)}",
        )


# =========================================================
# DOMAIN INTELLIGENCE ACTIONS
# =========================================================

@app.post("/domain-dashboard")
def domain_dashboard(domain: str):
    if domain not in DOMAIN_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown NEXUS domain: {domain}")
    try:
        return {"dashboard": run_domain_dashboard(domain)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print("\n========== DOMAIN DASHBOARD ERROR ==========")
        print("Error type:", type(exc).__name__)
        print("Error:", str(exc))
        print("============================================\n")
        raise HTTPException(status_code=500, detail=f"Domain dashboard failed: {str(exc)}")


@app.post("/domain-action")
def domain_action(request: DomainActionRequest):
    if request.domain not in DOMAIN_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown NEXUS domain: {request.domain}")
    try:
        return {"response": run_domain_action(request.domain, request.action)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print("\\n========== DOMAIN ACTION ERROR ==========")
        print("Error type:", type(exc).__name__)
        print("Error:", str(exc))
        print("=========================================\\n")
        raise HTTPException(status_code=500, detail=f"Domain action failed: {str(exc)}")
