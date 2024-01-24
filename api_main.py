from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import jwt
from datetime import datetime, timedelta
from functools import wraps

#token para usuario cadastrado
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({"mensagem": "Token não foi incluído!"}, 401)
        try:
            resultado = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            autor = Autor.query.filter_by(id_autor=resultado["id_autor"]).first()
        except:
            return jsonify({"mensagem": "Token é inválido"}, 401)

        return f(autor, *args, **kwargs)

    return decorated


# autenticação basic auth
@app.route("/login")
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            {"mensagem": "Login inválido"},
            401,
            {"WWW-Authenticate": 'Basic realm="Login obrigatório"'},
        )

    user = Autor.query.filter_by(nome=auth.username).first()
    if not user:
        return make_response(
            {"mensagem": "Login inválido"},
            401,
            {"WWW-Authenticate": 'Basic realm="Login obrigatório"'},
        )
    if auth.password == user.senha:
        token = jwt.encode(
            {
                "id_autor": user.id_autor,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )
        return jsonify({"token": token})
    return make_response(
        {"mensagem": "Login inválido"},
        401,
        {"WWW-Authenticate": 'Basic realm="Login obrigatório"'},
    )


# Ler todas as postagens da lista
@app.route("/")
@token_obrigatorio
def home_postagem(autor):
    postagens = Postagem.query.all()
    list_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual["titulo"] = postagem.titulo
        postagem_atual["id_autor"] = postagem.id_autor
        list_postagens.append(postagem_atual)
    return jsonify({"postagens": list_postagens})


# GET (Ler uma musica da lista por indice)  http://localhost:12129/postagens/1
@app.route("/postagens/<int:id_postagem>", methods=["GET"])
@token_obrigatorio
def get_post_indice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual["titulo"] = postagem.titulo
    except:
        pass
    postagem_atual["id_autor"] = postagem.id_autor

    return jsonify({"postagens": postagem_atual})


# POST (adicionar musica) http://localhost:12129/postagens
@app.route("/postagens", methods=["POST"])
@token_obrigatorio
def post_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem["titulo"], id_autor=nova_postagem["id_autor"]
    )

    db.session.add(postagem)
    db.session.commit()

    return jsonify({"mensagem": "Postagem criada com sucesso"})


# PUT (Editar musica existente por indice) http://localhost:12129/postagens/1
@app.route("/postagens/<int:id_postagem>", methods=["PUT"])
@token_obrigatorio
def put_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada["titulo"]
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada["id_autor"]
    except:
        pass

    db.session.commit()
    return jsonify({"mensagem": "Postagem alterada com sucessso"})


# DELETE (Deletar musica existente por indice) http://localhost:12129/postagens/1
@app.route("/postagens/<int:id_postagem>", methods=["DELETE"])
@token_obrigatorio
def deletar_postagem(autor, id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_a_ser_excluida:
        return jsonify({"mensagem": "Não foi encontrado uma postagem com este id"})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({"mensagem": "Postagem excluída com sucesso!"})


# http://localhost:12129/autores
@app.route("/autores")
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual["id_autor"] = autor.id_autor
        autor_atual["nome"] = autor.nome
        autor_atual["email"] = autor.email
        lista_de_autores.append(autor_atual)
    return jsonify({"autores": lista_de_autores})


# http://localhost:12129/autores/1
@app.route("/autores/<int:id_autor>", methods=["GET"])
@token_obrigatorio
def obter_autor_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({"mensagem": "Esse usuário não foi encontrado!"})
    autor_atual = {}
    autor_atual["id_autor"] = autor.id_autor
    autor_atual["nome"] = autor.nome
    autor_atual["email"] = autor.email
    return jsonify({"autor": autor_atual})


# http://localhost:12129/autores
@app.route("/autores", methods=["POST"])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor["nome"], senha=novo_autor["senha"], email=novo_autor["email"]
    )
    db.session.add(autor)
    db.session.commit()

    return jsonify({"mensagem": "Usuário criado com sucesso!"}, 200)


# http://localhost:12129/autores/1
@app.route("/autores/<int:id_autor>", methods=["PUT"])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    alterar_autor = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({"mensagem": "Esse usuário não foi encontrado!"})
    try:
        autor.nome = alterar_autor["nome"]
    except:
        pass
    try:
        autor.senha = alterar_autor["senha"]
    except:
        pass
    try:
        autor.email = alterar_autor["email"]
    except:
        pass

    db.session.commit()

    return jsonify({"mensagem": "Usuário alterado com sucesso!"}, 200)


# http://localhost:12129/autores/1
@app.route("/autores/<int:id_autor>", methods=["DELETE"])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({"mensagem": "Este usuário não foi encontrado"})
    db.session.delete(autor_existente)
    db.session.commit()
    return jsonify({"mensagem": "Usuário deletado com sucesso!"})


app.run(port=12129, host="localhost", debug=True)
