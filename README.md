# Mini-CFO-Copilot

CFO Copilot is an **AI-powered assistant** that helps financial executives understand business performance by answering questions directly from structured CSV data. It can interpret natural language queries, run the necessary data analysis, and return concise, board-ready answers with charts.

---
## Table of Contents

- [Project Overview](#project-overview)  
- [Data & Metrics](#data--metrics)  
- [Built Features](#built-features)  
- [Rule Engine Features](#rule-engine-features)  
- [Tech Stack](#tech-stack)  
- [Project Structure](#project-structure)  
- [Setup and Installation](#setup-and-installation)  
- [Extra Feature: Export to PDF](#extra-feature-export-to-pdf)  
- [Example Questions to Ask](#example-questions-to-ask)  
- [License](#license)  
- [Contributing](#contributing)  
- [Future Work](#future-work)  

---

## Project Overview

CFOs rely on monthly financial summaries to understand how the business is performing, spot risks, and explain results to the board. Traditionally, preparing these reports takes hours of manual work: pulling numbers from finance systems, reconciling actuals with budget, calculating margins, and creating charts for presentations.

As part of this project, I built **Mini CFO Copilot**, a **rule-based agent** that automates this workflow.  
The assistant is not a full finance platform — instead, it demonstrates how an end-to-end workflow can be designed where:

1. A **question is interpreted** in natural language  
2. The agent **runs the right data functions** on structured CSVs  
3. The system **returns concise, board-ready answers with charts**  

This project was intentionally scoped to be small but complete, combining **data analysis, agent design, and user experience** into a working product.

---

## Data & Metrics

The CFO Copilot is powered by **four structured CSV files** that simulate monthly financial inputs:

- **actuals.csv** → monthly actuals by entity/account  
- **budget.csv** → monthly budget by entity/account  
- **fx.csv** → currency exchange rates  
- **cash.csv** → monthly cash balances  

📎 [CSV Dataset Link](https://docs.google.com/spreadsheets/d/e/2PACX-1vRPAvun4Gcow4ZNgHAAdE5b36kJgnqeVNNCQLfbzc_T6-IGLxJJsxmms9TJPDn61Q/pub?output=xlsx)

### Metrics Implemented
- **Revenue (USD):** actual vs budget  
- **Gross Margin %:** (Revenue – COGS) ÷ Revenue  
- **Opex total (USD):** grouped by `Opex:*` categories  
- **EBITDA (proxy):** Revenue – COGS – Opex  
- **Cash runway:** cash ÷ avg monthly net burn (last 3 months)  

---

## Built Features

- **Chat Interface:** CFO can type questions in natural language  
- **Rule-Based Agent:** classifies intent → runs data functions → returns text + chart  
- **Charts:** generated via Matplotlib & Seaborn, displayed inline in Streamlit  
- **Export to PDF:** option to export answers or the entire conversation into a clean report  

---


## Rule Engine Features
The agent can understand a wide variety of financial questions, including:

- **Revenue vs. Budget**  
  *Example:* “What was June 2025 revenue vs budget?”

- **Trend Analysis**  
  *Example:* “Show me the Gross Margin trend for the last 3 months.”

- **Categorical Breakdown**  
  *Example:* “Break down Opex by category for June.”

- **Key Metrics**  
  *Examples:* “What is our cash runway right now?” or “What was EBITDA in July?”

- **Entity-Level Performance**  
  *Example:* “Which entity missed its revenue budget in June?”

- **Performance Ranking**  
  *Examples:* “What were the top 3 months for revenue?” or “What was the worst month for Gross Margin?”

- **Multi-Month Comparison**  
  *Example:* “Compare revenue for June and July 2025.”

---

## Tech Stack
- **Web Framework:** Streamlit  
- **Data Analysis:** pandas  
- **Charting:** Matplotlib & Seaborn  
- **Testing:** pytest  
- **PDF Export:** reportlab, Pillow  

---

## Project Structure
```
cfo-copilot/
│
├── agent/
│ ├── init.py
│ ├── planner.py # The agent's "brain" - interprets questions
│ ├── tools.py # The agent's "hands" - performs calculations & makes charts
│ └── pdf_export.py # Handles PDF generation
│
├── fixtures/
│ ├── actuals.csv
│ ├── budget.csv
│ ├── cash.csv
│ └── fx.csv
│
├── tests/
│ ├── init.py
│ └── test_agent.py # Tests for the agent's logic
│
├── app.py # The main Streamlit application
├── README.md # This file
└── requirements.txt # Project dependencies
```

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/divija14nd/Mini-CFO-Copilot.git
cd cfo-copilot
```
### 2. Create and Activate Virtual Environment

For MacOS/Linux
```bash
python3 -venv .venv
source .venv/bin/activate
```

For Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```
### 3. Install Dependencies
Install all required libraries
```bash
pip3 install -r requirements.txt
```
### 4. Running the Application
Start the Streamlit web app
```bash
streamlit run app.py
```
This will open Mini CFO Copilot in your browser. 

### 5. Running the Tests
Verify that agent's core logic is working running the following on tests.
```bash
PYTHONPATH=. pytest
```
All tests should pass.

## Extra Feature: Export to PDF

Export Single Answer: Each response with a chart includes an "Export Answer button

Export Conversation: Use the "Download Conversation" button in the sidebar to save the full ocnversation.

## Example Questions to ask

“What was June 2025 revenue vs budget in USD?”

“Show Gross Margin % trend for the last 3 months.”

“Break down Opex by category for June.”

“What is our cash runway right now?”

“Which entity missed its revenue budget in June?”

“What were the top 3 months for revenue?”

“Compare revenue for June and July 2025.”

“What was EBITDA in July 2025?”

“What was the worst month for Gross Margin?”

“Show me revenue trend vs budget for the last 6 months.”


---

## License
This project is licensed under the MIT License.  
You are free to use, modify, and distribute it with proper attribution.

---

## Contributing
Contributions, issues, and feature requests are welcome!  
Feel free to open a pull request or create an issue to suggest improvements.

---

## Future Work
- Use Large Language Models anf GenAI for prompt refining.
- Support for additional file formats (Excel, Google Sheets)  
- More advanced financial KPIs (EBITDA margin, ROI, NPV)  
- Interactive dashboards beyond Streamlit  
- Integration with real-time financial APIs  


