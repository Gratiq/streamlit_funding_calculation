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

# Streamlit UI
st.title('Funding Arbitrage Calculator')

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
        
        # Создаем HTML таблицу
        html = '''
        <style>
            .results-table {
                width: 100%;
                border-collapse: collapse;
            }
            .results-table td {
                padding: 8px;
                border: none;
            }
            .section-header {
                text-align: center;
                padding: 15px;
                font-weight: bold;
                background-color: #f5f5f5;
            }
            .param-name {
                padding-left: 30px;
            }
        </style>
        <table class="results-table">
            <tr><td colspan="2" class="section-header">Capital Distribution</td></tr>
            <tr><td class="param-name">Capital Spot</td><td>{:,.2f} USDT</td></tr>
            <tr><td class="param-name">Capital Futures</td><td>{:,.2f} USDT</td></tr>
            <tr><td class="param-name">Borrow Amount</td><td>{:,.2f} USDT</td></tr>
            
            <tr><td colspan="2" class="section-header">Position Details</td></tr>
            <tr><td class="param-name">ETH Initial</td><td>{:.4f} ETH</td></tr>
            <tr><td class="param-name">ETH Borrowed</td><td>{:.4f} ETH</td></tr>
            <tr><td class="param-name">Total ETH</td><td>{:.4f} ETH</td></tr>
            
            <tr><td colspan="2" class="section-header">Leverage</td></tr>
            <tr><td class="param-name">Spot Leverage</td><td>{:.2f}x</td></tr>
            <tr><td class="param-name">Futures Leverage</td><td>{:.2f}x</td></tr>
            
            <tr><td colspan="2" class="section-header">Liquidation Prices</td></tr>
            <tr><td class="param-name">Spot Liquidation</td><td>${:.2f}</td></tr>
            <tr><td class="param-name">Futures Liquidation</td><td>${:.2f}</td></tr>
            <tr><td class="param-name">Spot Distance</td><td>{:.2f}%</td></tr>
            <tr><td class="param-name">Futures Distance</td><td>{:.2f}%</td></tr>
            
            <tr><td colspan="2" class="section-header">Performance Metrics</td></tr>
            <tr><td class="param-name">ROI (annual)</td><td>{:.2f}%</td></tr>
            <tr><td class="param-name">Net Income</td><td>{:,.2f} USDT</td></tr>
            <tr><td class="param-name">LTV</td><td>{:.2f}%</td></tr>
        </table>
        '''.format(
            result['Capital_Spot'],
            result['Capital_Futures'],
            result['Borrow_Amount'],
            result['ETH_Initial'],
            result['ETH_Borrowed'],
            result['Total_ETH'],
            result['Leverage_Spot'],
            result['Leverage_Futures'],
            result['Liq_Price_Spot'],
            result['Liq_Price_Futures'],
            result['Liq_Distance_Spot_%'],
            result['Liq_Distance_Futures_%'],
            result['ROI']*100,
            result['Net_Income'],
            result['LTV']*100
        )
        
        st.markdown(html, unsafe_allow_html=True)
        
    else:
        st.error('No valid strategy found with given parameters')
