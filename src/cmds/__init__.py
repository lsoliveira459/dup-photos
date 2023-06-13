import click
from pillow_heif import register_heif_opener

from src.hashers import enabled_hashers

from ..models import async_create_all, async_drop_all, engine
from ..werkzeug.async2sync import await_
from .run import cmd as run_cmd

register_heif_opener()

@click.group()
@click.version_option()
@click.option('-v', '--verbose',
              count=True,
              help='v = PROGRESS, vv = INFO, vvv = DEBUG',)
def cli(*args, **kwargs):
    pass

@cli.command()
@click.option('-d', '--directory',
              multiple=True,
              default=['.'],
              help='search directories',
              type=click.Path(exists=True, file_okay=False, readable=True,),
              show_default=True)
@click.option('-h', '--hash',
              multiple=True,
              default=['hashlib.md5', 'dhash.dhash'],
              help='hash algorithms to use',
              type=click.Choice(enabled_hashers.keys(), case_sensitive=False),
              show_default=True)
@click.option('-r', '--reset',
              is_flag=True,
              default=False,
              help='force reset database',
              show_default=True)
def run(**kwargs):
    if kwargs.pop('reset', False):
        await_(async_drop_all(engine))
        click.echo('Dropped the database')
    await_(async_create_all(engine))
    run_cmd(**kwargs)

@cli.command()
def cluster(**kwargs):
    #cluster_cmd(**kwargs)
    click.echo('Clustering')

@cli.command()
def dropdb(*args, **kwargs):
    await_(async_drop_all(engine))
    click.echo('Dropped the database')

cli.add_command(run)
cli.add_command(dropdb)