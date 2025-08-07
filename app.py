from flask import Flask
from flask import render_template, request, redirect, session, send_file, render_template_string
from flask_mysqldb import MySQL
from datetime import datetime
from flask import send_from_directory
import os
from flask_paginate import Pagination, get_page_parameter
from fpdf import FPDF
import io

app=Flask(__name__)
app.secret_key="develoteca"

# configuración de la base de datos
app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='demo_db'
mysql = MySQL(app)

# configuración de Flask-Paginate para paginación
app.config['PAGINATE_PER_PAGE'] = 5 # número de registros por página

def get_paginated_data(table_name, page=None):
  
   # Obtener el número de página actual
    page = page or int(request.args.get(get_page_parameter(), type=int, default=1))

    # configurar la consulta SQL para obtener los registros con paginación
    offset = (page -1) * app.config['PAGINATE_PER_PAGE']
    sql = f"SELECT * FROM {table_name} LIMIT %s, %s"
    datos = (offset, app.config['PAGINATE_PER_PAGE'])

    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    lista_registros_tabla = cursor.fetchall()
    print(lista_registros_tabla)

    # Obtener el total de registros para la pagina
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cursor.fetchone()[0]

    # configurar la paginación
    pagination = Pagination(
        page=page,
        total=total,
        per_page=app.config['PAGINATE_PER_PAGE'],
        css_framework='bootstrap4'
    )

    return lista_registros_tabla, pagination

@app.route('/generar_reporte_pdf')
def generar_reporte_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hola, reporte PDF", ln=True, align='C')

    # Generar el PDF y obtener el contenido como bytes
    pdf_output = pdf.output(dest='S').encode('latin-1')

    # Crear un objeto BytesIO a partir de los bytes del PDF
    pdf_bytes_io = io.BytesIO(pdf_output)

    # Mover el puntero al inicio del archivo
    pdf_bytes_io.seek(0)

    return send_file(pdf_bytes_io, as_attachment=True, download_name='reporte.pdf', mimetype='application/pdf')


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

    # Obtener el número de página actual
    page = request.args.get(get_page_parameter(), type=int, default=1)

    table_name = 'tbl_libros'
    libros, pagination = get_paginated_data(table_name, page)

    return render_template('admin/libros.html', lista_libros=libros, pagination=pagination)


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

@app.route('/admin/libros/seleccionar', methods=['POST', 'GET'])
def admin_libros_seleccionar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    if request.method == 'POST':
        _id=request.form['txtID']
        page = int(request.form['page']) # convertir a entero
        print(_id)

        conexion=mysql.connection
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM tbl_libros WHERE ID=%s", (_id,))
        libro=cursor.fetchone()
        print(libro)
    else:
        libro = None
        page = request.args.get(get_page_parameter(), type=int, default=1)


    table_name = 'tbl_libros'
    libros, pagination = get_paginated_data(table_name, page)

    return render_template('admin/libros.html', registro_libro=libro, lista_libros=libros, pagination=pagination)


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