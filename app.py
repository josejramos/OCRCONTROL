from flask import Flask, render_template, request, redirect, url_for, send_file, flash ,abort
import psycopg2
from psycopg2 import sql
from datetime import datetime
import io
import os
import signal


app = Flask(__name__)
app.secret_key = 'supersecretkey'

def connect_db():
    return psycopg2.connect(
        dbname="controle", user="postgres", password="1234", host="localhost"
    )

def fetch_records(table, start_date=None, end_date=None, offset=0, limit=20):
    conn = connect_db()
    cursor = conn.cursor()
    if start_date and end_date:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora, img 
            FROM {} 
            WHERE data BETWEEN %s AND %s 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """).format(sql.Identifier(table))
        cursor.execute(query, (start_date, end_date, limit, offset))
    else:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora, img 
            FROM {} 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """).format(sql.Identifier(table))
        cursor.execute(query, (limit, offset))
    records = cursor.fetchall()
    conn.close()
    return records

def count_records(table, start_date=None, end_date=None):
    conn = connect_db()
    cursor = conn.cursor()
    if start_date and end_date:
        query = sql.SQL("SELECT COUNT(DISTINCT placa) FROM {} WHERE data BETWEEN %s AND %s").format(sql.Identifier(table))
        cursor.execute(query, (start_date, end_date))
    else:
        query = sql.SQL("SELECT COUNT(DISTINCT placa) FROM {}").format(sql.Identifier(table))
        cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def fetch_historico_entrada(placa=None, start_date=None, end_date=None, offset=0, limit=20):
    conn = connect_db()
    cursor = conn.cursor()
    if placa and start_date and end_date:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora 
            FROM historico_entrada 
            WHERE placa = %s AND data BETWEEN %s AND %s 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """)
        cursor.execute(query, (placa, start_date, end_date, limit, offset))
    elif placa:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora 
            FROM historico_entrada 
            WHERE placa = %s 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """)
        cursor.execute(query, (placa, limit, offset))
    elif start_date and end_date:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora 
            FROM historico_entrada 
            WHERE data BETWEEN %s AND %s 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """)
        cursor.execute(query, (start_date, end_date, limit, offset))
    else:
        query = sql.SQL("""
            SELECT DISTINCT ON (placa) placa, data, hora 
            FROM historico_entrada 
            ORDER BY placa, data DESC, hora DESC 
            LIMIT %s OFFSET %s
        """)
        cursor.execute(query, (limit, offset))
    records = cursor.fetchall()
    conn.close()
    return records

def update_record(table, placa, new_placa):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = sql.SQL("UPDATE {} SET placa = %s WHERE placa = %s").format(sql.Identifier(table))
        cursor.execute(query, (new_placa, placa))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar registro: {e}")
        return False
    finally:
        conn.close()

def delete_record(table, placa):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = sql.SQL("DELETE FROM {} WHERE placa = %s").format(sql.Identifier(table))
        cursor.execute(query, (placa,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao excluir registro: {e}")
        return False
    finally:
        conn.close()

def add_record(table, placa, data, hora):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Inserir na tabela especificada
        query = sql.SQL("INSERT INTO {} (placa, data, hora) VALUES (%s, %s, %s)").format(sql.Identifier(table))
        cursor.execute(query, (placa, data, hora))
        
        # Inserir na tabela registro_placas
        query = sql.SQL("INSERT INTO registro_placas (placa) VALUES (%s) ON CONFLICT (placa) DO NOTHING")
        cursor.execute(query, (placa,))
        
        # Inserir na tabela historico_entrada
        query = sql.SQL("INSERT INTO historico_entrada (placa, data, hora) VALUES (%s, %s, %s)")
        cursor.execute(query, (placa, data, hora))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar registro: {e}")
        return False
    finally:
        conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'show_all_entries' in request.form:
            records = fetch_records("entrada")
            return render_template('index.html', records=records, table="entrada", show_section='entries')

        elif 'show_all_exits' in request.form:
            records = fetch_records("saida")
            return render_template('index.html', records=records, table="saida", show_section='entries')

        elif 'show_historico' in request.form:
            records = fetch_historico_entrada()
            return render_template('index.html', records=records, table="historico_entrada", show_section='historico')

        elif 'edit_record' in request.form:
            table = request.form.get('table')
            placa = request.form.get('placa')
            new_placa = request.form.get('new_placa')
            if update_record(table, placa, new_placa):
                flash("Registro atualizado com sucesso.")
            else:
                flash("Erro ao atualizar registro.")
            return redirect(url_for('index'))

        elif 'delete_record' in request.form:
            table = request.form.get('table')
            placa = request.form.get('placa')
            if delete_record(table, placa):
                flash("Registro excluído com sucesso.")
            else:
                flash("Erro ao excluir registro.")
            return redirect(url_for('index'))

    return render_template('index.html', records=None, table=None, show_section=None)

@app.route('/image/<table>/<record_id>')
def image(table, record_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = sql.SQL("SELECT img FROM {} WHERE placa = %s").format(sql.Identifier(table))
    cursor.execute(query, (record_id,))
    img = cursor.fetchone()
    conn.close()
    if img and img[0]:
        return send_file(io.BytesIO(img[0]), mimetype='image/jpeg')
    return "Imagem não encontrada", 404

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin8822':  # Senha para acessar a página de administração
            return redirect(url_for('admin_page'))
        else:
            flash("Senha incorreta.")
            return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/admin_page')
def admin_page():
    return render_template('admin.html')

@app.route('/admin/add', methods=['POST'])
def admin_add():
    table = request.form.get('table')
    placa = request.form.get('placa')
    data = request.form.get('data')
    hora = request.form.get('hora')
    if add_record(table, placa, data, hora):
        flash("Registro adicionado com sucesso.")
    else:
        flash("Erro ao adicionar registro.")
    return redirect(url_for('admin_page'))

@app.route('/admin/edit', methods=['POST'])
def admin_edit():
    table = request.form.get('table')
    placa = request.form.get('placa')
    new_placa = request.form.get('new_placa')
    if update_record(table, placa, new_placa):
        flash("Registro atualizado com sucesso.")
    else:
        flash("Erro ao atualizar registro.")
    return redirect(url_for('admin_page'))

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    table = request.form.get('table')
    placa = request.form.get('placa')
    if delete_record(table, placa):
        flash("Registro excluído com sucesso.")
    else:
        flash("Erro ao excluir registro.")
    return redirect(url_for('admin_page'))

@app.route('/entries')
def show_entries():
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    records = fetch_records("entrada", offset=offset, limit=per_page)
    total_records = count_records("entrada")
    total_pages = (total_records + per_page - 1) // per_page
    return render_template('entrada.html', records=records, page=page, total_pages=total_pages)

@app.route('/exits')
def show_exits():
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    records = fetch_records("saida", offset=offset, limit=per_page)
    total_records = count_records("saida")
    total_pages = (total_records + per_page - 1) // per_page
    return render_template('saida.html', records=records, page=page, total_pages=total_pages)

@app.route('/historico_entrada', methods=['GET', 'POST'])
def show_historico_entrada():
    placa = request.form.get('placa', None)
    start_date = request.form.get('start_date', None)
    end_date = request.form.get('end_date', None)
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    records = fetch_historico_entrada(placa, start_date, end_date, offset=offset, limit=per_page)
    total_records = count_records("historico_entrada", start_date, end_date)
    total_pages = (total_records + per_page - 1) // per_page
    return render_template('historico_entrada.html', records=records, page=page, total_pages=total_pages, placa=placa, start_date=start_date, end_date=end_date)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if 'werkzeug.server.shutdown' in request.environ:
        func = request.environ['werkzeug.server.shutdown']
        func()
        return 'Servidor desligado!', 200
    else:
        # Se `werkzeug.server.shutdown` não está disponível, simule a parada do processo
        os.kill(os.getpid(), signal.SIGINT)
        return 'Servidor desligado!', 200

if __name__ == "__main__":
    app.run(debug=True)
