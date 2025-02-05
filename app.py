from flask import Flask, render_template
from models import db, Pessoa, StatusTarefa, ServicoProjeto, TipoTarefa, Tarefa, LancamentoHoras

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    # Buscar todas as tarefas no banco de dados
    tarefas = Tarefa.query.all()  # Usando o SQLAlchemy para buscar todas as tarefas

    # Passar as tarefas para o template HTML
    return render_template('index.html', tarefas=tarefas)

if __name__ == '__main__':
    app.run(debug=True)
