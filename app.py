import streamlit as st
import pandas as pd

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
    
    # Iterate over capital allocation to spot from 60% to 90%
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
                "Capital Spot (USDT)": round(c_spot, 2),
                "Capital Futures (USDT)": round(c_futures, 2),
                "Borrow Amount (USDT)": round(borrow_amount, 2),
                "ETH Initial": round(eth_initial, 4),
                "ETH Borrowed": round(eth_borrowed, 4),
                "Total ETH": round(total_eth, 4),
                "LTV": round(ltv, 2),
                "Spot Leverage": round(spot_leverage, 2),
                "Liq. Price Spot (USD)": round(liq_price_spot, 2),
                "Liq. Distance Spot (%)": round(liq_distance_spot, 2),
                "Futures Position Size (USDT)": round(futures_position_size, 2),
                "Futures Leverage": round(leverage_futures, 2),
                "Liq. Price Futures (USD)": round(liq_price_futures, 2),
                "Liq. Distance Futures (%)": round(liq_distance_futures, 2),
                "Net Income (USDT)": round(net_income, 2),
                "ROI (%)": round(roi * 100, 2),
            })

    return max(results, key=lambda x: x["ROI (%)"]) if results else None

# Streamlit UI
st.title('Funding Arbitrage Calculator')
st.markdown('<h4>Optimize your funding strategies and visualize results with enhanced clarity.</h4>', unsafe_allow_html=True)

# Input parameters
with st.sidebar:
    st.header('Input Parameters')
    capital = st.number_input('Initial Capital (USDT)', value=10000)
    eth_price = st.number_input('ETH Price (USD)', value=3000)
    funding_rate = st.number_input('Funding Rate (% per year)', value=30) / 100
    eth_supply_rate = st.number_input('ETH Supply Rate (% per year)', value=2) / 100
    usdc_borrow_rate = st.number_input('USDC Borrow Rate (% per year)', value=5) / 100
    min_liq_distance = st.number_input('Minimum Liquidation Distance (%)', value=30)
    
    # AAVE parameters
    st.markdown('<h6>AAVE Parameters</h6>', unsafe_allow_html=True)
    ltv_max = st.number_input('Maximum LTV', value=0.80)
    liquidation_threshold = st.number_input('Liquidation Threshold', value=0.825)

if st.button('Calculate Optimal Strategy'):
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
        st.markdown('<h4>Optimal Strategy Results</h4>', unsafe_allow_html=True)
        
        # Display results in sections for better readability
        st.markdown('<h6>Capital Allocation</h6>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Capital Spot (USDT): {result['Capital Spot (USDT)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Capital Futures (USDT): {result['Capital Futures (USDT)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Borrow Amount (USDT): {result['Borrow Amount (USDT)']}</p>', unsafe_allow_html=True)

        st.markdown('<h6>ETH Position Details</h6>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">ETH Initial: {result['ETH Initial']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">ETH Borrowed: {result['ETH Borrowed']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Total ETH: {result['Total ETH']}</p>', unsafe_allow_html=True)

        st.markdown('<h6>Leverage and Risk Metrics</h6>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">LTV: {result['LTV']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Spot Leverage: {result['Spot Leverage']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Liq. Price Spot (USD): {result['Liq. Price Spot (USD)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Liq. Distance Spot (%): {result['Liq. Distance Spot (%)']}</p>', unsafe_allow_html=True)
        
        st.markdown('<h6>Futures Position Metrics</h6>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Futures Position Size (USDT): {result['Futures Position Size (USDT)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Futures Leverage: {result['Futures Leverage']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Liq. Price Futures (USD): {result['Liq. Price Futures (USD)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Liq. Distance Futures (%): {result['Liq. Distance Futures (%)']}</p>', unsafe_allow_html=True)
        
        st.markdown('<h6>Income and ROI</h6>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">Net Income (USDT): {result['Net Income (USDT)']}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin: 0;">ROI (%): {result['ROI (%)']}</p>', unsafe_allow_html=True)
        
        st.success('Calculation complete. Check the results above.')
    else:
        st.error('No valid strategy found with given parameters')
