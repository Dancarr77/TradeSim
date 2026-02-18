from fastapi import FastAPI, Form, Cookie, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from database import Base, engine
import crud
import yfinance as yf
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

QUOTE_CACHE = {}
QUOTE_TTL = 5


def page(name):
    return FileResponse(f"frontend/{name}.html")


def require_user(token):
    user = crud.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=302,
            headers={"Location": "/login"}
        )
    return user


def to_yahoo_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if symbol.endswith("USD") and "-" not in symbol:
        return symbol[:-3] + "-USD"
    return symbol


def get_price(symbol: str) -> float:
    symbol = to_yahoo_symbol(symbol)
    now = time.time()

    if symbol in QUOTE_CACHE and now - QUOTE_CACHE[symbol][1] < QUOTE_TTL:
        return QUOTE_CACHE[symbol][0]

    t = yf.Ticker(symbol)

    try:
        price = float(t.fast_info["last_price"])
    except Exception:
        h = t.history(period="1d", interval="1m")
        if h.empty:
            raise HTTPException(status_code=404, detail="No price data")
        price = float(h["Close"].iloc[-1])

    QUOTE_CACHE[symbol] = (price, now)
    return price


@app.get("/")
def index():
    return page("index")


@app.get("/signup")
def signup_page():
    return page("signup")


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    if crud.get_user_by_username(username):
        raise HTTPException(status_code=400)
    crud.create_user(username, password)
    return RedirectResponse("/login", status_code=302)


@app.get("/login")
def login_page():
    return page("login")


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = crud.authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401)
    token = crud.create_session(username)
    r = RedirectResponse("/trading", status_code=302)
    r.set_cookie("session_token", token, httponly=True)
    return r


@app.post("/logout")
def logout(session_token: str | None = Cookie(default=None)):
    if session_token:
        crud.delete_session(session_token)
    r = RedirectResponse("/", status_code=302)
    r.delete_cookie("session_token")
    return r


@app.get("/trading")
def trading(session_token: str | None = Cookie(default=None)):
    require_user(session_token)
    return page("trading")


@app.get("/api/trades")
def trades(session_token: str | None = Cookie(default=None)):
    user = require_user(session_token)
    rows = []

    for t in crud.list_open_trades(user.username):
        price = get_price(t.ticker)
        value = t.shares * price
        pnl = value - t.money_investment

        rows.append({
            "id": t.id,
            "ticker": t.ticker,
            "invested": t.money_investment,
            "pnl": pnl
        })

    return {"items": rows}


@app.post("/api/trades/open")
def open_trade(
    ticker: str = Form(...),
    amount: float = Form(...),
    session_token: str | None = Cookie(default=None),
):
    user = require_user(session_token)
    price = get_price(ticker)
    crud.open_trade(user.username, ticker, amount, price)
    return {"ok": True}

@app.post("/api/trades/close")
def close_trade(
    trade_id: int = Form(...),
    session_token: str | None = Cookie(default=None),
):
    user = require_user(session_token)

    trade = crud.get_trade_by_id(trade_id)
    if not trade or trade.username != user.username:
        raise HTTPException(status_code=404)

    price = get_price(trade.ticker)
    crud.close_trade(user.username, trade_id, price)

    return {"ok": True}

