"""
Document classifier implementation
"""
import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """
    Classifies legal documents by type
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the document classifier
        
        Args:
            model_path: Optional path to a pre-trained classifier model
        """
        self.model_path = model_path
        self.model = None
        
        # Load classifier model if specified
        if model_path:
            self._load_model(model_path)
        
        # Define document types and their key indicators
        self.document_types = {
            "non-disclosure-agreement": [
                "confidentiality", "non-disclosure", "confidential information",
                "trade secrets", "proprietary information", "confidential disclosure"
            ],
            "employment-agreement": [
                "employment", "salary", "compensation", "duties", "responsibilities",
                "termination of employment", "at-will employment"
            ],
            "sales-agreement": [
                "purchase", "sale", "price", "delivery", "payment terms",
                "sales agreement", "goods", "services"
            ],
            "service-agreement": [
                "services", "service provider", "statement of work",
                "service level", "service agreement"
            ],
            "license-agreement": [
                "license", "licensee", "licensor", "intellectual property",
                "copyright", "patent", "trademark", "royalties"
            ],
            "lease-agreement": [
                "lease", "landlord", "tenant", "premises", "rent", "property",
                "term of lease"
            ],
        }
        
    def _load_model(self, model_path: str) -> None:
        """
        Load a pre-trained classifier model
        
        Args:
            model_path: Path to the model file
        """
        # In a real implementation, this would load a machine learning model
        # For now, we'll just log that a model would be loaded
        logger.info(f"Would load classifier model from {model_path}")
        
    def classify(self, text: str) -> str:
        """
        Classify a document based on its content
        
        Args:
            text: Document text
            
        Returns:
            str: Document type classification
        """
        # If we have a trained model, use it
        if self.model:
            # This would use the model to classify the document
            # For now, fall back to rule-based classification
            logger.info("Would use trained model for classification")
        
        # Rule-based classification
        return self._rule_based_classify(text)
        
    def _rule_based_classify(self, text: str) -> str:
        """
        Use rule-based approach to classify a document
        
        Args:
            text: Document text
            
        Returns:
            str: Document type classification
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Count occurrences of key indicators for each document type
        scores = {}
        for doc_type, indicators in self.document_types.items():
            score = 0
            for indicator in indicators:
                # Count occurrences of each indicator
                count = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
                score += count
            
            scores[doc_type] = score
            
        # Find document type with highest score
        if not scores:
            return "unknown"
            
        max_score = max(scores.values())
        if max_score == 0:
            return "unknown"
            
        # If multiple types have the same max score, check title or first few lines
        max_types = [doc_type for doc_type, score in scores.items() if score == max_score]
        if len(max_types) > 1:
            # Check document title (first few lines)
            first_lines = " ".join(text.split('\n')[:5]).lower()
            for doc_type in max_types:
                for indicator in self.document_types[doc_type]:
                    if indicator in first_lines:
                        return doc_type
            
            # If still tied, return the first one
            return max_types[0]
        else:
            return max_types[0] 