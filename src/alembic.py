    """
    
    Sources: 
    https://stackoverflow.com/a/54402853
    """

from alembic.config import Config
from alembic import command

def run_migrations(script_location: str, dsn: str) -> None:
    LOG.info('Running DB migrations in %r on %r', script_location, dsn)
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', dsn)
    command.upgrade(alembic_cfg, 'head')