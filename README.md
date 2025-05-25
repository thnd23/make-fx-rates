# Make FX Rates 
_A blueprint for a scalable & efficient data pipeline for managing foreign exchange rates._

## Overview  
Make FX Rates is a **high-performance ETL solution** designed to fetch, store, and synchronize **foreign exchange (FX) rates** efficiently.  
It utilizes **Redis for fast caching**, **JSON for persistent storage**, and **Poetry for dependency management** to ensure seamless execution and scalability.

## Core Features  
✔ **Automated FX rate extraction** from the [Exchange Rates API](https://open.er-api.com/)  
✔ **Fast caching with Redis** to minimize API calls and reduce latency  
✔ **Persistent JSON storage** as a fallback when Redis isn't available  
✔ **Multi-level logging** for structured error tracking and debugging  
✔ **Poetry-powered dependency management** for streamlined installation and portability  
✔ **Robust error handling** to gracefully manage API failures and Redis downtime  

## Project Structure  
```
make-fx-rates/
│── logs/                   # Stores execution logs per run
│── currency_rates.json      # Local JSON storage for FX rates
│── main.py                  # ETL pipeline script
│── pyproject.toml           # Poetry-based dependencies
│── README.md                # Project Documentation
```

## Installation & Setup  
### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/thnd23/make-fx-rates.git
cd make-fx-rates
```

### 2️⃣ Install Dependencies via Poetry  
This project uses **Poetry** for dependency management. Install Poetry first:  
```bash
pip install poetry
```
Then, install dependencies:  
```bash
poetry install
```

### 3️⃣ Start Redis  
Redis is used as a **fast caching layer** for exchange rates. Ensure it's running:  
```bash
redis-server
```
*Note:* If Redis isn't available, the pipeline **falls back to JSON storage**.

### 4️⃣ Run the ETL Pipeline  
```bash
poetry run python .
```

## How It Works  
1️⃣ **Check Redis first** → If **today's FX rates exist**, no API call is made  
2️⃣ **Fallback to JSON** → If Redis is **unavailable**, JSON is checked  
3️⃣ **If neither source has today's data**, FX rates are **fetched via API**  
4️⃣ **Data is stored** in both Redis & JSON, ensuring **redundancy**  
5️⃣ **Structured logs** track execution in the `/logs` folder  

##  Logging System  
**Multi-Level Logging for Better Debugging**  
✔ **INFO** → Successful operations (data stored, Redis connected)  
✔ **WARNING** → Recoverable issues (Redis unavailable, retrying API calls)  
✔ **ERROR** → Critical failures (API unavailable after retries)  

**Logs are stored in `logs/`**, each execution generating a separate file.

# FX Rate Data Pipeline: Reasoning and Approach  

## 1️⃣ Evaluating Market Options  
### Potential Sources for Currency Rates  
- **Exchange Rate API** ([https://open.er-api.com](https://open.er-api.com)) – Reliable, well-documented API  
- **European Central Bank (ECB)** – Official currency rates with historical data  
- **Open Exchange Rates** – Offers real-time exchange rates with API access  
- **CurrencyLayer** – Provides FX rates with extensive currency support  

### Selection Criteria  
- **Reliability** → Data should come from a credible financial institution or well-maintained service  
- **Real-time access** → Ideally provides up-to-date market rates rather than delayed values  
- **Latency & Availability** → API response times must be fast and consistent  
- **Pricing & Limits** → Cost-effectiveness and API rate limits need evaluation  

### Risks  
- **Data discrepancies** → Rates might differ slightly between sources due to methodology  
- **API downtime** → Service outages can impact real-time updates  
- **Regulatory changes** → Compliance concerns may arise based on country or API provider  
- **Rate limits** → Restrictions could prevent large-scale querying  

### Thought Process in Evaluating  
Given the requirements of **real-time FX rate retrieval**, we prioritize **speed, reliability, cost-effectiveness, and ease of integration**.  
The **Exchange Rate API** is selected due to its **free access**, **fast responses**, and **clear documentation** for seamless integration.  

---

## 2️⃣ ETL Pipeline Development  
### Extraction  
- **Utilizing API calls** to fetch real-time FX rates  
- **Retries with exponential backoff** to handle API failures  
- **Caching with Redis** to minimize redundant API requests  

### Transformation  
- **Standardizing the rate format** (e.g., USD → base currency)  
- **Handling missing values** to ensure data integrity  
- **Optimizing structure for conversion calculations**  

### Load  
- **Redis** → In-memory storage for fast access in page service requests  
- **JSON** → Persistent storage for long-term data retention  
- **Future Plan: Parquet** → Optimized format for analytical queries  

### ETL vs. ELT Approach  
**ETL (Extract → Transform → Load) is chosen** to clean and preprocess data **before storage**, ensuring optimized data retrieval.  
**ELT (Extract → Load → Transform) is avoided** as transformation at query time would slow down performance for real-time processing.

---

## 3️⃣ Module Readiness & Design  
### Proof of Concept vs. Production Readiness  
- **Current state** → Functional implementation, but scalable enhancements planned  
- **Production enhancements** → Airflow scheduling, API monitoring, logging improvements  

### Tools & Language Choice  
- **Python** → Widely used, great libraries for data handling  
- **Redis** → High-speed cache for quick queries  
- **Poetry** → Dependable package management  
- **Parquet (Future)** → Better query performance for large datasets  

### Best Practices Implemented  
- **Modular architecture** → Easy maintenance and scaling  
- **Structured logging** → Debugging and tracking execution  
- **Error handling** → Handling API failures & Redis downtime  

---

## 4️⃣ Deployment & Integration  
###  Deployment Strategy  
- **Airflow (Future)** → Scheduled ETL jobs for automated updates  
- **Version control via GitHub** → Ensuring collaboration  

### Integration Into a Broader Data Model  
- **Redis handles fast service queries**  
- **JSON ensures persistent historical data storage**  
- **Parquet enables efficient analytical querying** (planned)  

### Communicating Project Goals  
- **Simplifies access to real-time FX rates** for applications needing currency conversion  
- **Improves response times** through Redis caching  
- **Ensures long-term accessibility** for financial data insights  

### Value to Organization  
- **Reduces reliance on frequent API calls** → Lowers data retrieval costs  
- **Enhances system performance** → Quick FX rate lookups via Redis  
- **Supports analytical needs** → Future Parquet conversion for deeper financial insights  
- **Optimized for scalability** → Designed for production readiness  

---

## Future Enhancements  
- **Airflow integration** for scheduled execution  
- **Better monitoring & analytics** for tracking API failures  
- **Future conversion to Parquet for optimized storage**  

Transitioning from **JSON to Parquet** will offer advantages:  
- **Columnar storage** → Improves query performance and minimizes I/O costs  
- **Optimized compression** → Reduces storage footprint while retaining accuracy  
- **Enhanced scalability** → Easier integration into analytics frameworks  

This will be particularly useful for **batch processing** and **historical trend analysis**, ensuring FX rate data remains accessible and performant in analytical workflows.  