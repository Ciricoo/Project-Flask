from mercado import app
from flask import render_template, redirect, url_for, flash, request
from mercado.model import Item, User
from mercado.forms import CadastroForm, LoginForm, CompraProdutoForm, VendaProdutoForm
from mercado import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def page_home():
    return render_template("home.html")

@app.route('/produto', methods=["GET", "POST"])
@login_required
def page_produto():
    compra_form = CompraProdutoForm()
    venda_form = VendaProdutoForm()
    if request.method == "POST":
        #Compra produto
        compra_produto = request.form.get('compra_produto')
        produto_obj = Item.query.filter_by(nome=compra_produto).first()
        if produto_obj:
            if current_user.compra_disponivel(produto_obj):
                produto_obj.compra(current_user)
                flash(f"Parabéns! Você comprou o produto {produto_obj.nome}", category='success')
            else:
                flash(f"Você não possui saldo suficiente para comprar o produto {produto_obj.nome}", category='danger')
        #Venda Produto
        venda_produto = request.form.get('venda_produto')
        produto_obj_venda = Item.query.filter_by(nome=venda_produto).first()
        if produto_obj_venda:
            if current_user.venda_disponivel(produto_obj_venda):
                produto_obj_venda.venda(current_user)
                flash(f"Parabéns! Você vendeu o produto {produto_obj.nome}", category="success")
        else:
            flash(f"Algo deu errado com a venda do produto {produto_obj.nome}", category="danger")
        return redirect(url_for('page_produto'))
    if request.method == "GET":
        itens = Item.query.filter_by(dono=None)
        dono_item = Item.query.filter_by(dono = current_user.id)
        return render_template('produto.html', itens=itens, compra_form=compra_form, dono_item=dono_item, venda_form=venda_form)

@app.route('/cadastro', methods=['GET', 'POST'])
def page_cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        usuario = User(
            usuario=form.usuario.data,
            email=form.email.data,
            senhacrip=form.senha1.data
        )

        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('page_produto'))
    if form.errors:
        for err in form.errors.values():
            flash(f"Erro ao cadastrar usuário {err}", category="danger")
    return render_template("cadastro.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def page_login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario_logado = User.query.filter_by(usuario=form.usuario.data).first()
        if usuario_logado and usuario_logado.converte_senha(senha_texto_claro=form.senha.data):
            login_user(usuario_logado)
            flash(f'Sucesso! Seu login é: {usuario_logado.usuario}', category='success')
            return redirect(url_for('page_produto'))
        else:
            flash(f'Usuário ou senha estão incorretos! Tente novamente.', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def page_logout():
    logout_user()
    flash("Você fez o logout", category="info")
    return redirect(url_for("page_home"))