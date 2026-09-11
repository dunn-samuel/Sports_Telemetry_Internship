# Summer Economics Research Internship: Autonomous Sports Telemetry ETL Pipeline & Consumer Forecasting

A modular Python data engineering pipeline and econometric forecasting project developed during a Quantitative Summer Research Internship (UEA School of Economics). This architecture autonomously scrapes concurrent viewership figures across major global sporting events, bypassing Client-Side Rendering (CSR) to parse raw backend JSON payloads into a clean dataset of 1,025 intra-match observations.

---

## Project Overview
* **Cloud Deployment & Automation:** Deployed to a **PythonAnywhere** cloud server as an "always-on" background task to guarantee autonomous data polling during live sporting events.
* **Data Engineering:** Engineered an automated, multi-threaded extraction pipeline with a master orchestrator managing distinct parsers for F1, Football, Tennis, Golf, and Rugby.
* **Econometric Modeling:** Estimated dynamic panel regression models in Stata to forecast consumer engagement.
* **Feature Integration:** Merged real-time viewership telemetry with pre-match implied probabilities (derived from betting market odds) to model behavioral engagement heuristics.

---

## Tech Stack & Architecture
* **ETL Pipeline:** Python (`requests`, `pandas`, `json`).
* **Deployment & Hosting:** PythonAnywhere (Cloud Server, Always-On Tasks).
* **Architecture:** Master Orchestrator pattern with modular, sport-specific parser scripts to handle varying API endpoint structures.
* **Statistical Analysis:** Stata (Panel Data Regressions).
* **Data Visualization:** Stata graphics engine.

---

## Key Insights & Outputs
The complete high-dimensional econometric outputs and structural market transformations are synthesized in the attached report. 

* **Consumer Behavior Forecasting:** Successfully modeled human decision-making and viewership elasticity.
* **Data Architecture:** Resolved severe missing-data artifacts inherent in live API polling by implementing robust JSON flattening and error-handling protocols.

---

## Repository Structure
* `/etl_pipeline`: Contains the `Master_Orchestrator.py` and the suite of modular parsing scripts used to bypass CSR and extract backend JSON payloads.
* `/econometrics`: Contains the `Stata_Analysis.do` file executing the panel regression models.
* `/images`: Visual outputs, coefficient plots, and timeline distributions generated via Stata.
* **[Samuel_Dunn_Summary_Report.pdf](./Samuel_Dunn_Summary_Report.pdf)**: The final synthesized high-level report demonstrating the translation of data engineering pipelines into actionable insights.

*(Note: Raw telemetry data and betting odds datasets have been excluded from this public repository to protect private original dataset).*
