

# Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector

def connectionBD():
    try:
        connection = mysql.connector.connect(
            host="b3n9f9pgc9p0mwukdhdw-mysql.services.clever-cloud.com",
            user="ulzydw4lytbtwqcu",
            password="85eKV71nVTrStw3uQgEp",  # Asegúrate de usar la contraseña correcta
            database="b3n9f9pgc9p0mwukdhdw",
            port=3306,  # Cambia el puerto si es necesario
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if connection.is_connected():
            # print("Conexión exitosa a la BD")
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
