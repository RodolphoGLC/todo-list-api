# 📋 Task List API

Uma API RESTful para gerenciamento de tarefas dos usuários, construída com Flask, Flask-OpenAPI3, SQLAlchemy e Pydantic.

## 🚀 Funcionalidades

- CRUD de tarefas
- Autenticação de usuários
- Contagem de tarefas por status
- Documentação interativa via Swagger, Redoc ou RapiDoc

---

## 📦 Tecnologias

- Python 3.10+
- Flask
- Flask-CORS
- Flask-OpenAPI3
- SQLAlchemy
- Pydantic

---

## 🛠️ Instalação

1. Clonar o repositorio no seu computador
```
    git clone "https://github.com/RodolphoGLC/todo-list-api.git"
```

2. Baixar o venv no projeto e iniciar ele (siga o passo a passo a baixo)

```
    python -m venv venv
```

```
    .\venv\Scripts\activate
```

3. Instale as bibliotecas

```
    pip install -r requirements.txt
```

4. Por fim rode a aplicação usando o comando abaixo

```
    flask run --host 0.0.0.0 --port 5000
```
