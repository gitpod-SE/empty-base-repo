FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the scripts executable
RUN chmod +x compound_analyzer.py example.py

# Default command
CMD ["python", "example.py"]
