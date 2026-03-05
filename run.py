from app import create_app, formatar_preco

app = create_app()

app.jinja_env.filters['preco_br'] = formatar_preco

if __name__ == '__main__':
    app.run(debug=True)