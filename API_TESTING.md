# API Testing Guide for Elite AI Chart Scanner

## Setup

### 1. Start the Backend
```bash
uvicorn app.main:app --reload
```

### 2. Get API Documentation
Visit: http://localhost:8000/docs

---

## Test Scenarios

### Scenario 1: User Registration & Login

#### Register New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=trader123&email=trader@example.com&password=SecurePass123"
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=trader123&password=SecurePass123"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com"
  }
}
```

#### Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 2: Scanning Symbols

#### Scan Single Symbol
```bash
curl -X GET "http://localhost:8000/scan/AAPL?interval=1d&period=1y" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "symbol": "AAPL",
  "interval": "1d",
  "signal": "BUY",
  "confidence": 78.5,
  "price": 150.25,
  "ema20": 148.30,
  "ema50": 146.80,
  "rsi14": 62.5,
  "support": 145.00,
  "resistance": 155.00,
  "trend": "Bullish",
  "reason": "Strong uptrend | MACD bullish | Strong volume",
  "created_at": "2024-01-15T10:30:00"
}
```

#### Scan Multiple Symbols
```bash
for symbol in AAPL MSFT TSLA GOOGL; do
  curl -X GET "http://localhost:8000/scan/$symbol?interval=1d" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE"
done
```

#### Scan Different Timeframes
```bash
# 1 Hour
curl -X GET "http://localhost:8000/scan/AAPL?interval=1h" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 1 Week
curl -X GET "http://localhost:8000/scan/AAPL?interval=1wk" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Get Recent Scans
```bash
curl -X GET "http://localhost:8000/recent-scans?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 3: Watchlist Management

#### Add to Watchlist
```bash
curl -X POST "http://localhost:8000/watchlist?symbol=AAPL" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "symbol": "AAPL",
  "added_at": "2024-01-15T10:30:00",
  "is_alert_enabled": false
}
```

#### Get Watchlist
```bash
curl -X GET "http://localhost:8000/watchlist" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "symbol": "AAPL",
    "added_at": "2024-01-15T10:30:00",
    "is_alert_enabled": false
  },
  {
    "id": 2,
    "user_id": 1,
    "symbol": "MSFT",
    "added_at": "2024-01-15T10:35:00",
    "is_alert_enabled": true
  }
]
```

#### Remove from Watchlist
```bash
curl -X DELETE "http://localhost:8000/watchlist/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 4: Alert Management

#### Create Price Alert
```bash
curl -X POST "http://localhost:8000/alerts?symbol=AAPL&alert_type=PRICE&threshold=150.00" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Create Signal Alert
```bash
curl -X POST "http://localhost:8000/alerts?symbol=MSFT&alert_type=SIGNAL&signal_type=BUY" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "symbol": "AAPL",
  "alert_type": "PRICE",
  "threshold": 150.00,
  "signal_type": null,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "triggered_at": null
}
```

#### Get All Alerts
```bash
curl -X GET "http://localhost:8000/alerts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Delete Alert
```bash
curl -X DELETE "http://localhost:8000/alerts/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 5: Portfolio Management

#### Get Portfolio
```bash
curl -X GET "http://localhost:8000/portfolio" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "total_value": 10000.00,
  "cash": 10000.00,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Add Position
```bash
curl -X POST "http://localhost:8000/portfolio/positions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "symbol=AAPL&quantity=100&entry_price=150.25&position_type=LONG"
```

**Expected Response:**
```json
{
  "id": 1,
  "portfolio_id": 1,
  "symbol": "AAPL",
  "quantity": 100,
  "entry_price": 150.25,
  "current_price": 150.25,
  "position_type": "LONG",
  "opened_at": "2024-01-15T10:30:00",
  "is_open": true
}
```

#### Get Positions
```bash
curl -X GET "http://localhost:8000/portfolio/positions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 6: Dashboard

#### Get Complete Dashboard Data
```bash
curl -X GET "http://localhost:8000/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "stats": {
    "total_scans": 15,
    "buy_signals": 8,
    "sell_signals": 3,
    "win_rate": 75.0,
    "portfolio_value": 12450.00,
    "portfolio_cash": 2450.00,
    "open_positions": 3
  },
  "recent_scans": [...],
  "watchlist": [...],
  "portfolio": {...},
  "alerts": [...]
}
```

---

## Testing Checklist

- [ ] User Registration
- [ ] User Login
- [ ] Get Current User
- [ ] Scan AAPL (1d)
- [ ] Scan MSFT (1h)
- [ ] Scan TSLA (1wk)
- [ ] Get Recent Scans
- [ ] Add to Watchlist
- [ ] Get Watchlist
- [ ] Remove from Watchlist
- [ ] Create Price Alert
- [ ] Create Signal Alert
- [ ] Get Alerts
- [ ] Delete Alert
- [ ] Get Portfolio
- [ ] Add Position
- [ ] Get Positions
- [ ] Get Dashboard

---

## Common Test Symbols

### Stocks
- AAPL (Apple)
- MSFT (Microsoft)
- TSLA (Tesla)
- GOOGL (Google)
- AMZN (Amazon)
- NVDA (NVIDIA)
- META (Meta)

### Crypto
- BTC-USD (Bitcoin)
- ETH-USD (Ethereum)
- ADA-USD (Cardano)

### ETFs
- SPY (S&P 500)
- QQQ (Nasdaq-100)
- IVV (iShares Core S&P 500)

---

## Error Handling

### 401 Unauthorized
```bash
# Missing or invalid token
curl -X GET "http://localhost:8000/scan/AAPL" \
  -H "Authorization: Bearer invalid_token"
```

### 404 Not Found
```bash
# Invalid symbol
curl -X GET "http://localhost:8000/scan/INVALIDTICKER" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 400 Bad Request
```bash
# Missing required fields
curl -X POST "http://localhost:8000/watchlist?symbol=" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Performance Testing

### Load Testing with Apache Bench
```bash
ab -n 100 -c 10 http://localhost:8000/
```

### Test Multiple Scans in Parallel
```bash
for i in {1..10}; do
  curl -X GET "http://localhost:8000/scan/AAPL" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" &
done
wait
```

---

## Postman Collection

Import this into Postman for easier API testing:

```json
{
  "info": {
    "name": "Elite AI Chart Scanner",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/register?username=trader&email=trader@example.com&password=pass"
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/login",
            "body": "username=trader&password=pass"
          }
        }
      ]
    },
    {
      "name": "Scanner",
      "item": [
        {
          "name": "Scan Symbol",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/scan/AAPL",
            "header": {
              "Authorization": "Bearer {{token}}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": ""
    }
  ]
}
```

---

## Notes

- Always include the JWT token in the `Authorization` header for protected endpoints
- Use the `Bearer` scheme for token authentication
- All timestamps are in ISO 8601 format
- Prices are returned as floats with 4 decimal places
- Confidence scores range from 0-100

---

**Happy Testing! 💎**
