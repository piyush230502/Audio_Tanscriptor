# Use the official Python image
FROM python:3.9.21-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirements if using one
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Create upload folder (in case it doesn't exist)
RUN mkdir -p uploads

# Expose Flask port
EXPOSE 5050

# Start the Flask app
CMD ["python", "app.py"]
