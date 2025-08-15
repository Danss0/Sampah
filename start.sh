#!/bin/bash
set -eu

# Pastikan log langsung tampil
export PYTHONUNBUFFERED=true

# Jalankan dengan Gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
