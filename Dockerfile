#Build image
FROM python:3.13-slim

#Working directory
WORKDIR /app

#Copy the requires file from build context
COPY requirements.txt .

#Install app dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy from local to the image
COPY application ./application

#Expose port on which app will run
EXPOSE 8000

#Start the Uvicorn server,Find app inside application/main.py,Listen on all network interfaces inside the container
CMD ["uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]
