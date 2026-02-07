from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# Конфигурация базы данных
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'maxim2727',
    'database': 'Barbershop'
}

def get_db_connection():
    """Создает подключение к MySQL."""
    return mysql.connector.connect(**db_config)

# --- ГЛАВНАЯ СТРАНИЦА ---
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    cursor.execute("SELECT * FROM barbers")
    barbers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', services=services, barbers=barbers)

# --- БРОНИРОВАНИЕ ---
@app.route('/booking.html', methods=['GET', 'POST'])
def booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone = request.form.get('phone')
            service = request.form.get('service')
            barber = request.form.get('barber')
            date = request.form.get('date')

            # Используем процедуру регистрации клиента (если есть) или прямой запрос
            cursor.execute("INSERT IGNORE INTO clients (name, phone) VALUES (%s, %s)", (name, phone))
            cursor.execute("SELECT id FROM clients WHERE phone = %s", (phone,))
            c_id = cursor.fetchone()['id']

            cursor.execute("SELECT id FROM services WHERE name = %s", (service,))
            s_id = cursor.fetchone()['id']
            
            cursor.execute("SELECT id FROM barbers WHERE name = %s", (barber,))
            b_id = cursor.fetchone()['id']

            # При вставке сработает триггер trg_after_appointment_insert
            cursor.execute("INSERT INTO appointments (client_id, barber_id, service_id, app_date) VALUES (%s, %s, %s, %s)",
                           (c_id, b_id, s_id, date))
            conn.commit()
            return "SUCCESS"
        except Exception as e:
            return str(e), 500
        finally:
            cursor.close()
            conn.close()

    cursor.execute("SELECT * FROM services")
    s_list = cursor.fetchall()
    cursor.execute("SELECT * FROM barbers")
    b_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('booking.html', services=s_list, barbers=b_list)

# --- ПАНЕЛЬ АДМИНИСТРАТОРА (ОБНОВЛЕННАЯ) ---
@app.route('/admin')
def admin_panel():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Основные данные
        cursor.execute("SELECT * FROM View_FullAppointments")
        appointments = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory")
        inventory = cursor.fetchall()

        # --- 10 ПРЕДСТАВЛЕНИЙ ДЛЯ АДМИНКИ ---
        
        # 1. Выручка (View_BarberRevenue)
        cursor.execute("SELECT * FROM View_BarberRevenue")
        revenues = cursor.fetchall()
        
        # 2. Логи (View_SystemLogs)
        cursor.execute("SELECT * FROM View_SystemLogs")
        logs = cursor.fetchall()

        # 3. Популярные услуги (View_PopularServices)
        cursor.execute("SELECT * FROM View_PopularServices")
        pop_services = cursor.fetchall()

        # 4. Активные клиенты (View_ClientActivity)
        cursor.execute("SELECT * FROM View_ClientActivity")
        top_clients = cursor.fetchall()

        # 5. Загруженность мастеров (View_BarberWorkload)
        cursor.execute("SELECT * FROM View_BarberWorkload")
        workload = cursor.fetchall()

        # 6. Остатки на складе (View_InventoryAlert)
        cursor.execute("SELECT * FROM View_InventoryAlert")
        alerts = cursor.fetchall()

        # 7. Финансы склада (View_InventoryValue)
        cursor.execute("SELECT * FROM View_InventoryValue")
        inv_value = cursor.fetchone()

        # 8. Средний чек (View_AvgCheck)
        cursor.execute("SELECT * FROM View_AvgCheck")
        avg_check = cursor.fetchone()

        # 9. Расписание на сегодня (View_DailySchedule)
        cursor.execute("SELECT * FROM View_DailySchedule")
        today_apps = cursor.fetchall()

        # 10. Общая касса (View_TotalFinance) - заменим на простую сумму
        cursor.execute("SELECT SUM(price) as total FROM View_FullAppointments")
        total_finance = cursor.fetchone()

        cursor.close()
        conn.close()
        
        return render_template('admin.html', 
                               appointments=appointments, inventory=inventory,
                               revenues=revenues, logs=logs, pop_services=pop_services,
                               top_clients=top_clients, workload=workload, alerts=alerts,
                               inv_value=inv_value, avg_check=avg_check, today_apps=today_apps,
                               total_finance=total_finance)
    except Exception as e:
        return f"Ошибка: {e}"

# --- УПРАВЛЕНИЕ СКЛАДОМ (ЧЕРЕЗ ПРОЦЕДУРУ) ---
@app.route('/admin/add-inventory', methods=['POST'])
def add_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Вызываем процедуру sp_AddInventory
    cursor.callproc('sp_AddInventory', [
        request.form.get('item_name'),
        request.form.get('quantity'),
        request.form.get('price')
    ])
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

# --- УДАЛЕНИЕ ЗАПИСИ (ЧЕРЕЗ ПРОЦЕДУРУ) ---
@app.route('/admin/delete-appointment/<int:app_id>', methods=['POST'])
def delete_appointment(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Вызываем процедуру sp_DeleteApp
    cursor.callproc('sp_DeleteApp', [app_id])
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

# --- УДАЛЕНИЕ ТОВАРА ---
@app.route('/admin/delete-inventory/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)