import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Stock Market Tracker", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
#  STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background-color: #1a1d27;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2a2d3a;
    }
    .positive {
        color: #00e5a0;
    }
    .negative {
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("⚙️ Stock Tracker Settings")

# Stock symbol input
stock_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL, MSFT):", "AAPL").upper()

# Time period selection
time_period = st.sidebar.selectbox(
    "Select Time Period:",
    ["1 week", "1 month", "3 months", "6 months", "1 year", "5 years"]
)

period_map = {
    "1 week": "7d",
    "1 month": "1mo",
    "3 months": "3mo",
    "6 months": "6mo",
    "1 year": "1y",
    "5 years": "5y"
}

# Technical indicators
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Technical Indicators")
show_ma20 = st.sidebar.checkbox("Show 20-Day Moving Average", value=True)
show_ma50 = st.sidebar.checkbox("Show 50-Day Moving Average", value=True)
show_volume = st.sidebar.checkbox("Show Volume", value=True)

# Portfolio tracking
st.sidebar.markdown("---")
st.sidebar.subheader("💼 Portfolio")
portfolio_shares = st.sidebar.number_input("Number of Shares Owned:", value=0, min_value=0, step=0.5)
purchase_price = st.sidebar.number_input("Purchase Price per Share (₹):", value=0.0, min_value=0.0, step=1.0)

# ─────────────────────────────────────────────
#  FETCH STOCK DATA
# ─────────────────────────────────────────────
try:
    # Download stock data
    stock_data = yf.download(stock_symbol, period=period_map[time_period], progress=False)
    
    if stock_data.empty:
        st.error(f"❌ Stock symbol '{stock_symbol}' not found. Please try another symbol.")
        st.stop()
    
    # Get current stock info
    stock_info = yf.Ticker(stock_symbol)
    current_price = stock_data['Close'].iloc[-1]
    previous_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
    price_change = current_price - previous_close
    price_change_percent = (price_change / previous_close) * 100
    
    # ─────────────────────────────────────────────
    #  HEADER & KPI CARDS
    # ─────────────────────────────────────────────
    st.title(f"📈 {stock_symbol} - Stock Market Tracker")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # KPI Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price",
            f"₹{current_price:.2f}",
            delta=f"₹{price_change:.2f} ({price_change_percent:.2f}%)" if price_change != 0 else None
        )
    
    with col2:
        st.metric(
            "Day High",
            f"₹{stock_data['High'].iloc[-1]:.2f}"
        )
    
    with col3:
        st.metric(
            "Day Low",
            f"₹{stock_data['Low'].iloc[-1]:.2f}"
        )
    
    with col4:
        st.metric(
            "Volume",
            f"{stock_data['Volume'].iloc[-1] / 1e6:.2f}M"
        )
    
    # Portfolio metrics
    if portfolio_shares > 0 and purchase_price > 0:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        portfolio_value = portfolio_shares * current_price
        portfolio_cost = portfolio_shares * purchase_price
        portfolio_gain = portfolio_value - portfolio_cost
        portfolio_gain_percent = (portfolio_gain / portfolio_cost) * 100
        
        with col1:
            st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}")
        
        with col2:
            st.metric("Total Invested", f"₹{portfolio_cost:,.2f}")
        
        with col3:
            color = "green" if portfolio_gain >= 0 else "red"
            st.metric(
                "Total Gain/Loss",
                f"₹{portfolio_gain:,.2f}",
                delta=f"{portfolio_gain_percent:.2f}%"
            )
        
        with col4:
            st.metric("Shares Owned", f"{portfolio_shares:.2f}")
    
    # ─────────────────────────────────────────────
    #  PRICE CHART WITH MOVING AVERAGES
    # ─────────────────────────────────────────────
    st.subheader("📊 Price Chart")
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#00e5a0', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Close: ₹%{y:.2f}<extra></extra>'
    ))
    
    # 20-Day Moving Average
    if show_ma20 and len(stock_data) >= 20:
        ma20 = stock_data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=ma20,
            mode='lines',
            name='20-Day MA',
            line=dict(color='#ffd166', width=1, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>20-Day MA: ₹%{y:.2f}<extra></extra>'
        ))
    
    # 50-Day Moving Average
    if show_ma50 and len(stock_data) >= 50:
        ma50 = stock_data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=ma50,
            mode='lines',
            name='50-Day MA',
            line=dict(color='#3b82f6', width=1, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>50-Day MA: ₹%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'{stock_symbol} Price Chart - {time_period}',
        yaxis_title='Price (₹)',
        xaxis_title='Date',
        template='plotly_dark',
        hovermode='x unified',
        height=500,
        plot_bgcolor='#1a1d27',
        paper_bgcolor='#0f1117',
        font=dict(color='#e8eaf0', family='DejaVu Sans'),
        xaxis=dict(gridcolor='#2a2d3a'),
        yaxis=dict(gridcolor='#2a2d3a')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ───────────────��─────────────────────────────
    #  VOLUME CHART
    # ─────────────────────────────────────────────
    if show_volume:
        st.subheader("📊 Trading Volume")
        
        colors = ['#00e5a0' if stock_data['Close'].iloc[i] >= stock_data['Close'].iloc[i-1] else '#ff6b6b' 
                  for i in range(1, len(stock_data))]
        colors = ['#00e5a0'] + colors
        
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(
            x=stock_data.index,
            y=stock_data['Volume'],
            marker_color=colors,
            name='Volume',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Volume: %{y:,.0f}<extra></extra>'
        ))
        
        fig_volume.update_layout(
            title=f'{stock_symbol} Trading Volume',
            yaxis_title='Volume',
            xaxis_title='Date',
            template='plotly_dark',
            height=400,
            plot_bgcolor='#1a1d27',
            paper_bgcolor='#0f1117',
            font=dict(color='#e8eaf0', family='DejaVu Sans'),
            xaxis=dict(gridcolor='#2a2d3a'),
            yaxis=dict(gridcolor='#2a2d3a'),
            showlegend=False
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # ─────────────────────────────────────────────
    #  DAILY RETURNS
    # ─────────────────────────────────────────────
    st.subheader("📈 Daily Returns Distribution")
    
    daily_returns = stock_data['Close'].pct_change() * 100
    
    fig_returns = go.Figure()
    fig_returns.add_trace(go.Histogram(
        x=daily_returns.dropna(),
        nbinsx=50,
        marker_color='#3b82f6',
        name='Daily Returns (%)',
        hovertemplate='<b>Return Range:</b> %{x:.2f}%<br><b>Frequency:</b> %{y}<extra></extra>'
    ))
    
    fig_returns.update_layout(
        title=f'{stock_symbol} Daily Returns Distribution',
        xaxis_title='Daily Return (%)',
        yaxis_title='Frequency',
        template='plotly_dark',
        height=400,
        plot_bgcolor='#1a1d27',
        paper_bgcolor='#0f1117',
        font=dict(color='#e8eaf0', family='DejaVu Sans'),
        xaxis=dict(gridcolor='#2a2d3a'),
        yaxis=dict(gridcolor='#2a2d3a'),
        showlegend=False
    )
    
    st.plotly_chart(fig_returns, use_container_width=True)
    
    # ─────────────────────────────────────────────
    #  STATISTICS TABLE
    # ─────────────────────────────────────────────
    st.subheader("📋 Stock Statistics")
    
    stats = {
        "Metric": [
            "Current Price",
            "52-Week High",
            "52-Week Low",
            "Average Volume (20D)",
            "P/E Ratio",
            "Market Cap",
            "Dividend Yield",
            "Beta"
        ],
        "Value": [
            f"₹{current_price:.2f}",
            f"₹{stock_data['High'].max():.2f}",
            f"₹{stock_data['Low'].min():.2f}",
            f"{stock_data['Volume'].tail(20).mean() / 1e6:.2f}M",
            f"{getattr(stock_info.info.get('trailingPE'), '__format__', lambda x: 'N/A')(f'{stock_info.info.get(\"trailingPE\", \"N/A\")}')}",
            f"₹{stock_info.info.get('marketCap', 'N/A'):,}",
            f"{stock_info.info.get('dividendYield', 0) * 100:.2f}%",
            f"{stock_info.info.get('beta', 'N/A')}"
        ]
    }
    
    df_stats = pd.DataFrame(stats)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)
    
    # ─────────────────────────────────────────────
    #  RECENT DATA TABLE
    # ─────────────────────────────────────────────
    st.subheader("📅 Recent Price Data")
    
    recent_data = stock_data.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    recent_data['Daily Change %'] = daily_returns.tail(10).values
    recent_data = recent_data.round(2)
    
    st.dataframe(recent_data, use_container_width=True)
    
    # ─────────────────────────────────────────────
    #  COMPARISON: Multiple Stocks
    # ─────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🔄 Compare Multiple Stocks")
    
    compare_symbols = st.multiselect(
        "Select stocks to compare (optional):",
        ["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK", "WIPRO", "MARUTI"],
        help="These are popular Indian stocks. Add any others you want to compare."
    )
    
    if compare_symbols:
        compare_data = {}
        for symbol in compare_symbols + [stock_symbol]:
            try:
                data = yf.download(symbol, period="1y", progress=False)
                normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                compare_data[symbol] = normalized_price
            except:
                pass
        
        if compare_data:
            fig_compare = go.Figure()
            for symbol, prices in compare_data.items():
                fig_compare.add_trace(go.Scatter(
                    x=prices.index,
                    y=prices,
                    mode='lines',
                    name=symbol,
                    line=dict(width=2),
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>%{y:.2f}%<extra></extra>'
                ))
            
            fig_compare.update_layout(
                title='Stock Performance Comparison (1 Year)',
                yaxis_title='Normalized Price (Base = 100)',
                xaxis_title='Date',
                template='plotly_dark',
                height=500,
                plot_bgcolor='#1a1d27',
                paper_bgcolor='#0f1117',
                font=dict(color='#e8eaf0', family='DejaVu Sans'),
                xaxis=dict(gridcolor='#2a2d3a'),
                yaxis=dict(gridcolor='#2a2d3a'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Make sure the stock symbol is correct. Example: AAPL, GOOGL, MSFT, RELIANCE, TCS")
