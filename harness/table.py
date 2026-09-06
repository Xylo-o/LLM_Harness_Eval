from rich.console import Console
from rich.table import Table

def print_table(results):
    table = Table(title="Results")
    table.add_column("Case")
    table.add_column("Scorer")
    table.add_column("Result")

    for case in results:
        if case.error:
            table.add_row(case.case_key, "-", f"[yellow]ERROR[/yellow] {case.error[:60]}")
            continue
        for score in case.scores:
            status = "[green]PASS[/green]" if score.passed else "[red]FAIL[/red]"
            table.add_row(case.case_key, score.scorer_name, status)

    Console().print(table)