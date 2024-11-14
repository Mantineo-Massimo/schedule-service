# Step 1: Use an official Python runtime as a base image
FROM quay.io/sclorg/python-311-minimal-c9s

# Step 2: Update the package manager and install essential build tools
RUN microdnf update -y && \
    pip install --upgrade pip setuptools && \
    microdnf clean all

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy the current directory contents into the container at /app
COPY . /app

# Step 5: Install any needed Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Expose port 5000
EXPOSE 5000

# Step 7: Set environment variables
# Control debug mode with environment variable (production = no debug)
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV FLASK_APP=src.main:app

# Step 8: Use Gunicorn to run the app with 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
