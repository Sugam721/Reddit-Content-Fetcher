from flask import Flask, render_template_string, request
from editor_contextual import edit_comment  # your existing logic here
import re
from markupsafe import escape

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Editor Contextual Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        textarea { width: 100%; height: 200px; margin-bottom: 10px; font-family: monospace; font-size: 14px; }
        .container { display: flex; gap: 20px; }
        .box { flex: 1; }
        h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        pre { white-space: pre-wrap; background: #f9f9f9; padding: 10px; border: 1px solid #ddd; height: 400px; overflow-y: scroll; }
        strong { font-weight: bold; color: black; }  /* changed from red to black */
    </style>
</head>
<body>
    <h1>Editor Contextual - Web Interface</h1>
    <form method="post">
        <label for="original_text"><strong>Enter Original Text:</strong></label><br />
        <textarea id="original_text" name="original_text" placeholder="Paste your original text here...">{{ original_text|default('') }}</textarea><br />
        <button type="submit">Process</button>
    </form>

    {% if processed %}
    <div class="container">
        <div class="box">
            <h2>Original with Bolded Changes</h2>
            <pre>{{ original_output|safe }}</pre>
        </div>
        <div class="box">
            <h2>Clean Edited Text</h2>
            <pre>{{ edited_output|safe }}</pre>
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    original_text = ""
    original_output = ""
    edited_output = ""
    processed = False

    if request.method == "POST":
        original_text = request.form.get("original_text", "")

        # Replace all forms of <br> tags (case-insensitive) with newline
        original_text = re.sub(r'(?i)<br\s*/?>', '\n', original_text)

        if original_text.strip():
            # Call your existing edit_comment logic
            bolded_original, edited = edit_comment(original_text)

            # Convert markdown-style bold (**text**) to HTML <strong> tags
            def bold_replacer(match):
                return f"<strong>{match.group(1)}</strong>"

            html_original = re.sub(r"\*\*(.+?)\*\*", bold_replacer, bolded_original)

            # Format edited text into paragraphs for HTML
            paragraphs = re.split(r'\n\s*\n', edited.strip())
            html_edited = "".join(
                f"<p>{escape(p.strip()).replace(chr(10), '<br />')}</p>" for p in paragraphs
            )

            original_output = html_original
            edited_output = html_edited
            processed = True

    return render_template_string(
        HTML_TEMPLATE,
        original_text=original_text,
        original_output=original_output,
        edited_output=edited_output,
        processed=processed,
    )


if __name__ == "__main__":
    print("🚀 Starting web server at http://127.0.0.1:5000")
    app.run(debug=True)
