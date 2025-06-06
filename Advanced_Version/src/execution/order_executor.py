class SmartOrderRouter:
    def __init__(self, client, market_data):
        self.client = client
        self.market_data = market_data
    
    def determine_best_execution(self, order):
        liquidity_score = self._calculate_liquidity_score(order['symbol'])
        
        if liquidity_score > 0.7:
            return {
                'type': 'VWAP',
                'params': {'duration': '15min'}
            }
        elif liquidity_score > 0.4:
            return {
                'type': 'TWAP',
                'params': {'slices': 5}
            }
        else:
            return {
                'type': 'LIMIT',
                'params': {'price': self._calculate_limit_price(order)}
            }
    
    def _calculate_liquidity_score(self, symbol):
        book = self.market_data.get_order_book(symbol)
        spread = book['ask'][0] - book['bid'][0]
        depth = sum(book['bid_qty'][:3]) + sum(book['ask_qty'][:3])
        return min(1.0, depth / 10000) * (1 - min(1.0, spread / (book['bid'][0] * 0.01)))
    
    def _calculate_limit_price(self, order):
        mid = (self.market_data.bid + self.market_data.ask) / 2
        if order['side'] == 'BUY':
            return mid * 0.9995
        else:
            return mid * 1.0005

class TransactionCostAnalyzer:
    def __init__(self):
        self.historical_slippage = {}
    
    def record_execution(self, symbol, intended_price, actual_price, size):
        slippage = (actual_price - intended_price) / intended_price
        if symbol not in self.historical_slippage:
            self.historical_slippage[symbol] = []
        self.historical_slippage[symbol].append({
            'slippage': slippage,
            'size': size,
            'timestamp': datetime.now()
        })
    
    def predict_slippage(self, symbol, size):
        if symbol not in self.historical_slippage:
            return 0.0005  # Default estimate
        
        recent = [x for x in self.historical_slippage[symbol] 
                 if datetime.now() - x['timestamp'] < timedelta(days=30)]
        
        if not recent:
            return 0.0005
        
        # Weighted average by size
        total_size = sum(x['size'] for x in recent)
        return sum(x['slippage'] * (x['size'] / total_size) for x in recent)