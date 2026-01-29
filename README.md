# FUT Performance Prediction Model
## Project Overview
This project develops a supervised machine learning regression model to predict future FC (FIFA/EA Sports FC) player ratings and market values based on real-world performance statistics (goals, assists, tackles, etc.) from previous seasons. Will involve an interactive UI where users will be able to enter potential season statistics and determine predicted future ratings & performance.

## Tech Stack
- **Python:** Primary language for data processing and model training.
- **Libraries:** Pandas, NumPy, XGBoost.
- **Frontend:** Next.js 
- **Backend/API:** FastAPI
- **Database:** AWS RDS (PostgreSQL) - storing historical player stats, ratings, and market value data.
- **Machine Learning:** XGBoost - regression model used to train and predict future player ratings and market value.
- **Cloud/Deployment:** AWS Lambda via Magnum - to be implemented.

## Data
The complete data set is available on Kaggle. For more specific datasets that are 'ML Ready' with engineered features, please message me.
https://www.kaggle.com/datasets/jacksonjohannessen/fifa-and-irl-soccer-player-data
https://www.linkedin.com/in/jackyjoh/

## Data Sources
Historical FIFA player data and corresponding real-world match performance metrics. 'Top' 10 leagues and FIFA data from seasons 17/18 through 24/25.
Data collected through web-scraping FBref & various Kaggle datasets of FC player data.



---
