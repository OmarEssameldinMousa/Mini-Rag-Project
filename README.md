# mini-rag

This is a minimal implementation of TAG model for question answering

## Requirements 

- Python 3.8 or higher

### Install python and activate your virtual environemnt

1) start virtual environment
```bash
$ python3 -m venv env
```

2) activate the virtual environment
```bash 
$ source env/bin/activate
```


# installation 

### install the required packages
```bash
$ pip3 install -r requirements.txt
```

```bash 
$ cp .env.example .env
```

## Run Docker compose Services
```bash
$ cd docker
$ cp .env.example .env
```


## Run the FastAPI server 

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection 
Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)# Mini-Rag-Project

