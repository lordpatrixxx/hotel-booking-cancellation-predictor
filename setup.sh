#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Setting up Hotel Booking Cancellation Predictor ==="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip --quiet

echo "Installing requirements..."
pip install -r requirements-lock.txt || pip install -r requirements.in

if [ ! -f "artifacts/cancellation_model.joblib" ]; then
    echo "Training model..."
    python train.py
fi

echo "=== Setup complete! Run ./run.sh to start ==="
