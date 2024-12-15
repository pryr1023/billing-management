from flask import Flask, render_template, request, redirect, url_for, flash
from backend.database import db, initialize_database
from backend.scheduler import add_bill, get_all_bills
from backend.debt_manager import get_debt_summary

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Initialize the database
db.init_app(app)

with app.app_context():
    initialize_database(app)

@app.route('/')
def home():
    bills = get_all_bills()
    debt_summary = get_debt_summary()
    return render_template('index.html', bills=bills, debt_summary=debt_summary)

@app.route('/bills', methods=['GET', 'POST'])
def manage_bills():
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
    bills = get_all_bills()
    return render_template('bills.html', bills=bills)

if __name__ == '__main__':
    app.run(debug=True)
