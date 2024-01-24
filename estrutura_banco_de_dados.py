from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Criar um API Flask

app = Flask(__name__)

# Criar uma instância de SQLALCHEMY
app.config["SECRET_KEY"] = "FSD2323f#%$SAEEW"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_dados.db"

db = SQLAlchemy(app)
db: SQLAlchemy


# Definir a estrutura da tabela Postagem
# id_postagem, titulo, autor
class Postagem(db.Model):
    __tablename__ = "postagem"
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))


# Definir a estrutura da tabela Autor
# id_autorm, nome, email, senha, admin, postagens
class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship("Postagem")


def inicializar_banco():
    with app.app_context():
        # Executar o comando para criar o banco de dados
        db.drop_all()
        db.create_all()
        # Criar usuarios admins
        autor = Autor(nome="joao", email="joao@gmail.com", senha="123@456", admin=True)
        db.session.add(autor)
        db.session.commit()

#Para criar a dadabase execute no terminal python estrutura_banco_de_dados.py
if __name__ == "__main__":
    inicializar_banco()
