"""
LLM Agent module for FinanceGPT
Handles communication with local LLMs via Ollama and generates financial insights.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Ollama not available. Install with: pip install ollama")

logger = logging.getLogger(__name__)

class FinancialLLMAgent:
    """Handles LLM communication for financial analysis and advice generation."""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.ollama_available = OLLAMA_AVAILABLE
        
        if self.ollama_available:
            self.client = ollama.Client()
            self._check_model_availability()
        else:
            logger.warning("Ollama client not available. LLM features will be limited.")
            
    def _check_model_availability(self):
        """Check if the specified model is available locally."""
        try:
            # Try to list models to see if ollama is running
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            if not any(self.model_name in model for model in available_models):
                logger.warning(f"Model {self.model_name} not found locally. Available models: {available_models}")
                logger.info(f"To install the model, run: ollama pull {self.model_name}")
                
        except Exception as e:
            logger.error(f"Error checking Ollama models: {str(e)}")
            logger.info("Make sure Ollama is running: ollama serve")
            
    def generate_financial_insights(self, analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive financial insights from analysis results."""
        
        if not self.ollama_available:
            return self._generate_fallback_insights(analysis_results)
            
        try:
            # Create a comprehensive prompt with analysis data
            prompt = self._create_analysis_prompt(analysis_results)
            
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self._get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            )
            
            insights = response['message']['content']
            logger.info("Generated LLM insights successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating LLM insights: {str(e)}")
            return self._generate_fallback_insights(analysis_results)
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the financial advisor."""
        return """You are a knowledgeable and empathetic personal financial advisor. Your role is to:

1. Analyze spending patterns and provide actionable insights
2. Identify areas for potential savings and optimization  
3. Offer practical, realistic financial advice
4. Maintain a supportive and encouraging tone
5. Focus on building sustainable financial habits

Guidelines:
- Be specific with recommendations and mention actual numbers from the data
- Prioritize the most impactful suggestions first
- Consider the user's lifestyle and spending patterns
- Avoid being judgmental; focus on positive reinforcement
- Provide concrete, actionable steps
- Keep advice practical and achievable"""

    def _create_analysis_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create a comprehensive prompt with analysis data."""
        
        overview = analysis_results.get('overview', {})
        category_analysis = analysis_results.get('category_analysis', {})
        time_analysis = analysis_results.get('time_analysis', {})
        weekday_analysis = analysis_results.get('weekday_analysis', {})
        trend_analysis = analysis_results.get('trend_analysis', {})
        outlier_analysis = analysis_results.get('outlier_analysis', {})
        basic_insights = analysis_results.get('insights', [])
        
        prompt = f"""
Please analyze this user's spending data and provide personalized financial advice:

## SPENDING OVERVIEW
- Total spending: ${overview.get('total_spending', 0)}
- Time period: {overview.get('date_range', {}).get('start', 'N/A')} to {overview.get('date_range', {}).get('end', 'N/A')} ({overview.get('date_range', {}).get('days', 0)} days)
- Number of transactions: {overview.get('num_transactions', 0)}
- Average daily spending: ${overview.get('avg_daily_spending', 0)}
- Average transaction amount: ${overview.get('avg_transaction_amount', 0)}

## TOP SPENDING CATEGORIES
"""
        
        # Add top categories
        top_categories = category_analysis.get('top_categories', {})
        for i, (category, data) in enumerate(list(top_categories.items())[:5], 1):
            prompt += f"{i}. {category}: ${data.get('total', 0)} ({data.get('percentage', 0)}% of total)\n"
            
        prompt += f"""
## SPENDING PATTERNS
- Weekend vs Weekday average: ${weekday_analysis.get('weekend_vs_weekday', {}).get('weekend_avg', 0):.2f} vs ${weekday_analysis.get('weekend_vs_weekday', {}).get('weekday_avg', 0):.2f}
"""

        # Add trend information
        if 'mom_growth' in trend_analysis:
            prompt += f"- Month-over-month spending change: {trend_analysis['mom_growth']}%\n"
            
        # Add outlier information
        if outlier_analysis.get('num_outliers', 0) > 0:
            prompt += f"- Unusual transactions: {outlier_analysis['num_outliers']} transactions above ${outlier_analysis.get('outlier_threshold', 0)}\n"
            
        prompt += f"""
## BASIC INSIGHTS DETECTED
{chr(10).join(f"- {insight}" for insight in basic_insights)}

Please provide:
1. **Key Observations**: What are the most important patterns you notice?
2. **Areas for Improvement**: Which categories or habits should the user focus on?
3. **Specific Recommendations**: Concrete steps to reduce spending (with dollar amounts when possible)
4. **Positive Reinforcement**: What is the user doing well?
5. **Action Plan**: 3-5 prioritized steps to improve their financial situation

Format your response in a friendly, conversational tone as if speaking directly to the user.
"""
        
        return prompt
        
    def generate_savings_advice(self, savings_simulation: Dict[str, Any]) -> str:
        """Generate specific advice for a savings simulation."""
        
        if not self.ollama_available:
            return self._generate_fallback_savings_advice(savings_simulation)
            
        try:
            prompt = f"""
The user is considering reducing their {savings_simulation['category']} spending by {savings_simulation['reduction_percentage']}%.

Current situation:
- Current {savings_simulation['category']} spending: ${savings_simulation['current_spending']}
- Potential savings: ${savings_simulation['potential_savings']}
- Estimated monthly savings: ${savings_simulation['monthly_savings_estimate']}
- Estimated annual savings: ${savings_simulation['annual_savings_estimate']}

Please provide:
1. Whether this reduction seems realistic and achievable
2. Specific strategies to reduce spending in this category
3. What they could do with the money they save
4. Any potential challenges and how to overcome them

Keep the advice practical and encouraging.
"""
            
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self._get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'max_tokens': 500
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating savings advice: {str(e)}")
            return self._generate_fallback_savings_advice(savings_simulation)
            
    def _generate_fallback_insights(self, analysis_results: Dict[str, Any]) -> str:
        """Generate basic insights when LLM is not available."""
        
        overview = analysis_results.get('overview', {})
        category_analysis = analysis_results.get('category_analysis', {})
        weekday_analysis = analysis_results.get('weekday_analysis', {})
        basic_insights = analysis_results.get('insights', [])
        
        fallback_text = f"""
## Financial Analysis Summary

**Overview:**
Your total spending over the analyzed period was ${overview.get('total_spending', 0):.2f} across {overview.get('num_transactions', 0)} transactions, averaging ${overview.get('avg_daily_spending', 0):.2f} per day.

**Key Insights:**
"""
        
        for insight in basic_insights:
            fallback_text += f"• {insight}\n"
            
        fallback_text += f"""
**Top Spending Categories:**
"""
        
        top_categories = category_analysis.get('top_categories', {})
        for category, data in list(top_categories.items())[:3]:
            fallback_text += f"• {category}: ${data.get('total', 0):.2f} ({data.get('percentage', 0):.1f}% of total)\n"
            
        fallback_text += f"""
**Recommendations:**
• Focus on your highest spending category to maximize savings impact
• Review weekend spending patterns if they're significantly higher than weekdays
• Consider setting daily spending limits based on your average of ${overview.get('avg_daily_spending', 0):.2f}
• Track unusual large purchases to maintain better control

*Note: Enhanced AI insights require Ollama to be installed and running with a language model.*
"""
        
        return fallback_text
        
    def _generate_fallback_savings_advice(self, savings_simulation: Dict[str, Any]) -> str:
        """Generate basic savings advice when LLM is not available."""
        
        category = savings_simulation['category']
        reduction = savings_simulation['reduction_percentage']
        monthly_savings = savings_simulation['monthly_savings_estimate']
        annual_savings = savings_simulation['annual_savings_estimate']
        
        return f"""
## Savings Simulation for {category}

**Potential Impact:**
By reducing your {category} spending by {reduction}%, you could save approximately:
• ${monthly_savings:.2f} per month
• ${annual_savings:.2f} per year

**General Strategies for {category}:**
• Set a monthly budget limit
• Look for discounts and alternatives
• Track purchases more closely
• Consider if all expenses in this category are necessary

**What to do with savings:**
• Build an emergency fund
• Pay down debt
• Invest for long-term goals
• Save for specific purchases

*Note: For personalized strategies, install Ollama with a language model for enhanced AI advice.*
"""

    def check_ollama_status(self) -> Dict[str, Any]:
        """Check if Ollama is available and running."""
        status = {
            'ollama_installed': self.ollama_available,
            'ollama_running': False,
            'model_available': False,
            'available_models': []
        }
        
        if not self.ollama_available:
            return status
            
        try:
            models_response = self.client.list()
            status['ollama_running'] = True
            status['available_models'] = [model['name'] for model in models_response['models']]
            status['model_available'] = any(self.model_name in model for model in status['available_models'])
            
        except Exception as e:
            logger.error(f"Error checking Ollama status: {str(e)}")
            
        return status
        
    def suggest_model_setup(self) -> str:
        """Provide setup instructions for Ollama and models."""
        return f"""
## Setting up Local LLM with Ollama

1. **Install Ollama:**
   Visit https://ollama.ai and download for your system
   
2. **Start Ollama:**
   Run in terminal: `ollama serve`
   
3. **Install a model:**
   Run: `ollama pull {self.model_name}`
   
   Alternative lightweight models:
   - `ollama pull llama3.2:1b` (smaller, faster)
   - `ollama pull phi3:mini` (Microsoft's efficient model)
   - `ollama pull mistral:7b` (good balance of size/quality)
   
4. **Verify installation:**
   Run: `ollama list`
   
5. **Test the model:**
   Run: `ollama run {self.model_name}`

Once setup is complete, restart the FinanceGPT application for enhanced AI insights!
""" 