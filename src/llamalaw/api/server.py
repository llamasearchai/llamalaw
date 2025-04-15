"""
FastAPI server for LlamaLaw
"""

import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from llamalaw.analysis.analyzer import ContractAnalyzer
from llamalaw.models.analysis import AnalysisResult
from llamalaw.models.contract import Clause, Contract, Party, Risk
from llamalaw.storage.repository import ContractRepository

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llamalaw.api")

# Create FastAPI app
app = FastAPI(
    title="LlamaLaw API",
    description="Legal contract analysis and management API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define API models
class AnalyzeRequest(BaseModel):
    """Request data for analyzing a contract"""

    save_to_repository: bool = Field(
        False, description="Whether to save results to repository"
    )


class ContractSummary(BaseModel):
    """Summary information for a contract"""

    id: str = Field(..., description="Contract ID")
    title: str = Field(..., description="Contract title")
    document_type: str = Field(..., description="Type of legal document")
    parties: List[str] = Field(..., description="Names of parties involved")
    effective_date: Optional[str] = Field(None, description="Effective date")
    risk_count: int = Field(..., description="Number of identified risks")
    clause_count: int = Field(..., description="Number of extracted clauses")


class RiskSummary(BaseModel):
    """Summary information for a risk"""

    id: str = Field(..., description="Risk ID")
    description: str = Field(..., description="Risk description")
    severity: str = Field(..., description="Risk severity level")
    category: str = Field(..., description="Risk category")
    recommendation: str = Field(..., description="Recommendation to mitigate risk")


class ErrorResponse(BaseModel):
    """Error response data"""

    detail: str = Field(..., description="Error message")


# Initialize analyzer and repository globally
analyzer = ContractAnalyzer()
repository = ContractRepository()


# API endpoints
@app.get("/", response_model=Dict[str, str])
def root():
    """API root endpoint"""
    return {
        "name": "LlamaLaw API",
        "version": "0.1.0",
        "description": "Legal contract analysis and management API",
    }


@app.post(
    "/analyze", response_model=Union[AnalysisResult, ErrorResponse], status_code=200
)
async def analyze_contract(
    background_tasks: BackgroundTasks,
    save_to_repository: bool = False,
    file: UploadFile = File(...),
):
    """
    Analyze a contract document

    Upload a contract document to analyze its content and extract information.
    Supported file formats: PDF, DOCX, TXT
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported formats: PDF, DOCX, TXT",
        )

    try:
        # Save uploaded file to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # Analyze document
        result = analyzer.analyze(temp_file_path)

        # Set original filename
        result.contract.filename = file.filename

        # Save to repository if requested
        if save_to_repository:
            # Save in background to not block the response
            background_tasks.add_task(repository.add, result)

        # Clean up temporary file
        background_tasks.add_task(os.unlink, temp_file_path)

        return result

    except Exception as e:
        logger.exception(f"Error analyzing contract: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error analyzing contract: {str(e)}"
        )


@app.get("/contracts", response_model=List[ContractSummary])
def list_contracts(
    document_type: Optional[str] = Query(None, description="Filter by document type")
):
    """
    List contracts in repository

    Returns a list of contract summaries, optionally filtered by document type.
    """
    try:
        contracts = repository.list(document_type)

        # Convert to contract summaries
        summaries = []
        for contract in contracts:
            summaries.append(
                ContractSummary(
                    id=contract.id,
                    title=contract.title,
                    document_type=contract.document_type,
                    parties=[p.name for p in contract.parties],
                    effective_date=contract.dates.effective,
                    risk_count=len(contract.risks),
                    clause_count=len(contract.clauses),
                )
            )

        return summaries

    except Exception as e:
        logger.exception(f"Error listing contracts: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error listing contracts: {str(e)}"
        )


@app.get("/contracts/{contract_id}", response_model=Contract)
def get_contract(contract_id: str = Path(..., description="Contract ID")):
    """
    Get a contract by ID

    Returns the full contract data for the specified ID.
    """
    try:
        contract = repository.get(contract_id)

        if not contract:
            raise HTTPException(
                status_code=404, detail=f"Contract with ID '{contract_id}' not found"
            )

        return contract

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting contract: {str(e)}")


@app.get("/contracts/{contract_id}/text", response_model=Dict[str, str])
def get_contract_text(contract_id: str = Path(..., description="Contract ID")):
    """
    Get the original document text for a contract

    Returns the raw text content of the contract document.
    """
    try:
        # Check if contract exists
        contract = repository.get(contract_id)
        if not contract:
            raise HTTPException(
                status_code=404, detail=f"Contract with ID '{contract_id}' not found"
            )

        # Get document text
        text = repository.get_document_text(contract_id)

        if text is None:
            raise HTTPException(
                status_code=404,
                detail=f"Document text not found for contract '{contract_id}'",
            )

        return {"text": text}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract text: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting contract text: {str(e)}"
        )


@app.get("/contracts/{contract_id}/risks", response_model=List[RiskSummary])
def get_contract_risks(
    contract_id: str = Path(..., description="Contract ID"),
    severity: Optional[str] = Query(None, description="Filter by risk severity"),
    category: Optional[str] = Query(None, description="Filter by risk category"),
):
    """
    Get risks for a contract

    Returns risks identified in the contract, optionally filtered by severity or category.
    """
    try:
        # Get contract
        contract = repository.get(contract_id)

        if not contract:
            raise HTTPException(
                status_code=404, detail=f"Contract with ID '{contract_id}' not found"
            )

        # Apply filters
        risks = contract.risks

        if severity:
            risks = [r for r in risks if r.severity == severity]

        if category:
            risks = [r for r in risks if r.category == category]

        # Convert to risk summaries
        summaries = []
        for risk in risks:
            summaries.append(
                RiskSummary(
                    id=risk.id,
                    description=risk.description,
                    severity=risk.severity,
                    category=risk.category,
                    recommendation=risk.recommendation,
                )
            )

        return summaries

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract risks: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting contract risks: {str(e)}"
        )


@app.get("/contracts/{contract_id}/clauses", response_model=List[Clause])
def get_contract_clauses(
    contract_id: str = Path(..., description="Contract ID"),
    clause_type: Optional[str] = Query(None, description="Filter by clause type"),
):
    """
    Get clauses from a contract

    Returns clauses extracted from the contract, optionally filtered by type.
    """
    try:
        # Get contract
        contract = repository.get(contract_id)

        if not contract:
            raise HTTPException(
                status_code=404, detail=f"Contract with ID '{contract_id}' not found"
            )

        # Apply filter
        clauses = contract.clauses

        if clause_type:
            clauses = [c for c in clauses if c.type == clause_type]

        return clauses

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract clauses: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting contract clauses: {str(e)}"
        )


@app.delete("/contracts/{contract_id}", response_model=Dict[str, bool])
def delete_contract(contract_id: str = Path(..., description="Contract ID")):
    """
    Delete a contract by ID

    Deletes a contract and all associated data from the repository.
    """
    try:
        # Check if contract exists
        contract = repository.get(contract_id)
        if not contract:
            raise HTTPException(
                status_code=404, detail=f"Contract with ID '{contract_id}' not found"
            )

        # Delete contract
        success = repository.delete(contract_id)

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete contract '{contract_id}'"
            )

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting contract: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting contract: {str(e)}"
        )


@app.get("/search", response_model=List[ContractSummary])
def search_contracts(query: str = Query(..., description="Search query")):
    """
    Search for contracts

    Searches for contracts by title, parties, or content.
    """
    try:
        contracts = repository.search(query)

        # Convert to contract summaries
        summaries = []
        for contract in contracts:
            summaries.append(
                ContractSummary(
                    id=contract.id,
                    title=contract.title,
                    document_type=contract.document_type,
                    parties=[p.name for p in contract.parties],
                    effective_date=contract.dates.effective,
                    risk_count=len(contract.risks),
                    clause_count=len(contract.clauses),
                )
            )

        return summaries

    except Exception as e:
        logger.exception(f"Error searching contracts: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error searching contracts: {str(e)}"
        )


@app.get("/stats", response_model=Dict[str, Any])
def get_stats():
    """
    Get repository statistics

    Returns statistics about the contract repository.
    """
    try:
        stats = repository.get_stats()

        # Convert datetime objects to strings for JSON serialization
        for key, value in stats.items():
            if hasattr(value, "isoformat"):
                stats[key] = value.isoformat()

        return stats

    except Exception as e:
        logger.exception(f"Error getting repository statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting statistics: {str(e)}"
        )


def run_server(host="0.0.0.0", port=8000, debug=False):
    """
    Run the API server

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Whether to run in debug mode
    """
    import uvicorn

    uvicorn.run("llamalaw.api.server:app", host=host, port=port, reload=debug)


if __name__ == "__main__":
    run_server(debug=True)
