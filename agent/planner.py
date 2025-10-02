import re
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from .tools import (
    get_revenue_vs_budget, get_opex_breakdown, _calculate_net_burn,
    get_cash_runway, get_cash_projection, get_ebitda, get_metric_trend,
    get_revenue_variance_by_entity, get_cash_balance_trend, get_metric_ranking,
    get_single_metric, get_multi_month_metric, get_gross_margin_trend
)

def run_agent(query: str, data_frames: dict):
    """The main entry point for the agent."""
    intent_data = get_intent(query, data_frames)
    intent = intent_data.get("intent")
    
    # --- Route to the correct tool based on intent ---
    if intent == "revenue_vs_budget":
        return get_revenue_vs_budget(intent_data["month"], data_frames)
    elif intent == "opex_breakdown":
        return get_opex_breakdown(intent_data["month"], data_frames)
    elif intent == "cash_runway_projection":
        avg_burn, latest_cash, last_month = _calculate_net_burn(data_frames)
        if avg_burn is None:
            return "Not enough data to calculate cash runway or projection.", None
        if avg_burn > 0:
            return get_cash_runway(avg_burn, latest_cash, last_month, data_frames)
        else:
            return get_cash_projection(-avg_burn, latest_cash, last_month, data_frames)
    elif intent == "ebitda_single_month":
        return get_ebitda(intent_data["month"], data_frames)
    elif intent == "metric_trend":
        return get_metric_trend(intent_data["metric"], intent_data["months"], data_frames)
    elif intent == "gross_margin_trend":
        return get_gross_margin_trend(intent_data["months"], data_frames)
    elif intent == "revenue_variance_by_entity":
        return get_revenue_variance_by_entity(intent_data["month"], data_frames)
    elif intent == "cash_balance_trend":
        return get_cash_balance_trend(intent_data["months"], data_frames)
    elif intent == "metric_ranking":
        return get_metric_ranking(intent_data["metric"], intent_data["ranking"], intent_data["n"], data_frames)
    elif intent == "single_metric":
        return get_single_metric(intent_data["metric"], intent_data["month"], data_frames)
    elif intent == "multi_month_metric":
        return get_multi_month_metric(intent_data["metric"], intent_data["months"], data_frames)
    else:
        return "Sorry, I'm not equipped to answer that question. Please try asking about revenue, opex, cash, or margins.", None

def get_intent(query: str, data_frames: dict) -> dict:
    """Classifies the user's intent based on keywords."""
    query = query.lower()
    months = _extract_months(query, data_frames)
    
    # --- Ranking / Extrema ---
    ranking_match = re.search(r'(top|bottom|highest|lowest|best|worst)\s*(\d*)', query)
    if ranking_match:
        ranking_type = ranking_match.group(1)
        n = int(ranking_match.group(2) or 1)
        ranking = 'top' if ranking_type in ['top', 'highest', 'best'] else 'bottom'
        if 'revenue' in query: return {"intent": "metric_ranking", "metric": "Revenue", "ranking": ranking, "n": n}
        if 'opex' in query: return {"intent": "metric_ranking", "metric": "Opex", "ranking": ranking, "n": n}
        if 'ebitda' in query: return {"intent": "metric_ranking", "metric": "EBITDA", "ranking": ranking, "n": n}
        if 'gross margin' in query: return {"intent": "metric_ranking", "metric": "Gross Margin", "ranking": ranking, "n": n}

    # --- Trend Analysis ---
    if 'trend' in query or 'history' in query or 'historical' in query:
        months_n = _extract_number_of_months(query, default=6)
        if 'revenue' in query: return {"intent": "metric_trend", "metric": "Revenue", "months": months_n}
        if 'opex' in query: return {"intent": "metric_trend", "metric": "Opex", "months": months_n}
        if 'ebitda' in query: return {"intent": "metric_trend", "metric": "EBITDA", "months": months_n}
        if 'gross margin' in query: return {"intent": "gross_margin_trend", "months": months_n}
        if 'cash balance' in query: return {"intent": "cash_balance_trend", "months": months_n}

    # --- Specific Month(s) Analysis ---
    if len(months) > 1:
        if 'revenue' in query: return {"intent": "multi_month_metric", "metric": "Revenue", "months": months}
        if 'opex' in query: return {"intent": "multi_month_metric", "metric": "Opex", "months": months}
        if 'gross margin' in query: return {"intent": "multi_month_metric", "metric": "Gross Margin", "months": months}
        
    if len(months) == 1:
        month = months[0]
        if 'revenue' in query and 'budget' in query: return {"intent": "revenue_vs_budget", "month": month}
        if 'opex' in query and ('break down' in query or 'breakdown' in query): return {"intent": "opex_breakdown", "month": month}
        if 'ebitda' in query: return {"intent": "ebitda_single_month", "month": month}
        if 'revenue' in query and 'entity' in query: return {"intent": "revenue_variance_by_entity", "month": month}
        if 'revenue' in query: return {"intent": "single_metric", "metric": "Revenue", "month": month}
        if 'opex' in query: return {"intent": "single_metric", "metric": "Opex", "month": month}
        if 'gross margin' in query: return {"intent": "single_metric", "metric": "Gross Margin", "month": month}

    # --- General Questions ---
    if 'cash runway' in query or 'runway' in query:
        return {"intent": "cash_runway_projection"}
    
    return {"intent": "unknown"}


def _extract_months(query: str, data_frames: dict) -> list:
    """Extracts all mentioned months and years from a query."""
    month_names = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b'
    patterns = [
        month_names + r'\s+(\d{4})',  # Month YYYY
        month_names  # Month (no year)
    ]
    
    found_months = []
    
    # Use word boundaries to avoid matching parts of words like 'margin'
    full_pattern = re.compile(r'\b(' + '|'.join(p.replace(month_names, r'(' + month_names + r')') for p in patterns) + r')\b', re.IGNORECASE)
    
    # A more precise regex to find months to avoid partial matches
    month_regex = re.compile(r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b(?:\s+(\d{4}))?', re.IGNORECASE)
    matches = month_regex.finditer(query)

    for match in matches:
        month_str, year_str = match.groups()
        
        month_num = datetime.strptime(month_str[:3], '%b').month
        
        if year_str:
            year = int(year_str)
        else: # Find latest year in data for this month
            actuals_df = data_frames['actuals']
            relevant_dates = actuals_df[actuals_df['month'].dt.month == month_num]
            if not relevant_dates.empty:
                year = relevant_dates['month'].dt.year.max()
            else: # Default to current year if no data
                year = datetime.now().year
        
        full_date = datetime(year, month_num, 1).strftime('%Y-%m-%d')
        if full_date not in found_months:
            found_months.append(full_date)
            
    return sorted(list(set(found_months)))


def _extract_number_of_months(query: str, default: int = 6) -> int:
    """Extracts the number of months for a trend (e.g., "last 3 months")."""
    match = re.search(r'(last|past)\s*(\d+)\s*months', query)
    if match:
        return int(match.group(2))
    return default

