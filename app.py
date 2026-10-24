
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection and table creation
def get_db():
    conn = sqlite3.connect("notes.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    return conn


# Website design
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Notes Management System</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
            color: #1e293b;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        h1 {
            color: #2563eb;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #64748b;
            margin-bottom: 25px;
        }

        .form-box {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px #0000000d;
            margin-bottom: 30px;
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin: 8px 0 15px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 15px;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        button, .btn {
            display: inline-block;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }

        button {
            background: #2563eb;
            color: white;
        }

        button:hover {
            background: #1d4ed8;
        }

        .notes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
        }

        .note {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 3px 10px #0000000d;
            overflow-wrap: anywhere;
        }

        .note h3 {
            margin-top: 0;
            color: #1d4ed8;
        }

        .note-content {
            white-space: pre-wrap;
            line-height: 1.5;
        }

        .edit-btn {
            background: #e0ecff;
            color: #1d4ed8;
        }

        .delete-btn {
            background: #fee2e2;
            color: #b91c1c;
        }

        .empty {
            color: #64748b;
        }

        @media (max-width: 600px) {
            body {
                padding: 15px;
            }
        }
    </style>
</head>

<body>
<div class="container">

    <h1>☁️ Cloud Notes Management System</h1>
    <p class="subtitle">
        Create, organize, update and manage your notes easily.
    </p>

    <div class="form-box">
        <h2>Add a New Note</h2>

        <form method="POST" action="{{ url_for('add_note') }}">
            <label for="title">Note Title</label>
            <input id="title" name="title"
                   placeholder="Enter note title" required>

            <label for="content">Note Content</label>
            <textarea id="content" name="content"
                      placeholder="Write your note here..."
                      required></textarea>

            <button type="submit">+ Save Note</button>
        </form>
    </div>

    <h2>My Notes ({{ notes|length }})</h2>

    {% if notes %}
        <div class="notes-grid">
        {% for note in notes %}
            <div class="note">
                <h3>{{ note[1] }}</h3>

                <p class="note-content">{{ note[2] }}</p>

                <a class="btn edit-btn"
                   href="{{ url_for('edit_note', note_id=note[0]) }}">
                    ✏️ Edit
                </a>

                <form method="POST"
                      action="{{ url_for('delete_note', note_id=note[0]) }}"
                      style="display:inline;"
                      onsubmit="return confirm('Delete this note?');">
                    <button class="delete-btn" type="submit">
                        🗑️ Delete
                    </button>
                </form>
            </div>
        {% endfor %}
        </div>
    {% else %}
        <p class="empty">No notes yet. Add your first note!</p>
    {% endif %}

</div>
</body>
</html>
"""


# Home page: display all notes
@app.route("/")
def home():
    conn = get_db()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string(HTML, notes=notes)


# Add a new note
@app.route("/add", methods=["POST"])
def add_note():
    title = request.form["title"].strip()
    content = request.form["content"].strip()

    if title and content:
        conn = get_db()
        conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("home"))


# Edit an existing note
@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    conn = get_db()

    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?", (note_id,)
    ).fetchone()

    if note is None:
        conn.close()
        return "Note not found", 404

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if title and content:
            conn.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ?",
                (title, content, note_id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("home"))

    conn.close()

    edit_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Edit Note</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                padding: 30px;
            }
            .box {
                background: white;
                max-width: 650px;
                margin: 30px auto;
                padding: 25px;
                border-radius: 12px;
            }
            input, textarea {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                margin: 10px 0 18px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 15px;
            }
            textarea {
                height: 150px;
            }
            button, a {
                display: inline-block;
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                cursor: pointer;
                font-size: 14px;
            }
            button {
                background: #2563eb;
                color: white;
            }
            a {
                background: #e2e8f0;
                color: #1e293b;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>✏️ Edit Note</h1>

            <form method="POST">
                <label for="title">Note Title</label>
                <input id="title" name="title"
                       value="{{ note[1] }}" required>

                <label for="content">Note Content</label>
                <textarea id="content" name="content"
                          required>{{ note[2] }}</textarea>

                <button type="submit">Update Note</button>
                <a href="{{ url_for('home') }}">Cancel</a>
            </form>
        </div>
    </body>
    </html>
    """

    return render_template_string(edit_html, note=note)


# Delete a note
@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM notes WHERE id = ?", (note_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
