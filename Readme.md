# Mutual Fund API Application

This project consists of a FastAPI backend and a React frontend for managing mutual fund investments. The backend handles authentication, fund retrieval, and purchasing functionalities, while the frontend provides a user interface to interact with the backend.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Usage](#usage)

## Prerequisites

Make sure you have the following installed:
- [Python 3.7+](https://www.python.org/downloads/)
- [Node.js 14+](https://nodejs.org/en/download/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [npm](https://www.npmjs.com/get-npm)

## Backend Setup

1. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install Required Packages**:
   ```bash
   pip install fastapi uvicorn python-dotenv pydantic requests pyjwt
   ```

5. **Start the FastAPI Server**:
   ```bash
   uvicorn main:app --reload
   ```
   - This will start the server at `http://127.0.0.1:8000`.

## Frontend Setup

1. **Navigate to the Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Required Packages**:
   ```bash
   npm install
   ```

3. **Start the React Development Server**:
   ```bash
   npm start
   ```
   - This will start the frontend application at `http://localhost:3000`.

## Environment Variables

Create a `.env` file in the `backend` directory and add the following environment variables:

```env
DUMMY_USERNAME=admin
DUMMY_PASSWORD=password
SECRET_KEY=secret_key_for_jwt
RAPIDAPI_KEY=rapidapi_key
```

### Explanation of Environment Variables
- **DUMMY_USERNAME**: The username used for authentication (default: `admin`).
- **DUMMY_PASSWORD**: The password used for authentication (default: `password`).
- **SECRET_KEY**: A secret key used for signing JSON Web Tokens (JWT).
- **RAPIDAPI_KEY**: Your API key for accessing RapidAPI services. Replace `rapidapi_key` with your actual API key.

## Running the Application

1. **Start the Backend**:
   - Follow the steps in the **Backend Setup** section to start the FastAPI server.

2. **Start the Frontend**:
   - Follow the steps in the **Frontend Setup** section to start the React application.

3. **Access the Application**:
   - Open your web browser and navigate to `http://localhost:3000` to access the frontend.
   - The backend API will be available at `http://127.0.0.1:8000`.

## Usage

- Use the dummy credentials (`admin` / `password`) to log in to the application.
- After logging in, you can access various features, including fetching fund families and purchasing mutual fund units.
- The backend also provides RESTful endpoints to interact with the mutual fund API.