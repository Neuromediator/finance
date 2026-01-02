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

## Technologies

- **Backend**: Python, Flask
- **Database**: SQLite (via CS50 SQL)
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **API**: CS50 Finance API for stock quotes

## Installation

1. Make sure you have Python 3.x installed

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
flask run
```

## Project Structure

```
finance/
├── app.py              # Main Flask application
├── helpers.py          # Helper functions
├── requirements.txt    # Project dependencies
├── finance.db          # SQLite database
├── templates/          # HTML templates
│   ├── layout.html
│   ├── index.html
│   ├── buy.html
│   ├── sell.html
│   ├── quote.html
│   ├── history.html
│   └── ...
└── static/             # Static files (CSS, images)
```

## Features

### Registration and Login
- Secure password storage using hashing
- Session management for user state

### Buying Stocks
- Look up stocks by symbol
- Check sufficient funds
- Automatic balance update

### Selling Stocks
- Select stocks from portfolio via dropdown menu
- Verify sufficient shares ownership
- Automatic balance update

### Portfolio
- Display all user's stocks
- Current market prices
- Total portfolio value
- Current cash balance

### Transaction History
- Complete history of purchases and sales
- Date and time of each transaction
- Details of each operation

## Note

This project is created **solely for educational purposes** based on CS50 course assignment. It demonstrates the fundamentals of web development, database operations, form handling, and external API integration.

## License

Educational project - not intended for commercial use.

