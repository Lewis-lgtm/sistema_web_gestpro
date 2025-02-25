from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
import os

# Inicialização do Flask
app = Flask(__name__)

# Caminho absoluto para o banco de dados SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Pega o caminho onde o script principal está

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "project.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Para evitar alertas desnecessários
app.config['SECRET_KEY'] = 'mysecretkey'  # Chave secreta para sessões

# Inicializando o db (note que agora não passamos o app diretamente)
db = SQLAlchemy()
db.init_app(app)

# Inicializando o Migrate e o db (migrate precisa da configuração de app)
migrate = Migrate(app, db)

# Inicializando o LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Página de login

# Definir os modelos de dados
class Pessoa(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nivel_senioridade = db.Column(db.String(50), nullable=False)
    custo_por_hora = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)  # Senha armazenada de forma segura

    def __repr__(self):
        return f'<Pessoa {self.nome}>'

class TipoServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    horas_fechadas = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<TipoServico {self.titulo}>'

class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim_previsto = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(100), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    total_horas_estimadas = db.Column(db.Integer, nullable=False)

    responsavel = db.relationship('Pessoa', backref='projetos', lazy=True)
    tarefas = db.relationship('Tarefa', backref='projeto', lazy=True)
    servicos = db.relationship('ServicoProjeto', backref='projeto', lazy=True)

    def __repr__(self):
        return f'<Projeto {self.nome}>'

class ServicoProjeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

    tipo_servico = db.relationship('TipoServico', backref='servicos', lazy=True)

    def __repr__(self):
        return f'<ServicoProjeto {self.titulo}>'

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    horas_estimadas = db.Column(db.Integer, nullable=False)
    horas_gastas = db.Column(db.Integer, default=0)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

    responsavel = db.relationship('Pessoa', backref='tarefas', lazy=True)
    lancamentos = db.relationship('LancamentoHoras', backref='tarefa', lazy=True)

    def __repr__(self):
        return f'<Tarefa {self.titulo}>'

class LancamentoHoras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)

    def __repr__(self):
        return f'<LancamentoHoras {self.data} - {self.horas} horas>'

# Função para calcular custo total do projeto
def calcular_custo_total(projeto):
    custo_total_estimado = projeto.total_horas_estimadas * sum([tarefa.responsavel.custo_por_hora for tarefa in projeto.tarefas])
    horas_trabalhadas = sum([lancamento.horas for tarefa in projeto.tarefas for lancamento in tarefa.lancamentos])
    custo_total_real = horas_trabalhadas * sum([tarefa.responsavel.custo_por_hora for tarefa in projeto.tarefas])
    return custo_total_estimado, custo_total_real

# Rota para cadastrar um projeto
@app.route('/cadastro_projeto', methods=['GET', 'POST'])
@login_required
def cadastro_projeto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_inicio = request.form['data_inicio']
        data_fim_previsto = request.form['data_fim']
        cliente = request.form['cliente']
        responsavel_id = request.form['responsavel']
        horas_estimadas = request.form['horas_estimadas']

        projeto = Projeto(
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim_previsto=data_fim_previsto,
            cliente=cliente,
            responsavel_id=responsavel_id,
            total_horas_estimadas=horas_estimadas
        )

        db.session.add(projeto)
        db.session.commit()
        return redirect(url_for('index'))

    pessoas = Pessoa.query.all()
    return render_template('cadastro_projeto.html', pessoas=pessoas)

# Rota para cadastro de serviço
@app.route('/cadastro_servico', methods=['GET', 'POST'])
@login_required
def cadastro_servico():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo_servico_id = request.form['tipo_servico']
        projeto_id = request.form['projeto_id']

        servico = ServicoProjeto(
            titulo=titulo,
            descricao=descricao,
            tipo_servico_id=tipo_servico_id,
            projeto_id=projeto_id
        )

        db.session.add(servico)
        db.session.commit()
        return redirect(url_for('index'))

    tipos_servicos = TipoServico.query.all()
    projetos = Projeto.query.all()
    return render_template('cadastro_servico.html', tipos_servicos=tipos_servicos, projetos=projetos)

# Rota para cadastro de tipo de serviço
@app.route('/cadastro_tipo_servico', methods=['GET', 'POST'])
@login_required
def cadastro_tipo_servico():
    if request.method == 'POST':
        titulo = request.form['titulo']
        horas_fechadas = request.form['horas_fechadas'] == 'True'

        tipo_servico = TipoServico(
            titulo=titulo,
            horas_fechadas=horas_fechadas
        )

        db.session.add(tipo_servico)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cadastro_tipo_servico.html')

# Rota para cadastro de responsável
@app.route('/cadastro_responsavel', methods=['GET', 'POST'])
@login_required
def cadastro_responsavel():
    if request.method == 'POST':
        nome = request.form['nome']
        nivel_senioridade = request.form['nivel_senioridade']
        custo_por_hora = request.form['custo_por_hora']
        email = request.form['email']
        senha = request.form['senha']  # Aqui você deve adicionar criptografia de senha

        responsavel = Pessoa(
            nome=nome,
            nivel_senioridade=nivel_senioridade,
            custo_por_hora=custo_por_hora,
            email=email,
            senha=senha
        )

        db.session.add(responsavel)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cadastro_responsavel.html')

# Rota para apontamento de horas
@app.route('/apontar_horas/<int:tarefa_id>', methods=['GET', 'POST'])
@login_required
def apontar_horas(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if request.method == 'POST':
        horas_trabalhadas = float(request.form['horas_trabalhadas'])
        
        if tarefa.responsavel_id != current_user.id:
            flash("Você não tem permissão para apontar horas para essa tarefa.")
            return redirect(url_for('index'))

        lancamento = LancamentoHoras(
            data=date.today(),
            horas=horas_trabalhadas,
            tarefa_id=tarefa.id
        )

        tarefa.horas_gastas += horas_trabalhadas  # Atualizar horas gastas na tarefa
        db.session.add(lancamento)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('apontar_horas.html', tarefa=tarefa)

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Pessoa.query.filter_by(email=email).first()
        if usuario and usuario.senha == senha:
            login_user(usuario)
            return redirect(url_for('index'))
        flash('Login inválido. Verifique seu email e senha.', 'danger')

    return render_template('login.html')

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Página inicial (apenas exemplo)
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Carregar usuário (necessário para Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return Pessoa.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
