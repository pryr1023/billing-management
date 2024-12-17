from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from backend.database import CreditCard, db, initialize_database
from backend.scheduler import add_bill, get_all_bills, generate_test_bills
from backend.debt_manager import get_debt_summary, add_credit_card
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Initialize the database
db.init_app(app)

# Setup Flask-Migrate
migrate = Migrate(app, db)

# Testing Mode Flag
app.config['TESTING_MODE'] = False

with app.app_context():
    initialize_database(app)

@app.route('/')
def home():
    bills = get_all_bills()
    debt_summary = get_debt_summary()
    testing_mode = app.config['TESTING_MODE']
    return render_template(
        'index.html',
        bills=bills,
        debt_summary=debt_summary,
        testing_mode=testing_mode
    )

@app.route('/bills', methods=['GET', 'POST'])
def manage_bills():
    from backend.database import Bill
    
    if request.method == 'POST':
        bill_data = {
            'name': request.form['name'],
            'amount': float(request.form['amount']),
            'due_date': request.form['due_date'],
            'recurring': 'recurring' in request.form
        }
        add_bill(bill_data)
        flash('Bill added successfully!', 'success')
        return redirect(url_for('manage_bills'))

    # Handle search and filter query parameters
    search_query = request.args.get('search', '').lower()
    recurring_filter = request.args.get('recurring')
    sort_by = request.args.get('sort_by', 'due_date')

    query = Bill.query
    if search_query:
        query = query.filter(Bill.name.ilike(f'%{search_query}%'))
    if recurring_filter == 'yes':
        query = query.filter(Bill.recurring == True)
    elif recurring_filter == 'no':
        query = query.filter(Bill.recurring == False)
    if sort_by == 'amount':
        query = query.order_by(Bill.amount)
    else:
        query = query.order_by(Bill.due_date)

    bills = query.all()
    return render_template('bills.html', bills=bills, sort_by=sort_by)

@app.route('/credit-cards', methods=['GET', 'POST'])
def manage_credit_cards():
    from backend.database import CreditCard

    if request.method == 'POST':
        card_data = {
            'name': request.form['name'],
            'balance': float(request.form['balance']),
            'interest_rate': float(request.form['interest_rate']),
            'due_date': request.form['due_date']
        }
        add_credit_card(card_data)
        flash('Credit card added successfully!', 'success')
        return redirect(url_for('manage_credit_cards'))

    # Handle search and filter query parameters
    search_query = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'balance')

    query = CreditCard.query
    if search_query:
        query = query.filter(CreditCard.name.ilike(f'%{search_query}%'))
    if sort_by == 'interest_rate':
        query = query.order_by(CreditCard.interest_rate)
    else:
        query = query.order_by(CreditCard.balance)

    credit_cards = query.all()
    return render_template('credit_cards.html', credit_cards=credit_cards, sort_by=sort_by)

@app.route('/add-credit-card', methods=['POST'])
def add_new_credit_card():  # Renamed to avoid conflict with debt_manager function
    """Route to add a new credit card"""
    from backend.debt_manager import add_credit_card  # Explicit import to avoid shadowing
    card_data = {
        'name': request.form['name'],
        'balance': float(request.form['balance']),
        'interest_rate': float(request.form['interest_rate']),
        'due_date': datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()  # Convert to date
    }
    add_credit_card(card_data)
    flash(f'Credit Card "{card_data["name"]}" added successfully!', 'success')
    return redirect(url_for('manage_credit_cards'))

@app.route('/edit-credit-card/<int:card_id>', methods=['GET', 'POST'])
def edit_credit_card(card_id):
    """Route to edit an existing credit card."""
    from backend.debt_manager import update_credit_card  # Import the new shared function
    if request.method == 'POST':
        card_data = {
            'name': request.form['name'],
            'balance': float(request.form['balance']),
            'interest_rate': float(request.form['interest_rate']),
            'due_date': datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()  # Convert to date
        }
        update_credit_card(card_id, card_data)
        flash(f'Credit Card "{card_data["name"]}" updated successfully!', 'success')
        return redirect(url_for('manage_credit_cards'))
    
    card = CreditCard.query.get_or_404(card_id)
    return render_template('edit_credit_card.html', card=card)

@app.route('/delete-bill/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    from backend.database import Bill
    bill = Bill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    flash(f'Bill "{bill.name}" has been deleted successfully!', 'success')
    return redirect(url_for('manage_bills'))

@app.route('/delete-credit-card/<int:card_id>', methods=['POST'])
def delete_credit_card(card_id):
    from backend.database import CreditCard
    card = CreditCard.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    flash(f'Credit Card "{card.name}" has been deleted successfully!', 'success')
    return redirect(url_for('manage_credit_cards'))

@app.route('/edit-bill/<int:bill_id>', methods=['GET', 'POST'])
def edit_bill(bill_id):
    from backend.database import Bill
    from datetime import datetime
    bill = Bill.query.get_or_404(bill_id)
    
    if request.method == 'POST':
        bill.name = request.form['name']
        bill.amount = float(request.form['amount'])
        bill.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        bill.recurring = 'recurring' in request.form
        db.session.commit()
        flash(f'Bill "{bill.name}" updated successfully!', 'success')
        return redirect(url_for('manage_bills'))
    
    return render_template('edit_bill.html', bill=bill)

@app.route('/toggle-bill-exclusion/<int:bill_id>', methods=['POST'])
def toggle_bill_exclusion(bill_id):
    from backend.database import Bill
    bill = Bill.query.get_or_404(bill_id)
    bill.exclude_from_projections = not bill.exclude_from_projections
    db.session.commit()
    flash(f'Bill "{bill.name}" updated successfully!', 'success')
    return redirect(url_for('manage_bills'))

@app.route('/toggle-credit-card-exclusion/<int:card_id>', methods=['POST'])
def toggle_credit_card_exclusion(card_id):
    from backend.database import CreditCard
    card = CreditCard.query.get_or_404(card_id)
    card.exclude_from_projections = not card.exclude_from_projections
    db.session.commit()
    flash(f'Credit Card "{card.name}" updated successfully!', 'success')
    return redirect(url_for('manage_credit_cards'))

@app.route('/api/payment-projections')
def payment_projections():
    from backend.database import Bill
    from datetime import datetime
    from collections import defaultdict

    # Aggregate payments by month
    monthly_totals = defaultdict(float)
    bills = Bill.query.all()

    for bill in bills:
        if bill.due_date:
            month = bill.due_date.strftime('%Y-%m')
            monthly_totals[month] += bill.amount

    # Sort the data by month
    sorted_data = sorted(monthly_totals.items())
    labels = [month for month, total in sorted_data]
    data = [total for month, total in sorted_data]

    return jsonify({"labels": labels, "data": data})

@app.route('/toggle-testing-mode')
def toggle_testing_mode():
    app.config['TESTING_MODE'] = not app.config['TESTING_MODE']
    flash(f"Testing mode {'enabled' if app.config['TESTING_MODE'] else 'disabled'}!", 'info')
    return redirect(url_for('home'))

@app.route('/generate-test-data')
def generate_test_data():
    generate_test_bills()
    flash('Test data generated successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
