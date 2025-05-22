# 🏦 FinanceGPT - AI-Powered Personal Finance Analyzer

FinanceGPT is a Python-based personal finance analyzer that uses local AI models to provide personalized spending insights and financial advice. All your data stays local for complete privacy.

## ✨ Features

- 📊 **Comprehensive Spending Analysis** - Detailed breakdown by category, time trends, and patterns
- 📈 **Interactive Visualizations** - Beautiful charts using Plotly for spending insights
- 🤖 **Local AI Insights** - Personalized financial advice using Ollama (no cloud APIs needed)
- 💰 **Savings Simulation** - Calculate potential savings by reducing specific categories
- 🔒 **Privacy-Focused** - All analysis happens locally, your data never leaves your computer
- 📱 **Beautiful CLI** - Rich terminal interface with progress bars and colorful output
- 📝 **Sample Data Generator** - Built-in tool to create realistic test data

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd FinGPT

# Install dependencies
pip install -r requirements.txt
```

### 2. Set up Ollama (for AI insights)

```bash
# Install Ollama (visit https://ollama.ai)
# On macOS:
brew install ollama

# Start Ollama
ollama serve

# Install a model (in another terminal)
ollama pull llama3.2:3b
# or for a smaller model:
ollama pull llama3.2:1b
```

### 3. Run FinanceGPT

```bash
# Interactive mode
python main.py

# Quick analysis of existing CSV
python main.py --file your_spending.csv

# Generate sample data
python main.py --sample
```

## 📊 CSV Format

Your spending data should be a CSV file with these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `date` | ✅ | Transaction date | 2024-01-15 |
| `category` | ✅ | Spending category | Groceries |
| `amount` | ✅ | Amount spent (positive) | 45.67 |
| `notes` | ❌ | Optional description | Weekly shopping |

### Example CSV:
```csv
date,category,amount,notes
2024-01-15,Groceries,45.67,Weekly shopping
2024-01-16,Coffee,4.50,Morning latte
2024-01-17,Dining,23.45,Lunch with friends
2024-01-18,Transport,12.00,Bus fare
```

## 🎯 Usage Guide

### 1. Load Your Data
- **Option A**: Use the interactive menu to load your CSV file
- **Option B**: Generate sample data for testing
- **Option C**: Use command line: `python main.py --file your_data.csv`

### 2. Analyze Spending
The analyzer will provide:
- **Overview statistics** (total spending, averages, transaction count)
- **Category breakdown** (top spending categories with percentages)
- **Time patterns** (monthly trends, weekday vs weekend spending)
- **Outlier detection** (unusually large transactions)
- **AI-generated insights** (personalized financial advice)

### 3. Visualizations
Interactive Plotly charts including:
- 🥧 Spending distribution by category (pie chart)
- 📈 Daily spending timeline
- 🔥 Category vs weekday heatmap  
- 📊 Weekday spending comparison
- 📅 Monthly spending trends

### 4. Savings Simulation
- Select any spending category
- Set a reduction percentage (e.g., 20%)
- See potential monthly and annual savings
- Get AI advice on how to achieve the reduction

## 🤖 AI Features

FinanceGPT uses local LLM models via Ollama to provide:

### Personalized Insights
- "You tend to overspend on weekends in the dining category"
- "Consider reducing transport costs on weekdays"
- "Your grocery spending is well-controlled compared to similar households"

### Actionable Recommendations
- Specific strategies for reducing spending in problem areas
- Budget suggestions based on your patterns
- Tips for building better financial habits

### Savings Advice
- Realistic assessment of proposed spending reductions
- Specific tactics for achieving savings goals
- Ideas for what to do with money saved

## 📁 Project Structure

```
FinGPT/
├── main.py              # Main entry point
├── data_loader.py       # CSV loading and validation
├── analyzer.py          # Data analysis and trend detection
├── llm_agent.py         # Local LLM communication via Ollama
├── ui.py               # Rich CLI interface
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── sample_spending.csv  # Generated sample data (after first run)
```

## 🛠️ Dependencies

- **pandas** - Data manipulation and analysis
- **plotly** - Interactive visualizations
- **matplotlib/seaborn** - Additional plotting capabilities
- **ollama** - Local LLM integration
- **rich** - Beautiful terminal formatting
- **click** - Command-line interface
- **numpy** - Numerical computations

## 🔧 Configuration

### LLM Models

You can use different Ollama models by modifying `llm_agent.py`:

```python
# Lightweight models (faster, less detailed)
llm_agent = FinancialLLMAgent("llama3.2:1b")
llm_agent = FinancialLLMAgent("phi3:mini")

# Standard models (good balance)
llm_agent = FinancialLLMAgent("llama3.2:3b")  # default
llm_agent = FinancialLLMAgent("mistral:7b")

# Larger models (more detailed, slower)
llm_agent = FinancialLLMAgent("llama3.1:8b")
```

### Sample Data Customization

Modify the categories and spending ranges in `data_loader.py`:

```python
categories = {
    'Groceries': (20, 150),
    'Dining': (15, 80),
    'Your_Category': (min_amount, max_amount),
    # Add more categories...
}
```

## 📊 Example Output

```
┌─────────────────── Spending Overview ───────────────────┐
│ Metric          │ Value                                 │
├─────────────────┼───────────────────────────────────────┤
│ Total Spending  │ $3,245.67                            │
│ Transactions    │ 156                                   │
│ Avg Daily       │ $54.09                               │
│ Avg Transaction │ $20.81                               │
│ Time Period     │ 60 days                              │
└─────────────────┴───────────────────────────────────────┘

🤖 AI Financial Insights:

Based on your spending data, here are my key observations:

**Key Observations:**
Your spending shows a clear pattern with Groceries being your largest 
expense at 28% of total spending. You're doing well with consistent 
daily averages, but there's room for optimization in dining expenses.

**Areas for Improvement:**
1. Weekend dining spending is 45% higher than weekdays
2. Consider meal planning to reduce grocery waste
3. Transport costs could be optimized with monthly passes

**Action Plan:**
1. Set a weekend dining budget of $30 per weekend
2. Try batch cooking on Sundays to reduce weekday takeout
3. Track coffee purchases - they add up to $87/month
```

## 🚨 Troubleshooting

### Common Issues

**1. "Ollama not available" message**
```bash
# Install Ollama from https://ollama.ai
# Then run:
ollama serve
ollama pull llama3.2:3b
```

**2. CSV loading errors**
- Check that your CSV has required columns: `date`, `category`, `amount`
- Ensure dates are in YYYY-MM-DD format
- Verify amounts are positive numbers

**3. Visualization not opening**
- Make sure you have a default browser set
- Try running with `--browser` flag if available

**4. Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- Check the logs in `financegpt.log`
- Use the "Check Ollama setup" option in the main menu
- Ensure all dependencies are installed: `pip list`

## 🎨 Customization

### Adding New Analysis Features

1. **Extend `analyzer.py`** - Add new analysis methods
2. **Update `llm_agent.py`** - Include new data in AI prompts
3. **Modify `ui.py`** - Add new menu options

### Custom Visualizations

Add new chart types in `analyzer.py`:

```python
def create_custom_visualization(self):
    # Your custom Plotly chart
    fig = px.your_chart_type(...)
    return fig
```

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional visualization types
- More sophisticated AI prompts
- Export features (PDF reports)
- Streamlit web interface
- Budget planning features
- Integration with bank APIs

## 🔮 Future Features

- [ ] Streamlit web interface
- [ ] PDF report generation
- [ ] Budget planning and tracking
- [ ] Category-based budgeting
- [ ] Expense prediction models
- [ ] Integration with popular banking APIs
- [ ] Mobile app companion
- [ ] Multi-currency support

---

**Happy budgeting! 💰**

*Remember: The best financial plan is the one you actually follow. Start small, be consistent, and let FinanceGPT help you build better money habits.* 