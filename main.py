from __future__ import annotations

import json

import click
from dotenv import load_dotenv

from docpipe import Pipeline


load_dotenv()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False, path_type=str), required=False)
@click.option("--dir", "dir_path", type=click.Path(exists=True, file_okay=False, path_type=str), required=False)
@click.option("--config", "config_path", default="config.yaml", show_default=True)
def ingest(file_path: str | None, dir_path: str | None, config_path: str) -> None:
    if bool(file_path) == bool(dir_path):
        raise click.ClickException("Use exactly one of --file or --dir")

    pipe = Pipeline(config=config_path)
    try:
        target = file_path if file_path else dir_path
        count = pipe.ingest(target)
        click.echo(f"Ingested files: {count}")
    finally:
        pipe.close()


@cli.command()
@click.argument("query_text", type=str)
@click.option("--top-k", default=None, type=int)
@click.option("--config", "config_path", default="config.yaml", show_default=True)
def query(query_text: str, top_k: int | None, config_path: str) -> None:
    pipe = Pipeline(config=config_path)
    try:
        results = pipe.search(query_text, top_k=top_k)
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    finally:
        pipe.close()


@cli.command()
@click.option("--config", "config_path", default="config.yaml", show_default=True)
def stats(config_path: str) -> None:
    pipe = Pipeline(config=config_path)
    try:
        click.echo(json.dumps(pipe.stats(), indent=2))
    finally:
        pipe.close()


if __name__ == "__main__":
    cli()
