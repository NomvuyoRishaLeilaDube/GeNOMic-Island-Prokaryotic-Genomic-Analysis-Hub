# GeNOMic Island: Prokaryotic Genomic Analysis Hub

GeNOMic Island is a **Flask-based web application** designed for the exploration, visualization, and analysis of **prokaryotic genomic islands (GIs)**. It provides a user-friendly interface for inspecting outputs from the **SeqWord Genomic Island Sniffer (SWGIS)**, including `.svg` visualizations, `.out` GI reports, and `.fas` sequences. The platform supports both **archaeal and bacterial genomes**, allowing researchers to quickly summarize GI counts, explore GI content, and navigate between genome-level data and individual GI annotations.

---

## Features

- View **archaeal and bacterial genomes** with GI summaries.
- Inspect **Number of Genomic Islands (GIs)** per genome.
- Browse **.svg visualizations**, `.out` reports, and `.fas` sequences.
- Select specific GIs by **ID** or **coordinates**.
- Lightweight web interface using **Flask**, **HTML**, and **CSS**.
- Automatic caching to improve performance on repeated accesses.

---

## Project Structure

├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── .gitignore # Files/folders to ignore in Git
├── README.md # This file
├── templates/ # HTML templates
│ ├── home.html
│ ├── index.html
│ ├── genome.html
│ └── viewer.html
├── static/ # Static assets (CSS, images)
│ └── style.css
├── output/ # Genome output files (.svg, .out, .fas)
│ ├── Archaea/
│ └── Bacteria/
└── venv/ # Python virtual environment (ignored in Git)


---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <repo-folder>

#### Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
#### On Windows PowerShell:
#### venv\Scripts\Activate.ps1

##### Install dependencies
pip install -r requirements.txt

###### Organize genome output files
Place your SWGIS output files in the following directories:
Archaea: output/Archaea/
Bacteria: output/Bacteria/
File types supported:
.svg → Visual representations of genomic islands.
.out → GI annotation reports.
.fas → DNA sequences of genomic islands.
Order of files for each genome: .svg, .out, .fas

####### Run the application
python app.py
Open your browser and navigate to: http://127.0.0.1:5002


######## USING THE WEB APP:
1) Home Page: Displays the total number of genomes and GIs per domain (Archaea/Bacteria).

2) Genome Table: Lists all genomes for the selected domain with:
Sequence ID
Organism name
Number of genomic islands (GIs)

3) Genome Page: Click a Sequence ID to:
Browse .svg visualizations
View GI reports (.out)
Inspect GI sequences (.fas)
Filter GIs by ID or coordinate

4) File Viewer: Renders .svg visualizations in a resizable container for clarity.


######### Dependencies
Python 3.8+
Flask >= 2.3
Install all required packages via: pip install -r requirements.txt

