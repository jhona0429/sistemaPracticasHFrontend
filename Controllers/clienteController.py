from flask import Blueprint, request, jsonify
from Data.conexion import conexion
from Models.cliente import cliente
from flask_cors import CORS

cliente_blueprint = Blueprint('cliente_blueprint', __name__)
CORS(cliente_blueprint, resources={r"/*": {"origins": "http://192.168.0.4:8005"}})


@cliente_blueprint.route('/registrar', methods=['POST'])
def registroCliente():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        data = request.json
        nombre = data.get('nombre')
        apellidoP = data.get('apellidoP')
        apellidoM = data.get('apellidoM')

        if not nombre or not apellidoP or not apellidoM:
            raise Exception("Nombre, apellido paterno y apellido materno son requeridos")

        # Crear instancia de Cliente y registrar el cliente
        nuevo_cliente = cliente(nombre=nombre, apellidoP=apellidoP, apellidoM=apellidoM)
        respuesta_registro = nuevo_cliente.registrar()

        if respuesta_registro['codigo'] != 0:
            raise Exception(respuesta_registro['mensaje'])

        respuesta['mensaje'] = 'Cliente registrado correctamente'

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)
@cliente_blueprint.route('/listar', methods=['GET'])
def listarClientes():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = 'SELECT * FROM cliente'
            cursor.execute(sql)
            clientes_data = cursor.fetchall()

            if clientes_data:
                clientes = []
                for cliente_data in clientes_data:
                    cliente = {
                        'id_cliente': cliente_data['id_cliente'],
                        'nombre': cliente_data['nombre'],
                        'apellidoP': cliente_data['apellidoP'],
                        'apellidoM': cliente_data['apellidoM']
                    }
                    clientes.append(cliente)

                respuesta['clientes'] = clientes
            else:
                respuesta['clientes'] = []
                respuesta['mensaje'] = 'No se encontraron clientes'

    except Exception as ex:
        respuesta['codigo'] = 401
        respuesta['mensaje'] = f"Error al listar clientes: {str(ex)}"
    finally:
        conexion().db.close()

    return jsonify(respuesta)
@cliente_blueprint.route('/eliminar/<int:id_cliente>', methods=['DELETE'])
def eliminarCliente(id_cliente):
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = 'DELETE FROM cliente WHERE id_cliente = %s'
            cursor.execute(sql, (id_cliente,))
            if cursor.rowcount > 0:
                respuesta['mensaje'] = f"Cliente con ID {id_cliente} eliminado correctamente"
            else:
                respuesta['codigo'] = 404
                respuesta['mensaje'] = f"Cliente con ID {id_cliente} no encontrado para eliminar"

            conexion().db.commit()

    except Exception as ex:
        respuesta['codigo'] = 401
        respuesta['mensaje'] = f"Error al eliminar cliente: {str(ex)}"
        conexion().db.rollback()

    finally:
        conexion().db.close()

    return jsonify(respuesta)