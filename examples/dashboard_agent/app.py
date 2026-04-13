"""Pizza Sales Dashboard with AI Chat Assistant."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from streamlit_bubble_chat import bubble_chat

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

ALL_CATEGORIES = ["Chicken", "Classic", "Supreme", "Veggie"]
ALL_SIZES = ["S", "M", "L"]

# Derived from the original raw data: total_quantity / total_unique_orders.
# Used to approximate order counts from the pre-aggregated dataset.
AVG_ITEMS_PER_ORDER = 2.322

SYSTEM_PROMPT = """You are an expert pizza sales analyst assistant embedded in an interactive dashboard.
The dashboard shows 2015 pizza sales data. You have two tools available:

1. get_dashboard_context — call this FIRST to see the current filters and KPIs before answering any
   question about the data.
2. apply_filters — use this to update the dashboard filters when the user asks you to do so (e.g.
   "show me only Veggie pizzas" or "filter by size M").

Guidelines:
- Always call get_dashboard_context before providing insights or numbers.
- When applying filters, confirm what you changed and briefly summarise the new KPIs.
- Be concise, data-driven, and proactive in surfacing interesting patterns.
- Numbers: format currency with $ and thousands separator.
"""  # noqa: E501

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the pre-aggregated sales summary CSV."""
    return pd.read_csv(DATA_DIR / "sales_summary.csv")


def apply_dataframe_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply session-state filters to the master DataFrame."""
    months = st.session_state.get("filter_months", (1, 12))
    if isinstance(months, (list, tuple)) and len(months) == 2:
        start_m, end_m = months
    else:
        start_m, end_m = 1, 12
    categories = st.session_state.get("filter_categories", [])
    sizes = st.session_state.get("filter_sizes", [])

    filtered = df[df["month"].between(start_m, end_m)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]
    if sizes:
        filtered = filtered[filtered["size"].isin(sizes)]
    return filtered


# ---------------------------------------------------------------------------
# KPI helpers
# ---------------------------------------------------------------------------


def compute_kpis(df: pd.DataFrame) -> dict:
    total_revenue = df["revenue"].sum()
    total_pizzas = int(df["quantity"].sum())
    # Approximate unique orders from aggregated data using the historical avg.
    total_orders = round(total_pizzas / AVG_ITEMS_PER_ORDER)
    aov = total_revenue / total_orders if total_orders else 0
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_pizzas": total_pizzas,
        "aov": aov,
    }


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------

# Bridge dict for passing filter changes from agent tools (running in a
# thread pool without ScriptRunContext) to handle_message (running in the
# Streamlit thread where session_state is available).
# IMPORTANT: These must be cached resources so the same dict instances are
# shared between the cached agent's tools and handle_message across Streamlit
# reruns (which re-execute module-level code, creating new dicts).


@st.cache_resource
def _get_filter_changes() -> dict:
    return {}


@st.cache_resource
def _get_current_filters() -> dict:
    return {
        "months": (1, 12),
        "categories": [],
        "sizes": [],
    }


@tool
def get_dashboard_context() -> str:
    """Return a structured summary of the current dashboard state."""
    master = load_data()

    # Read from current_filters snapshot (thread-safe, set by handle_message)
    current_filters = _get_current_filters()
    start_m, end_m = current_filters["months"]
    categories = current_filters["categories"]
    sizes = current_filters["sizes"]

    filtered = master[master["month"].between(start_m, end_m)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]
    if sizes:
        filtered = filtered[filtered["size"].isin(sizes)]

    kpis = compute_kpis(filtered)

    cat_display = categories if categories else ["All"]
    size_display = sizes if sizes else ["All"]

    return (
        f"## Current Dashboard State\n"
        f"**Filters**\n"
        f"- Months: {MONTH_NAMES[start_m - 1]} – {MONTH_NAMES[end_m - 1]}\n"
        f"- Categories: {', '.join(cat_display)}\n"
        f"- Sizes: {', '.join(size_display)}\n\n"
        f"**KPIs (filtered data)**\n"
        f"- Total Revenue: ${kpis['total_revenue']:,.2f}\n"
        f"- Total Orders: {kpis['total_orders']:,}\n"
        f"- Total Pizzas Sold: {kpis['total_pizzas']:,}\n"
        f"- Average Order Value: ${kpis['aov']:,.2f}\n\n"
        f"**Top 5 Pizzas by Revenue**\n"
        + filtered.groupby("name")["revenue"]
        .sum()
        .nlargest(5)
        .reset_index()
        .apply(lambda r: f"- {r['name']}: ${r['revenue']:,.2f}", axis=1)
        .str.cat(sep="\n")
        + "\n\n**Revenue by Category**\n"
        + filtered.groupby("category")["revenue"]
        .sum()
        .reset_index()
        .apply(lambda r: f"- {r['category']}: ${r['revenue']:,.2f}", axis=1)
        .str.cat(sep="\n")
    )


@tool
def apply_filters(
    start_month: int | None = None,
    end_month: int | None = None,
    categories: list[str] | None = None,
    sizes: list[str] | None = None,
) -> str:
    """
    Update the dashboard filters.

    Args:
        start_month: Start month number (1-12). Pass None to keep current.
        end_month: End month number (1-12). Pass None to keep current.
        categories: List of pizza categories to show. Valid values: Chicken, Classic,
            Supreme, Veggie. Pass an empty list [] to show all categories.
        sizes: List of pizza sizes to show. Valid values: S, M, L.
            Pass an empty list [] to show all sizes.
    """
    changes = []

    filter_changes = _get_filter_changes()
    current_filters = _get_current_filters()
    cur_start, cur_end = current_filters["months"]

    if start_month is not None or end_month is not None:
        new_start = (
            max(1, min(12, start_month)) if start_month is not None else cur_start
        )
        new_end = max(1, min(12, end_month)) if end_month is not None else cur_end
        if new_start > new_end:
            new_start, new_end = new_end, new_start
        filter_changes["months"] = (new_start, new_end)
        current_filters["months"] = (new_start, new_end)
        changes.append(
            f"Month range → {MONTH_NAMES[new_start - 1]}–{MONTH_NAMES[new_end - 1]}"
        )

    if categories is not None:
        valid = [c for c in categories if c in ALL_CATEGORIES]
        filter_changes["categories"] = valid
        current_filters["categories"] = valid
        changes.append(f"Categories → {', '.join(valid) if valid else 'All'}")

    if sizes is not None:
        valid_s = [s for s in sizes if s in ALL_SIZES]
        filter_changes["sizes"] = valid_s
        current_filters["sizes"] = valid_s
        changes.append(f"Sizes → {', '.join(valid_s) if valid_s else 'All'}")

    if not changes:
        return "No valid filter changes were provided."

    # Compute KPIs with the new filters applied
    master = load_data()
    start_m, end_m = current_filters["months"]
    filtered = master[master["month"].between(start_m, end_m)]
    cats = current_filters["categories"]
    szs = current_filters["sizes"]
    if cats:
        filtered = filtered[filtered["category"].isin(cats)]
    if szs:
        filtered = filtered[filtered["size"].isin(szs)]
    kpis = compute_kpis(filtered)

    return (
        "Filters updated:\n" + "\n".join(f"- {c}" for c in changes) + "\n\n"
        f"Updated KPIs:\n"
        f"- Revenue: ${kpis['total_revenue']:,.2f}\n"
        f"- Orders: {kpis['total_orders']:,}\n"
        f"- Pizzas Sold: {kpis['total_pizzas']:,}\n"
        f"- AOV: ${kpis['aov']:,.2f}"
    )


# ---------------------------------------------------------------------------
# LangChain agent
# ---------------------------------------------------------------------------


@st.cache_resource
def get_agent_executor():
    """Create and cache the LangChain agent."""

    # Use your LLM provider of choice here
    llm = ChatOpenAI(
        model=os.environ["MODEL_NAME"],
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    )

    memory = MemorySaver()
    return create_agent(
        llm,
        [get_dashboard_context, apply_filters],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I'm your pizza sales assistant. I can analyse the data you're "
                    "viewing and adjust the dashboard filters for you. What would you "
                    "like to know?"
                ),
            }
        ]
    if "filter_months" not in st.session_state:
        st.session_state.filter_months = (1, 12)
    if "filter_categories" not in st.session_state:
        st.session_state.filter_categories = []
    if "filter_sizes" not in st.session_state:
        st.session_state.filter_sizes = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "unread" not in st.session_state:
        st.session_state.unread = 1


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


def render_kpi_cards(kpis: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"${kpis['total_revenue']:,.0f}")
    col2.metric("🛒 Total Orders", f"{kpis['total_orders']:,}")
    col3.metric("🍕 Pizzas Sold", f"{kpis['total_pizzas']:,}")
    col4.metric("📊 Avg Order Value", f"${kpis['aov']:,.2f}")


def render_charts(df: pd.DataFrame) -> None:
    # ── Row 1: Revenue by month + Category distribution ──────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        rev_by_month = df.groupby("month")["revenue"].sum().sort_index().reset_index()
        rev_by_month["month_name"] = rev_by_month["month"].apply(
            lambda m: MONTH_NAMES[m - 1]
        )
        fig_line = px.line(
            rev_by_month,
            x="month_name",
            y="revenue",
            markers=True,
            title="Monthly Revenue",
            labels={"month_name": "Month", "revenue": "Revenue ($)"},
        )
        fig_line.update_traces(line_color="#FF4B4B", marker_color="#FF4B4B")
        fig_line.update_layout(margin=dict(t=40, b=20), yaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_line, width="stretch")

    with col_right:
        rev_by_cat = df.groupby("category")["revenue"].sum().reset_index()
        fig_pie = px.pie(
            rev_by_cat,
            names="category",
            values="revenue",
            title="Revenue by Category",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, width="stretch")

    # ── Row 2: Top pizzas + Day of week ──────────────────────────────────
    col_left2, col_right2 = st.columns([2, 1])

    with col_left2:
        top_pizzas = (
            df.groupby("name")["revenue"]
            .sum()
            .nlargest(10)
            .reset_index()
            .sort_values("revenue")
        )
        fig_bar = px.bar(
            top_pizzas,
            x="revenue",
            y="name",
            orientation="h",
            title="Top 10 Pizzas by Revenue",
            labels={"revenue": "Revenue ($)", "name": "Pizza"},
            color="revenue",
            color_continuous_scale="Reds",
        )
        fig_bar.update_layout(margin=dict(t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, width="stretch")

    with col_right2:
        rev_by_size = (
            df.groupby("size")["revenue"]
            .sum()
            .reindex(ALL_SIZES, fill_value=0)
            .reset_index()
        )
        fig_size = px.bar(
            rev_by_size,
            x="size",
            y="revenue",
            title="Revenue by Pizza Size",
            labels={"size": "Size", "revenue": "Revenue ($)"},
            color="size",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_size.update_layout(margin=dict(t=40, b=20), showlegend=False)
        st.plotly_chart(fig_size, width="stretch")


# ---------------------------------------------------------------------------
# on_message callback
# ---------------------------------------------------------------------------


def handle_message() -> None:
    text = st.session_state["pizza_chat"].new_message
    if not text or not text.strip():
        return

    st.session_state.messages.append({"role": "user", "content": text})

    # Snapshot current filters so tools can read them from a thread.
    current_filters = _get_current_filters()
    current_filters["months"] = st.session_state.filter_months
    current_filters["categories"] = st.session_state.filter_categories
    current_filters["sizes"] = st.session_state.filter_sizes
    _get_filter_changes().clear()

    agent = get_agent_executor()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": text}]},
            config=config,
        )
        response = result["messages"][-1].content
    except Exception as exc:  # noqa: BLE001
        response = f"Sorry, I encountered an error: {exc}"

    # Apply any filter changes the tool requested (now in the Streamlit thread).
    needs_rerun = False
    filter_changes = _get_filter_changes()
    if filter_changes:
        if "months" in filter_changes:
            st.session_state.filter_months = filter_changes["months"]
        if "categories" in filter_changes:
            st.session_state.filter_categories = filter_changes["categories"]
        if "sizes" in filter_changes:
            st.session_state.filter_sizes = filter_changes["sizes"]
        needs_rerun = True
        filter_changes.clear()

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.unread = 0

    if needs_rerun:
        st.session_state["_month_slider"] = st.session_state.filter_months
        st.session_state["_category_multi"] = st.session_state.filter_categories
        st.session_state["_size_multi"] = st.session_state.filter_sizes
        st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Pizza Sales Dashboard",
        page_icon="🍕",
        layout="wide",
    )

    init_session_state()

    master_df = load_data()

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("🍕 Pizza Sales")
        st.caption("2015 Sales Analytics")
        st.divider()

        st.subheader("Filters")

        # Month range
        month_range = st.select_slider(
            "Month Range",
            options=list(range(1, 13)),
            value=st.session_state.filter_months,
            format_func=lambda m: MONTH_NAMES[m - 1],
            key="_month_slider",
        )
        st.session_state.filter_months = month_range

        # Category
        selected_categories = st.multiselect(
            "Category",
            options=ALL_CATEGORIES,
            key="_category_multi",
        )
        st.session_state.filter_categories = selected_categories

        # Size
        selected_sizes = st.multiselect(
            "Size",
            options=ALL_SIZES,
            key="_size_multi",
        )
        st.session_state.filter_sizes = selected_sizes

        if st.button("Reset Filters", use_container_width=True):
            st.session_state.filter_months = (1, 12)
            st.session_state.filter_categories = []
            st.session_state.filter_sizes = []
            st.session_state["_month_slider"] = (1, 12)
            st.session_state["_category_multi"] = []
            st.session_state["_size_multi"] = []
            st.rerun()

        st.divider()
        st.caption("The AI assistant can also apply filters — just ask!")

    # ── Apply filters & compute KPIs ───────────────────────────────────────
    filtered_df = apply_dataframe_filters(master_df)
    kpis = compute_kpis(filtered_df)

    # ── Header ─────────────────────────────────────────────────────────────
    st.title("🍕 Pizza Sales Dashboard")

    start_m, end_m = st.session_state.filter_months
    active_filters = []
    if (start_m, end_m) != (1, 12):
        active_filters.append(f"{MONTH_NAMES[start_m - 1]}–{MONTH_NAMES[end_m - 1]}")
    if st.session_state.filter_categories:
        active_filters.append(", ".join(st.session_state.filter_categories))
    if st.session_state.filter_sizes:
        active_filters.append("Size: " + ", ".join(st.session_state.filter_sizes))

    if active_filters:
        st.caption(f"Filtered by: {' | '.join(active_filters)}")
    else:
        st.caption("Showing all data — Jan to Dec 2015")

    st.divider()

    # ── KPI cards ──────────────────────────────────────────────────────────
    render_kpi_cards(kpis)

    st.divider()

    # ── Charts ─────────────────────────────────────────────────────────────
    render_charts(filtered_df)

    # ── Bubble chat ────────────────────────────────────────────────────────
    bubble_chat(
        messages=st.session_state.messages,
        unread_count=st.session_state.unread,
        key="pizza_chat",
        window_title="Pizza Sales AI Assistant",
        theme_color="#007AFF",
        on_message=handle_message,
    )

    # Reset unread when user opens the chat
    chat_state = st.session_state.get("pizza_chat", {})
    if chat_state.get("is_open", False) and st.session_state.unread > 0:
        st.session_state.unread = 0


if __name__ == "__main__":
    main()
