FROM python:3
COPY . /app
WORKDIR /app

# Install any necessary dependencies
RUN pip install fastapi uvicorn

# Command to run the FastAPI server when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]