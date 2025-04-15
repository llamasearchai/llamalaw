"""
LlamaLaw - Legal contract analysis and management for LlamaSearch.ai
"""

__version__ = "0.1.0"
__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__license__ = "MIT"

from llamalaw.analysis.analyzer import ContractAnalyzer
from llamalaw.analysis.classifier import DocumentClassifier
from llamalaw.analysis.extractor import ClauseExtractor, EntityExtractor
from llamalaw.analysis.risks import RiskAssessor
from llamalaw.models.analysis import (
    AnalysisResult,
    ExtractionResult,
    RiskAssessmentResult,
)
from llamalaw.models.contract import (
    Clause,
    Contract,
    ContractDates,
    Obligation,
    Party,
    Risk,
    Term,
)
from llamalaw.storage.repository import ContractRepository

__all__ = [
    # Main classes
    "ContractAnalyzer",
    "EntityExtractor",
    "ClauseExtractor",
    "DocumentClassifier",
    "RiskAssessor",
    "ContractRepository",
    
    # Models
    "Contract",
    "Clause",
    "Obligation",
    "Party",
    "Risk",
    "ContractDates",
    "Term",
    
    # Result types
    "AnalysisResult",
    "ExtractionResult",
    "RiskAssessmentResult",
] 