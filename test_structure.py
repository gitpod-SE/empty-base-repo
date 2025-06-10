#!/usr/bin/env python3
"""
Simple test script to verify the structure of the compound_analyzer module.
"""

import os
import sys

# Check if the script exists
if os.path.exists('compound_analyzer.py'):
    print("✓ compound_analyzer.py exists")
else:
    print("✗ compound_analyzer.py not found")
    sys.exit(1)

# Check if README exists
if os.path.exists('README.md'):
    print("✓ README.md exists")
else:
    print("✗ README.md not found")

# Check if requirements.txt exists
if os.path.exists('requirements.txt'):
    print("✓ requirements.txt exists")
else:
    print("✗ requirements.txt not found")

# Check if example.py exists
if os.path.exists('example.py'):
    print("✓ example.py exists")
else:
    print("✗ example.py not found")

# Try to import the module
try:
    sys.path.append(os.getcwd())
    from compound_analyzer import analyze_compounds, calculate_properties, check_and_install_dependencies
    print("✓ Module imports successfully")
    
    # Check function signatures
    import inspect
    
    # Check analyze_compounds parameters
    analyze_sig = inspect.signature(analyze_compounds)
    params = list(analyze_sig.parameters.keys())
    if 'smiles_list' in params and 'compound_ids' in params and 'n_workers' in params:
        print("✓ analyze_compounds has correct parameters")
    else:
        print("✗ analyze_compounds has incorrect parameters:", params)
    
    # Check calculate_properties parameters
    calc_sig = inspect.signature(calculate_properties)
    params = list(calc_sig.parameters.keys())
    if 'smiles' in params and 'compound_id' in params:
        print("✓ calculate_properties has correct parameters")
    else:
        print("✗ calculate_properties has incorrect parameters:", params)
    
    print("\nStructure verification complete. The module appears to be correctly structured.")
    
except ImportError as e:
    print(f"✗ Failed to import module: {str(e)}")
except Exception as e:
    print(f"✗ Error during verification: {str(e)}")
