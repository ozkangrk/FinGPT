#!/usr/bin/env python3
"""
Demo script for FinanceGPT
Generates sample data and runs a quick analysis to test all components.
"""

import sys
from pathlib import Path
import logging

# Add current directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import SpendingDataLoader, create_sample_data
from analyzer import SpendingAnalyzer
from llm_agent import FinancialLLMAgent
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown

console = Console()

def run_demo():
    """Run a complete demo of FinanceGPT functionality."""
    
    console.print(Panel(
        "[bold blue]🏦 FinanceGPT Demo[/bold blue]\n\n"
        "This demo will:\n"
        "1. Generate sample spending data\n"
        "2. Load and validate the data\n"
        "3. Run comprehensive analysis\n"
        "4. Generate AI insights\n"
        "5. Create visualizations\n"
        "6. Run savings simulation",
        title="Demo Script",
        border_style="blue"
    ))
    
    try:
        # Step 1: Generate sample data
        console.print("\n[bold cyan]Step 1: Generating sample data...[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating sample spending data...", total=None)
            
            sample_file = create_sample_data("demo_spending.csv")
            
            progress.update(task, description="✅ Sample data created!")
            
        console.print(f"[green]✅ Created: {sample_file}[/green]")
        
        # Step 2: Load data
        console.print("\n[bold cyan]Step 2: Loading and validating data...[/bold cyan]")
        
        loader = SpendingDataLoader()
        data = loader.load_csv(sample_file)
        
        # Show data summary
        summary_table = Table(title="Data Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Records", str(len(data)))
        summary_table.add_row("Date Range", f"{data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}")
        summary_table.add_row("Total Amount", f"${data['amount'].sum():.2f}")
        summary_table.add_row("Categories", str(len(data['category'].unique())))
        summary_table.add_row("Avg Transaction", f"${data['amount'].mean():.2f}")
        
        console.print(summary_table)
        
        # Step 3: Run analysis
        console.print("\n[bold cyan]Step 3: Running comprehensive analysis...[/bold cyan]")
        
        analyzer = SpendingAnalyzer(data)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing spending patterns...", total=None)
            
            analysis_results = analyzer.run_full_analysis()
            
            progress.update(task, description="✅ Analysis complete!")
            
        # Show key results
        overview = analysis_results['overview']
        categories = analysis_results['category_analysis']['top_categories']
        
        # Overview table
        overview_table = Table(title="Spending Overview", show_header=True, header_style="bold blue")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        
        overview_table.add_row("Total Spending", f"${overview['total_spending']}")
        overview_table.add_row("Avg Daily", f"${overview['avg_daily_spending']}")
        overview_table.add_row("Time Period", f"{overview['date_range']['days']} days")
        
        console.print(overview_table)
        
        # Top categories
        cat_table = Table(title="Top Spending Categories", show_header=True, header_style="bold green")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Amount", style="green", justify="right")
        cat_table.add_column("Percentage", style="yellow", justify="right")
        
        for category, data_dict in list(categories.items())[:5]:
            cat_table.add_row(
                category,
                f"${data_dict['total']:.2f}",
                f"{data_dict['percentage']:.1f}%"
            )
            
        console.print(cat_table)
        
        # Step 4: Generate AI insights
        console.print("\n[bold cyan]Step 4: Generating AI insights...[/bold cyan]")
        
        llm_agent = FinancialLLMAgent()
        
        # Check Ollama status
        status = llm_agent.check_ollama_status()
        
        status_table = Table(title="AI System Status", show_header=True, header_style="bold yellow")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        
        status_table.add_row("Ollama Installed", "✅ Yes" if status['ollama_installed'] else "❌ No")
        status_table.add_row("Ollama Running", "✅ Yes" if status['ollama_running'] else "❌ No")
        status_table.add_row("Model Available", "✅ Yes" if status['model_available'] else "❌ No")
        
        console.print(status_table)
        
        # Generate insights
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating AI insights...", total=None)
            
            insights = llm_agent.generate_financial_insights(analysis_results)
            
            progress.update(task, description="✅ AI insights generated!")
            
        # Display insights
        insights_panel = Panel(
            Markdown(insights),
            title="[bold green]🤖 AI Financial Insights[/bold green]",
            border_style="green"
        )
        
        console.print(insights_panel)
        
        # Step 5: Create visualizations
        console.print("\n[bold cyan]Step 5: Creating visualizations...[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating interactive charts...", total=None)
            
            visualizations = analyzer.create_visualizations()
            
            progress.update(task, description="✅ Visualizations created!")
            
        console.print(f"[green]✅ Created {len(visualizations)} interactive charts[/green]")
        console.print("[dim]Charts can be opened in browser through the main application[/dim]")
        
        # Step 6: Savings simulation
        console.print("\n[bold cyan]Step 6: Running savings simulation...[/bold cyan]")
        
        # Get top spending category for simulation
        top_category = list(categories.keys())[0]
        reduction_percentage = 20
        
        simulation = analyzer.simulate_savings(top_category, reduction_percentage)
        
        # Display simulation results
        sim_table = Table(title=f"Savings Simulation: {top_category}", show_header=True, header_style="bold yellow")
        sim_table.add_column("Metric", style="cyan")
        sim_table.add_column("Value", style="green", justify="right")
        
        sim_table.add_row("Current Spending", f"${simulation['current_spending']:.2f}")
        sim_table.add_row("Reduction", f"{simulation['reduction_percentage']:.1f}%")
        sim_table.add_row("Potential Savings", f"${simulation['potential_savings']:.2f}")
        sim_table.add_row("Monthly Estimate", f"${simulation['monthly_savings_estimate']:.2f}")
        sim_table.add_row("Annual Estimate", f"${simulation['annual_savings_estimate']:.2f}")
        
        console.print(sim_table)
        
        # Get savings advice
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating savings advice...", total=None)
            
            savings_advice = llm_agent.generate_savings_advice(simulation)
            
            progress.update(task, description="✅ Savings advice generated!")
            
        advice_panel = Panel(
            Markdown(savings_advice),
            title="[bold yellow]💡 Savings Advice[/bold yellow]",
            border_style="yellow"
        )
        
        console.print(advice_panel)
        
        # Demo complete
        console.print("\n[bold green]🎉 Demo Complete![/bold green]")
        
        next_steps = """
## Next Steps:

1. **Run the main application:**
   ```bash
   python main.py
   ```

2. **Load your own CSV data:**
   ```bash
   python main.py --file your_spending.csv
   ```

3. **Set up Ollama for enhanced AI insights:**
   ```bash
   ollama serve
   ollama pull llama3.2:3b
   ```

4. **Explore visualizations in the main app**

5. **Try different savings simulations**
"""
        
        console.print(Panel(
            Markdown(next_steps),
            title="[bold blue]What's Next?[/bold blue]",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed with error: {str(e)}[/red]")
        logging.error(f"Demo error: {str(e)}", exc_info=True)
        return False
        
    return True

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    console.print("[bold blue]Starting FinanceGPT Demo...[/bold blue]\n")
    
    success = run_demo()
    
    if success:
        console.print("\n[bold green]Demo completed successfully! 🎉[/bold green]")
    else:
        console.print("\n[bold red]Demo encountered issues. Check the logs for details.[/bold red]")
        sys.exit(1) 