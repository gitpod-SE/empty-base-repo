#!/usr/bin/env python3
"""
Unit tests for the compound_analyzer module.
"""

import unittest
from typing import List, Dict, Any
import sys
import os

# Add the current directory to the path to import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compound_analyzer import analyze_compounds, calculate_properties

class TestCompoundAnalyzer(unittest.TestCase):
    """Test cases for the compound_analyzer module."""
    
    def test_calculate_properties_valid_smiles(self):
        """Test calculating properties for a valid SMILES string."""
        # Aspirin
        result = calculate_properties("CC(=O)OC1=CC=CC=C1C(=O)O", "ASP001")
        
        self.assertEqual(result['compound_id'], "ASP001")
        self.assertEqual(result['smiles'], "CC(=O)OC1=CC=CC=C1C(=O)O")
        self.assertTrue(result['is_valid'])
        self.assertIsNotNone(result['molecular_weight'])
        self.assertIsNotNone(result['logP'])
        self.assertIsInstance(result['is_compliant'], bool)
        self.assertIsInstance(result['rule_violations'], list)
    
    def test_calculate_properties_invalid_smiles(self):
        """Test calculating properties for an invalid SMILES string."""
        result = calculate_properties("INVALID_SMILES", "INV001")
        
        self.assertEqual(result['compound_id'], "INV001")
        self.assertEqual(result['smiles'], "INVALID_SMILES")
        self.assertFalse(result['is_valid'])
        self.assertIsNone(result['molecular_weight'])
        self.assertIsNone(result['logP'])
        self.assertFalse(result['is_compliant'])
        self.assertIn('Invalid SMILES string', result['rule_violations'])
    
    def test_analyze_compounds_with_ids(self):
        """Test analyzing compounds with provided IDs."""
        smiles_list = ["CC(=O)OC1=CC=CC=C1C(=O)O", "INVALID_SMILES"]
        compound_ids = ["ASP001", "INV001"]
        
        results = analyze_compounds(smiles_list, compound_ids)
        
        # Check if results is a DataFrame or list
        if hasattr(results, 'shape'):
            # It's a DataFrame
            self.assertEqual(len(results), 2)
            self.assertIn('ASP001', results['compound_id'].values)
            self.assertIn('INV001', results['compound_id'].values)
        else:
            # It's a list
            self.assertEqual(len(results), 2)
            ids = [r['compound_id'] for r in results]
            self.assertIn('ASP001', ids)
            self.assertIn('INV001', ids)
    
    def test_analyze_compounds_without_ids(self):
        """Test analyzing compounds without provided IDs."""
        smiles_list = ["CC(=O)OC1=CC=CC=C1C(=O)O", "INVALID_SMILES"]
        
        results = analyze_compounds(smiles_list)
        
        # Check if results is a DataFrame or list
        if hasattr(results, 'shape'):
            # It's a DataFrame
            self.assertEqual(len(results), 2)
            self.assertTrue(all(id.startswith('CPND') for id in results['compound_id'].values))
        else:
            # It's a list
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r['compound_id'].startswith('CPND') for r in results))
    
    def test_analyze_compounds_mismatched_ids(self):
        """Test analyzing compounds with mismatched IDs."""
        smiles_list = ["CC(=O)OC1=CC=CC=C1C(=O)O", "INVALID_SMILES"]
        compound_ids = ["ASP001"]  # One ID missing
        
        with self.assertRaises(ValueError):
            analyze_compounds(smiles_list, compound_ids)

if __name__ == '__main__':
    unittest.main()
