import logging
import click
from .database import Database
from .yledl import yledl_metadata, yledl_download, get_title

BASE_URL = "https://areena.yle.fi/"


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
@click.argument("url")
def add(freq, url: str):
    """Add series to the database."""
    db = Database()
    if url.startswith(BASE_URL):
        program_id = url.split("/")[-1]
    else:
        program_id = url
        url = BASE_URL + program_id
    title = get_title(url)
    if db.add(program_id, url, title, freq):
        click.echo(f'Added "{title}"')
    else:
        raise click.ClickException()


@cli.command()
@click.argument("url")
def remove(url: str):
    """Remove series to the database."""
    db = Database()
    if url.startswith(BASE_URL):
        program_id = url.split("/")[-1]
    else:
        program_id = url
    db.remove(program_id)


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
                click.echo("--> downloaded once")
                continue

            if series["freq"] == "hourly" and series["days_since_check"] < 1:
                click.echo(
                    f"--> downloaded {round(series['days_since_check']*60)} minutes ago"
                )
                continue

            if series["freq"] == "daily" and series["days_since_check"] < 23:
                click.echo(
                    f"--> downloaded {round(series['days_since_check'])} hours ago"
                )
                continue

            if series["freq"] == "weekly" and series["days_since_check"] < 23 * 7:
                click.echo(
                    f"--> downloaded {round(series['days_since_check']/24)} days ago"
                )
                continue

        metadata = yledl_metadata(series["webpage"])
        total = len(metadata)

        all_ok = True
        for i, episode in enumerate(metadata):
            if db.episode_exists(episode["program_id"]):
                click.echo(
                    f"  Episode {i+1}/{total}: {episode['title']} exists, skipping"
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
                ok = False

        if all_ok:
            db.update(series["program_id"])
