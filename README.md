# ParamedicGuard

Parametric Insurance Platform for Gig Workers

## Overview
ParamedicGuard is a full-stack, AI-driven platform providing parametric insurance solutions tailored for the gig economy. By replacing tedious manual claim processes with dynamic risk calculations and automated real-time triggers (like high rainfall or severe AQI levels), it ensures delivery partners an accurate safety net for disruptions out of their control. 

## Project Structure
- **`backend-python/`**: A robust Python FastAPI system providing micro-services for calculating premiums, evaluating real-time weather triggers, executing payouts, processing claims, and managing fraud detection (Trust Engine) telemetry.
- **`frontend-worker/`**: A realistic, mobile-responsive React app designed for gig workers to monitor live conditions (AQI/Rainfall), review their coverage plans, and observe recent payouts. Contains no mock simulation buttons.
- **`frontend-admin/`**: A React app containing the overarching system console for administrators to view platform performance metrics, loss ratios, zone risk distributions, and flagged anomalous claims.

---

## Prerequisites
Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/en/) (v16.14 or later)
- [Python](https://www.python.org/downloads/) (v3.9 or later)
- [Git](https://git-scm.com/)

---

## Installation & Running Guide

### 1. Clone the repository
```bash
git clone https://github.com/Jarvis-the-og/trial.git
cd trial
```
*(If you renamed the local directory upon cloning, `cd` into your project directory instead)*

### 2. Run the Backend API (Python / FastAPI)
The Python application powers our trigger systems and logic algorithms. Open a terminal and run:

```bash
cd backend-python

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install strictly required dependencies
pip install -r requirements.txt

# Start the uvicorn development server
uvicorn main:app --reload --port 8000
```
This boots up the backend. The API docs can be visited directly at `http://127.0.0.1:8000/docs`.

### 3. Run the Worker Frontend
The worker dashboard is powered by Vite + React and interfaces directly with the backend. Open a **new terminal tab**:

```bash
cd frontend-worker

# Install necessary libraries
npm install

# Start the dev server
npm run dev
```
The Worker Dashboard will typically be exposed at `http://localhost:5173`.

### 4. Run the Admin Frontend
The administrative oversight dashboard provides health analytics on fraud, payouts, and incoming data streams. Open another **new terminal tab**:

```bash
cd frontend-admin

# Install necessary libraries
npm install

# Start the dev server on a different port to avoid conflicts
npm run dev -- --port 5174
```
The Admin Dashboard will be exposed at `http://localhost:5174` (or whatever alternative port Vite dictates).

---

## Technical Highlights
- **Micro-Premiums System**: Premiums explicitly adapt based on chosen delivery zones (e.g., standard vs sub-zones), the specific labor platform, and risk probability profiles (weather, traffic disruption).
- **Automated Payouts via Trust Engine**: Payouts systematically filter through an internal engine that calculates risk parameters based on device IP tracking and historical anomalies to enforce fraud monitoring realistically.
- **No Simulation on the Frontline**: The worker application accurately mirrors a deployed product architecture, limiting mock triggers solely to underlying platform APIs.
