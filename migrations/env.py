import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import Base  # Certifique-se de que você está importando o objeto Base corretamente do seu arquivo de modelos.


# Interpretar o arquivo de configuração para o logging
fileConfig(context.config.config_file_name)
logger = logging.getLogger('alembic.env')

# Configuração do banco de dados
config = context.config

# Definindo a URL do banco de dados diretamente (ajuste conforme seu banco de dados)
config.set_main_option('sqlalchemy.url', 'mysql+pymysql://root:12345678@localhost:3306/meu_banco')

# Metadados dos seus modelos
target_metadata = Base.metadata  # Base é a classe base de seus modelos SQLAlchemy

def run_migrations_offline():
    """Executar as migrações no modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executar as migrações no modo online."""
    # Criar a engine de conexão
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Verificar se estamos no modo offline ou online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
