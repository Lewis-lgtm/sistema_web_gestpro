from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # Usando SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Tabela Pessoa
class Pessoa(db.Model):
    __tablename__ = 'pessoa'
    Pessoa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Pessoa_Nome = db.Column(db.String(100), nullable=False)
    Pessoa_Email = db.Column(db.String(100), nullable=False, unique=True)
    Pessoa_NivelSenioridade = db.Column(db.String(50), nullable=False)  # Campo adicionado
    Pessoa_CustoPorHora = db.Column(db.Numeric(5, 2), nullable=False)  # Campo adicionado
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='pessoa', lazy=True)


# Tabela Status_Tarefa
class StatusTarefa(db.Model):
    __tablename__ = 'status_tarefa'
    StatusTarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StatusTarefa_Titulo = db.Column(db.String(100), nullable=False)
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='status_tarefa', lazy=True)

    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='servico_projeto', lazy=True)

# Tabela Tipo_Tarefa
class TipoTarefa(db.Model):
    __tablename__ = 'tipo_tarefa'
    TipoTarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TipoTarefa_Titulo = db.Column(db.String(100), nullable=False)
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='tipo_tarefa', lazy=True)

    
    # Relacionamentos
    Pessoa_ID = db.Column(db.Integer, db.ForeignKey('pessoa.Pessoa_ID'), nullable=False)
    StatusTarefa_ID = db.Column(db.Integer, db.ForeignKey('status_tarefa.StatusTarefa_ID'), nullable=False)
    ServicoProjeto_ID = db.Column(db.Integer, db.ForeignKey('servico_projeto.ServicoProjeto_ID'), nullable=True)  # Relacionamento 0,1:N
    TipoTarefa_ID = db.Column(db.Integer, db.ForeignKey('tipo_tarefa.TipoTarefa_ID'), nullable=False)

    # Relacionamento 0,N com Lançamento_Horas
    lancamentos_horas = db.relationship('LancamentoHoras', backref='tarefa', lazy=True)

# Tabela Lançamento_Horas
class LancamentoHoras(db.Model):
    __tablename__ = 'lancamento_horas'
    Lancamento_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Lancamento_Data = db.Column(db.Date, nullable=False)
    Lancamento_Horas = db.Column(db.Numeric(5, 2), nullable=False)
    
    Tarefa_ID = db.Column(db.Integer, db.ForeignKey('tarefa.Tarefa_ID'), nullable=False)
 
# Inicializa o banco de dados
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

# Adicione a classe Projeto
class Projeto(db.Model):
    __tablename__ = 'projeto'
    Projeto_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Projeto_Nome = db.Column(db.String(255), nullable=False)
    Projeto_Descricao = db.Column(db.Text, nullable=False)
    Projeto_DataInicio = db.Column(db.Date, nullable=False)
    Projeto_DataFimPrevisto = db.Column(db.Date, nullable=False)
    Cliente = db.Column(db.String(100), nullable=False)
    Responsavel_ID = db.Column(db.Integer, db.ForeignKey('pessoa.Pessoa_ID'), nullable=False)
    Total_HorasEstimadas = db.Column(db.Numeric(5, 2), nullable=False)
    servicos = db.relationship('ServicoProjeto', backref='projeto', lazy=True)

# Adicione a classe ServicoProjeto
class ServicoProjeto(db.Model):
    __tablename__ = 'servico_projeto'
    ServicoProjeto_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServicoProjeto_Titulo = db.Column(db.String(100), nullable=False)
    ServicoProjeto_Descricao = db.Column(db.Text, nullable=False)
    TipoServico_ID = db.Column(db.Integer, db.ForeignKey('tipo_servico.TipoServico_ID'), nullable=False)
    Projeto_ID = db.Column(db.Integer, db.ForeignKey('projeto.Projeto_ID'), nullable=False)

# Adicione a classe TipoServico
class TipoServico(db.Model):
    __tablename__ = 'tipo_servico'
    TipoServico_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TipoServico_Titulo = db.Column(db.String(100), nullable=False)
    TipoServico_HorasFechadas = db.Column(db.Boolean, nullable=False)

# Adicione a classe Tarefa
class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    Tarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tarefa_Titulo = db.Column(db.String(255), nullable=False)
    Tarefa_Descricao = db.Column(db.Text, nullable=True)
    Tarefa_HorasEstimadas = db.Column(db.Numeric(5, 2), nullable=False)
    Tarefa_HorasGastas = db.Column(db.Numeric(5, 2), nullable=False, default=0)  # Campo adicionado
    Tarefa_DataInicio = db.Column(db.Date, nullable=False)
    Tarefa_DataFim = db.Column(db.Date, nullable=True)
    Projeto_ID = db.Column(db.Integer, db.ForeignKey('projeto.Projeto_ID'), nullable=False)
    Responsavel_ID = db.Column(db.Integer, db.ForeignKey('pessoa.Pessoa_ID'), nullable=False)
    StatusTarefa_ID = db.Column(db.Integer, db.ForeignKey('status_tarefa.StatusTarefa_ID'), nullable=False)
    ServicoProjeto_ID = db.Column(db.Integer, db.ForeignKey('servico_projeto.ServicoProjeto_ID'), nullable=True)
    TipoTarefa_ID = db.Column(db.Integer, db.ForeignKey('tipo_tarefa.TipoTarefa_ID'), nullable=False)


# Adicione a classe LancamentoHoras
class LancamentoHoras(db.Model):
    __tablename__ = 'lancamento_horas'
    Lancamento_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Lancamento_Data = db.Column(db.Date, nullable=False)
    Lancamento_Horas = db.Column(db.Numeric(5, 2), nullable=False)
    Tarefa_ID = db.Column(db.Integer, db.ForeignKey('tarefa.Tarefa_ID'), nullable=False)



 
 