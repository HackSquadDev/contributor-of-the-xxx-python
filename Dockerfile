# Initialize Python 3.11 and set current directory.
FROM python:3.11

# Copy project files into working directory.
COPY . /app/
WORKDIR /app

# Install requirements using frozen requirements file (pip).
RUN pip install --no-cache-dir -r requirements.txt

# Real-time project view.
ENV PYTHONBUFFERED 1

# Run.
CMD [ "python", "main.py" ]