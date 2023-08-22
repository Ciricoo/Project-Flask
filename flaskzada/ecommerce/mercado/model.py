from mercado import db, login_manager
from mercado import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(length=30), nullable=True, unique=True)
    email = db.Column(db.String(length=50), nullable=True, unique=True)
    senha = db.Column(db.String(length=60), nullable=True, unique=True)
    valor = db.Column(db.Integer, nullable=False, default=5000)
    itens = db.relationship('Item', backref='dono_user', lazy=True)

    @property
    def formataValor(self):
        if len(str(self.valor)) >= 4: # R$ 400
            return f"R$ {str(self.valor)[:-3]}, {str(self.valor)[-3:]}"
        else:
            return f"R$ {self.valor}"

    @property
    def senhacrip(self):
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto):
        self.senha = bcrypt.generate_password_hash(senha_texto).decode('utf-8')

    def converte_senha(self, senha_texto_claro):
        return bcrypt.check_password_hash(self.senha, senha_texto_claro)
    
    def compra_disponivel(self, produto_obj):
        return self.valor >= produto_obj.preco
    
    def venda_disponivel(self, produto_obj):
        return produto_obj in self.itens
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(length=30), nullable=False, unique=True)
    preco = db.Column(db.Integer, nullable=False)
    cod_barra = db.Column(db.String(length=12), nullable=False, unique=True)
    descricao = db.Column(db.String(length=1024), nullable=False, unique=True)
    dono = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Item {self.nome}"

    def compra(self, usuario):
        self.dono = usuario.id
        usuario.valor -= self.preco
        db.session.commit()

        def venda(self, usuario):
            self.dono = None
            usuario.valor += self.preco
            db.session.commit()