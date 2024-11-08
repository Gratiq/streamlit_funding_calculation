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
st.markdown('### Optimize your funding strategies and visualize results with enhanced clarity.')

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
    st.subheader('AAVE Parameters')
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
        st.header('Optimal Strategy Results')
        
        # Display results in sections for better readability
        st.subheader('Capital Allocation')
        st.write(f"Capital Spot (USDT): {result['Capital Spot (USDT)']}")
        st.write(f"Capital Futures (USDT): {result['Capital Futures (USDT)']}")
        st.write(f"Borrow Amount (USDT): {result['Borrow Amount (USDT)']}")

        st.subheader('ETH Position Details')
        st.write(f"ETH Initial: {result['ETH Initial']}")
        st.write(f"ETH Borrowed: {result['ETH Borrowed']}")
        st.write(f"Total ETH: {result['Total ETH']}")

        st.subheader('Leverage and Risk Metrics')
        st.write(f"LTV: {result['LTV']}")
        st.write(f"Spot Leverage: {result['Spot Leverage']}")
        st.write(f"Liq. Price Spot (USD): {result['Liq. Price Spot (USD)']}")
        st.write(f"Liq. Distance Spot (%): {result['Liq. Distance Spot (%)']}")
        
        st.subheader('Futures Position Metrics')
        st.write(f"Futures Position Size (USDT): {result['Futures Position Size (USDT)']}")
        st.write(f"Futures Leverage: {result['Futures Leverage']}")
        st.write(f"Liq. Price Futures (USD): {result['Liq. Price Futures (USD)']}")
        st.write(f"Liq. Distance Futures (%): {result['Liq. Distance Futures (%)']}")
        
        st.subheader('Income and ROI')
        st.write(f"Net Income (USDT): {result['Net Income (USDT)']}")
        st.write(f"ROI (%): {result['ROI (%)']}")
        
        st.success('Calculation complete. Check the results above.')
    else:
        st.error('No valid strategy found with given parameters')
