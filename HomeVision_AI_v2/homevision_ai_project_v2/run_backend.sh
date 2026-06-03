#!/bin/bash
cd backend
python train_model.py
uvicorn app:app --reload
