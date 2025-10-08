from flask import Flask, render_template, request, url_for
import os
import re

app = Flask(__name__)

# Path to your Sniffer output directory
OUTPUT_DIR = "/home/nomvuyo/2025/Honours/BIF703/Archaea/Input_Output_Archaea/Sniffer/output"

# ------------------ PARSING FUNCTIONS ------------------

def parse_files():
    """
    Scan OUTPUT_DIR and return structured info per sequence ID:
    {
        "CP045482": {
            "organism": "Acidianus_ambivalens_strain_LEI_10_chromosome",
            "domain": "Archaea",
            "files": ["..._MGE.out", "..._MGE.fas", "..._MGE.svg"]
        },
        ...
    }
    """
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
    """Parse fasta file into GI blocks keyed by GI IDs and coordinates."""
    gi_data = {}
    with open(filepath, "r") as f:
        content = f.read()
    entries = re.findall(r"(>.*?\n[^>]+)", content, re.S)
    for entry in entries:
        gi_match = re.search(r">([\w:.]+)", entry)
        gi_id = gi_match.group(1) if gi_match else "Unknown"

        coord_match = re.search(r"\[(\d+-\d+)\]", entry)
        coords = coord_match.group(1) if coord_match else "Unknown"

        gi_data[gi_id] = {"gi_id": gi_id, "coordinates": coords, "block": entry.strip()}
    return gi_data

# ------------------ ROUTES ------------------

@app.route("/")
@app.route("/home")
def home():
    seq_map = parse_files()
    archaea_count = sum(1 for v in seq_map.values() if v["domain"].lower() == "archaea")
    bacteria_count = sum(1 for v in seq_map.values() if v["domain"].lower() == "bacteria")
    return render_template("home.html",
                           archaea_count=archaea_count,
                           bacteria_count=bacteria_count)

@app.route("/index")
@app.route("/index/<domain>")
def index(domain=None):
    seq_map = parse_files()
    if domain:
        seq_map = {k: v for k, v in seq_map.items() if v["domain"].lower() == domain.lower()}
    return render_template("index.html", seq_map=seq_map, domain=domain)

@app.route("/genome/<seq_id>")
def genome(seq_id):
    seq_map = parse_files()
    if seq_id not in seq_map:
        return f"Sequence ID {seq_id} not found", 404
    return render_template("genome.html", seq_id=seq_id, data=seq_map[seq_id])

@app.route("/file/<seq_id>/<filename>", methods=["GET", "POST"])
def view_file(seq_id, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return f"File {filename} not found for {seq_id}", 404

    ext = filename.split(".")[-1]
    selected_block = None
    gi_options, coord_options = [], []

    if ext == "out":
        gi_data = parse_out_file(filepath)
    elif ext in ["fas", "fasta"]:
        gi_data = parse_fasta_file(filepath)
    elif ext == "svg":
        with open(filepath, "r") as f:
            svg_content = f.read()
        return render_template("viewer.html", file_type="svg",
                               filename=filename, svg_content=svg_content, seq_id=seq_id)
    else:
        return "Unsupported file type"

    gi_options = list(gi_data.keys())
    coord_options = [v["coordinates"] for v in gi_data.values()]

    if request.method == "POST":
        gi_id = request.form.get("gi_id")
        coord = request.form.get("coordinates")
        if gi_id and gi_id in gi_data:
            selected_block = gi_data[gi_id]["block"]
        elif coord:
            for v in gi_data.values():
                if v["coordinates"] == coord:
                    selected_block = v["block"]
                    break

    return render_template("viewer.html", file_type=ext, filename=filename,
                           gi_options=gi_options, coord_options=coord_options,
                           selected_block=selected_block, seq_id=seq_id)

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)
