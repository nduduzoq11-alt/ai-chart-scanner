#!/usr/bin/env python3
"""
Elite AI Chart Scanner - Test Suite
Run automated tests to verify functionality
"""

import sys
import requests
import json
from colorama import Fore, Back, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8000"
TEST_RESULTS = {"passed": 0, "failed": 0}

def print_header(text):
    print(f"\n{Back.CYAN}{Fore.BLACK} {text} {Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    TEST_RESULTS["passed"] += 1

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    TEST_RESULTS["failed"] += 1

def print_info(text):
    print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

def test_api_availability():
    """Test if API is running"""
    print_header("Testing API Availability")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("API is running and responding")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print_info("Make sure to run: uvicorn app.main:app --reload")
        return False

def test_registration():
    """Test user registration"""
    print_header("Testing User Registration")
    
    test_user = {
        "username": f"test_user_{int(requests.get(BASE_URL).elapsed.total_seconds())}",
        "email": f"test{int(requests.get(BASE_URL).elapsed.total_seconds())}@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            params=test_user
        )
        
        if response.status_code == 200:
            print_success(f"Registration successful: {test_user['username']}")
            return test_user
        else:
            print_error(f"Registration failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None

def test_login(user_data):
    """Test user login"""
    print_header("Testing User Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print_success(f"Login successful")
            print_info(f"Token: {token[:50]}...")
            return token
        else:
            print_error(f"Login failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def test_scan(token):
    """Test chart scanning"""
    print_header("Testing Chart Scanning")
    
    symbols = ["AAPL", "MSFT", "TSLA"]
    
    for symbol in symbols:
        try:
            response = requests.get(
                f"{BASE_URL}/scan/{symbol}",
                params={"interval": "1d", "period": "1y"},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                signal = data.get("signal")
                confidence = data.get("confidence")
                print_success(f"{symbol}: {signal} ({confidence}% confidence)")
            else:
                print_error(f"Scan failed for {symbol}: {response.json()}")
        except Exception as e:
            print_error(f"Scan error for {symbol}: {str(e)}")

def test_watchlist(token):
    """Test watchlist operations"""
    print_header("Testing Watchlist Operations")
    
    # Add to watchlist
    try:
        response = requests.post(
            f"{BASE_URL}/watchlist?symbol=AAPL",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            print_success("Added AAPL to watchlist")
        else:
            print_error(f"Failed to add to watchlist: {response.json()}")
    except Exception as e:
        print_error(f"Watchlist add error: {str(e)}")
    
    # Get watchlist
    try:
        response = requests.get(
            f"{BASE_URL}/watchlist",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            items = response.json()
            print_success(f"Retrieved watchlist ({len(items)} items)")
        else:
            print_error(f"Failed to get watchlist: {response.json()}")
    except Exception as e:
        print_error(f"Watchlist get error: {str(e)}")

def test_alerts(token):
    """Test alert operations"""
    print_header("Testing Alert Operations")
    
    # Create price alert
    try:
        response = requests.post(
            f"{BASE_URL}/alerts?symbol=AAPL&alert_type=PRICE&threshold=150.00",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            print_success("Created price alert for AAPL")
        else:
            print_error(f"Failed to create alert: {response.json()}")
    except Exception as e:
        print_error(f"Alert creation error: {str(e)}")
    
    # Get alerts
    try:
        response = requests.get(
            f"{BASE_URL}/alerts",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            alerts = response.json()
            print_success(f"Retrieved alerts ({len(alerts)} items)")
        else:
            print_error(f"Failed to get alerts: {response.json()}")
    except Exception as e:
        print_error(f"Alerts get error: {str(e)}")

def test_portfolio(token):
    """Test portfolio operations"""
    print_header("Testing Portfolio Operations")
    
    # Get portfolio
    try:
        response = requests.get(
            f"{BASE_URL}/portfolio",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            portfolio = response.json()
            print_success(f"Portfolio Value: ${portfolio.get('total_value', 0)}")
            print_info(f"Available Cash: ${portfolio.get('cash', 0)}")
        else:
            print_error(f"Failed to get portfolio: {response.json()}")
    except Exception as e:
        print_error(f"Portfolio error: {str(e)}")

def test_dashboard(token):
    """Test dashboard endpoint"""
    print_header("Testing Dashboard")
    
    try:
        response = requests.get(
            f"{BASE_URL}/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            stats = data.get("stats", {})
            print_success("Dashboard loaded successfully")
            print_info(f"Total Scans: {stats.get('total_scans', 0)}")
            print_info(f"Buy Signals: {stats.get('buy_signals', 0)}")
            print_info(f"Sell Signals: {stats.get('sell_signals', 0)}")
            print_info(f"Portfolio Value: ${stats.get('portfolio_value', 0)}")
        else:
            print_error(f"Failed to load dashboard: {response.json()}")
    except Exception as e:
        print_error(f"Dashboard error: {str(e)}")

def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = TEST_RESULTS["passed"] + TEST_RESULTS["failed"]
    passed = TEST_RESULTS["passed"]
    failed = TEST_RESULTS["failed"]
    
    print(f"Total Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}{Back.BLACK}✓ All tests passed!{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"\n{Fore.RED}{Back.BLACK}✗ Some tests failed{Style.RESET_ALL}\n")
        return 1

def main():
    """Run all tests"""
    print(f"{Back.YELLOW}{Fore.BLACK} Elite AI Chart Scanner - Test Suite {Style.RESET_ALL}\n")
    
    # Test API availability
    if not test_api_availability():
        print_error("Cannot continue without API")
        return 1
    
    # Register and login
    user_data = test_registration()
    if not user_data:
        print_error("Cannot continue without user registration")
        return 1
    
    token = test_login(user_data)
    if not token:
        print_error("Cannot continue without authentication")
        return 1
    
    # Run feature tests
    test_scan(token)
    test_watchlist(token)
    test_alerts(token)
    test_portfolio(token)
    test_dashboard(token)
    
    # Print summary
    return print_summary()

if __name__ == "__main__":
    sys.exit(main())
