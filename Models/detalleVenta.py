from Data.conexion import conexion
from datetime import datetime, date
from Models.producto import producto

class detalleVenta:
    oconexion = conexion()

    def __init__(self, id_venta=None, id_producto=None, cantidad=None, precio_unitario=None, subtotal=None):
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        # Ajustar el cálculo del subtotal para manejar casos de None
        if cantidad is not None and precio_unitario is not None:
            self.subtotal = subtotal if subtotal is not None else cantidad * precio_unitario
        else:
            self.subtotal = subtotal
        self.oconexion = conexion()

    def registrar(self):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                parametros = [self.id_venta, self.id_producto, self.cantidad, self.precio_unitario, self.subtotal]
                sql = 'INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(sql, parametros)
                
                # No se requiere actualizar el stock del producto aquí, ya que se hace en ventaProducto.registrarVenta

                self.oconexion.getConexion().commit()

        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)

        return respuesta
    def obtener_por_id(self, id_venta):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto',
            'detalles': []
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                sql = 'SELECT * FROM detalle_venta WHERE id_venta = %s'
                cursor.execute(sql, (id_venta,))
                detalles = cursor.fetchall()
                for detalle in detalles:
                    detalle_info = {
                        'id_detalle': detalle['id_detalle'],
                        'id_venta': detalle['id_venta'],
                        'id_producto': detalle['id_producto'],
                        'cantidad': detalle['cantidad'],
                        'precio_unitario': detalle['precio_unitario'],
                        'subtotal': detalle['subtotal']
                    }
                    respuesta['detalles'].append(detalle_info)
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)

        return respuesta
    
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
    
    def revertir_venta(self, id_venta):
        respuesta = {'codigo': 0, 'mensaje': 'Proceso correcto'}
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                detalles_respuesta = self.obtener_por_id(id_venta)
                if detalles_respuesta['codigo'] != 0:
                    raise Exception(detalles_respuesta['mensaje'])

                detalles = detalles_respuesta['detalles']
                for detalle in detalles:
                    producto_id = detalle['id_producto']
                    cantidad = detalle['cantidad']
                    # Revertir el stock de los productos vendidos
                    respuesta_stock = self.actualizar_stock(producto_id, cantidad)
                    if respuesta_stock['codigo'] != 0:
                        raise Exception(respuesta_stock['mensaje'])

                # Eliminar los detalles de la venta revertida (opcional)
                sql_eliminar = 'DELETE FROM detalle_venta WHERE id_venta = %s'
                cursor.execute(sql_eliminar, (id_venta,))
                self.oconexion.db.commit()

        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
            self.oconexion.db.rollback()

        return respuesta