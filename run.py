import os
from app import create_app, db
from app.models.expense import ExpenseCategory

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    from app.models.user import User
    from app.models.expense import Expense, ExpenseCategory
    from app.models.goal import Goal
    from app.models.settings import UserSettings
    from app.models.ai_insight import AIInsight
    from app.models.recurring import RecurringExpense
    return dict(db=db, User=User, Expense=Expense,
                ExpenseCategory=ExpenseCategory, Goal=Goal,
                UserSettings=UserSettings, AIInsight=AIInsight,
                RecurringExpense=RecurringExpense)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
