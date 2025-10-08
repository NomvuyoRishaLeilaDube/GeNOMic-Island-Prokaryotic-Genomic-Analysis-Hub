from flask import Flask, render_template, request, url_for, redirect
import os

app = Flask(__name__)

BASE_DIR = "./genomes"

def get_genomes(domain):
    folder = os.path.join(BASE_DIR, domain)
    if not os.path.exists(folder):
        return []
    files = os.listdir(folder)
    return sorted([f for f in files if f.endswith((".out", ".fas", ".svg"))])

def read_file(domain, filename):
    path = os.path.join(BASE_DIR, domain, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()

@app.route("/")
def home():
    archaea_count = len(get_genomes("archaea"))
    bacteria_count = len(get_genomes("bacteria"))
    return render_template("home.html", archaea_count=archaea_count, bacteria_count=bacteria_count)

@app.route("/genomes/<domain>")
def genomes(domain):
    seq_map = get_genomes(domain)
    return render_template("index.html", seq_map=seq_map, domain=domain)

@app.route("/viewer/<domain>/<filename>", methods=["GET", "POST"])
def view_file(domain, filename):
    ext = filename.split(".")[-1]
    content = read_file(domain, filename)
    
    # Reset functionality for .out and .fas
    if request.method == "POST" and request.form.get("reset"):
        return redirect(url_for("genomes", domain=domain))
    
    return render_template(
        "viewer.html",
        file_type=ext,
        filename=filename,
        domain=domain,
        content=content
    )

if __name__ == "__main__":
    app.run(debug=True)
