from app import app
from flask import render_template, request, flash, redirect, url_for, session
import requests

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *

# Clave secreta de reCAPTCHA
SECRET_KEY = '6Lca13AqAAAAAJLh8vCD3Gkuwk0ddbNQ2_wbemTM'
PATH_URL_LOGIN = "public/login"

@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil', methods=['GET'])
def perfil():
    if 'conectado' in session:
        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session())
    else:
        return redirect(url_for('inicio'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html')


# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelResgisterUserBD():
    if request.method == 'POST' and 'name_surname' in request.form and 'pass_user' in request.form:
        name_surname = request.form['name_surname']
        email_user = request.form['email_user']
        pass_user = request.form['pass_user']

        resultData = recibeInsertRegisterUser(name_surname, email_user, pass_user)
        if resultData != 0:
            flash('La cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('inicio'))
    else:
        flash('El método HTTP es incorrecto', 'error')
        return redirect(url_for('inicio'))


# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil", methods=['POST'])
def actualizarPerfil():
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form)
            if respuesta == 1:
                flash('Los datos fueron actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash('La contraseña actual está incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 2:
                flash('Ambas claves deben ser iguales, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 3:
                flash('La clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil'))
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'email_user' in request.form and 'pass_user' in request.form:
            email_user = str(request.form['email_user'])
            pass_user = str(request.form['pass_user'])

            # Obtener la respuesta del reCAPTCHA
            recaptcha_response = request.form['g-recaptcha-response']
            
            # Verificar el reCAPTCHA
            payload = {
                'secret': SECRET_KEY,
                'response': recaptcha_response
            }
            
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
            result = response.json()

            if result['success']:
                # Comprobando si existe una cuenta
                conexion_MySQLdb = connectionBD()
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE email_user = %s", [email_user])
                account = cursor.fetchone()

                if account:
                    if check_password_hash(account['pass_user'], pass_user):
                        # Crear datos de sesión
                        session['conectado'] = True
                        session['id'] = account['id']
                        session['name_surname'] = account['name_surname']
                        session['email_user'] = account['email_user']

                        flash('La sesión fue correcta.', 'success')
                        return redirect(url_for('inicio'))
                    else:
                        flash('Datos incorrectos, por favor revise.', 'error')
                        return render_template(f'{PATH_URL_LOGIN}/base_login.html')
                else:
                    flash('El usuario no existe, por favor verifique.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('Error en la verificación del CAPTCHA. Intenta de nuevo.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session', methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email_user', None)
            flash('Tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Recuerde que debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
