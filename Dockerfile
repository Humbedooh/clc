# syntax=docker/dockerfile:1
FROM python:3.8
COPY server /x1/server
EXPOSE 8080
RUN mkdir -p /x1/scratch
WORKDIR /x1/server
RUN ["pip3", "install", "-r", "requirements.txt"]
CMD ["python3", "main.py"]
