from flask import Flask, jsonify, request
from dotenv import load_dotenv
import mariadb
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

def obtener_conexion():
    return mariadb.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "EV-SERVICE API funcionando correctamente",
        "estado": "OK"
    })


@app.route("/api")
def api():
    return jsonify({
        "aplicacion": "EV-SERVICE",
        "version": "1.0",
        "mensaje": "API REST activa"
    })


@app.route("/api/prueba-bd")
def prueba_bd():
    conexion = None

    try:
        conexion = obtener_conexion()

        cursor = conexion.cursor()
        cursor.execute("SELECT DATABASE()")
        resultado = cursor.fetchone()

        return jsonify({
            "estado": "OK",
            "mensaje": "Conexión con MariaDB exitosa",
            "base_datos": resultado[0]
        })

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudo conectar con MariaDB",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    datos = request.get_json()

    nombre = datos.get("nombre")
    email = datos.get("email")
    password = datos.get("password")
    rol = datos.get("rol", "Cliente")

    if not nombre or not email or not password:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Nombre, email y contraseña son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, email, password, rol))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Usuario registrado correctamente",
            "id": cursor.lastrowid
        }), 201

    except mariadb.IntegrityError:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "El correo electrónico ya está registrado"
        }), 409

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al registrar usuario",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id, nombre, email, telefono, rol
            FROM usuarios
            ORDER BY id
        """)

        usuarios = cursor.fetchall()

        resultado = []

        for usuario in usuarios:
            resultado.append({
                "id": usuario[0],
                "nombre": usuario[1],
                "email": usuario[2],
                "telefono": usuario[3],
                "rol": usuario[4]
            })

        return jsonify(resultado)

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudieron consultar los usuarios",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/vehiculos", methods=["GET"])
def listar_vehiculos():
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                v.id,
                v.usuario_id,
                u.nombre,
                v.marca,
                v.modelo,
                v.anio,
                v.placa,
                v.kilometraje,
                v.vin,
                v.bateria_kwh,
                v.voltaje
            FROM vehiculos v
            INNER JOIN usuarios u ON v.usuario_id = u.id
            ORDER BY v.id
        """)

        vehiculos = cursor.fetchall()

        resultado = []

        for vehiculo in vehiculos:
            resultado.append({
                "id": vehiculo[0],
                "usuario_id": vehiculo[1],
                "cliente": vehiculo[2],
                "marca": vehiculo[3],
                "modelo": vehiculo[4],
                "anio": vehiculo[5],
                "placa": vehiculo[6],
                "kilometraje": float(vehiculo[7]),
                "vin": vehiculo[8],
                "bateria_kwh": float(vehiculo[9]) if vehiculo[9] is not None else None,
                "voltaje": float(vehiculo[10]) if vehiculo[10] is not None else None
            })

        return jsonify(resultado)

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudieron consultar los vehículos",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/vehiculos", methods=["POST"])
def crear_vehiculo():
    datos = request.get_json()

    usuario_id = datos.get("usuario_id")
    marca = datos.get("marca")
    modelo = datos.get("modelo")
    anio = datos.get("anio")
    placa = datos.get("placa")
    kilometraje = datos.get("kilometraje", 0)
    vin = datos.get("vin")
    bateria_kwh = datos.get("bateria_kwh")
    voltaje = datos.get("voltaje")

    if not usuario_id or not marca or not modelo or not anio or not placa:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Usuario, marca, modelo, año y placa son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO vehiculos
            (
                usuario_id,
                marca,
                modelo,
                anio,
                placa,
                kilometraje,
                vin,
                bateria_kwh,
                voltaje
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_id,
            marca,
            modelo,
            anio,
            placa,
            kilometraje,
            vin,
            bateria_kwh,
            voltaje
        ))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Vehículo registrado correctamente",
            "id": cursor.lastrowid
        }), 201

    except mariadb.IntegrityError:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "La placa ya está registrada"
        }), 409

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al registrar el vehículo",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/vehiculos/<int:vehiculo_id>", methods=["PUT"])
def actualizar_vehiculo(vehiculo_id):
    datos = request.get_json()

    marca = datos.get("marca")
    modelo = datos.get("modelo")
    anio = datos.get("anio")
    placa = datos.get("placa")
    kilometraje = datos.get("kilometraje", 0)
    vin = datos.get("vin")
    bateria_kwh = datos.get("bateria_kwh")
    voltaje = datos.get("voltaje")

    if not marca or not modelo or not anio or not placa:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Marca, modelo, año y placa son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE vehiculos
            SET
                marca = ?,
                modelo = ?,
                anio = ?,
                placa = ?,
                kilometraje = ?,
                vin = ?,
                bateria_kwh = ?,
                voltaje = ?
            WHERE id = ?
        """, (
            marca,
            modelo,
            anio,
            placa,
            kilometraje,
            vin,
            bateria_kwh,
            voltaje,
            vehiculo_id
        ))

        conexion.commit()

        cursor.execute(
         "SELECT id FROM vehiculos WHERE id = ?",
         (vehiculo_id,)
)

        vehiculo = cursor.fetchone()

        if vehiculo is None:
         return jsonify({
            "estado": "ERROR",
            "mensaje": "Vehículo no encontrado"
     }), 404

        return jsonify({
            "estado": "OK",
            "mensaje": "Vehículo actualizado correctamente"
        }), 200

    except mariadb.IntegrityError:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "La placa ya está registrada"
        }), 409

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al actualizar el vehículo",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/vehiculos/usuario/<int:usuario_id>", methods=["GET"])
def obtener_vehiculos_usuario(usuario_id):
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                v.id,
                v.usuario_id,
                v.marca,
                v.modelo,
                v.anio,
                v.placa,
                v.kilometraje,
                v.vin,
                v.bateria_kwh,
                v.voltaje
            FROM vehiculos v
            WHERE v.usuario_id = ?
            ORDER BY v.id
        """, (usuario_id,))

        vehiculos = cursor.fetchall()

        resultado = []

        for vehiculo in vehiculos:
            resultado.append({
                "id": vehiculo[0],
                "usuario_id": vehiculo[1],
                "marca": vehiculo[2],
                "modelo": vehiculo[3],
                "anio": vehiculo[4],
                "placa": vehiculo[5],
                "kilometraje": float(vehiculo[6]),
                "vin": vehiculo[7],
                "bateria_kwh": float(vehiculo[8]) if vehiculo[8] is not None else None,
                "voltaje": float(vehiculo[9]) if vehiculo[9] is not None else None
            })

        return jsonify(resultado), 200

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudieron consultar los vehículos del usuario",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


@app.route("/api/citas", methods=["GET"])
def listar_citas():
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.usuario_id,
                u.nombre,
                c.mecanico_id,
                m.nombre,
                c.vehiculo_id,
                v.marca,
                v.modelo,
                v.placa,
                c.servicio,
                c.fecha,
                c.hora,
                c.descripcion,
                c.estado
            FROM citas c
            INNER JOIN usuarios u
                ON c.usuario_id = u.id
            LEFT JOIN usuarios m
                ON c.mecanico_id = m.id
            INNER JOIN vehiculos v
                ON c.vehiculo_id = v.id
            ORDER BY c.fecha, c.hora
        """)

        citas = cursor.fetchall()

        resultado = []

        for cita in citas:
            resultado.append({
                "id": cita[0],
                "usuario_id": cita[1],
                "cliente": cita[2],
                "mecanico_id": cita[3],
                "mecanico": cita[4],
                "vehiculo_id": cita[5],
                "marca": cita[6],
                "modelo": cita[7],
                "placa": cita[8],
                "servicio": cita[9],
                "fecha": str(cita[10]),
                "hora": str(cita[11]),
                "descripcion": cita[12],
                "estado": cita[13]
            })

        return jsonify(resultado)

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudieron consultar las citas",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/citas", methods=["POST"])
def registrar_cita():
    conexion = None

    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Debe enviar datos JSON válidos"
            }), 400

        usuario_id = datos.get("usuario_id")
        vehiculo_id = datos.get("vehiculo_id")
        servicio = datos.get("servicio")
        fecha = datos.get("fecha")
        hora = datos.get("hora")
        descripcion = datos.get("descripcion", "")

        if not all([
            usuario_id, vehiculo_id, servicio, fecha, hora
        ]):
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Complete todos los campos obligatorios"
            }), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el vehículo pertenezca al cliente
        cursor.execute("""
            SELECT id
            FROM vehiculos
            WHERE id = ? AND usuario_id = ?
        """, (vehiculo_id, usuario_id))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El vehículo no pertenece al cliente"
            }), 400

        cursor.execute("""
            INSERT INTO citas (
                usuario_id,
                vehiculo_id,
                servicio,
                fecha,
                hora,
                descripcion,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
        """, (
            usuario_id,
            vehiculo_id,
            servicio,
            fecha,
            hora,
            descripcion
        ))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Cita registrada correctamente"
        }), 201

    except mariadb.Error as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudo registrar la cita",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


@app.route("/api/historial", methods=["GET"])
def listar_historial():
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                h.id,
                h.usuario_id,
                u.nombre,
                h.vehiculo_id,
                v.marca,
                v.modelo,
                v.placa,
                h.tipo_servicio,
                h.descripcion,
                h.fecha,
                h.kilometraje,
                h.resultado,
                h.observaciones
            FROM historial h
            INNER JOIN usuarios u ON h.usuario_id = u.id
            INNER JOIN vehiculos v ON h.vehiculo_id = v.id
            ORDER BY h.fecha DESC
        """)

        registros = cursor.fetchall()

        resultado = []

        for registro in registros:
            resultado.append({
                "id": registro[0],
                "usuario_id": registro[1],
                "cliente": registro[2],
                "vehiculo_id": registro[3],
                "marca": registro[4],
                "modelo": registro[5],
                "placa": registro[6],
                "tipo_servicio": registro[7],
                "descripcion": registro[8],
                "fecha": str(registro[9]),
                "kilometraje": float(registro[10]) if registro[10] is not None else None,
                "resultado": registro[11],
                "observaciones": registro[12]
            })

        return jsonify(resultado)

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudo consultar el historial",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/vehiculos/<int:vehiculo_id>", methods=["DELETE"])
def eliminar_vehiculo(vehiculo_id):
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM vehiculos WHERE id = ?",
            (vehiculo_id,)
        )

        vehiculo = cursor.fetchone()

        if vehiculo is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Vehículo no encontrado"
            }), 404

        cursor.execute(
            "DELETE FROM vehiculos WHERE id = ?",
            (vehiculo_id,)
        )

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Vehículo eliminado correctamente"
        }), 200

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al eliminar el vehículo",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


@app.route("/api/login", methods=["POST"])
def login():
    conexion = None

    try:
        datos = request.get_json()

        email = datos.get("email")
        password = datos.get("password")

        if not email or not password:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Correo y contraseña son obligatorios"
            }), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id, nombre, email, telefono, password, rol
            FROM usuarios
            WHERE email = ?
        """, (email,))

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Usuario no encontrado"
            }), 401

        if usuario[4] != password:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Contraseña incorrecta"
            }), 401

        return jsonify({
            "estado": "OK",
            "mensaje": "Inicio de sesión correcto",
            "usuario": {
                "id": usuario[0],
                "nombre": usuario[1],
                "email": usuario[2],
                "telefono": usuario[3],
                "rol": usuario[5]
            }
        })

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error de conexión con la base de datos",
            "detalle": str(error)
        }), 500

@app.route("/api/citas/usuario/<int:usuario_id>", methods=["GET"])
def obtener_citas_usuario(usuario_id):
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.usuario_id,
                c.vehiculo_id,
                v.marca,
                v.modelo,
                v.placa,
                c.servicio,
                c.fecha,
                c.hora,
                c.descripcion,
                c.estado,
                c.mecanico_id,
                m.nombre
            FROM citas c
            INNER JOIN vehiculos v
                ON c.vehiculo_id = v.id
            LEFT JOIN usuarios m
                ON c.mecanico_id = m.id
            WHERE c.usuario_id = ?
            ORDER BY c.fecha DESC, c.hora DESC
        """, (usuario_id,))

        citas = cursor.fetchall()

        resultado = []

        for cita in citas:
            resultado.append({
                "id": cita[0],
                "usuario_id": cita[1],
                "vehiculo_id": cita[2],
                "marca": cita[3],
                "modelo": cita[4],
                "placa": cita[5],
                "servicio": cita[6],
                "fecha": str(cita[7]),
                "hora": str(cita[8]),
                "descripcion": cita[9],
                "estado": cita[10],
                "mecanico_id": cita[11],
                "mecanico": cita[12]
            })

        return jsonify(resultado), 200

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "No se pudieron consultar las citas",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/citas/<int:cita_id>/confirmar", methods=["PUT"])
def confirmar_cita(cita_id):
    conexion = None

    try:
        datos = request.get_json()
        mecanico_id = datos.get("mecanico_id")

        if not mecanico_id:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El mecánico es obligatorio"
            }), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el usuario exista y sea Mecánico
        cursor.execute(
            """
            SELECT id, nombre, rol
            FROM usuarios
            WHERE id = ?
            """,
            (mecanico_id,)
        )

        mecanico = cursor.fetchone()

        if mecanico is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Mecánico no encontrado"
            }), 404

        if mecanico[2] != "Mecánico":
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El usuario seleccionado no es mecánico"
            }), 400

        # Buscar la cita
        cursor.execute(
            "SELECT id, estado FROM citas WHERE id = ?",
            (cita_id,)
        )

        cita = cursor.fetchone()

        if cita is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Cita no encontrada"
            }), 404

        if cita[1] != "Pendiente":
            return jsonify({
                "estado": "ERROR",
                "mensaje": "La cita no está pendiente"
            }), 400

        # Confirmar y asignar mecánico
        cursor.execute(
            """
            UPDATE citas
            SET estado = 'Confirmada',
                mecanico_id = ?
            WHERE id = ?
            """,
            (mecanico_id, cita_id)
        )

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Cita confirmada correctamente",
            "mecanico_id": mecanico[0],
            "mecanico": mecanico[1]
        }), 200

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al confirmar la cita",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/citas/<int:cita_id>/atender", methods=["PUT"])
def atender_cita(cita_id):
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, estado FROM citas WHERE id = ?",
            (cita_id,)
        )

        cita = cursor.fetchone()

        if cita is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "Cita no encontrada"
            }), 404

        if cita[1] != "Confirmada":
            return jsonify({
                "estado": "ERROR",
                "mensaje": "La cita debe estar confirmada antes de atenderla"
            }), 400

        cursor.execute(
            """
            UPDATE citas
            SET estado = 'Atendida'
            WHERE id = ?
            """,
            (cita_id,)
        )

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Cita marcada como atendida correctamente"
        }), 200

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al actualizar la cita",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()



@app.route("/api/diagnosticos", methods=["POST"])
def crear_diagnostico():
    datos = request.get_json()

    usuario_id = datos.get("usuario_id")
    vehiculo_id = datos.get("vehiculo_id")
    mecanico_id = datos.get("mecanico_id")
    descripcion = datos.get("descripcion")
    resultado = datos.get("resultado")
    observaciones = datos.get("observaciones")
    kilometraje = datos.get("kilometraje", 0)

    if (
        not usuario_id
        or not vehiculo_id
        or not descripcion
        or not resultado
    ):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Usuario, vehículo, descripción y resultado son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el vehículo pertenezca al cliente
        cursor.execute("""
            SELECT id
            FROM vehiculos
            WHERE id = ? AND usuario_id = ?
        """, (vehiculo_id, usuario_id))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El vehículo no pertenece al cliente indicado"
            }), 400

        # Verificar que el usuario responsable sea mecánico
        cursor.execute("""
            SELECT id
            FROM usuarios
            WHERE id = ? AND LOWER(rol) = 'mecánico'
        """, (mecanico_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El mecánico seleccionado no es válido"
            }), 400


        cursor.execute("""
            INSERT INTO historial
            (
                usuario_id,
                mecanico_id,
                vehiculo_id,
                tipo_servicio,
                descripcion,
                fecha,
                kilometraje,
                resultado,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, CURDATE(), ?, ?, ?)
        """, (
            usuario_id,
            mecanico_id,
            vehiculo_id,
            "Diagnóstico",
            descripcion,
            kilometraje,
            resultado,
            observaciones
        ))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Diagnóstico registrado correctamente",
            "id": cursor.lastrowid
        }), 201

    except mariadb.Error as error:
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al registrar el diagnóstico",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()

@app.route("/api/mantenimientos", methods=["POST"])
def crear_mantenimiento():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Debe enviar datos JSON válidos"
        }), 400

    usuario_id = datos.get("usuario_id")
    vehiculo_id = datos.get("vehiculo_id")
    mecanico_id = datos.get("mecanico_id")
    descripcion = datos.get("descripcion")
    resultado = datos.get("resultado")
    observaciones = datos.get("observaciones")
    kilometraje = datos.get("kilometraje", 0)

    if (
        not usuario_id
        or not vehiculo_id
        or not mecanico_id
        or not descripcion
        or not resultado
    ):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Cliente, vehículo, mecánico, descripción y resultado son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el vehículo pertenezca al cliente
        cursor.execute("""
            SELECT id
            FROM vehiculos
            WHERE id = ? AND usuario_id = ?
        """, (vehiculo_id, usuario_id))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El vehículo no pertenece al cliente indicado"
            }), 400

        # Verificar que el responsable sea mecánico
        cursor.execute("""
            SELECT id
            FROM usuarios
            WHERE id = ? AND LOWER(rol) = 'mecánico'
        """, (mecanico_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El mecánico seleccionado no es válido"
            }), 400

        # Registrar mantenimiento
        cursor.execute("""
            INSERT INTO historial
            (
                usuario_id,
                mecanico_id,
                vehiculo_id,
                tipo_servicio,
                descripcion,
                fecha,
                kilometraje,
                resultado,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, CURDATE(), ?, ?, ?)
        """, (
            usuario_id,
            mecanico_id,
            vehiculo_id,
            "Mantenimiento",
            descripcion,
            kilometraje,
            resultado,
            observaciones
        ))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Mantenimiento registrado correctamente",
            "id": cursor.lastrowid
        }), 201

    except mariadb.Error as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al registrar el mantenimiento",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()



@app.route("/api/cambios-bateria", methods=["POST"])
def crear_cambio_bateria():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Debe enviar datos JSON válidos"
        }), 400

    usuario_id = datos.get("usuario_id")
    vehiculo_id = datos.get("vehiculo_id")
    mecanico_id = datos.get("mecanico_id")
    descripcion = datos.get("descripcion")
    resultado = datos.get("resultado")
    observaciones = datos.get("observaciones")
    kilometraje = datos.get("kilometraje", 0)

    if (
        not usuario_id
        or not vehiculo_id
        or not mecanico_id
        or not descripcion
        or not resultado
    ):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Cliente, vehículo, mecánico, descripción y resultado son obligatorios"
        }), 400

    try:
        kilometraje = float(kilometraje)
        if kilometraje < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "estado": "ERROR",
            "mensaje": "El kilometraje debe ser un número válido"
        }), 400

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el vehículo pertenezca al cliente
        cursor.execute("""
            SELECT id
            FROM vehiculos
            WHERE id = ? AND usuario_id = ?
        """, (vehiculo_id, usuario_id))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El vehículo no pertenece al cliente indicado"
            }), 400

        # Verificar que el responsable sea mecánico
        cursor.execute("""
            SELECT id
            FROM usuarios
            WHERE id = ? AND LOWER(rol) = 'mecánico'
        """, (mecanico_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "estado": "ERROR",
                "mensaje": "El mecánico seleccionado no es válido"
            }), 400

        # Registrar el cambio de batería
        cursor.execute("""
            INSERT INTO historial
            (
                usuario_id,
                mecanico_id,
                vehiculo_id,
                tipo_servicio,
                descripcion,
                fecha,
                kilometraje,
                resultado,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, CURDATE(), ?, ?, ?)
        """, (
            usuario_id,
            mecanico_id,
            vehiculo_id,
            "Cambio de batería",
            descripcion,
            kilometraje,
            resultado,
            observaciones
        ))

        conexion.commit()

        return jsonify({
            "estado": "OK",
            "mensaje": "Cambio de batería registrado correctamente",
            "id": cursor.lastrowid
        }), 201

    except mariadb.Error as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "estado": "ERROR",
            "mensaje": "Error al registrar el cambio de batería",
            "detalle": str(error)
        }), 500

    finally:
        if conexion:
            conexion.close()


if __name__ == "__main__":
    app.run(debug=True)
