from __future__ import annotations
import re, sqlite3, os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash


app = Flask(__name__)
app.config.update(
SECRET_KEY="dev", # 개발용. 배포 시 환경변수로 교체
DATABASE=str(Path("instance") / "guesthouse.db"),
)


# --- 최소 DB 유틸 ---
def get_db():
    conn = sqlite3.connect(app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    Path("instance").mkdir(exist_ok=True)
    with get_db() as db:
        db.execute(
        """
        CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        checkin DATE NOT NULL,
        checkout DATE NOT NULL,
        guests INTEGER NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )


# @app.before_first_request
# def _bootstrap():
#     init_db()


# --- 라우트 ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attractions")
def attractions():
    # 실제 서비스에서는 DB/외부 API로 대체 가능
    places = [
    {
    "title": "해변 산책로",
    "desc": "숙소에서 도보 7분. 일몰 명소.",
    "tag": "nature",
    },
    {"title": "전통 시장", "desc": "로컬 간식 천국. 오전 9시~오후 6시.", "tag": "food"},
    {"title": "전시 갤러리", "desc": "매주 수·토 무료 입장.", "tag": "art"},
    ]
    return render_template("attractions.html", places=places)


_phone_rx = re.compile(r"^0\d{1,2}-?\d{3,4}-?\d{4}$") # 한국형 기본 패턴


@app.route("/reserve", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        form = {k: (request.form.get(k, "").strip()) for k in [
            "name", "phone", "checkin", "checkout", "guests", "note"
        ]}
        # 서버측 검증 (필수)
        errors = []
        if not form["name"]:
            errors.append("이름을 입력해 주세요.")
        if not _phone_rx.match(form["phone"]):
            errors.append("전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678).")
        if not form["checkin"] or not form["checkout"]:
            errors.append("체크인/체크아웃 날짜를 선택해 주세요.")
        try:
            guests = int(form["guests"] or 1)
            if guests < 1 or guests > 10:
                errors.append("투숙 인원은 1~10 사이여야 합니다.")
        except ValueError:
            errors.append("투숙 인원을 숫자로 입력해 주세요.")

        if errors:
            for e in errors: flash(e, "error")
            return render_template("reserve.html", form=form), 400

        with get_db() as db:
            cur = db.execute(
                """
                INSERT INTO reservations(name, phone, checkin, checkout, guests, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (form["name"], form["phone"], form["checkin"], form["checkout"], guests, form["note"]),
            )
            res_id = cur.lastrowid
        return redirect(url_for("success", rid=res_id))

    # GET
    return render_template("reserve.html", form={})

@app.route("/success/<int:rid>")
def success(rid: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM reservations WHERE id = ?", (rid,)).fetchone()
    if not row:
        flash("예약 정보를 찾을 수 없습니다.", "error")
        return redirect(url_for("reserve"))
    return render_template("success.html", r=row)

if __name__ == "__main__":
    app.run(debug=True)