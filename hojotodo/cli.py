from pathlib import Path
from typing import Optional, List

import typer

from hojotodo import __version__, __app_name__, ERRORS, config, database, hojotodo

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="to-do database path?"
    )
):
    """Initialize the application"""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f"Creating config file failed with '{ERRORS[app_init_error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"The to-do database is {db_path}", fg=typer.colors.GREEN)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} version {__version__}")
        raise typer.Exit()


@app.callback()
def main(version: Optional[bool] = typer.Option(
    None,
        "--version",
        "-v",
        help="How the application's version and exit",
        callback=_version_callback,
        is_eager=True
)) -> None:
    return


def get_todoer() -> hojotodo.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "hojotodo init"', typer.colors.RED)
        raise typer.Exit(1)
    if db_path.exists():
        return hojotodo.Todoer(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "rptodo init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.command()
def add(
    description: List[str] = typer.Argument(...),
    priority: int = typer.Option(2, "--priority", "-p", min=1, max=3),
) -> None:
    """Add a new todo"""
    todoer = get_todoer()
    todo, error = todoer.add(description, priority)
    if error:
        typer.secho(
            f'Adding to-do failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do: "{todo['Description']}" was added """
            f"""with priority: {priority}""",
            fg=typer.colors.GREEN,
        )
