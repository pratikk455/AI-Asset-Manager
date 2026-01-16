#!/bin/bash
cd /Users/pratikshrestha/shrestha-capital/backend
export $(cat .env | xargs)
cd api
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
