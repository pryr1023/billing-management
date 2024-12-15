from backend.database import db, Debt

def add_debt(debt_data):
    new_debt = Debt(
        name=debt_data['name'],
        balance=debt_data['balance'],
        interest_rate=debt_data['interest_rate']
    )
    db.session.add(new_debt)
    db.session.commit()

def get_debt_summary():
    debts = Debt.query.all()
    total_balance = sum(debt.balance for debt in debts)
    total_interest = sum(debt.balance * debt.interest_rate / 100 for debt in debts)
    return {'total_balance': total_balance, 'total_interest': total_interest}
