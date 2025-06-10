#!/usr/bin/env python3
"""
Example script demonstrating how to use the compound_analyzer module.
"""

from compound_analyzer import analyze_compounds
import pandas as pd

def main():
    # Example list of SMILES strings
    smiles_list = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "C1=CC=C(C=C1)C(=O)O",  # Benzoic acid
        "INVALID_SMILES",  # Invalid SMILES
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        "C(C(=O)O)N",  # Glycine
        "CC(C)(C)NCC(O)C1=CC(=C(C=C1)O)CO",  # Salbutamol
        "CC1=C(C=C(C=C1)S(=O)(=O)N)CC(=O)O"  # Tolmetin
    ]

    # Custom compound IDs
    compound_ids = [
        "ASP001", "CAF001", "BNZ001", "INV001", 
        "IBU001", "GLY001", "SLB001", "TLM001"
    ]

    # Analyze compounds
    print("Analyzing compounds...")
    results = analyze_compounds(smiles_list, compound_ids, n_workers=2)

    # Display results
    print("\nResults:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    print(results[['compound_id', 'smiles', 'is_valid', 'molecular_weight', 'logP', 'is_compliant']])
    
    # Display rule violations for non-compliant compounds
    print("\nRule violations:")
    non_compliant = results[~results['is_compliant']]
    for _, row in non_compliant.iterrows():
        print(f"{row['compound_id']} ({row['smiles']}): {', '.join(row['rule_violations'])}")
    
    # Summary statistics
    print("\nSummary:")
    print(f"Total compounds: {len(results)}")
    print(f"Valid compounds: {results['is_valid'].sum()}")
    print(f"Compliant compounds: {results['is_compliant'].sum()}")
    
    # Save results to CSV
    results.to_csv('compound_analysis_results.csv', index=False)
    print("\nResults saved to 'compound_analysis_results.csv'")

if __name__ == "__main__":
    main()
