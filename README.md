# FUT Performance Prediction Model
## Project Overview
This project develops a supervised machine learning regression model to predict future FC (FIFA/EA Sports FC) player ratings and market values based on real-world performance statistics (goals, assists, tackles, etc.) from previous seasons. Will involve an interactive UI where users will be able to enter potential season statistics and determine predicted future ratings & performance.

## Tech Stack
- **Python:** Primary language for data processing and model training.
- **Libraries:** Pandas, NumPy, scikit-learn (or XGBoost/LightGBM).
- **Frontend:** Next.js - Builds on your React experience for the user interface, handling player input and displaying predictions.
- **Backend/API:** FastAPI - High-performance Python backend to manage API requests and serve as the intermediary between the frontend and the ML model.
- **Database:** AWS RDS (PostgreSQL) - Managed relational database for structuring and storing historical player stats, ratings, and market value data.
- **Machine Learning:** XGBoost - The high-performance regression model used to train and predict future player ratings and market value.
- **Cloud/Deployment:** AWS SagesMaker - Used for training, deploying, and hosting your XGBoost model as a real-time prediction endpoint.

## Data Sources
Historical FIFA player data and corresponding real-world match performance metrics.

The project is broken into four distinct phases to ensure clean integration and focused development.

### Phase 1: Data Acquisition & Backend Foundation
* **1.1 Database Setup & Schema:** Configure the AWS RDS Free Tier instance and define the core relational schema (`Players`, `Stats`, `Ratings` tables).
* **1.2 Data Ingestion:** Write Python/Pandas scripts to clean and load historical data into PostgreSQL.
* **1.3 Base API:** Set up the initial FastAPI application, define data models (using Pydantic/SQLModel), and confirm connection to RDS via a basic API endpoint (e.g., `/players`).

### Phase 2: Machine Learning Pipeline (SageMaker & XGBoost)
* **2.1 Feature Engineering:** Write complex SQL queries to generate predictive features (e.g., Goals Per 90, age differential) from the raw data.
* **2.2 Model Training:** Use a **SageMaker Notebook Instance** to train the **XGBoost Regressor** and tune hyperparameters for optimal prediction accuracy.
* **2.3 Model Deployment:** Deploy the finalized XGBoost model to a **SageMaker Real-Time Endpoint** for low-latency predictions.

### Phase 3: Full-Stack Integration
* **3.1 Backend Prediction API:** Create the core FastAPI endpoint (`POST /predict`) that handles feature input, calls the external SageMaker Endpoint, and processes the prediction result.
* **3.2 Next.js Setup & UI:** Set up the Next.js frontend, design the player input form, and establish client-side API communication with the FastAPI backend.
* **3.3 Frontend Integration:** Connect the user input form to the `/predict` API and display the returned future Rating/Market Value prediction clearly in the UI.

### Phase 4: Finalization & Production Deployment
* **4.1 Security & Environment:** Implement robust handling of AWS credentials and database strings using environment variables. Adjust RDS security to lock down access.
* **4.2 Containerization:** Dockerize the FastAPI application for consistent deployment environments.
* **4.3 Final Deployment:** Deploy the Next.js frontend (e.g., Vercel) and the FastAPI backend (e.g., AWS Elastic Beanstalk) to finalize the working, end-to-end web application.

---