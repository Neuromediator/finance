import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from database import Database
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLAlchemy Core to use SQLite database
db = Database("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    
    # Get user's cash balance
    user = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    if not user:
        return apology("user not found", 400)
    
    cash = user[0]["cash"]
    
    # Get all stocks owned by user with total shares
    # Use GROUP BY and SUM to aggregate shares per symbol
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
        session["user_id"]
    )
    
    portfolio = []
    grand_total = cash
    
    # For each stock, get current price and calculate total value
    for stock in stocks:
        symbol = stock["symbol"]
        shares = stock["total_shares"]
        
        # Look up current price
        quote_data = lookup(symbol)
        if quote_data is None:
            continue
        
        current_price = quote_data["price"]
        total_value = shares * current_price
        grand_total += total_value
        
        portfolio.append({
            "symbol": symbol,
            "name": quote_data["name"],
            "shares": shares,
            "price": current_price,
            "total": total_value
        })
    
    # Render template with portfolio data
    return render_template("index.html", portfolio=portfolio, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure shares was submitted
        if not request.form.get("shares"):
            return apology("must provide shares", 400)

        # Look up the stock symbol
        symbol = request.form.get("symbol").upper()
        quote_data = lookup(symbol)

        # Check if lookup was successful
        if quote_data is None:
            return apology("invalid symbol", 400)

        # Validate shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                return apology("must provide a positive integer", 400)
        except ValueError:
            return apology("must provide a positive integer", 400)

        # Get user's current cash
        user = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if not user:
            return apology("user not found", 400)

        cash = user[0]["cash"]
        price = quote_data["price"]
        total_cost = shares * price

        # Check if user can afford the purchase
        if cash < total_cost:
            return apology("can't afford", 400)

        # Insert transaction into database
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"],
            symbol,
            shares,
            price
        )

        # Update user's cash
        db.execute(
            "UPDATE users SET cash = cash - ? WHERE id = ?",
            total_cost,
            session["user_id"]
        )

        # Redirect to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    
    # Get all transactions for the user, ordered by timestamp (most recent first)
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )
    
    # Process transactions to determine type and format data
    history_data = []
    for transaction in transactions:
        shares = transaction["shares"]
        transaction_type = "BUY" if shares > 0 else "SELL"
        shares_abs = abs(shares)
        
        history_data.append({
            "type": transaction_type,
            "symbol": transaction["symbol"],
            "shares": shares_abs,
            "price": transaction["price"],
            "timestamp": transaction["timestamp"]
        })
    
    # Render template with transaction history
    return render_template("history.html", transactions=history_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Change password or delete account"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        action = request.form.get("action")
        
        # Handle account deletion
        if action == "delete_account":
            # Ensure password was submitted for confirmation
            if not request.form.get("delete_password"):
                return apology("must provide password to delete account", 400)
            
            # Get user's current password hash
            user = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
            if not user:
                return apology("user not found", 400)
            
            current_hash = user[0]["hash"]
            delete_password = request.form.get("delete_password")
            
            # Check if password is correct
            if not check_password_hash(current_hash, delete_password):
                return apology("password is incorrect", 400)
            
            # Delete all user's transactions
            db.execute("DELETE FROM transactions WHERE user_id = ?", session["user_id"])
            
            # Delete user account
            db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
            
            # Clear session
            session.clear()
            
            # Flash success message
            flash("Account deleted successfully!")
            
            # Redirect to registration page
            return redirect("/register")
        
        # Handle password change
        else:
            # Ensure current password was submitted
            if not request.form.get("current_password"):
                return apology("must provide current password", 400)
            
            # Ensure new password was submitted
            if not request.form.get("new_password"):
                return apology("must provide new password", 400)
            
            # Ensure confirmation was submitted
            if not request.form.get("confirmation"):
                return apology("must provide password confirmation", 400)
            
            # Get user's current password hash
            user = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
            if not user:
                return apology("user not found", 400)
            
            current_hash = user[0]["hash"]
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirmation = request.form.get("confirmation")
            
            # Check if current password is correct
            if not check_password_hash(current_hash, current_password):
                return apology("current password is incorrect", 400)
            
            # Ensure new password and confirmation match
            if new_password != confirmation:
                return apology("new passwords do not match", 400)
            
            # Update password in database
            new_hash = generate_password_hash(new_password)
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?",
                new_hash,
                session["user_id"]
            )
            
            # Flash success message
            flash("Password changed successfully!")
            
            # Redirect to home page
            return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("profile.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Look up the stock symbol
        quote_data = lookup(request.form.get("symbol"))

        # Check if lookup was successful
        if quote_data is None:
            return apology("invalid symbol", 400)

        # Render the quoted template with the quote data
        return render_template("quoted.html", 
                             name=quote_data["name"],
                             symbol=quote_data["symbol"],
                             price=quote_data["price"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Try to insert new user into database
        try:
            user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password"))
            )
        except ValueError:
            # Username already exists (UNIQUE INDEX constraint)
            return apology("username already exists", 400)

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must select symbol", 400)
        
        symbol = request.form.get("symbol").upper()
        
        # Ensure shares was submitted
        if not request.form.get("shares"):
            return apology("must provide shares", 400)
        
        # Validate shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                return apology("must provide a positive integer", 400)
        except ValueError:
            return apology("must provide a positive integer", 400)
        
        # Check if user owns this stock
        user_stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol HAVING SUM(shares) > 0",
            session["user_id"],
            symbol
        )
        
        if not user_stocks:
            return apology("you don't own this stock", 400)
        
        owned_shares = user_stocks[0]["total_shares"]
        
        # Check if user owns enough shares
        if shares > owned_shares:
            return apology("you don't own that many shares", 400)
        
        # Look up the stock symbol to get current price
        quote_data = lookup(symbol)
        if quote_data is None:
            return apology("invalid symbol", 400)
        
        price = quote_data["price"]
        total_value = shares * price
        
        # Insert transaction with negative shares (selling)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"],
            symbol,
            -shares,
            price
        )
        
        # Update user's cash (add money from sale)
        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?",
            total_value,
            session["user_id"]
        )
        
        # Redirect to home page
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get all stocks owned by user
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
            session["user_id"]
        )
        
        return render_template("sell.html", stocks=stocks)
