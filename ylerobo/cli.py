import logging
import click
from .database import Database
from .yledl import (
    yledl_metadata,
    yledl_download,
    get_title,
    get_program_id_and_url,
)


@click.group()
@click.option("--verbose", "-v", is_flag=True)
@click.option("--dryrun", "-n", is_flag=True)
@click.pass_context
def cli(ctx, verbose, dryrun):
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        level=logging.DEBUG if verbose else logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["dryrun"] = dryrun


@cli.command()
@click.option("--force", is_flag=True)
def init(force: bool):
    """Initialize database. Give --force to recreate database."""
    db = Database()
    if not db.init(force):
        raise click.ClickException()


@cli.command()
@click.option("--once", "freq", flag_value="once")
@click.option("--hourly", "freq", flag_value="hourly")
@click.option("--daily", "freq", flag_value="daily")
@click.option("--weekly", "freq", flag_value="weekly", default=True)
@click.argument("program")
def add(freq, program: str):
    """Add series to the database."""
    db = Database()
    program_id, url = get_program_id_and_url(program)
    title = get_title(url)
    if db.add(program_id, url, title, freq):
        click.echo(f'Added "{title}"')
    else:
        del db  # For pytest, otherwise SQLite connection remains
        raise click.ClickException("Failed to add")


@cli.command()
@click.argument("program")
def remove(program: str):
    """Remove series to the database."""
    db = Database()
    program_id, _ = get_program_id_and_url(program)
    if db.remove(program_id):
        click.echo(f'Removed "{program}"')
    else:
        del db  # For pytest, otherwise SQLite connection remains
        raise click.ClickException("Failed to remove")


@cli.command()
@click.option("-r", is_flag=True)
def list(r):
    """Lists series to the database. If -r is given, lists also downloaded episodes."""
    db = Database()
    for series in db.list():
        click.echo(
            f"# Series {series['program_id']} "
            f"- {series['title']} "
            f"({series['freq']}, last {series['last_check']})"
        )
        if not r:
            continue
        for episode in db.episode_list(series["program_id"]):
            click.echo(f"  Episode: {episode['program_id']} - {episode['title']}")


@cli.command()
@click.option("--force", is_flag=True)
@click.argument("program_id", required=False)
@click.pass_context
def download(ctx, force, program_id):
    """Download episodes. All episodes that are found but does not exist in the
    database will be downloaded."""
    db = Database()
    for series in db.list():
        if program_id and program_id != series["program_id"]:
            continue
        click.echo(f"# Series {series['program_id']} - {series['title']}")

        if series["last_check"] and not force:
            if series["freq"] == "once":
                if ctx.obj["verbose"]:
                    click.echo("--> downloaded once")
                continue

            mins = round(series["days_since_check"] * 24 * 60)
            if series["freq"] == "hourly" and mins < 55:
                if ctx.obj["verbose"]:
                    click.echo(f"--> downloaded {mins} minutes ago")
                continue

            hours = round(series["days_since_check"] * 24)
            if series["freq"] == "daily" and hours < 24:
                if ctx.obj["verbose"]:
                    click.echo(f"--> downloaded {hours} hours ago")
                continue

            days = round(series["days_since_check"])
            if series["freq"] == "weekly" and days < 7:
                if ctx.obj["verbose"]:
                    click.echo(f"--> downloaded {days} days ago")
                continue

        metadata = yledl_metadata(series["webpage"])
        total = len(metadata)

        all_ok = True
        for i, episode in enumerate(metadata):
            if db.episode_exists(episode["program_id"]):
                # The episode has been downloaded previously.
                click.echo(
                    f"  Episode {i+1}/{total}: {episode['title']} already downloaded"
                )
                continue

            click.echo(f"- {episode['title']} downloading")
            if ctx.obj["dryrun"]:
                ok = True
            else:
                ok = yledl_download(episode["webpage"])

            if ok:
                db.episode_add(series["program_id"], episode)
            else:
                click.echo("Failed to download.")
                all_ok = False

        if all_ok:
            # Mark series succesfully downloaded. This sets the next
            # download to be tried after the specified interval.
            db.update(series["program_id"])


@cli.command()
@click.option("--debug", is_flag=True)
def serve(debug):
    """Run web service."""
    from . import service

    service.serve(debug=debug)
