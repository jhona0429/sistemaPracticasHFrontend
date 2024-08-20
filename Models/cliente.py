from Data.conexion import conexion

class cliente:
    def __init__(self, id_cliente=None, nombre=None, apellidoP=None, apellidoM=None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellidoP = apellidoP
        self.apellidoM = apellidoM
        self.oconexion = conexion()

    def buscar_por_id(self, id_cliente):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = 'SELECT * FROM cliente WHERE id_cliente = %s'
                cursor.execute(sql, (id_cliente,))
                cliente_data = cursor.fetchone()
                if cliente_data:
                    cliente = {
                        'id_cliente': cliente_data['id_cliente'],
                        'nombre': cliente_data['nombre'],
                        'apellidoP': cliente_data['apellidoP'],
                        'apellidoM': cliente_data['apellidoM']
                    }
                    respuesta['data'] = cliente
                else:
                    respuesta['codigo'] = 404
                    respuesta['mensaje'] = f"Cliente con ID {id_cliente} no encontrado"
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = f"Error al buscar cliente: {str(ex)}"
        finally:
            self.oconexion.db.close()
        return respuesta
    
    def registrar(self):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }

        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = '''
                    INSERT INTO cliente (nombre, apellidoP, apellidoM)
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