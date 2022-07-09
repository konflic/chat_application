# Client - Server chat application

This app represents chat application based on server - clients architecture. 
Multiple clients allowed for communication. 

## Install

Follow the basic python project setup. 
Minimum python version is 3.7.5.

```bash
python -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requiremetns.txt
```

## Run

```bash
>>> python3 backend/server.py
Started server on: 127.0.0.1:54355
=> Start accepting client connections

>>> python3 backend/client.py
HOST:PORT 127.0.0.1:54355
Username: test
```
