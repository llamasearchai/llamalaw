"""
Entity and clause extraction utilities
"""

import logging
import re
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from llamalaw.models.contract import Clause, ContractDates, Party

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Types of entities that can be extracted"""

    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    TIME = "time"
    DURATION = "duration"


class EntityExtractor:
    """
    Extracts named entities from legal documents
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the entity extractor

        Args:
            model_path: Optional path to a pre-trained NER model
        """
        self.model_path = model_path
        self.model = None

        # Load NER model if specified
        if model_path:
            self._load_model(model_path)

        # Compile patterns for rule-based extraction
        self._compile_patterns()

    def _load_model(self, model_path: str) -> None:
        """
        Load a pre-trained NER model

        Args:
            model_path: Path to the model file
        """
        # In a real implementation, this would load a model like spaCy or a custom NER model
        # For now, we'll just log that a model would be loaded
        logger.info(f"Would load NER model from {model_path}")

    def _compile_patterns(self) -> None:
        """Compile regex patterns for rule-based entity extraction"""
        # Date patterns
        self.date_patterns = [
            # MM/DD/YYYY or DD/MM/YYYY
            re.compile(
                r"\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d\d\b"
            ),
            # Month DD, YYYY
            re.compile(
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?,\s+(19|20)\d\d\b"
            ),
            # Abbreviated month
            re.compile(
                r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?,\s+(19|20)\d\d\b"
            ),
            # YYYY-MM-DD (ISO format)
            re.compile(
                r"\b(19|20)\d\d[-](0?[1-9]|1[0-2])[-](0?[1-9]|[12][0-9]|3[01])\b"
            ),
        ]

        # Money patterns
        self.money_patterns = [
            # Currency symbols
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b"),
            re.compile(r"€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b"),
            re.compile(r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b"),
            # Written out
            re.compile(
                r"\b(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\s*(?:dollars|euros|pounds))\b"
            ),
            # USD, EUR, etc.
            re.compile(r"\b(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\s*(?:USD|EUR|GBP))\b"),
        ]

        # Organization patterns - simplified, would be more complex in reality
        self.org_patterns = [
            re.compile(
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,)?\s+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co|GmbH|LP|LLP|Limited|International))\b"
            ),
            re.compile(
                r"\b((?:The\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Trust|Foundation|Association|Institute|University|College|School))\b"
            ),
        ]

        # Person patterns - simplified
        self.person_patterns = [
            re.compile(
                r"\b((?:Mr|Mrs|Ms|Dr|Prof)\.\s+(?:[A-Z][a-z]+\s+)+(?:[A-Z][a-z]+))\b"
            ),
            re.compile(r"\b((?:[A-Z][a-z]+\s+)(?:[A-Z]\.\s+)?(?:[A-Z][a-z]+))\b"),
        ]

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text

        Args:
            text: Document text

        Returns:
            Dict[str, List[str]]: Dictionary of entity types and their values
        """
        # If we have a trained model, use it
        if self.model:
            # This would use the model to extract entities
            # For now, fall back to rule-based extraction
            logger.info("Would use trained model for entity extraction")

        # Rule-based extraction
        return self._rule_based_extract(text)

    def _rule_based_extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using rule-based patterns

        Args:
            text: Document text

        Returns:
            Dict[str, List[str]]: Dictionary of entity types and their values
        """
        # Initialize entity dictionary
        entities = {
            EntityType.PERSON: [],
            EntityType.ORGANIZATION: [],
            EntityType.DATE: [],
            EntityType.MONEY: [],
            EntityType.LOCATION: [],
            EntityType.PERCENTAGE: [],
            EntityType.TIME: [],
            EntityType.DURATION: [],
        }

        # Extract dates
        for pattern in self.date_patterns:
            for match in pattern.finditer(text):
                entities[EntityType.DATE].append(match.group(0))

        # Extract money
        for pattern in self.money_patterns:
            for match in pattern.finditer(text):
                entities[EntityType.MONEY].append(match.group(0))

        # Extract organizations
        for pattern in self.org_patterns:
            for match in pattern.finditer(text):
                entities[EntityType.ORGANIZATION].append(match.group(1))

        # Extract persons
        for pattern in self.person_patterns:
            for match in pattern.finditer(text):
                entities[EntityType.PERSON].append(match.group(1))

        # Remove duplicates while preserving order
        for entity_type in entities:
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))

        return entities

    def extract_parties(self, text: str) -> List[Party]:
        """
        Extract contract parties from text

        Args:
            text: Document text

        Returns:
            List[Party]: List of contract parties
        """
        # Extract organizations first
        entities = self.extract(text)
        organizations = entities[EntityType.ORGANIZATION]

        # Look for common party indicators
        party_indicators = [
            r"(?:between|by and between)\s+([^,]+)(?:,|and|\n)",
            r"(?:party of the first part|party of the second part)(?::|,)?\s+([^,\n]+)",
            r'(?:the "(?:Company|Employer|Client|Vendor|Supplier|Licensor|Licensee|Landlord|Tenant)")(?::|,)?\s+([^,\n]+)',
            r'(?:hereinafter referred to as|herein referred to as)(?::|,)?\s+"?([^",\n]+)"?',
        ]

        additional_parties = []
        for pattern in party_indicators:
            matches = re.finditer(pattern, text)
            for match in matches:
                additional_parties.append(match.group(1).strip())

        # Combine with organizations and remove duplicates
        all_party_names = list(dict.fromkeys(organizations + additional_parties))

        # Create Party objects
        parties = []
        for i, name in enumerate(all_party_names):
            party_id = f"party-{i+1}"
            parties.append(Party(id=party_id, name=name))

        return parties

    def extract_dates(self, text: str) -> ContractDates:
        """
        Extract key contract dates

        Args:
            text: Document text

        Returns:
            ContractDates: Contract dates
        """
        # Extract all dates first
        entities = self.extract(text)
        all_dates = entities[EntityType.DATE]

        # Initialize with empty dates
        contract_dates = ContractDates()

        # Look for effective date indicators
        effective_patterns = [
            r"(?:effective\s+(?:as\s+of\s+|date:?\s*))([^,\n]+)",
            r"(?:agreement\s+date:?\s*)([^,\n]+)",
            r"(?:dated\s+(?:as\s+of\s+)?)([^,\n]+)",
        ]

        # Look for termination date indicators
        termination_patterns = [
            r"(?:terminat(?:es|ion)\s+(?:date|on):?\s*)([^,\n]+)",
            r"(?:expir(?:es|ation)\s+(?:date|on):?\s*)([^,\n]+)",
            r"(?:end\s+date:?\s*)([^,\n]+)",
        ]

        # Try to find effective date
        for pattern in effective_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group(1).strip()
                if date_text in all_dates:
                    contract_dates.effective = date_text
                    break

        # Try to find termination date
        for pattern in termination_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group(1).strip()
                if date_text in all_dates:
                    contract_dates.termination = date_text
                    break

        return contract_dates


class ClauseExtractor:
    """
    Extracts clauses from legal documents
    """

    def __init__(self):
        """Initialize the clause extractor"""
        # Define common clause types and their indicators
        self.clause_types = {
            "definition": [
                "definitions",
                "defined terms",
                "interpretation",
                "meaning of",
            ],
            "payment": ["payment", "consideration", "fees", "compensation", "price"],
            "term": ["term of", "duration", "period", "agreement term"],
            "termination": ["termination", "cancellation", "ending the agreement"],
            "confidentiality": [
                "confidentiality",
                "confidential information",
                "non-disclosure",
            ],
            "governing-law": [
                "governing law",
                "applicable law",
                "jurisdiction",
                "choice of law",
            ],
            "indemnification": ["indemnification", "indemnity", "hold harmless"],
            "warranty": ["warranty", "warranties", "representations"],
            "limitation-of-liability": [
                "limitation of liability",
                "limited liability",
                "liability cap",
                "limitation on liability",
            ],
            "assignment": ["assignment", "assignability", "transfer of"],
            "force-majeure": ["force majeure", "act of god", "events beyond control"],
            "notice": ["notice", "notification", "communications"],
            "amendment": ["amendment", "modification", "changes to this agreement"],
            "dispute-resolution": [
                "dispute resolution",
                "arbitration",
                "mediation",
                "litigation",
            ],
        }

        # Compile section header patterns
        self.section_patterns = [
            # Numbered sections (1., 1.1, etc.)
            re.compile(r"(?:^|\n)(?:\s*)(\d+(?:\.\d+)*)\s+([^\n]+)", re.MULTILINE),
            # Sections with uppercase titles
            re.compile(r"(?:^|\n)(?:\s*)([A-Z][A-Z\s]+[A-Z])(?:\.|:|\n)", re.MULTILINE),
            # Sections with title case
            re.compile(
                r"(?:^|\n)(?:\s*)((?:[A-Z][a-z]+\s*)+)(?:\.|:|\n)", re.MULTILINE
            ),
        ]

    def extract(self, text: str) -> List[Clause]:
        """
        Extract clauses from document text

        Args:
            text: Document text

        Returns:
            List[Clause]: List of extracted clauses
        """
        # Extract sections from the document
        sections = self._extract_sections(text)

        # Convert sections to clauses
        clauses = []
        for i, (title, content) in enumerate(sections):
            clause_id = f"clause-{i+1}"
            clause_type = self._determine_clause_type(title, content)

            clauses.append(
                Clause(id=clause_id, title=title, content=content, type=clause_type)
            )

        return clauses

    def _extract_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract sections with titles and content

        Args:
            text: Document text

        Returns:
            List[Tuple[str, str]]: List of (title, content) tuples
        """
        sections = []

        # Try each section pattern
        for pattern in self.section_patterns:
            matches = list(pattern.finditer(text))
            if matches:
                # Get section titles and their positions
                section_positions = []
                for match in matches:
                    if len(match.groups()) == 1:
                        # Only title group is captured
                        title = match.group(1)
                        position = match.start(1)
                    else:
                        # Number and title are captured
                        number = match.group(1)
                        title = match.group(2)
                        position = match.start(1)
                        title = f"{number} {title}"

                    section_positions.append((title, position))

                # Extract content between sections
                for i, (title, start) in enumerate(section_positions):
                    if i < len(section_positions) - 1:
                        next_start = section_positions[i + 1][1]
                        content = text[start + len(title) : next_start].strip()
                    else:
                        content = text[start + len(title) :].strip()

                    sections.append((title, content))

                # If we found sections with this pattern, stop looking
                if sections:
                    break

        # If no sections found using patterns, try splitting by blank lines
        if not sections:
            paragraphs = re.split(r"\n\s*\n", text)
            for i, para in enumerate(paragraphs):
                # Try to extract a title from the first line
                lines = para.split("\n")
                if lines:
                    title = lines[0].strip()
                    content = "\n".join(lines[1:]).strip()
                    sections.append((title, content))

        return sections

    def _determine_clause_type(self, title: str, content: str) -> str:
        """
        Determine the type of clause based on its title and content

        Args:
            title: Section title
            content: Section content

        Returns:
            str: Clause type
        """
        title_lower = title.lower()
        content_lower = content.lower()

        # Check each clause type
        for clause_type, indicators in self.clause_types.items():
            for indicator in indicators:
                if indicator.lower() in title_lower:
                    return clause_type

        # If not found in title, check content
        for clause_type, indicators in self.clause_types.items():
            for indicator in indicators:
                if (
                    indicator.lower() in content_lower[:100]
                ):  # Check only first 100 chars
                    return clause_type

        # Default to "other" if not identified
        return "other"
