import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates
from pandas.tseries.offsets import DateOffset

# --- Data Loading and Preparation ---

def _load_and_prepare_data(files: dict) -> dict:
    """Loads CSVs, standardizes, and prepares data for analysis."""
    data_frames = {}
    for name, file in files.items():
        df = pd.read_csv(file)
        df['month'] = pd.to_datetime(df['month'])
        data_frames[name] = df
    return data_frames

def _convert_to_usd(df: pd.DataFrame, fx_rates: pd.DataFrame) -> pd.DataFrame:
    """Converts amounts to USD using monthly exchange rates."""
    df_merged = pd.merge(df, fx_rates, on=['month', 'currency'], how='left')
    df_merged['rate_to_usd'].fillna(1.0, inplace=True) # Assume 1.0 for USD
    df_merged['amount_usd'] = df_merged['amount'] * df_merged['rate_to_usd']
    return df_merged

def _style_plot(fig, ax, title):
    """Applies consistent, aesthetic styling to matplotlib plots."""
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_title(title, fontsize=14, weight='bold', loc='left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#d1d5db')
    ax.spines['bottom'].set_color('#d1d5db')
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()

# --- Core Financial Tools ---

def get_revenue_vs_budget(month_str: str, data_frames: dict):
    """Compares actual revenue vs. budget for a given month."""
    actuals = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    budget = _convert_to_usd(data_frames['budget'], data_frames['fx'])
    target_month = pd.to_datetime(month_str)

    actual_rev = actuals[(actuals['month'].dt.to_period('M') == target_month.to_period('M')) & (actuals['account_category'] == 'Revenue')]['amount_usd'].sum()
    budget_rev = budget[(budget['month'].dt.to_period('M') == target_month.to_period('M')) & (budget['account_category'] == 'Revenue')]['amount_usd'].sum()
    variance = actual_rev - budget_rev
    
    summary = f"**Revenue for {target_month.strftime('%B %Y')}:**\n" \
              f"- **Actual:** ${actual_rev:,.2f} USD\n" \
              f"- **Budget:** ${budget_rev:,.2f} USD\n" \
              f"- **Variance:** ${variance:,.2f} USD"

    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Actual', 'Budget']
    values = [actual_rev, budget_rev]
    sns.barplot(x=categories, y=values, ax=ax, palette='viridis')
    _style_plot(fig, ax, f"Revenue vs. Budget for {target_month.strftime('%B %Y')}")
    ax.set_ylabel("Amount (USD)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: categories[int(x)]))

    return summary, fig

def get_gross_margin_trend(months: int, data_frames: dict):
    """Calculates and plots the gross margin trend for the last N months."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    today = pd.Timestamp.now()
    df_historical = df_usd[df_usd['month'] <= today].set_index('month')

    monthly_pivot = df_historical.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
    monthly_pivot['Gross Margin'] = ((monthly_pivot['Revenue'] - monthly_pivot['COGS']) / monthly_pivot['Revenue']) * 100
    
    trend_data = monthly_pivot.sort_index().last(f'{months}M')
    
    summary = f"**Gross Margin Trend ({months} Months):**\n"
    for date, row in trend_data.iterrows():
        summary += f"- **{date.strftime('%b %Y')}:** {row['Gross Margin']:.2f}%\n"

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=trend_data, x=trend_data.index, y='Gross Margin', ax=ax, marker='o')
    _style_plot(fig, ax, f"Gross Margin Trend (Last {months} Months)")
    ax.set_ylabel("Gross Margin (%)")
    ax.set_xlabel("Month")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    return summary, fig

def get_opex_breakdown(month_str: str, data_frames: dict):
    """Shows a breakdown of Opex by category for a given month."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    target_month = pd.to_datetime(month_str)
    month_data = df_usd[df_usd['month'].dt.to_period('M') == target_month.to_period('M')]
    
    opex_data = month_data[month_data['account_category'].str.startswith('Opex:')].copy()
    opex_data['category'] = opex_data['account_category'].str.replace('Opex: ', '')
    opex_summary = opex_data.groupby('category')['amount_usd'].sum().sort_values(ascending=False)
    
    total_opex = opex_summary.sum()
    summary = f"**Opex Breakdown for {target_month.strftime('%B %Y')} (Total: ${total_opex:,.2f} USD):**\n"
    for category, amount in opex_summary.items():
        summary += f"- **{category}:** ${amount:,.2f} USD\n"

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette('viridis', len(opex_summary))
    opex_summary.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90, legend=False, colors=colors)
    ax.set_ylabel('')
    _style_plot(fig, ax, f"Opex Breakdown for {target_month.strftime('%B %Y')}")
    
    return summary, fig

def _calculate_net_burn(data_frames: dict):
    """Helper to calculate average net burn and latest cash."""
    actuals = data_frames['actuals']
    cash = data_frames['cash']
    fx_rates = data_frames['fx']
    today = pd.Timestamp.now()

    cash_up_to_today = cash[cash['month'] <= today].copy()
    if cash_up_to_today.empty: return None, None, None
    latest_cash_balance = cash_up_to_today.iloc[-1]['cash_usd']
    last_cash_month = cash_up_to_today.iloc[-1]['month']

    df_usd = _convert_to_usd(actuals, fx_rates)
    monthly_totals = df_usd.groupby('month')['amount_usd'].sum()
    burn_up_to_today = monthly_totals[monthly_totals.index <= today]
    last_3_months_burn = burn_up_to_today.sort_index().last('3M')
    
    if len(last_3_months_burn) < 3: return None, None, None
    avg_monthly_burn = -last_3_months_burn.mean()

    return avg_monthly_burn, latest_cash_balance, last_cash_month

def get_cash_runway(avg_monthly_burn, latest_cash, last_month, data_frames):
    """Calculates and plots cash runway for cash-negative scenario."""
    runway_months = latest_cash / avg_monthly_burn
    end_date = last_month + DateOffset(months=int(runway_months))
    
    summary = f"**Cash Runway Analysis:**\n" \
              f"- **Current Cash Balance:** ${latest_cash:,.2f} USD\n" \
              f"- **Avg. Monthly Net Burn (3-mo):** ${avg_monthly_burn:,.2f} USD\n" \
              f"- **Estimated Runway:** {runway_months:.1f} months (until **{end_date.strftime('%B %Y')}**)"
              
    projection_dates = [last_month + DateOffset(months=i) for i in range(int(runway_months) + 2)]
    projection_cash = [latest_cash - (avg_monthly_burn * i) for i in range(len(projection_dates))]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=projection_dates, y=projection_cash, ax=ax, linestyle='--', color='red', label='Projected Runway')
    sns.lineplot(data=data_frames['cash'][data_frames['cash']['month'] <= last_month], x='month', y='cash_usd', ax=ax, marker='o', label='Historical Cash')
    ax.axhline(0, color='black', linestyle='-')
    _style_plot(fig, ax, "Cash Runway Projection")
    ax.set_ylabel("Cash Balance (USD)")

    return summary, fig
    
def get_cash_projection(avg_monthly_gain, latest_cash, last_month, data_frames):
    """Calculates and plots cash projection for cash-positive scenario."""
    summary = f"**Cash Flow Positive Analysis:**\n" \
              f"- **Current Cash Balance:** ${latest_cash:,.2f} USD\n" \
              f"- **Avg. Monthly Net Gain (3-mo):** ${avg_monthly_gain:,.2f} USD\n" \
              f"- Your business is currently cash flow positive."
              
    projection_dates = [last_month + DateOffset(months=i) for i in range(13)]
    projection_cash = [latest_cash + (avg_monthly_gain * i) for i in range(len(projection_dates))]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=projection_dates, y=projection_cash, ax=ax, linestyle='--', color='green', label='Projected Growth')
    sns.lineplot(data=data_frames['cash'][data_frames['cash']['month'] <= last_month], x='month', y='cash_usd', ax=ax, marker='o', label='Historical Cash')
    _style_plot(fig, ax, "Cash Growth Projection (12 Months)")
    ax.set_ylabel("Cash Balance (USD)")

    return summary, fig

def get_ebitda(month_str: str, data_frames: dict):
    """Calculates EBITDA for a given month and shows a waterfall chart."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    target_month = pd.to_datetime(month_str)
    month_data = df_usd[df_usd['month'].dt.to_period('M') == target_month.to_period('M')]
    
    pivot = month_data.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
    revenue = pivot.get('Revenue', pd.Series([0])).sum()
    cogs = pivot.get('COGS', pd.Series([0])).sum()
    opex = pivot.filter(regex='^Opex').sum().sum()
    ebitda = revenue - cogs - opex
    
    summary = f"**EBITDA Calculation for {target_month.strftime('%B %Y')}:**\n" \
              f"- **Revenue:** ${revenue:,.2f} USD\n" \
              f"- **COGS:** -${cogs:,.2f} USD\n" \
              f"- **Opex:** -${opex:,.2f} USD\n" \
              f"-----------------------------\n" \
              f"- **EBITDA:** **${ebitda:,.2f} USD**"
              
    data = {'Category': ['Revenue', 'COGS', 'Opex', 'EBITDA'], 'Amount': [revenue, -cogs, -opex, ebitda]}
    df_chart = pd.DataFrame(data)
    
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x='Category', y='Amount', data=df_chart, ax=ax, palette='viridis')
    _style_plot(fig, ax, f"EBITDA Waterfall for {target_month.strftime('%B %Y')}")
    ax.set_ylabel("Amount (USD)")

    return summary, fig

def get_metric_trend(metric_name: str, months: int, data_frames: dict):
    """Calculates and plots a trend for a given metric (Rev, Opex, EBITDA)."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    today = pd.Timestamp.now()
    df_historical = df_usd[df_usd['month'] <= today]

    pivot = df_historical.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
    if metric_name == 'Revenue': pivot['value'] = pivot['Revenue']
    elif metric_name == 'Opex': pivot['value'] = pivot.filter(regex='^Opex').sum(axis=1)
    elif metric_name == 'EBITDA': pivot['value'] = pivot['Revenue'] - pivot['COGS'] - pivot.filter(regex='^Opex').sum(axis=1)
    
    trend_data = pivot.sort_index().last(f'{months}M')
    
    summary = f"**{metric_name} Trend ({months} Months):**\n"
    for date, row in trend_data.iterrows():
        summary += f"- **{date.strftime('%b %Y')}:** ${row['value']:,.2f} USD\n"
        
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=trend_data, x=trend_data.index, y='value', ax=ax, marker='o')
    _style_plot(fig, ax, f"{metric_name} Trend (Last {months} Months)")
    ax.set_ylabel(f"{metric_name} (USD)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    return summary, fig

def get_revenue_variance_by_entity(month_str: str, data_frames: dict):
    """Analyzes which entities missed their revenue budget for a month."""
    actuals = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    budget = _convert_to_usd(data_frames['budget'], data_frames['fx'])
    target_month = pd.to_datetime(month_str)

    actual_rev = actuals[(actuals['month'].dt.to_period('M') == target_month.to_period('M')) & (actuals['account_category'] == 'Revenue')]
    budget_rev = budget[(budget['month'].dt.to_period('M') == target_month.to_period('M')) & (budget['account_category'] == 'Revenue')]
    
    actual_by_entity = actual_rev.groupby('entity')['amount_usd'].sum()
    budget_by_entity = budget_rev.groupby('entity')['amount_usd'].sum()
    
    variance_df = pd.DataFrame({'Actual': actual_by_entity, 'Budget': budget_by_entity}).fillna(0)
    variance_df['Variance'] = variance_df['Actual'] - variance_df['Budget']
    missed_budget = variance_df[variance_df['Variance'] < 0].sort_values('Variance')
    
    summary = f"**Entities That Missed Revenue Budget for {target_month.strftime('%B %Y')}:**\n"
    if missed_budget.empty:
        summary += "Congratulations! All entities met or exceeded their revenue budget."
    else:
        for entity, row in missed_budget.iterrows():
            summary += f"- **{entity}:** Missed by ${abs(row['Variance']):,.2f} USD (Actual: ${row['Actual']:,.2f}, Budget: ${row['Budget']:,.2f})\n"

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = (variance_df['Variance'] > 0).map({True: '#22c55e', False: '#ef4444'})
    variance_df['Variance'].sort_values().plot(kind='barh', ax=ax, color=colors)
    _style_plot(fig, ax, f"Revenue Variance by Entity for {target_month.strftime('%B %Y')}")
    ax.set_xlabel("Variance (USD) - Actual vs. Budget")

    return summary, fig
    
def get_cash_balance_trend(months: int, data_frames: dict):
    """Plots the cash balance for the last N months."""
    cash = data_frames['cash']
    today = pd.Timestamp.now()
    cash_up_to_today = cash[cash['month'] <= today].copy()
    
    cash_up_to_today.set_index('month', inplace=True)
    last_n_months = cash_up_to_today.sort_index().last(f'{months}M')
    
    summary = f"**Cash Balance Trend ({months} Months):**\n"
    for date, row in last_n_months.iterrows():
        summary += f"- **{date.strftime('%b %Y')}:** ${row['cash_usd']:,.2f} USD\n"
        
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=last_n_months, x=last_n_months.index, y='cash_usd', ax=ax, marker='o')
    _style_plot(fig, ax, f"Cash Balance Trend (Last {months} Months)")
    ax.set_ylabel("Cash Balance (USD)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    return summary, fig

def get_metric_ranking(metric_name: str, ranking_type: str, n: int, data_frames: dict):
    """Finds the top or bottom N months for a given metric."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    today = pd.Timestamp.now()
    df_historical = df_usd[df_usd['month'] <= today]

    pivot = df_historical.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
    if metric_name == 'Revenue': pivot['value'] = pivot['Revenue']
    elif metric_name == 'Opex': pivot['value'] = pivot.filter(regex='^Opex').sum(axis=1)
    elif metric_name == 'EBITDA': pivot['value'] = pivot['Revenue'] - pivot['COGS'] - pivot.filter(regex='^Opex').sum(axis=1)
    elif metric_name == 'Gross Margin': pivot['value'] = ((pivot['Revenue'] - pivot['COGS']) / pivot['Revenue']) * 100
    
    ascending = True if ranking_type == 'bottom' else False
    ranked_data = pivot['value'].sort_values(ascending=ascending).head(n)
    
    summary = f"**{ranking_type.capitalize()} {n} Month(s) for {metric_name}:**\n"
    for date, value in ranked_data.items():
        if metric_name == 'Gross Margin':
            summary += f"- **{date.strftime('%B %Y')}:** {value:.2f}%\n"
        else:
            summary += f"- **{date.strftime('%B %Y')}:** ${value:,.2f} USD\n"

    fig, ax = plt.subplots(figsize=(8, 5))
    ranked_data.sort_values().plot(kind='barh', ax=ax, color=sns.color_palette('viridis', n))
    _style_plot(fig, ax, f"{ranking_type.capitalize()} {n} {metric_name} Months")
    ax.set_xlabel(f"{metric_name} {'(%)' if metric_name == 'Gross Margin' else '(USD)'}")

    return summary, fig

def get_single_metric(metric_name: str, month_str: str, data_frames: dict):
    """Calculates a single metric for a single month."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    target_month = pd.to_datetime(month_str)
    
    month_data = df_usd[df_usd['month'].dt.to_period('M') == target_month.to_period('M')]
    if month_data.empty: return f"No data found for {target_month.strftime('%B %Y')}.", None
    pivot_month = month_data.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
    
    value = 0
    unit = "USD"
    
    if metric_name == 'Gross Margin':
        unit = "%"
        revenue = pivot_month.get('Revenue', pd.Series([0])).sum()
        cogs = pivot_month.get('COGS', pd.Series([0])).sum()
        value = ((revenue - cogs) / revenue * 100) if revenue != 0 else 0
    elif metric_name == 'Revenue':
        value = pivot_month.get('Revenue', pd.Series([0])).sum()
    elif metric_name == 'Opex':
        value = pivot_month.filter(regex='^Opex').sum().sum()

    summary = f"**{metric_name} for {target_month.strftime('%B %Y')}:** {value:,.2f} {unit}"
              
    return summary, None

def get_multi_month_metric(metric_name: str, months_list: list, data_frames: dict):
    """Calculates a metric for multiple specified months and compares them."""
    df_usd = _convert_to_usd(data_frames['actuals'], data_frames['fx'])
    target_months = [pd.to_datetime(m) for m in months_list]
    results = {}
    
    for target_month in target_months:
        month_data = df_usd[df_usd['month'].dt.to_period('M') == target_month.to_period('M')]
        if month_data.empty: continue
        pivot = month_data.pivot_table(index='month', columns='account_category', values='amount_usd', aggfunc='sum').fillna(0)
        value = None
        if metric_name == 'Gross Margin':
            revenue = pivot.get('Revenue', pd.Series([0])).sum()
            cogs = pivot.get('COGS', pd.Series([0])).sum()
            if revenue != 0: value = (revenue - cogs) / revenue * 100
        elif metric_name == 'Revenue':
            value = pivot.get('Revenue', pd.Series([0])).sum()
        elif metric_name == 'Opex':
            value = pivot.filter(regex='^Opex').sum().sum()
        if value is not None: results[target_month.strftime('%b %Y')] = value

    if not results: return "No data found for the specified months.", None

    results_df = pd.Series(results).sort_index()
    metric_display_name = "Gross Margin %" if metric_name == 'Gross Margin' else metric_name
    summary = f"**Comparison for {metric_display_name}:**\n"
    for month, value in results_df.items():
        summary += f"- **{month}**: {'$' if metric_name != 'Gross Margin' else ''}{value:,.2f}{'%' if metric_name == 'Gross Margin' else ' USD'}\n"

    fig, ax = plt.subplots(figsize=(8, 5))
    results_df.plot(kind='bar', ax=ax, color=sns.color_palette('viridis', len(results_df)))
    _style_plot(fig, ax, f"{metric_display_name} Comparison")
    ax.set_ylabel(metric_display_name)

    return summary, fig

