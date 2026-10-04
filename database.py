import os
import sqlite3

from werkzeug.security import generate_password_hash


# =========================================================
# DATABASE PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DB_PATH = os.path.join(
    DB_DIR,
    "beyond_badulla.db"
)

SCHEMA_PATH = os.path.join(
    BASE_DIR,
    "schema.sql"
)


# =========================================================
# INITIAL ATTRACTIONS
# =========================================================

ATTRACTIONS = [
    (
        "Nine Arches Bridge",
        "Heritage",
        "An iconic colonial-era railway bridge surrounded by lush green hills and tea plantations near Ella.",
        "06:00 AM",
        "06:00 PM",
        "Approx. 32 km from Badulla",
        "Visit early for a quieter experience and check the train schedule.",
        "Nine Arches Bridge, Demodara, Ella",
        6.8768,
        81.0597,
        "nine-arches.jpg",
        1
    ),

    (
        "Flying Ravana Adventure Park",
        "Adventure",
        "An adventure destination offering ziplining and outdoor experiences with panoramic hill-country views.",
        "08:30 AM",
        "05:30 PM",
        "Approx. 35 km from Badulla",
        "Wear comfortable clothes and check weather conditions.",
        "Flying Ravana, Ella",
        6.8667,
        81.0560,
        "flying-ravana.jpg",
        1
    ),

    (
        "Little Adam's Peak",
        "Nature",
        "A popular hilltop viewpoint with an accessible hike and beautiful views across Ella's mountains.",
        "06:00 AM",
        "06:30 PM",
        "Approx. 34 km from Badulla",
        "Carry water and use shoes with good grip.",
        "Little Adam's Peak, Ella",
        6.8667,
        81.0542,
        "little-adams-peak.jpg",
        1
    ),

    (
        "Sarungal Kanda",
        "Nature",
        "A scenic mountain area offering peaceful landscapes and opportunities for nature exploration.",
        "06:00 AM",
        "05:30 PM",
        "Within the Badulla region",
        "Take sufficient water and avoid isolated trails after heavy rain.",
        "Sarungal Kanda, Uva",
        7.0000,
        81.0000,
        "sarungal-kanda.jpg",
        0
    ),

    (
        "Narangala Mountain",
        "Hiking",
        "A striking mountain destination known for ridge views, sunrise scenery and a challenging hiking experience.",
        "05:30 AM",
        "05:30 PM",
        "Approx. 30 km from Badulla",
        "Start early, carry water and avoid severe weather.",
        "Narangala Mountain, Uva",
        7.0315,
        81.0590,
        "narangala.jpg",
        1
    ),

    (
        "Bogoda Wooden Bridge",
        "Heritage",
        "A historic wooden bridge associated with the Bogoda temple complex and traditional Sri Lankan craftsmanship.",
        "07:00 AM",
        "05:30 PM",
        "Approx. 15 km from Badulla",
        "Combine the bridge visit with the nearby historic temple.",
        "Bogoda, Badulla",
        6.8980,
        81.0200,
        "bogoda-bridge.jpg",
        1
    ),

    (
        "Dunhinda Falls",
        "Waterfall",
        "A spectacular waterfall surrounded by forest and one of the best-known natural attractions near Badulla.",
        "07:00 AM",
        "05:30 PM",
        "Approx. 5 km from Badulla",
        "The trail can be slippery; wear suitable footwear.",
        "Dunhinda, Badulla",
        7.0038,
        81.0576,
        "dunhinda.jpg",
        1
    ),

    (
        "Halaba Steel Bridge",
        "Heritage",
        "A distinctive local bridge and photographic viewpoint surrounded by Badulla landscapes.",
        "06:00 AM",
        "06:00 PM",
        "Within the Badulla area",
        "Use caution around traffic and unsafe sections.",
        "Halaba, Badulla",
        6.9900,
        81.0600,
        "halaba-bridge.jpg",
        0
    ),

    (
        "Uva Museum",
        "Culture",
        "A local museum offering visitors an introduction to the history, culture and heritage of Uva.",
        "09:00 AM",
        "05:00 PM",
        "Approx. 1 km from Badulla town",
        "Allow enough time to explore the exhibits.",
        "Badulla, Uva Province",
        6.9847,
        81.0567,
        "uva-museum.jpg",
        0
    ),

    (
        "Uva Halpewatte Tea Factory Tour",
        "Tea & Culture",
        "A tea experience where visitors can learn about tea processing in the hill country.",
        "08:00 AM",
        "05:00 PM",
        "Approx. 30 km from Badulla",
        "Contact the venue before visiting to confirm tour availability.",
        "Halpewatte Tea Factory, Ella",
        6.8866,
        81.0491,
        "tea-factory.jpg",
        1
    ),

    (
        "Muthiyangana Raja Maha Vihara",
        "Culture",
        "A historic Buddhist temple in Badulla and an important cultural and religious landmark.",
        "05:00 AM",
        "09:00 PM",
        "Approx. 1 km from Badulla town",
        "Dress respectfully and maintain a quiet atmosphere.",
        "Muthiyangana Road, Badulla",
        6.9934,
        81.0560,
        "muthiyangana.jpg",
        0
    )
]


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    os.makedirs(
        DB_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# =========================================================
# DATABASE MIGRATION
# =========================================================

def ensure_attraction_columns(connection):

    columns = connection.execute(
        """
        PRAGMA table_info(attractions)
        """
    ).fetchall()

    column_names = {
        column["name"]
        for column in columns
    }

    # Add best_time if it does not already exist
    if "best_time" not in column_names:

        connection.execute(
            """
            ALTER TABLE attractions
            ADD COLUMN best_time TEXT
            """
        )

    # Add visit_duration if it does not already exist
    if "visit_duration" not in column_names:

        connection.execute(
            """
            ALTER TABLE attractions
            ADD COLUMN visit_duration TEXT
            """
        )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    connection = get_connection()

    # Load database schema
    with open(
        SCHEMA_PATH,
        encoding="utf-8"
    ) as schema_file:

        connection.executescript(
            schema_file.read()
        )

    # -----------------------------------------------------
    # Add new attraction columns if they do not exist
    # -----------------------------------------------------

    ensure_attraction_columns(connection)

    # -----------------------------------------------------
    # Create admin account if it does not already exist
    # -----------------------------------------------------

    admin_exists = connection.execute(
        """
        SELECT id
        FROM users
        WHERE username = 'admin'
        """
    ).fetchone()

    if not admin_exists:

        connection.execute(
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
                'admin'
            )
            """,
            (
                "admin",
                "admin@beyondbadulla.lk",
                generate_password_hash("admin123")
            )
        )

    # -----------------------------------------------------
    # Insert default attractions only if database is empty
    # -----------------------------------------------------

    attraction_count = connection.execute(
        """
        SELECT COUNT(*) AS c
        FROM attractions
        """
    ).fetchone()["c"]

    if attraction_count == 0:

        connection.executemany(
            """
            INSERT INTO attractions(
                name,
                category,
                description,
                opening_time,
                closing_time,
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
                ?
            )
            """,
            ATTRACTIONS
        )

    connection.commit()

    connection.close()


# =========================================================
# RUN DATABASE INITIALIZATION
# =========================================================

if __name__ == "__main__":

    init_db()

    print(DB_PATH)