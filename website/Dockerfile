FROM python:3.11-slim

# Set the working directory
WORKDIR /website

# Copy the current directory contents into the container at /app
COPY . /website

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Start the flask application
CMD ["python", "-m", "flask","--app",".","run","--host=0.0.0.0", "--port=80"]