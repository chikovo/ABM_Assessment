FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set working directory
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies including Playwright stealth and Pytest
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries
RUN playwright install chromium

# Copy application source code
COPY . .

# Environment setup
ENV PYTHONUNBUFFERED=1

# By default, run the tests to verify the container image works
CMD ["pytest", "tests/", "-v"]
