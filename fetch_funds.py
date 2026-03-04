# FourFund - Data Collection Script v4
# Uses historical data to calculate returns + known expense ratios

import yfinance as yf
import json
from datetime import datetime
import time

# Known expense ratios for popular funds (static data - these don't change often)
# Format: ticker: (expense_ratio_as_decimal, category, name)
# Note: These are the NET expense ratios (already low!)
KNOWN_FUNDS = {
    # Large Cap Growth ETFs
    'SPYG': (0.000945, 'Large Cap Growth', 'SPDR Portfolio S&P 500 Growth'),
    'IVW': (0.00104, 'Large Cap Growth', 'iShares S&P 500 Growth'),
    'QQQM': (0.0015, 'Large Cap Growth', 'Invesco NASDAQ 100'),
    'VGT': (0.0010, 'Large Cap Growth', 'Vanguard Info Tech'),
    'XLK': (0.0010, 'Large Cap Growth', 'Tech Select Sector SPDR'),
    'VOO': (0.0003, 'Large Cap Growth', 'Vanguard S&P 500'),
    'IWF': (0.0019, 'Large Cap Growth', 'iShares Russell 1000 Growth'),
    'IWD': (0.0019, 'Large Cap Growth', 'iShares Russell 1000 Value'),
    
    # Mid Cap
    'VO': (0.0004, 'Mid Cap', 'Vanguard Mid-Cap ETF'),
    'IJH': (0.0005, 'Mid Cap', 'iShares Core S&P Mid-Cap'),
    'MDY': (0.000945, 'Mid Cap', 'SPDR S&P MidCap 400'),
    'VOT': (0.0004, 'Mid Cap', 'Vanguard Mid-Cap Growth'),
    'IJK': (0.0017, 'Mid Cap', 'iShares S&P MidCap 400 Growth'),
    
    # Small Cap
    'VB': (0.0005, 'Small Cap', 'Vanguard Small-Cap ETF'),
    'IJR': (0.0006, 'Small Cap', 'iShares Core S&P Small-Cap'),
    'IWM': (0.0019, 'Small Cap', 'iShares Russell 2000'),
    'SCHA': (0.0005, 'Small Cap', 'Schwab US Small-Cap'),
    'SLY': (0.0019, 'Small Cap', 'SPDR S&P 600 Small Cap'),
    
    # International
    'VXUS': (0.0007, 'International', 'Vanguard Total Intl Stock'),
    'IXUS': (0.0007, 'International', 'iShares Core MSCI Total Intl'),
    'VEU': (0.0007, 'International', 'Vanguard FTSE All-World ex-US'),
    'VEA': (0.0005, 'International', 'Vanguard FTSE Developed Markets'),
    'VWO': (0.0008, 'International', 'Vanguard FTSE Emerging Markets'),
    'IEFA': (0.0007, 'International', 'iShares Core MSCI EAFE'),
    'EFA': (0.0032, 'International', 'iShares MSCI EAFE'),
    'IEMG': (0.0009, 'International', 'iShares Core MSCI Emerging'),
    'SCHF': (0.0006, 'International', 'Schwab Intl Equity ETF'),
    'ACWX': (0.0032, 'International', 'iShares MSCI ACWI ex US'),
    'SPDW': (0.0004, 'International', 'SPDR MSCI World exUS'),
    'SPEM': (0.0011, 'International', 'SPDR MSCI Emerging Markets'),
    'EEM': (0.0068, 'International', 'iShares MSCI Emerging Markets'),
}

def get_fund_data(ticker):
    """Get data for a single fund"""
    try:
        if ticker not in KNOWN_FUNDS:
            return None
            
        expense_ratio, category, name = KNOWN_FUNDS[ticker]
        
        fund = yf.Ticker(ticker)
        
        # Get historical data to calculate returns
        hist = fund.history(period='10y')
        
        if len(hist) < 100:  # Need enough data
            return None
        
        # Get current price and calculate returns
        now = hist['Close'].iloc[-1]
        
        # Get oldest available price
        oldest_price = hist['Close'].iloc[0]
        years_available = len(hist) / 252
        
        # Calculate return from oldest available data
        total_return = ((now - oldest_price) / oldest_price) * 100
        
        # Calculate 5-year return if available
        five_year_return = None
        if len(hist) >= 252 * 5:
            five_year_price = hist['Close'].iloc[-252*5]
            five_year_return = ((now - five_year_price) / five_year_price) * 100
        
        # Calculate 3-year return if available
        three_year_return = None
        if len(hist) >= 252 * 3:
            three_year_price = hist['Close'].iloc[-252*3]
            three_year_return = ((now - three_year_price) / three_year_price) * 100
        
        # Calculate 1-year return
        one_year_return = None
        if len(hist) >= 252:
            one_year_price = hist['Close'].iloc[-252]
            one_year_return = ((now - one_year_price) / one_year_price) * 100
        
        data = {
            'ticker': ticker,
            'name': name,
            'category': category,
            'expense_ratio': expense_ratio,
            'expense_percent': expense_ratio * 100,
            'is_no_load': True,  # All ETFs are no-load
            'ten_year': total_return,
            'five_year': five_year_return,
            'three_year': three_year_return,
            'one_year': one_year_return,
            'years_available': round(years_available, 1),
        }
        
        return data
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def rank_funds(funds_data):
    """Rank funds by Ramsey-style criteria"""
    valid_funds = []
    
    for fund in funds_data:
        if fund and fund.get('ten_year') and fund['ten_year'] > 0:
            # Calculate score
            # Lower expense = huge bonus (all these are < 0.5%)
            # Score heavily rewards lower expense ratios
            expense_score = max(0, 30 - (fund['expense_ratio'] * 10000))  # Max 30 points
            
            # Consistency: reward solid 10-year returns
            consistency_score = min(fund['ten_year'] / 3, 40)  # Max 40 points
            
            # Overall score
            fund['score'] = round(expense_score + consistency_score, 1)
            valid_funds.append(fund)
    
    # Sort by score (highest first)
    valid_funds.sort(key=lambda x: x['score'], reverse=True)
    return valid_funds

def main():
    print("Fetching fund data...")
    all_funds = {
        'Large Cap Growth': [],
        'Mid Cap': [],
        'Small Cap': [],
        'International': []
    }
    
    tickers = list(KNOWN_FUNDS.keys())
    total = len(tickers)
    
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i}/{total}] {ticker}...", end=" ", flush=True)
        data = get_fund_data(ticker)
        if data:
            all_funds[data['category']].append(data)
            years = data.get('years_available', 0)
            ret = data.get('ten_year')
            ret_str = f"{ret:.1f}%" if ret else "N/A"
            print(f"✓ {years}Y data, Return: {ret_str}")
        else:
            print("✗")
        time.sleep(0.15)  # Rate limiting
    
    # Rank each category
    print("\nRanking funds...")
    for category in all_funds:
        all_funds[category] = rank_funds(all_funds[category])
    
    # Save results
    output = {
        'generated': datetime.now().isoformat(),
        'funds': all_funds
    }
    
    with open('fund_data.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✓ Data saved to fund_data.json")
    
    # Print results
    print("\n" + "="*70)
    print("FOURFUND - TOP RECOMMENDED FUNDS")
    print("="*70)
    
    for category, funds in all_funds.items():
        print(f"\n{category}:")
        if not funds:
            print("  No qualifying funds found")
        else:
            for i, fund in enumerate(funds[:5], 1):
                print(f"  {i}. {fund['ticker']} - {fund['name']}")
                print(f"     Expense: {fund['expense_percent']:.2f}%, {fund.get('years_available', 0)}Y Return: {fund['ten_year']:.1f}%")
                print(f"     Score: {fund['score']}")

if __name__ == "__main__":
    main()
