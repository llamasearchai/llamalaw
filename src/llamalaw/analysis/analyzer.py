"""
Contract analyzer implementation
"""
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import logging

from llamalaw.analysis.classifier import DocumentClassifier
from llamalaw.analysis.extractor import EntityExtractor, ClauseExtractor
from llamalaw.analysis.risks import RiskAssessor
from llamalaw.models.analysis import AnalysisResult
from llamalaw.models.contract import Contract, ContractDates, Party
from llamalaw.utils.document import DocumentLoader, TextPreprocessor

logger = logging.getLogger(__name__)


class ContractAnalyzer:
    """
    Main class for analyzing legal contracts and extracting structured information.
    """

    def __init__(
        self,
        document_loader: Optional[DocumentLoader] = None,
        text_preprocessor: Optional[TextPreprocessor] = None,
        document_classifier: Optional[DocumentClassifier] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        clause_extractor: Optional[ClauseExtractor] = None,
        risk_assessor: Optional[RiskAssessor] = None,
    ):
        """
        Initialize the contract analyzer with optional component overrides.

        Args:
            document_loader: Custom document loader implementation
            text_preprocessor: Custom text preprocessor implementation
            document_classifier: Custom document classifier implementation
            entity_extractor: Custom entity extractor implementation
            clause_extractor: Custom clause extractor implementation
            risk_assessor: Custom risk assessment implementation
        """
        self.document_loader = document_loader or DocumentLoader()
        self.text_preprocessor = text_preprocessor or TextPreprocessor()
        self.document_classifier = document_classifier or DocumentClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.clause_extractor = clause_extractor or ClauseExtractor()
        self.risk_assessor = risk_assessor or RiskAssessor()

    def analyze(
        self, document_path: Union[str, Path], **kwargs
    ) -> AnalysisResult:
        """
        Analyze a contract document and extract structured information.

        Args:
            document_path: Path to the document file
            **kwargs: Additional options for analysis

        Returns:
            AnalysisResult containing structured information about the contract
        """
        # Convert to Path if string
        if isinstance(document_path, str):
            document_path = Path(document_path)

        # Load the document
        logger.info(f"Loading document: {document_path}")
        document_text = self.document_loader.load(document_path)

        # Preprocess the text
        logger.info("Preprocessing document text")
        processed_text = self.text_preprocessor.preprocess(document_text)

        # Classify the document
        logger.info("Classifying document type")
        document_type = self.document_classifier.classify(processed_text)

        # Extract entities
        logger.info("Extracting entities")
        entities = self.entity_extractor.extract(processed_text)

        # Extract clauses
        logger.info("Extracting clauses")
        clauses = self.clause_extractor.extract(processed_text)

        # Assess risks
        logger.info("Assessing risks")
        risks = self.risk_assessor.assess(processed_text, clauses, document_type)

        # Create a contract object
        contract = self._create_contract(
            document_path, processed_text, document_type, entities, clauses
        )

        # Create and return the analysis result
        return AnalysisResult(
            contract=contract,
            document_type=document_type,
            entities=entities,
            clauses=clauses,
            risks=risks,
            raw_text=document_text,
            processed_text=processed_text,
        )

    def batch_analyze(
        self, directory_path: Union[str, Path], **kwargs
    ) -> List[AnalysisResult]:
        """
        Analyze all contract documents in a directory.

        Args:
            directory_path: Path to the directory containing documents
            **kwargs: Additional options for analysis

        Returns:
            List of AnalysisResult objects for each document
        """
        # Convert to Path if string
        if isinstance(directory_path, str):
            directory_path = Path(directory_path)

        # Get list of documents to analyze
        supported_extensions = self.document_loader.supported_extensions
        documents = []

        for extension in supported_extensions:
            documents.extend(directory_path.glob(f"**/*{extension}"))

        # Analyze each document
        results = []
        for document_path in documents:
            try:
                logger.info(f"Analyzing document: {document_path}")
                result = self.analyze(document_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {document_path}: {e}")
                continue

        return results

    def _create_contract(
        self,
        document_path: Path,
        text: str,
        document_type: str,
        entities: Dict[str, Any],
        clauses: List[Any],
    ) -> Contract:
        """
        Create a Contract object from extracted information.

        Args:
            document_path: Path to the document
            text: Processed text
            document_type: Document type classification
            entities: Extracted entities
            clauses: Extracted clauses

        Returns:
            Contract object
        """
        # Create a unique ID
        contract_id = str(uuid.uuid4())

        # Get contract title
        title = os.path.basename(document_path)

        # Extract parties
        parties = []
        if "parties" in entities and entities["parties"]:
            for party_data in entities["parties"]:
                parties.append(
                    Party(
                        name=party_data.get("name", ""),
                        type=party_data.get("type", ""),
                        address=party_data.get("address", ""),
                    )
                )

        # Extract dates
        dates = ContractDates()
        if "dates" in entities and entities["dates"]:
            date_data = entities["dates"]
            if "effective" in date_data:
                dates.effective = date_data["effective"]
            if "execution" in date_data:
                dates.execution = date_data["execution"]
            if "expiration" in date_data:
                dates.expiration = date_data["expiration"]

        # Create Contract object
        return Contract(
            id=contract_id,
            title=title,
            document_type=document_type,
            text=text,
            parties=parties,
            dates=dates,
            clauses=clauses,
            file_path=str(document_path),
        ) 