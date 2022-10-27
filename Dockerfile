# Initialize Python 3.10 and set current directory.
FROM python:3.10

# Copy project files into working directory.
COPY . /app/
WORKDIR /app

# Install libraqm and its dependencies for image manipulation.
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install libfreetype6-dev libharfbuzz-dev libfribidi-dev meson

# Install requirements using frozen requirements file (pip).
RUN pip install --no-cache-dir -r requirements.txt

# Real-time project view.
ENV PYTHONBUFFERED 1

# Run.
CMD [ "python", "main.py" ]