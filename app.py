from flask import Flask, render_template, request, url_for, redirect
import os, re, time
from datetime import datetime

app = Flask(__name__)

# ---------------- OUTPUT DIRECTORIES ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIRS = {
    "archaea": os.path.join(BASE_DIR, "output"),
    "bacteria": os.path.join(BASE_DIR.replace("Archaea/Input_Output_Archaea/Sniffer", 
                                              "Bacteria/Input_Output_Bacteria/Sniffer"), 
                             "output")
}

# ---------------- CACHE ----------------
cache = {
    "archaea_islands": 0,
    "archaea_update": None,
    "bacteria_islands": 0,
    "bacteria_update": None,
    "last_file_state": {}  # Tracks last modified times per domain+file
}

# ---------------- PARSERS ----------------
def parse_files():
    """Scan all domain directories and return structured info per sequence ID."""
    seq_map = {}
    for domain, dir_path in OUTPUT_DIRS.items():
        for fname in os.listdir(dir_path):
            match = re.match(r"(.+)_\[(.+)\]_MGE\.(.+)", fname)
            if match:
                organism, seq_id, ext = match.groups()
                if seq_id not in seq_map:
                    seq_map[seq_id] = {"organism": organism,
                                       "domain": domain.capitalize(),
                                       "files": [],
                                       "dir": dir_path}
                seq_map[seq_id]["files"].append(fname)

# Deduplicate and sort files: svg first, then out, then fasta (UPDATED VERSION, IN USE)
    for seq_id, data in seq_map.items():
        # Remove duplicates while preserving order
        data["files"] = list(dict.fromkeys(data["files"]))
        # Sort by type
        data["files"].sort(key=lambda x: (0 if x.endswith(".svg") else 1 if x.endswith(".out") else 2))

    return seq_map

       # Sort files: svg first, then out, then fasta (OLD, not necessary but don't want to change the code too much now:)
    for seq_id, data in seq_map.items():
            if data["domain"].lower() == domain:
                data["files"].sort(key=lambda x: (0 if x.endswith(".svg") else 1 if x.endswith(".out") else 2))
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
        lines = entry.splitlines()
        seq_lines = [line.strip() for line in lines[1:] if re.match(r"^[ACGTacgt]+$", line)]
        clean_block = lines[0] + "\n" + "\n".join(seq_lines)
        gi_data[gi_id] = {"gi_id": gi_id, "coordinates": coords, "block": clean_block.strip()}
    return gi_data

def get_last_updated(filepath):
    if os.path.exists(filepath):
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

# ---------------- CACHE UPDATE ----------------
def update_cache():
    global cache
    seq_map = parse_files()
    new_file_state = {}
    for domain, dir_path in OUTPUT_DIRS.items():
        for f in os.listdir(dir_path):
            if f.endswith(".out"):
                key = f"{domain}_{f}"
                new_file_state[key] = os.path.getmtime(os.path.join(dir_path, f))

    archaea_total = 0
    bacteria_total = 0

    for seq_id, data in seq_map.items():
        gi_count = 0
        last_update = "N/A"
        for f in data.get("files", []):
            path = os.path.join(data["dir"], f)
            if f.endswith(".out"):
                with open(path) as fh:
                    gi_count += sum(1 for line in fh if line.startswith("<GI>"))
                last_update = get_last_updated(path)
        data["num_gis"] = gi_count
        data["last_updated"] = last_update
        if data["domain"].lower() == "archaea":
            archaea_total += gi_count
        else:
            bacteria_total += gi_count

# Update cache totals and timestamps
    if new_file_state != cache["last_file_state"]:
        cache["archaea_islands"] = archaea_total
        cache["archaea_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        cache["bacteria_islands"] = bacteria_total
        cache["bacteria_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        cache["last_file_state"] = new_file_state

    return seq_map

# ---------------- ROUTES ----------------
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
    filepath = os.path.join(data["dir"], filename)
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
                               filename=filename, svg_content=svg_content,
                               seq_id=seq_id, domain=domain)
    else:
        return "Unsupported file type"

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

    return render_template("viewer.html", file_type=ext, filename=filename,
                           gi_options=gi_options, coord_options=coord_options,
                           selected_block=selected_block, seq_id=seq_id, domain=domain)


# BLAST SECTION  

@app.route("/blast_gi", methods=["POST"])
def blast_gi():
    seq_id = request.form.get("seq_id")
    fasta_block = request.form.get("fasta_block")
    results = []

    if not fasta_block:
        return "No sequence selected for BLAST.", 400

    try:
        from Bio.Blast import NCBIWWW, NCBIXML
        from io import StringIO
        import os

        # Run BLAST
        result_handle = NCBIWWW.qblast("blastn", "nt", fasta_block, hitlist_size=50)
        xml_data = result_handle.read()

        # Save XML
        BLAST_RESULTS_DIR = os.path.join("static", "blast_results")
        os.makedirs(BLAST_RESULTS_DIR, exist_ok=True)
        xml_filename = f"{seq_id}_blast.xml"
        xml_path = os.path.join(BLAST_RESULTS_DIR, xml_filename)
        with open(xml_path, "w") as f:
            f.write(xml_data)

        # Parse BLAST
        blast_records = NCBIXML.read(StringIO(xml_data))
        seen_organisms = set()

        for alignment in blast_records.alignments:
            for hsp in alignment.hsps:
                organism = alignment.title.split(",")[0].split()[-1]
                if organism not in seen_organisms:
                    seen_organisms.add(organism)

                    pct_identity = round((hsp.identities / hsp.align_length) * 100, 2)
                    query_cov = round((hsp.align_length / blast_records.query_length) * 100, 2)

                    # Extract accession and HSP coordinates for region-specific NCBI link
                    accession = alignment.accession if hasattr(alignment, "accession") else \
                                (alignment.title.split('|')[1] if '|' in alignment.title else alignment.title.split()[0])
                    start = hsp.sbjct_start
                    end = hsp.sbjct_end 
                    ncbi_url = f"https://www.ncbi.nlm.nih.gov/nuccore/{accession}?from={start}&to={end}&report=genbank"

                    # Add results
                    results.append({
                        "title": alignment.title,  
                        "clickable_title": f'<a href="{ncbi_url}" target="_blank">{alignment.title}</a>',  # clickable
                        "length": alignment.length,
                        "score": hsp.score,
                        "e_value": hsp.expect,
                        "identities": hsp.identities,
                        "pct_identity": pct_identity,
                        "query_cov": query_cov,
                        "accession": accession,
                        "ncbi_url": ncbi_url
                    })

                    break  # only top HSP per organism

        full_results_url = url_for("static", filename=f"blast_results/{xml_filename}")

    except Exception as e:
        results = [{"error": str(e)}]
        full_results_url = None

    return render_template("blast.html", blast_results=results, full_results_url=full_results_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)

