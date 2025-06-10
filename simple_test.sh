#!/bin/bash
echo "Testing if we can run Python code"

# Try to find Python
echo "Looking for Python..."
which python || echo "Python not found"
which python3 || echo "Python3 not found"

# Create a simple Python script
echo 'print("Hello from Python")' > test.py

# Try different ways to run it
echo "Trying to run Python script..."
python test.py 2>/dev/null || echo "Failed with python"
python3 test.py 2>/dev/null || echo "Failed with python3"
/usr/bin/python test.py 2>/dev/null || echo "Failed with /usr/bin/python"
/usr/bin/python3 test.py 2>/dev/null || echo "Failed with /usr/bin/python3"

echo "Environment information:"
uname -a
echo "PATH: $PATH"
