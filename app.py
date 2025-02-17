from flask import Flask, render_template, request, redirect, url_for
from models import db, Pessoa, StatusTarefa, ServicoProjeto, TipoTarefa, Tarefa, LancamentoHoras, Projeto, TipoServico  # Importando os novos modelos
from datetime import date

#comeca o código
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    tarefas = Tarefa.query.all()  
    return render_template('index.html', tarefas=tarefas)

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
     # Buscar todas as pessoas para o campo de responsável
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


# Apontamento de horas
@app.route('/apontar_horas/<int:tarefa_id>', methods=['GET', 'POST'])
def apontar_horas(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if request.method == 'POST':
        horas_trabalhadas = request.form['horas_trabalhadas']
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

if __name__ == '__main__':
    app.run(debug=True)
