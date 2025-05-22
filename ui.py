"""
UI module for FinanceGPT
Handles command-line interface with Rich for beautiful formatting.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown
import logging

# Import our modules
from data_loader import SpendingDataLoader, create_sample_data
from analyzer import SpendingAnalyzer
from llm_agent import FinancialLLMAgent

console = Console()
logger = logging.getLogger(__name__)

class FinanceGPTUI:
    """Main UI class for FinanceGPT CLI application."""
    
    def __init__(self):
        self.console = console
        self.data_loader = SpendingDataLoader()
        self.analyzer = None
        self.llm_agent = FinancialLLMAgent()
        self.current_data = None
        self.current_analysis = None
        
    def run(self):
        """Main application loop."""
        self._show_welcome()
        
        while True:
            try:
                choice = self._show_main_menu()
                
                if choice == "1":
                    self._load_csv_workflow()
                elif choice == "2":
                    self._create_sample_data_workflow()
                elif choice == "3":
                    self._analyze_data_workflow()
                elif choice == "4":
                    self._show_visualizations_workflow()
                elif choice == "5":
                    self._savings_simulation_workflow()
                elif choice == "6":
                    self._check_ollama_setup()
                elif choice == "7":
                    self._show_about()
                elif choice == "8":
                    self._exit_application()
                    break
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
                    
            except KeyboardInterrupt:
                self._exit_application()
                break
            except Exception as e:
                self.console.print(f"[red]An error occurred: {str(e)}[/red]")
                
    def _show_welcome(self):
        """Show welcome screen."""
        welcome_text = """
# 🏦 FinanceGPT - Personal Finance Analyzer

Welcome to FinanceGPT! This tool analyzes your spending data and provides AI-powered 
financial insights to help you improve your financial habits.

## Features:
- 📊 Comprehensive spending analysis
- 📈 Interactive visualizations  
- 🤖 AI-powered financial advice (via local LLM)
- 💰 Savings simulation
- 📋 Export capabilities
"""
        
        panel = Panel(
            Markdown(welcome_text),
            title="[bold blue]FinanceGPT[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(panel)
        
    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        
        # Check current data status
        data_status = "✅ Loaded" if self.current_data is not None else "❌ No data"
        analysis_status = "✅ Complete" if self.current_analysis is not None else "❌ Not run"
        
        menu_text = f"""
[bold cyan]Main Menu[/bold cyan]

Data Status: {data_status} | Analysis Status: {analysis_status}

[bold]1.[/bold] 📁 Load CSV file
[bold]2.[/bold] 📝 Create sample data for testing
[bold]3.[/bold] 📊 Analyze spending data
[bold]4.[/bold] 📈 View visualizations
[bold]5.[/bold] 💰 Savings simulation
[bold]6.[/bold] 🤖 Check Ollama setup
[bold]7.[/bold] ℹ️  About
[bold]8.[/bold] 🚪 Exit
"""
        
        self.console.print(Panel(menu_text, border_style="cyan"))
        
        choice = Prompt.ask(
            "Enter your choice",
            choices=["1", "2", "3", "4", "5", "6", "7", "8"],
            default="1"
        )
        
        return choice
        
    def _load_csv_workflow(self):
        """Handle CSV loading workflow."""
        self.console.print("\n[bold cyan]📁 Load CSV File[/bold cyan]")
        
        # Get file path
        file_path = Prompt.ask("Enter path to your CSV file")
        
        if not Path(file_path).exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Loading and validating CSV...", total=None)
                
                self.current_data = self.data_loader.load_csv(file_path)
                self.analyzer = SpendingAnalyzer(self.current_data)
                self.current_analysis = None  # Reset analysis
                
                progress.update(task, description="✅ CSV loaded successfully!")
                
            # Show data summary
            self._show_data_summary()
            
        except Exception as e:
            self.console.print(f"[red]Error loading CSV: {str(e)}[/red]")
            
    def _create_sample_data_workflow(self):
        """Handle sample data creation workflow."""
        self.console.print("\n[bold cyan]📝 Create Sample Data[/bold cyan]")
        
        num_records = Prompt.ask("Number of sample records", default="200")
        output_path = Prompt.ask("Output file path", default="sample_spending.csv")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Creating sample data...", total=None)
                
                create_sample_data(output_path)
                
                progress.update(task, description="✅ Sample data created!")
                
            self.console.print(f"[green]Sample data created: {output_path}[/green]")
            
            # Ask if user wants to load it
            if Confirm.ask("Load the sample data now?"):
                self.current_data = self.data_loader.load_csv(output_path)
                self.analyzer = SpendingAnalyzer(self.current_data)
                self.current_analysis = None
                self._show_data_summary()
                
        except Exception as e:
            self.console.print(f"[red]Error creating sample data: {str(e)}[/red]")
            
    def _analyze_data_workflow(self):
        """Handle data analysis workflow."""
        if self.current_data is None:
            self.console.print("[red]Please load data first![/red]")
            return
            
        self.console.print("\n[bold cyan]📊 Analyzing Spending Data[/bold cyan]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task1 = progress.add_task("Running data analysis...", total=None)
                
                self.current_analysis = self.analyzer.run_full_analysis()
                
                progress.update(task1, description="✅ Analysis complete!")
                
                task2 = progress.add_task("Generating AI insights...", total=None)
                
                ai_insights = self.llm_agent.generate_financial_insights(self.current_analysis)
                
                progress.update(task2, description="✅ AI insights generated!")
                
            # Show results
            self._show_analysis_results(ai_insights)
            
        except Exception as e:
            self.console.print(f"[red]Error during analysis: {str(e)}[/red]")
            
    def _show_data_summary(self):
        """Show summary of loaded data."""
        if self.current_data is None:
            return
            
        overview = {
            'Total Records': len(self.current_data),
            'Date Range': f"{self.current_data['date'].min().strftime('%Y-%m-%d')} to {self.current_data['date'].max().strftime('%Y-%m-%d')}",
            'Total Amount': f"${self.current_data['amount'].sum():.2f}",
            'Categories': len(self.current_data['category'].unique()),
            'Avg Transaction': f"${self.current_data['amount'].mean():.2f}"
        }
        
        table = Table(title="Data Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for metric, value in overview.items():
            table.add_row(metric, str(value))
            
        self.console.print(table)
        
    def _show_analysis_results(self, ai_insights: str):
        """Show analysis results."""
        if self.current_analysis is None:
            return
            
        # Overview table
        overview = self.current_analysis['overview']
        overview_table = Table(title="Spending Overview", show_header=True, header_style="bold blue")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        
        overview_display = {
            'Total Spending': f"${overview['total_spending']}",
            'Transactions': overview['num_transactions'],
            'Avg Daily': f"${overview['avg_daily_spending']}",
            'Avg Transaction': f"${overview['avg_transaction_amount']}",
            'Time Period': f"{overview['date_range']['days']} days"
        }
        
        for metric, value in overview_display.items():
            overview_table.add_row(metric, str(value))
            
        self.console.print(overview_table)
        
        # Top categories table
        categories = self.current_analysis['category_analysis']['top_categories']
        cat_table = Table(title="Top Spending Categories", show_header=True, header_style="bold green")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Amount", style="green", justify="right")
        cat_table.add_column("Percentage", style="yellow", justify="right")
        cat_table.add_column("Frequency", style="blue", justify="right")
        
        for category, data in list(categories.items())[:5]:
            cat_table.add_row(
                category,
                f"${data['total']:.2f}",
                f"{data['percentage']:.1f}%",
                str(int(data['frequency']))
            )
            
        self.console.print(cat_table)
        
        # AI Insights
        insights_panel = Panel(
            Markdown(ai_insights),
            title="[bold green]🤖 AI Financial Insights[/bold green]",
            border_style="green"
        )
        
        self.console.print(insights_panel)
        
    def _show_visualizations_workflow(self):
        """Handle visualization display workflow."""
        if self.current_data is None:
            self.console.print("[red]Please load data first![/red]")
            return
            
        if self.analyzer is None:
            self.analyzer = SpendingAnalyzer(self.current_data)
            
        self.console.print("\n[bold cyan]📈 Creating Visualizations[/bold cyan]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating visualizations...", total=None)
                
                figs = self.analyzer.create_visualizations()
                
                progress.update(task, description="✅ Visualizations created!")
                
            # Show visualization options
            viz_menu = """
[bold]Available Visualizations:[/bold]

1. 🥧 Spending by Category (Pie Chart)
2. 📈 Spending Timeline (Line Chart)
3. 🔥 Category vs Weekday Heatmap
4. 📊 Weekday Spending Comparison
5. 📅 Monthly Spending Trend
6. 🌐 Open all in browser
7. ⬅️  Back to main menu
"""
            
            self.console.print(Panel(viz_menu, border_style="magenta"))
            
            choice = Prompt.ask(
                "Select visualization",
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="6"
            )
            
            if choice == "7":
                return
            elif choice == "6":
                # Open all visualizations
                for name, fig in figs.items():
                    fig.show()
                self.console.print("[green]All visualizations opened in browser![/green]")
            else:
                # Open specific visualization
                viz_names = list(figs.keys())
                if int(choice) <= len(viz_names):
                    selected_viz = viz_names[int(choice) - 1]
                    figs[selected_viz].show()
                    self.console.print(f"[green]Opened {selected_viz} in browser![/green]")
                    
        except Exception as e:
            self.console.print(f"[red]Error creating visualizations: {str(e)}[/red]")
            
    def _savings_simulation_workflow(self):
        """Handle savings simulation workflow."""
        if self.current_data is None:
            self.console.print("[red]Please load data first![/red]")
            return
            
        if self.analyzer is None:
            self.analyzer = SpendingAnalyzer(self.current_data)
            
        self.console.print("\n[bold cyan]💰 Savings Simulation[/bold cyan]")
        
        # Show available categories
        categories = sorted(self.current_data['category'].unique())
        
        cat_table = Table(title="Available Categories", show_header=False)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Total Spent", style="green", justify="right")
        
        for category in categories:
            total = self.current_data[self.current_data['category'] == category]['amount'].sum()
            cat_table.add_row(category, f"${total:.2f}")
            
        self.console.print(cat_table)
        
        # Get user input
        category = Prompt.ask("Enter category name", choices=categories)
        reduction = float(Prompt.ask("Enter reduction percentage", default="20"))
        
        try:
            simulation = self.analyzer.simulate_savings(category, reduction)
            
            # Show simulation results
            sim_table = Table(title=f"Savings Simulation: {category}", show_header=True, header_style="bold yellow")
            sim_table.add_column("Metric", style="cyan")
            sim_table.add_column("Value", style="green", justify="right")
            
            sim_table.add_row("Current Spending", f"${simulation['current_spending']:.2f}")
            sim_table.add_row("Reduction", f"{simulation['reduction_percentage']:.1f}%")
            sim_table.add_row("Potential Savings", f"${simulation['potential_savings']:.2f}")
            sim_table.add_row("Monthly Estimate", f"${simulation['monthly_savings_estimate']:.2f}")
            sim_table.add_row("Annual Estimate", f"${simulation['annual_savings_estimate']:.2f}")
            
            self.console.print(sim_table)
            
            # Get AI advice for savings
            if Confirm.ask("Get AI advice for this savings plan?"):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Generating savings advice...", total=None)
                    
                    advice = self.llm_agent.generate_savings_advice(simulation)
                    
                    progress.update(task, description="✅ Advice generated!")
                    
                advice_panel = Panel(
                    Markdown(advice),
                    title="[bold yellow]💡 Savings Advice[/bold yellow]",
                    border_style="yellow"
                )
                
                self.console.print(advice_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error in savings simulation: {str(e)}[/red]")
            
    def _check_ollama_setup(self):
        """Check and show Ollama setup status."""
        self.console.print("\n[bold cyan]🤖 Ollama Setup Status[/bold cyan]")
        
        status = self.llm_agent.check_ollama_status()
        
        status_table = Table(title="Ollama Status", show_header=True, header_style="bold blue")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        
        status_table.add_row(
            "Ollama Installed", 
            "✅ Yes" if status['ollama_installed'] else "❌ No"
        )
        status_table.add_row(
            "Ollama Running",
            "✅ Yes" if status['ollama_running'] else "❌ No"
        )
        status_table.add_row(
            "Model Available",
            "✅ Yes" if status['model_available'] else "❌ No"
        )
        
        if status['available_models']:
            status_table.add_row(
                "Available Models",
                ", ".join(status['available_models'])
            )
            
        self.console.print(status_table)
        
        if not status['ollama_installed'] or not status['ollama_running'] or not status['model_available']:
            setup_panel = Panel(
                Markdown(self.llm_agent.suggest_model_setup()),
                title="[bold red]Setup Instructions[/bold red]",
                border_style="red"
            )
            self.console.print(setup_panel)
            
    def _show_about(self):
        """Show about information."""
        about_text = """
# 🏦 FinanceGPT v1.0

A personal finance analyzer that uses local AI to provide spending insights.

## Created by:
- Data Analysis: Pandas, NumPy
- Visualizations: Plotly, Matplotlib
- AI Insights: Ollama (local LLM)
- Interface: Rich, Click

## Features:
- 📊 Comprehensive spending analysis
- 📈 Interactive visualizations
- 🤖 Local AI-powered insights
- 💰 Savings simulations
- 🔒 Privacy-focused (all data stays local)

## Support:
For issues or questions, check the README.md file.
"""
        
        about_panel = Panel(
            Markdown(about_text),
            title="[bold blue]About FinanceGPT[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(about_panel)
        
    def _exit_application(self):
        """Handle application exit."""
        self.console.print("\n[bold green]Thanks for using FinanceGPT! 💰[/bold green]")
        self.console.print("Remember: [italic]Small changes in spending habits can lead to big savings![/italic]")

@click.command()
@click.option('--sample', is_flag=True, help='Create sample data and exit')
@click.option('--file', '-f', help='CSV file to analyze directly')
def main(sample, file):
    """FinanceGPT - AI-powered personal finance analyzer."""
    
    if sample:
        # Just create sample data and exit
        output_path = create_sample_data()
        console.print(f"[green]Sample data created: {output_path}[/green]")
        return
        
    if file:
        # Load file directly and run analysis
        try:
            ui = FinanceGPTUI()
            ui.current_data = ui.data_loader.load_csv(file)
            ui.analyzer = SpendingAnalyzer(ui.current_data)
            ui._show_data_summary()
            ui._analyze_data_workflow()
            return
        except Exception as e:
            console.print(f"[red]Error analyzing file: {str(e)}[/red]")
            return
            
    # Run interactive UI
    ui = FinanceGPTUI()
    ui.run()

if __name__ == "__main__":
    main() 