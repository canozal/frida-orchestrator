import click
from rich.console import Console
from frida_orchestrator.cli.commands import scan, prepare, profile

console = Console()

@click.group()
def cli():
    """Frida Orchestrator: Automated Mobile Security Environment Setup."""
    pass

cli.add_command(scan)
cli.add_command(prepare)
cli.add_command(profile)

if __name__ == "__main__":
    cli()
