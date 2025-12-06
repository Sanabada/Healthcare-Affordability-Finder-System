# Healthcare Affordability Finder

This project helps people **look up and compare hospital procedure prices** from large hospital price files (CMS Hospital Price Transparency data).

---

## Architecture

The system runs inside a virtual environment and exposes a simple UI on the host machine.

<img width="2672" height="1136" alt="image" src="https://github.com/user-attachments/assets/6ae87028-5e8e-4147-97ab-3839c1a46aa9" />


---

## What this project does

- Reads raw hospital price files (large CSVs from multiple hospitals).
- Cleans and standardizes key fields like:
  - Procedure description
  - Hospital name
  - Listed (gross) price
  - Discounted cash price
- Stores:
  - **Processed data** (clean tables)
  - **Models** and **artifacts**
  - **Predictions** for later use
- Lets you search using **simple text** (e.g., `“knee replacement”`, `“MRI brain”`) and see matching procedures with their prices.

---

## Why this is useful

Hospital price files are usually:

- Huge (millions of rows)
- Inconsistent between hospitals
- Full of technical codes and jargon

This project turns them into a **clean, searchable view** so it’s easier to:

- See price ranges for a given procedure
- Compare prices across hospitals
- Get a rough idea of out-of-pocket cash prices

---

## Technologies used

- **Hadoop / HDFS** – store and manage large raw files
- **Hadoop MapReduce** – first-pass cleaning and merging
- **Apache Spark (PySpark)** – further cleaning, analysis, and model training
- **Python** – scripts, notebooks, and search logic
- **SentenceTransformers** – convert procedure descriptions and user queries into embeddings for text search

---
## Exploratory Data Analysis (EDA)

Our main EDA steps focused on understanding price behavior across hospitals:

- Checked basic stats (row counts, missing values, min/median/max) for each price field.
- Plotted distributions of **gross price** and **discounted cash price**  
  (both normal and log scale) to see skewness and outliers.
- Compared prices across hospitals to spot unusually cheap or expensive procedures.
- Looked at how often key fields (description, gross price, discounted cash, payer rates) are missing or zero.
- Examined the relationship between **gross price** and **discounted cash price** using scatter plots and correlation.
<img width="1870" height="1054" alt="image" src="https://github.com/user-attachments/assets/c7bad2f4-2315-45f6-b6bf-fa1ce750c176" />

<img width="1892" height="1064" alt="image" src="https://github.com/user-attachments/assets/83891280-4c72-4c1a-942b-2abf6c2408e5" />


---
## Machine Learning Models

We used Spark ML to model hospital prices:

- Treated **discounted cash price** as the target.
- Used features such as:
  - Gross price
  - Hospital identifier
  - Payer / plan information (encoded as categorical features)
- Built and evaluated regression models in Spark ML
  (regression pipeline with feature vectorization + scaler + regressor).
- Measured performance with standard regression metrics (e.g., RMSE, MAE, R²)
  to see how closely the model can predict discounted cash prices.
---
## Key Findings from Visualizations

From our plots and dashboards we observed:

- Price distributions are **heavily right-skewed** with a few very high outliers.
- After cleaning, most hospitals show a **consistent discount pattern**:
  discounted cash prices are often a fairly stable fraction of the gross price.
- The **correlation between gross price and discounted cash price** is very high,
  which explains why models using gross price as a main feature perform well.
- Some procedures show large price variation across hospitals,
  highlighting potential opportunities for patients to save by comparing hospitals.
- Removing obvious data errors and duplicates significantly tightened
  the price ranges shown in the charts, making comparisons more meaningful.
<img width="1858" height="772" alt="image" src="https://github.com/user-attachments/assets/8367d9c8-56b1-4db1-b352-817418e24262" />
<img width="1852" height="562" alt="image" src="https://github.com/user-attachments/assets/3255aa2c-1926-4ccb-8101-71a48007a868" />

## Model Pipeline:

<img width="962" height="882" alt="image" src="https://github.com/user-attachments/assets/9576c47d-5d51-4e92-a2c2-fcf1f4b86ec9" />

## Key Findings from Visualizations

From our plots and dashboards we observed:

- Price distributions are **heavily right-skewed** with a few very high outliers.
- After cleaning, most hospitals show a **consistent discount pattern**:
  discounted cash prices are often a fairly stable fraction of the gross price.
- The **correlation between gross price and discounted cash price** is very high,
  which explains why models using gross price as a main feature perform well.
- Some procedures show large price variation across hospitals,
  highlighting potential opportunities for patients to save by comparing hospitals.
- Removing obvious data errors and duplicates significantly tightened
  the price ranges shown in the charts, making comparisons more meaningful.



## How it works (high level)

1. **Raw data → HDFS**  
   Raw hospital CSVs are copied into the cluster (RAW zone).

   <img width="2668" height="1374" alt="image" src="https://github.com/user-attachments/assets/cb513526-06c6-4072-9415-7b14e2e561f5" />


3. **Preprocessing (Hadoop + Spark)**  
   - MapReduce and Spark clean and standardize the data.
  
   - <img width="2500" height="1124" alt="image" src="https://github.com/user-attachments/assets/222b80ff-a617-4ced-8cda-fbe56fcfa355" />

   - Output is stored as **PROCESSED** data and **ARTIFACTS** (e.g., feature tables).

4. **Model training**  
   Spark trains models to estimate discounted cash prices and saves them in the **MODELS** area, along with **META DATA** about each run.

5. **Predictions & UI**  
   - Models write **PREDICTIONS** back to storage.  
   - A simple **user interface** running on the host system reads processed data and predictions, and lets users search procedures and view prices.
