from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando conexión a BD
from controllers.funciones_home import *

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
        return render_template('public/empleados/form_evento.html')
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


    
# Proyectos
@app.route('/registrar-proyectos', methods=['GET'])
def viewProyecto():
    if 'conectado' in session:
        return render_template('public/empleados/form_proyecto.html')
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

    
# Tickets
@app.route('/registrar-tickets', methods=['GET'])
def viewTicket():
    if 'conectado' in session:
        return render_template('public/empleados/form_ticket.html')
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

    
# Ventas
@app.route('/registrar-venta', methods=['GET'])
def viewVenta():
    if 'conectado' in session:
        return render_template('public/empleados/form_venta.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
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



# Formulario Tareas
@app.route('/registrar-tarea', methods=['GET'])
def viewFormTarea():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_tarea.html')
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
                    # Consultar todas las tareas de la base de datos
                    sql = "SELECT id_tarea, titulo, descripcion, proyecto, estado, prioridad, fecha_inicio, fecha_vencimiento, id_empleado_asignado FROM tbl_tareas"
                    cursor.execute(sql)
                    tareas = cursor.fetchall()  # Obtener todas las tareas

            # Enviar las tareas al template para mostrarlas
            return render_template('public/empleados/lista_tareas.html', tareas=tareas)
        
        except Exception as e:
            flash(f'Error al listar las tareas: {str(e)}', 'error')
            return render_template('public/empleados/lista_tareas.html', tareas=[])
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
    
# Formulario evento
@app.route('/form_evento', methods=['GET'])
def viewFormEvento():
    if 'conectado' in session:
        return render_template('public/empleados/form_evento.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Formulario proyecto
@app.route('/form_proyecto', methods=['GET'])
def viewFormProyecto():
    if 'conectado' in session:
        return render_template('public/empleados/form_proyecto.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    
# Formulario ticket
@app.route('/form_ticket', methods=['GET'])
def viewFormTicket():
    if 'conectado' in session:
        return render_template('public/empleados/form_ticket.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# Formulario venta
@app.route('/form_venta', methods=['GET'])
def viewFormVenta():
    if 'conectado' in session:
        return render_template('public/empleados/form_venta.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))