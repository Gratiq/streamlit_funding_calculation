import streamlit as st
import pandas as pd

# Настройка страницы и стилей
st.set_page_config(
    page_title="Funding Arbitrage Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Добавляем CSS стили
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
            border: none;
            padding: 0.5rem;
            font-size: 1.1rem;
        }
        .stButton>button:hover {
            background-color: #FF2B2B;
        }
        .sidebar-content {
            padding: 1.5rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        h1 {
            color: #FF4B4B;
            text-align: center;
            padding: 1rem 0;
        }
        h2 {
            color: #31333F;
            padding: 0.5rem 0;
        }
        .stMetricLabel {
            font-size: 1rem !important;
        }
        .stMetricValue {
            font-size: 1.5rem !important;
            font-weight: bold !important;
        }
        .stSidebar {
            background-color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)

def calculate_funding_arbitrage(
    capital: float,
    eth_price: float,
    ltv_max: float,
    liquidation_threshold: float,
    funding_rate: float,
    eth_supply_rate: float,
    usdc_borrow_rate: float,
    min_liq_distance: float
):
    results = []
    
    # Iterate over capital allocation to spot from 60% to 100%
    for c_spot in range(int(0.6 * capital), int(0.9 * capital), 250):
        c_futures = capital - c_spot
        eth_initial = c_spot / eth_price

        collateral_value = eth_initial * eth_price
        max_borrow = ltv_max * collateral_value

        # Iterate over borrow amounts
        for borrow_amount in range(0, int(max_borrow) + 1, 500):
            if borrow_amount == 0:
                continue

            ltv = borrow_amount / collateral_value

            # Calculate liquidation price on spot leg
            liq_price_spot = borrow_amount / (liquidation_threshold * eth_initial)
            liq_distance_spot = ((eth_price - liq_price_spot) / eth_price) * 100

            if liq_distance_spot < min_liq_distance:
                continue

            # Total ETH after borrowing
            eth_borrowed = borrow_amount / eth_price
            total_eth = eth_initial + eth_borrowed

            # Futures position size
            futures_position_size = total_eth * eth_price

            # Leverage calculations
            leverage_futures = futures_position_size / c_futures
            spot_leverage = futures_position_size / c_spot

            # Calculate liquidation price on futures leg
            liq_price_futures = eth_price * (1 + 1 / leverage_futures)
            liq_distance_futures = ((liq_price_futures - eth_price) / eth_price) * 100

            if liq_distance_futures < min_liq_distance:
                continue

            # Calculate net income
            funding_income = futures_position_size * funding_rate
            eth_interest = eth_initial * eth_price * eth_supply_rate
            borrow_interest = borrow_amount * usdc_borrow_rate
            net_income = funding_income + eth_interest - borrow_interest

            roi = net_income / capital

            results.append({
                "Capital_Spot": c_spot,
                "Capital_Futures": c_futures,
                "Borrow_Amount": borrow_amount,
                "ETH_Initial": eth_initial,
                "ETH_Borrowed": eth_borrowed,
                "Total_ETH": total_eth,
                "LTV": ltv,
                "Leverage_Spot": spot_leverage,
                "Liq_Price_Spot": liq_price_spot,
                "Liq_Distance_Spot_%": liq_distance_spot,
                "Futures_Position_Size": futures_position_size,
                "Leverage_Futures": leverage_futures,
                "Liq_Price_Futures": liq_price_futures,
                "Liq_Distance_Futures_%": liq_distance_futures,
                "Net_Income": net_income,
                "ROI": roi,
            })

    return max(results, key=lambda x: x["ROI"]) if results else None

# Заголовок с эмодзи и описанием
st.markdown("<h1>📈 Funding Arbitrage Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 0 2rem 2rem 2rem; color: #666;'>
        Optimize your funding arbitrage strategy across spot and futures markets
    </div>
""", unsafe_allow_html=True)

# Боковая панель с параметрами
with st.sidebar:
    st.markdown("""
        <div class='sidebar-content'>
            <h2>Strategy Parameters</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Основные параметры в отдельном контейнере
    with st.expander("Market Parameters", expanded=True):
        capital = st.number_input(
            'Initial Capital (USDT)',
            value=10000,
            min_value=100,
            help="Your initial investment amount in USDT"
        )
        eth_price = st.number_input(
            'ETH Price (USD)',
            value=3000,
            min_value=100,
            help="Current ETH price in USD"
        )
        funding_rate = st.slider(
            'Funding Rate (% per year)',
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=0.1,
            help="Annual funding rate for futures"
        ) / 100

    # AAVE параметры в отдельном контейнере
    with st.expander("AAVE Parameters", expanded=True):
        eth_supply_rate = st.slider(
            'ETH Supply Rate (% per year)',
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.1,
            help="Annual supply rate for ETH on AAVE"
        ) / 100
        usdc_borrow_rate = st.slider(
            'USDC Borrow Rate (% per year)',
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            help="Annual borrow rate for USDC on AAVE"
        ) / 100
        ltv_max = st.slider(
            'Maximum LTV',
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.01,
            help="Maximum Loan-to-Value ratio on AAVE"
        )
        liquidation_threshold = st.slider(
            'Liquidation Threshold',
            min_value=0.0,
            max_value=1.0,
            value=0.825,
            step=0.001,
            help="Liquidation threshold on AAVE"
        )

    # Параметры риска
    with st.expander("Risk Parameters", expanded=True):
        min_liq_distance = st.slider(
            'Minimum Liquidation Distance (%)',
            min_value=5,
            max_value=50,
            value=30,
            step=1,
            help="Minimum safe distance to liquidation price"
        )

    calculate_button = st.button('Calculate Optimal Strategy', use_container_width=True)

# Основной контент
if calculate_button:
    with st.spinner('Calculating optimal strategy...'):
        result = calculate_funding_arbitrage(
            capital=capital,
            eth_price=eth_price,
            ltv_max=ltv_max,
            liquidation_threshold=liquidation_threshold,
            funding_rate=funding_rate,
            eth_supply_rate=eth_supply_rate,
            usdc_borrow_rate=usdc_borrow_rate,
            min_liq_distance=min_liq_distance
        )
    
    if result:
        # Создаем вкладки для разных групп метрик
        tab1, tab2, tab3 = st.tabs(["💰 Position Overview", "📊 Risk Metrics", "📈 Performance"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "Capital Spot",
                    f"{result['Capital_Spot']:,.2f} USDT",
                    f"{result['Capital_Spot']/capital*100:.1f}% of capital"
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col2:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "Capital Futures",
                    f"{result['Capital_Futures']:,.2f} USDT",
                    f"{result['Capital_Futures']/capital*100:.1f}% of capital"
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col3:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "Borrow Amount",
                    f"{result['Borrow_Amount']:,.2f} USDT",
                    f"LTV: {result['LTV']*100:.1f}%"
                )
                st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Spot Position")
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("Leverage", f"{result['Leverage_Spot']:.2f}x")
                st.metric("Liquidation Price", f"${result['Liq_Price_Spot']:.2f}")
                st.metric("Distance to Liquidation", f"{result['Liq_Distance_Spot_%']:.1f}%")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col2:
                st.markdown("### Futures Position")
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("Leverage", f"{result['Leverage_Futures']:.2f}x")
                st.metric("Liquidation Price", f"${result['Liq_Price_Futures']:.2f}")
                st.metric("Distance to Liquidation", f"{result['Liq_Distance_Futures_%']:.1f}%")
                st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "Annual ROI",
                    f"{result['ROI']*100:.2f}%",
                    f"${result['Net_Income']:,.2f} income"
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col2:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "ETH Position",
                    f"{result['Total_ETH']:.4f} ETH",
                    f"${result['Futures_Position_Size']:,.2f} total exposure"
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col3:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric(
                    "Borrowed ETH",
                    f"{result['ETH_Borrowed']:.4f} ETH",
                    f"{result['ETH_Borrowed']/result['Total_ETH']*100:.1f}% of position"
                )
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error('No valid strategy found with given parameters. Try adjusting your inputs.')

# Добавляем footer
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)
