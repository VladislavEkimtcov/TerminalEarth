from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from engine import GameState

console = Console()

def draw_map(state: GameState):
    def get_color(abbr):
        if abbr not in state.regions: return "white"
        status = state.regions[abbr].status_with_player
        if status == "Friendly": return "green"
        if status == "Hostile": return "red"
        return "yellow"

    map_str = f"""
         [{get_color('NT')}]NT[/{get_color('NT')}]      [{get_color('QLD')}]QLD[/{get_color('QLD')}]
      [{get_color('WA')}]WA[/{get_color('WA')}]
                 [{get_color('SA')}]SA[/{get_color('SA')}]   [{get_color('NSW')}]NSW[/{get_color('NSW')}]
                      [{get_color('VIC')}]VIC[/{get_color('VIC')}]
    """
    console.print(Panel(map_str, title="Map of AUSTRA-NULL", expand=False))

def show_status(state: GameState):
    console.print(Panel(f"[bold yellow]Player Resources:[/bold yellow] Wealth: {state.player_wealth} | Troops: {state.player_troops}", expand=False))
    
    table = Table(title=f"World State - {state.month} {state.year}")
    table.add_column("Region", style="cyan")
    table.add_column("Stability", justify="right")
    table.add_column("Status", style="magenta")
    table.add_column("Wealth", justify="right", style="yellow")
    table.add_column("Troops", justify="right", style="blue")

    for r in state.regions.values():
        color = "green" if r.stability > 70 else "yellow" if r.stability > 30 else "red"
        table.add_row(r.name, f"[{color}]{r.stability}[/{color}]", r.status_with_player, str(r.wealth), str(r.troops))

    console.print(table)

def show_history(state: GameState):
    if not state.history:
        return
    console.print("\n[bold underline]Recent History[/bold underline]")
    for h in state.history[-5:]:
        console.print(f"- {h}")
    console.print()

def main_menu(state: GameState):
    while True:
        console.clear()
        console.print(f"[bold blue]AUSTRA-NULL[/bold blue] - {state.month} {state.year}")
        draw_map(state)
        show_status(state)
        show_history(state)

        console.print("\n[bold]Commands:[/bold]")
        console.print("1. [green]Batch Actions & End Turn[/green]")
        console.print("2. [yellow]Chat with Nation[/yellow]")
        console.print("3. [cyan]Consult the Archives (Oracle)[/cyan]")
        console.print("4. [red]Reset Game[/red]")
        console.print("5. Quit")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            actions_str = Prompt.ask("Enter actions separated by ';' (e.g., Build factory; Send envoy)")
            actions = [a.strip() for a in actions_str.split(";") if a.strip()]
            if actions:
                with console.status("[bold green]Processing turn..."):
                    narrative = state.process_turn(actions)
                console.print(Panel(narrative, title="Turn Results", border_style="green"))
                Prompt.ask("Press Enter to continue")
        elif choice == "2":
            abbr = Prompt.ask("Enter region abbreviation (WA, NT, QLD, NSW, VIC, SA)")
            if abbr in state.regions:
                msg = Prompt.ask(f"Message to {state.regions[abbr].name}")
                with console.status("[bold yellow]Awaiting response..."):
                    response = state.chat_with_nation(abbr, msg)
                console.print(Panel(response, title=f"Response from {abbr}", border_style="yellow"))
                Prompt.ask("Press Enter to continue")
            else:
                console.print("[red]Invalid region.[/red]")
                Prompt.ask("Press Enter to continue")
        elif choice == "3":
            q = Prompt.ask("Ask the Oracle")
            with console.status("[bold cyan]Consulting archives..."):
                response = state.consult_oracle(q)
            console.print(Panel(response, title="The Oracle Speaks", border_style="cyan"))
            Prompt.ask("Press Enter to continue")
        elif choice == "4":
            confirm = Prompt.ask("Are you sure? (y/n)", choices=["y", "n"])
            if confirm == "y":
                start_date = Prompt.ask("Enter start date (e.g., January 2077)", default="January 2077")
                state.reset(start_date)
        elif choice == "5":
            break

