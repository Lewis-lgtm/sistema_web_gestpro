from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Tabela Pessoa
class Pessoa(db.Model):
    __tablename__ = 'pessoa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    nivel_senioridade = db.Column(db.String(50), nullable=False)
    custo_por_hora = db.Column(db.Numeric(5, 2), nullable=False)

    tarefas = db.relationship('Tarefa', backref='responsavel', lazy=True)

    def __repr__(self):
        return f'<Pessoa {self.nome}>'

# Tabela StatusTarefa
class StatusTarefa(db.Model):
    __tablename__ = 'status_tarefa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)

    tarefas = db.relationship('Tarefa', backref='status_tarefa', lazy=True)

    def __repr__(self):
        return f'<StatusTarefa {self.titulo}>'

# Tabela TipoTarefa
class TipoTarefa(db.Model):
    __tablename__ = 'tipo_tarefa'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    nome = db.Column(db.String(100), nullable=False)
    
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)  
    status_tarefa_id = db.Column(db.Integer, db.ForeignKey('status_tarefa.id'), nullable=False)  
    servico_projeto_id = db.Column(db.Integer, db.ForeignKey('servico_projeto.id'), nullable=True)

    pessoa = db.relationship('Pessoa', backref='tipo_tarefas')
    status_tarefa = db.relationship('StatusTarefa', backref='tipo_tarefas')
    servico_projeto = db.relationship('ServicoProjeto', backref='tipo_tarefas', lazy=True)

    lancamentos_horas = db.relationship('LancamentoHoras', backref='tipo_tarefa_lancamentos', lazy=True)

    def __repr__(self):
        return f'<TipoTarefa {self.nome}>'

# Tabela ServicoProjeto
class ServicoProjeto(db.Model):
    __tablename__ = 'servico_projeto'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)  
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

    def __repr__(self):
        return f'<ServicoProjeto {self.titulo}>'

# Tabela Projeto
class Projeto(db.Model):
    __tablename__ = 'projeto'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim_previsto = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(100), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)  
    total_horas_estimadas = db.Column(db.Numeric(5, 2), nullable=False)

    servicos = db.relationship('ServicoProjeto', backref='projeto', lazy=True)

    def __repr__(self):
        return f'<Projeto {self.nome}>'

# Tabela Tarefa
class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    horas_estimadas = db.Column(db.Numeric(5, 2), nullable=False)
    horas_gastas = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)  
    responsavel_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)  
    status_tarefa_id = db.Column(db.Integer, db.ForeignKey('status_tarefa.id'), nullable=False)  
    servico_projeto_id = db.Column(db.Integer, db.ForeignKey('servico_projeto.id'), nullable=True)  
    tipo_tarefa_id = db.Column(db.Integer, db.ForeignKey('tipo_tarefa.id'), nullable=False)  

    tipo_tarefa = db.relationship('TipoTarefa', backref='tarefas', lazy=True)

    def __repr__(self):
        return f'<Tarefa {self.titulo}>'

# Tabela LançamentoHoras
class LancamentoHoras(db.Model):
    __tablename__ = 'lancamento_horas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    data = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Numeric(5, 2), nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)  
    tipo_tarefa_id = db.Column(db.Integer, db.ForeignKey('tipo_tarefa.id'), nullable=False)  

    tipo_tarefa = db.relationship('TipoTarefa', lazy=True)

    def __repr__(self):
        return f'<LancamentoHoras {self.horas}>'


