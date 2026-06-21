

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from models import Base, User, Watchlist
from services.stock_service import (
    get_stock_data,
    get_chart_data,
    ticker_exists
)

app = Flask(__name__)
app.secret_key = "secret-key"

engine = create_engine("sqlite:///stock_watchlist.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    return SessionLocal()


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    db = get_db()

    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        try:
            exists = db.query(User).filter(
                User.username == username
            ).first()

            if exists:
                flash("ログインIDは既に使用されています")
                return render_template("register.html")

            user = User(
                display_name=display_name,
                email=email,
                username=username,
                password_hash=generate_password_hash(password)
            )

            db.add(user)
            db.commit()

            return redirect(url_for("login"))

        finally:
            db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if not user:
                flash("ログインIDまたはパスワードが正しくありません")
                return render_template("login.html")

            if not check_password_hash(user.password_hash, password):
                flash("ログインIDまたはパスワードが正しくありません")
                return render_template("login.html")

            session["user_id"] = user.id

            return redirect(url_for("dashboard"))

        finally:
            db.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    try:
        watchlist = (
            db.query(Watchlist)
            .filter(Watchlist.user_id == user.id)
            .all()
        )

        items = []

        rising_count = 0
        falling_count = 0
        total_value = 0

        for item in watchlist:
            stock = get_stock_data(item.ticker)

            if stock["change"] > 0:
                rising_count += 1

            if stock["change"] < 0:
                falling_count += 1

            valuation = None

            if item.shares:
                valuation = stock["current_price"] * item.shares
                total_value += valuation

            items.append({
                "record": item,
                "stock": stock,
                "valuation": valuation
            })

        selected_ticker = request.args.get("ticker")

        if items:
            available_tickers = [
                item["record"].ticker
                for item in items
            ]

            if not selected_ticker or selected_ticker not in available_tickers:
                selected_ticker = items[0]["record"].ticker

        return render_template(
            "dashboard.html",
            user=user,
            items=items,
            selected_ticker=selected_ticker,
            registered_count=len(items),
            rising_count=rising_count,
            falling_count=falling_count,
            total_value=total_value
        )

    finally:
        db.close()

@app.route("/add_ticker", methods=["POST"])
def add_ticker():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    ticker = request.form.get("ticker", "").strip().upper()

    if not ticker_exists(ticker):
        flash("有効な銘柄コードではありません")
        return redirect(url_for("dashboard"))

    db = get_db()

    try:
        exists = (
            db.query(Watchlist)
            .filter(
                Watchlist.user_id == user.id,
                Watchlist.ticker == ticker
            )
            .first()
        )

        if exists:
            flash("この銘柄は登録済みです")
            return redirect(url_for("dashboard"))

        item = Watchlist(
            user_id=user.id,
            ticker=ticker
        )

        db.add(item)
        db.commit()

        return redirect(url_for("dashboard"))

    finally:
        db.close()


@app.route("/delete_ticker/<int:item_id>", methods=["POST"])
def delete_ticker(item_id):
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    try:
        item = (
            db.query(Watchlist)
            .filter(
                Watchlist.id == item_id,
                Watchlist.user_id == user.id
            )
            .first()
        )

        if item:
            db.delete(item)
            db.commit()

        return redirect(url_for("dashboard"))

    finally:
        db.close()


@app.route("/update_shares/<int:item_id>", methods=["POST"])
def update_shares(item_id):
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    shares = request.form.get("shares", "").strip()

    db = get_db()

    try:
        item = (
            db.query(Watchlist)
            .filter(
                Watchlist.id == item_id,
                Watchlist.user_id == user.id
            )
            .first()
        )

        if item:
            item.shares = int(shares) if shares else None
            db.commit()

        return redirect(url_for("dashboard"))

    finally:
        db.close()


@app.route("/update_purchase_price/<int:item_id>", methods=["POST"])
def update_purchase_price(item_id):
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    purchase_price = request.form.get(
        "purchase_price",
        ""
    ).strip()

    db = get_db()

    try:
        item = (
            db.query(Watchlist)
            .filter(
                Watchlist.id == item_id,
                Watchlist.user_id == user.id
            )
            .first()
        )

        if item:
            item.purchase_price = (
                float(purchase_price)
                if purchase_price
                else None
            )

            db.commit()

        return redirect(url_for("dashboard"))

    finally:
        db.close()


@app.route("/stock/<ticker>")
def stock_detail(ticker):
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    try:
        item = (
            db.query(Watchlist)
            .filter(
                Watchlist.user_id == user.id,
                Watchlist.ticker == ticker
            )
            .first()
        )

        if not item:
            return redirect(url_for("dashboard"))

        stock = get_stock_data(ticker)

        return render_template(
            "mobile_detail.html",
            item=item,
            stock=stock
        )

    finally:
        db.close()


@app.route("/chart/<ticker>/<period>")
def chart_data(ticker, period):
    return jsonify(
        get_chart_data(ticker, period)
    )


if __name__ == "__main__":
    app.run(debug=True)       