# Budget Buddy AI — SQL Database Schema Design

## 1. Database Overview

This schema is designed for:

* Expense tracking
* Budget management
* AI insights
* Goal tracking
* Recurring subscriptions
* Spending analytics
* User preferences
* Financial scoring

---

# 2. Main Database Tables

---

# USERS TABLE

Stores user account information.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    currency VARCHAR(10) DEFAULT 'INR',
    city VARCHAR(100),

    profile_image TEXT,

    theme_preference VARCHAR(20) DEFAULT 'dark',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# USER_SETTINGS TABLE

Stores budgeting and app preferences.

```sql
CREATE TABLE user_settings (
    setting_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,

    monthly_budget DECIMAL(12,2) DEFAULT 0,
    monthly_saving_goal DECIMAL(12,2) DEFAULT 0,

    ai_overspending_alerts BOOLEAN DEFAULT TRUE,

    notification_enabled BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# EXPENSE_CATEGORIES TABLE

Predefined categories.

```sql
CREATE TABLE expense_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    category_name VARCHAR(50) UNIQUE NOT NULL,

    category_color VARCHAR(20),

    icon_name VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# Default Categories

```sql
INSERT INTO expense_categories
(category_name, category_color, icon_name)
VALUES
('Food', '#5EF2D6', 'utensils'),
('Transport', '#5BA8FF', 'car'),
('Shopping', '#F59DB1', 'shopping-bag'),
('Bills', '#F7D154', 'receipt'),
('Entertainment', '#A78BFA', 'film'),
('Health', '#FCA5A5', 'heart'),
('Other', '#94A3B8', 'circle');
```

---

# EXPENSES TABLE

Stores all user expenses.

```sql
CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    category_id UUID REFERENCES expense_categories(category_id),

    amount DECIMAL(12,2) NOT NULL,

    note TEXT,

    expense_date DATE NOT NULL,

    is_recurring BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# RECURRING_EXPENSES TABLE

Stores subscriptions and fixed bills.

```sql
CREATE TABLE recurring_expenses (
    recurring_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    category_id UUID REFERENCES expense_categories(category_id),

    title VARCHAR(100) NOT NULL,

    amount DECIMAL(12,2) NOT NULL,

    billing_cycle VARCHAR(20) NOT NULL,
    -- monthly / yearly / weekly

    next_due_date DATE,

    auto_add BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# GOALS TABLE

Stores user financial goals.

```sql
CREATE TABLE goals (
    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    goal_name VARCHAR(100) NOT NULL,

    goal_type VARCHAR(50),
    -- savings / investment / emergency / vacation

    target_amount DECIMAL(12,2) NOT NULL,

    current_amount DECIMAL(12,2) DEFAULT 0,

    target_date DATE,

    status VARCHAR(20) DEFAULT 'active',
    -- active / completed / paused

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# GOAL_TRANSACTIONS TABLE

Tracks deposits into goals.

```sql
CREATE TABLE goal_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    goal_id UUID REFERENCES goals(goal_id) ON DELETE CASCADE,

    amount DECIMAL(12,2) NOT NULL,

    note TEXT,

    transaction_date DATE DEFAULT CURRENT_DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# AI_INSIGHTS TABLE

Stores generated AI recommendations.

```sql
CREATE TABLE ai_insights (
    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    insight_type VARCHAR(50),
    -- warning / suggestion / prediction / saving

    title VARCHAR(150),

    message TEXT NOT NULL,

    priority VARCHAR(20) DEFAULT 'medium',
    -- low / medium / high

    is_read BOOLEAN DEFAULT FALSE,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# MONTHLY_ANALYTICS TABLE

Precomputed analytics for performance.

```sql
CREATE TABLE monthly_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    month INTEGER NOT NULL,
    year INTEGER NOT NULL,

    total_spending DECIMAL(12,2) DEFAULT 0,

    total_savings DECIMAL(12,2) DEFAULT 0,

    largest_category_id UUID REFERENCES expense_categories(category_id),

    projected_month_end DECIMAL(12,2),

    money_score INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# CATEGORY_ANALYTICS TABLE

Stores category-level monthly analysis.

```sql
CREATE TABLE category_analytics (
    category_analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    analytics_id UUID REFERENCES monthly_analytics(analytics_id)
    ON DELETE CASCADE,

    category_id UUID REFERENCES expense_categories(category_id),

    total_amount DECIMAL(12,2) DEFAULT 0,

    percentage DECIMAL(5,2) DEFAULT 0
);
```

---

# MONEY_SCORE_HISTORY TABLE

Tracks money score trends.

```sql
CREATE TABLE money_score_history (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    score INTEGER NOT NULL,

    reason TEXT,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# NOTIFICATIONS TABLE

Stores app notifications.

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    title VARCHAR(150),

    message TEXT,

    notification_type VARCHAR(50),

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# AI_CHAT_HISTORY TABLE (OPTIONAL FUTURE)

For AI finance assistant/chatbot.

```sql
CREATE TABLE ai_chat_history (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    user_message TEXT,

    ai_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 3. Database Relationships

## Relationship Overview

```text
users
 ├── user_settings
 ├── expenses
 ├── recurring_expenses
 ├── goals
 ├── ai_insights
 ├── notifications
 ├── monthly_analytics
 └── money_score_history

goals
 └── goal_transactions

monthly_analytics
 └── category_analytics

expense_categories
 ├── expenses
 ├── recurring_expenses
 └── category_analytics
```

---

# 4. Recommended Indexes

## Expense Queries

```sql
CREATE INDEX idx_expenses_user
ON expenses(user_id);

CREATE INDEX idx_expenses_date
ON expenses(expense_date);

CREATE INDEX idx_expenses_category
ON expenses(category_id);
```

---

## Analytics Optimization

```sql
CREATE INDEX idx_monthly_analytics_user
ON monthly_analytics(user_id);

CREATE INDEX idx_category_analytics
ON category_analytics(category_id);
```

---

## Notifications

```sql
CREATE INDEX idx_notifications_user
ON notifications(user_id);
```

---

# 5. Suggested Backend Logic

---

# Monthly Budget Calculation

```sql
SELECT
    SUM(amount) AS total_spent
FROM expenses
WHERE user_id = 'USER_ID'
AND DATE_TRUNC('month', expense_date)
    = DATE_TRUNC('month', CURRENT_DATE);
```

---

# Category Breakdown

```sql
SELECT
    ec.category_name,
    SUM(e.amount) AS total
FROM expenses e
JOIN expense_categories ec
ON e.category_id = ec.category_id
WHERE e.user_id = 'USER_ID'
GROUP BY ec.category_name
ORDER BY total DESC;
```

---

# Money Score Logic (Example)

## Factors

* Staying under budget
* Saving consistency
* Reduced unnecessary spending
* Goal completion
* Subscription control

## Example Formula

```text
Base Score = 100

- Overspending penalty
- Subscription overload penalty
+ Savings bonus
+ Goal achievement bonus
```

---

# 6. Recommended Future Tables

---

# BANK_ACCOUNTS

```sql
bank_accounts
```

For:

* UPI sync
* Bank integration
* Auto transaction import

---

# TRANSACTION_IMPORTS

```sql
transaction_imports
```

For:

* SMS parsing
* CSV uploads
* Statement imports

---

# SAVINGS_CHALLENGES

```sql
savings_challenges
```

Gamification system.

---

# ACHIEVEMENTS

```sql
achievements
```

Badges and streaks.

---

# 7. Recommended Production Stack

| Layer          | Recommendation           |
| -------------- | ------------------------ |
| Database       | PostgreSQL               |
| ORM            | Prisma                   |
| Backend        | Node.js + Express        |
| Auth           | JWT                      |
| Hosting        | Supabase / Railway / AWS |
| Analytics Jobs | Cron Jobs                |
| AI Insights    | OpenAI API               |

---

# 8. Suggested Prisma Models (Optional)

If you're using Prisma, this schema converts very cleanly because:

* UUID support
* Relations
* Analytics querying
* Good TypeScript integration

---

# 9. Scalability Notes

This schema is designed to support:

* Thousands of users
* Large expense histories
* Real-time analytics
* AI-generated insights
* Future mobile app support

---


