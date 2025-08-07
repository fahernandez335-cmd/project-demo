from flask import Flask
from flask import render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime
from flask import send_from_directory
import os

app=Flask(__name__)
app.secret_key="develoteca"

# configuración de la base de datos
app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='demo_db'
mysql = MySQL(app)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/libros')
def libros():

    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tbl_libros")
    libros = cursor.fetchall()
    return render_template('sitio/libros.html',lista_libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')


@app.route('/admin/')
def admin_index():
    
    if not 'login' in session:
        return redirect("/admin/login")
     
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _email=request.form['txtEmail']
    _password=request.form['txtPassword']


    sql = "SELECT *, count(*) as n_usuario FROM tbl_usuarios WHERE correo=%s AND password=%s"
    datos = (_email, _password)

    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    lista_usuario = cursor.fetchone()
    n_usuario=lista_usuario[5]

    if n_usuario==1:
        session["usuario_id"]=lista_usuario[0]
        session['usuario_nombre']=lista_usuario[1]
        session['usuario_email']=lista_usuario[2]
        session["usuario_rol"]=lista_usuario[4]
        session["login"]=True
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect("/admin/login")

    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tbl_libros")
    libros = cursor.fetchall()
    print(libros)

    return render_template('admin/libros.html', lista_libros=libros)


@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect("/admin/login")

    _id=request.form.get('id')
    _nombre=request.form['txtNombre']
    _url=request.form['txtUrl']
    _archivo=request.files['txtImagen']

    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)
    else:
        nuevoNombre=None

    if _id:
        # Editar el libro existente
        sql= "UPDATE tbl_libros SET nombre=%s, imagen=%s, url=%s WHERE ID=%s"
        datos=(_nombre, nuevoNombre,_url,_id)

    else:
        # Guardar un nuevo libro
        sql="INSERT INTO tbl_libros (ID, nombre, imagen, url) VALUES (NULL,%s, %s, %s);"
        datos=(_nombre,nuevoNombre,_url)

    conexion=mysql.connection
    cursor=conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()


    # print(request.form['txtNombre'])
    print(_nombre)   
    print(_url)
    print(_archivo)   

    return redirect('/admin/libros')

@app.route('/admin/libros/seleccionar', methods=['POST'])
def admin_libros_seleccionar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connection
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM tbl_libros WHERE ID=%s", (_id,))
    libro=cursor.fetchone()
    print(libro)

    cursor.execute("SELECT * FROM tbl_libros")
    libros = cursor.fetchall()

    return render_template('admin/libros.html', registro_libro=libro, lista_libros=libros )


@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():

    if not 'login' in session:
        return redirect("/admin/login")

    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connection
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM tbl_libros WHERE ID=%s", (_id,))
    libro=cursor.fetchall()
    print(libro)

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))

    conexion=mysql.connection
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM tbl_libros WHERE ID=%s", (_id))
    conexion.commit()

    return redirect('/admin/libros')



if __name__ == '__main__':
    app.run(debug=True)