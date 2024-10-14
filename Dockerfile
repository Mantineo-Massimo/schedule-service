# Step 1: Use an official Python runtime as a base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install any needed Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose port 5000
EXPOSE 5000

# Step 6: Set the FLASK_APP environment variable
ENV FLASK_APP=data_extractor.py

# Step 7: Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
