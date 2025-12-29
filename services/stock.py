import asyncio
import aiohttp
import requests
import pandas as pd
import yfinance as yf
from io import StringIO

# --- 1. Hardcoded Crypto List ---
CRYPTO_LIST = {
    "bitcoin", "btc", "ethereum", "eth", "tether", "usdt", 
    "bnb", "solana", "sol", "xrp", "usdc", "cardano", "ada", 
    "avalanche", "avax", "dogecoin", "doge", "tron", "trx", 
    "polkadot", "dot", "shiba inu", "shib", "litecoin", "ltc",
    "bitcoin cash", "bch", "chainlink", "link", "cosmos", "atom",
    "crypto", "cryptocurrency", "coins"
}

# --- 2. Currency Helper ---

def get_symbol_from_code(currency_code: str) -> str:
    """Converts ISO currency codes to symbols."""
    if not currency_code: return "$"
    
    currency_map = {
        "USD": "$", "INR": "₹", "GBP": "£", "EUR": "€",
        "JPY": "¥", "AUD": "A$", "CAD": "C$", "HKD": "HK$",
        "CNY": "¥", "SGD": "S$", "CHF": "Fr", "RUB": "₽",
        "TRY": "₺", "BRL": "R$", "ZAR": "R", "KRW": "₩"
    }
    return currency_map.get(currency_code.upper(), f"{currency_code} ")

# --- 3. Dynamic List Fetcher ---

def get_tickers_from_wikipedia(city: str) -> list:
    """Scrapes Wikipedia for the latest stock list."""
    city_lower = city.lower()
    
    # --- ENHANCED RESTRICTED LOGIC ---
    restricted_map = {
        "russia": "Russia", "moscow": "Russia", "ru": "Russia",
        "china": "China", "beijing": "China", "shanghai": "China",
        "north korea": "North Korea", "iran": "Iran"
    }
    
    if city_lower in restricted_map:
        country_name = restricted_map[city_lower]
        return [f"RESTRICTED_ERROR:{city.title()}:{country_name}"]

    # --- STANDARD SCRAPING ---
    url, suffix, target_column = "", "", ""

    if city_lower in ["mumbai", "india", "delhi"]:
        print(f"   Fetching Nifty 50 list from Wikipedia...")
        url, suffix, target_column = "https://en.wikipedia.org/wiki/NIFTY_50", ".NS", "Symbol"
        
    elif city_lower in ["new york", "nyc", "usa", "us"]:
        print(f"   Fetching Dow Jones list from Wikipedia...")
        url, suffix, target_column = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average", "", "Symbol"
        
    elif city_lower in ["london", "uk"]:
        print(f"   Fetching FTSE 100 list from Wikipedia...")
        url, suffix, target_column = "https://en.wikipedia.org/wiki/FTSE_100_Index", ".L", "Ticker"

    elif city_lower in ["germany", "frankfurt", "berlin"]:
        print(f"   Fetching DAX 40 (Germany)...")
        url, suffix, target_column = "https://en.wikipedia.org/wiki/DAX", "", "Ticker"
    
    else: return []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(StringIO(response.text))

        df = None
        for table in tables:
            if target_column in table.columns:
                df = table
                break
        
        if df is None: return []

        raw_tickers = df[target_column].tolist()
        cleaned_tickers = []
        for t in raw_tickers:
            t = str(t).split('[')[0].strip()
            if t.endswith('.'): t = t[:-1] 
            if suffix and not t.endswith(suffix): t = f"{t}{suffix}"
            cleaned_tickers.append(t)

        return cleaned_tickers[:15]

    except Exception as e:
        print(f"   Scraping Error: {e}")
        return []

# --- 4. Helper: Search (Double Check) ---

async def search_symbol(query: str) -> str:
    """Finds the best ticker. STRICTLY FILTERS OUT CRYPTO."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    quotes = data.get("quotes", [])
                    if not quotes: return query

                    valid_quote = None
                    for q in quotes:
                        # Reject Crypto (Backend Check)
                        if q.get("quoteType", "").upper() == "CRYPTOCURRENCY":
                            continue 
                        
                        # Prioritize US
                        if q.get("exchange") in ["NYQ", "NMS", "NAM", "NYS", "NAS"]:
                            return q["symbol"]
                        
                        if valid_quote is None: valid_quote = q["symbol"]
                    
                    if valid_quote: return valid_quote
                    return "NO_VALID_STOCK_FOUND"

    except Exception as e:
        print(f"Search Error: {e}")
    return query

# --- 5. Core Pricing Logic ---

def _get_stock_perf_sync(ticker: str):
    """Fetches price and detects currency dynamically."""
    try:
        if ticker in ["NO_VALID_STOCK_FOUND"]: return None

        stock = yf.Ticker(ticker)
        
        # Double check metadata to block crypto
        if stock.info.get('quoteType') == 'CRYPTOCURRENCY': return None

        price = stock.fast_info.last_price
        prev_close = stock.fast_info.previous_close
        
        currency_code = stock.fast_info.currency
        currency_symbol = get_symbol_from_code(currency_code)
        
        if price is None or prev_close is None: return None

        change_percent = ((price - prev_close) / prev_close) * 100
        
        return {
            "ticker": ticker.upper(),
            "price": price,
            "change": change_percent,
            "currency": currency_symbol
        }
    except Exception:
        return None

async def find_top_gainer(city: str) -> str:
    """Scrapes list -> Scans prices -> Returns winner."""
    
    tickers = await asyncio.to_thread(get_tickers_from_wikipedia, city)
    
    # --- CHECK FOR RESTRICTED ERROR FORMAT ---
    if tickers and tickers[0].startswith("RESTRICTED_ERROR"):
        _, input_city, country = tickers[0].split(":")
        return f"{input_city} belongs to {country} and Wikipedia has no access for that information"

    if not tickers:
        return f"Sorry, I couldn't fetch the dynamic stock list for '{city}'."

    print(f"   Scanning {len(tickers)} companies in {city.title()}...")
    
    tasks = [asyncio.to_thread(_get_stock_perf_sync, t) for t in tickers]
    results = await asyncio.gather(*tasks)
    
    valid_results = [r for r in results if r is not None]
    
    if not valid_results:
        return f"Could not fetch market data for {city}."

    top_stock = max(valid_results, key=lambda x: x['change'])
    
    return (
        f"Top Gainer in {city.title()} (Live from Wikipedia):\n"
        f"   - {top_stock['ticker']}\n"
        f"   - Price: {top_stock['currency']}{top_stock['price']:,.2f}\n"
        f"   - Growth (24h): {top_stock['change']:+.2f}%"
    )

async def get_single_stock_output(ticker: str) -> str:
    if ticker == "NO_VALID_STOCK_FOUND":
        return "I can only provide the answer for companies stock only"

    data = await asyncio.to_thread(_get_stock_perf_sync, ticker)
    if not data: return f"Stock '{ticker}' not found."
    
    return f"{data['ticker']}: {data['currency']}{data['price']:,.2f} ({data['change']:+.2f}%)"

# --- 6. Main Controller ---

async def get_stock_data(query: str) -> str:
    query_lower = query.lower().strip()
    
    # --- 1. HARDCODED CRYPTO CHECK ---
    # Check if the user input matches our blocked list
    if query_lower in CRYPTO_LIST:
        return "I can only provide the answer for companies stock only"
    
    # --- 2. LOCATION & GENERAL CHECKS ---
    restricted_keys = ["russia", "moscow", "ru", "china", "beijing", "shanghai"]
    supported_scrape = ["london", "uk", "mumbai", "india", "delhi", "new york", "nyc", "usa", "us", "germany"]
    
    if query_lower in restricted_keys or query_lower in supported_scrape:
        return await find_top_gainer(query_lower)

    if query_lower == "general":
        indices = ["^GSPC", "^NSEI", "^FTSE"]
        tasks = [get_single_stock_output(i) for i in indices]
        res = await asyncio.gather(*tasks)
        return "Global Overview:\n" + "\n".join(res)

    # --- 3. SINGLE STOCK SEARCH ---
    found_ticker = await search_symbol(query)
    return await get_single_stock_output(found_ticker)
