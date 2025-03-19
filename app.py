import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Pessoa, Projeto, Tarefa, TipoServico, ServicoProjeto, ApontamentoHoras
from datetime import date
import os
import bcrypt
 
 
# Conectar ao banco de dados
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'mysql+pymysql://root:12345678@localhost:3306/meu_banco'
 
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
 
 
 
# Função para criar um novo usuário (incluindo um usuário de teste)
# Função para criar um novo usuário (incluindo um usuário de teste)
def criar_usuario(nome, email, senha, perfil, nivel_senioridade="Junior", custo_por_hora=0):
    # Verifica se o usuário já existe
    usuario_existente = session.query(Pessoa).filter_by(email=email).first()
    if usuario_existente:
        print(f"Usuário com o email {email} já existe, pulando criação.")
        return  # Não cria o usuário novamente
   
    # Hashificando a senha antes de salvar no banco de dados
    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
   
    # Criando o novo usuário com a senha hashificada
    usuario = Pessoa(
        nome=nome,
        email=email,
        senha=hashed_password,  # Aqui você não precisa de base64, o bcrypt já faz isso
        perfil=perfil,
        nivel_senioridade=nivel_senioridade,  
        custo_por_hora=custo_por_hora  
    )
   
    session.add(usuario)
    session.commit()
    print(f"Usuário {nome} criado com sucesso!")
 
 
# Função para realizar login
def login_page():
    st.title("Login")
 
    # Verifique se o usuário de teste já existe antes de criar
    usuario_existente = session.query(Pessoa).filter_by(email='admin@teste.com').first()
    if not usuario_existente:
        criar_usuario('Administrador', 'admin@teste.com', 'senha123', 'admin')
   
    email = st.text_input('Email')
    senha = st.text_input('Senha', type='password')
   
    if st.button('Entrar'):
        usuario = session.query(Pessoa).filter_by(email=email).first()  # Verificando pelo email
 
        if usuario:
            # Verifica se a senha fornecida corresponde ao hash armazenado
            if bcrypt.checkpw(senha.encode('utf-8'), usuario.senha.encode('utf-8')):
                st.session_state['user_id'] = usuario.id
                st.success(f"Bem-vindo(a), {usuario.nome}!")
                return True  # Login bem-sucedido
            else:
                st.error('Senha incorreta. Tente novamente.')
                return False
        else:
            st.error('Usuário não encontrado.')
            return False
    return False


# Função para criar um Projeto de Teste
 # Função para criar um Projeto de Teste
def criar_projeto_teste():
    if not verificar_permissao(["admin", "gerente"]):  # Somente admin e gerente podem criar projetos
        return

    st.title("Criar Projeto de Teste")

    # Selecionar um responsável para o projeto
    responsavel = session.query(Pessoa).first()  # Selecionando o primeiro responsável existente
    if not responsavel:
        st.error("Nenhum responsável encontrado! Crie um responsável primeiro.")
        return

    # Selecionar serviços existentes
    servicos = session.query(ServicoProjeto).all()  # Todos os serviços cadastrados
    if not servicos:
        st.error("Nenhum serviço encontrado! Crie um serviço primeiro.")
        return

    # Criando o projeto de teste com dados pré-definidos
    nome = "Projeto de Teste"
    descricao = "Descrição do projeto de teste"
    data_inicio = date.today()
    data_fim = date.today()  # A data de término pode ser a data de hoje ou uma data futura
    cliente = "Cliente Teste"
    horas_estimadas = 100  # Exemplo de horas estimadas

    # Criando o projeto
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

    # Associando serviços ao projeto
    for servico in servicos:
        servico.projeto_id = projeto.id  # Associando o serviço ao projeto
        session.commit()

    st.success(f"Projeto de Teste '{nome}' criado com sucesso!")


# Função para criar uma Tarefa de Teste
# Função para criar uma Tarefa de Teste
def criar_tarefa_teste():
    if not verificar_permissao(["admin", "gerente"]):  # Só admin e gerente podem criar tarefas
        return
    
    st.title("Criar Tarefa de Teste")
    
    # Selecionar um projeto já existente    
    projeto = session.query(Projeto).first()
    if not projeto:
        st.error("Nenhum projeto encontrado! Crie um projeto primeiro.")
        return
    
    # Selecionar um responsável    
    responsavel = session.query(Pessoa).first()
    if not responsavel:
        st.error("Nenhum responsável encontrado! Crie um responsável primeiro.")
        return
    
    # Criar tarefa    
    descricao = "Tarefa de Teste"
    tempo_estimado = 8  # Por exemplo, 8 horas estimadas    
    tarefa = Tarefa(
        descricao=descricao,
        projeto_id=projeto.id,
        horas_estimadas=tempo_estimado,
        horas_gastas=0,
        responsavel_id=responsavel.id
    )
    
    session.add(tarefa)
    session.commit()
    st.success(f"Tarefa de Teste '{descricao}' criada com sucesso no projeto '{projeto.nome}'.")


# Função para criar um Tipo de Serviço de Teste
def criar_tipo_servico_teste():
    if not verificar_permissao(["admin"]):  # Apenas admin pode criar tipos de serviços
        return

    st.title("Criar Tipo de Serviço de Teste")

    # Criando o tipo de serviço com dados pré-definidos
    titulo = "Tipo de Serviço de Teste"
    horas_fechadas = 1.00  # 1.00 representando 'Fechadas'

    # Criando o tipo de serviço
    tipo_servico = TipoServico(
        titulo=titulo,
        horas_fechadas=horas_fechadas  # Passando o valor correto para horas_fechadas
    )
    
    session.add(tipo_servico)
    session.commit()

    st.success(f"Tipo de Serviço de Teste '{titulo}' criado com sucesso!")

# Função para criar um Serviço de Teste
# Função para criar um Serviço de Teste
def criar_servico_teste():
    if not verificar_permissao(["admin"]):  # Apenas admin pode criar serviços
        return
    
    st.title("Criar Serviço de Teste")
    
    # Selecionar um tipo de serviço    
    tipo_servico = session.query(TipoServico).first()
    if not tipo_servico:
        st.error("Nenhum tipo de serviço encontrado! Crie um tipo de serviço primeiro.")
        return
    
    # Selecionar um projeto já existente    
    projeto = session.query(Projeto).first()
    if not projeto:
        st.error("Nenhum projeto encontrado! Crie um projeto primeiro.")
        return
    
    # Criar serviço    
    titulo = "Serviço de Teste"
    descricao = "Este é um serviço de teste para o projeto."
    servico = ServicoProjeto(
        titulo=titulo,
        descricao=descricao,
        tipo_servico_id=tipo_servico.id,
        projeto_id=projeto.id
    )
    
    session.add(servico)
    session.commit()
    st.success(f"Serviço de Teste '{titulo}' criado com sucesso no projeto '{projeto.nome}'.")


# Página de boas-vindas após login
def pagina_boas_vindas():
    st.title("Bem-vindo(a) ao Sistema de Gestão de Projetos")
    st.write(f"Olá, {st.session_state['usuario_nome']}! Seja bem-vindo ao sistema.")
    st.write("Agora você pode começar a gerenciar projetos, tarefas e serviços.")
    
    if st.button('Ir para o Dashboard'):
        st.session_state['pagina_atual'] = 'dashboard'  # Redireciona para o dashboard
        st.experimental_rerun()  # Recarrega para mostrar o dashboard

# Página principal de navegação
def main():
    if 'user_id' not in st.session_state:
        if login_page():  # Se o login for bem-sucedido
            st.session_state['user_id'] = 1  # Exemplo: Usuário logado
            st.rerun()

    if 'pagina_atual' not in st.session_state:
        st.session_state['pagina_atual'] = 'login'  # Página inicial ao acessar o app

    if st.session_state['pagina_atual'] == 'login':
        login_page()
    elif st.session_state['pagina_atual'] == 'boas_vindas':
        pagina_boas_vindas()
    elif st.session_state['pagina_atual'] == 'dashboard':
        menu = ["Cadastro de Projeto", "Cadastro de Serviço", "Cadastro de Tipo de Serviço", "Cadastro de Tarefa", "Apontar Horas", "Logout"]
        escolha = st.sidebar.selectbox("Escolha uma opção", menu)

        if escolha == "Cadastro de Projeto":
            cadastro_projeto()
        elif escolha == "Cadastro de Serviço":
            cadastro_servico()
        elif escolha == "Cadastro de Tipo de Serviço":
            cadastro_tipo_servico()
        elif escolha == "Cadastro de Tarefa":
            cadastro_tarefa()
        elif escolha == "Apontar Horas":
            apontar_horas()
        elif escolha == "Logout":
            st.session_state.clear()  # Limpar a sessão do usuário
            st.success("Deslogado com sucesso!")
            st.rerun()
 
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
 
        # Verificação de cumprimento de prazos
        prazo_atrasado = date.today() > projeto.data_fim_previsto
        return lucro, percentual_conclusao, prazo_atrasado
    return 0, 0, False
 
 
# Função de verificação de permissão
def verificar_permissao(perfil_necessario):
    if 'user_id' not in st.session_state:
        st.error("Você precisa estar logado para acessar esta página.")
        return False
    
    usuario = session.query(Pessoa).get(st.session_state['user_id'])
    
    # Aqui, fazemos uma verificação para que o gerente tenha permissão na tarefa
    if usuario.perfil not in perfil_necessario:
        st.error("Você não tem permissão para acessar esta funcionalidade.")
        return False
    
    return True
 
 
# Cadastro de Projeto com validação de serviço associado
def cadastro_projeto():
    if not verificar_permissao("admin"):  
        return
 
    st.title("Cadastro de Projeto")
 
    nome = st.text_input('Nome do Projeto')
    descricao = st.text_area('Descrição do Projeto')
    data_inicio = st.date_input('Data de Início')
    data_fim = st.date_input('Data de Término')
    cliente = st.text_input('Cliente')
 
    responsavel_id = st.selectbox('Responsável', [p.nome for p in session.query(Pessoa).all()])
    horas_estimadas = st.number_input('Horas Estimadas', min_value=1, max_value=10000)
 
    # Seleção dos serviços associados ao projeto
    servicos = [servico.titulo for servico in session.query(ServicoProjeto).all()]
    servicos_associados = st.multiselect("Selecione os serviços associados", servicos)
 
    if st.button('Cadastrar Projeto'):
        if not servicos_associados:
            st.error("Ao menos um serviço deve ser associado ao projeto.")
            return
 
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
 
        # Vincula os serviços ao projeto
        for servico_titulo in servicos_associados:
            servico = session.query(ServicoProjeto).filter_by(titulo=servico_titulo).first()
            servico.projeto_id = projeto.id
            session.commit()
 
        st.success("Projeto cadastrado com sucesso!")
 
 
# Cadastro de Tipo de Serviço
def cadastro_tipo_servico():
    if not verificar_permissao("admin"):  
        return
 
    st.title("Cadastro de Tipo de Serviço")
 
    titulo = st.text_input('Título do Tipo de Serviço')
    horas_fechadas = st.radio('Tipo de Hora', ('Fechadas', 'Abertas'))

     # Mapeando 'Fechadas' para 1.00 e 'Abertas' para 0.00
    horas_fechadas = 1.00 if horas_fechadas == 'Fechadas' else 0.00
 
    if st.button('Cadastrar Tipo de Serviço'):
        tipo_servico = TipoServico(
            titulo=titulo,
            horas_fechadas=horas_fechadas
        )
        session.add(tipo_servico)
        session.commit()
        st.success("Tipo de Serviço cadastrado com sucesso!")
 
 
# Cadastro de Serviço com vinculação ao tipo de serviço
def cadastro_servico():
    if not verificar_permissao("admin"):  
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
 
 
# Cadastro de Tarefa com validação do tempo gasto
def cadastro_tarefa():
    # Permitir tanto admin quanto gerente para cadastrar tarefa
    if not verificar_permissao(["admin", "gerente"]):  
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
 
# Apontamento de horas com controle de responsabilidade
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
            st.rerun()
 
    # Menu de navegação
    menu = ["Cadastro de Projeto", "Cadastro de Serviço", "Cadastro de Tipo de Serviço", "Cadastro de Tarefa", "Apontar Horas", "Criar Tarefa de Teste", "Criar Serviço de Teste", "Criar Projeto de Teste", "Criar Tipo de Serviço de Teste", "Logout"]
    escolha = st.sidebar.selectbox("Escolha uma opção", menu)
 
    if escolha == "Cadastro de Projeto":
        cadastro_projeto()
    elif escolha == "Cadastro de Serviço":
        cadastro_servico()
    elif escolha == "Cadastro de Tipo de Serviço":
        cadastro_tipo_servico()
    elif escolha == "Cadastro de Tarefa":
        cadastro_tarefa()
    elif escolha == "Apontar Horas":
        apontar_horas()
    elif escolha == "Criar Tarefa de Teste":  # Verifica se o usuário escolheu criar uma tarefa de teste
        criar_tarefa_teste()
    elif escolha == "Criar Serviço de Teste":  # Verifica se o usuário escolheu criar um serviço de teste
        criar_servico_teste()
    elif escolha == "Criar Projeto de Teste":
        criar_projeto_teste()  # Chama a função de criação de projeto de teste
    elif escolha == "Criar Tipo de Serviço de Teste":
        criar_tipo_servico_teste()  # Chama a função de criação de tipo de serviço de teste
    elif escolha == "Logout":
        st.session_state.clear()  # Limpar a sessão do usuário
        st.success("Deslogado com sucesso!")
        st.rerun()
 
# Inicializa o app
if __name__ == '__main__':
    main() 