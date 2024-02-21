# Use the base Python image
FROM python:3.10-slim

# Create a non-root user and group with specific UID and GID (you can adjust these values)
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser appuser

# Set the working directory to /app
WORKDIR /app

# Set the HOME environment variable to /app
ENV HOME /app

# Copy project files into the container
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

# Change the ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Expose port 8000
EXPOSE 8000

# Switch to the non-root user
USER appuser

# Command to start the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
