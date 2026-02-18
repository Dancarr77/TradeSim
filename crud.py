from database import session
import models
import uuid
from datetime import datetime

def get_user_by_username(username):
    return session.query(models.User).filter_by(username=username).first()

def create_user(username, password):
    user = models.User(username=username, password=password)
    session.add(user)
    session.commit()
    return user

def authenticate(username, password):
    return session.query(models.User).filter_by(
        username=username, password=password
    ).first()

def create_session(username):
    token = str(uuid.uuid4())
    session.add(models.Session(token=token, username=username))
    session.commit()
    return token

def get_user_from_token(token):
    if not token:
        return None
    sess = session.query(models.Session).filter_by(token=token).first()
    if not sess:
        return None
    return get_user_by_username(sess.username)

def delete_session(token):
    session.query(models.Session).filter_by(token=token).delete()
    session.commit()

def open_trade(username, ticker, amount, price):
    shares = amount / price
    trade = models.Trade(
        username=username,
        ticker=ticker,
        money_investment=amount,
        init_price=price,
        shares=shares,
        is_open=True,
    )
    session.add(trade)
    session.commit()
    return trade

def list_open_trades(username):
    return session.query(models.Trade).filter_by(
        username=username, is_open=True
    ).all()

def close_trade(username, trade_id, price):
    trade = session.query(models.Trade).filter_by(
        id=trade_id, username=username, is_open=True
    ).first()
    if not trade:
        return None
    trade.is_open = False
    trade.close_price = price
    trade.closed_at = datetime.utcnow()
    session.commit()
    return trade
