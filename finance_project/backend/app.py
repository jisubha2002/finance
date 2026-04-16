from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
import json
from functools import wraps
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configure session - Updated for newer versions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session'

# Create session directory if it doesn't exist
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize session
Session(app)

# Configure CORS for frontend
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:5173"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

class EnhancedNSEStockAnalyzer:
    def __init__(self, start_date='2022-01-01'):
        self.start_date = start_date
        self.end_date = datetime.now().strftime('%Y-%m-%d')

        # NIFTY 50 stocks
        self.nifty50_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'LT.NS',
            'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS',
            'ULTRACEMCO.NS', 'NESTLEIND.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'ONGC.NS',
            'NTPC.NS', 'POWERGRID.NS', 'TECHM.NS', 'HCLTECH.NS', 'SBIN.NS',
            'ADANIPORTS.NS', 'COALINDIA.NS', 'TATASTEEL.NS', 'GRASIM.NS', 'JSWSTEEL.NS',
            'INDUSINDBK.NS', 'BAJAJFINSV.NS', 'M&M.NS', 'DRREDDY.NS', 'CIPLA.NS',
            'EICHERMOT.NS', 'APOLLOHOSP.NS', 'DIVISLAB.NS', 'BRITANNIA.NS', 'TATACONSUM.NS',
            'HEROMOTOCO.NS', 'SHREECEM.NS', 'HINDALCO.NS', 'BPCL.NS', 'TATAMOTORS.NS',
            'ADANIENT.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'BAJAJ-AUTO.NS', 'LTIM.NS'
        ]

        # NIFTY Next 50 stocks
        self.nifty_next50_stocks = [
            'MOTHERSUMI.NS', 'GODREJCP.NS', 'SIEMENS.NS', 'BOSCHLTD.NS', 'HAVELLS.NS',
            'PAGEIND.NS', 'PIDILITIND.NS', 'TORNTPHARM.NS', 'AMBUJACEM.NS', 'DABUR.NS',
            'MARICO.NS', 'SRF.NS', 'LUPIN.NS', 'GAIL.NS', 'CONCOR.NS',
            'BANKBARODA.NS', 'NMDC.NS', 'NAUKRI.NS', 'MCDOWELL-N.NS', 'CHOLAFIN.NS',
            'TRENT.NS', 'INDIGO.NS', 'DMART.NS', 'ZYDUSLIFE.NS', 'IPCALAB.NS',
            'POLYCAB.NS', 'MPHASIS.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS', 'OFSS.NS',
            'CADILAHC.NS', 'COLPAL.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 'HDFCAMC.NS',
            'ICICIPRULI.NS', 'INDUSTOWER.NS', 'IOC.NS', 'IRCTC.NS', 'JINDALSTEL.NS',
            'LICHSGFIN.NS', 'MRF.NS', 'PEL.NS', 'PIRAMALENT.NS', 'PNB.NS',
            'RAMCOCEM.NS', 'TVSMOTOR.NS', 'UBL.NS', 'VEDL.NS', 'VOLTAS.NS'
        ]

        # Additional NIFTY 100 stocks
        self.nifty100_additional = [
            'ABBOTINDIA.NS', 'ABCAPITAL.NS', 'ALKEM.NS', 'APOLLOTYRE.NS', 'ASHOKLEY.NS',
            'AUBANK.NS', 'AUROPHARMA.NS', 'BALKRISIND.NS', 'BATAINDIA.NS', 'BEL.NS',
            'BHARATFORG.NS', 'BIOCON.NS', 'BSOFT.NS', 'CANBK.NS', 'CANFINHOME.NS',
            'CASTROLIND.NS', 'CEATLTD.NS', 'CHAMBLFERT.NS', 'CHOLAHLDNG.NS', 'COFORGE.NS'
        ]

        # NIFTY 200 additional stocks
        self.nifty200_additional = [
            'ACC.NS', 'AFFLE.NS', 'AJANTPHARM.NS', 'ASTRAL.NS', 'ATUL.NS',
            'BALRAMCHIN.NS', 'BHEL.NS', 'BLUEDART.NS', 'CESCLTD.NS', 'CLEAN.NS',
            'COROMANDEL.NS', 'CROMPTON.NS', 'CUB.NS', 'CUMMINSIND.NS', 'DELTACORP.NS',
            'DIXON.NS', 'DLF.NS', 'ESCORTS.NS', 'EXIDEIND.NS', 'FEDERALBNK.NS',
            'FORTIS.NS', 'FSL.NS', 'GICRE.NS', 'GILLETTE.NS', 'GLAXO.NS',
            'GMRINFRA.NS', 'GNFC.NS', 'GRANULES.NS', 'GSPL.NS', 'GUJGASLTD.NS',
            'HAL.NS', 'HEIDELBERG.NS', 'HINDPETRO.NS', 'HONAUT.NS', 'HUDCO.NS',
            'IBULHSGFIN.NS', 'IDFCFIRSTB.NS', 'IEX.NS', 'IGL.NS', 'INDHOTEL.NS',
            'INDIAMART.NS', 'INTELLECT.NS', 'IOB.NS', 'IRB.NS', 'ISEC.NS',
            'ITI.NS', 'JBCHEPHARM.NS', 'JKCEMENT.NS', 'JKLAKSHMI.NS', 'JMFINANCIL.NS'
        ]

        # NSE Midcap 100 stocks
        self.midcap100_stocks = [
            'ABFRL.NS', 'PERSISTENT.NS', 'MANAPPURAM.NS', 'MUTHOOTFIN.NS', 'RECLTD.NS',
            'SAIL.NS', 'SHOPERSTOP.NS', 'STARHEALTH.NS', 'SYNGENE.NS', 'TATACHEM.NS',
            'TATACOMM.NS', 'TATAELXSI.NS', 'TATAPOWER.NS', 'THERMAX.NS', 'TIINDIA.NS',
            'TORNTPOWER.NS', 'TTKPRESTIG.NS', 'UJJIVAN.NS', 'UNIONBANK.NS', 'UPL.NS',
            'VGUARD.NS', 'VINATIORGA.NS', 'VIPIND.NS', 'WHIRLPOOL.NS', 'WOCKPHARMA.NS',
            'YESBANK.NS', 'ZEEL.NS', 'ZENSARTECH.NS', 'LALPATHLAB.NS', 'LAURUSLABS.NS',
            'LEMONTREE.NS', 'LTTS.NS', 'MINDTREE.NS', 'MMTC.NS', 'MOIL.NS',
            'NATIONALUM.NS', 'NAVINFLUOR.NS', 'NBCC.NS', 'NCC.NS', 'NIACL.NS',
            'NLCINDIA.NS', 'NOCIL.NS', 'OBEROIRLTY.NS', 'ORIENTBANK.NS', 'PETRONET.NS',
            'PFIZER.NS', 'PHOENIXLTD.NS', 'POLYMED.NS', 'PVRINOX.NS', 'QUESS.NS',
            'RAIN.NS', 'RAJESHEXPO.NS', 'RBLBANK.NS', 'REDINGTON.NS', 'RELAXO.NS',
            'ROUTE.NS', 'SANOFI.NS', 'SCHAEFFLER.NS', 'SEQUENT.NS', 'SFL.NS',
            'SHANKARA.NS', 'SHILPAMED.NS', 'SJVN.NS', 'SKFINDIA.NS', 'SOBHA.NS',
            'SOLARINDS.NS', 'SONACOMS.NS', 'STARCEMENT.NS', 'SUBEXLTD.NS', 'SUNDARMFIN.NS',
            'SUNDRMFAST.NS', 'SUPREMEIND.NS', 'TIMKEN.NS', 'VAKRANGEE.NS', 'VMART.NS'
        ]

        # NSE Smallcap 100 stocks
        self.smallcap100_stocks = [
            'AAVAS.NS', 'AIAENG.NS', 'ANANTRAJ.NS', 'APARINDS.NS', 'ARVINDFASN.NS',
            'BASF.NS', 'BIRLACORPN.NS', 'BLUESTARCO.NS', 'CENTURYPLY.NS', 'CHALET.NS',
            'CRISIL.NS', 'CYIENT.NS', 'DCMSHRIRAM.NS', 'DEVYANI.NS', 'ECLERX.NS',
            'FILATEX.NS', 'FINEORG.NS', 'FINPIPE.NS', 'FLUOROCHEM.NS', 'GPPL.NS',
            'GRINDWELL.NS', 'HLEGLAS.NS', 'HOMEFIRST.NS', 'HSIL.NS', 'IFBIND.NS',
            'IGPL.NS', 'INOXWIND.NS', 'JCHAC.NS', 'JYOTHYLAB.NS', 'KAJARIACER.NS',
            'KPRMILL.NS', 'KRSNAA.NS', 'LAXMIMACH.NS', 'LINC.NS', 'LUXIND.NS',
            'MAHSCOOTER.NS', 'MAPMYINDIA.NS', 'MEDPLUS.NS', 'METROPOLIS.NS', 'MGEL.NS',
            'MIDHANI.NS', 'MOLDTKPAC.NS', 'MOTILALOFS.NS', 'NEWGEN.NS', 'NYKAA.NS',
            'PAYTM.NS', 'PNBHOUSING.NS', 'PRSMJOHNSN.NS', 'RAILTEL.NS', 'RATNAMANI.NS',
            'RITES.NS', 'ROUTE.NS', 'RTNINDIA.NS', 'SCHNEIDER.NS', 'SHYAMMETL.NS',
            'SNOWMAN.NS', 'SOLARINDS.NS', 'SPLPETRO.NS', 'STLTECH.NS', 'SUDARSCHEM.NS',
            'SYMPHONY.NS', 'TARSONS.NS', 'TEAMLEASE.NS', 'TECHM.NS', 'TEXRAIL.NS',
            'THYROCARE.NS', 'TITAGARH.NS', 'TRIDENT.NS', 'TRITURBINE.NS', 'VAIBHAVGBL.NS',
            'VARROC.NS', 'VSTIND.NS', 'WELCORP.NS', 'WESTLIFE.NS', 'WONDERLA.NS'
        ]

        # Major F&O stocks
        self.fo_stocks = [
            'ABCAPITAL.NS', 'AMBUJACEM.NS', 'APOLLOTYRE.NS', 'ASHOKLEY.NS', 'ASTRAL.NS',
            'BALRAMCHIN.NS', 'BHARATFORG.NS', 'CANBK.NS', 'CANFINHOME.NS', 'CHOLAFIN.NS',
            'COFORGE.NS', 'CROMPTON.NS', 'CUMMINSIND.NS', 'DELTACORP.NS', 'ESCORTS.NS',
            'EXIDEIND.NS', 'FEDERALBNK.NS', 'GAIL.NS', 'GMRINFRA.NS', 'GODREJCP.NS',
            'HAVELLS.NS', 'IDEA.NS', 'IDFCFIRSTB.NS', 'IGL.NS', 'INDIAMART.NS',
            'JINDALSTEL.NS', 'LICHSGFIN.NS', 'LUPIN.NS', 'MANAPPURAM.NS', 'MCDOWELL-N.NS',
            'MOTHERSUMI.NS', 'MUTHOOTFIN.NS', 'NMDC.NS', 'PAGEIND.NS', 'PEL.NS',
            'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS', 'POLYCAB.NS', 'RBLBANK.NS',
            'RECLTD.NS', 'SAIL.NS', 'SIEMENS.NS', 'SRF.NS', 'TATACOMM.NS',
            'TORNTPHARM.NS', 'TRENT.NS', 'TVSMOTOR.NS', 'UBL.NS', 'VEDL.NS'
        ]

        # Combine all unique stocks
        all_stocks = set()
        all_stocks.update(self.nifty50_stocks)
        all_stocks.update(self.nifty_next50_stocks)
        all_stocks.update(self.nifty100_additional)
        all_stocks.update(self.nifty200_additional)
        all_stocks.update(self.midcap100_stocks)
        all_stocks.update(self.smallcap100_stocks)
        all_stocks.update(self.fo_stocks)

        self.all_stocks = list(all_stocks)

        # Create index mappings
        self.stock_index_map = {}
        for stock in self.nifty50_stocks:
            self.stock_index_map[stock] = 'NIFTY50'
        for stock in self.nifty_next50_stocks:
            self.stock_index_map[stock] = 'NIFTY_NEXT50'
        for stock in self.nifty100_additional:
            self.stock_index_map[stock] = 'NIFTY100'
        for stock in self.nifty200_additional:
            self.stock_index_map[stock] = 'NIFTY200'
        for stock in self.midcap100_stocks:
            self.stock_index_map[stock] = 'MIDCAP100'
        for stock in self.smallcap100_stocks:
            self.stock_index_map[stock] = 'SMALLCAP100'
        for stock in self.fo_stocks:
            if stock not in self.stock_index_map:
                self.stock_index_map[stock] = 'FO_STOCKS'

    def fetch_stock_data(self, symbol):
        """Fetch stock data for a given symbol"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(start=self.start_date, end=self.end_date)
            if data.empty:
                return None

            data['Daily_Return_Pct'] = ((data['Close'] - data['Open']) / data['Open']) * 100
            data['High_Low_Range'] = data['High'] - data['Low']
            data['Close_to_High'] = np.where(data['High_Low_Range'] > 0,
                                           (data['High'] - data['Close']) / data['High_Low_Range'], 0)
            data['Close_to_Low'] = np.where(data['High_Low_Range'] > 0,
                                          (data['Close'] - data['Low']) / data['High_Low_Range'], 0)
            data['Avg_Volume_20d'] = data['Volume'].rolling(window=20).mean()
            data['Volume_Ratio'] = data['Volume'] / data['Avg_Volume_20d']

            return data
        except Exception as e:
            return None

    def analyze_stock_movement(self, data, symbol):
        """Analyze stock for 5%+ moves"""
        if data is None or data.empty:
            return []

        results = []
        index_category = self.stock_index_map.get(symbol, 'OTHER')

        for date, row in data.iterrows():
            daily_return = row['Daily_Return_Pct']
            volume_ratio = row['Volume_Ratio']
            close_to_high = row['Close_to_High']
            close_to_low = row['Close_to_Low']

            if pd.isna(volume_ratio) or pd.isna(daily_return):
                continue

            if abs(daily_return) >= 5.0:
                if daily_return > 0 and close_to_high <= 0.15:
                    results.append({
                        'Symbol': symbol.replace('.NS', ''),
                        'Index': index_category,
                        'Date': date.strftime('%Y-%m-%d'),
                        'Type': 'UP',
                        'Move': round(daily_return, 2),
                        'Open': round(row['Open'], 2),
                        'High': round(row['High'], 2),
                        'Low': round(row['Low'], 2),
                        'Close': round(row['Close'], 2),
                        'ClosePos': f"{round((1-close_to_high)*100, 1)}% from High",
                        'VolRatio': round(volume_ratio, 2),
                        'VolChange': f"{round((volume_ratio-1)*100, 1)}%"
                    })
                elif daily_return < 0 and close_to_low <= 0.15:
                    results.append({
                        'Symbol': symbol.replace('.NS', ''),
                        'Index': index_category,
                        'Date': date.strftime('%Y-%m-%d'),
                        'Type': 'DOWN',
                        'Move': round(daily_return, 2),
                        'Open': round(row['Open'], 2),
                        'High': round(row['High'], 2),
                        'Low': round(row['Low'], 2),
                        'Close': round(row['Close'], 2),
                        'ClosePos': f"{round(close_to_low*100, 1)}% from Low",
                        'VolRatio': round(volume_ratio, 2),
                        'VolChange': f"{round((volume_ratio-1)*100, 1)}%"
                    })

        return results

    def run_analysis(self, max_stocks=None):
        """Run complete analysis"""
        all_results = []
        # For testing, use fewer stocks to avoid long wait times
        stocks_to_process = self.all_stocks[:50] if max_stocks is None else self.all_stocks[:max_stocks]
        total_stocks = len(stocks_to_process)
        processed = 0

        print(f"Analyzing {total_stocks} NSE stocks...")

        for symbol in stocks_to_process:
            processed += 1
            if processed % 10 == 0:
                print(f"Processed {processed}/{total_stocks} stocks...")

            data = self.fetch_stock_data(symbol)
            if data is not None:
                results = self.analyze_stock_movement(data, symbol)
                all_results.extend(results)

        if not all_results:
            return pd.DataFrame()

        df = pd.DataFrame(all_results)
        df = df.sort_values(['Date', 'VolRatio'], ascending=[False, False])
        return df

    def get_summary_data(self, df):
        if df.empty:
            return {
                'totalInstances': 0,
                'upMoves': 0,
                'downMoves': 0,
                'uniqueStocks': 0,
                'highVolumeDays': 0,
                'dateRange': 'N/A'
            }
        return {
            'totalInstances': len(df),
            'upMoves': len(df[df['Type'] == 'UP']),
            'downMoves': len(df[df['Type'] == 'DOWN']),
            'uniqueStocks': df['Symbol'].nunique(),
            'highVolumeDays': len(df[df['VolRatio'] >= 2.0]),
            'dateRange': f"{df['Date'].min()} to {df['Date'].max()}"
        }

    def get_index_breakdown(self, df):
        if df.empty:
            return []
        breakdown = df['Index'].value_counts().reset_index()
        breakdown.columns = ['index', 'count']
        return breakdown.to_dict('records')

    def get_recent_occurrences(self, df):
        if df.empty:
            return []
        return df.head(150).to_dict('records')

    def get_high_volume_data(self, df):
        if df.empty:
            return []
        return df[df['VolRatio'] >= 2.0].head(30).to_dict('records')

    def get_stock_summary(self, df):
        if df.empty:
            return []
        stock_summary = df.groupby(['Symbol', 'Index']).agg({
            'Date': 'count',
            'Type': lambda x: f"{sum(x=='UP')}/{sum(x=='DOWN')}",
            'VolRatio': 'mean',
            'Move': ['mean', 'std']
        }).round(2)
        stock_summary.columns = ['Count', 'UpDown', 'AvgVolRatio', 'AvgMove', 'MoveStd']
        stock_summary = stock_summary.reset_index()
        stock_summary = stock_summary.sort_values('Count', ascending=False).head(30)
        return stock_summary.to_dict('records')

    def get_index_performance(self, df):
        if df.empty:
            return []
        index_perf = df.groupby('Index').agg({
            'Date': 'count',
            'Type': lambda x: f"{sum(x=='UP')}/{sum(x=='DOWN')}",
            'VolRatio': 'mean',
            'Move': ['mean', 'std'],
            'Symbol': 'nunique'
        }).round(2)
        index_perf.columns = ['Total', 'UpDown', 'AvgVolRatio', 'AvgMove', 'MoveStd', 'UniqueStocks']
        index_perf = index_perf.reset_index()
        index_perf = index_perf.sort_values('Total', ascending=False)
        return index_perf.to_dict('records')

# Initialize analyzer
analyzer = EnhancedNSEStockAnalyzer(start_date='2022-01-01')

# Run analysis (limit to 50 stocks for faster initial load)
print("Starting analysis...")
results_df = analyzer.run_analysis(max_stocks=50)
print(f"Analysis complete! Found {len(results_df)} instances.")

# Cache for storing uploaded file data
uploaded_data = None

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"success": False, "message": "No authorization token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if email == 'security@alphaxine.com' and password == 'Alphaxine@security1234':
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    if request.method == 'OPTIONS':
        return '', 200
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})

@app.route('/api/summary', methods=['GET', 'OPTIONS'])
def get_summary():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_summary_data(results_df))

@app.route('/api/index-breakdown', methods=['GET', 'OPTIONS'])
def get_index_breakdown():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_index_breakdown(results_df))

@app.route('/api/recent-occurrences', methods=['GET', 'OPTIONS'])
def get_recent_occurrences():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_recent_occurrences(results_df))

@app.route('/api/high-volume', methods=['GET', 'OPTIONS'])
def get_high_volume():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_high_volume_data(results_df))

@app.route('/api/stock-summary', methods=['GET', 'OPTIONS'])
def get_stock_summary():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_stock_summary(results_df))

@app.route('/api/index-performance', methods=['GET', 'OPTIONS'])
def get_index_performance():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(analyzer.get_index_performance(results_df))

@app.route('/api/refresh', methods=['POST', 'OPTIONS'])
def refresh_data():
    if request.method == 'OPTIONS':
        return '', 200
    global results_df
    results_df = analyzer.run_analysis(max_stocks=50)
    return jsonify({"success": True, "message": "Data refreshed successfully"})

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({"success": False, "message": "Unsupported file format"}), 400
        
        global results_df, uploaded_data
        uploaded_data = df.to_dict('records')
        
        # Process uploaded data
        temp_df = pd.DataFrame(uploaded_data)
        if not temp_df.empty:
            # Update results with uploaded data
            results_df = pd.concat([temp_df, results_df]).drop_duplicates(subset=['Symbol', 'Date'])
            results_df = results_df.sort_values('Date', ascending=False)
        
        return jsonify({"success": True, "message": f"File {file.filename} uploaded successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    


