# Use Python 3.12.9 as base image
FROM python:3.12.9-slim

# Set working directory
WORKDIR /

# Copy requirements first to leverage Docker cache
COPY frontend/requirements.txt /app/

# Copy the scraper directory to root level
COPY scraper /scraper/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the frontend application
COPY frontend/ /app/

# Create output directory
RUN mkdir -p /app/output

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "/app/frontend.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
