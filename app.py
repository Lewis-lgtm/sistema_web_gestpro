import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Pessoa, Projeto, Tarefa, TipoServico, ServicoProjeto, ApontamentoHoras, db
from datetime import date
import os

# Conectar ao banco de dados
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'mysql+pymysql://root:12345678@localhost:3306/meu_banco'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Função para realizar login
def login_page():
    st.title("Login")
    
    email = st.text_input('Email')
    senha = st.text_input('Senha', type='password')
    
    if st.button('Entrar'):
        usuario = session.query(Pessoa).filter_by(email=email).first()
        if usuario and usuario.senha == senha:
            st.session_state['user_id'] = usuario.id
            st.success("Login bem-sucedido")
            return True
        else:
            st.error('Email ou senha inválidos')
            return False
    return False

# Função para calcular o custo total de um projeto
def calcular_custo_total(projeto_id):
    projeto = session.query(Projeto).get(projeto_id)
    if projeto:
        custo_total_estimado = 0
        for tarefa in projeto.tarefas:
            for apontamento in tarefa.apontamentos:
                responsavel = session.query(Pessoa).get(tarefa.responsavel_id)
                custo_total_estimado += apontamento.horas_trabalhadas * responsavel.custo_por_hora
        return custo_total_estimado
    return 0

# Função para calcular lucro ou prejuízo e percentual de conclusão
def calcular_resultados(projeto_id):
    projeto = session.query(Projeto).get(projeto_id)
    if projeto:
        custo_total_estimado = calcular_custo_total(projeto_id)
        valor_pago_cliente = 10000  # Exemplo, seria o valor acordado com o cliente para o projeto
        lucro = valor_pago_cliente - custo_total_estimado
        percentual_conclusao = sum([tarefa.horas_gastas for tarefa in projeto.tarefas]) / sum([tarefa.horas_estimadas for tarefa in projeto.tarefas]) * 100
        return lucro, percentual_conclusao
    return 0, 0

# Função de verificação de permissão
def verificar_permissao(perfil_necessario):
    if 'user_id' not in st.session_state:
        st.error("Você precisa estar logado para acessar esta página.")
        return False
    
    usuario = session.query(Pessoa).get(st.session_state['user_id'])
    if usuario.perfil != perfil_necessario:
        st.error("Você não tem permissão para acessar esta funcionalidade.")
        return False
    
    return True

# Cadastro de projeto
def cadastro_projeto():
    # Verificar permissão do usuário
    if not verificar_permissao("admin"):  # Apenas um 'admin' pode cadastrar projetos
        return

    st.title("Cadastro de Projeto")

    nome = st.text_input('Nome do Projeto')
    descricao = st.text_area('Descrição do Projeto')
    data_inicio = st.date_input('Data de Início')
    data_fim = st.date_input('Data de Término')
    cliente = st.text_input('Cliente')

    responsavel_id = st.selectbox('Responsável', [p.nome for p in session.query(Pessoa).all()])

    horas_estimadas = st.number_input('Horas Estimadas', min_value=1, max_value=10000)

    if st.button('Cadastrar Projeto'):
        responsavel = session.query(Pessoa).filter_by(nome=responsavel_id).first()
        projeto = Projeto(
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim_previsto=data_fim,
            cliente=cliente,
            responsavel_id=responsavel.id,
            total_horas_estimadas=horas_estimadas
        )
        session.add(projeto)
        session.commit()
        st.success("Projeto cadastrado com sucesso!")


# Cadastro de serviço
def cadastro_servico():
    # Verificar permissão do usuário
    if not verificar_permissao("admin"):  # Apenas um 'admin' pode cadastrar serviços
        return

    st.title("Cadastro de Serviço")

    titulo = st.text_input('Título do Serviço')
    descricao = st.text_area('Descrição do Serviço')

    tipo_servico_id = st.selectbox('Tipo de Serviço', [tipo_servico.titulo for tipo_servico in session.query(TipoServico).all()])
    projeto_id = st.selectbox('Projeto', [projeto.nome for projeto in session.query(Projeto).all()])

    if st.button('Cadastrar Serviço'):
        tipo_servico = session.query(TipoServico).filter_by(titulo=tipo_servico_id).first()
        projeto = session.query(Projeto).filter_by(nome=projeto_id).first()
        servico = ServicoProjeto(
            titulo=titulo,
            descricao=descricao,
            tipo_servico_id=tipo_servico.id,
            projeto_id=projeto.id
        )
        session.add(servico)
        session.commit()
        st.success("Serviço cadastrado com sucesso!")

# Cadastro de tarefas
def cadastro_tarefa():
    # Verificar permissão do usuário
    if not verificar_permissao("gerente"):  # Apenas um 'gerente' pode cadastrar tarefas
        return

    st.title("Cadastro de Tarefa")

    descricao = st.text_input('Descrição da Tarefa')
    projeto_id = st.selectbox('Projeto', [projeto.nome for projeto in session.query(Projeto).all()])
    tempo_estimado = st.number_input('Tempo Estimado', min_value=1, max_value=10000)
    responsavel_id = st.selectbox('Responsável', [p.nome for p in session.query(Pessoa).all()])

    if st.button('Cadastrar Tarefa'):
        projeto = session.query(Projeto).filter_by(nome=projeto_id).first()
        responsavel = session.query(Pessoa).filter_by(nome=responsavel_id).first()
        tarefa = Tarefa(
            descricao=descricao,
            projeto_id=projeto.id,
            horas_estimadas=tempo_estimado,
            horas_gastas=0,
            responsavel_id=responsavel.id
        )
        session.add(tarefa)
        session.commit()
        st.success("Tarefa cadastrada com sucesso!")

# Apontamento de horas
def apontar_horas():
    st.title("Apontamento de Horas")

    tarefa_id = st.selectbox('Tarefa', [tarefa.descricao for tarefa in session.query(Tarefa).all()])
    horas_trabalhadas = st.number_input('Horas Trabalhadas', min_value=1)

    if st.button('Apontar Horas'):
        tarefa = session.query(Tarefa).filter_by(descricao=tarefa_id).first()
        usuario = session.query(Pessoa).get(st.session_state['user_id'])

        # Verificar se o usuário logado é o responsável pela tarefa
        if tarefa.responsavel_id != usuario.id:
            st.error("Você não tem permissão para apontar horas nesta tarefa.")
            return

        apontamento = ApontamentoHoras(
            data=date.today(),
            tarefa_id=tarefa.id,
            horas_trabalhadas=horas_trabalhadas
        )
        tarefa.horas_gastas += horas_trabalhadas  # Atualiza o tempo gasto na tarefa
        session.add(apontamento)
        session.commit()
        st.success(f"{horas_trabalhadas} horas apontadas com sucesso!")

# Página principal de navegação
def main():
    if 'user_id' not in st.session_state:
        if login_page():
            st.session_state['user_id'] = 1  # Exemplo: Usuário logado
            st.experimental_rerun()

    # Menu de navegação
    menu = ["Cadastro de Projeto", "Cadastro de Serviço", "Cadastro de Tarefa", "Apontar Horas", "Logout"]
    escolha = st.sidebar.selectbox("Escolha uma opção", menu)

    if escolha == "Cadastro de Projeto":
        cadastro_projeto()
    elif escolha == "Cadastro de Serviço":
        cadastro_servico()
    elif escolha == "Cadastro de Tarefa":
        cadastro_tarefa()
    elif escolha == "Apontar Horas":
        apontar_horas()
    elif escolha == "Logout":
        st.session_state.clear()  # Limpar a sessão do usuário
        st.success("Deslogado com sucesso!")
        st.experimental_rerun()

# Inicializa o app
if __name__ == '__main__':
    main()
