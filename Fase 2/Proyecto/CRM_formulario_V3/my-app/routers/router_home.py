from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify, Flask
from mysql.connector.errors import Error


# Importando conexión a BD
from controllers.funciones_home import *

import pymysql

PATH_URL = "public/empleados"


@app.route('/registrar-empleado', methods=['GET'])
def viewFormEmpleado():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-empleado', methods=['POST'])
def formEmpleado():
    if 'conectado' in session:
        if 'foto_empleado' in request.files:
            foto_perfil = request.files['foto_empleado']
            resultado = procesar_form_empleado(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_empleados'))
            else:
                flash('El empleado NO fue registrado.', 'error')
                return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/lista-de-empleados', methods=['GET'])
def lista_empleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/lista_empleados.html', empleados=sql_lista_empleadosBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-empleado/", methods=['GET'])
@app.route("/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def detalleEmpleado(idEmpleado=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idEmpleado es None o no está presente en la URL
        if idEmpleado is None:
            return redirect(url_for('inicio'))
        else:
            detalle_empleado = sql_detalles_empleadosBD(idEmpleado) or []
            return render_template(f'{PATH_URL}/detalles_empleado.html', detalle_empleado=detalle_empleado)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Buscadon de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            return render_template(f'{PATH_URL}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Recibir formulario para actulizar informacion de empleado
@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))


@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Dashboard
@app.route('/dashboard', methods=['GET'])
def viewDashboard():
    if 'conectado' in session:
        return render_template('public/empleados/dashboard.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Contactos
@app.route('/registrar-contactos', methods=['GET'])
def viewContacto():
    if 'conectado' in session:
        return render_template('public/empleados/form_contacto.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Ruta para mostrar el formulario de edición de contacto
@app.route('/editar_contacto/<int:id_contacto>', methods=['GET'])
def editar_contacto(id_contacto):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    # Selecciona el contacto a editar
                    cursor.execute("SELECT * FROM tbl_contactos WHERE id_contacto = %s", (id_contacto,))
                    contacto = cursor.fetchone()
            return render_template('public/empleados/form_editar_contacto.html', contacto=contacto)
        except Exception as e:
            flash(f'Error al obtener los datos del contacto: {str(e)}', 'error')
            return redirect(url_for('lista_contactos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta para procesar la actualización del contacto
@app.route('/actualizar_contacto', methods=['POST'])
def actualizar_contacto():
    if 'conectado' in session:
        id_contacto = request.form.get('id_contacto')
        # Obtener los datos actualizados desde el formulario
        datos_contacto = {
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'teléfono': request.form.get('teléfono'),
            'empresa': request.form.get('empresa'),
            'sexo_empleado': request.form.get('sexo_empleado'),
            'propietario': request.form.get('propietario'),
            'foto_empleado': request.form.get('foto_empleado'),
            'id_miembro_responsable': request.form.get('id_miembro_responsable')
        }
        
        # Llamar a la función de procesamiento para actualizar el contacto
        resultado = procesar_actualizacion_contacto(id_contacto, datos_contacto)
        
        # Redireccionar según el resultado
        if resultado:
            flash('Contacto actualizado exitosamente.', 'success')
        else:
            flash('Error al actualizar el contacto.', 'error')
        return redirect(url_for('lista_contactos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/eliminar_contacto/<int:id_contacto>', methods=['POST'])
def eliminar_contacto(id_contacto):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    # Ejecutar la consulta para eliminar el contacto
                    sql = "DELETE FROM tbl_contactos WHERE id_contacto = %s"
                    cursor.execute(sql, (id_contacto,))
                    conexion_MySQLdb.commit()
            
            flash('Contacto eliminado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al eliminar el contacto: {str(e)}', 'error')
        
        # Redirigir de nuevo a la lista de contactos
        return redirect(url_for('lista_contactos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    
# Ruta para agregar contacto
@app.route('/add_contacto', methods=['POST'])
def addContacto():
    if 'conectado' in session:
        # Obtener los datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        teléfono = request.form.get('teléfono')
        empresa = request.form.get('empresa')
        sexo_empleado = request.form.get('sexo_empleado')
        propietario = request.form.get('propietario')
        foto_empleado = request.files['foto_empleado'].read() if 'foto_empleado' in request.files else None
        id_miembro_responsable = request.form.get('id_miembro_responsable')
        
        # Empaquetar los datos en un diccionario
        datos_contacto = {
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'teléfono': teléfono,
            'empresa': empresa,
            'sexo_empleado': sexo_empleado,
            'propietario': propietario,
            'foto_empleado': foto_empleado,
            'id_miembro_responsable': id_miembro_responsable
        }
        
        # Llamar a la función de procesamiento
        resultado = procesar_form_contacto(datos_contacto)
        
        # Verificar si el contacto se agregó correctamente
        if isinstance(resultado, int) and resultado > 0:
            flash('Contacto agregado exitosamente', 'success')
            return redirect(url_for('lista_contactos'))
        else:
            flash(f'Error al agregar el contacto: {resultado}', 'error')
            return render_template('public/empleados/form_contacto.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/lista_contactos', methods=['GET'])
def lista_contactos():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM tbl_contactos")
                    contactos = cursor.fetchall()
            return render_template('public/empleados/lista_contactos.html', contactos=contactos)
        except Exception as e:
            flash(f'Error al obtener la lista de contactos: {str(e)}', 'error')
            return render_template('public/empleados/lista_contactos.html', contactos=[])
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    
# Eventos
@app.route('/registrar-eventos', methods=['GET'])
def viewEvento():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    # Recuperar clientes para el desplegable
                    cursor.execute("SELECT id_contacto, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM tbl_contactos")
                    clientes = cursor.fetchall()
                    # Recuperar empleados para el desplegable
                    cursor.execute("SELECT id_empleado, CONCAT(nombre_empleado, ' ', apellido_empleado) AS nombre_completo FROM tbl_empleados")
                    empleados = cursor.fetchall()
            return render_template('public/empleados/form_evento.html', clientes=clientes , empleados=empleados)
        except Exception as e:
            flash(f'Error al cargar los clientes: {str(e)}', 'error')
        return redirect(url_for('lista_eventos'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Ruta para agregar un evento
@app.route('/add_evento', methods=['POST'])
def addEvento():
    if 'conectado' in session:
        # Obtener datos del formulario
        nombre_evento = request.form.get('nombre_evento')
        descripcion = request.form.get('descripcion')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_termino = request.form.get('fecha_termino')
        ubicacion = request.form.get('ubicacion')
        id_cliente = request.form.get('id_cliente')
        id_miembro_responsable = request.form.get('id_miembro_responsable')
        asistencia = request.form.get('asistencia')
        foto_empleado = request.form.get('foto_empleado')  # En caso de archivo

        # Empaquetar datos para la función de procesamiento
        datos_evento = {
            'nombre_evento': nombre_evento,
            'descripcion': descripcion,
            'fecha_inicio': fecha_inicio,
            'fecha_termino': fecha_termino,
            'ubicacion': ubicacion,
            'id_cliente': id_cliente,
            'id_miembro_responsable': id_miembro_responsable,
            'asistencia': asistencia,
            'foto_empleado': foto_empleado
        }

        # Llamar a la función de procesamiento
        resultado = procesar_form_evento(datos_evento)

        # Verificar si se agregó correctamente
        if isinstance(resultado, int) and resultado > 0:
            flash('Evento agregado exitosamente', 'success')
            return redirect(url_for('lista_eventos'))
        else:
            flash(f'Error al agregar el evento: {resultado}', 'error')
            return render_template('public/empleados/form_evento.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Ruta para listar eventos
@app.route('/lista_eventos', methods=['GET'])
def lista_eventos():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM tbl_eventos")
                    eventos = cursor.fetchall()
            return render_template('public/empleados/lista_eventos.html', eventos=eventos)
        except Exception as e:
            flash(f'Error al obtener la lista de eventos: {str(e)}', 'error')
            return render_template('public/empleados/lista_eventos.html', eventos=[])
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/modificar_evento/<int:id_evento>', methods=['GET', 'POST'])
def modificar_evento(id_evento):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    if request.method == 'POST':
                        dataForm = {
                            'nombre_evento': request.form.get('nombre_evento'),
                            'descripcion': request.form.get('descripcion'),
                            'fecha_inicio': request.form.get('fecha_inicio'),
                            'fecha_termino': request.form.get('fecha_termino'),
                            'ubicacion': request.form.get('ubicacion'),
                            'id_cliente': int(request.form.get('id_cliente')),
                            'id_miembro_responsable': int(request.form.get('id_miembro_responsable')),
                            'asistencia': int(request.form.get('asistencia'))
                        }
                        sql = """UPDATE tbl_eventos SET nombre_evento=%s, descripcion=%s, fecha_inicio=%s, 
                                 fecha_termino=%s, ubicacion=%s, id_cliente=%s, id_miembro_responsable=%s, 
                                 asistencia=%s WHERE id_evento=%s"""
                        cursor.execute(sql, (*dataForm.values(), id_evento))
                        conexion_MySQLdb.commit()
                        flash('Evento modificado exitosamente', 'success')
                        return redirect(url_for('lista_eventos'))
                    else:
                        cursor.execute("SELECT * FROM tbl_eventos WHERE id_evento = %s", (id_evento,))
                        evento = cursor.fetchone()
            return render_template('public/empleados/form_editar_evento.html', evento=evento)
        except Exception as e:
            flash(f'Error al modificar el evento: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/eliminar_evento/<int:id_evento>', methods=['POST'])
def eliminar_evento(id_evento):
    if 'conectado' in session:
        try:
            # Iniciar la conexión y definir el cursor
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    # Consulta SQL para eliminar el evento por ID
                    sql = "DELETE FROM tbl_eventos WHERE id_evento = %s"
                    cursor.execute(sql, (id_evento,))
                    conexion_MySQLdb.commit()

            flash('Evento eliminado con éxito.', 'success')
        except Exception as e:
            flash(f'Error al eliminar el evento: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')

    return redirect(url_for('lista_eventos'))
    
# Proyectos
@app.route('/registrar-proyectos', methods=['GET'])
def viewProyecto():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    # Recuperar clientes para el desplegable
                    cursor.execute("SELECT id_contacto, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM tbl_contactos")
                    clientes = cursor.fetchall()
                    # Recuperar empleados para el desplegable
                    cursor.execute("SELECT id_empleado, CONCAT(nombre_empleado, ' ', apellido_empleado) AS nombre_completo FROM tbl_empleados")
                    empleados = cursor.fetchall()
            return render_template('public/empleados/form_proyecto.html', clientes=clientes, empleados=empleados)
        except Exception as e:
            flash(f'Error al cargar los clientes: {str(e)}', 'error')
            return redirect(url_for('lista_proyectos'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/add_proyecto', methods=['POST'])
def add_proyecto():
    if 'conectado' in session:
        # Obtener los datos del formulario
        nombre_proyecto = request.form.get('nombre_proyecto')
        descripcion = request.form.get('descripcion')
        tipo_evento = request.form.get('tipo_evento')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        id_cliente = request.form.get('id_cliente')
        id_miembro_responsable = request.form.get('id_miembro_responsable')

        # Empaquetar los datos en un diccionario
        datos_proyecto = {
            'nombre_proyecto': nombre_proyecto,
            'descripcion': descripcion,
            'tipo_evento': tipo_evento,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'id_cliente': id_cliente,
            'id_miembro_responsable': id_miembro_responsable
        }

        # Llamar a la función de procesamiento
        resultado = procesar_form_proyecto(datos_proyecto)
        
        # Verificar si el proyecto se agregó correctamente
        if isinstance(resultado, int) and resultado > 0:
            flash('Proyecto agregado exitosamente', 'success')
            return redirect(url_for('lista_proyectos'))
        else:
            flash(f'Error al agregar el proyecto: {resultado}', 'error')
            return render_template('public/empleados/form_proyecto.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/lista_proyectos', methods=['GET'])
def lista_proyectos():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM tbl_proyectos")
                    proyectos = cursor.fetchall()
            return render_template('public/empleados/lista_proyectos.html', proyectos=proyectos)
        except Exception as e:
            flash(f'Error al obtener la lista de proyectos: {str(e)}', 'error')
            return render_template('public/empleados/lista_proyectos.html', proyectos=[])
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Función para mostrar el formulario de edición de un proyecto
@app.route('/editar_proyecto/<int:id_proyecto>', methods=['GET', 'POST'])
def editar_proyecto(id_proyecto):
    if 'conectado' in session:
        if request.method == 'POST':
            # Obtener los datos del formulario de edición
            nombre_proyecto = request.form.get('nombre_proyecto')
            descripcion = request.form.get('descripcion')
            tipo_evento = request.form.get('tipo_evento')
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            id_cliente = request.form.get('id_cliente')
            id_miembro_responsable = request.form.get('id_miembro_responsable')

            # Llamar a la base de datos para actualizar el proyecto
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor() as cursor:
                        sql = """
                            UPDATE tbl_proyectos 
                            SET nombre_proyecto = %s, descripcion = %s, tipo_evento = %s, fecha_inicio = %s, 
                                fecha_fin = %s, id_cliente = %s, id_miembro_responsable = %s 
                            WHERE id_proyecto = %s
                        """
                        cursor.execute(sql, (nombre_proyecto, descripcion, tipo_evento, fecha_inicio,
                                             fecha_fin, id_cliente, id_miembro_responsable, id_proyecto))
                        conexion_MySQLdb.commit()
                flash('Proyecto actualizado con éxito.', 'success')
                return redirect(url_for('lista_proyectos'))
            except Exception as e:
                flash(f'Error al actualizar el proyecto: {str(e)}', 'error')
        else:
            # Obtener los datos actuales del proyecto para mostrar en el formulario
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        cursor.execute("SELECT * FROM tbl_proyectos WHERE id_proyecto = %s", (id_proyecto,))
                        proyecto = cursor.fetchone()
            except Exception as e:
                flash(f'Error al cargar el proyecto: {str(e)}', 'error')
                return redirect(url_for('lista_proyectos'))

            return render_template('public/empleados/form_editar_proyecto.html', proyecto=proyecto)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/eliminar_proyecto/<int:id_proyecto>', methods=['POST'])
def eliminar_proyecto(id_proyecto):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    cursor.execute("DELETE FROM tbl_proyectos WHERE id_proyecto = %s", (id_proyecto,))
                    conexion_MySQLdb.commit()
            flash('Proyecto eliminado con éxito.', 'success')
        except Exception as e:
            flash(f'Error al eliminar el proyecto: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')
    return redirect(url_for('lista_proyectos'))

    
# Tickets
@app.route('/registrar-tickets', methods=['GET'])
def viewTicket():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    # Recuperar usuarios para el desplegable
                    cursor.execute("SELECT id, name_surname FROM users")
                    usuarios = cursor.fetchall()
                    cursor.execute("SELECT id_empleado, CONCAT(nombre_empleado, ' ', apellido_empleado) AS nombre_completo FROM tbl_empleados")
                    empleados = cursor.fetchall()
            return render_template('public/empleados/form_ticket.html', usuarios=usuarios, empleados=empleados)
        except Exception as e:
            flash(f'Error al cargar los usuarios: {str(e)}', 'error')
            return redirect(url_for('lista_tickets'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Ruta para listar los tickets
@app.route('/lista_tickets', methods=['GET'])
def lista_tickets():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM tbl_tickets")
                    tickets = cursor.fetchall()
            return render_template('public/empleados/lista_tickets.html', tickets=tickets)
        except Exception as e:
            flash(f'Error al obtener la lista de tickets: {str(e)}', 'error')
            return render_template('public/empleados/lista_tickets.html', tickets=[])
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/add_ticket', methods=['POST'])
def addTicket():
    if 'conectado' in session:
        # Obtener los datos del formulario
        datos_ticket = {
            'titulo_ticket': request.form.get('titulo_ticket'),
            'descripcion_ticket': request.form.get('descripcion_ticket'),
            'tipo_ticket': request.form.get('tipo_ticket'),
            'id_user': request.form.get('id_user'),
            'id_empleado_asignado': request.form.get('id_empleado_asignado')
        }
        
        # Llamar a la función de procesamiento
        resultado = procesar_form_ticket(datos_ticket)
        
        # Verificar si el procesamiento fue exitoso
        if isinstance(resultado, tuple):
            try:
                # Conectar a la base de datos e insertar el ticket
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        sql = """
                            INSERT INTO tbl_tickets 
                            (titulo_ticket, descripcion_ticket, tipo_ticket, id_user, id_empleado_asignado) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        
                        cursor.execute(sql, resultado)
                        conexion_MySQLdb.commit()

                        # Confirmar éxito si se inserta correctamente
                        if cursor.rowcount > 0:
                            flash('Ticket agregado exitosamente.', 'success')
                        else:
                            flash('No se pudo agregar el ticket.', 'error')
            
            except Exception as e:
                flash(f"Error al agregar el ticket: {e}", 'error')
                print(f"Error en addTicket: {e}")

            return redirect(url_for('tickets'))
        
        else:
            # Si el procesamiento falló, mostrar el mensaje de error
            flash(resultado, 'error')
            return render_template('public/empleados/form_ticket.html')
    
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Función para mostrar el formulario de edición de un ticket
@app.route('/editar_ticket/<int:id_ticket>', methods=['GET', 'POST'])
def editar_ticket(id_ticket):
    if 'conectado' in session:
        if request.method == 'POST':
            # Obtener datos del formulario
            titulo_ticket = request.form.get('titulo_ticket')
            descripcion_ticket = request.form.get('descripcion_ticket')
            tipo_ticket = request.form.get('tipo_ticket')
            id_user = request.form.get('id_user')
            id_empleado_asignado = request.form.get('id_empleado_asignado')

            # Actualizar el ticket en la base de datos
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor() as cursor:
                        sql = """
                            UPDATE tbl_tickets 
                            SET titulo_ticket = %s, descripcion_ticket = %s, tipo_ticket = %s, 
                                id_user = %s, id_empleado_asignado = %s 
                            WHERE id_ticket = %s
                        """
                        cursor.execute(sql, (titulo_ticket, descripcion_ticket, tipo_ticket, id_user, id_empleado_asignado, id_ticket))
                        conexion_MySQLdb.commit()
                flash('Ticket actualizado con éxito.', 'success')
                return redirect(url_for('lista_tickets'))
            except Exception as e:
                flash(f'Error al actualizar el ticket: {str(e)}', 'error')
        else:
            # Obtener datos actuales del ticket para mostrar en el formulario
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        cursor.execute("SELECT * FROM tbl_tickets WHERE id_ticket = %s", (id_ticket,))
                        ticket = cursor.fetchone()
            except Exception as e:
                flash(f'Error al cargar el ticket: {str(e)}', 'error')
                return redirect(url_for('lista_tickets'))

            return render_template('public/empleados/form_editar_ticket.html', ticket=ticket)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/eliminar_ticket/<int:id_ticket>', methods=['POST'])
def eliminar_ticket(id_ticket):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    cursor.execute("DELETE FROM tbl_tickets WHERE id_ticket = %s", (id_ticket,))
                    conexion_MySQLdb.commit()
            flash('Ticket eliminado con éxito.', 'success')
        except Exception as e:
            flash(f'Error al eliminar el ticket: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')
    return redirect(url_for('lista_tickets'))

    
# Ventas
@app.route('/registrar-venta', methods=['GET'])
def viewVenta():
    if 'conectado' in session:
        try:
            # Obtener los clientes de la base de datos
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT id_contacto, nombre FROM tbl_contactos")
                    clientes = cursor.fetchall()
                    print(clientes)
            # Renderizar el formulario, pasando la lista de clientes
            return render_template('public/empleados/form_venta.html', clientes=clientes)

        except Exception as e:
            flash(f'Error al cargar el formulario: {str(e)}', 'error')
            return redirect(url_for('lista_ventas'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/lista_ventas', methods=['GET'])
def lista_ventas():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    sql = "SELECT * FROM tbl_ventas"
                    cursor.execute(sql)
                    ventas = cursor.fetchall()
                    
            return render_template('public/empleados/lista_ventas.html', ventas=ventas)
        
        except Exception as e:
            flash(f"Error al cargar las ventas: {e}", 'error')
            return redirect(url_for('inicio'))
    
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/add_venta', methods=['POST'])
def addVenta():
    if 'conectado' in session:
        # Obtener datos del formulario
        datos_venta = {
            'id_cliente': request.form.get('id_cliente'),
            'proyecto': request.form.get('proyecto'),
            'empresa': request.form.get('empresa'),
            'fecha_cobro': request.form.get('fecha_cobro'),
            'fecha_venta_vencimiento': request.form.get('fecha_venta_vencimiento')
        }
        
        # Llamar a la función de procesamiento
        resultado = procesar_form_venta(datos_venta)
        
        if isinstance(resultado, tuple):
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        sql = """
                            INSERT INTO tbl_ventas 
                            (id_cliente, proyecto, empresa, fecha_cobro, fecha_venta_vencimiento) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, resultado)
                        conexion_MySQLdb.commit()
                        
                        if cursor.rowcount > 0:
                            flash('Venta agregada exitosamente.', 'success')
                        else:
                            flash('No se pudo agregar la venta.', 'error')
            
            except Exception as e:
                flash(f"Error al agregar la venta: {e}", 'error')
                print(f"Error en addVenta: {e}")

            return redirect(url_for('lista_ventas'))
        
        else:
            flash(resultado, 'error')
            return render_template('public/empleados/form_venta.html')
    
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Función para mostrar el formulario de edición de una venta
@app.route('/editar_venta/<int:id_venta>', methods=['GET', 'POST'])
def editar_venta(id_venta):
    if 'conectado' in session:
        if request.method == 'POST':
            id_cliente = request.form['id_cliente']
            proyecto = request.form['proyecto']
            empresa = request.form['empresa']
            fecha_cobro = request.form['fecha_cobro']
            fecha_venta_vencimiento = request.form['fecha_venta_vencimiento']
            
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor() as cursor:
                        sql = """
                            UPDATE tbl_ventas 
                            SET id_cliente = %s, proyecto = %s, empresa = %s, 
                                fecha_cobro = %s, fecha_venta_vencimiento = %s 
                            WHERE id_venta = %s
                        """
                        valores = (id_cliente, proyecto, empresa, fecha_cobro, fecha_venta_vencimiento, id_venta)
                        cursor.execute(sql, valores)
                        conexion_MySQLdb.commit()
                
                flash('Venta actualizada con éxito', 'success')
                return redirect(url_for('lista_ventas'))
            except Exception as e:
                flash(f'Error al actualizar la venta: {str(e)}', 'error')
                return redirect(url_for('lista_ventas'))
        
        # Si es una solicitud GET, se obtienen los datos de la venta actual
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM tbl_ventas WHERE id_venta = %s", (id_venta,))
                    venta = cursor.fetchone()
            return render_template('public/empleados/form_editar_venta.html', venta=venta)
        except Exception as e:
            flash(f'Error al obtener la venta: {str(e)}', 'error')
            return redirect(url_for('lista_ventas'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/eliminar_venta/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    cursor.execute("DELETE FROM tbl_ventas WHERE id_venta = %s", (id_venta,))
                    conexion_MySQLdb.commit()
            flash('Venta eliminada con éxito.', 'success')
        except Exception as e:
            flash(f'Error al eliminar la venta: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')
    return redirect(url_for('lista_ventas'))


# Formulario Tareas
@app.route('/registrar-tarea', methods=['GET'])
def viewFormTarea():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    # Recuperar empleados para asignar la tarea
                    cursor.execute("SELECT id_empleado, CONCAT(nombre_empleado, ' ', apellido_empleado) AS nombre_completo FROM tbl_empleados")
                    empleados = cursor.fetchall()
            return render_template('public/empleados/form_tarea.html', empleados=empleados)
        except Exception as e:
            flash(f'Error al cargar los empleados: {str(e)}', 'error')
            return redirect(url_for('lista_tareas'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# lista tarea
@app.route('/lista_tareas', methods=['GET'])
def lista_tareas():
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    sql = "SELECT * FROM tbl_tareas"
                    cursor.execute(sql)
                    tareas = cursor.fetchall()
                    print("Datos obtenidos:", tareas)  # Depuración

            return render_template('public/empleados/lista_tareas.html', tareas=tareas)

        except Exception as e:
            print("Error al cargar las tareas:", e)  # Depuración
            flash(f"Error al cargar las tareas: {e}", 'error')
            return redirect(url_for('inicio'))

    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))



# agregar tarea
@app.route('/add_tarea', methods=['POST'])
def addTarea():
    if 'conectado' in session:
        # Obtener los datos del formulario
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        proyecto = request.form.get('proyecto')
        estado = request.form.get('estado')  # Texto: 'Por hacer', 'En progreso', etc.
        prioridad = request.form.get('prioridad')  # Texto: 'Alta', 'Media', 'Baja'
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        id_empleado_asignado = request.form.get('id_empleado_asignado')
        
        # Empaquetar los datos en un diccionario para enviarlos a la función procesar_form_tarea
        datos_tarea = {
            'titulo': titulo,
            'descripcion': descripcion,
            'proyecto': proyecto,
            'estado': estado,
            'prioridad': prioridad,
            'fecha_inicio': fecha_inicio,
            'fecha_vencimiento': fecha_vencimiento,
            'id_empleado_asignado': id_empleado_asignado
        }
        
        # Llamar a la función de procesamiento
        resultado = procesar_form_tarea(datos_tarea)
        
        # Verificar si la tarea se agregó correctamente
        if isinstance(resultado, int) and resultado > 0:
            flash('Tarea agregada exitosamente', 'success')
            return redirect(url_for('lista_tareas'))
        else:
            flash(f'Error al agregar la tarea: {resultado}', 'error')
            return render_template('public/empleados/form_tarea.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Función para mostrar el formulario de edición de una tarea
@app.route('/editar_tarea/<int:id_tarea>', methods=['GET', 'POST'])
def editar_tarea(id_tarea):
    if 'conectado' in session:
        if request.method == 'POST':
            # Obtener datos del formulario
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            proyecto = request.form.get('proyecto')
            estado = request.form.get('estado')
            prioridad = request.form.get('prioridad')
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_vencimiento = request.form.get('fecha_vencimiento')
            id_empleado_asignado = request.form.get('id_empleado_asignado')

            # Actualizar la tarea en la base de datos
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor() as cursor:
                        sql = """
                            UPDATE tbl_tareas 
                            SET titulo = %s, descripcion = %s, proyecto = %s, estado = %s, 
                                prioridad = %s, fecha_inicio = %s, fecha_vencimiento = %s, 
                                id_empleado_asignado = %s
                            WHERE id_tarea = %s
                        """
                        cursor.execute(sql, (titulo, descripcion, proyecto, estado, prioridad,
                                             fecha_inicio, fecha_vencimiento, id_empleado_asignado, id_tarea))
                        conexion_MySQLdb.commit()
                flash('Tarea actualizada con éxito.', 'success')
                return redirect(url_for('lista_tareas'))
            except Exception as e:
                flash(f'Error al actualizar la tarea: {str(e)}', 'error')
        else:
            # Obtener datos actuales de la tarea para mostrar en el formulario
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        cursor.execute("SELECT * FROM tbl_tareas WHERE id_tarea = %s", (id_tarea,))
                        tarea = cursor.fetchone()
            except Exception as e:
                flash(f'Error al cargar la tarea: {str(e)}', 'error')
                return redirect(url_for('lista_tareas'))

            return render_template('public/empleados/form_editar_tarea.html', tarea=tarea)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/eliminar_tarea/<int:id_tarea>', methods=['POST'])
def eliminar_tarea(id_tarea):
    if 'conectado' in session:
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor() as cursor:
                    cursor.execute("DELETE FROM tbl_tareas WHERE id_tarea = %s", (id_tarea,))
                    conexion_MySQLdb.commit()
            flash('Tarea eliminada con éxito.', 'success')
        except Exception as e:
            flash(f'Error al eliminar la tarea: {str(e)}', 'error')
    else:
        flash('Primero debes iniciar sesión.', 'error')
    return redirect(url_for('lista_tareas'))

     
# Dashboard

app = Flask(__name__)

try:
    db = pymysql.connect(
        host="b3n9f9pgc9p0mwukdhdw-mysql.services.clever-cloud.com",
        user="ulzydw4lytbtwqcu",
        password="85eKV71nVTrStw3uQgEp",
        database="b3n9f9pgc9p0mwukdhdw",
        port=3306
    )
    print("Conexión a la base de datos exitosa")
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")

@app.route('/dashboard')
def dashboard():
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total_tickets FROM tbl_tickets")
        total_tickets = cursor.fetchone()[0]
        print(f"Total tickets: {total_tickets}")

        cursor.execute("SELECT COUNT(*) as total_proyectos FROM tbl_proyectos")
        total_proyectos = cursor.fetchone()[0]
        print(f"Total proyectos: {total_proyectos}")

        cursor.execute("SELECT COUNT(*) as total_eventos FROM tbl_eventos")
        total_eventos = cursor.fetchone()[0]
        print(f"Total eventos: {total_eventos}")

        cursor.execute("SELECT COUNT(*) as total_ventas FROM tbl_ventas")
        total_ventas = cursor.fetchone()[0]
        print(f"Total ventas: {total_ventas}")
    except Exception as e:
        print(f"Error al realizar las consultas SQL: {e}")
        total_tickets = total_proyectos = total_eventos = total_ventas = 0

    return render_template('dashboard.html', total_tickets=total_tickets, total_proyectos=total_proyectos, total_eventos=total_eventos, total_ventas=total_ventas)

if __name__ == '__main__':
    app.run(debug=True)
