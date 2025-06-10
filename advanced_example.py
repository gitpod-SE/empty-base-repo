#!/usr/bin/env python3
"""
Advanced example demonstrating how to use the compound_analyzer module
with larger datasets and batch processing.
"""

import time
import logging
from typing import List, Dict, Any
from compound_analyzer import analyze_compounds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Example dataset of SMILES strings (a larger set)
EXAMPLE_SMILES = [
    # Common drugs
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
    "C1=CC=C(C=C1)C(=O)O",  # Benzoic acid
    "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
    "C(C(=O)O)N",  # Glycine
    "CC1=C(C=C(C=C1)S(=O)(=O)N)CC(=O)O",  # Tolmetin
    "CC(C)NCC(O)C1=CC(=C(C=C1)O)CO",  # Salbutamol
    "CN1C(=O)NC(C)=C1C(=O)N(C)C",  # Theophylline
    "CC(C)(C)NCC(O)COC1=CC=CC=C1CC=C",  # Salmeterol
    "CC(CS)C(=O)N1CCCC1C(=O)O",  # Captopril
    
    # Invalid SMILES for testing error handling
    "INVALID_SMILES_1",
    "C1=CC=CC=Z",  # Invalid atom
    "C1=CC=CC",  # Unclosed ring
    
    # Large molecules that might violate rules
    "CCCCCCCCCCCCCCCCCCCC(=O)OC",  # Very long chain ester
    "C1=CC=C(C=C1)C(=O)NCCNCCNCCNCCNCCNCCNCCNCC",  # Large molecule
    "C1=CC=C(C=C1)OC2=CC=C(C=C2)OC3=CC=C(C=C3)OC4=CC=C(C=C4)OC5=CC=CC=C5"  # Multiple aromatic rings
]

def generate_large_dataset(base_smiles: List[str], size: int = 1000) -> List[str]:
    """
    Generate a larger dataset by repeating and slightly modifying base SMILES.
    
    Parameters
    ----------
    base_smiles : List[str]
        Base set of SMILES strings
    size : int, optional
        Target size of the dataset, by default 1000
        
    Returns
    -------
    List[str]
        Expanded dataset of SMILES strings
    """
    import random
    
    result = []
    while len(result) < size:
        for smiles in base_smiles:
            if "INVALID" in smiles:
                # Keep invalid SMILES as is
                result.append(smiles)
            elif len(result) >= size:
                break
            else:
                # For valid SMILES, sometimes add a modification
                if random.random() < 0.2:
                    # Add a methyl group or similar simple modification
                    # Note: This is a simplistic approach and might produce invalid SMILES
                    modified = smiles.replace("C", "CC", 1)
                    result.append(modified)
                else:
                    result.append(smiles)
    
    return result[:size]

def process_in_batches(
    smiles_list: List[str], 
    batch_size: int = 100, 
    n_workers: int = 4
) -> List[Dict[str, Any]]:
    """
    Process a large list of SMILES strings in batches.
    
    Parameters
    ----------
    smiles_list : List[str]
        List of SMILES strings to process
    batch_size : int, optional
        Size of each batch, by default 100
    n_workers : int, optional
        Number of workers for parallel processing, by default 4
        
    Returns
    -------
    List[Dict[str, Any]]
        Combined results from all batches
    """
    start_time = time.time()
    total_compounds = len(smiles_list)
    logger.info(f"Processing {total_compounds} compounds in batches of {batch_size}")
    
    all_results = []
    
    for i in range(0, total_compounds, batch_size):
        batch_start = time.time()
        end_idx = min(i + batch_size, total_compounds)
        batch = smiles_list[i:end_idx]
        
        logger.info(f"Processing batch {i//batch_size + 1}/{(total_compounds + batch_size - 1)//batch_size} "
                   f"({len(batch)} compounds)")
        
        # Generate sequential IDs for this batch
        batch_ids = [f"CPND{j+1:06d}" for j in range(i, end_idx)]
        
        # Process the batch
        results = analyze_compounds(batch, batch_ids, n_workers=n_workers)
        
        # Convert to list if it's a DataFrame
        if hasattr(results, 'to_dict'):
            results_list = results.to_dict('records')
        else:
            results_list = results
            
        all_results.extend(results_list)
        
        batch_time = time.time() - batch_start
        logger.info(f"Batch processed in {batch_time:.2f} seconds "
                   f"({len(batch)/batch_time:.2f} compounds/second)")
        
        # Optional: save intermediate results
        # save_results(results_list, f"batch_{i//batch_size + 1}_results.json")
    
    total_time = time.time() - start_time
    logger.info(f"All processing completed in {total_time:.2f} seconds "
               f"({total_compounds/total_time:.2f} compounds/second overall)")
    
    return all_results

def analyze_results(results: List[Dict[str, Any]]) -> None:
    """
    Analyze and print summary statistics from the results.
    
    Parameters
    ----------
    results : List[Dict[str, Any]]
        List of compound analysis results
    """
    total = len(results)
    valid_count = sum(1 for r in results if r.get('is_valid') is True)
    invalid_count = sum(1 for r in results if r.get('is_valid') is False)
    compliant_count = sum(1 for r in results if r.get('is_compliant') is True)
    
    # Calculate average properties for valid compounds
    valid_results = [r for r in results if r.get('is_valid') is True]
    avg_mw = sum(r.get('molecular_weight', 0) for r in valid_results) / max(1, len(valid_results))
    avg_logp = sum(r.get('logP', 0) for r in valid_results) / max(1, len(valid_results))
    
    # Count rule violations
    violation_counts = {}
    for result in results:
        for violation in result.get('rule_violations', []):
            violation_counts[violation] = violation_counts.get(violation, 0) + 1
    
    # Print summary
    print("\n===== ANALYSIS SUMMARY =====")
    print(f"Total compounds: {total}")
    print(f"Valid compounds: {valid_count} ({valid_count/total*100:.1f}%)")
    print(f"Invalid compounds: {invalid_count} ({invalid_count/total*100:.1f}%)")
    print(f"Rule-compliant compounds: {compliant_count} ({compliant_count/total*100:.1f}%)")
    print(f"Average molecular weight: {avg_mw:.2f}")
    print(f"Average logP: {avg_logp:.2f}")
    
    print("\nRule violations:")
    for violation, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {violation}: {count} compounds ({count/total*100:.1f}%)")

def save_results(results: List[Dict[str, Any]], filename: str) -> None:
    """
    Save results to a file.
    
    Parameters
    ----------
    results : List[Dict[str, Any]]
        Results to save
    filename : str
        Output filename
    """
    try:
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving results to {filename}: {str(e)}")

def main():
    """Main function demonstrating advanced usage."""
    # Generate a larger dataset
    dataset_size = 200  # Adjust based on your system's capabilities
    logger.info(f"Generating dataset of {dataset_size} compounds")
    large_dataset = generate_large_dataset(EXAMPLE_SMILES, size=dataset_size)
    
    # Process in batches
    batch_size = 50
    n_workers = 2  # Adjust based on your CPU cores
    
    results = process_in_batches(large_dataset, batch_size, n_workers)
    
    # Analyze results
    analyze_results(results)
    
    # Save final results
    save_results(results, "compound_analysis_results.json")
    
    # Convert to DataFrame if pandas is available
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv("compound_analysis_results.csv", index=False)
        logger.info("Results saved to compound_analysis_results.csv")
    except ImportError:
        logger.warning("Pandas not available. Results saved as JSON only.")

if __name__ == "__main__":
    main()
