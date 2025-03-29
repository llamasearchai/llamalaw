"""
Basic tests for LlamaLaw
"""
import os
import tempfile
import unittest
from pathlib import Path

from llamalaw.analysis import ContractAnalyzer
from llamalaw.models import Contract, Party
from llamalaw.storage import ContractRepository


class TestBasic(unittest.TestCase):
    """Basic tests for LlamaLaw"""
    
    def setUp(self):
        """Set up for tests"""
        # Create a temp directory for storage
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name)
        self.repository = ContractRepository(storage_path=self.storage_path)
        
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
        
    def test_document_analysis(self):
        """Test basic document analysis"""
        # Create a simple contract document
        sample_nda = """CONFIDENTIALITY AGREEMENT

EFFECTIVE DATE: January 1, 2024

This Confidentiality Agreement is entered into by and between:

LlamaSearch Inc, a Delaware corporation, and
Test Company LLC, a California limited liability company.

1. CONFIDENTIAL INFORMATION

This includes all non-public information.

2. OBLIGATIONS OF RECIPIENT

Keep information confidential.

3. TERM

This agreement is effective for 2 years.
"""
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(sample_nda.encode('utf-8'))
            
        try:
            # Analyze document
            analyzer = ContractAnalyzer()
            result = analyzer.analyze(temp_path)
            
            # Check basic properties
            self.assertIsNotNone(result)
            self.assertIsInstance(result.contract, Contract)
            self.assertEqual(result.document_type, "non-disclosure-agreement")
            
            # Check parties
            self.assertEqual(len(result.contract.parties), 2)
            party_names = [p.name for p in result.contract.parties]
            self.assertIn("LlamaSearch Inc", party_names)
            self.assertIn("Test Company LLC", party_names)
            
            # Check if clauses were extracted
            self.assertGreater(len(result.clauses), 0)
            
            # Add to repository
            contract_id = self.repository.add(result)
            self.assertIsNotNone(contract_id)
            
            # Retrieve from repository
            stored_contract = self.repository.get(contract_id)
            self.assertIsNotNone(stored_contract)
            self.assertEqual(stored_contract.id, contract_id)
            
            # Check if the contract text was stored
            contract_text = self.repository.get_document_text(contract_id)
            self.assertIsNotNone(contract_text)
            self.assertIn("CONFIDENTIALITY AGREEMENT", contract_text)
            
            # Test repository listing
            contracts = self.repository.list()
            self.assertEqual(len(contracts), 1)
            
            # Test repository search
            search_results = self.repository.search("LlamaSearch")
            self.assertEqual(len(search_results), 1)
            
            # Test repository delete
            deleted = self.repository.delete(contract_id)
            self.assertTrue(deleted)
            
            # Verify deletion
            contracts_after_delete = self.repository.list()
            self.assertEqual(len(contracts_after_delete), 0)
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_contract_creation(self):
        """Test contract creation directly"""
        # Create parties
        party1 = Party(id="party-1", name="LlamaSearch Inc")
        party2 = Party(id="party-2", name="Test Company LLC")
        
        # Create contract
        contract = Contract(
            id="test-contract-1",
            title="Test Contract",
            document_type="non-disclosure-agreement",
            parties=[party1, party2],
            clauses=[],
            risks=[]
        )
        
        self.assertEqual(contract.title, "Test Contract")
        self.assertEqual(len(contract.parties), 2)


if __name__ == "__main__":
    unittest.main() 