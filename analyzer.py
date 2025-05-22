"""
Analyzer module for FinanceGPT
Handles data analysis, trend detection, and visualization generation.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class SpendingAnalyzer:
    """Analyzes spending patterns and generates insights."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.total_spending = self.data['amount'].sum()
        self.date_range = (self.data['date'].min(), self.data['date'].max())
        self.analysis_results = {}
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analysis and return results."""
        try:
            results = {
                'overview': self._get_overview(),
                'category_analysis': self._analyze_by_category(),
                'time_analysis': self._analyze_by_time(),
                'trend_analysis': self._analyze_trends(),
                'weekday_analysis': self._analyze_weekday_patterns(),
                'outlier_analysis': self._detect_outliers(),
                'insights': self._generate_insights()
            }
            
            self.analysis_results = results
            logger.info("Completed full spending analysis")
            return results
            
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            raise
            
    def _get_overview(self) -> Dict[str, Any]:
        """Get basic overview statistics."""
        days_span = (self.date_range[1] - self.date_range[0]).days + 1
        
        overview = {
            'total_spending': round(self.total_spending, 2),
            'num_transactions': len(self.data),
            'date_range': {
                'start': self.date_range[0].strftime('%Y-%m-%d'),
                'end': self.date_range[1].strftime('%Y-%m-%d'),
                'days': days_span
            },
            'avg_daily_spending': round(self.total_spending / days_span, 2),
            'avg_transaction_amount': round(self.data['amount'].mean(), 2),
            'median_transaction_amount': round(self.data['amount'].median(), 2),
            'spending_std': round(self.data['amount'].std(), 2)
        }
        
        return overview
        
    def _analyze_by_category(self) -> Dict[str, Any]:
        """Analyze spending patterns by category."""
        category_stats = self.data.groupby('category').agg({
            'amount': ['sum', 'mean', 'count', 'std']
        }).round(2)
        
        category_stats.columns = ['total', 'avg_per_transaction', 'frequency', 'std']
        category_stats = category_stats.sort_values('total', ascending=False)
        
        # Calculate percentages
        category_stats['percentage'] = (category_stats['total'] / self.total_spending * 100).round(1)
        
        # Get top spending categories
        top_categories = category_stats.head(5).to_dict('index')
        
        return {
            'summary': category_stats.to_dict('index'),
            'top_categories': top_categories,
            'category_count': len(category_stats)
        }
        
    def _analyze_by_time(self) -> Dict[str, Any]:
        """Analyze spending patterns over time."""
        # Monthly analysis
        monthly = self.data.groupby(['year', 'month']).agg({
            'amount': ['sum', 'count']
        }).round(2)
        monthly.columns = ['total_spending', 'transaction_count']
        
        # Weekly analysis
        weekly = self.data.groupby('week_number').agg({
            'amount': ['sum', 'mean', 'count']
        }).round(2)
        weekly.columns = ['total', 'avg', 'count']
        
        # Daily analysis (last 30 days if available)
        recent_data = self.data[self.data['date'] >= (self.data['date'].max() - timedelta(days=30))]
        daily_recent = recent_data.groupby('date')['amount'].sum().round(2)
        
        return {
            'monthly': monthly.to_dict('index'),
            'weekly': weekly.to_dict('index'),
            'daily_recent': daily_recent.to_dict(),
            'monthly_trend': self._calculate_monthly_trend(monthly)
        }
        
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze spending trends and patterns."""
        # Calculate rolling averages
        daily_spending = self.data.groupby('date')['amount'].sum().sort_index()
        
        trends = {}
        
        if len(daily_spending) > 7:
            trends['7_day_avg'] = daily_spending.rolling(window=7).mean().iloc[-1]
            
        if len(daily_spending) > 30:
            trends['30_day_avg'] = daily_spending.rolling(window=30).mean().iloc[-1]
            
        # Calculate month-over-month growth
        monthly_totals = self.data.groupby(['year', 'month'])['amount'].sum()
        if len(monthly_totals) > 1:
            recent_months = monthly_totals.tail(2)
            if len(recent_months) == 2:
                current, previous = recent_months.iloc[-1], recent_months.iloc[-2]
                trends['mom_growth'] = round(((current - previous) / previous) * 100, 1)
                
        return trends
        
    def _analyze_weekday_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns by day of week."""
        weekday_stats = self.data.groupby('weekday').agg({
            'amount': ['sum', 'mean', 'count']
        }).round(2)
        weekday_stats.columns = ['total', 'avg', 'frequency']
        
        # Order by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_stats = weekday_stats.reindex(weekday_order)
        
        weekend_vs_weekday = {
            'weekend_avg': self.data[self.data['is_weekend']]['amount'].mean(),
            'weekday_avg': self.data[~self.data['is_weekend']]['amount'].mean(),
            'weekend_total': self.data[self.data['is_weekend']]['amount'].sum(),
            'weekday_total': self.data[~self.data['is_weekend']]['amount'].sum()
        }
        
        return {
            'by_weekday': weekday_stats.to_dict('index'),
            'weekend_vs_weekday': weekend_vs_weekday
        }
        
    def _detect_outliers(self) -> Dict[str, Any]:
        """Detect unusual spending patterns."""
        # Use IQR method to detect outliers
        Q1 = self.data['amount'].quantile(0.25)
        Q3 = self.data['amount'].quantile(0.75)
        IQR = Q3 - Q1
        
        outlier_threshold = Q3 + 1.5 * IQR
        outliers = self.data[self.data['amount'] > outlier_threshold]
        
        # Detect categories with high variance
        category_variance = self.data.groupby('category')['amount'].std().sort_values(ascending=False)
        
        return {
            'high_amount_transactions': outliers.nlargest(5, 'amount')[['date', 'category', 'amount']].to_dict('records'),
            'outlier_threshold': round(outlier_threshold, 2),
            'num_outliers': len(outliers),
            'high_variance_categories': category_variance.head(3).to_dict()
        }
        
    def _generate_insights(self) -> List[str]:
        """Generate text insights from the analysis."""
        insights = []
        
        # Category insights
        category_analysis = self._analyze_by_category()
        top_category = list(category_analysis['top_categories'].keys())[0]
        top_percentage = category_analysis['top_categories'][top_category]['percentage']
        
        insights.append(f"Your highest spending category is {top_category}, accounting for {top_percentage}% of total expenses.")
        
        # Weekend vs weekday insights
        weekday_analysis = self._analyze_weekday_patterns()
        weekend_avg = weekday_analysis['weekend_vs_weekday']['weekend_avg']
        weekday_avg = weekday_analysis['weekend_vs_weekday']['weekday_avg']
        
        if weekend_avg > weekday_avg * 1.2:
            insights.append(f"You tend to spend {round((weekend_avg/weekday_avg - 1) * 100, 1)}% more on weekends than weekdays.")
        
        # Trend insights
        trends = self._analyze_trends()
        if 'mom_growth' in trends:
            if trends['mom_growth'] > 10:
                insights.append(f"Your spending increased by {trends['mom_growth']}% compared to last month.")
            elif trends['mom_growth'] < -10:
                insights.append(f"Good news! Your spending decreased by {abs(trends['mom_growth'])}% compared to last month.")
                
        # Outlier insights
        outliers = self._detect_outliers()
        if outliers['num_outliers'] > 0:
            insights.append(f"You had {outliers['num_outliers']} unusually large transactions above ${outliers['outlier_threshold']}.")
            
        return insights
        
    def _calculate_monthly_trend(self, monthly_data: pd.DataFrame) -> str:
        """Calculate overall monthly trend."""
        if len(monthly_data) < 3:
            return "Insufficient data for trend analysis"
            
        recent_months = monthly_data['total_spending'].tail(3)
        if recent_months.iloc[-1] > recent_months.iloc[0]:
            return "Increasing"
        elif recent_months.iloc[-1] < recent_months.iloc[0]:
            return "Decreasing"
        else:
            return "Stable"
            
    def create_visualizations(self) -> Dict[str, Any]:
        """Create all visualizations and return plotly figures."""
        figs = {}
        
        try:
            # 1. Spending by Category (Pie Chart)
            category_totals = self.data.groupby('category')['amount'].sum().sort_values(ascending=False)
            figs['category_pie'] = px.pie(
                values=category_totals.values,
                names=category_totals.index,
                title="Spending Distribution by Category"
            )
            
            # 2. Spending Over Time (Line Chart)
            daily_spending = self.data.groupby('date')['amount'].sum().reset_index()
            figs['spending_timeline'] = px.line(
                daily_spending,
                x='date',
                y='amount',
                title="Daily Spending Over Time"
            )
            
            # 3. Category vs Weekday Heatmap
            category_weekday = self.data.groupby(['category', 'weekday'])['amount'].sum().reset_index()
            category_weekday_pivot = category_weekday.pivot(index='category', columns='weekday', values='amount').fillna(0)
            
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            category_weekday_pivot = category_weekday_pivot.reindex(columns=weekday_order, fill_value=0)
            
            figs['category_weekday_heatmap'] = px.imshow(
                category_weekday_pivot.values,
                x=category_weekday_pivot.columns,
                y=category_weekday_pivot.index,
                title="Spending Patterns: Category vs Day of Week"
            )
            
            # 4. Weekly Spending Comparison
            weekday_spending = self.data.groupby('weekday')['amount'].sum()
            weekday_spending = weekday_spending.reindex(weekday_order)
            
            figs['weekday_spending'] = px.bar(
                x=weekday_spending.index,
                y=weekday_spending.values,
                title="Total Spending by Day of Week"
            )
            
            # 5. Monthly Spending Trend
            monthly_spending = self.data.groupby(['year', 'month'])['amount'].sum().reset_index()
            monthly_spending['date'] = pd.to_datetime(monthly_spending[['year', 'month']].assign(day=1))
            
            figs['monthly_trend'] = px.line(
                monthly_spending,
                x='date',
                y='amount',
                title="Monthly Spending Trend"
            )
            
            logger.info("Created all visualizations successfully")
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            
        return figs
        
    def simulate_savings(self, category: str, reduction_percentage: float) -> Dict[str, Any]:
        """Simulate potential savings by reducing spending in a category."""
        if category not in self.data['category'].values:
            raise ValueError(f"Category '{category}' not found in data")
            
        category_total = self.data[self.data['category'] == category]['amount'].sum()
        potential_savings = category_total * (reduction_percentage / 100)
        
        # Calculate monthly savings (approximate)
        days_in_data = (self.date_range[1] - self.date_range[0]).days + 1
        monthly_savings = potential_savings * (30 / days_in_data)
        annual_savings = potential_savings * (365 / days_in_data)
        
        return {
            'category': category,
            'current_spending': round(category_total, 2),
            'reduction_percentage': reduction_percentage,
            'potential_savings': round(potential_savings, 2),
            'monthly_savings_estimate': round(monthly_savings, 2),
            'annual_savings_estimate': round(annual_savings, 2),
            'new_category_total': round(category_total - potential_savings, 2)
        } 