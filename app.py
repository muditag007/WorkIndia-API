from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from config import Config
from utils import token_required, get_user_by_username

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

@app.route("/")
def hello_world():
    return "Hello, My World!"

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    try:
        cur = mysql.connection.cursor()

        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cur.fetchone()[0] > 0:
            return jsonify({"status": "Username already taken. Please use a different username.", "status_code": 409}), 409

        cur.execute(
            """INSERT INTO users (username, password, email) VALUES (%s, %s, %s)""",
            (username, password, email),
        )
        mysql.connection.commit()
        user_id = cur.lastrowid
        cur.close()
        return (
            jsonify(
                {
                    "status": "Account successfully created",
                    "status_code": 200,
                    "user_id": user_id,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    user = get_user_by_username(mysql, username)
    # print(user)
    if user:
        if user[2] == password:
            token = jwt.encode(
                {
                    "user_id": user[0],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify(
                {
                    "status": "Login successful",
                    "status_code": 200,
                    "user_id": user[0],
                    "access_token": token,
                }
            )
        else:
            return jsonify(
                {
                    "status": "Password Mismatch",
                    "status_code": 402,
                }
            )
    else:
        return jsonify(
            {
                "status": "Incorrect username/password provided. Please retry",
                "status_code": 401,
            }
        )

@app.route("/api/shorts/create", methods=["POST"])
def add_short():
    data = request.json
    category = data["category"]
    title = data["title"]
    author = data["author"]
    publish_date = data["publish_date"]
    content = data["content"]
    actual_content_link = data["actual_content_link"]
    image = data["image"]

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO shorts (category, title, author, publish_date, content, actual_content_link, image) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (category, title, author, publish_date, content, actual_content_link, image),
    )
    mysql.connection.commit()
    short_id = cur.lastrowid
    cur.close()

    return jsonify(
        {
            "message": "Short added successfully",
            "short_id": short_id,
            "status_code": 200,
        }
    )


@app.route("/api/shorts/feed", methods=["GET"])
def get_shorts_feed():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shorts ORDER BY publish_date DESC, upvotes DESC")
    shorts = cur.fetchall()
    cur.close()
    return jsonify(shorts)

@app.route("/api/shorts/filter", methods=["GET"])
@token_required
def filter_shorts():
    filter_params = request.args.get("filter", "{}")
    search_params = request.args.get("search", "{}")
    print("here")
    import json
    filter_params = json.loads(filter_params)
    search_params = json.loads(search_params)

    query = "SELECT * FROM shorts"
    query_params = []

    if "category" in filter_params:
        query += " AND category = %s"
        query_params.append(filter_params["category"])
    if "publish_date" in filter_params:
        query += " AND publish_date >= %s"
        query_params.append(filter_params["publish_date"])
    if "upvote" in filter_params:
        query += " AND upvote >= %s"
        query_params.append(filter_params["upvote"])

    if "title" in search_params:
        query += " AND title LIKE %s"
        query_params.append(f"%{search_params['title']}%")
    if "keyword" in search_params:
        query += " AND (title LIKE %s OR content LIKE %s)"
        query_params.extend([f"%{search_params['keyword']}%", f"%{search_params['keyword']}%"])
    if "author" in search_params:
        query += " AND author LIKE %s"
        query_params.append(f"%{search_params['author']}%")

    cur = mysql.connection.cursor()
    cur.execute(query, query_params)
    shorts = cur.fetchall()
    cur.close()

    if shorts:
        return jsonify(shorts)
    else:
        return jsonify(
            {"status": "No short matches your search criteria", "status_code": 400}
        )

if __name__ == "__main__":
    app.run(debug=True)
