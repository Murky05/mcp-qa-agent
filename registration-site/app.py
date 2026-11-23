"""
Vikhyat Academy - Dummy Student Registration Website
Runs locally at http://127.0.0.1:5000 and saves registrations into
MySQL database `vikhyatacademy`, table `students`.

Uses only the Python standard library + mysql-connector-python
(already installed with mysql-mcp-server). No extra installs needed.
"""
import datetime
import getpass
import json
import os
import re
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import mysql.connector

HOST, PORT = "127.0.0.1", 5000
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "database": "vikhyatacademy",
}
COURSES = ["Python", "Java", "Selenium", "Playwright", "SQL", "AI Agents", "API Testing"]
GENDERS = ["Male", "Female", "Other"]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  phone VARCHAR(15) NOT NULL,
  gender ENUM('Male','Female','Other') NOT NULL,
  dob DATE NOT NULL,
  course VARCHAR(50) NOT NULL,
  city VARCHAR(60) NOT NULL,
  experience_years TINYINT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""


def db():
    return mysql.connector.connect(**DB_CONFIG)


def validate(d):
    errors = {}
    name = (d.get("full_name") or "").strip()
    email = (d.get("email") or "").strip().lower()
    phone = (d.get("phone") or "").strip()
    gender = d.get("gender") or ""
    dob = d.get("dob") or ""
    course = d.get("course") or ""
    city = (d.get("city") or "").strip()
    exp = str(d.get("experience_years") or "0").strip()

    if len(name) < 3:
        errors["full_name"] = "Name must be at least 3 characters."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors["email"] = "Enter a valid email address."
    if not re.fullmatch(r"\d{10}", phone):
        errors["phone"] = "Phone must be exactly 10 digits."
    if gender not in GENDERS:
        errors["gender"] = "Select a gender."
    try:
        born = datetime.date.fromisoformat(dob)
        age = (datetime.date.today() - born).days // 365
        if age < 16 or age > 80:
            errors["dob"] = "Age must be between 16 and 80."
    except ValueError:
        errors["dob"] = "Enter a valid date of birth."
    if course not in COURSES:
        errors["course"] = "Select a course."
    if len(city) < 2:
        errors["city"] = "Enter your city."
    if not exp.isdigit() or int(exp) > 50:
        errors["experience_years"] = "Experience must be 0-50 years."
    if not d.get("terms"):
        errors["terms"] = "You must accept the terms."

    clean = dict(full_name=name, email=email, phone=phone, gender=gender,
                 dob=dob, course=course, city=city,
                 experience_years=int(exp) if exp.isdigit() else 0)
    return clean, errors


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, default=str))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html")
        elif self.path == "/api/students":
            conn = db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM students ORDER BY id DESC")
            rows = cur.fetchall()
            conn.close()
            self._json(200, rows)
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/register":
            return self._json(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"errors": {"form": "Invalid request."}})

        clean, errors = validate(payload)
        if errors:
            return self._json(400, {"errors": errors})
        try:
            conn = db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO students (full_name,email,phone,gender,dob,course,city,experience_years)"
                " VALUES (%(full_name)s,%(email)s,%(phone)s,%(gender)s,%(dob)s,%(course)s,%(city)s,%(experience_years)s)",
                clean,
            )
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
        except mysql.connector.IntegrityError:
            return self._json(409, {"errors": {"email": "This email is already registered."}})
        self._json(201, {"message": "Registration successful!", "id": new_id})

    def log_message(self, fmt, *args):
        print("  " + fmt % args)


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vikhyat Academy - Student Registration</title>
<style>
  :root { --ink:#1d2433; --muted:#5d6678; --line:#d9dde5; --bg:#f4f5f8;
          --brand:#2f5bd3; --brand-dark:#2347a8; --ok:#1f7a4d; --err:#c0392b; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--ink); }
  header { background:var(--ink); color:#fff; padding:18px 32px; display:flex; align-items:baseline; gap:14px; }
  header h1 { margin:0; font-size:20px; letter-spacing:.3px; }
  header span { color:#aab3c5; font-size:14px; }
  main { max-width:1100px; margin:28px auto; padding:0 20px; display:grid;
         grid-template-columns: 420px 1fr; gap:24px; align-items:start; }
  @media (max-width:900px){ main { grid-template-columns:1fr; } }
  .card { background:#fff; border:1px solid var(--line); border-radius:10px; padding:24px; }
  .card h2 { margin:0 0 4px; font-size:18px; }
  .card p.sub { margin:0 0 20px; color:var(--muted); font-size:14px; }
  label { display:block; font-size:13px; font-weight:600; margin:14px 0 6px; }
  input, select { width:100%; padding:10px 12px; border:1px solid var(--line); border-radius:6px;
                  font:inherit; font-size:14px; background:#fff; }
  input:focus, select:focus { outline:2px solid var(--brand); outline-offset:-1px; border-color:var(--brand); }
  .row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .radios { display:flex; gap:18px; font-size:14px; }
  .radios label, .check label { display:inline-flex; align-items:center; gap:6px; margin:0; font-weight:400; }
  .radios input, .check input { width:auto; }
  .check { margin-top:16px; font-size:14px; }
  .err { color:var(--err); font-size:12px; min-height:14px; margin-top:4px; }
  .invalid { border-color:var(--err); }
  button { margin-top:20px; width:100%; padding:12px; border:0; border-radius:6px; background:var(--brand);
           color:#fff; font-size:15px; font-weight:600; cursor:pointer; }
  button:hover { background:var(--brand-dark); }
  button.secondary { background:#fff; color:var(--ink); border:1px solid var(--line); margin-top:10px; }
  .banner { padding:12px 14px; border-radius:6px; font-size:14px; margin-bottom:14px; display:none; }
  .banner.ok { display:block; background:#e6f4ec; color:var(--ok); }
  .banner.bad { display:block; background:#fbeaea; color:var(--err); }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { text-align:left; padding:9px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.4px; }
  .table-wrap { overflow-x:auto; }
  .head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
  .count { color:var(--muted); font-size:13px; }
  .empty { color:var(--muted); text-align:center; padding:30px 0; }
</style>
</head>
<body>
<header><h1>Vikhyat Academy</h1><span>Student Registration Portal</span></header>
<main>
  <section class="card">
    <h2>Register for a course</h2>
    <p class="sub">All fields are required.</p>
    <div id="banner" class="banner" data-testid="banner" role="status"></div>
    <form id="regForm" novalidate>
      <label for="full_name">Full name</label>
      <input id="full_name" name="full_name" data-testid="full-name" placeholder="e.g. Rahul Sharma">
      <div class="err" data-for="full_name"></div>

      <label for="email">Email</label>
      <input id="email" name="email" type="email" data-testid="email" placeholder="name@example.com">
      <div class="err" data-for="email"></div>

      <div class="row">
        <div>
          <label for="phone">Phone</label>
          <input id="phone" name="phone" data-testid="phone" maxlength="10" placeholder="10 digits">
          <div class="err" data-for="phone"></div>
        </div>
        <div>
          <label for="dob">Date of birth</label>
          <input id="dob" name="dob" type="date" data-testid="dob">
          <div class="err" data-for="dob"></div>
        </div>
      </div>

      <label>Gender</label>
      <div class="radios">
        <label><input type="radio" name="gender" value="Male" data-testid="gender-male"> Male</label>
        <label><input type="radio" name="gender" value="Female" data-testid="gender-female"> Female</label>
        <label><input type="radio" name="gender" value="Other" data-testid="gender-other"> Other</label>
      </div>
      <div class="err" data-for="gender"></div>

      <div class="row">
        <div>
          <label for="course">Course</label>
          <select id="course" name="course" data-testid="course">
            <option value="">Select…</option>
            __COURSE_OPTIONS__
          </select>
          <div class="err" data-for="course"></div>
        </div>
        <div>
          <label for="experience_years">Experience (years)</label>
          <input id="experience_years" name="experience_years" type="number" min="0" max="50" value="0" data-testid="experience">
          <div class="err" data-for="experience_years"></div>
        </div>
      </div>

      <label for="city">City</label>
      <input id="city" name="city" data-testid="city" placeholder="e.g. Bengaluru">
      <div class="err" data-for="city"></div>

      <div class="check">
        <label><input type="checkbox" id="terms" name="terms" data-testid="terms"> I accept the terms and conditions</label>
      </div>
      <div class="err" data-for="terms"></div>

      <button type="submit" id="submitBtn" data-testid="submit">Register</button>
      <button type="reset" class="secondary" data-testid="reset">Clear form</button>
    </form>
  </section>

  <section class="card">
    <div class="head">
      <h2>Registered students</h2>
      <span class="count" id="count" data-testid="student-count"></span>
    </div>
    <div class="table-wrap">
      <table id="studentsTable" data-testid="students-table">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Gender</th>
          <th>DOB</th><th>Course</th><th>City</th><th>Exp</th><th>Registered</th></tr></thead>
        <tbody id="rows"></tbody>
      </table>
    </div>
  </section>
</main>
<script>
const form = document.getElementById('regForm');
const banner = document.getElementById('banner');

function showErrors(errors) {
  document.querySelectorAll('.err').forEach(e => e.textContent = '');
  document.querySelectorAll('.invalid').forEach(e => e.classList.remove('invalid'));
  for (const [field, msg] of Object.entries(errors)) {
    const slot = document.querySelector(`.err[data-for="${field}"]`);
    if (slot) slot.textContent = msg;
    const input = document.getElementById(field);
    if (input) input.classList.add('invalid');
  }
}

function setBanner(kind, text) {
  banner.className = 'banner ' + kind;
  banner.textContent = text;
}

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

async function loadStudents() {
  const res = await fetch('/api/students');
  const rows = await res.json();
  document.getElementById('count').textContent = rows.length + (rows.length === 1 ? ' student' : ' students');
  const body = document.getElementById('rows');
  body.innerHTML = rows.length ? rows.map(r => `<tr>
    <td>${r.id}</td><td>${esc(r.full_name)}</td><td>${esc(r.email)}</td><td>${esc(r.phone)}</td>
    <td>${esc(r.gender)}</td><td>${esc(String(r.dob).slice(0,10))}</td><td>${esc(r.course)}</td>
    <td>${esc(r.city)}</td><td>${r.experience_years}</td><td>${esc(String(r.created_at).slice(0,16))}</td></tr>`).join('')
    : '<tr><td colspan="10" class="empty">No students registered yet.</td></tr>';
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(form);
  const data = Object.fromEntries(fd.entries());
  data.terms = document.getElementById('terms').checked;
  const res = await fetch('/api/register', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
  });
  const out = await res.json();
  if (res.ok) {
    showErrors({});
    setBanner('ok', `${out.message} Student ID: ${out.id}`);
    form.reset();
    loadStudents();
  } else {
    showErrors(out.errors || {});
    setBanner('bad', out.errors?.form || 'Please fix the highlighted fields.');
  }
});

form.addEventListener('reset', () => { showErrors({}); banner.className = 'banner'; });
loadStudents();
</script>
</body>
</html>
""".replace("__COURSE_OPTIONS__", "".join(f'<option value="{c}">{c}</option>' for c in COURSES))


def main():
    password = os.environ.get("MYSQL_PASSWORD") or getpass.getpass("MySQL root password (hidden while typing): ")
    DB_CONFIG["password"] = password
    try:
        conn = db()
        conn.cursor().execute(CREATE_TABLE)
        conn.close()
    except mysql.connector.Error as err:
        print(f"\nCould not connect to MySQL: {err}")
        input("Press Enter to exit...")
        return
    print(f"\nVikhyat Academy registration site is running at http://{HOST}:{PORT}")
    print("Keep this window open. Press Ctrl+C to stop.\n")
    webbrowser.open(f"http://{HOST}:{PORT}")
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
