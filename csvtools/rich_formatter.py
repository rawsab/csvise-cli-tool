from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import box
from typing import List, Tuple, Optional
from .config import CONFIG
from .utils import log_verbose
from .cleaning import apply_string_case

console = Console()

def create_rich_table(rows: List[List[str]], expected_types: List[str], 
                     start_index: int = 1, num_rows: Optional[int] = None) -> Table:
    """Create a Rich table from CSV data with enhanced formatting."""
    
    if not rows:
        return Table(title="Empty CSV File")
    
    # Determine number of rows to display
    if num_rows is None:
        num_rows = len(rows) - start_index
    
    # Create table with appropriate styling
    table = Table(
        title="[bold blue]CSV Data Display[/bold blue]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    
    # Add row number column
    table.add_column("#", style="dim", width=4, justify="right")
    
    # Add data columns with type-based styling
    for i, header in enumerate(rows[0]):
        column_style = "cyan"
        if expected_types and i < len(expected_types):
            if expected_types[i] == "int":
                column_style = "green"
            elif expected_types[i] == "float":
                column_style = "yellow"
            elif expected_types[i] == "bool":
                column_style = "magenta"
        
        table.add_column(
            apply_string_case(header, CONFIG["string_case"]), 
            style=column_style,
            justify="left"
        )
    
    # Add rows with enhanced formatting
    end_index = min(start_index + num_rows, len(rows))
    for row_idx, row in enumerate(rows[start_index:end_index], start=start_index):
        # Create row with row number
        formatted_row = [str(row_idx)]
        
        # Add data cells with type-based formatting
        for i, cell in enumerate(row):
            if i < len(expected_types) and expected_types[i]:
                # Apply type-specific formatting
                if expected_types[i] == "int" and cell.isdigit():
                    formatted_cell = f"[green]{cell}[/green]"
                elif expected_types[i] == "float":
                    try:
                        float_val = float(cell)
                        formatted_cell = f"[yellow]{cell}[/yellow]"
                    except ValueError:
                        formatted_cell = f"[red]{cell}[/red]"
                elif expected_types[i] == "bool":
                    if cell.lower() in ['true', 'false']:
                        formatted_cell = f"[magenta]{cell}[/magenta]"
                    else:
                        formatted_cell = f"[red]{cell}[/red]"
                else:
                    formatted_cell = cell
            else:
                formatted_cell = cell
            
            formatted_row.append(formatted_cell)
        
        table.add_row(*formatted_row)
    
    return table

def create_validation_panel(incorrect_length_rows: List[Tuple[int, int]], 
                           type_mismatches: List[Tuple[int, int, str, str]], 
                           expected_length: int) -> Optional[Panel]:
    """Create a Rich panel showing validation issues."""
    
    if not incorrect_length_rows and not type_mismatches:
        return None
    
    content = []
    
    if incorrect_length_rows:
        content.append("[bold red]Rows with Incorrect Length:[/bold red]")
        for row_number, actual_length in incorrect_length_rows:
            content.append(f"  • Row {row_number}: Found {actual_length} columns, expected {expected_length}")
        content.append("")
    
    if type_mismatches:
        content.append("[bold orange]Type Mismatches:[/bold orange]")
        for row_number, column, actual_type, expected_type in type_mismatches:
            content.append(f"  • Row {row_number}, Column {column}: [red]{actual_type}[/red] → [green]{expected_type}[/green]")
        content.append("")
    
    content.append(f"[bold]Summary:[/bold] {len(incorrect_length_rows)} length issues, {len(type_mismatches)} type mismatches")
    
    return Panel(
        "\n".join(content),
        title="[bold red]Data Validation Issues[/bold red]",
        border_style="red",
        padding=(1, 2)
    )

def create_stats_panel(rows: List[List[str]], delimiter: str) -> Panel:
    """Create a Rich panel showing CSV statistics."""
    
    total_rows = len(rows)
    total_columns = len(rows[0]) if rows else 0
    data_rows = total_rows - 1  # Exclude header
    
    stats_content = [
        f"[bold blue]File Statistics:[/bold blue]",
        f"  • Total Rows: [cyan]{total_rows}[/cyan]",
        f"  • Data Rows: [cyan]{data_rows}[/cyan]",
        f"  • Columns: [cyan]{total_columns}[/cyan]",
        f"  • Delimiter: [yellow]'{delimiter}'[/yellow]",
        "",
        f"[bold green]Data Quality:[/bold green]",
        f"  • Complete Rows: [green]{data_rows}[/green]",
    ]
    
    return Panel(
        "\n".join(stats_content),
        title="[bold blue]CSV Overview[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def format_and_output_csv_rich(rows: List[List[str]], expected_types: List[str], 
                              col_widths: List[int], display_table: bool, 
                              save_to_file: Optional[str], debug_mode: bool,
                              incorrect_length_rows: List[Tuple[int, int]], 
                              type_mismatches: List[Tuple[int, int, str, str]],
                              delimiter: str = ",") -> None:
    """Enhanced CSV formatter using Rich for beautiful CLI output."""
    
    expected_length = len(rows[0]) if rows else 0
    
    # Create console for output
    if save_to_file:
        # For file output, we'll capture the console output
        with console.capture() as capture:
            _render_rich_output(rows, expected_types, display_table, debug_mode, 
                              incorrect_length_rows, type_mismatches, delimiter)
        
        # Save captured output to file
        with open(save_to_file, 'w') as file:
            file.write(capture.get())
        console.print(f"[green]Output saved to {save_to_file}[/green]")
    else:
        # Direct console output
        _render_rich_output(rows, expected_types, display_table, debug_mode,
                          incorrect_length_rows, type_mismatches, delimiter)

def _render_rich_output(rows: List[List[str]], expected_types: List[str], 
                       display_table: bool, debug_mode: bool,
                       incorrect_length_rows: List[Tuple[int, int]], 
                       type_mismatches: List[Tuple[int, int, str, str]],
                       delimiter: str) -> None:
    """Render the Rich output components."""
    
    expected_length = len(rows[0]) if rows else 0
    
    # Show processing message
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task("Processing CSV data...", total=None)
    
    # Display statistics panel
    if rows:
        stats_panel = create_stats_panel(rows, delimiter)
        console.print(stats_panel)
        console.print()  # Add spacing
    
    # Display the main table
    if display_table and rows:
        start_index = CONFIG["start_index"]
        num_rows_to_print = CONFIG["num_rows_to_print"] or (len(rows) - start_index)
        
        table = create_rich_table(rows, expected_types, start_index, num_rows_to_print)
        console.print(table)
        console.print()  # Add spacing
    
    # Display validation issues if in debug mode
    if debug_mode and (incorrect_length_rows or type_mismatches):
        validation_panel = create_validation_panel(
            incorrect_length_rows, type_mismatches, expected_length
        )
        if validation_panel:
            console.print(validation_panel)
    
    # Show success message if no issues
    elif debug_mode and not incorrect_length_rows and not type_mismatches:
        console.print(Panel(
            "[bold green]✓ No data validation issues found![/bold green]",
            border_style="green",
            padding=(1, 2)
        ))

def show_file_info(filename: str) -> None:
    """Display file information with Rich formatting."""
    
    console.print(Panel(
        f"[bold blue]Processing:[/bold blue] [cyan]{filename}[/cyan]",
        title="[bold blue]CSVise[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()

def show_error_message(message: str) -> None:
    """Display error messages with Rich formatting."""
    
    console.print(Panel(
        f"[bold red]{message}[/bold red]",
        title="[bold red]Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))

def show_success_message(message: str) -> None:
    """Display success messages with Rich formatting."""
    
    console.print(Panel(
        f"[bold green]{message}[/bold green]",
        title="[bold green]Success[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
