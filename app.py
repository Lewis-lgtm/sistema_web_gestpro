from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importando o Migrate
from models import db, Pessoa, StatusTarefa, ServicoProjeto, TipoTarefa, Tarefa, LancamentoHoras, Projeto, TipoServico
from datetime import date
import os

# Inicialização do Flask
app = Flask(__name__)

# Caminho absoluto para o banco de dados SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Pega o caminho onde o script principal está

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "project.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Para evitar alertas desnecessários

# Inicializando o Migrate e o db (db já é inicializado no models.py)
migrate = Migrate(app, db)

# Inicializando o db com o app
db.init_app(app)

# Criando o banco de dados dentro do bloco `if __name__ == '__main__':`
if __name__ == '__main__':
    # Criando o banco de dados se ele não existir
    with app.app_context():
        db.create_all()  # Isso deve ser chamado dentro do app.app_context()
        print("Banco de dados criado com sucesso!")

    # Rodando o servidor Flask
    app.run(debug=True)


@app.route('/cadastro_projeto', methods=['GET', 'POST'])
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
            Projeto_Nome=nome,
            Projeto_Descricao=descricao,
            Projeto_DataInicio=data_inicio,
            Projeto_DataFimPrevisto=data_fim_previsto,
            Cliente=cliente,
            Responsavel_ID=responsavel_id,
            Total_HorasEstimadas=horas_estimadas
        )

        db.session.add(projeto)
        db.session.commit()
        return redirect(url_for('index'))
    
    pessoas = Pessoa.query.all()
    return render_template('cadastro_projeto.html', pessoas=pessoas)


@app.route('/cadastro_servico', methods=['GET', 'POST'])  # Cadastro de serviço
def cadastro_servico():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo_servico_id = request.form['tipo_servico']

        servico = ServicoProjeto(
            ServicoProjeto_Titulo=titulo,
            ServicoProjeto_Descricao=descricao,
            TipoServico_ID=tipo_servico_id  # Associando o tipo de serviço
        )

        db.session.add(servico)
        db.session.commit()
        return redirect(url_for('index'))

    tipos_servicos = TipoServico.query.all()  # Buscar tipos de serviços para o formulário
    return render_template('cadastro_servico.html', tipos_servicos=tipos_servicos)


@app.route('/cadastro_tipo_servico', methods=['GET', 'POST'])  # Cadastro de tipo de serviço
def cadastro_tipo_servico():
    if request.method == 'POST':
        titulo = request.form['titulo']
        horas_fechadas = request.form['horas_fechadas'] == 'True'  # Convertendo a string para booleano

        tipo_servico = TipoServico(
            TipoServico_Titulo=titulo,
            TipoServico_HorasFechadas=horas_fechadas
        )

        db.session.add(tipo_servico)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cadastro_tipo_servico.html')


@app.route('/cadastro_responsavel', methods=['GET', 'POST'])  # Cadastro de responsável
def cadastro_responsavel():
    if request.method == 'POST':
        nome = request.form['nome']
        nivel_senioridade = request.form['nivel_senioridade']
        custo_por_hora = request.form['custo_por_hora']
        email = request.form['email']  # Captura o email do formulário

        responsavel = Pessoa(
            Pessoa_Nome=nome,
            Pessoa_NivelSenioridade=nivel_senioridade,
            Pessoa_CustoPorHora=custo_por_hora,
            Pessoa_Email=email  # Inclui o email na criação da instância
        )

        db.session.add(responsavel)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cadastro_responsavel.html')


@app.route('/cadastro_tarefa', methods=['GET', 'POST'])  # Cadastro de tarefa
def cadastro_tarefa():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        horas_estimadas = request.form['horas_estimadas']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']

        tarefa = Tarefa(
            Tarefa_Titulo=titulo,
            Tarefa_Descricao=descricao,
            Tarefa_HorasEstimadas=horas_estimadas,
            Tarefa_DataInicio=data_inicio,
            Tarefa_DataFim=data_fim
        )

        db.session.add(tarefa)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('cadastro_tarefa.html')  # Crie este template


@app.route('/')
def index():
    # Buscar tarefas para exibir na página principal
    tarefas = Tarefa.query.all()
    return render_template('index.html', tarefas=tarefas)


@app.route('/apontar_horas/<int:tarefa_id>', methods=['GET', 'POST'])
def apontar_horas(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if request.method == 'POST':
        horas_trabalhadas = float(request.form['horas_trabalhadas'])
        lancamento = LancamentoHoras(
            Lancamento_Data=date.today(),
            Lancamento_Horas=horas_trabalhadas,
            Tarefa_ID=tarefa_id
        )
        tarefa.Tarefa_HorasGastas += horas_trabalhadas
        db.session.add(lancamento)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('apontar_horas.html', tarefa=tarefa)
