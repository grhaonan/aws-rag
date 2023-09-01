# Use Python 3.8 image
FROM public.ecr.aws/lambda/python:3.8

# Set working directory
WORKDIR /app

# Copy requirements file
COPY ./app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY ./app /app

# Expose the FastAPI application port
EXPOSE 8000

# Set PYTHONPATH, this is important otherwise CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] can't find relative modules
ENV PYTHONPATH=/app

# Define entrypoint to run the FastAPI app
CMD ["main.handler"]
