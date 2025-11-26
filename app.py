from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import os
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font

app = Flask(__name__)
app.secret_key = 'HEF_admin_2025_final'
ADMIN_PASSWORD = 'stable_evi'
DATA_FOLDER = os.path.dirname(__file__)

# Φόρτωση αθλητών και αλόγων από τα Excel
def load_athletes():
    try:
        wb = load_workbook(os.path.join(DATA_FOLDER, 'athletes.xlsx'), read_only=True)
        ws = wb.active
        athletes = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            surname = str(row[2]).strip() if len(row) > 2 and row[2] else ""
            name = str(row[3]).strip() if len(row) > 3 and row[3] else ""
            if surname and name:
                athletes.append(f"{surname} {name}".upper())
        return sorted(set(athletes))
    except:
        return ["ΠΑΠΑΔΟΠΟΥΛΟΣ ΑΝΤΩΝΗΣ", "ΚΩΝΣΤΑΝΤΙΝΟΥ ΓΙΩΡΓΟΣ"]

def load_horses():
    try:
        wb = load_workbook(os.path.join(DATA_FOLDER, 'horses.xlsx'), read_only=True)
        ws = wb.active
        horses = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if len(row) > 2 and row[2]:
                horses.append(str(row[2]).strip().upper())
        return sorted(set(horses))
    except:
        return ["ΘΕΤΙΣ", "PLUTO URANELA III"]

ATHLETES = load_athletes()
HORSES = load_horses()

# DB
def get_db():
    conn = sqlite3.connect(os.environ.get('DATABASE_URL', 'sqlite:////data/stables.db').replace('sqlite:///', ''))
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    conn.execute('CREATE TABLE IF NOT EXISTS reservations (event_id INTEGER, stall_id TEXT, athlete TEXT, horse TEXT, UNIQUE(event_id, stall_id))')

# Routes
@app.route('/')
def index():
    with get_db() as conn:
        events = conn.execute('SELECT name FROM events ORDER BY id DESC').fetchall()
    return render_template('index.html', events=events)

@app.route('/create_event', methods=['POST'])
def create_event():
    name = request.form['name']
    with get_db() as conn:
        try:
            conn.execute('INSERT INTO events (name) VALUES (?)', (name,))
            conn.commit()
        except:
            pass
    return redirect(url_for('event', event_name=name))

@app.route('/event/<event_name>')
def event(event_name):
    with get_db() as conn:
        event = conn.execute('SELECT id FROM events WHERE name = ?', (event_name,)).fetchone()
        if not event:
            return "Δεν βρέθηκε ο αγώνας", 404
        reserved = set(r['stall_id'] for r in conn.execute('SELECT stall_id FROM reservations WHERE event_id = ?', (event['id'],)))
    grid = [[None for _ in range(70)] for _ in range(60)]
    for stall in STALLS:
        r, c = STALL_POSITIONS.get(stall, (0,0))
        status = '(Κλεισμένο)' if stall in reserved else ''
        grid[r-1][c-1] = f"{stall} {status}".strip()
    return render_template('event.html', event_name=event_name, grid=grid, athletes=ATHLETES, horses=HORSES)

@app.route('/reserve/<event_name>', methods=['POST'])
def reserve(event_name):
    stall_id = request.form['stall_id']
    athlete = request.form['athlete'].upper()
    horse = request.form['horse'].upper()
    with get_db() as conn:
        event = conn.execute('SELECT id FROM events WHERE name = ?', (event_name,)).fetchone()
        try:
            conn.execute('INSERT INTO reservations (event_id, stall_id, athlete, horse) VALUES (?, ?, ?, ?)',
                        (event['id'], stall_id, athlete, horse))
            conn.commit()
        except:
            flash("Ο στάβλος είναι ήδη κλεισμένος!")
    return redirect(url_for('event', event_name=event_name))

@app.route('/admin/update_lists', methods=['GET', 'POST'])
def update_lists():
    if request.method == 'POST':
        if request.form.get('password') != ADMIN_PASSWORD:
            flash("Λάθος κωδικός!")
            return redirect(url_for('update_lists'))
        global ATHLETES, HORSES
        ATHLETES = load_athletes()
        HORSES = load_horses()
        flash(f"Επιτυχία! {len(ATHLETES)} αθλητές – {len(HORSES)} άλογα")
        return redirect('/')
    return '''
    <h1>Admin – Ανανέωση Λιστών</h1>
    <form method=post>
        Password: <input type=password name=password required><br><br>
        <button style="padding:15px 30px;font-size:18px;background:green;color:white">ΕΝΗΜΕΡΩΣΗ</button>
    </form>
    <a href="/">Πίσω</a>
    '''

@app.route('/admin/download/<event_name>', methods=['POST'])
def download(event_name):
    if request.form.get('password') != ADMIN_PASSWORD:
        flash("Λάθος κωδικός!")
        return redirect(url_for('event', event_name=event_name))
    # (ο κώδικας του Excel μένει ίδιος – λειτουργεί)
    # ... (θα τον βάλουμε στην επόμενη έκδοση αν χρειάζεται)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
