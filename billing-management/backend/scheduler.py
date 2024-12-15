from datetime import datetime
from backend.database import db, Bill

def add_bill(bill_data):
    new_bill = Bill(
        name=bill_data['name'],
        amount=bill_data['amount'],
        due_date=datetime.strptime(bill_data['due_date'], '%Y-%m-%d'),
        recurring=bill_data['recurring']
    )
    db.session.add(new_bill)
    db.session.commit()

def get_all_bills():
    return Bill.query.order_by(Bill.due_date).all()
