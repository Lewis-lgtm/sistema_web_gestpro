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
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='pessoa', lazy=True)

# Tabela Status_Tarefa
class StatusTarefa(db.Model):
    __tablename__ = 'status_tarefa'
    StatusTarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StatusTarefa_Titulo = db.Column(db.String(100), nullable=False)
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='status_tarefa', lazy=True)

# Tabela Servico_Projeto
class ServicoProjeto(db.Model):
    __tablename__ = 'servico_projeto'
    ServicoProjeto_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServicoProjeto_Titulo = db.Column(db.String(100), nullable=False)
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='servico_projeto', lazy=True)

# Tabela Tipo_Tarefa
class TipoTarefa(db.Model):
    __tablename__ = 'tipo_tarefa'
    TipoTarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TipoTarefa_Titulo = db.Column(db.String(100), nullable=False)
    
    # Relacionamento 1:N com Tarefa
    tarefas = db.relationship('Tarefa', backref='tipo_tarefa', lazy=True)

# Tabela Tarefa
class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    Tarefa_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tarefa_Titulo = db.Column(db.String(255), nullable=False)
    Tarefa_Descricao = db.Column(db.Text, nullable=True)
    Tarefa_HorasEstimadas = db.Column(db.Numeric(5, 2), nullable=False)
    Tarefa_DataInicio = db.Column(db.Date, nullable=False)
    Tarefa_DataFim = db.Column(db.Date, nullable=True)
    
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


 
 