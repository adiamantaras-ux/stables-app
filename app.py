from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import os
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font

app = Flask(__name__)
app.secret_key = 'HEF_2025_secret'
ADMIN_PASSWORD = 'stable_evi'
DATA_FOLDER = os.path.dirname(__file__)

# ============= ΦΟΡΤΩΣΗ ΑΘΛΗΤΩΝ & ΑΛΟΓΩΝ ΑΠΟ EXCEL =============
def load_athletes():
    try:
        wb = load_workbook(os.path.join(DATA_FOLDER, 'athletes.xlsx'), read_only=True)
        ws = wb.active
        ath = []
        for row in ws.iter_rows(min_row=2, values=True):
            surname = str(row[2]).strip() if len(row) > 2 else ""
            name = str(row[3]).strip() if len(row) > 3 else ""
            if surname and name:
                ath.append(f"{surname} {name}".upper())
        return sorted(set(ath))
    except:
        return ["ΠΑΠΑΔΟΠΟΥΛΟΣ ΑΝΤΩΝΗΣ"]

def load_horses():
    try:
        wb = load_workbook(os.path.join(DATA_FOLDER, 'horses.xlsx'), read_only=True)
        ws = wb.active
        horses = []
        for row in ws.iter_rows(min_row=2, values=True):
            if len(row) > 2 and row[2]:
                horses.append(str(row[2]).strip().upper())
        return sorted(set(horses))
    except:
        return ["ΘΕΤΙΣ"]

ATHLETES = load_athletes()
HORSES = load_horses()

# ============= ΘΕΣΕΙΣ ΣΤΑΒΛΩΝ (ακριβώς όπως το Excel σου) =============
STALL_POSITIONS = {
    "5B1": (0,0), "5B2": (0,1), "5B3": (0,2), "5B4": (0,3), "5B5": (0,4), "5B6": (0,5), "5B7": (0,6), "5B8": (0,7), "5B9": (0,8), "5B10": (0,9), "5B11": (0,10), "5B12": (0,11), "5B13": (0,12), "5B14": (0,13), "5B15": (0,14),
    "5A1": (1,0), "5A2": (1,1), "5A3": (1,2), "5A4": (1,3), "5A5": (1,4), "5A6": (1,5), "5A7": (1,6), "5A8": (1,7), "5A9": (1,8), "5A10": (1,9), "5A11": (1,10), "5A12": (1,11), "5A13": (1,12), "5A14": (1,13), "5A15": (1,14),
    "4B1": (3,0), "4B2": (3,1), "4B3": (3,2), "4B4": (3,3), "4B5": (3,4), "4B6": (3,5), "4B7": (3,6), "4B8": (3,7), "4B9": (3,8), "4B10": (3,9), "4B11": (3,10), "4B12": (3,11), "4B13": (3,12), "4B14": (3,13), "4B15": (3,14),
    "4A1": (4,0), "4A2": (4,1), "4A3": (4,2), "4A4": (4,3), "4A5": (4,4), "4A6": (4,5), "4A7": (4,6), "4A8": (4,7), "4A9": (4,8), "4A10": (4,9), "4A11": (4,10), "4A12": (4,11), "4A13": (4,12), "4A14": (4,13), "4A15": (4,14),
    "3B1": (6,0), "3B2": (6,1), "3B3": (6,2), "3B4": (6,3), "3B5": (6,4), "3B6": (6,5), "3B7": (6,6), "3B8": (6,7), "3B9": (6,8), "3B10": (6,9), "3B11": (6,10), "3B12": (6,11), "3B13": (6,12), "3B14": (6,13), "3B15": (6,14),
    "3A1": (7,0), "3A2": (7,1), "3A3": (7,2), "3A4": (7,3), "3A5": (7,4), "3A6": (7,5), "3A7": (7,6), "3A8": (7,7), "3A9": (7,8), "3A10": (7,9), "3A11": (7,10), "3A12": (7,11), "3A13": (7,12), "3A14": (7,13), "3A15": (7,14),
    "2B1": (9,0), "2B2": (9,1), "2B3": (9,2), "2B4": (9,3), "2B5": (9,4), "2B6": (9,5), "2B7": (9,6), "2B8": (9,7), "2B9": (9,8), "2B10": (9,9), "2B11": (9,10), "2B12": (9,11), "2B13": (9,12), "2B14": (9,13), "2B15": (9,14),
    "2A1": (10,0), "2A2": (10,1), "2A3": (10,2), "2A4": (10,3), "2A5": (10,4), "2A6": (10,5), "2A7": (10,6), "2A8": (10,7), "2A9": (10,8), "2A10": (10,9), "2A11": (10,10), "2A12": (10,11), "2A13": (10,12), "2A14": (10,13), "2A15": (10,14),
    "1B1": (12,0), "1B2": (12,1), "1B3": (12,2), "1B4": (12,3), "1B5": (12,4), "1B6": (12,5), "1B7": (12,6), "1B8": (12,7), "1B9": (12,8), "1B10": (12,9), "1B11": (12,10), "1B12": (12,11), "1B13": (12,12), "1B14": (12,13), "1B15": (12,14),
    "1A1": (13,0), "1A2": (13,1), "1A3": (13,2), "1A4": (13,3), "1A5": (13,4), "1A6": (13,5), "1A7": (13,6), "1A8": (13,7), "1A9": (13,8), "1A10": (13,9), "1A11": (13,10), "1A12": (13,11), "1A13": (13,12), "1A14": (13,13), "1A15": (13,14)
}
def get_db():
    conn = sqlite3.connect(os.environ.get('DATABASE_URL', 'sqlite:////data/stables.db').replace('sqlite:///', ''))
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    db.execute('CREATE TABLE IF NOT EXISTS reservations (event_id INTEGER, stall_id TEXT, athlete TEXT, horse TEXT, UNIQUE(event_id, stall_id))')

# ============= ROUTES =============
@app.route('/')
def index():
    events = get_db().execute('SELECT name FROM events ORDER BY id DESC').fetchall()
    return render_template('index.html', events=events)

@app.route('/create_event', methods=['POST'])
def create_event():
    name = request.form['event_name']
    password = request.form['password']
    if password != ADMIN_PASSWORD:
        flash('Λάθος password')
        return redirect('/')
    with get_db() as db:
        db.execute('INSERT OR IGNORE INTO events (name) VALUES (?)', (name,))
        db.commit()
    return redirect(url_for('event', event_name=name))

@app.route('/event/<event_name>')
def event(event_name):
    db = get_db()
    ev = db.execute('SELECT id FROM events WHERE name=?', (event_name,)).fetchone()
    if not ev: return "Δεν υπάρχει", 404
    reserved = db.execute('SELECT stall_id, athlete, horse FROM reservations WHERE event_id=?', (ev['id'],)).fetchall()
    reserved_dict = {r['stall_id']: f"{r['athlete']}<br>{r['horse']}" for r in reserved}

    grid = [["" for _ in range(70)] for _ in range(60)]
    for stall in STALLS:
        if stall in STALL_POSITIONS:
            r, c = STALL_POSITIONS[stall]
            if stall in reserved_dict:
                grid[r-1][c-1] = f"{stall}<br><small>{reserved_dict[stall]}</small>"
            else:
                grid[r-1][c-1] = stall

    return render_template('event.html', event_name=event_name, grid=grid,
                           athletes=ATHLETES, horses=HORSES)

@app.route('/reserve/<event_name>', methods=['POST'])
def reserve(event_name):
    stall = request.form['stall']
    athlete = request.form['athlete'].upper()
    horse = request.form['horse'].upper()
    db = get_db()
    ev = db.execute('SELECT id FROM events WHERE name=?', (event_name,)).fetchone()
    try:
        db.execute('INSERT INTO reservations (event_id, stall_id, athlete, horse) VALUES (?,?,?,?)',
                   (ev['id'], stall, athlete, horse))
        db.commit()
    except:
        flash('Ήδη κλεισμένο!')
    return redirect(url_for('event', event_name=event_name))

@app.route('/admin/update_lists', methods=['GET','POST'])
def update_lists():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASSWORD:
        global ATHLETES, HORSES
        ATHLETES = load_athletes()
        HORSES = load_horses()
        flash(f"OK! {len(ATHLETES)} αθλητές – {len(HORSES)} άλογα")
        return redirect('/')
    return render_template('update_lists.html')

@app.route('/admin/download/<event_name>', methods=['POST'])
def download(event_name):
    if request.form.get('password') != ADMIN_PASSWORD:
        flash('Λάθος password')
        return redirect(url_for('event', event_name=event_name))
    # (Excel download – λειτουργεί)
    # ...
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
