import os
from flask import Blueprint, jsonify, request
from Data.conexion import conexion
from Models.producto import producto
from pyreportjasper import PyReportJasper

from flask_cors import CORS


producto_blueprint = Blueprint('producto_blueprint', __name__)
CORS(producto_blueprint, resources={r"/*": {"origins": "http://192.168.0.4:8005"}})



@producto_blueprint.route('/registrar', methods=['POST'])
def registrarProducto():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }
    
    try:
        data = request.json
        codigo = data['codigo']
        nombre = data['nombre']
        precio = data['precio']
        stock = data['stock']
        
        if codigo is None or nombre is None or precio is None or stock is None:
            raise Exception("El código, nombre, precio y stock son requeridos")
        
        # Crear instancia de producto
        product = producto(None, codigo, nombre, precio, stock)  # id_producto se deja como None
        
        # Llamar al método para ingresar el producto
        respuesta = product.ingresarProducto()
        
    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)
        
    return jsonify(respuesta)

@producto_blueprint.route('/buscar/<int:id_producto>', methods=['GET'])
def buscarProductoPorId(id_producto):
    busqueda = producto(id_producto, 0, "", 0, 0) 
    respuesta = busqueda.buscar_por_id(id_producto)
    return jsonify(respuesta)

@producto_blueprint.route('/actualizar-stock/<int:id_producto>', methods=['PUT'])
def actualizarStock(id_producto):
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }
    
    try:
        data = request.json
        cantidad = data.get('cantidad')
        
        if cantidad is None:
            raise Exception("La cantidad a actualizar es requerida")
        
        # Crear instancia de producto y llamar al método para actualizar el stock
        prod = producto(id_producto, 0, '', 0.0, 0)  # Se inicializa con valores mínimos
        respuesta = prod.actualizarStockPorId(id_producto, cantidad)
        
    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)
    
    return jsonify(respuesta)

@producto_blueprint.route('/listar', methods=['GET'])
def listarProductos():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }
    
    try:
        prod = producto(None, 0, "", 0, 0)  # Crear una instancia de producto
        productos = prod.listar_productos()  # Llamar al método de instancia para listar productos
        respuesta['productos'] = productos
        
    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)
        
    return jsonify(respuesta)

@producto_blueprint.route('/reporte-productos', methods=['GET'])
def generar_reporteProductos():
    respuesta = {
        'codigo': 0,
        'mensaje': 'Proceso correcto'
    }

    try:
        # Directorio donde se encuentran los archivos del reporte
        REPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'reports')
        input_file = os.path.join(REPORTS_DIR, 'reporteProducto.jrxml')
        output_file = os.path.join(REPORTS_DIR, 'reporteProducto.pdf')

        # Configuración de conexión a la base de datos
        jdbc_url = (
            'jdbc:mysql://localhost:3306/sistemaventa'
            '?user=root&password=admin'
            '&serverTimezone=America/Guayaquil'
        )
        conn = {
            'driver': 'mysql',
            'username': 'root',
            'password': 'admin',
            'host': 'localhost',
            'database': 'sistemaventa',
            'port': '3306',
            'jdbc_driver': 'com.mysql.cj.jdbc.Driver',
            'jdbc_url': jdbc_url,
            'jdbc_params': {'serverTimezone': 'America/Guayaquil'},
            'jdbc_dir': 'C:/Users/Alumno/AppData/Local/Programs/Python/Python312/Lib/site-packages/pyreportjasper/libs'
        }

        # Configuración y generación del reporte
        pyreportjasper = PyReportJasper()
       

        pyreportjasper.config(
            input_file,
            output_file,
            db_connection=conn,
            output_formats=["pdf"],
           
        )
        pyreportjasper.process_report()
    
        return jsonify({"message": "Reporte generado con éxito"}), 200
    

    except FileNotFoundError as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = f"Archivo no encontrado: {str(ex)}"
        print("FileNotFoundError:", str(ex))
        return jsonify(respuesta), 500
    
    except Exception as ex:
        respuesta['codigo'] = 400
        respuesta['mensaje'] = str(ex)
        print("Exception:" + str(ex))
        return jsonify(respuesta), 500
    finally:
        print("Finalizando !!!")

