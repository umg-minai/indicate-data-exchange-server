## Introduction

This program implements the server (aka. hub) part of the INDICATE data exchange protocol.

## Requirements.

Python >= 3.10

## Installation

To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
```

## Usage

```bash
PYTHONPATH=. uvicorn indicate_data_exchange_server.main:app --host 0.0.0.0 --port 8080
```

and open your browser at `http://localhost:8080/docs/` to see the docs.
