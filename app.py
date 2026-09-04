from app import create_app

# Creamos la instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecutamos el servidor en modo desarrollo (debug=True)
    app.run(debug=True)