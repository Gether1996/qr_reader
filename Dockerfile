# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/
ENV DJANGO_SETTINGS_MODULE=qr_reader_django.settings
# Ensure STATIC_ROOT exists and build hashed assets
# (this creates /app/staticfiles/** and staticfiles.json)
RUN mkdir -p /app/staticfiles \
 && python manage.py collectstatic --clear --noinput -v 2

# Expose the port the Django app runs on
EXPOSE 8000

# Run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]