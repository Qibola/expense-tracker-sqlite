"""Interactive Plotly chart of spending by month, stacked by category."""
from . import store


def chart_data(conn):
    """Reshape the DB rows into ({category: {month: total}}, [sorted months])."""
    rows = store.spending_by_month_category(conn)
    months = sorted({m for m, _, _ in rows})
    series = {}
    for month, category, total in rows:
        series.setdefault(category, {})[month] = total
    return series, months


def build_figure(conn):
    """Return a stacked bar Figure, one trace per category. Needs plotly."""
    import plotly.graph_objects as go  # imported lazily: the CLI works without it

    series, months = chart_data(conn)
    if not months:
        raise ValueError("no expenses to chart yet")
    fig = go.Figure()
    for category in sorted(series):
        fig.add_bar(name=category, x=months,
                    y=[series[category].get(m, 0) for m in months],
                    hovertemplate="%{x}<br>" + category + ": $%{y:.2f}<extra></extra>")
    fig.update_layout(barmode="stack", title="Monthly spending by category",
                      xaxis_title="Month", yaxis_title="Total spent ($)",
                      xaxis_type="category", legend_title="Category")
    return fig


def write_chart(conn, path):
    """Write the chart to a standalone interactive HTML file."""
    build_figure(conn).write_html(path, include_plotlyjs="cdn")
    return path
