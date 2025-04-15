"""
Contract storage and retrieval
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from llamalaw.models.analysis import AnalysisResult
from llamalaw.models.contract import Clause, Contract, ContractDates, Party, Risk

logger = logging.getLogger(__name__)

# Define SQLAlchemy Base
Base = declarative_base()


class ContractRecord(Base):
    """Contract database record"""

    __tablename__ = "contracts"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    effective_date = Column(String, nullable=True)
    termination_date = Column(String, nullable=True)
    parties = Column(Text, nullable=False)  # JSON string
    clauses = Column(Text, nullable=False)  # JSON string
    risks = Column(Text, nullable=False)  # JSON string
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_contract(self) -> Contract:
        """Convert database record to Contract model"""
        # Parse JSON strings
        parties_data = json.loads(self.parties)
        clauses_data = json.loads(self.clauses)
        risks_data = json.loads(self.risks)

        # Create dates object
        dates = ContractDates(
            effective=self.effective_date, termination=self.termination_date
        )

        # Create parties list
        parties = [Party(**party_data) for party_data in parties_data]

        # Create clauses list
        clauses = [Clause(**clause_data) for clause_data in clauses_data]

        # Create risks list
        risks = [Risk(**risk_data) for risk_data in risks_data]

        # Create contract
        return Contract(
            id=self.id,
            title=self.title,
            document_type=self.document_type,
            filename=self.filename,
            dates=dates,
            parties=parties,
            clauses=clauses,
            risks=risks,
        )


class ContractRepository:
    """
    Repository for storing and retrieving contracts
    """

    def __init__(self, storage_path: Union[str, Path] = None, db_url: str = None):
        """
        Initialize the contract repository

        Args:
            storage_path: Path to directory for storing contract files
            db_url: SQLAlchemy database URL (if None, uses SQLite in storage_path)
        """
        # Set storage path
        if storage_path is None:
            # Default to user data directory
            storage_path = Path.home() / ".llamalaw" / "contracts"
        elif isinstance(storage_path, str):
            storage_path = Path(storage_path)

        self.storage_path = storage_path

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

        # Set up database
        if db_url is None:
            # Default to SQLite database in storage path
            db_path = self.storage_path / "contracts.db"
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def add(self, analysis_result: AnalysisResult) -> str:
        """
        Add a contract to the repository from analysis results

        Args:
            analysis_result: Contract analysis results

        Returns:
            str: ID of the stored contract
        """
        # Extract contract from analysis result
        contract = analysis_result.contract

        # Serialize complex objects to JSON
        parties_json = json.dumps([party.dict() for party in contract.parties])
        clauses_json = json.dumps([clause.dict() for clause in contract.clauses])
        risks_json = json.dumps([risk.dict() for risk in analysis_result.risks])

        # Create contract record
        contract_record = ContractRecord(
            id=contract.id,
            title=contract.title,
            document_type=analysis_result.document_type,
            filename=contract.filename,
            effective_date=contract.dates.effective,
            termination_date=contract.dates.termination,
            parties=parties_json,
            clauses=clauses_json,
            risks=risks_json,
            risk_score=analysis_result.metadata.get("risk_score"),
        )

        # Add to database
        with self.Session() as session:
            # Check if contract with this ID already exists
            existing = session.query(ContractRecord).filter_by(id=contract.id).first()
            if existing:
                # Update existing record
                existing.title = contract_record.title
                existing.document_type = contract_record.document_type
                existing.filename = contract_record.filename
                existing.effective_date = contract_record.effective_date
                existing.termination_date = contract_record.termination_date
                existing.parties = contract_record.parties
                existing.clauses = contract_record.clauses
                existing.risks = contract_record.risks
                existing.risk_score = contract_record.risk_score
                existing.updated_at = datetime.utcnow()
            else:
                # Add new record
                session.add(contract_record)

            session.commit()

        # Save original document text if available
        if analysis_result.raw_text:
            self._save_document_text(contract.id, analysis_result.raw_text)

        return contract.id

    def get(self, contract_id: str) -> Optional[Contract]:
        """
        Get a contract by ID

        Args:
            contract_id: Contract ID

        Returns:
            Optional[Contract]: Contract if found, None otherwise
        """
        with self.Session() as session:
            record = session.query(ContractRecord).filter_by(id=contract_id).first()
            if record:
                return record.to_contract()
            else:
                return None

    def delete(self, contract_id: str) -> bool:
        """
        Delete a contract by ID

        Args:
            contract_id: Contract ID

        Returns:
            bool: True if deleted, False if not found
        """
        with self.Session() as session:
            record = session.query(ContractRecord).filter_by(id=contract_id).first()
            if record:
                session.delete(record)
                session.commit()

                # Delete document text file if it exists
                doc_path = self._get_document_path(contract_id)
                if doc_path.exists():
                    os.remove(doc_path)

                return True
            else:
                return False

    def list(self, document_type: Optional[str] = None) -> List[Contract]:
        """
        List all contracts, optionally filtered by document type

        Args:
            document_type: Optional document type to filter by

        Returns:
            List[Contract]: List of contracts
        """
        with self.Session() as session:
            query = session.query(ContractRecord)
            if document_type:
                query = query.filter_by(document_type=document_type)

            records = query.all()
            return [record.to_contract() for record in records]

    def search(self, query: str) -> List[Contract]:
        """
        Search for contracts by title, parties, or content

        Args:
            query: Search query

        Returns:
            List[Contract]: List of matching contracts
        """
        # In a real implementation, this would use full-text search capabilities
        # Here we'll do a simple in-memory search
        query = query.lower()
        results = []

        with self.Session() as session:
            records = session.query(ContractRecord).all()
            for record in records:
                # Check title
                if query in record.title.lower():
                    results.append(record.to_contract())
                    continue

                # Check parties
                parties_data = json.loads(record.parties)
                for party_data in parties_data:
                    if query in party_data.get("name", "").lower():
                        results.append(record.to_contract())
                        break

                # Check document text if available
                doc_path = self._get_document_path(record.id)
                if doc_path.exists():
                    try:
                        with open(doc_path, "r", encoding="utf-8") as f:
                            text = f.read()
                            if query in text.lower():
                                results.append(record.to_contract())
                                continue
                    except Exception as e:
                        logger.warning(f"Error reading document text: {e}")

        return results

    def get_document_text(self, contract_id: str) -> Optional[str]:
        """
        Get the original document text for a contract

        Args:
            contract_id: Contract ID

        Returns:
            Optional[str]: Document text if available, None otherwise
        """
        doc_path = self._get_document_path(contract_id)
        if doc_path.exists():
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Error reading document text: {e}")

        return None

    def _get_document_path(self, contract_id: str) -> Path:
        """Get path to document text file"""
        return self.storage_path / f"{contract_id}.txt"

    def _save_document_text(self, contract_id: str, text: str) -> None:
        """Save document text to file"""
        doc_path = self._get_document_path(contract_id)
        try:
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logger.warning(f"Error saving document text: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the contract repository

        Returns:
            Dict[str, Any]: Repository statistics
        """
        with self.Session() as session:
            total_count = session.query(ContractRecord).count()

            # Count by document type
            type_counts = {}
            types = session.query(ContractRecord.document_type).distinct().all()
            for (doc_type,) in types:
                count = (
                    session.query(ContractRecord)
                    .filter_by(document_type=doc_type)
                    .count()
                )
                type_counts[doc_type] = count

            # Get average risk score
            risk_query = session.query(ContractRecord.risk_score).filter(
                ContractRecord.risk_score.isnot(None)
            )
            risk_scores = [row[0] for row in risk_query.all()]
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

            # Get date ranges
            date_query = session.query(
                ContractRecord.created_at, ContractRecord.updated_at
            ).order_by(ContractRecord.created_at)

            first_record = date_query.first()
            last_record = date_query.order_by(ContractRecord.created_at.desc()).first()

            first_date = first_record[0] if first_record else None
            last_date = last_record[1] if last_record else None

        return {
            "total_contracts": total_count,
            "contracts_by_type": type_counts,
            "average_risk_score": avg_risk,
            "first_contract_date": first_date,
            "last_updated_date": last_date,
        }
