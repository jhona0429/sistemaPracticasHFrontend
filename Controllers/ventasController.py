import os
from flask import send_file,Blueprint, jsonify, request, current_app, Response

from Data.conexion import conexion
from Models.producto import producto
from Models.registroVenta import ventaProducto
from Models.detalleVenta import detalleVenta
from flask_cors import CORS


from datetime import datetime, date


ventas_blueprint = Blueprint('ventas_blueprint', __name__)

CORS(ventas_blueprint, resources={r"/*": {"origins": "http://192.168.0.4:8005"}})

@ventas_blueprint.route('/registrar', methods=['POST'])
def registroVenta():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        data = request.json
        id_usuario = data.get('id_usuario')
        id_cliente = data.get('id_cliente')
        productos = data.get('productos')

        if not id_usuario or not id_cliente or not productos:
            raise Exception("ID de usuario, ID de cliente y productos son requeridos")
        
        # Verificar stock suficiente para cada producto
        for producto_data in productos:
            id_producto = producto_data['id_producto']
            cantidad = producto_data['cantidad']

            # Obtener información del producto
            prod = producto(id_producto=id_producto, codigo=0, nombre='', precio=0.0, stock=0)
            producto_info= prod.buscar_por_id(id_producto)

            if producto_info['codigo'] != 0:
                raise Exception(producto_info['mensaje'])

            stock_actual = producto_info['data']['stock']

            # Validar stock suficiente
            if stock_actual < cantidad:
                raise Exception(f"No hay suficiente stock para el producto {id_producto}")

        # Crear instancia de ventaProducto y registrar la venta
        venta = ventaProducto(id_usuario=id_usuario, id_cliente=id_cliente, descripcion=data.get('descripcion'))
        respuesta_venta = venta.registrarVenta(productos)

        if respuesta_venta['codigo'] != 0:
            raise Exception(respuesta_venta['mensaje'])

        respuesta['mensaje'] = 'Venta registrada correctamente'

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)

@ventas_blueprint.route('/venta/<int:id_venta>', methods=['GET'])
def ver_detalle_venta(id_venta):
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto',
        'venta': {},
        'detalles': [],
        'total': 0
    }

    try:
        # Obtener información de la venta
        venta_prod = ventaProducto(id_usuario=0, id_cliente=0)  
        venta_info = venta_prod.obtener_por_id(id_venta)

        if venta_info['codigo'] != 0:
            raise Exception(venta_info['mensaje'])

        respuesta['venta'] = {
            'Nro. Venta': venta_info['venta']['id_venta'],
            'Fecha': venta_info['venta']['fecha'],
            'Empleado': venta_info['venta']['nombre_usuario'],
            'Cliente': venta_info['venta']['nombre_cliente'],
            'Descripcion': venta_info['venta']['descripcion'],
            'Estado': venta_info['venta']['estado']
        }

        # Obtengo detalles de la venta usando detalleVenta
        detalles_respuesta = detalleVenta().obtener_por_id(id_venta)  # Crear instancia de detalleVenta

        if detalles_respuesta['codigo'] != 0:
            raise Exception(detalles_respuesta['mensaje'])

        detalles = detalles_respuesta['detalles']

        for detalle in detalles:
            producto_info = venta_prod.obtener_info_producto(detalle['id_producto'])

            if producto_info['codigo'] != 0:
                raise Exception(producto_info['mensaje'])

            producto_data = producto_info['producto']

            respuesta['detalles'].append({
                'Nro.': detalle['id_detalle'],
                'Codigo': producto_data['codigo'],
                'Nombre': producto_data['nombre'],
                'Cantidad': detalle['cantidad'],
                'Precio': producto_data['precio'],
                'SubTotal': detalle['cantidad'] * producto_data['precio']
            })

            respuesta['total'] += detalle['cantidad'] * producto_data['precio']

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)

@ventas_blueprint.route('/lista-activas', methods=['GET'])
def listar_ventas_activas():
    respuesta = {'codigo': 0, 'mensaje': 'Proceso correcto', 'ventas_activas': []}

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = '''
                SELECT id_venta, fecha, id_usuario, id_cliente, descripcion, total
                FROM venta
                WHERE estado = 'activo'
            '''
            cursor.execute(sql)
            ventas_activas = cursor.fetchall()

            for venta in ventas_activas:
                venta_info = {
                    'id_venta': venta['id_venta'],
                    'fecha': venta['fecha'].strftime('%d/%m/%Y'),
                    'id_usuario': venta['id_usuario'],  # Aquí debes obtener el nombre completo del usuario
                    'id_cliente': venta['id_cliente'],  # Aquí debes obtener el nombre completo del cliente
                    'descripcion': venta['descripcion'],
                    'total': venta['total']
                }
                respuesta['ventas_activas'].append(venta_info)

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)

@ventas_blueprint.route('/lista-revertidas', methods=['GET'])
def listar_ventas_revertidas():
    respuesta = {'codigo': 0, 'mensaje': 'Proceso correcto', 'ventas_revertidas': []}

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = '''
                SELECT id_venta, fecha, id_usuario, id_cliente, descripcion, total
                FROM venta
                WHERE estado = 'revertido'
            '''
            cursor.execute(sql)
            ventas_revertidas = cursor.fetchall()

            for venta in ventas_revertidas:
                venta_info = {
                    'id_venta': venta['id_venta'],
                    'fecha': venta['fecha'].strftime('%d/%m/%Y'),
                    'id_usuario': venta['id_usuario'],  # Aquí debes obtener el nombre completo del usuario
                    'id_cliente': venta['id_cliente'],  # Aquí debes obtener el nombre completo del cliente
                    'descripcion': venta['descripcion'],
                    'total': venta['total']
                }
                respuesta['ventas_revertidas'].append(venta_info)

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)
@ventas_blueprint.route('/revertir/<int:id_venta>', methods=['PUT'])
def revertir_venta(id_venta):
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        # Llamar al método para revertir la venta en tu clase ventaProducto
        venta_prod = ventaProducto(id_usuario=0, id_cliente=0)  # Ajusta los parámetros según tu implementación
        revertir_respuesta = venta_prod.revertirVenta(id_venta)

        # Verificar el resultado de revertir la venta
        if revertir_respuesta['codigo'] != 0:
            raise Exception(revertir_respuesta['mensaje'])

        respuesta['mensaje'] = revertir_respuesta['mensaje']

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)

@ventas_blueprint.route('/listar-ventas', methods=['GET'])
def listar_ventas():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto',
        'ventas': []
    }

    try:
        with conexion().getConexion().cursor() as cursor:
            sql = '''
                SELECT v.id_venta, v.fecha, v.id_usuario, v.id_cliente, v.descripcion, v.total, v.estado,
                       c.nombre AS nombre_cliente, c.apellidoP, c.apellidoM
                FROM venta v
                INNER JOIN cliente c ON v.id_cliente = c.id_cliente
                ORDER BY v.fecha DESC
            '''
            cursor.execute(sql)
            ventas = cursor.fetchall()

            for venta in ventas:
                # Formatear la fecha correctamente
                fecha_formateada = venta['fecha'].strftime('%d/%m/%Y')

                venta_info = {
                    'id_venta': venta['id_venta'],
                    'fecha': fecha_formateada,
                    'id_usuario': venta['id_usuario'],  # Aquí puedes obtener el nombre completo del usuario si lo deseas
                    'id_cliente': venta['id_cliente'],  # Aquí puedes obtener el nombre completo del cliente si lo deseas
                    'nombre_cliente': f"{venta['nombre_cliente']} {venta['apellidoP']} {venta['apellidoM']}",
                    'descripcion': venta['descripcion'],
                    'total': venta['total'],
                    'estado': venta['estado']
                }
                respuesta['ventas'].append(venta_info)

    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)

    return jsonify(respuesta)


