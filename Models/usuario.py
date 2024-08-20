from Data.conexion import conexion

class usuario:
    def __init__(self, id_usuario=None, nombre=None, apellidoP=None, apellidoM=None):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellidoP = apellidoP
        self.apellidoM = apellidoM
        self.oconexion = conexion()
    

    def registrar(self):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }

        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = '''
                    INSERT INTO usuario (nombre, apellidoP, apellidoM)
                    VALUES (%s, %s, %s)
                '''
                cursor.execute(sql, (self.nombre, self.apellidoP, self.apellidoM))

            self.oconexion.db.commit()

        except Exception as ex:
            self.oconexion.db.rollback()
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)

        finally:
            self.oconexion.db.close()

        return respuesta
    def buscar_por_id(self, id_usuario):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = 'SELECT * FROM usuario WHERE id_usuario = %s'
                cursor.execute(sql, (id_usuario,))
                usuario_data = cursor.fetchone()
                if usuario_data:
                    usuario = {
                        'id_usuario': usuario_data['id_usuario'],
                        'nombre': usuario_data['nombre'],
                        'apellidoP': usuario_data['apellidoP'],
                        'apellidoM': usuario_data['apellidoM']
                    }
                    respuesta['data'] = usuario
                else:
                    respuesta['codigo'] = 404
                    respuesta['mensaje'] = f"Usuario con ID {id_usuario} no encontrado"
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = f"Error al buscar usuario: {str(ex)}"
        finally:
            self.oconexion.db.close()
        return respuesta