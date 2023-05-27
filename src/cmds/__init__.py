import click
from ..models.files import metadata, engine, async_create_all, async_drop_all
from ..werkzeug.async2sync import async2sync
from .run import cmd as run_cmd, algorithms_available
from pillow_heif import register_heif_opener

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
              default=['md5', 'visual'],
              help='hash algorithms to use',
              type=click.Choice(algorithms_available, case_sensitive=False),
              show_default=True)
def run(**kwargs):
    async2sync(async_create_all(engine))
    run_cmd(**kwargs)

@cli.command()
def cluster(**kwargs):
    #cluster_cmd(**kwargs)
    click.echo('Clustering')

@cli.command()
def dropdb(*args, **kwargs):
    async2sync(async_drop_all(engine))
    click.echo('Dropped the database')

cli.add_command(run)
cli.add_command(dropdb)