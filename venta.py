import flask
from flask import Flask
from flask import request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS



from Controllers.ventasController import ventas_blueprint
from Controllers.productosController import producto_blueprint
from Controllers.clienteController import cliente_blueprint
from Controllers.usuarioController import usuario_blueprint

app = flask.Flask(__name__)
mysql = MySQL(app)
CORS(app)

app.config['mysql'] = mysql
app.config["DEBUG"] = True

app.register_blueprint(ventas_blueprint, url_prefix='/ventas')
app.register_blueprint(producto_blueprint, url_prefix='/producto')
app.register_blueprint(cliente_blueprint, url_prefix='/cliente')
app.register_blueprint(usuario_blueprint,url_prefix='/usuario')

if __name__ == "__main__":

    app.run()