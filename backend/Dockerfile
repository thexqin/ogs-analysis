FROM python:3.11.12
ADD requirements.txt /
RUN pip install -U pip --no-cache-dir
RUN pip install -r /requirements.txt --no-cache-dir
ADD app.py /
ENV PYTHONUNBUFFERED=1
CMD ["python", "./app.py"]