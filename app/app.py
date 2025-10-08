from flask import Flask, render_template, request
import os, re, time
from datetime import datetime

app = Flask(__name__)

# Path to your Sniffer output directory
OUTPUT_DIR = "/home/nomvuyo/2025/Honours/BIF703/Archaea/Input_Output_Archaea/Sniffer/output"

# ---------------- CACHE ----------------
# Stores GI counts and last update times per domain
cache = {
    "archaea_islands": 0,
    "archaea_update": None,
    "bacteria_islands": 0,
    "bacteria_update": None,
    "last_file_state": {}  # Tracks last modified times for .out files
}

# ------------------ PARSERS ------------------
def parse_files():
    """Scan OUTPUT_DIR and return structured info per sequence ID."""
    seq_map = {}
    for fname in os.listdir(OUTPUT_DIR):
        match = re.match(r"(.+)_\[(.+)\]_MGE\.(.+)", fname)
        if match:
            organism, seq_id, ext = match.groups()
            if seq_id not in seq_map:
                seq_map[seq_id] = {"organism": organism, "domain": "Archaea", "files": []}
            seq_map[seq_id]["files"].append(fname)
    return seq_map

def parse_out_file(filepath):
    """Parse .out file into GI blocks keyed by GI IDs and coordinates."""
    with open(filepath, "r") as f:
        content = f.read()
    entries = re.findall(r"(<GI>.*?<END>)", content, re.S)
    gi_data = {}
    for entry in entries:
        gi_match = re.search(r"<GI>\s*([\w:.]+)", entry)
        gi_id = gi_match.group(1) if gi_match else "Unknown"

        coord_match = re.search(r"<COORDINATES>\s*([\d-]+)", entry)
        coords = coord_match.group(1) if coord_match else "Unknown"

        gi_data[gi_id] = {"gi_id": gi_id, "coordinates": coords, "block": entry.strip()}
    return gi_data

def parse_fasta_file(filepath):
    """Parse fasta file into GI blocks keyed by GI IDs and coordinates, keeping only DNA sequences."""
    gi_data = {}
    with open(filepath, "r") as f:
        content = f.read()
    entries = re.findall(r"(>.*?\n(?:[^>]+))", content, re.S)
    for entry in entries:
        gi_match = re.search(r">([\w:.]+)", entry)
        gi_id = gi_match.group(1) if gi_match else "Unknown"

        coord_match = re.search(r"\[(\d+-\d+)\]", entry)
        coords = coord_match.group(1) if coord_match else "Unknown"

        # Keep only lines that are DNA sequences (A/C/G/T)
        lines = entry.splitlines()
        seq_lines = [line.strip() for line in lines[1:] if re.match(r"^[ACGTacgt]+$", line)]
        clean_block = lines[0] + "\n" + "\n".join(seq_lines)

        gi_data[gi_id] = {"gi_id": gi_id, "coordinates": coords, "block": clean_block.strip()}
    return gi_data

def get_last_updated(filepath):
    """Return last modified date of a file."""
    if os.path.exists(filepath):
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

# ------------------ CACHE UPDATE ------------------
def update_cache():
    """Update cached GI counts and last updated timestamps only if files changed."""
    global cache
    seq_map = parse_files()

    # Get last modified times for all .out files
    new_file_state = {
        f: os.path.getmtime(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith(".out")
    }

    # Only update if any file changed
    if new_file_state != cache["last_file_state"]:
        archaea_total = 0
        bacteria_total = 0

        for seq_id, data in seq_map.items():
            gi_count = 0
            last_update = "N/A"
            for f in data.get("files", []):
                if f.endswith(".out"):
                    path = os.path.join(OUTPUT_DIR, f)
                    with open(path) as fh:
                        gi_count += sum(1 for line in fh if line.startswith("<GI>"))
                    last_update = get_last_updated(path)
            data["num_gis"] = gi_count
            data["last_updated"] = last_update

            if data["domain"].lower() == "archaea":
                archaea_total += gi_count
            else:
                bacteria_total += gi_count

        # Update cache
        cache["archaea_islands"] = archaea_total
        cache["archaea_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        cache["bacteria_islands"] = bacteria_total
        cache["bacteria_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        cache["last_file_state"] = new_file_state

    return seq_map

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    seq_map = update_cache()

    archaea_count = sum(1 for v in seq_map.values() if v["domain"].lower() == "archaea")
    bacteria_count = sum(1 for v in seq_map.values() if v["domain"].lower() == "bacteria")

    return render_template(
        "home.html",
        archaea_count=archaea_count,
        bacteria_count=bacteria_count,
        archaea_islands=cache["archaea_islands"],
        bacteria_islands=cache["bacteria_islands"],
        archaea_update=cache["archaea_update"],
        bacteria_update=cache["bacteria_update"]
    )

@app.route("/index")
@app.route("/index/<domain>")
def index(domain=None):
    seq_map = update_cache()
    if domain:
        seq_map = {k: v for k, v in seq_map.items() if v["domain"].lower() == domain.lower()}
    return render_template("index.html", seq_map=seq_map, domain=domain if domain else "All")

@app.route("/genomes/<domain>")
def genomes(domain):
    seq_map = update_cache()
    seq_map = {k: v for k, v in seq_map.items() if v["domain"].lower() == domain.lower()}
    return render_template("index.html", seq_map=seq_map, domain=domain)

@app.route("/genome/<seq_id>")
def genome(seq_id):
    seq_map = update_cache()
    if seq_id not in seq_map:
        return f"Sequence ID {seq_id} not found", 404
    data = seq_map[seq_id]
    return render_template("genome.html", seq_id=seq_id, data=data)

@app.route("/file/<seq_id>/<filename>", methods=["GET", "POST"])
def view_file(seq_id, filename):
    seq_map = update_cache()
    if seq_id not in seq_map:
        return f"Sequence ID {seq_id} not found", 404
    data = seq_map[seq_id]
    domain = data["domain"]

    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return f"File {filename} not found for {seq_id}", 404

    ext = filename.split(".")[-1]
    selected_block = None
    gi_options, coord_options = [], []

    # --- OUT file ---
    if ext == "out":
        gi_data = parse_out_file(filepath)
        gi_options = list(gi_data.keys())
        coord_options = [v["coordinates"] for v in gi_data.values()]

        if request.method == "POST":
            if request.form.get("reset"):
                selected_block = "\n\n".join([v["block"] for v in gi_data.values()])
            else:
                gi_id = request.form.get("gi_id")
                coord = request.form.get("coordinates")
                if gi_id and gi_id in gi_data:
                    selected_block = gi_data[gi_id]["block"]
                elif coord:
                    for v in gi_data.values():
                        if v["coordinates"] == coord:
                            selected_block = v["block"]
                            break
        if not selected_block:
            selected_block = "\n\n".join([v["block"] for v in gi_data.values()])

        return render_template("viewer.html", file_type="out", filename=filename,
                               gi_options=gi_options, coord_options=coord_options,
                               selected_block=selected_block, seq_id=seq_id, domain=domain)

    # --- FASTA file ---
    elif ext in ["fas", "fasta"]:
        gi_data = parse_fasta_file(filepath)
        gi_options = list(gi_data.keys())
        coord_options = [v["coordinates"] for v in gi_data.values()]

        if request.method == "POST":
            if request.form.get("reset"):
                selected_block = "\n\n".join([v["block"] for v in gi_data.values()])
            else:
                gi_id = request.form.get("gi_id")
                coord = request.form.get("coordinates")
                if gi_id and gi_id in gi_data:
                    selected_block = gi_data[gi_id]["block"]
                elif coord:
                    for v in gi_data.values():
                        if v["coordinates"] == coord:
                            selected_block = v["block"]
                            break
        if not selected_block:
            selected_block = "\n\n".join([v["block"] for v in gi_data.values()])

        return render_template("viewer.html", file_type="fas", filename=filename,
                               gi_options=gi_options, coord_options=coord_options,
                               selected_block=selected_block, seq_id=seq_id, domain=domain)

    # --- SVG file ---
    elif ext == "svg":
        with open(filepath, "r") as f:
            svg_content = f.read()
        return render_template("viewer.html", file_type="svg",
                               filename=filename, svg_content=svg_content,
                               seq_id=seq_id, domain=domain)

    return "Unsupported file type"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)
