from fastapi import FastAPI, Depends, HTTPException, Query, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

from app.database import Base, engine, get_db
from app.models import User, Scan, WatchlistItem, Alert, Portfolio, Position
from app.auth import hash_password, authenticate_user, create_access_token, get_current_user
from app.scanner import analyze_chart

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Elite AI Chart Scanner",
    version="1.0.0",
    description="AI-powered chart scanner for identifying trading buy and sell setups with user authentication.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "is_active": user.is_active,
    }


def serialize_scan(scan: Scan):
    return {
        "id": scan.id,
        "user_id": scan.user_id,
        "symbol": scan.symbol,
        "interval": scan.interval,
        "signal": scan.signal,
        "confidence": scan.confidence,
        "price": scan.price,
        "ema20": scan.ema20,
        "ema50": scan.ema50,
        "ema200": scan.ema200,
        "rsi14": scan.rsi14,
        "macd": scan.macd,
        "macd_signal": scan.macd_signal,
        "support": scan.support,
        "resistance": scan.resistance,
        "trend": scan.trend,
        "reason": scan.reason,
        "volume_ratio": scan.volume_ratio,
        "created_at": scan.created_at,
    }


def serialize_watchlist_item(item: WatchlistItem):
    return {
        "id": item.id,
        "user_id": item.user_id,
        "symbol": item.symbol,
        "added_at": item.added_at,
        "is_alert_enabled": item.is_alert_enabled,
    }


def serialize_alert(alert: Alert):
    return {
        "id": alert.id,
        "user_id": alert.user_id,
        "watchlist_id": alert.watchlist_id,
        "symbol": alert.symbol,
        "alert_type": alert.alert_type,
        "threshold": alert.threshold,
        "signal_type": alert.signal_type,
        "is_active": alert.is_active,
        "created_at": alert.created_at,
        "triggered_at": alert.triggered_at,
    }


def serialize_position(position: Position):
    return {
        "id": position.id,
        "portfolio_id": position.portfolio_id,
        "symbol": position.symbol,
        "quantity": position.quantity,
        "entry_price": position.entry_price,
        "current_price": position.current_price,
        "position_type": position.position_type,
        "opened_at": position.opened_at,
        "is_open": position.is_open,
    }


def serialize_portfolio(portfolio: Portfolio):
    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "total_value": portfolio.total_value,
        "cash": portfolio.cash,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at,
    }


@app.get("/")
def root():
    return {"message": "Elite AI Chart Scanner API", "status": "running"}


@app.post("/auth/register")
def register_user(
    username: str = Query(...),
    email: str = Query(...),
    password: str = Query(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    email = email.strip()

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email and password are required")

    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}


@app.post("/auth/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@app.get("/auth/me")
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@app.get("/scan/{symbol}")
def scan_symbol(
    symbol: str,
    interval: str = Query("1d"),
    period: str = Query("1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticker = symbol.upper().strip()
    analysis = analyze_chart(ticker, interval=interval, period=period)

    if analysis.get("signal") == "ERROR":
        raise HTTPException(status_code=400, detail=analysis.get("reason", "Unable to analyze symbol"))

    if analysis.get("signal") == "NO_DATA":
        raise HTTPException(status_code=404, detail=analysis.get("reason", f"No data found for {ticker}"))

    scan = Scan(
        user_id=current_user.id,
        symbol=ticker,
        interval=interval,
        signal=analysis.get("signal", "WAIT"),
        confidence=analysis.get("confidence", 0),
        price=analysis.get("price"),
        ema20=analysis.get("ema20"),
        ema50=analysis.get("ema50"),
        ema200=analysis.get("ema200"),
        rsi14=analysis.get("rsi14"),
        macd=analysis.get("macd"),
        macd_signal=analysis.get("macd_signal"),
        support=analysis.get("support"),
        resistance=analysis.get("resistance"),
        trend=analysis.get("trend"),
        reason=analysis.get("reason"),
        volume_ratio=analysis.get("volume_ratio"),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    response = serialize_scan(scan)
    response.update({
        "signal": analysis.get("signal", "WAIT"),
        "confidence": analysis.get("confidence", 0),
        "reason": analysis.get("reason"),
        "price": analysis.get("price"),
        "ema20": analysis.get("ema20"),
        "ema50": analysis.get("ema50"),
        "ema200": analysis.get("ema200"),
        "rsi14": analysis.get("rsi14"),
        "support": analysis.get("support"),
        "resistance": analysis.get("resistance"),
        "trend": analysis.get("trend"),
        "volume_ratio": analysis.get("volume_ratio"),
    })
    return response


@app.get("/recent-scans")
def get_recent_scans(
    limit: int = Query(5, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scans = db.query(Scan).filter(Scan.user_id == current_user.id).order_by(Scan.created_at.desc()).limit(limit).all()
    return [serialize_scan(scan) for scan in scans]


@app.get("/scan-history/{symbol}")
def get_scan_history(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticker = symbol.upper().strip()
    scans = db.query(Scan).filter(Scan.user_id == current_user.id, Scan.symbol == ticker).order_by(Scan.created_at.desc()).all()
    if not scans:
        return {"symbol": ticker, "latest_scan": None, "scan_count": 0, "last_scan_date": None}

    latest = scans[0]
    return {
        "symbol": ticker,
        "latest_scan": serialize_scan(latest),
        "scan_count": len(scans),
        "last_scan_date": latest.created_at,
    }


@app.post("/watchlist")
def add_watchlist_item(
    symbol: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticker = symbol.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="Symbol is required")

    existing = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id, WatchlistItem.symbol == ticker).first()
    if existing:
        return serialize_watchlist_item(existing)

    item = WatchlistItem(user_id=current_user.id, symbol=ticker)
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_watchlist_item(item)


@app.get("/watchlist")
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).order_by(WatchlistItem.added_at.desc()).all()
    return [serialize_watchlist_item(item) for item in items]


@app.delete("/watchlist/{item_id}")
def delete_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id, WatchlistItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    db.delete(item)
    db.commit()
    return {"message": "Watchlist item removed", "id": item_id}


@app.post("/alerts")
def create_alert(
    symbol: str = Query(...),
    alert_type: str = Query(...),
    threshold: Optional[float] = Query(None),
    signal_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticker = symbol.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="Symbol is required")

    alert = Alert(
        user_id=current_user.id,
        symbol=ticker,
        alert_type=alert_type.upper(),
        threshold=threshold,
        signal_type=signal_type.upper() if signal_type else None,
        is_active=True,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return serialize_alert(alert)


@app.get("/alerts")
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).order_by(Alert.created_at.desc()).all()
    return [serialize_alert(alert) for alert in alerts]


@app.delete("/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"message": "Alert removed", "id": alert_id}


@app.get("/portfolio")
def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, total_value=0, cash=10000)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    return serialize_portfolio(portfolio)


@app.post("/portfolio/positions")
def create_position(
    symbol: str = Query(...),
    quantity: float = Query(...),
    entry_price: float = Query(...),
    position_type: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, total_value=0, cash=10000)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    position = Position(
        portfolio_id=portfolio.id,
        symbol=symbol.upper().strip(),
        quantity=quantity,
        entry_price=entry_price,
        current_price=entry_price,
        position_type=position_type.upper(),
        is_open=True,
    )
    db.add(position)
    db.commit()
    db.refresh(position)

    portfolio.total_value = (portfolio.cash or 0) + sum(p.current_price * p.quantity for p in portfolio.positions if p.is_open)
    db.commit()
    return serialize_position(position)


@app.get("/portfolio/positions")
def get_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        return []
    positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).order_by(Position.opened_at.desc()).all()
    return [serialize_position(p) for p in positions]


@app.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scans = db.query(Scan).filter(Scan.user_id == current_user.id).all()
    watchlist = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, total_value=0, cash=10000)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    buy_signals = sum(1 for scan in scans if (scan.signal or "").upper() == "BUY")
    sell_signals = sum(1 for scan in scans if (scan.signal or "").upper() == "SELL")
    total_scans = len(scans)
    portfolio_value = portfolio.total_value or 0
    open_positions = db.query(Position).filter(Position.portfolio_id == portfolio.id, Position.is_open.is_(True)).count()

    stats = {
        "total_scans": total_scans,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "win_rate": round((buy_signals / total_scans) * 100, 2) if total_scans else 0,
        "portfolio_value": portfolio_value,
        "portfolio_cash": portfolio.cash,
        "open_positions": open_positions,
    }

    return {
        "stats": stats,
        "recent_scans": [serialize_scan(scan) for scan in sorted(scans, key=lambda x: x.created_at, reverse=True)[:10]],
        "watchlist": [serialize_watchlist_item(item) for item in sorted(watchlist, key=lambda x: x.added_at, reverse=True)],
        "alerts": [serialize_alert(alert) for alert in sorted(alerts, key=lambda x: x.created_at, reverse=True)],
        "portfolio": serialize_portfolio(portfolio),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
