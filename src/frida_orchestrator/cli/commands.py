import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.command()
def scan():
    """Scan for connected devices (USB/Network)."""
    from frida_orchestrator.core.device_manager import DeviceManager
    
    console.print("[bold cyan]Scanning for devices...[/bold cyan]")
    
    manager = DeviceManager()
    try:
        devices = manager.list_devices()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("[yellow]Hint: Add 'platform-tools' to your PATH or install Android SDK.[/yellow]")
        return
    
    if not devices:
        console.print("[yellow]No devices detected.[/yellow]")
        return

    table = Table(title="Detected Devices")
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Model", style="magenta")
    table.add_column("Platform", justify="right", style="green")
    
    for device in devices:
        table.add_row(device.device_id, device.model, device.platform.capitalize())
    
    console.print(table)

@click.command()
@click.argument('device_id')
def profile(device_id):
    """Analyze a device to determine Frida compatibility."""
    from frida_orchestrator.core.profiler import DeviceProfiler
    from frida_orchestrator.core.device_manager import Device
    
    console.print(f"[bold blue]Profiling device {device_id}...[/bold blue]")
    
    # We need a temporary Device object to pass to the profiler
    # In a full flow, we might fetch this from DeviceManager to get connection type etc.
    # For now, assuming Android/USB is fine for the MVP CLI flow if we just pass the ID.
    # But ideally we detect platform first. Let's default to Android for this command's laziness 
    # or quick check.
    # BETTER: Retrieve from manager first.
    from frida_orchestrator.core.device_manager import DeviceManager
    manager = DeviceManager()
    devices = manager.list_devices()
    target_device = next((d for d in devices if d.device_id == device_id), None)
    
    if not target_device:
        console.print(f"[red]Device {device_id} not found![/red]")
        return
        
    profiler = DeviceProfiler()
    data = profiler.profile(target_device)
    
    console.print("\n[bold]Device Profile Generated:[/bold]")
    table = Table(show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("OS Type", data.os_name)
    table.add_row("OS Version", data.os_version)
    table.add_row("CPU Arch (ABI)", data.abi)
    table.add_row("Rooted/Jailbroken", str(data.is_rooted))
    if data.ro_build_fingerprint:
        table.add_row("Fingerprint", data.ro_build_fingerprint)
        
    console.print(table)

@click.command()
@click.argument('device_id')
def prepare(device_id):
    """Download and install the correct Frida server."""
    from frida_orchestrator.core.device_manager import DeviceManager
    from frida_orchestrator.core.profiler import DeviceProfiler
    from frida_orchestrator.core.frida_manager import FridaManager

    console.print(f"[bold yellow]Preparing Frida for device {device_id}...[/bold yellow]")
    
    # 1. Get Device
    manager = DeviceManager()
    devices = manager.list_devices()
    target_device = next((d for d in devices if d.device_id == device_id), None)
    
    if not target_device:
        console.print(f"[red]Device {device_id} not found![/red]")
        return

    # 2. Get Profile
    profiler = DeviceProfiler()
    profile = profiler.profile(target_device)
    console.print(f"Detected: {profile.os_name} {profile.os_version} ({profile.abi})")

    # 3. Install
    fm = FridaManager()
    success = fm.ensure_frida_installed(target_device, profile)
    
    if success:
        console.print("[bold green]Frida Server setup complete![/bold green]")
    else:
        console.print("[bold red]Setup failed.[/bold red]")
