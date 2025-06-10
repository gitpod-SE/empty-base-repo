#!/usr/bin/env python3
"""
Compound Analyzer: A tool for analyzing chemical compounds using RDKit.
"""

import os
import sys
import logging
import concurrent.futures
from typing import List, Dict, Tuple, Optional, Union, Any
import subprocess
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_and_install_dependencies() -> bool:
    """
    Check if required dependencies are installed and install them if not.
    
    Returns
    -------
    bool
        True if dependencies are available, False otherwise
    """
    try:
        import rdkit
        import pandas
        import numpy
        return True
    except ImportError:
        try:
            logger.info("Installing required dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rdkit", "pandas", "numpy"])
            logger.info("Dependencies installed successfully.")
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Failed to install dependencies: {str(e)}")
            logger.error("Please install the required dependencies manually:")
            logger.error("pip install rdkit pandas numpy")
            return False

def calculate_properties(smiles: str, compound_id: str) -> Dict[str, Any]:
    """
    Calculate molecular properties for a given SMILES string.
    
    Parameters
    ----------
    smiles : str
        SMILES representation of the molecule
    compound_id : str
        Identifier for the compound
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing calculated properties
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Lipinski
        
        # Initialize result dictionary with compound ID and SMILES
        result = {
            'compound_id': compound_id,
            'smiles': smiles,
            'is_valid': False,
            'molecular_weight': None,
            'logP': None,
            'is_compliant': False,
            'rule_violations': []
        }
        
        # Parse SMILES string
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            result['rule_violations'].append('Invalid SMILES string')
            return result
            
        # Mark as valid since we have a valid molecule
        result['is_valid'] = True
        
        # Calculate molecular weight
        result['molecular_weight'] = Descriptors.MolWt(mol)
        
        # Calculate logP
        result['logP'] = Descriptors.MolLogP(mol)
        
        # Check internal rule compliance (Lipinski's Rule of Five as an example)
        violations = []
        
        # Rule 1: Molecular weight < 500
        if result['molecular_weight'] > 500:
            violations.append('MW > 500')
            
        # Rule 2: logP <= 5
        if result['logP'] > 5:
            violations.append('logP > 5')
            
        # Rule 3: H-bond donors <= 5
        h_donors = Lipinski.NumHDonors(mol)
        if h_donors > 5:
            violations.append('H-donors > 5')
            
        # Rule 4: H-bond acceptors <= 10
        h_acceptors = Lipinski.NumHAcceptors(mol)
        if h_acceptors > 10:
            violations.append('H-acceptors > 10')
            
        # Rule 5: Rotatable bonds <= 10
        rot_bonds = Descriptors.NumRotatableBonds(mol)
        if rot_bonds > 10:
            violations.append('Rotatable bonds > 10')
        
        result['rule_violations'] = violations
        result['is_compliant'] = len(violations) == 0
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing compound {compound_id}: {str(e)}")
        return {
            'compound_id': compound_id,
            'smiles': smiles,
            'is_valid': False,
            'molecular_weight': None,
            'logP': None,
            'is_compliant': False,
            'rule_violations': [f'Processing error: {str(e)}']
        }

def analyze_compounds(
    smiles_list: List[str], 
    compound_ids: Optional[List[str]] = None,
    n_workers: int = 4
) -> Union['pandas.DataFrame', List[Dict[str, Any]]]:
    """
    Analyze a list of compounds represented as SMILES strings.
    
    Parameters
    ----------
    smiles_list : List[str]
        List of SMILES strings representing chemical compounds
    compound_ids : Optional[List[str]], optional
        List of compound identifiers, by default None
        If None, sequential IDs will be generated
    n_workers : int, optional
        Number of parallel workers to use, by default 4
        
    Returns
    -------
    Union[pandas.DataFrame, List[Dict[str, Any]]]
        DataFrame containing analysis results with columns:
        - compound_id: Compound identifier
        - smiles: SMILES string
        - is_valid: Boolean indicating if SMILES is valid
        - molecular_weight: Calculated molecular weight
        - logP: Calculated octanol-water partition coefficient
        - is_compliant: Boolean indicating if compound complies with internal rules
        - rule_violations: List of rule violations
        
        If pandas is not available, returns a list of dictionaries with the same data.
        
    Notes
    -----
    This function uses parallel processing to efficiently handle large datasets.
    Invalid SMILES strings are handled gracefully and marked as invalid in the results.
    """
    # Check and install dependencies if needed
    dependencies_available = check_and_install_dependencies()
    
    # Generate sequential IDs if not provided
    if compound_ids is None:
        compound_ids = [f"CPND{i+1:06d}" for i in range(len(smiles_list))]
    
    # Ensure compound_ids and smiles_list have the same length
    if len(compound_ids) != len(smiles_list):
        raise ValueError("Length of compound_ids must match length of smiles_list")
    
    # If dependencies are not available, return basic results
    if not dependencies_available:
        logger.warning("Required dependencies not available. Returning basic results without calculations.")
        results = []
        for smiles, compound_id in zip(smiles_list, compound_ids):
            results.append({
                'compound_id': compound_id,
                'smiles': smiles,
                'is_valid': None,  # Cannot validate without RDKit
                'molecular_weight': None,
                'logP': None,
                'is_compliant': None,
                'rule_violations': ['Dependencies not available']
            })
        
        try:
            import pandas as pd
            return pd.DataFrame(results)
        except ImportError:
            return results
    
    # Import pandas here after ensuring it's installed
    try:
        import pandas as pd
    except ImportError:
        logger.warning("Pandas not available. Returning results as a list of dictionaries.")
    
    # Prepare inputs for parallel processing
    inputs = list(zip(smiles_list, compound_ids))
    
    # Adjust number of workers based on input size and available cores
    try:
        import multiprocessing
        available_cores = multiprocessing.cpu_count()
        n_workers = min(n_workers, available_cores, len(inputs))
    except (ImportError, NotImplementedError):
        n_workers = min(n_workers, len(inputs))
    
    # Process compounds in parallel if multiprocessing is available
    results = []
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
            # Create a partial function with only smiles and compound_id as arguments
            process_func = lambda x: calculate_properties(x[0], x[1])
            
            # Submit all tasks and collect results
            future_to_input = {executor.submit(process_func, inp): inp for inp in inputs}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_input):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    inp = future_to_input[future]
                    logger.error(f"Unhandled exception processing {inp[1]}: {str(e)}")
                    results.append({
                        'compound_id': inp[1],
                        'smiles': inp[0],
                        'is_valid': False,
                        'molecular_weight': None,
                        'logP': None,
                        'is_compliant': False,
                        'rule_violations': [f'Unhandled error: {str(e)}']
                    })
    except (ImportError, RuntimeError):
        # Fall back to sequential processing if multiprocessing is not available
        logger.warning("Multiprocessing not available. Processing compounds sequentially.")
        for smiles, compound_id in inputs:
            try:
                result = calculate_properties(smiles, compound_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Unhandled exception processing {compound_id}: {str(e)}")
                results.append({
                    'compound_id': compound_id,
                    'smiles': smiles,
                    'is_valid': False,
                    'molecular_weight': None,
                    'logP': None,
                    'is_compliant': False,
                    'rule_violations': [f'Unhandled error: {str(e)}']
                })
    
    # Convert results to DataFrame if pandas is available
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        
        # Sort by compound_id to maintain original order
        df = df.sort_values('compound_id')
        
        return df
    except ImportError:
        # Sort results by compound_id if pandas is not available
        results.sort(key=lambda x: x['compound_id'])
        return results

if __name__ == "__main__":
    # Example usage
    test_smiles = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "C1=CC=C(C=C1)C(=O)O",  # Benzoic acid
        "INVALID_SMILES",  # Invalid SMILES
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"  # Ibuprofen
    ]
    
    results_df = analyze_compounds(test_smiles)
    print(results_df)
