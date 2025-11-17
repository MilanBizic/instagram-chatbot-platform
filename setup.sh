#!/bin/bash

echo "🚀 Instagram Chatbot Platform - Quick Setup"
echo "============================================"

# Backend setup
echo ""
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your database credentials!"
fi

cd ..

# Frontend setup
echo ""
echo "📦 Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your PostgreSQL database URL"
echo "2. Start backend: cd backend && source venv/bin/activate && python main.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo ""
echo "📖 See README.md for Instagram API setup instructions"
