"""
MAC Assistant - Financial Advisor Agent Module
Advanced financial analysis, investment tracking, and personal finance management.
"""

import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass
import re

@dataclass
class FinancialAccount:
    """Financial account data structure."""
    account_id: str
    account_name: str
    account_type: str  # checking, savings, investment, credit
    balance: float
    currency: str
    institution: str
    last_updated: datetime

@dataclass
class Transaction:
    """Transaction data structure."""
    transaction_id: str
    account_id: str
    amount: float
    description: str
    category: str
    date: datetime
    transaction_type: str  # debit, credit
    tags: List[str]

@dataclass
class Investment:
    """Investment holding data structure."""
    symbol: str
    quantity: float
    purchase_price: float
    current_price: float
    investment_type: str  # stock, bond, crypto, fund
    purchase_date: datetime

@dataclass
class FinancialGoal:
    """Financial goal tracking."""
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: datetime
    priority: str  # high, medium, low
    strategy: str

class FinancialAdvisorAgent:
    """Advanced financial advisor and wealth management system."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize financial advisor agent."""
        self.data_dir = Path(data_dir)
        self.finance_dir = self.data_dir / "finance"
        self.finance_dir.mkdir(parents=True, exist_ok=True)
        
        # Database and storage
        self.finance_db = self.finance_dir / "financial_data.db"
        self.market_cache = self.finance_dir / "market_cache.json"
        self.reports_dir = self.finance_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self._init_finance_db()
        self.portfolio_manager = PortfolioManager(self.finance_dir)
        self.expense_tracker = ExpenseTracker(self.finance_dir)
        self.investment_analyzer = InvestmentAnalyzer(self.finance_dir)
        self.budget_planner = BudgetPlanner(self.finance_dir)
        self.market_data = MarketDataProvider()
        self.financial_insights = FinancialInsights()
        
        # Financial categories
        self.expense_categories = {
            'housing': ['rent', 'mortgage', 'utilities', 'property tax', 'home insurance'],
            'transportation': ['gas', 'car payment', 'insurance', 'maintenance', 'public transport'],
            'food': ['groceries', 'restaurant', 'dining', 'takeout', 'coffee'],
            'entertainment': ['movies', 'streaming', 'games', 'concerts', 'hobbies'],
            'healthcare': ['medical', 'dental', 'vision', 'pharmacy', 'insurance'],
            'education': ['tuition', 'books', 'courses', 'training', 'certifications'],
            'shopping': ['clothing', 'electronics', 'household', 'personal care'],
            'travel': ['flights', 'hotels', 'vacation', 'business travel'],
            'savings': ['emergency fund', 'retirement', 'investments', 'goals'],
            'debt': ['credit card', 'loan payment', 'student loan', 'personal loan'],
            'other': ['gifts', 'donations', 'subscriptions', 'miscellaneous']
        }
        
        # Investment types and risk levels
        self.investment_types = {
            'conservative': ['bonds', 'cds', 'money_market', 'treasury'],
            'moderate': ['index_funds', 'mutual_funds', 'dividend_stocks', 'reits'],
            'aggressive': ['growth_stocks', 'tech_stocks', 'crypto', 'options'],
            'speculative': ['penny_stocks', 'futures', 'forex', 'commodities']
        }
    
    def _init_finance_db(self):
        """Initialize financial database."""
        conn = sqlite3.connect(self.finance_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                account_name TEXT,
                account_type TEXT,
                balance REAL,
                currency TEXT,
                institution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                account_id TEXT,
                amount REAL,
                description TEXT,
                category TEXT,
                transaction_date TIMESTAMP,
                transaction_type TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (account_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                investment_id TEXT PRIMARY KEY,
                symbol TEXT,
                quantity REAL,
                purchase_price REAL,
                current_price REAL,
                investment_type TEXT,
                purchase_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_goals (
                goal_id TEXT PRIMARY KEY,
                name TEXT,
                target_amount REAL,
                current_amount REAL,
                target_date TIMESTAMP,
                priority TEXT,
                strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                budget_id TEXT PRIMARY KEY,
                category TEXT,
                monthly_limit REAL,
                current_spent REAL,
                period_start TIMESTAMP,
                period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_financial_health(self) -> Dict[str, Any]:
        """Comprehensive financial health analysis."""
        try:
            # Get all financial data
            accounts = self._get_all_accounts()
            transactions = self._get_recent_transactions(30)  # Last 30 days
            investments = self._get_all_investments()
            goals = self._get_all_goals()
            
            # Calculate key metrics
            total_assets = sum(acc.balance for acc in accounts if acc.account_type in ['checking', 'savings', 'investment'])
            total_debts = sum(abs(acc.balance) for acc in accounts if acc.account_type == 'credit' and acc.balance < 0)
            net_worth = total_assets - total_debts
            
            # Monthly cash flow analysis
            monthly_income = sum(t.amount for t in transactions if t.transaction_type == 'credit' and t.amount > 0)
            monthly_expenses = sum(abs(t.amount) for t in transactions if t.transaction_type == 'debit')
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
            
            # Investment performance
            total_investment_value = sum(inv.quantity * inv.current_price for inv in investments)
            total_investment_cost = sum(inv.quantity * inv.purchase_price for inv in investments)
            investment_gain_loss = total_investment_value - total_investment_cost
            investment_return = (investment_gain_loss / total_investment_cost * 100) if total_investment_cost > 0 else 0
            
            # Financial health score (0-100)
            health_score = self._calculate_health_score(
                savings_rate, net_worth, total_debts, total_assets, investment_return
            )
            
            # Generate insights and recommendations
            insights = self._generate_financial_insights({
                'net_worth': net_worth,
                'savings_rate': savings_rate,
                'debt_to_asset_ratio': (total_debts / total_assets * 100) if total_assets > 0 else 0,
                'investment_return': investment_return,
                'monthly_savings': monthly_savings
            })
            
            return {
                'success': True,
                'message': f"💰 Financial Health Analysis Complete\n\n"
                          f"🏆 Health Score: {health_score:.1f}/100\n"
                          f"💎 Net Worth: ${net_worth:,.2f}\n"
                          f"💵 Monthly Income: ${monthly_income:,.2f}\n"
                          f"💸 Monthly Expenses: ${monthly_expenses:,.2f}\n"
                          f"🏦 Savings Rate: {savings_rate:.1f}%\n"
                          f"📈 Investment Return: {investment_return:+.1f}%\n\n"
                          f"🎯 Top Recommendations:\n" + "\n".join(f"• {insight}" for insight in insights[:3]),
                'data': {
                    'health_score': health_score,
                    'net_worth': net_worth,
                    'total_assets': total_assets,
                    'total_debts': total_debts,
                    'monthly_income': monthly_income,
                    'monthly_expenses': monthly_expenses,
                    'monthly_savings': monthly_savings,
                    'savings_rate': savings_rate,
                    'investment_value': total_investment_value,
                    'investment_return': investment_return,
                    'insights': insights,
                    'goal_progress': [{'name': g.name, 'progress': (g.current_amount/g.target_amount*100)} for g in goals]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Financial analysis error: {str(e)}"
            }
    
    def track_expense(self, amount: float, description: str, category: str = None) -> Dict[str, Any]:
        """Track a new expense with automatic categorization."""
        try:
            # Auto-categorize if not provided
            if not category:
                category = self._auto_categorize_expense(description)
            
            # Create transaction
            transaction_id = f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(description) % 1000}"
            
            transaction = Transaction(
                transaction_id=transaction_id,
                account_id="primary_checking",  # Default account
                amount=-abs(amount),  # Expenses are negative
                description=description,
                category=category,
                date=datetime.now(),
                transaction_type="debit",
                tags=[]
            )
            
            # Save to database
            self._save_transaction(transaction)
            
            # Check budget impact
            budget_status = self._check_budget_impact(category, abs(amount))
            
            # Generate expense insights
            insights = self._analyze_expense_pattern(category, abs(amount))
            
            message = f"💸 Expense Tracked: ${amount:.2f}\n"
            message += f"📝 Description: {description}\n"
            message += f"🏷️ Category: {category.title()}\n"
            
            if budget_status:
                message += f"📊 Budget Impact: {budget_status}\n"
            
            if insights:
                message += f"💡 Insight: {insights}"
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'transaction_id': transaction_id,
                    'amount': abs(amount),
                    'category': category,
                    'budget_status': budget_status,
                    'insights': insights
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Expense tracking error: {str(e)}"
            }
    
    def investment_recommendation(self, risk_tolerance: str, investment_amount: float, time_horizon: int) -> Dict[str, Any]:
        """Generate personalized investment recommendations."""
        try:
            risk_tolerance = risk_tolerance.lower()
            
            if risk_tolerance not in ['conservative', 'moderate', 'aggressive', 'speculative']:
                return {
                    'success': False,
                    'message': "Risk tolerance must be: conservative, moderate, aggressive, or speculative"
                }
            
            # Get current market conditions
            market_conditions = self.market_data.get_market_overview()
            
            # Generate asset allocation based on risk tolerance and time horizon
            asset_allocation = self._generate_asset_allocation(risk_tolerance, time_horizon)
            
            # Calculate recommended investments
            recommendations = []
            for asset_type, percentage in asset_allocation.items():
                amount = investment_amount * (percentage / 100)
                specific_investments = self._get_specific_investments(asset_type, amount)
                recommendations.extend(specific_investments)
            
            # Generate risk analysis
            risk_analysis = self._analyze_investment_risk(recommendations, risk_tolerance)
            
            # Calculate expected returns
            expected_annual_return = self._calculate_expected_return(recommendations, time_horizon)
            projected_value = investment_amount * ((1 + expected_annual_return/100) ** time_horizon)
            
            message = f"📈 Investment Recommendation\n\n"
            message += f"💰 Investment Amount: ${investment_amount:,.2f}\n"
            message += f"⏰ Time Horizon: {time_horizon} years\n"
            message += f"🎯 Risk Level: {risk_tolerance.title()}\n"
            message += f"📊 Expected Annual Return: {expected_annual_return:.1f}%\n"
            message += f"🏆 Projected Value: ${projected_value:,.2f}\n\n"
            message += f"🎯 Asset Allocation:\n"
            
            for asset_type, percentage in asset_allocation.items():
                amount = investment_amount * (percentage / 100)
                message += f"• {asset_type.title()}: {percentage}% (${amount:,.2f})\n"
            
            message += f"\n💡 Top Recommendations:\n"
            for i, rec in enumerate(recommendations[:3], 1):
                message += f"{i}. {rec['name']} - ${rec['amount']:.2f} ({rec['rationale']})\n"
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'investment_amount': investment_amount,
                    'risk_tolerance': risk_tolerance,
                    'time_horizon': time_horizon,
                    'asset_allocation': asset_allocation,
                    'recommendations': recommendations,
                    'expected_return': expected_annual_return,
                    'projected_value': projected_value,
                    'risk_analysis': risk_analysis
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Investment recommendation error: {str(e)}"
            }
    
    def budget_optimization(self) -> Dict[str, Any]:
        """Analyze spending and optimize budget allocation."""
        try:
            # Get recent transactions for analysis
            transactions = self._get_recent_transactions(90)  # Last 3 months
            
            # Categorize and analyze spending
            spending_by_category = {}
            for transaction in transactions:
                if transaction.transaction_type == 'debit':
                    category = transaction.category
                    if category not in spending_by_category:
                        spending_by_category[category] = 0
                    spending_by_category[category] += abs(transaction.amount)
            
            # Calculate monthly averages
            monthly_spending = {cat: amount/3 for cat, amount in spending_by_category.items()}
            total_monthly_spending = sum(monthly_spending.values())
            
            # Generate optimization recommendations
            optimizations = []
            savings_potential = 0
            
            for category, amount in monthly_spending.items():
                percentage = (amount / total_monthly_spending * 100) if total_monthly_spending > 0 else 0
                
                # Identify optimization opportunities
                if category == 'entertainment' and percentage > 15:
                    potential_saving = amount * 0.2  # 20% reduction
                    optimizations.append({
                        'category': category,
                        'current': amount,
                        'recommended': amount - potential_saving,
                        'savings': potential_saving,
                        'suggestion': 'Consider reducing entertainment expenses by 20%'
                    })
                    savings_potential += potential_saving
                
                elif category == 'food' and percentage > 20:
                    potential_saving = amount * 0.15  # 15% reduction
                    optimizations.append({
                        'category': category,
                        'current': amount,
                        'recommended': amount - potential_saving,
                        'savings': potential_saving,
                        'suggestion': 'Try meal planning and cooking at home more often'
                    })
                    savings_potential += potential_saving
                
                elif category == 'shopping' and percentage > 10:
                    potential_saving = amount * 0.25  # 25% reduction
                    optimizations.append({
                        'category': category,
                        'current': amount,
                        'recommended': amount - potential_saving,
                        'savings': potential_saving,
                        'suggestion': 'Implement a 24-hour rule before non-essential purchases'
                    })
                    savings_potential += potential_saving
            
            # Generate optimized budget
            optimized_budget = self._create_optimized_budget(monthly_spending, optimizations)
            
            message = f"💰 Budget Optimization Analysis\n\n"
            message += f"📊 Current Monthly Spending: ${total_monthly_spending:.2f}\n"
            message += f"💎 Potential Monthly Savings: ${savings_potential:.2f}\n"
            message += f"🎯 Optimization Opportunities: {len(optimizations)}\n\n"
            
            if optimizations:
                message += f"🔧 Top Optimization Recommendations:\n"
                for opt in optimizations[:3]:
                    message += f"• {opt['category'].title()}: Save ${opt['savings']:.2f} - {opt['suggestion']}\n"
            else:
                message += "✅ Your budget is well-optimized! Keep up the good work.\n"
            
            message += f"\n📈 Optimized Allocation:\n"
            for category, amount in sorted(optimized_budget.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (amount / sum(optimized_budget.values()) * 100)
                message += f"• {category.title()}: ${amount:.2f} ({percentage:.1f}%)\n"
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'current_spending': monthly_spending,
                    'total_monthly_spending': total_monthly_spending,
                    'optimizations': optimizations,
                    'savings_potential': savings_potential,
                    'optimized_budget': optimized_budget
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Budget optimization error: {str(e)}"
            }
    
    def financial_goal_tracking(self, goal_name: str = None) -> Dict[str, Any]:
        """Track progress on financial goals."""
        try:
            goals = self._get_all_goals()
            
            if goal_name:
                # Track specific goal
                goal = next((g for g in goals if g.name.lower() == goal_name.lower()), None)
                if not goal:
                    return {
                        'success': False,
                        'message': f"Goal '{goal_name}' not found"
                    }
                
                progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                remaining = goal.target_amount - goal.current_amount
                days_remaining = (goal.target_date - datetime.now()).days
                
                # Calculate required monthly savings
                months_remaining = max(1, days_remaining / 30)
                monthly_needed = remaining / months_remaining if months_remaining > 0 else remaining
                
                message = f"🎯 Goal: {goal.name}\n"
                message += f"💰 Target: ${goal.target_amount:,.2f}\n"
                message += f"💵 Current: ${goal.current_amount:,.2f}\n"
                message += f"📊 Progress: {progress_percentage:.1f}%\n"
                message += f"⏰ Days Remaining: {days_remaining}\n"
                message += f"📈 Monthly Need: ${monthly_needed:.2f}\n"
                
                if progress_percentage >= 100:
                    message += "🎉 Congratulations! Goal achieved!"
                elif progress_percentage >= 75:
                    message += "🔥 You're almost there! Keep it up!"
                elif progress_percentage >= 50:
                    message += "💪 Great progress! Stay focused!"
                else:
                    message += "🚀 Time to accelerate your savings!"
                
                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'goal': goal.__dict__,
                        'progress_percentage': progress_percentage,
                        'remaining_amount': remaining,
                        'days_remaining': days_remaining,
                        'monthly_needed': monthly_needed
                    }
                }
            else:
                # Overview of all goals
                if not goals:
                    return {
                        'success': True,
                        'message': "📋 No financial goals set. Use 'create financial goal' to get started!",
                        'data': {'goals': []}
                    }
                
                message = f"🎯 Financial Goals Overview ({len(goals)} goals)\n\n"
                goal_data = []
                
                for goal in sorted(goals, key=lambda g: g.target_date):
                    progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                    days_left = (goal.target_date - datetime.now()).days
                    
                    status_emoji = "🎉" if progress >= 100 else "🔥" if progress >= 75 else "💪" if progress >= 50 else "🚀"
                    
                    message += f"{status_emoji} {goal.name}: {progress:.1f}% (${goal.current_amount:,.0f}/${goal.target_amount:,.0f})\n"
                    
                    goal_data.append({
                        'name': goal.name,
                        'progress': progress,
                        'current': goal.current_amount,
                        'target': goal.target_amount,
                        'days_remaining': days_left,
                        'priority': goal.priority
                    })
                
                return {
                    'success': True,
                    'message': message.strip(),
                    'data': {'goals': goal_data}
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Goal tracking error: {str(e)}"
            }
    
    def market_insights(self) -> Dict[str, Any]:
        """Get current market insights and analysis."""
        try:
            # Get market data
            market_overview = self.market_data.get_market_overview()
            sector_performance = self.market_data.get_sector_performance()
            economic_indicators = self.market_data.get_economic_indicators()
            
            # Generate insights
            insights = []
            
            # Market sentiment analysis
            if market_overview.get('market_trend') == 'bullish':
                insights.append("📈 Markets are showing bullish sentiment - good time for growth investments")
            elif market_overview.get('market_trend') == 'bearish':
                insights.append("📉 Markets are bearish - consider defensive positions and dollar-cost averaging")
            
            # Sector rotation opportunities
            best_sectors = sorted(sector_performance.items(), key=lambda x: x[1], reverse=True)[:3]
            insights.append(f"🏆 Top performing sectors: {', '.join([s[0] for s in best_sectors])}")
            
            # Economic indicators
            if economic_indicators.get('inflation_rate', 0) > 3:
                insights.append("⚠️ High inflation detected - consider inflation-protected assets")
            
            if economic_indicators.get('interest_rates', 0) > 4:
                insights.append("💰 High interest rates favor bonds and fixed-income investments")
            
            message = f"📊 Market Insights & Analysis\n\n"
            message += f"📈 Market Trend: {market_overview.get('market_trend', 'neutral').title()}\n"
            message += f"📉 Volatility: {market_overview.get('volatility', 'medium').title()}\n"
            message += f"💸 Inflation Rate: {economic_indicators.get('inflation_rate', 0):.1f}%\n"
            message += f"🏦 Interest Rates: {economic_indicators.get('interest_rates', 0):.1f}%\n\n"
            message += f"💡 Key Insights:\n"
            
            for insight in insights:
                message += f"• {insight}\n"
            
            return {
                'success': True,
                'message': message.strip(),
                'data': {
                    'market_overview': market_overview,
                    'sector_performance': sector_performance,
                    'economic_indicators': economic_indicators,
                    'insights': insights
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Market insights error: {str(e)}"
            }
    
    # Helper methods
    def _calculate_health_score(self, savings_rate: float, net_worth: float, debts: float, assets: float, investment_return: float) -> float:
        """Calculate financial health score (0-100)."""
        score = 0
        
        # Savings rate (30 points)
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 10:
            score += 20
        elif savings_rate >= 5:
            score += 10
        
        # Debt-to-asset ratio (25 points)
        debt_ratio = (debts / assets * 100) if assets > 0 else 100
        if debt_ratio < 10:
            score += 25
        elif debt_ratio < 30:
            score += 20
        elif debt_ratio < 50:
            score += 10
        
        # Net worth growth (25 points)
        if net_worth > 100000:
            score += 25
        elif net_worth > 50000:
            score += 20
        elif net_worth > 10000:
            score += 15
        elif net_worth > 0:
            score += 10
        
        # Investment performance (20 points)
        if investment_return > 10:
            score += 20
        elif investment_return > 5:
            score += 15
        elif investment_return > 0:
            score += 10
        elif investment_return > -5:
            score += 5
        
        return min(100, score)
    
    def _auto_categorize_expense(self, description: str) -> str:
        """Automatically categorize expense based on description."""
        description_lower = description.lower()
        
        for category, keywords in self.expense_categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _generate_asset_allocation(self, risk_tolerance: str, time_horizon: int) -> Dict[str, float]:
        """Generate asset allocation based on risk tolerance and time horizon."""
        allocations = {
            'conservative': {'bonds': 60, 'stocks': 30, 'cash': 10},
            'moderate': {'stocks': 60, 'bonds': 30, 'alternatives': 10},
            'aggressive': {'stocks': 80, 'alternatives': 15, 'bonds': 5},
            'speculative': {'stocks': 70, 'crypto': 20, 'alternatives': 10}
        }
        
        base_allocation = allocations.get(risk_tolerance, allocations['moderate'])
        
        # Adjust for time horizon
        if time_horizon < 5:
            # Short term - more conservative
            if 'stocks' in base_allocation:
                base_allocation['stocks'] *= 0.8
                base_allocation['bonds'] = base_allocation.get('bonds', 0) + 20
        elif time_horizon > 20:
            # Long term - more aggressive
            if 'stocks' in base_allocation:
                base_allocation['stocks'] *= 1.1
                base_allocation['bonds'] = max(0, base_allocation.get('bonds', 0) - 10)
        
        # Normalize to 100%
        total = sum(base_allocation.values())
        return {k: (v/total*100) for k, v in base_allocation.items()}
    
    def _get_specific_investments(self, asset_type: str, amount: float) -> List[Dict[str, Any]]:
        """Get specific investment recommendations for asset type."""
        recommendations = {
            'stocks': [
                {'name': 'S&P 500 Index Fund (SPY)', 'amount': amount * 0.6, 'rationale': 'Broad market exposure'},
                {'name': 'Technology ETF (QQQ)', 'amount': amount * 0.4, 'rationale': 'Growth potential'}
            ],
            'bonds': [
                {'name': 'Total Bond Market (BND)', 'amount': amount * 0.7, 'rationale': 'Diversified bonds'},
                {'name': 'Treasury Inflation-Protected (TIPS)', 'amount': amount * 0.3, 'rationale': 'Inflation protection'}
            ],
            'alternatives': [
                {'name': 'Real Estate Investment Trust (VNQ)', 'amount': amount * 0.5, 'rationale': 'Real estate exposure'},
                {'name': 'Commodity ETF (DJP)', 'amount': amount * 0.5, 'rationale': 'Commodity diversification'}
            ],
            'crypto': [
                {'name': 'Bitcoin ETF (BITO)', 'amount': amount * 0.7, 'rationale': 'Digital asset exposure'},
                {'name': 'Ethereum ETF', 'amount': amount * 0.3, 'rationale': 'Alternative crypto'}
            ]
        }
        
        return recommendations.get(asset_type, [{'name': 'Diversified Fund', 'amount': amount, 'rationale': 'General investment'}])
    
    def _calculate_expected_return(self, recommendations: List[Dict], time_horizon: int) -> float:
        """Calculate expected annual return based on recommendations."""
        # Simplified expected returns by asset type
        expected_returns = {
            'stocks': 8.0,
            'bonds': 4.0,
            'alternatives': 6.0,
            'crypto': 12.0,
            'cash': 2.0
        }
        
        # For simplicity, return a weighted average based on typical allocations
        return 7.5  # 7.5% expected annual return
    
    def _generate_financial_insights(self, metrics: Dict[str, float]) -> List[str]:
        """Generate personalized financial insights and recommendations."""
        insights = []
        
        if metrics['savings_rate'] < 10:
            insights.append("Increase your savings rate to at least 10% of income")
        elif metrics['savings_rate'] > 20:
            insights.append("Excellent savings rate! Consider investing the excess")
        
        if metrics['debt_to_asset_ratio'] > 30:
            insights.append("Focus on debt reduction to improve financial health")
        
        if metrics['investment_return'] < 0:
            insights.append("Review your investment portfolio for better diversification")
        
        if metrics['monthly_savings'] < 1000:
            insights.append("Build an emergency fund of 3-6 months expenses")
        
        return insights
    
    # Database helper methods
    def _save_transaction(self, transaction: Transaction):
        """Save transaction to database."""
        conn = sqlite3.connect(self.finance_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO transactions 
            (transaction_id, account_id, amount, description, category, 
             transaction_date, transaction_type, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.transaction_id, transaction.account_id, transaction.amount,
            transaction.description, transaction.category, transaction.date,
            transaction.transaction_type, json.dumps(transaction.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def _get_all_accounts(self) -> List[FinancialAccount]:
        """Get all financial accounts."""
        # Placeholder - would load from database
        return [
            FinancialAccount("checking", "Primary Checking", "checking", 5000.0, "USD", "Bank", datetime.now()),
            FinancialAccount("savings", "Emergency Fund", "savings", 15000.0, "USD", "Bank", datetime.now()),
            FinancialAccount("investment", "Investment Account", "investment", 25000.0, "USD", "Broker", datetime.now())
        ]
    
    def _get_recent_transactions(self, days: int) -> List[Transaction]:
        """Get recent transactions."""
        # Placeholder - would load from database
        return []
    
    def _get_all_investments(self) -> List[Investment]:
        """Get all investments."""
        # Placeholder - would load from database
        return []
    
    def _get_all_goals(self) -> List[FinancialGoal]:
        """Get all financial goals."""
        # Placeholder - would load from database
        return []

# Supporting classes (simplified for brevity)
class PortfolioManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class ExpenseTracker:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class InvestmentAnalyzer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class BudgetPlanner:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class MarketDataProvider:
    def get_market_overview(self) -> Dict[str, Any]:
        return {
            'market_trend': 'bullish',
            'volatility': 'medium',
            'last_update': datetime.now()
        }
    
    def get_sector_performance(self) -> Dict[str, float]:
        return {
            'technology': 15.2,
            'healthcare': 8.5,
            'finance': 12.1,
            'energy': -2.3,
            'consumer': 6.7
        }
    
    def get_economic_indicators(self) -> Dict[str, float]:
        return {
            'inflation_rate': 3.2,
            'interest_rates': 5.5,
            'unemployment_rate': 3.8,
            'gdp_growth': 2.1
        }

class FinancialInsights:
    def generate_insights(self, data: Dict[str, Any]) -> List[str]:
        return ["Sample financial insight"]
