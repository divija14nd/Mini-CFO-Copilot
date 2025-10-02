import pytest
import matplotlib.pyplot as plt
from agent.planner import run_agent
from agent.tools import _load_and_prepare_data

# This fixture loads the data once for all tests, making them run faster.
@pytest.fixture(scope="module")
def data_frames():
    """Fixture to load data once for all tests."""
    files = {
        'actuals': 'fixtures/actuals.csv',
        'budget': 'fixtures/budget.csv',
        'cash': 'fixtures/cash.csv',
        'fx': 'fixtures/fx.csv'
    }
    return _load_and_prepare_data(files)

# --- Test Cases for Each Core Functionality ---

def test_revenue_vs_budget(data_frames):
    """Tests a question about revenue vs. budget for a single month."""
    query = "What was June 2025 revenue vs budget in USD?"
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Revenue for June 2025" in summary
    assert isinstance(figure, plt.Figure)

def test_gross_margin_trend(data_frames):
    """Tests a trend question for a specific number of months."""
    query = "Show Gross Margin % trend for the last 3 months."
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Gross Margin Trend (3 Months)" in summary
    assert isinstance(figure, plt.Figure)

def test_opex_breakdown(data_frames):
    """Tests a question asking for an Opex breakdown."""
    query = "Break down Opex by category for June 2025."
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Opex Breakdown for June 2025" in summary
    assert isinstance(figure, plt.Figure)

def test_cash_runway(data_frames):
    """Tests a general question about cash runway."""
    query = "What is our cash runway right now?"
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    # The summary can be either positive or negative, so we check for both possibilities
    assert "Cash Runway Analysis" in summary or "Cash Flow Positive Analysis" in summary
    assert isinstance(figure, plt.Figure)

def test_single_metric(data_frames):
    """Tests a question for a single metric in a single month."""
    query = "What was the opex in July 2025?"
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Opex for July 2025" in summary
    assert figure is None # This tool should not return a chart

def test_multi_month_metric(data_frames):
    """Tests a comparison question for multiple specific months."""
    query = "Show me revenue for June and July 2025"
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Comparison for Revenue" in summary
    assert "Jun 2025" in summary
    assert "Jul 2025" in summary
    assert isinstance(figure, plt.Figure)

def test_metric_ranking(data_frames):
    """Tests a ranking question (e.g., top N)."""
    query = "What were the top 2 months for revenue?"
    summary, figure = run_agent(query, data_frames)
    assert isinstance(summary, str)
    assert "Top 2 Month(s) for Revenue" in summary
    assert isinstance(figure, plt.Figure)

def test_unknown_question(data_frames):
    """Tests a question the agent shouldn't understand."""
    query = "What is the capital of France?"
    summary, figure = run_agent(query, data_frames)
    assert "Sorry" in summary
    assert figure is None

