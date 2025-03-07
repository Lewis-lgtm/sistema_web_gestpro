from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Definindo a base do SQLAlchemy
Base = declarative_base()

# Definindo o caminho do banco de dados (SQLite local)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = 'mysql+pymysql://root:12345678@localhost:3306/meu_banco'


# Criando a engine do banco de dados
engine = create_engine(DATABASE_URL, echo=True)

# Criando a classe de sessão para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Tabela Pessoa (Agora inclui campo 'perfil')
class Pessoa(Base):
    __tablename__ = 'pessoa'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)  # Adicionando o campo senha
    nivel_senioridade = Column(String(50), nullable=False)
    custo_por_hora = Column(Numeric(5, 2), nullable=False)
    perfil = Column(String(50), nullable=False)  # 'admin', 'gerente', 'colaborador'

    tarefas = relationship('Tarefa', backref='responsavel', lazy=True)

    def __repr__(self):
        return f'<Pessoa {self.email}>'

# Tabela StatusTarefa
class StatusTarefa(Base):
    __tablename__ = 'status_tarefa'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)

    tarefas = relationship('Tarefa', backref='status_tarefa', lazy=True)

    def __repr__(self):
        return f'<StatusTarefa {self.titulo}>'

# Tabela TipoTarefa
class TipoTarefa(Base):
    __tablename__ = 'tipo_tarefa'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    nome = Column(String(100), nullable=False)
    
    pessoa_id = Column(Integer, ForeignKey('pessoa.id'), nullable=False)  
    status_tarefa_id = Column(Integer, ForeignKey('status_tarefa.id'), nullable=False)  
    servico_projeto_id = Column(Integer, ForeignKey('servico_projeto.id'), nullable=True)

    pessoa = relationship('Pessoa', backref='tipo_tarefas')
    status_tarefa = relationship('StatusTarefa', backref='tipo_tarefas')
    servico_projeto = relationship('ServicoProjeto', backref='tipo_tarefas', lazy=True)

    lancamentos_horas = relationship('LancamentoHoras', backref='tipo_tarefa_lancamentos', lazy=True)

    def __repr__(self):
        return f'<TipoTarefa {self.nome}>'

# Tabela TipoServico (novo modelo)
class TipoServico(Base):
    __tablename__ = 'tipo_servico'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    horas_fechadas = Column(Numeric(5, 2), nullable=False)

    def __repr__(self):
        return f'<TipoServico {self.titulo}>'

# Tabela ServicoProjeto
class ServicoProjeto(Base):
    __tablename__ = 'servico_projeto'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    tipo_servico_id = Column(Integer, ForeignKey('tipo_servico.id'), nullable=False)  
    projeto_id = Column(Integer, ForeignKey('projeto.id'), nullable=False)

    def __repr__(self):
        return f'<ServicoProjeto {self.titulo}>'

# Tabela Projeto
class Projeto(Base):
    __tablename__ = 'projeto'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim_previsto = Column(Date, nullable=False)
    cliente = Column(String(100), nullable=False)
    responsavel_id = Column(Integer, ForeignKey('pessoa.id'), nullable=False)  
    total_horas_estimadas = Column(Numeric(5, 2), nullable=False)

    servicos = relationship('ServicoProjeto', backref='projeto', lazy=True)

    def __repr__(self):
        return f'<Projeto {self.nome}>'

# Tabela Tarefa
class Tarefa(Base):
    __tablename__ = 'tarefa'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    horas_estimadas = Column(Numeric(5, 2), nullable=False)
    horas_gastas = Column(Numeric(5, 2), nullable=False, default=0)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=True)
    projeto_id = Column(Integer, ForeignKey('projeto.id'), nullable=False)  
    responsavel_id = Column(Integer, ForeignKey('pessoa.id'), nullable=False)  
    status_tarefa_id = Column(Integer, ForeignKey('status_tarefa.id'), nullable=False)  
    servico_projeto_id = Column(Integer, ForeignKey('servico_projeto.id'), nullable=True)  
    tipo_tarefa_id = Column(Integer, ForeignKey('tipo_tarefa.id'), nullable=False)  

    tipo_tarefa = relationship('TipoTarefa', backref='tarefas', lazy=True)

    def __repr__(self):
        return f'<Tarefa {self.titulo}>'

# Tabela LançamentoHoras
class LancamentoHoras(Base):
    __tablename__ = 'lancamento_horas'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    data = Column(Date, nullable=False)
    horas = Column(Numeric(5, 2), nullable=False)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id'), nullable=False)  
    tipo_tarefa_id = Column(Integer, ForeignKey('tipo_tarefa.id'), nullable=False)  

    tipo_tarefa = relationship('TipoTarefa', lazy=True)

    def __repr__(self):
        return f'<LancamentoHoras {self.horas}>'

# Tabela ApontamentoHoras (novo modelo)
class ApontamentoHoras(Base):
    __tablename__ = 'apontamento_horas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(Date, nullable=False)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id'), nullable=False)
    horas_trabalhadas = Column(Numeric(5, 2), nullable=False)

    tarefa = relationship('Tarefa', backref='apontamentos', lazy=True)

    def __repr__(self):
        return f'<ApontamentoHoras {self.horas_trabalhadas} horas em {self.data}>'

