"""
Rich Analysis Formatter
Provides beautiful Rich formatting for statistics and cleaning operations output.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from typing import List, Dict, Tuple, Optional, Any
from .config import CONFIG

console = Console()

def create_statistics_panel(stats: Dict[str, Any], column_name: str) -> Panel:
    """Create a Rich panel displaying column statistics."""
    
    content = []
    content.append(f"[bold blue]Column:[/bold blue] [cyan]{column_name}[/cyan]")
    content.append(f"[bold green]Data Type:[/bold green] [yellow]{stats.get('data_type', 'unknown')}[/yellow]")
    content.append("")
    
    # Basic statistics
    content.append("[bold]Basic Statistics:[/bold]")
    content.append(f"  • Total Values: [cyan]{stats.get('total_values', 0)}[/cyan]")
    content.append(f"  • Non-empty Values: [green]{stats.get('non_empty_values', 0)}[/green]")
    content.append(f"  • Empty Values: [red]{stats.get('empty_values', 0)}[/red]")
    content.append(f"  • Unique Values: [blue]{stats.get('unique_values', 0)}[/blue]")
    content.append(f"  • Missing Percentage: [orange]{stats.get('missing_percentage', 0):.1f}%[/orange]")
    
    # Type-specific statistics
    data_type = stats.get('data_type', 'unknown')
    
    if data_type == 'numeric':
        content.append("")
        content.append("[bold]Numeric Statistics:[/bold]")
        if stats.get('min') is not None:
            content.append(f"  • Min: [green]{stats.get('min'):.2f}[/green]")
            content.append(f"  • Max: [green]{stats.get('max'):.2f}[/green]")
            content.append(f"  • Mean: [green]{stats.get('mean'):.2f}[/green]")
            content.append(f"  • Median: [green]{stats.get('median'):.2f}[/green]")
            content.append(f"  • Std Dev: [green]{stats.get('std_dev'):.2f}[/green]")
            content.append(f"  • Q1: [green]{stats.get('q1'):.2f}[/green]")
            content.append(f"  • Q3: [green]{stats.get('q3'):.2f}[/green]")
            content.append(f"  • Range: [green]{stats.get('range'):.2f}[/green]")
    
    elif data_type == 'categorical':
        content.append("")
        content.append("[bold]Categorical Statistics:[/bold]")
        most_common = stats.get('most_common_value')
        if most_common:
            content.append(f"  • Most Common: [green]'{most_common[0]}'[/green] ([cyan]{most_common[1]}[/cyan] times)")
        
        least_common = stats.get('least_common_value')
        if least_common:
            content.append(f"  • Least Common: [red]'{least_common[0]}'[/red] ([cyan]{least_common[1]}[/cyan] times)")
        
        entropy = stats.get('entropy')
        if entropy is not None:
            content.append(f"  • Entropy: [blue]{entropy:.3f}[/blue]")
    
    return Panel(
        "\n".join(content),
        title=f"[bold blue]Statistics for {column_name}[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def create_data_quality_panel(quality_report: Dict[str, Any]) -> Panel:
    """Create a Rich panel displaying data quality metrics."""
    
    content = []
    
    # Overall quality score
    overall_score = quality_report.get('overall_quality_score', 0)
    score_color = "green" if overall_score >= 0.8 else "yellow" if overall_score >= 0.6 else "red"
    content.append(f"[bold]Overall Quality Score:[/bold] [{score_color}]{overall_score:.1%}[/{score_color}]")
    content.append("")
    
    # Individual scores
    content.append("[bold]Quality Metrics:[/bold]")
    completeness = quality_report.get('completeness_score', 0)
    completeness_color = "green" if completeness >= 0.8 else "yellow" if completeness >= 0.6 else "red"
    content.append(f"  • Completeness: [{completeness_color}]{completeness:.1%}[/{completeness_color}]")
    
    consistency = quality_report.get('consistency_score', 0)
    consistency_color = "green" if consistency >= 0.8 else "yellow" if consistency >= 0.6 else "red"
    content.append(f"  • Consistency: [{consistency_color}]{consistency:.1%}[/{consistency_color}]")
    
    uniqueness = quality_report.get('uniqueness_score', 0)
    uniqueness_color = "green" if uniqueness >= 0.8 else "yellow" if uniqueness >= 0.6 else "red"
    content.append(f"  • Uniqueness: [{uniqueness_color}]{uniqueness:.1%}[/{uniqueness_color}]")
    
    content.append("")
    content.append("[bold]Data Summary:[/bold]")
    content.append(f"  • Total Rows: [cyan]{quality_report.get('total_rows', 0)}[/cyan]")
    content.append(f"  • Total Columns: [cyan]{quality_report.get('total_columns', 0)}[/cyan]")
    content.append(f"  • Total Cells: [cyan]{quality_report.get('total_cells', 0)}[/cyan]")
    content.append(f"  • Empty Cells: [red]{quality_report.get('empty_cells', 0)}[/red]")
    content.append(f"  • Duplicate Rows: [orange]{quality_report.get('duplicate_rows', 0)}[/orange]")
    content.append(f"  • Inconsistent Lengths: [orange]{quality_report.get('inconsistent_lengths', 0)}[/orange]")
    
    return Panel(
        "\n".join(content),
        title="[bold blue]Data Quality Report[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def create_correlation_table(correlation_matrix: Dict[str, Dict[str, float]]) -> Table:
    """Create a Rich table displaying correlation matrix."""
    
    if not correlation_matrix:
        return Table(title="[bold red]No numeric columns found for correlation analysis[/bold red]")
    
    table = Table(
        title="[bold blue]Correlation Matrix[/bold blue]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    
    # Add columns
    columns = list(correlation_matrix.keys())
    table.add_column("", style="dim", width=8)
    for col in columns:
        table.add_column(col, justify="center", width=12)
    
    # Add rows
    for col1 in columns:
        row_data = [col1]
        for col2 in columns:
            corr_value = correlation_matrix[col1][col2]
            
            # Color code based on correlation strength
            if abs(corr_value) >= 0.7:
                color = "red"
            elif abs(corr_value) >= 0.5:
                color = "yellow"
            elif abs(corr_value) >= 0.3:
                color = "blue"
            else:
                color = "dim"
            
            row_data.append(f"[{color}]{corr_value:.3f}[/{color}]")
        
        table.add_row(*row_data)
    
    return table

def create_outliers_panel(outliers: List[Tuple[int, float]], column_name: str) -> Panel:
    """Create a Rich panel displaying outliers."""
    
    if not outliers:
        content = "[bold green]✓ No outliers detected[/bold green]"
    else:
        content = []
        content.append(f"[bold red]Found {len(outliers)} outliers:[/bold red]")
        content.append("")
        
        for row_idx, value in outliers[:10]:  # Show first 10 outliers
            content.append(f"  • Row {row_idx}: [red]{value}[/red]")
        
        if len(outliers) > 10:
            content.append(f"  ... and {len(outliers) - 10} more")
    
    return Panel(
        content if isinstance(content, str) else "\n".join(content),
        title=f"[bold red]Outliers in {column_name}[/bold red]",
        border_style="red",
        padding=(1, 2)
    )

def create_distribution_table(distribution: Dict[str, Any]) -> Table:
    """Create a Rich table displaying value distribution."""
    
    table = Table(
        title=f"[bold blue]Value Distribution: {distribution.get('column_name', 'Unknown')}[/bold blue]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("Value", style="cyan", width=20)
    table.add_column("Count", style="green", justify="right", width=10)
    table.add_column("Percentage", style="yellow", justify="right", width=12)
    
    top_values = distribution.get('top_values', [])
    for value, count, percentage in top_values:
        table.add_row(
            str(value)[:18] + "..." if len(str(value)) > 20 else str(value),
            str(count),
            f"{percentage:.1f}%"
        )
    
    return table

def create_cleaning_summary_panel(cleaning_summary: Dict[str, Any]) -> Panel:
    """Create a Rich panel displaying cleaning operations summary."""
    
    content = []
    
    content.append(f"[bold blue]Cleaning Summary:[/bold blue]")
    content.append(f"  • Total Operations: [cyan]{cleaning_summary.get('total_operations', 0)}[/cyan]")
    content.append(f"  • Original Rows: [yellow]{cleaning_summary.get('original_row_count', 0)}[/yellow]")
    content.append(f"  • Final Rows: [green]{cleaning_summary.get('final_row_count', 0)}[/green]")
    
    operations = cleaning_summary.get('operations', [])
    if operations:
        content.append("")
        content.append("[bold]Operations Performed:[/bold]")
        for op in operations[-5:]:  # Show last 5 operations
            content.append(f"  • {op.get('operation', 'Unknown')}: {op.get('details', '')}")
    
    return Panel(
        "\n".join(content),
        title="[bold blue]Data Cleaning Summary[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def display_statistics_rich(analyzer, columns: Optional[List[str]] = None, show_correlations: bool = False):
    """Display comprehensive statistics using Rich formatting."""
    
    if not columns:
        columns = analyzer.headers
    
    # Show data quality report first
    quality_report = analyzer.get_data_quality_report()
    quality_panel = create_data_quality_panel(quality_report)
    console.print(quality_panel)
    console.print()
    
    # Show individual column statistics
    for column in columns:
        if column in analyzer.headers:
            stats = analyzer.get_column_statistics(column)
            stats_panel = create_statistics_panel(stats, column)
            console.print(stats_panel)
            console.print()
    
    # Show correlations if requested
    if show_correlations:
        correlation_matrix = analyzer.get_correlation_matrix()
        if correlation_matrix:
            correlation_table = create_correlation_table(correlation_matrix)
            console.print(correlation_table)
            console.print()

def display_cleaning_operations_rich(cleaner, operations: List[str]):
    """Display cleaning operations using Rich formatting."""
    
    console.print(Panel(
        "[bold blue]Starting Data Cleaning Operations[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()
    
    # Show progress for operations
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing cleaning operations...", total=len(operations))
        
        for operation in operations:
            progress.update(task, description=f"Performing: {operation}")
            # Here you would actually perform the operation
            # For now, we'll just simulate progress
            progress.advance(task)
    
    # Show cleaning summary
    summary = cleaner.get_cleaning_summary()
    summary_panel = create_cleaning_summary_panel(summary)
    console.print(summary_panel)
    console.print()

def show_analysis_menu():
    """Display an interactive menu for analysis options."""
    
    menu_content = [
        "[bold blue]CSVise Analysis Options:[/bold blue]",
        "",
        "[bold]1.[/bold] Column Statistics",
        "[bold]2.[/bold] Data Quality Report", 
        "[bold]3.[/bold] Correlation Analysis",
        "[bold]4.[/bold] Outlier Detection",
        "[bold]5.[/bold] Value Distribution",
        "[bold]6.[/bold] All Analysis",
        "",
        "[bold]Cleaning Operations:[/bold]",
        "[bold]7.[/bold] Remove Duplicates",
        "[bold]8.[/bold] Normalize Whitespace",
        "[bold]9.[/bold] Standardize Case",
        "[bold]10.[/bold] Fill Missing Values",
        "[bold]11.[/bold] Remove Empty Rows",
        "",
        "[bold]0.[/bold] Exit"
    ]
    
    console.print(Panel(
        "\n".join(menu_content),
        title="[bold blue]CSVise Analysis & Cleaning Menu[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    ))
