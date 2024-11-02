FROM python:3.10.11-alpine3.18

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

# Copy the project directories (blum and memefi) into the container
COPY . .

# Expose port 3000 for the memefi service
EXPOSE 3000
CMD ["sh", "-c", "(python3 app.py) & (python3 main.py -a 1)"]
