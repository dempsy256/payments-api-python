# payments-api-python

# Fake Payment API

## Overview
This project is a RESTful API built with Python and FastAPI that simulates a payment processing server. It handles core payment flows including creating customers, authorizing payments, capturing/failing payments, and processing refunds. 

The entire application was built using strict **Test-Driven Development (TDD)**, ensuring that every feature, edge case, and security requirement was driven by a failing test before implementation.

## Setup Instructions

To run this project locally, you will need Python installed on your machine.

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link-here>
   cd payments-api-python

2. **Create and activate a virtual environment (recommended):**
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate

3. **Install the dependencies:**
pip install fastapi uvicorn pytest httpx pydantic

4. **Start the local development server:**
uvicorn src.main:app --reload
NB: The server will run at http://127.0.0.1:8000. You can view the interactive API documentation by navigating to http://127.0.0.1:8000/docs in your browser.

**How to Run Tests**
This project uses pytest and FastAPI's TestClient for automated routing and boundary testing.

To run the entire test suite, simply execute the following command in your terminal from the root project directory:
pytest in bash
This will run all endpoint tests, edge-case checks, and simulated 500-level security failure tests.

**Reflection**
Completing this assignment completely shifted how I approach building software. Adhering to strict Test-Driven Development (writing the failing test, making the git commit, and then writing the implementation code) initially felt slow, but it ultimately saved me hours of debugging by catching logic errors immediately. The most challenging but rewarding part was implementing Task 5's edge cases and security requirements. Learning how to use FastAPI's global exception handlers to intercept 500-level crashes and RequestValidationErrors—ensuring sensitive stack traces never leak to the client—showed me the difference between writing code that simply "works" and writing code that is truly production-ready.