from flask import Blueprint, request, jsonify
from Models.usuario import usuario  
from Data.conexion import conexion

usuario_blueprint = Blueprint('usuario_blueprint', __name__)

@usuario_blueprint.route('/registrar', methods=['POST'])
def registroUsuario():
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

        # Crear instancia de Usuario) y registrar el usuario
        nuevo_usuario = usuario(nombre=nombre, apellidoP=apellidoP, apellidoM=apellidoM)
        respuesta_registro = nuevo_usuario.registrar()

        if respuesta_registro['codigo'] != 0:
            raise Exception(respuesta_registro['mensaje'])

        respuesta['mensaje'] = 'Usuario registrado correctamente'

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)
@usuario_blueprint.route('/listar', methods=['GET'])
def listarUsuarios():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = 'SELECT * FROM usuario'
            cursor.execute(sql)
            usuarios_data = cursor.fetchall()

            if usuarios_data:
                usuarios = []
                for usuario_data in usuarios_data:
                    usuario = {
                        'id_usuario': usuario_data['id_usuario'],
                        'nombre': usuario_data['nombre'],
                        'apellidoP': usuario_data['apellidoP'],
                        'apellidoM': usuario_data['apellidoM']
                    }
                    usuarios.append(usuario)

                respuesta['usuarios'] = usuarios
            else:
                respuesta['usuarios'] = []
                respuesta['mensaje'] = 'No se encontraron usuarios'

    except Exception as ex:
        respuesta['codigo'] = 401
        respuesta['mensaje'] = f"Error al listar usuarios: {str(ex)}"
    finally:
        conexion().db.close()

    return jsonify(respuesta)

@usuario_blueprint.route('/eliminar/<int:id_usuario>', methods=['DELETE'])
def eliminarUsuario(id_usuario):
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = 'DELETE FROM usuario WHERE id_usuario = %s'
            cursor.execute(sql, (id_usuario,))
            if cursor.rowcount > 0:
                respuesta['mensaje'] = f"Usuario con ID {id_usuario} eliminado correctamente"
            else:
                respuesta['codigo'] = 404
                respuesta['mensaje'] = f"Usuario con ID {id_usuario} no encontrado para eliminar"

            conexion().db.commit()

    except Exception as ex:
        respuesta['codigo'] = 401
        respuesta['mensaje'] = f"Error al eliminar usuario: {str(ex)}"
        conexion().db.rollback()

    finally:
        conexion().db.close()

    return jsonify(respuesta)