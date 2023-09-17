# Use slim package only
FROM python:3.8-slim

# Copy requirements file
COPY ./requirements.txt /

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the excution code
COPY ./embedding_helper.py /


