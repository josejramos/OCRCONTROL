from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import psycopg2
from psycopg2 import sql
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def connect_db():
    return psycopg2.connect(
        dbname="controle", user="postgres", password="1234", host="localhost"
    )

def fetch_records(table, start_date=None, end_date=None):
    conn = connect_db()
    cursor = conn.cursor()
    if start_date and end_date:
        query = sql.SQL("SELECT placa, data, hora, img FROM {} WHERE data BETWEEN %s AND %s ORDER BY data, hora").format(sql.Identifier(table))
        cursor.execute(query, (start_date, end_date))
    else:
        query = sql.SQL("SELECT placa, data, hora, img FROM {} ORDER BY data, hora").format(sql.Identifier(table))
        cursor.execute(query)
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
        # Adiciona registro na tabela de entrada
        query = sql.SQL("INSERT INTO {} (placa, data, hora) VALUES (%s, %s, %s)").format(sql.Identifier(table))
        cursor.execute(query, (placa, data, hora))

        # Adiciona o mesmo registro na tabela de registro_placas
        query = sql.SQL("INSERT INTO registro_placas (placa) VALUES (%s)")
        cursor.execute(query, (placa,))

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
        if 'filter' in request.form:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            table = request.form.get('table')
            if start_date and end_date:
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    flash("Formato de data inválido. Use YYYY-MM-DD.")
                    return redirect(url_for('index'))

                records = fetch_records(table, start_date, end_date)
                return render_template('index.html', records=records, table=table, show_section='filter')
            else:
                flash("Por favor, preencha as datas inicial e final.")
                return redirect(url_for('index'))

        elif 'show_all_entries' in request.form:
            records = fetch_records("entrada")
            return render_template('index.html', records=records, table="entrada", show_section='entries')

        elif 'show_all_exits' in request.form:
            records = fetch_records("saida")
            return render_template('index.html', records=records, table="saida", show_section='entries')

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

@app.route('/image/<record_id>')
def image(record_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = sql.SQL("SELECT img FROM entrada WHERE placa = %s").format(sql.Identifier('entrada'))
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
    records = fetch_records("entrada")
    return render_template('entrada.html', records=records)

@app.route('/exits')
def show_exits():
    records = fetch_records("saida")
    return render_template('saida.html', records=records)

if __name__ == "__main__":
    app.run(debug=True)
