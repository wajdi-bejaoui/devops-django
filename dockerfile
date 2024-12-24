# # Use the official Python image as the base image
# FROM python:3.12-slim

# # Install dependencies for mysqlclient
# RUN apt-get update && apt-get install -y \
#     pkg-config \
#     libmariadb-dev \
#     build-essential

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the current directory (your project) to /app inside the container
# COPY . /app/

# # Install required Python packages from the requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose port 8000 to access the app
# EXPOSE 8000

# # Command to run the Django development server when the container starts
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



# # FROM python:3.12-slim: This tells Docker to use Python 3.12 on a slim Linux image as the base for your container.
# # WORKDIR /app: This sets the working directory inside the container to /app.
# # COPY . /app/: This copies all the files in your current directory (your Django project files) into /app/ inside the container.
# # RUN pip install --no-cache-dir -r requirements.txt: Installs the dependencies listed in the requirements.txt file.
# # EXPOSE 8000: Exposes port 8000 to access the Django app.
# # CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]: Runs the Django development server on port 8000.


FROM python:3.12-slim



# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Collect static files
# RUN python manage.py collectstatic --noinput

# Run the application
# CMD ["gunicorn", "auth.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["sh", "-c", "python manage.py migrate && gunicorn auth.wsgi:application --bind 0.0.0.0:8000"]


