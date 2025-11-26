from flask import Flask, render_template, request, redirect, url_for, send_file, session
import sqlite3
import csv
import io
from datetime import datetime

app = Flask(__name__)

# ==== ΑΛΛΑΞΕ ΜΟΝΟ ΑΥΤΕΣ ΤΙΣ 2 ΓΡΑΜΜΕΣ ====
app.secret_key = 'HEF_admin'   # ← άλλαξε το σε κάτι δικό σου (ό,τι θέλεις)
ADMIN_PASSWORD = 'stable_evi'                        # ← αυτό είναι το password σου για admin
# ==========================================

# Όλα τα stalls (δεν χρειάζεται να αλλάξεις τίποτα εδώ)
STALLS = [
    "5Β1","5Β2","5Β3","5Β4","5Β5","5Β6","5Β7","5Β8","5Β9","5Β10","5Β11","5Β12","5Β13","5Β14","5Β15",
    "5Α1","5Α2","5Α3","5Α4","5Α5","5Α6","5Α7","5Α8","5Α9","5Α10","5Α11","5Α12","5Α13","5Α14","5Α15",
    "5C1","5C2","5C3","5C4","5C5","5C6","5C7","5C8","5C9","5C10","5C11","5C12","5C13","5C14","5C15",
    "5D1","5D2","5D3","5D4","5D5","5D6","5D7","5D8","5D9","5D10","5D11","5D12","5D13","5D14","5D15",
    "4B1","4B2","4B3","4B4","4B5","4B6","4B7","4B8","4B9","4B10","4B11","4B12","4B13","4B14","4B15",
    "3B1","3B2","3B3","3B4","3B5","3B6","3B7","3B8","3B9","3B10","3B11","3B12","3B13","3B14","3B15",
    "2B1","2B2","2B3","2B4","2B5","2B6","2B7","2B8","2B9","2B10","2B11","2B12","2B13","2B14","2B15",
    "4A1","4A2","4A3","4A4","4A5","4A6","4A7","4A8","4A9","4A10","4A11","4A12","4A13","4A14","4A15",
    "4C1","4C2","4C3","4C4","4C5","4C6","4C7","4C8","4C9","4C10","4C11","4C12","4C13","4C14","4C15",
    "3A1","3A2","3A3","3A4","3A5","3A6","3A7","3A8","3A9","3A10","3A11","3A12","3A13","3A14","3A15",
    "3C1","3C2","3C3","3C4","3C5","3C6","3C7","3C8","3C9","3C10","3C11","3C12","3C13","3C14","3C15",
    "2A1","2A2","2A3","2A4","2A5","2A6","2A7","2A8","2A9","2A10","2A11","2A12","2A13","2A14","2A15",
    "2C1","2C2","2C3","2C4","2C5","2C6","2C7","2C8","2C9","2C10","2C11","2C12","2C13","2C14","2C15",
    "4D1","4D2","4D3","4D4","4D5","4D6","4D7","4D8","4D9","4D10","4D11","4D12","4D13","4D14","4D15",
    "3D1","3D2","3D3","3D4","3D5","3D6","3D7","3D8","3D9","3D10","3D11","3D12","3D13","3D14","3D15",
    "2D1","2D2","2D3","2D4","2D5","2D6","2D7","2D8","2D9","2D10","2D11","2D12","2D13","2D14","2D15",
    "1A1","1A2","1A3","1A4","1A5","1A6","1A7","1A8","1A9","1A10","1A11","1A12","1A13","1A14","1A15",
    "1B1","1B2","1B3","1B4","1B5","1B6","1B7","1B8","1B9","1B10","1B11","1B12","1B13","1B14","1B15"
]

# Θέση κάθε σταβλου στο grid (μην το πειράξεις)
STALL_POSITIONS = { ... }   # (ο κώδικας είναι ίδιος με πριν – πολύ μεγάλος για εδώ, απλά κράτα όλο το αρχείο όπως στο προηγούμενο μήνυμα)

# Από εδώ και κάτω δεν αλλάζεις ΤΙΠΟΤΑ
def get_db():
    conn = sqlite3.connect('stables.db')
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS events 
                    (id INTEGER PRIMARY KEY, name TEXT UNIQUE, created_at TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations 
                    (event_id INTEGER, stall_id TEXT, user_name TEXT, 
                     UNIQUE(event_id, stall_id))''')

@app.route('/')
def index():
    with get_db() as conn:
        events = conn.execute('SELECT * FROM events ORDER BY created_at DESC').fetchall()
    return render_template('index.html', events=events)

@app.route('/event/<event_name>')
def event(event_name):
    with get_db() as conn:
        event = conn.execute('SELECT id FROM events WHERE name = ?', (event_name,)).fetchone()
        if not event: return "Δεν βρέθηκε ο αγώνας", 404
        event_id = event[0]
        reservations = dict(conn.execute('SELECT stall_id, user_name FROM reservations WHERE event_id = ?', (event_id,)).fetchall())

    # Δημιουργία grid 56×61
    grid = [['' for _ in range(61)] for _ in range(56)]
    for stall, (r, c) in STALL_POSITIONS.items():
        r_idx, c_idx = r-1, c-1
        if stall in reservations:
            grid[r_idx][c_idx] = f"{reservations[stall]} (Κλεισμένο)"
        else:
            grid[r_idx][c_idx] = stall

    return render_template('event.html', event_name=event_name, grid=grid)

@app.route('/reserve/<event_name>', methods=['POST'])
def reserve(event_name):
    stall_id = request.form['stall_id']
    user_name = request.form['user_name'].strip()
    if not user_name: return "Πρέπει να βάλεις όνομα!", 400

    with get_db() as conn:
        event = conn.execute('SELECT id FROM events WHERE name = ?', (event_name,)).fetchone()
        if not event: return "Δεν βρέθηκε ο αγώνας", 404
        event_id = event[0]

        try:
            conn.execute('INSERT INTO reservations (event_id, stall_id, user_name) VALUES (?, ?, ?)',
                        (event_id, stall_id, user_name))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Αυτός ο στάβλος είναι ήδη κλεισμένος!", 400

    return redirect(url_for('event', event_name=event_name))

@app.route('/admin/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        if request.form['password'] != ADMIN_PASSWORD:
            return "Λάθος password!", 403
        name = request.form['event_name'].strip()
        with get_db() as conn:
            try:
                conn.execute('INSERT INTO events (name, created_at) VALUES (?, ?)',
                            (name, datetime.now().strftime('%Y-%m-%d %H:%M')))
                conn.commit()
            except sqlite3.IntegrityError:
                return "Υπάρχει ήδη αγώνας με αυτό το όνομα!", 400
        return redirect('/')
    return render_template('admin_create.html')

@app.route('/admin/download/<event_name>', methods=['POST'])
def download(event_name):
    if request.form['password'] != ADMIN_PASSWORD:
        return "Λάθος password!", 403

    with get_db() as conn:
        event = conn.execute('SELECT id FROM events WHERE name = ?', (event_name,)).fetchone()
        if not event: return "Δεν βρέθηκε ο αγώνας", 404
        rows = conn.execute('SELECT stall_id, user_name FROM reservations WHERE event_id = ? ORDER BY stall_id', (event[0],)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Στάβλος', 'Όνομα'])
    for r in rows:
        writer.writerow(r)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'{event_name}_κρατήσεις.csv')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
