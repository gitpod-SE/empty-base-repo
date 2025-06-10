# Compound Analyzer

A Python tool for analyzing chemical compounds using RDKit. This tool calculates molecular properties and evaluates rule compliance for chemical compounds represented as SMILES strings.

## Features

- Calculates molecular weight and logP (octanol-water partition coefficient)
- Evaluates compliance with internal rules (based on Lipinski's Rule of Five)
- Handles invalid SMILES strings gracefully
- Utilizes parallel processing for efficient handling of large datasets
- Returns results as a Pandas DataFrame

## Installation

### Option 1: Direct Installation

The tool automatically checks for and installs required dependencies (RDKit, Pandas, NumPy) if they are not already present.

```bash
# Clone the repository
git clone <repository-url>
cd compound-analyzer

# Install dependencies
pip install -r requirements.txt

# Make the script executable (Linux/Mac)
chmod +x compound_analyzer.py
```

### Option 2: Using Docker

If you have Docker installed, you can build and run the tool without installing dependencies locally:

```bash
# Build the Docker image
docker build -t compound-analyzer .

# Run the example script
docker run compound-analyzer

# Or run with your own script
docker run -v $(pwd)/your_data:/app/data compound-analyzer python your_script.py
```

## Usage

### As a Python Module

```python
from compound_analyzer import analyze_compounds

# Example list of SMILES strings
smiles_list = [
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
    "C1=CC=C(C=C1)C(=O)O",  # Benzoic acid
    "INVALID_SMILES",  # Invalid SMILES
    "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"  # Ibuprofen
]

# Optional: provide custom compound IDs
compound_ids = ["ASP001", "CAF001", "BNZ001", "INV001", "IBU001"]

# Analyze compounds
results = analyze_compounds(smiles_list, compound_ids, n_workers=4)

# Display results
print(results)

# Access specific properties
print("Molecular weights:", results['molecular_weight'].tolist())
print("Compliant compounds:", results[results['is_compliant']]['compound_id'].tolist())
```

### From Command Line

```bash
python example.py
```

This will run the example included in the script.

## Function Parameters

The `analyze_compounds` function accepts the following parameters:

- `smiles_list` (List[str]): List of SMILES strings representing chemical compounds
- `compound_ids` (Optional[List[str]]): List of compound identifiers (optional)
  - If not provided, sequential IDs will be generated (CPND000001, CPND000002, etc.)
- `n_workers` (int): Number of parallel workers to use (default: 4)

## Return Value

The function returns a Pandas DataFrame with the following columns:

- `compound_id`: Compound identifier
- `smiles`: SMILES string
- `is_valid`: Boolean indicating if SMILES is valid
- `molecular_weight`: Calculated molecular weight
- `logP`: Calculated octanol-water partition coefficient
- `is_compliant`: Boolean indicating if compound complies with internal rules
- `rule_violations`: List of rule violations

## Internal Rules

The tool evaluates compounds against the following rules (based on Lipinski's Rule of Five):

1. Molecular weight < 500
2. LogP ≤ 5
3. Number of hydrogen bond donors ≤ 5
4. Number of hydrogen bond acceptors ≤ 10
5. Number of rotatable bonds ≤ 10

## Error Handling

The tool handles errors gracefully:

- Invalid SMILES strings are marked as invalid in the results
- Processing errors are logged and included in the rule violations
- The function continues processing other compounds even if some fail

## Performance

For large datasets (>1000 compounds), the tool automatically utilizes parallel processing to improve performance. The number of workers can be adjusted using the `n_workers` parameter.

## Handling Large Datasets

When working with large datasets (>1000 compounds), consider the following:

1. Increase the number of workers to match your CPU cores:
   ```python
   results = analyze_compounds(large_smiles_list, n_workers=8)
   ```

2. Process in batches if memory is a concern:
   ```python
   batch_size = 1000
   all_results = []
   
   for i in range(0, len(large_smiles_list), batch_size):
       batch = large_smiles_list[i:i+batch_size]
       batch_ids = compound_ids[i:i+batch_size] if compound_ids else None
       results = analyze_compounds(batch, batch_ids)
       all_results.append(results)
   
   # Combine results
   import pandas as pd
   final_results = pd.concat(all_results)
   ```

3. Save results incrementally to disk:
   ```python
   for i, batch_results in enumerate(all_results):
       batch_results.to_csv(f'results_batch_{i}.csv', index=False)
   ```
