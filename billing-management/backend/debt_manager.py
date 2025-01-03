from backend.database import db, Debt, CreditCard

def add_debt(debt_data):
    new_debt = Debt(
        name=debt_data['name'],
        balance=debt_data['balance'],
        interest_rate=debt_data['interest_rate']
    )
    db.session.add(new_debt)
    db.session.commit()

def get_debt_summary():
    """Calculate total debt and interest, including credit card balances."""
    debts = Debt.query.all()
    credit_cards = CreditCard.query.all()

    total_balance = sum(debt.balance for debt in debts) + sum(card.balance for card in credit_cards)
    total_interest = sum(debt.balance * debt.interest_rate / 100 for debt in debts) + \
                     sum(card.balance * card.interest_rate / 100 for card in credit_cards)

    return {
        'total_balance': total_balance,
        'total_interest': total_interest,
        'credit_cards': credit_cards
    }

from backend.database import db, CreditCard

def add_credit_card(card_data):
    """Add a new credit card to the database."""
    new_card = CreditCard(
        name=card_data['name'],
        balance=card_data['balance'],
        interest_rate=card_data['interest_rate'],
        due_date=card_data.get('due_date')
    )
    db.session.add(new_card)
    db.session.commit()

def update_credit_card(card_id, card_data):
    """Update an existing credit card in the database."""
    card = CreditCard.query.get_or_404(card_id)
    card.name = card_data.get('name', card.name)
    card.balance = card_data.get('balance', card.balance)
    card.interest_rate = card_data.get('interest_rate', card.interest_rate)
    card.due_date = card_data.get('due_date', card.due_date)
    db.session.commit()
