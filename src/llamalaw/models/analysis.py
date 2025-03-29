"""
Analysis result data models
"""
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from llamalaw.models.contract import Contract, Clause, Risk


class ExtractionResult(BaseModel):
    """Results of information extraction from a document"""
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    clauses: List[Clause] = Field(..., description="Extracted clauses")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RiskAssessmentResult(BaseModel):
    """Results of risk assessment for a document"""
    risks: List[Risk] = Field(..., description="Identified risks")
    risk_score: Optional[float] = Field(None, description="Overall risk score")
    risk_categories: Dict[str, int] = Field(default_factory=dict, description="Risk counts by category")
    risk_severity: Dict[str, int] = Field(default_factory=dict, description="Risk counts by severity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalysisResult(BaseModel):
    """Complete results of contract analysis"""
    contract: Contract = Field(..., description="Contract with extracted information")
    document_type: str = Field(..., description="Type of legal document")
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    clauses: List[Clause] = Field(..., description="Extracted clauses")
    risks: List[Risk] = Field(..., description="Identified risks")
    raw_text: str = Field(..., description="Original document text")
    processed_text: str = Field(..., description="Preprocessed document text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def generate_summary(self) -> str:
        """
        Generate a plain language summary of the contract.
        
        Returns:
            str: Summary of the contract
        """
        # This would typically call a summarization model
        # For now, return a placeholder
        parties_str = ", ".join(p.name for p in self.contract.parties)
        
        # Extract effective date if available
        date_str = ""
        if self.contract.dates.effective:
            date_str = f" dated {self.contract.dates.effective}"
        
        # Count risks by severity
        risk_severity_counts = {}
        for risk in self.risks:
            severity = risk.severity.value
            risk_severity_counts[severity] = risk_severity_counts.get(severity, 0) + 1
        
        risks_str = ", ".join(f"{count} {sev}" for sev, count in risk_severity_counts.items())
        
        summary = (
            f"This is a {self.document_type}{date_str} between {parties_str}. "
            f"It contains {len(self.clauses)} clauses and {len(self.risks)} potential "
            f"risks ({risks_str})."
        )
        
        return summary 