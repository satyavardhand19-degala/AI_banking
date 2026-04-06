# How to Run the Vaani Banking Assistant Locally

This guide explains how to start the Vaani project on your local machine for development and testing.

## 1. Environment Setup

First, ensure you have Python 3.11+ installed.

Open a terminal or command prompt in the root of the project directory and pull down any required modules by setting up your Python virtual environment inside the `backend` folder:

```bash
cd backend

# Create a virtual environment (Windows)
python -m venv win_venv
# Or on Mac/Linux:
# python3 -m venv venv

# Activate the virtual environment (Windows)
win_venv\Scripts\activate
# Or on Mac/Linux:
# source venv/bin/activate
```

Next, install the required packages:
```bash
pip install -r requirements.txt
```

## 2. Configuration Settings

Create your local `.env` configuration file. The backend expects this to run securely:
```bash
# Still inside the `backend` folder, duplicate the example env:
cp ../.env.example .env
```
_Note: The application has built-in mock fallbacks. If you do not have an OpenAI or Sarvam API key right now, you can leave those fields blank or use placeholder text, and the app will gracefully fallback to "Demo Mode"._

## 3. Initialize the Database

For local development, Vaani handles the heavy lifting by using a local SQLite vault database. Before you boot up the server, seed it with initial mock banking data:

```bash
# Ensures your database is perfectly staged
python init_local_db.py
```
This generates `local_vault.db` containing mock customers, accounts, and 60 realistic transactions.

## 4. Run the Backend Server

Start up the FastAPI backend using `uvicorn`. The backend automatically serves the frontend static files on its root path.

```bash
# Start the server with Auto-Reload enabled
python -m uvicorn main:app --reload
```

## 5. Use the Application

Once Uvicorn verifies that the database is connected and displays `Application startup complete`, open your web browser and navigate directly to:

**[http://localhost:8000](http://localhost:8000)**

You should now see the premium Vaani Banking Dashboard! You can click the Microphone to use voice controls, or type commands like _"Show all customers"_ directly into the query prompt.

## Need to Stop the Server?
To gracefully shut down the server when you are done, simply go back to your terminal running Uvicorn and press `Ctrl + C`.
