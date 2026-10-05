FROM python:latest
WORKDIR /app
COPY . /app
USER root
RUN pip install -r requirements.txt
CMD ["python", "app.py"]