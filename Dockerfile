FROM python:3

WORKDIR /src
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .
CMD python -m flask run
EXPOSE 5000
