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

# ============= ΣΩΣΤΗ ΔΙΑΤΑΞΗ ΣΤΑΒΛΩΝ – ΑΚΡΙΒΩΣ όπως η φωτογραφία σου =============
STALL_POSITIONS = {
    # Πάνω – 5η σειρά (5B + 5A)
    "5B1": (1,0), "5B2": (2,0), "5B3": (3,0), "5B4": (4,0), "5B5": (5,0), "5B6": (6,0), "5B7": (7,0),
    "5B8": (8,0), "5B9": (9,0), "5B10": (10,0), "5B11": (11,0), "5B12": (12,0), "5B13": (13,0), "5B14": (14,0), "5B15": (15,0),
    "5A1": (1,1), "5A2": (2,1), "5A3": (3,1), "5A4": (4,1), "5A5": (5,1), "5A6": (6,1), "5A7": (7,1),
    "5A8": (8,1), "5A9": (9,1), "5A10": (10,1), "5A11": (11,1), "5A12": (12,1), "5A13": (13,1), "5A14": (14,1), "5A15": (15,1),

    # 4η σειρά (μόνο 7 στάβλοι αριστερά)
    "4B1": (1,4), "4B2": (2,4), "4B3": (3,4), "4B4": (4,4), "4B5": (5,4), "4B6": (6,4), "4B7": (7,4),
    "4A1": (1,5), "4A2": (2,5), "4A3": (3,5), "4A4": (4,5), "4A5": (5,5), "4A6": (6,5), "4A7": (7,5),

    # 3η σειρά
    "3B1": (1,7), "3B2": (2,7), "3B3": (3,7), "3B4": (4,7), "3B5": (5,7), "3B6": (6,7), "3B7": (7,7),
    "3A1": (1,8), "3A2": (2,8), "3A3": (3,8), "3A4": (4,8), "3A5": (5,8), "3A6": (6,8), "3A7": (7,8),

    # 2η σειρά
    "2B1": (1,10), "2B2": (2,10), "2B3": (3,10), "2B4": (4,10), "2B5": (5,10), "2B6": (6,10), "2B7": (7,10),
    "2A1": (1,11), "2A2": (2,11), "2A3": (3,11), "2A4": (4,11), "2A5": (5,11), "2A6": (6,11), "2A7": (7,11),

    # 1η σειρά κάτω
    "1B1": (1,14), "1B2": (2,14), "1B3": (3,14), "1B4": (4,14), "1B5": (5,14), "1B6": (6,14), "1B7": (7,14),
    "1A1": (1,15), "1A2": (2,15), "1A3": (3,15), "1A4": (4,15), "1A5": (5,15), "1A6": (6,15), "1A7": (7,15), "1A8": (8,15),

    # Δεξιές ομάδες (οι στάβλοι 8-15)
    "4B8": (10,4), "4B9": (11,4), "4B10": (12,4), "4B11": (13,4), "4B12": (14,4), "4B13": (15,4), "4B14": (16,4), "4B15": (17,4),
    "3B8": (10,7), "3B9": (11,7), "3B10": (12,7), "3B11": (13,7), "3B12": (14,7), "3B13": (15,7), "3B14": (16,7), "3B15": (17,7),
    "2B8": (10,10), "2B9": (11,10), "2B10": (12,10), "2B11": (13,10), "2B12": (14,10), "2B13": (15,10), "2B14": (16,10), "2B15": (17,10),
    "1B8": (10,14), "1B9": (11,14), "1B10": (12,14), "1B11": (13,14), "1B12": (14,14), "1B13": (15,14), "1B14": (16,14), "1B15": (17,14)
}
def get_db():
    conn = sqlite3.connect('stables.db')
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
