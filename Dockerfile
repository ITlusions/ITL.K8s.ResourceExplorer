FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container
COPY ./src /app
COPY ./requirements.txt /tmp/requirements.txt
# Install dependencies
RUN uv pip install --no-cache-dir -r /tmp/requirements.txt --system

# Expose the port the app runs on
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
