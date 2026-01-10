# Finance

A web application for managing a stock portfolio, created for educational purposes based on CS50 assignment.

## Description

This is an educational project implemented as part of the CS50 course. The application allows users to:

- **Register and log in** to the system
- **Buy stocks** at current market prices
- **Sell stocks** from their portfolio
- **Look up stock quotes** in real-time
- **Track their portfolio** with current prices and total value
- **View transaction history** of all trades
- **Manage account** - change password or delete account

## Technologies

- **Backend**: Python 3.x, Flask
- **Database**: SQLite with SQLAlchemy Core
- **Frontend**: HTML, CSS, Bootstrap 5.3, Jinja2
- **API**: CS50 Finance API for stock quotes
- **Security**: Werkzeug for password hashing, Flask-Session for session management

## Installation

1. Make sure you have Python 3.x installed

2. Clone the repository:
```bash
git clone <repository-url>
cd finance
```

3. Create a virtual environment:
```bash
python -m venv venv
```

4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Initialize the database (if not already created):
   - The database will be created automatically on first run
   - Or you can create it manually using SQLite

7. Run the application:
```bash
flask run
```

8. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
finance/
├── app.py              # Main Flask application
├── database.py         # Database wrapper using SQLAlchemy Core
├── helpers.py          # Helper functions (apology, login_required, lookup, usd)
├── requirements.txt    # Project dependencies
├── finance.db          # SQLite database
├── templates/          # HTML templates
│   ├── layout.html     # Base template
│   ├── index.html      # Portfolio page
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── buy.html        # Buy stocks page
│   ├── sell.html       # Sell stocks page
│   ├── quote.html      # Look up quotes form
│   ├── quoted.html     # Display quote result
│   ├── history.html    # Transaction history
│   ├── profile.html    # User profile management
│   └── apology.html    # Error page
└── static/             # Static files (CSS, images)
    ├── styles.css
    └── favicon.ico
```

## Features

### Registration and Login
- Secure password storage using Werkzeug password hashing
- Session management using Flask-Session
- Username uniqueness validation
- Password confirmation matching

### Buying Stocks
- Look up stocks by symbol using CS50 Finance API
- Real-time stock price retrieval
- Check sufficient funds before purchase
- Automatic balance update after purchase
- Transaction history recording

### Selling Stocks
- Select stocks from portfolio via dropdown menu
- Verify sufficient shares ownership
- Real-time price calculation
- Automatic balance update after sale
- Transaction history recording

### Portfolio
- Display all user's stocks with current holdings
- Real-time market prices for each stock
- Total portfolio value calculation
- Current cash balance display
- Grand total (cash + stocks value)

### Stock Quotes
- Look up any stock by symbol
- Display company name, symbol, and current price
- Formatted currency display

### Transaction History
- Complete history of all purchases and sales
- Date and time of each transaction
- Transaction type (BUY/SELL)
- Shares quantity and price per share
- Chronological ordering (most recent first)

### Account Management
- Change password with current password verification
- Delete account with password confirmation
- Automatic cleanup of user transactions

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `hash` - Hashed password
- `cash` - User's cash balance (default: $10,000.00)

### Transactions Table
- `id` - Primary key
- `user_id` - Foreign key to users table
- `symbol` - Stock symbol
- `shares` - Number of shares (positive for buy, negative for sell)
- `price` - Price per share at transaction time
- `timestamp` - Transaction date and time

## API Integration

The application uses the CS50 Finance API to retrieve real-time stock quotes:
- Endpoint: `https://finance.cs50.io/quote?symbol={SYMBOL}`
- Returns: Company name, current price, and symbol

## Technical Details

### Database Layer
- Uses SQLAlchemy Core for database operations
- Custom `Database` class provides compatibility with cs50.SQL API
- Automatic parameter binding and query execution
- Error handling for integrity constraints

### Security Features
- Password hashing using Werkzeug
- Session-based authentication
- SQL injection protection via parameterized queries
- CSRF protection through Flask forms

## Development Notes

- The project was originally built with `cs50.SQL` but has been migrated to SQLAlchemy Core for better compatibility.
- All database operations use parameterized queries for security
- The application follows Flask best practices and SOLID principles

## License

Educational project - not intended for commercial use.

## Acknowledgments

- Based on CS50 Finance assignment
- Uses CS50 Finance API for stock quotes
- Bootstrap for UI components