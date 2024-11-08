# Step 1: Use an official Python runtime as a base image
FROM python:3.11-minimal

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install any needed Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose port 5000
EXPOSE 5000

# Step 6: Set environment variables
# Control debug mode with environment variable (production = no debug)
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV FLASK_APP=src.main:app

# Step 7: Use Gunicorn to run the app with 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
