FROM python:3.10
LABEL maintainer="kn99.allen@gmail.com"

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD [ "python3", "app.py" ]