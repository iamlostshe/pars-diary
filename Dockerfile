# Use a base image with Python
FROM python:3.12-slim-trixie AS base

# Install git and other dependencies
RUN apt-get update && apt-get install -y git

# Copy the UV binary from the UV image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project files
COPY . .

# Start the project
CMD ["uv", "run", "-m", "pars_diary"]
