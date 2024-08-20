from Data.conexion import conexion

class producto:
    oconexion=conexion()

    def __init__(self, id_producto, codigo, nombre, precio,stock):
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def ingresarProducto(self):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                parametros = (self.codigo, self.nombre, self.precio, self.stock)
                sql = 'INSERT INTO producto (codigo, nombre, precio, stock) VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, parametros)
                
                self.oconexion.getConexion().commit()
                
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
        
        return respuesta
    

    def buscar_por_id(self,id_producto):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        self.oconexion.db.connect() 
        try:
            cursor = self.oconexion.db.cursor()
            sql = 'SELECT * FROM producto WHERE id_producto = %s'
            cursor.execute(sql, (id_producto,))
            producto_data = cursor.fetchone()
            if producto_data:
                producto = {
                    'id_producto': producto_data['id_producto'],
                    'codigo': producto_data['codigo'],
                    'nombre': producto_data['nombre'],
                    'precio': producto_data['precio'],
                    'stock': producto_data['stock']
                }
                respuesta['data'] = producto
            else:
                respuesta['codigo'] = 404
                respuesta['mensaje'] = f"Producto con ID {id_producto} no encontrado"
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = f"Error al buscar producto: {str(ex)}"
        finally:
            self.oconexion.db.close()
        return respuesta
    def actualizar_stock(self, id_producto, cantidad):
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                # Obtener stock actual
                sql_select_stock = 'SELECT stock FROM producto WHERE id_producto = %s'
                cursor.execute(sql_select_stock, (id_producto,))
                stock_actual = cursor.fetchone()['stock']
                
                # Actualizar stock
                nuevo_stock = stock_actual + cantidad
                sql_update_stock = 'UPDATE producto SET stock = %s WHERE id_producto = %s'
                cursor.execute(sql_update_stock, (nuevo_stock, id_producto))
                
                self.oconexion.getConexion().commit()
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
                # Obtener stock actual
                sql_select_stock = 'SELECT stock FROM producto WHERE id_producto = %s'
                cursor.execute(sql_select_stock, (id_producto,))
                stock_actual = cursor.fetchone()['stock']
                
                # Actualizar stock
                nuevo_stock = stock_actual + cantidad
                sql_update_stock = 'UPDATE producto SET stock = %s WHERE id_producto = %s'
                cursor.execute(sql_update_stock, (nuevo_stock, id_producto))
                
                self.oconexion.getConexion().commit()
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
        return respuesta
    
    def actualizarStockPorId(self, id_producto, cantidad):
        # Método para actualizar el stock de un producto por su id_producto
        respuesta = {
            'codigo': 0,
            'mensaje': 'Proceso correcto'
        }
        try:
            with self.oconexion.getConexion().cursor() as cursor:
                # Obtener stock actual
                sql_select_stock = 'SELECT stock FROM producto WHERE id_producto = %s'
                cursor.execute(sql_select_stock, (id_producto,))
                stock_actual = cursor.fetchone()['stock']
                
                # Actualizar stock
                nuevo_stock = stock_actual + cantidad
                sql_update_stock = 'UPDATE producto SET stock = %s WHERE id_producto = %s'
                cursor.execute(sql_update_stock, (nuevo_stock, id_producto))
                
                self.oconexion.getConexion().commit()
        except Exception as ex:
            respuesta['codigo'] = 401
            respuesta['mensaje'] = str(ex)
        
        return respuesta
    
    def listar_productos(self):
        # Método de instancia para listar todos los productos
        self.oconexion.db.connect() 
        try:
                cursor = self.oconexion.db.cursor()
                sql = 'SELECT * FROM producto'
                cursor.execute(sql)
                productos = cursor.fetchall()
                
                # Construir la lista de productos
                lista_productos = []
                for producto_data in productos:
                    producto = {
                        'id_producto': producto_data['id_producto'],
                        'codigo': producto_data['codigo'],
                        'nombre': producto_data['nombre'],
                        'precio': producto_data['precio'],
                        'stock': producto_data['stock']
                    }
                    lista_productos.append(producto)
                
                return lista_productos
                
        except Exception as ex:
            raise Exception(f"Error al listar productos: {str(ex)}")