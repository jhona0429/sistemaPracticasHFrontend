from Data.conexion import conexion
from datetime import datetime, date
from Models.producto import producto
from Models.detalleVenta import detalleVenta
from Models.cliente import cliente
from Models.usuario import usuario

class ventaProducto:
    def __init__(self, id_usuario, id_cliente, descripcion=''):
        self.id_usuario = id_usuario
        self.id_cliente = id_cliente
        self.descripcion = descripcion
        self.id_venta = None
        self.oconexion = conexion()

    def registrarVenta(self, productos):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        total_venta = 0

        try:
            # Verificar existencia de usuario
            usuario_existente = usuario().buscar_por_id(self.id_usuario)
            if usuario_existente['codigo'] != 0:
                raise Exception(f"El usuario con ID {self.id_usuario} no existe")

            # Verificar existencia de cliente
            cliente_existente = cliente().buscar_por_id(self.id_cliente)
            if cliente_existente['codigo'] != 0:
                raise Exception(f"El cliente con ID {self.id_cliente} no existe")
            
            ###
            self.oconexion.db.begin()  # Inicia transacción manualmente
            with self.oconexion.getConexion().cursor() as cursor:
                fecha_actual = datetime.now().strftime('%Y-%m-%d')

                # Calcular total de la venta sumando el precio total de cada producto
                total_venta = sum([self.obtener_precio_producto(producto['id_producto']) * producto['cantidad'] for producto in productos])

                parametros = [fecha_actual, self.id_usuario, self.id_cliente, self.descripcion, total_venta]
                sql_venta = '''
                    INSERT INTO venta (fecha, id_usuario, id_cliente, descripcion, total)
                    VALUES (%s, %s, %s, %s, %s)
                '''
                cursor.execute(sql_venta, parametros)
                self.id_venta = cursor.lastrowid
####3
                # Preparar los detalles de la venta para la inserción
                detalles_venta = []
                for producto in productos:
                    producto_id = producto['id_producto']
                    cantidad = producto['cantidad']
                    precio_unitario = self.obtener_precio_producto(producto_id)
                    subtotal = cantidad * precio_unitario
                    detalles_venta.append((self.id_venta, producto_id, cantidad, precio_unitario, subtotal))

                # Insertar los detalles de la venta
                sql_detalle_venta = '''
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                '''
                cursor.executemany(sql_detalle_venta, detalles_venta)

                # Actualizar el stock de cada producto
                for producto in productos:
                    producto_id = producto['id_producto']
                    cantidad = producto['cantidad']
                    respuesta_stock = self.actualizar_stock(producto_id, -cantidad)  # Restar cantidad vendida al stock
 
                if respuesta_stock['codigo'] != 0:
                    raise Exception(respuesta_stock['mensaje'])

                self.oconexion.db.commit()

        except Exception as ex:
            # Revertir transacción en caso de error
            self.oconexion.db.rollback()
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)

        return respuesta
        
    def actualizarTotalVenta(self, total_venta):
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql_update_total = 'UPDATE venta SET total = %s WHERE id_venta = %s'
                cursor.execute(sql_update_total, (total_venta, self.id_venta))
                self.oconexion.db.commit()

        except Exception as ex:
            self.oconexion.db.rollback()
            raise Exception(f"Error al actualizar el total de la venta: {str(ex)}")

    def obtener_por_id(self, id_venta):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto',
            'venta': {}  # Asegúrate de incluir el campo total en la estructura devuelta
        }

        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = '''
                 SELECT v.id_venta, v.fecha, v.id_usuario, u.nombre as nombre_usuario, u.apellidoP as apellidoP_usuario, u.apellidoM as apellidoM_usuario, 
                   v.id_cliente, c.nombre as nombre_cliente, c.apellidoP as apellidoP_cliente, c.apellidoM as apellidoM_cliente,
                   v.descripcion, v.total, v.estado
            FROM venta v
            INNER JOIN usuario u ON v.id_usuario = u.id_usuario
            INNER JOIN cliente c ON v.id_cliente = c.id_cliente
            WHERE v.id_venta = %s
                '''
                cursor.execute(sql, (id_venta,))
                venta = cursor.fetchone()

            if venta:
                # Convertir la fecha a datetime si es necesario
                if isinstance(venta['fecha'], date):
                    fecha_venta = datetime.combine(venta['fecha'], datetime.min.time())
                elif isinstance(venta['fecha'], datetime):
                    fecha_venta = venta['fecha']
                else:
                    raise ValueError("Tipo de fecha no reconocido")

                # Formatear la fecha
                if isinstance(fecha_venta, datetime):
                    fecha_formateada = fecha_venta.strftime('%d/%m/%Y')
                else:
                    fecha_formateada = str(fecha_venta)  # Tratar como cadena si no es datetime

                respuesta['venta'] = {
                   'id_venta': venta['id_venta'],
                'fecha': fecha_formateada,
                'id_usuario': venta['id_usuario'],
                'nombre_usuario': f"{venta['nombre_usuario']} {venta['apellidoP_usuario']} {venta['apellidoM_usuario']}",
                'id_cliente': venta['id_cliente'],
                'nombre_cliente': f"{venta['nombre_cliente']} {venta['apellidoP_cliente']} {venta['apellidoM_cliente']}",
                'descripcion': venta['descripcion'],
                'total': venta['total'],
                'estado': venta['estado']
                }
            else:
                respuesta['codigo'] = 404
                respuesta['mensaje'] = f"No se encontró la venta con ID {id_venta}"
        except Exception as ex:
            respuesta['codigo'] = 400
            respuesta['mensaje'] = str(ex)

        return respuesta

    def obtener_info_producto(self, id_producto):
        try:
            prod = producto(id_producto, 0, "",0, 0)  # Ajusta los valores según tu modelo de producto
            producto_info = prod.buscar_por_id(id_producto)
            return {
                'codigo': 0,
                'mensaje': 'Producto encontrado',
                'producto': producto_info['data']  # Ajusta según cómo devuelves los datos en tu método buscar_por_id
            }
        except Exception as ex:
            return {
                'codigo': 401,
                'mensaje': str(ex)
            }

    def actualizar_stock(self, id_producto, cantidad):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = 'UPDATE producto SET stock = stock + %s WHERE id_producto = %s'
                cursor.execute(sql, (cantidad, id_producto))
                self.oconexion.db.commit()
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
        
        return respuesta
    def obtener_precio_producto(self, id_producto):
        try:
            prod = producto(id_producto, 0, "", 0, 0)  # Inicializar correctamente el producto con id_producto
            producto_info = prod.buscar_por_id(id_producto)
            return producto_info['data']['precio']  # Ajustar según cómo devuelves los datos en buscar_por_id en producto
        except Exception as ex:
            raise Exception(f"No se pudo obtener el precio del producto con ID {id_producto}: {str(ex)}")
        
    def revertirVenta(self, id_venta):
        respuesta = {'codigo': 0, 'mensaje': 'Proceso correcto'}
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                # Obtener los detalles de la venta para revertir el stock
                detalles_respuesta = detalleVenta().obtener_por_id(id_venta)
                if detalles_respuesta['codigo'] != 0:
                    raise Exception(detalles_respuesta['mensaje'])
                
                detalles = detalles_respuesta['detalles']
                for detalle in detalles:
                    producto_id = detalle['id_producto']
                    cantidad = detalle['cantidad']
                    # Actualizar el stock de los productos vendidos
                    respuesta_stock = self.actualizar_stock(producto_id, cantidad)
                    if respuesta_stock['codigo'] != 0:
                        raise Exception(respuesta_stock['mensaje'])
                
                # Actualizar estado de la venta a revertido
                sql_revertir = 'UPDATE venta SET estado = "revertido" WHERE id_venta = %s'
                cursor.execute(sql_revertir, (id_venta,))
                self.oconexion.db.commit()

        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
            self.oconexion.db.rollback()

        return respuesta