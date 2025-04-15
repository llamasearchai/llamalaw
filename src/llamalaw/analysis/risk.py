"""
Risk assessment for legal documents
"""

import logging
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from llamalaw.models.analysis import RiskAssessmentResult
from llamalaw.models.contract import Clause, Risk

logger = logging.getLogger(__name__)


class RiskSeverity(str, Enum):
    """Risk severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Risk categories"""

    LEGAL = "legal"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    REPUTATION = "reputation"


class RiskAssessor:
    """
    Assesses risks in legal documents
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the risk assessor

        Args:
            model_path: Optional path to a pre-trained risk model
        """
        self.model_path = model_path
        self.model = None

        # Load risk model if specified
        if model_path:
            self._load_model(model_path)

        # Define common risk patterns
        self._define_risk_patterns()

    def _load_model(self, model_path: str) -> None:
        """
        Load a pre-trained risk model

        Args:
            model_path: Path to the model file
        """
        # In a real implementation, this would load a machine learning model
        # For now, we'll just log that a model would be loaded
        logger.info(f"Would load risk model from {model_path}")

    def _define_risk_patterns(self) -> None:
        """Define patterns for identifying risks in contract clauses"""
        # Risk patterns organized by type and severity
        self.risk_patterns = {
            # Indemnification risks
            "unlimited-indemnification": {
                "pattern": r"indemnify.*(?:all|any).*(?:losses|damages|claims|liabilities|expenses|costs)",
                "severity": RiskSeverity.HIGH,
                "category": RiskCategory.FINANCIAL,
                "description": "Unlimited indemnification",
                "recommendation": "Limit indemnification to direct damages with a cap",
            },
            "broad-indemnification": {
                "pattern": r"indemnify.*(?:indirect|consequential|special|punitive).*damages",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.FINANCIAL,
                "description": "Indemnification includes special damages",
                "recommendation": "Exclude indirect, consequential, special, and punitive damages",
            },
            # Liability risks
            "no-liability-cap": {
                "pattern": r"no\s+(?:limit|limitation|cap|maximum).*liability",
                "severity": RiskSeverity.HIGH,
                "category": RiskCategory.FINANCIAL,
                "description": "No liability cap",
                "recommendation": "Add a reasonable liability cap",
            },
            # Termination risks
            "termination-sole-discretion": {
                "pattern": r"terminat(?:e|ion).*(?:sole\s+discretion|any\s+reason|no\s+reason|any\s+time)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.OPERATIONAL,
                "description": "Counterparty can terminate at any time",
                "recommendation": "Add notice period and limit termination to material breach",
            },
            "no-termination-right": {
                "pattern": r"(?:no|not).*right.*terminat(?:e|ion)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.OPERATIONAL,
                "description": "No right to terminate",
                "recommendation": "Add right to terminate for material breach",
            },
            # IP risks
            "ip-assignment": {
                "pattern": r"(?:assign|transfer|convey).*(?:all|entire|exclusive).*(?:right|title|interest).*(?:intellectual\s+property|copyright|patent|trademark)",
                "severity": RiskSeverity.HIGH,
                "category": RiskCategory.LEGAL,
                "description": "Assignment of intellectual property",
                "recommendation": "Limit to license rather than assignment, or narrow scope",
            },
            # Governing law risks
            "unfavorable-jurisdiction": {
                "pattern": r"govern(?:ed|ing).*laws.*(?:of|in)\s+(?!your favorable jurisdiction)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.LEGAL,
                "description": "Potentially unfavorable governing law",
                "recommendation": "Negotiate for a neutral or more favorable jurisdiction",
            },
            # Confidentiality risks
            "perpetual-confidentiality": {
                "pattern": r"confidential(?:ity)?.*(?:perpetual|indefinite|unlimited|no expiration)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.COMPLIANCE,
                "description": "Perpetual confidentiality obligation",
                "recommendation": "Limit confidentiality term to reasonable period (2-5 years)",
            },
            # Change risks
            "unilateral-changes": {
                "pattern": r"(?:may|right to).*(?:change|modify|amend).*(?:sole discretion|any time|without notice)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.OPERATIONAL,
                "description": "Counterparty can make unilateral changes",
                "recommendation": "Require mutual agreement for changes",
            },
            # Non-compete risks
            "broad-non-compete": {
                "pattern": r"(?:non-compete|not compete|no compete).*(?:worldwide|global|any|all)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.LEGAL,
                "description": "Overly broad non-compete",
                "recommendation": "Limit non-compete to reasonable geographic scope and time period",
            },
            # Assignment risks
            "unrestricted-assignment": {
                "pattern": r"(?:may|right to).*assign.*(?:without|no).*(?:consent|notice|approval)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.OPERATIONAL,
                "description": "Unrestricted assignment rights",
                "recommendation": "Require consent for assignment",
            },
            # Payment risks
            "payment-upon-receipt": {
                "pattern": r"pay(?:ment)?.*(?:due|within).*(?:upon receipt|immediately)",
                "severity": RiskSeverity.LOW,
                "category": RiskCategory.FINANCIAL,
                "description": "Payment due immediately",
                "recommendation": "Negotiate for reasonable payment terms (net 30/60)",
            },
            # Warranty
            "no-warranty": {
                "pattern": r"(?:no|without).*(?:warranty|warranties|guarantees?)",
                "severity": RiskSeverity.MEDIUM,
                "category": RiskCategory.LEGAL,
                "description": "No warranty provided",
                "recommendation": "Request standard warranties for services/products",
            },
            # Audit rights
            "broad-audit-rights": {
                "pattern": r"(?:audit|inspect).*(?:any time|all|entire|without notice)",
                "severity": RiskSeverity.LOW,
                "category": RiskCategory.COMPLIANCE,
                "description": "Broad audit rights",
                "recommendation": "Limit audit rights with reasonable notice and scope",
            },
        }

    def assess(
        self, document_type: str, clauses: List[Clause], text: str
    ) -> RiskAssessmentResult:
        """
        Assess risks in a document

        Args:
            document_type: Type of document
            clauses: List of clauses
            text: Full document text

        Returns:
            RiskAssessmentResult: Risk assessment results
        """
        # If we have a trained model, use it
        if self.model:
            # This would use the model to assess risks
            # For now, fall back to rule-based assessment
            logger.info("Would use trained model for risk assessment")

        # Perform rule-based risk assessment
        risks = self._rule_based_assess(document_type, clauses, text)

        # Count risks by category and severity
        risk_categories = {}
        risk_severity = {}

        for risk in risks:
            # Count by category
            category = risk.category
            risk_categories[category] = risk_categories.get(category, 0) + 1

            # Count by severity
            severity = risk.severity
            risk_severity[severity] = risk_severity.get(severity, 0) + 1

        # Calculate overall risk score (0-100)
        risk_score = self._calculate_risk_score(risks)

        return RiskAssessmentResult(
            risks=risks,
            risk_score=risk_score,
            risk_categories=risk_categories,
            risk_severity=risk_severity,
        )

    def _rule_based_assess(
        self, document_type: str, clauses: List[Clause], text: str
    ) -> List[Risk]:
        """
        Perform rule-based risk assessment

        Args:
            document_type: Type of document
            clauses: List of clauses
            text: Full document text

        Returns:
            List[Risk]: List of identified risks
        """
        risks = []

        # Check document type specific risks
        document_risks = self._check_document_type_risks(document_type, text)
        risks.extend(document_risks)

        # Check each clause for risks
        for clause in clauses:
            clause_risks = self._check_clause_risks(clause)
            risks.extend(clause_risks)

        # Check for risks in entire document (missing clauses)
        missing_clause_risks = self._check_missing_clauses(document_type, clauses)
        risks.extend(missing_clause_risks)

        return risks

    def _check_document_type_risks(self, document_type: str, text: str) -> List[Risk]:
        """
        Check for document type specific risks

        Args:
            document_type: Type of document
            text: Document text

        Returns:
            List[Risk]: Document type specific risks
        """
        risks = []

        # Different risk checks based on document type
        if document_type == "non-disclosure-agreement":
            # Check for one-way vs. two-way NDA
            if "mutual" not in text.lower() and "two-way" not in text.lower():
                # Likely a one-way NDA, which may be higher risk
                risks.append(
                    Risk(
                        id=f"risk-doc-{len(risks)+1}",
                        description="One-way confidentiality obligations",
                        category=RiskCategory.LEGAL,
                        severity=RiskSeverity.MEDIUM,
                        recommendation="Consider requesting mutual confidentiality obligations",
                    )
                )

        elif document_type == "employment-agreement":
            # Check for at-will employment
            if "at will" in text.lower() or "at-will" in text.lower():
                risks.append(
                    Risk(
                        id=f"risk-doc-{len(risks)+1}",
                        description="At-will employment provision",
                        category=RiskCategory.LEGAL,
                        severity=RiskSeverity.MEDIUM,
                        recommendation="Consider negotiating for termination only for cause",
                    )
                )

        # Add more document type specific checks as needed

        return risks

    def _check_clause_risks(self, clause: Clause) -> List[Risk]:
        """
        Check a clause for risks using pattern matching

        Args:
            clause: Clause to check

        Returns:
            List[Risk]: Risks identified in the clause
        """
        risks = []

        # Combine title and content for checking
        text = f"{clause.title} {clause.content}".lower()

        # Check each risk pattern
        for risk_id, risk_info in self.risk_patterns.items():
            pattern = risk_info["pattern"]
            if re.search(pattern, text, re.IGNORECASE):
                # Create a new risk
                risk = Risk(
                    id=f"risk-{clause.id}-{len(risks)+1}",
                    description=risk_info["description"],
                    category=risk_info["category"],
                    severity=risk_info["severity"],
                    recommendation=risk_info["recommendation"],
                    clause_id=clause.id,
                )
                risks.append(risk)

        return risks

    def _check_missing_clauses(
        self, document_type: str, clauses: List[Clause]
    ) -> List[Risk]:
        """
        Check for missing important clauses

        Args:
            document_type: Type of document
            clauses: List of clauses

        Returns:
            List[Risk]: Risks from missing clauses
        """
        risks = []

        # Get set of clause types that are present
        present_clause_types = {clause.type for clause in clauses}

        # Required clauses by document type
        required_clauses = {
            "non-disclosure-agreement": {
                "definition": "Definition of confidential information",
                "confidentiality": "Confidentiality obligations",
                "term": "Term of agreement",
            },
            "employment-agreement": {
                "payment": "Compensation terms",
                "term": "Employment term",
                "termination": "Termination provisions",
            },
            "sales-agreement": {
                "payment": "Payment terms",
                "warranty": "Warranty provisions",
                "limitation-of-liability": "Limitation of liability",
            },
            "service-agreement": {
                "payment": "Payment terms",
                "term": "Service term",
                "termination": "Termination provisions",
            },
            "license-agreement": {
                "payment": "License fees",
                "term": "License term",
                "limitation-of-liability": "Limitation of liability",
            },
            "lease-agreement": {
                "payment": "Rent payments",
                "term": "Lease term",
                "termination": "Termination provisions",
            },
        }

        # Check if required clauses are present for this document type
        if document_type in required_clauses:
            for clause_type, description in required_clauses[document_type].items():
                if clause_type not in present_clause_types:
                    # Create a missing clause risk
                    risk = Risk(
                        id=f"risk-missing-{clause_type}",
                        description=f"Missing {description}",
                        category=RiskCategory.LEGAL,
                        severity=RiskSeverity.MEDIUM,
                        recommendation=f"Add a {clause_type} clause",
                    )
                    risks.append(risk)

        return risks

    def _calculate_risk_score(self, risks: List[Risk]) -> float:
        """
        Calculate an overall risk score from 0-100

        Args:
            risks: List of identified risks

        Returns:
            float: Risk score (0-100, higher is riskier)
        """
        if not risks:
            return 0.0

        # Assign weights to different severity levels
        severity_weights = {
            RiskSeverity.LOW: 1,
            RiskSeverity.MEDIUM: 3,
            RiskSeverity.HIGH: 5,
            RiskSeverity.CRITICAL: 10,
        }

        # Calculate weighted sum of risks
        weighted_sum = sum(severity_weights[risk.severity] for risk in risks)

        # Scale to 0-100 (assuming max reasonable weighted sum is 50)
        score = min(100, (weighted_sum / 50) * 100)

        return round(score, 1)
