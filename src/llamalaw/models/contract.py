"""
Contract data models
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """Risk severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Risk(BaseModel):
    """Risk identified in a contract"""

    id: str = Field(..., description="Unique identifier for the risk")
    type: str = Field(..., description="Type of risk")
    description: str = Field(..., description="Description of the risk")
    severity: RiskSeverity = Field(
        default=RiskSeverity.MEDIUM, description="Severity level"
    )
    clause_id: Optional[str] = Field(
        None, description="ID of the clause containing the risk"
    )
    section: Optional[str] = Field(None, description="Section containing the risk")
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for mitigation"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Party(BaseModel):
    """Party to a contract"""

    name: str = Field(..., description="Name of the party")
    type: Optional[str] = Field(
        None, description="Type of party (individual, company, etc.)"
    )
    address: Optional[str] = Field(None, description="Address of the party")
    contact_info: Optional[str] = Field(None, description="Contact information")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Clause(BaseModel):
    """Clause in a contract"""

    id: str = Field(..., description="Unique identifier for the clause")
    title: Optional[str] = Field(None, description="Title or name of the clause")
    type: str = Field(..., description="Type of clause")
    text: str = Field(..., description="Full text of the clause")
    section: Optional[str] = Field(None, description="Section containing the clause")
    page: Optional[int] = Field(None, description="Page number containing the clause")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Obligation(BaseModel):
    """Obligation specified in a contract"""

    id: str = Field(..., description="Unique identifier for the obligation")
    description: str = Field(..., description="Description of the obligation")
    clause_id: str = Field(
        ..., description="ID of the clause containing the obligation"
    )
    responsible_party: Optional[str] = Field(
        None, description="Party responsible for the obligation"
    )
    beneficiary_party: Optional[str] = Field(
        None, description="Party benefiting from the obligation"
    )
    deadline: Optional[Union[date, str]] = Field(
        None, description="Deadline for the obligation"
    )
    condition: Optional[str] = Field(None, description="Condition for the obligation")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ContractDates(BaseModel):
    """Important dates related to a contract"""

    effective: Optional[Union[date, str]] = Field(None, description="Effective date")
    execution: Optional[Union[date, str]] = Field(None, description="Execution date")
    expiration: Optional[Union[date, str]] = Field(None, description="Expiration date")
    renewal: Optional[Union[date, str]] = Field(None, description="Renewal date")
    termination: Optional[Union[date, str]] = Field(
        None, description="Termination date"
    )


class Term(BaseModel):
    """Term information for a contract"""

    length: Optional[str] = Field(None, description="Length of the term")
    start_date: Optional[Union[date, str]] = Field(
        None, description="Start date of the term"
    )
    end_date: Optional[Union[date, str]] = Field(
        None, description="End date of the term"
    )
    is_auto_renewal: bool = Field(False, description="Whether the term auto-renews")
    renewal_terms: Optional[str] = Field(None, description="Terms for renewal")
    termination_notice: Optional[str] = Field(
        None, description="Notice required for termination"
    )


class Contract(BaseModel):
    """Contract document with extracted information"""

    id: str = Field(..., description="Unique identifier for the contract")
    title: str = Field(..., description="Title of the contract")
    document_type: str = Field(..., description="Type of legal document")
    text: str = Field(..., description="Full text of the contract")
    summary: Optional[str] = Field(None, description="Summary of the contract")
    parties: List[Party] = Field(
        default_factory=list, description="Parties to the contract"
    )
    dates: ContractDates = Field(
        default_factory=ContractDates, description="Important dates"
    )
    term: Optional[Term] = Field(None, description="Term information")
    clauses: List[Clause] = Field(
        default_factory=list, description="Clauses in the contract"
    )
    obligations: List[Obligation] = Field(
        default_factory=list, description="Obligations in the contract"
    )
    file_path: Optional[str] = Field(None, description="Path to the original document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )
