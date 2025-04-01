# Use Python 3.12.9 as base image
FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY frontend/requirements.txt ./requirements.txt

# Copy the scraper directory
COPY scraper /app/scraper/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application maintaining the structure
COPY frontend/static /app/static/
COPY frontend/pages /app/pages/
COPY frontend/*.py /app/
COPY frontend/.env* /app/

# Create output directory
RUN mkdir -p /app/output

# Expose the port Streamlit runs on
EXPOSE 8501

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Run the application
CMD ["streamlit", "run", "/app/0_Input_Form.py", "--server.port", "8501", "--server.address", "0.0.0.0"]