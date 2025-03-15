# FlyEase Project Setup Guide

## Project Repositories

This project consists of two separate repositories:
- Backend repository: https://github.com/amirkhalifa285/FlyEase-Backend
- Frontend repository: https://github.com/amirkhalifa285/FlyEase-Frontend

## Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Python 3.11.x** (specifically 3.11.9 if possible)
   - Download from [Python.org](https://www.python.org/downloads/release/python-3119/)
   - Make sure to check "Add Python to PATH" during installation

2. **Node.js and npm** (Latest LTS version)
   - Download from [Node.js website](https://nodejs.org/)

3. **PostgreSQL Client Tools** (OPTIONAL - only needed if you want to inspect the database directly)
   - Not required to run the application
   - The database is hosted remotely on Heroku and doesn't require local PostgreSQL installation
   - Only install if you need to access the database console for debugging

4. **Heroku CLI** (for database connection)
   - Download from [Heroku Dev Center](https://devcenter.heroku.com/articles/heroku-cli)

## Backend Setup

1. **Clone the backend repository**
   ```
   git clone https://github.com/amirkhalifa285/FlyEase-Backend
   cd FlyEase-Backend/FlyEase-Backend
   ```

2. **Create and activate virtual environment**
   ```
   # Create a virtual environment with Python 3.11
   python -m venv env
   
   # Activate on Windows
   env\Scripts\Activate.ps1
   
   # Activate on macOS/Linux
   source env/bin/activate
   ```

3. **Install backend dependencies**
   ```
   # Upgrade pip first
   python -m pip install --upgrade pip
   
   # Install requirements
   pip install -r requirements.txt
   ```

4. **Run the FastAPI backend server**
   ```
   uvicorn main:app --reload
   ```
   The backend should now be running on http://127.0.0.1:8000

## Database Connection

The database is hosted on Heroku and doesn't require local setup. The backend is already configured to connect to the remote database automatically.

**Note: Database inspection is OPTIONAL and not required to run the application.**

If you need to inspect the database for debugging purposes:

1. Install PostgreSQL Client Tools first (see Prerequisites section)

2. **Log in to Heroku**
   ```
   heroku login
   ```

3. **View database information**
   ```
   heroku pg:info --app flyease
   ```

4. **Connect to the database console** (requires PostgreSQL client tools)
   ```
   heroku pg:psql --app flyease
   ```

## Frontend Setup

1. **Clone the frontend repository**
   ```
   # Open a new terminal (keep backend running in original terminal)
   git clone https://github.com/amirkhalifa285/FlyEase-Frontend
   cd FlyEase-Frontend
   ```

2. **Install frontend dependencies**
   ```
   npm install
   ```

3. **Start the React development server**
   ```
   npm start
   ```
   The frontend should now be running on http://localhost:3000

## Running the Complete Application

1. Keep the backend server (uvicorn) running in one terminal
2. Keep the frontend server (npm start) running in another terminal
3. Access the application by navigating to http://localhost:3000 in your browser

## Troubleshooting

1. **Python version issues**
   - Make sure you're using Python 3.11.x
   - If you have multiple Python versions, use `py -3.11 -m venv env` to create the virtual environment

2. **Package installation errors**
   - Try installing problematic packages individually:
     ```
     pip install cffi --no-binary :all: -v
     pip install cryptography -v
     ```

3. **Database connection issues**
   - The application connects to a remote Heroku database automatically
   - No local PostgreSQL installation is required
   - Check internet connectivity if database connection fails

4. **Node.js/npm not found**
   - Make sure Node.js is installed and in PATH
   - Close and reopen terminal after installation
   - Run `node --version` and `npm --version` to verify

5. **Frontend API connection issues**
   - Check that backend is running on the expected port
   - Verify that the frontend is configured to use the correct API URL

