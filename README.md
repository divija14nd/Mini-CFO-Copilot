# Mini-CFO-Copilot

CFO Copilot is an **AI-powered assistant** that helps financial executives understand business performance by answering questions directly from structured CSV data. It can interpret natural language queries, run the necessary data analysis, and return concise, board-ready answers with charts.

---

## ✨ Features
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

## 🚀 Tech Stack
- **Web Framework:** Streamlit  
- **Data Analysis:** pandas  
- **Charting:** Matplotlib & Seaborn  
- **Testing:** pytest  
- **PDF Export:** reportlab, Pillow  

---

## 📂 Project Structure
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

## ⚙️ Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
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
All tests should pass

## 📄Extra Feature: Export to PDF

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
