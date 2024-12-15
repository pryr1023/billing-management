from datetime import datetime, timedelta
from calendar import monthrange
from backend.database import db, Bill, CreditCard
import random

def add_bill(bill_data):
    new_bill = Bill(
        name=bill_data['name'],
        amount=bill_data['amount'],
        due_date=datetime.strptime(bill_data['due_date'], '%Y-%m-%d'),
        recurring=bill_data['recurring']
    )
    db.session.add(new_bill)
    db.session.commit()

def get_all_bills(sort_by="due_date"):
    """Retrieve all bills sorted by a specific column."""
    if sort_by == "amount":
        return Bill.query.order_by(Bill.amount).all()
    else:
        return Bill.query.order_by(Bill.due_date).all()

def calculate_monthly_projections():
    """Calculate total payments (bills + credit card minimums) for the next 12 months."""
    today = datetime.today()
    projections = {}

    # Helper: Get the minimum payment for credit cards
    def get_min_payment(balance):
        return max(balance * 0.05, 50)  # 5% or $50 minimum payment

    # Generate projections for the next 12 months
    for i in range(12):
        # Calculate the month and year
        month_date = today + timedelta(days=monthrange(today.year, today.month)[1] * i)
        month_key = month_date.strftime('%B %Y')  # Format: "May 2024"

        # Initialize totals
        month_total = 0

        # Aggregate bill amounts for the month
        bills = Bill.query.filter_by(exclude_from_projections=False).all()  # Filter bills
        for bill in bills:
            if bill.recurring or bill.due_date.month == month_date.month:
                month_total += bill.amount

        # Add minimum credit card payments
        credit_cards = CreditCard.query.filter_by(exclude_from_projections=False).all()  # Filter credit cards
        for card in credit_cards:
            month_total += get_min_payment(card.balance)

        # Store the total in projections
        projections[month_key] = month_total

    return projections

def generate_test_bills(num_bills=5):
    """Generate dynamic test bills for testing purposes."""
    bill_names = ['Electricity', 'Water', 'Internet', 'Gym Membership', 'Groceries',
                  'Car Insurance', 'Streaming Service', 'Credit Card Payment', 'Rent', 'Phone Bill']
    current_date = datetime.now()

    test_bills = []
    for _ in range(num_bills):
        name = random.choice(bill_names)
        amount = round(random.uniform(20, 500), 2)  # Random amounts between 20 and 500
        days_offset = random.randint(1, 60)  # Due dates within the next 60 days
        due_date = (current_date + timedelta(days=days_offset)).date()
        recurring = random.choice([True, False])

        test_bills.append({
            'name': name,
            'amount': amount,
            'due_date': due_date,
            'recurring': recurring
        })

    # Add bills to the database
    for bill_data in test_bills:
        bill = Bill(
            name=bill_data['name'],
            amount=bill_data['amount'],
            due_date=bill_data['due_date'],
            recurring=bill_data['recurring']
        )
        db.session.add(bill)

    db.session.commit()
    print(f"Successfully generated {num_bills} test bills.")

