from functools import wraps
import sqlite3
import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from database import init_db, get_connection


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = "change-this-secret-key-before-production"


# =========================================================
# IMAGE UPLOAD CONFIGURATION
# =========================================================

IMAGE_FOLDER = os.path.join(
    app.static_folder,
    "images"
)

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}

os.makedirs(
    IMAGE_FOLDER,
    exist_ok=True
)


def allowed_image(filename):
    """
    Check whether the uploaded file is an allowed image.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def save_image():
    """
    Save the uploaded image into static/images
    and return the saved filename.

    If no image was uploaded, return an empty string.
    """

    file = request.files.get("image")

    if not file:
        return ""

    if not file.filename:
        return ""

    if not allowed_image(file.filename):
        flash(
            "Please upload a JPG, JPEG, or PNG image only.",
            "error"
        )
        return None

    filename = secure_filename(
        file.filename
    )

    file_path = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    file.save(file_path)

    return filename


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(f):

    @wraps(f)
    def w(*a, **k):

        if "user_id" not in session:

            flash(
                "Please log in to continue.",
                "info"
            )

            return redirect(
                url_for(
                    "login",
                    next=request.path
                )
            )

        return f(*a, **k)

    return w


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(f):

    @wraps(f)
    def w(*a, **k):

        if session.get("role") != "admin":

            flash(
                "Administrator access is required.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return f(*a, **k)

    return w


# =========================================================
# GLOBAL TEMPLATE VARIABLES
# =========================================================

@app.context_processor
def globals():

    return {
        "current_user": session.get("username"),
        "current_role": session.get("role")
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    c = get_connection()

    featured = c.execute(
        """
        SELECT *
        FROM attractions
        WHERE featured = 1
        ORDER BY id
        LIMIT 6
        """
    ).fetchall()

    total = c.execute(
        """
        SELECT COUNT(*) AS c
        FROM attractions
        """
    ).fetchone()["c"]

    cats = c.execute(
        """
        SELECT DISTINCT category
        FROM attractions
        ORDER BY category
        """
    ).fetchall()

    c.close()

    return render_template(
        "index.html",
        featured=featured,
        total=total,
        categories=cats
    )


# =========================================================
# ATTRACTIONS
# =========================================================

@app.route("/attractions")
def attractions():

    q = request.args.get(
        "q",
        ""
    ).strip()

    cat = request.args.get(
        "category",
        ""
    ).strip()

    c = get_connection()

    sql = """
        SELECT *
        FROM attractions
        WHERE 1 = 1
    """

    p = []

    if q:

        sql += """
            AND (
                name LIKE ?
                OR description LIKE ?
                OR address LIKE ?
            )
        """

        v = f"%{q}%"

        p += [
            v,
            v,
            v
        ]

    if cat:

        sql += """
            AND category = ?
        """

        p.append(cat)

    sql += """
        ORDER BY featured DESC, name
    """

    rows = c.execute(
        sql,
        p
    ).fetchall()

    cats = c.execute(
        """
        SELECT DISTINCT category
        FROM attractions
        ORDER BY category
        """
    ).fetchall()

    c.close()

    return render_template(
        "attractions.html",
        attractions=rows,
        categories=cats,
        q=q,
        selected_category=cat
    )

# =========================================================
# LIVE ATTRACTION SEARCH SUGGESTIONS
# =========================================================

@app.route("/api/attraction-suggestions")
def attraction_suggestions():
    q = request.args.get("q", "").strip()

    if len(q) < 2:
        return jsonify([])

    c = get_connection()

    search_value = f"%{q}%"

    rows = c.execute(
        """
        SELECT id, name, category, distance
        FROM attractions
        WHERE name LIKE ?
           OR category LIKE ?
           OR address LIKE ?
           OR description LIKE ?
        ORDER BY featured DESC, name
        LIMIT 8
        """,
        (search_value, search_value, search_value, search_value)
    ).fetchall()

    suggestions = [
        {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "distance": row["distance"],
            "url": url_for("detail", id=row["id"])
        }
        for row in rows
    ]

    c.close()

    return jsonify(suggestions)

# =========================================================
# ATTRACTION DETAILS
# =========================================================

@app.route("/attraction/<int:id>")
def detail(id):

    c = get_connection()

    a = c.execute(
        """
        SELECT *
        FROM attractions
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    c.close()

    if not a:
        abort(404)

    return render_template(
        "attraction_detail.html",
        attraction=a
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        u = request.form.get(
            "username",
            ""
        ).strip()

        e = request.form.get(
            "email",
            ""
        ).strip().lower()

        pw = request.form.get(
            "password",
            ""
        )

        cp = request.form.get(
            "confirm_password",
            ""
        )

        if not u or not e or not pw:

            flash(
                "Please complete all required fields.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if len(pw) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if pw != cp:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "register.html"
            )

        c = get_connection()

        try:

            c.execute(
                """
                INSERT INTO users(
                    username,
                    email,
                    password_hash,
                    role
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    'tourist'
                )
                """,
                (
                    u,
                    e,
                    generate_password_hash(pw)
                )
            )

            c.commit()

        except sqlite3.IntegrityError:

            c.close()

            flash(
                "Username or email already exists.",
                "error"
            )

            return render_template(
                "register.html"
            )

        c.close()

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        u = request.form.get(
            "username",
            ""
        ).strip()

        pw = request.form.get(
            "password",
            ""
        )

        c = get_connection()

        user = c.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (u,)
        ).fetchone()

        c.close()

        if user and check_password_hash(
            user["password_hash"],
            pw
        ):

            session.clear()

            session.update(
                user_id=user["id"],
                username=user["username"],
                role=user["role"]
            )

            if user["role"] == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )

            return redirect(
                request.args.get("next")
                or url_for("attractions")
            )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# PLAN
# =========================================================

@app.route("/plan")
@login_required
def plan():

    c = get_connection()

    rows = c.execute(
        """
        SELECT a.*
        FROM attractions a
        JOIN plans p
            ON p.attraction_id = a.id
        WHERE p.user_id = ?
        ORDER BY p.created_at
        """,
        (session["user_id"],)
    ).fetchall()

    c.close()

    return render_template(
        "plan.html",
        attractions=rows
    )


# =========================================================
# ADD TO PLAN
# =========================================================

@app.post("/plan/add/<int:id>")
@login_required
def add_plan(id):

    c = get_connection()

    attraction = c.execute(
        """
        SELECT id
        FROM attractions
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    if not attraction:

        c.close()

        abort(404)

    try:

        c.execute(
            """
            INSERT INTO plans(
                user_id,
                attraction_id
            )
            VALUES(
                ?,
                ?
            )
            """,
            (
                session["user_id"],
                id
            )
        )

        c.commit()

        flash(
            "Added to your one-day plan.",
            "success"
        )

    except sqlite3.IntegrityError:

        flash(
            "This attraction is already in your plan.",
            "info"
        )

    c.close()

    return redirect(
        request.referrer
        or url_for("plan")
    )


# =========================================================
# REMOVE FROM PLAN
# =========================================================

@app.post("/plan/remove/<int:id>")
@login_required
def remove_plan(id):

    c = get_connection()

    c.execute(
        """
        DELETE FROM plans
        WHERE user_id = ?
        AND attraction_id = ?
        """,
        (
            session["user_id"],
            id
        )
    )

    c.commit()

    c.close()

    flash(
        "Removed from your plan.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("plan")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    c = get_connection()

    rows = c.execute(
        """
        SELECT *
        FROM attractions
        ORDER BY id DESC
        """
    ).fetchall()

    n = c.execute(
        """
        SELECT COUNT(*) AS c
        FROM users
        WHERE role = 'tourist'
        """
    ).fetchone()["c"]

    c.close()

    return render_template(
        "admin_dashboard.html",
        attractions=rows,
        tourist_count=n
    )


# =========================================================
# FORM DATA
# =========================================================

def form_data():

    def num(x):

        try:

            value = request.form.get(
                x,
                ""
            ).strip()

            return (
                float(value)
                if value
                else None
            )

        except ValueError:

            return None

    return {
        k: request.form.get(
            k,
            ""
        ).strip()

        for k in [
            "name",
            "category",
            "description",
            "opening_time",
            "closing_time",
            "best_time",
            "visit_duration",
            "distance",
            "travel_tip",
            "address"
        ]

    } | {

        "latitude": num("latitude"),

        "longitude": num("longitude"),

        "featured": (
            1
            if request.form.get("featured") == "1"
            else 0
        )
    }


# =========================================================
# ADMIN - NEW ATTRACTION
# =========================================================

@app.route(
    "/admin/attraction/new",
    methods=["GET", "POST"]
)
@admin_required
def admin_new():

    if request.method == "POST":

        d = form_data()

        if (
            not d["name"]
            or not d["category"]
            or not d["description"]
        ):

            flash(
                "Name, category and description are required.",
                "error"
            )

            return render_template(
                "admin_form.html",
                attraction=d,
                editing=False
            )

        # Save image
        image_filename = save_image()

        if image_filename is None:

            return render_template(
                "admin_form.html",
                attraction=d,
                editing=False
            )

        c = get_connection()

        c.execute(
            """
            INSERT INTO attractions(
                name,
                category,
                description,
                opening_time,
                closing_time,
                best_time,
                visit_duration,
                distance,
                travel_tip,
                address,
                latitude,
                longitude,
                image,
                featured
            )
            VALUES(
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                d["name"],
                d["category"],
                d["description"],
                d["opening_time"],
                d["closing_time"],
                d["best_time"],
                d["visit_duration"],
                d["distance"],
                d["travel_tip"],
                d["address"],
                d["latitude"],
                d["longitude"],
                image_filename,
                d["featured"]
            )
        )

        c.commit()

        c.close()

        flash(
            "Attraction added.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_form.html",
        attraction=None,
        editing=False
    )


# =========================================================
# ADMIN - EDIT ATTRACTION
# =========================================================

@app.route(
    "/admin/attraction/<int:id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def admin_edit(id):

    c = get_connection()

    a = c.execute(
        """
        SELECT *
        FROM attractions
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    if not a:

        c.close()

        abort(404)

    if request.method == "POST":

        d = form_data()

        # Check whether a new image was uploaded
        uploaded_image = request.files.get("image")

        if (
            uploaded_image
            and uploaded_image.filename
        ):

            image_filename = save_image()

            if image_filename is None:

                c.close()

                return render_template(
                    "admin_form.html",
                    attraction=a,
                    editing=True
                )

        else:

            # Keep existing image
            image_filename = a["image"]

        c.execute(
            """
            UPDATE attractions
            SET
                name = ?,
                category = ?,
                description = ?,
                opening_time = ?,
                closing_time = ?,
                best_time = ?,
                visit_duration = ?,
                distance = ?,
                travel_tip = ?,
                address = ?,
                latitude = ?,
                longitude = ?,
                image = ?,
                featured = ?
            WHERE id = ?
            """,
            (
                d["name"],
                d["category"],
                d["description"],
                d["opening_time"],
                d["closing_time"],
                d["best_time"],
                d["visit_duration"],
                d["distance"],
                d["travel_tip"],
                d["address"],
                d["latitude"],
                d["longitude"],
                image_filename,
                d["featured"],
                id
            )
        )

        c.commit()

        c.close()

        flash(
            "Attraction updated.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    c.close()

    return render_template(
        "admin_form.html",
        attraction=a,
        editing=True
    )


# =========================================================
# ADMIN - DELETE ATTRACTION
# =========================================================

@app.post(
    "/admin/attraction/<int:id>/delete"
)
@admin_required
def admin_delete(id):

    c = get_connection()

    c.execute(
        """
        DELETE FROM attractions
        WHERE id = ?
        """,
        (id,)
    )

    c.commit()

    c.close()

    flash(
        "Attraction deleted.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def not_found(e):

    return render_template(
        "404.html"
    ), 404


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)