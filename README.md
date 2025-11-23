<h1 align="center"> GeNOMic Island: Prokaryotic Genome Analysis Hub </h1>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fe301491-6d45-4fb9-81af-1d737f47e3b5" alt="Project Banner" width="100%">
</p>

<h2 align="center">🧬 GeNOMic Island Viewer</h2>
<p align="center">
Explore genomic islands → visualize, analyze, and BLAST with Flask! 
</p>

GeNOMic Island is a **Flask-based web application** designed for the exploration, visualization, and analysis of **prokaryotic genomic islands (GIs)**. It provides a user-friendly interface for inspecting outputs from the **SeqWord Genomic Island Sniffer (SWGIS)**, including .svg visualizations, .out GI reports, and .fas sequences. The platform supports both **archaeal and bacterial genomes**, allowing researchers to quickly summarize GI counts, explore GI content, and navigate between genome-level data and individual GI annotations, and **perform BLAST searches on selected GI sequences directly from the web interface**.

---

## Features

- View **archaeal and bacterial genomes** with GI summaries.
- Inspect **Number of Genomic Islands (GIs)** per genome.
- Browse **`.svg` visualizations**, **`.out` reports**, and **`.fas` sequences**.
- Select specific GIs by **ID** or **coordinates**.
- Run **BLAST searches** on selected genomic island sequences directly from the web interface.
- Lightweight web interface using **Flask**, **HTML**, and **CSS**.
- Automatic caching to improve performance on repeated accesses.

---

## Project Structure

```
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/              # HTML templates
│ ├── home.html             # Home page
│ ├── index.html            # Genomic Table
│ ├── genome.html           # Genomic data
│ └── viewer.html           # Genomic Interface
│ └── blast.html            # Blast Results
├── static/                 # Static assets (CSS)
│ └── style.css
├── output/                 # Genome output files (.svg, .out, .fas)
│ ├── Archaea/
│ └── Bacteria/
```


## Setup Instructions

## **1. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate # Linux/Mac
```

## **2. Install dependencies**
```bash
pip install -r requirements.txt
```

## **3. Organize genome output files**

Place your SWGIS output files in the following directories:  
**Archaea**: output/Archaea/  
**Bacteria**: output/Bacteria/  

File types supported:  
**.svg** → Visual representations of genomic islands  
**.out** → GI annotation reports  
**.fas** → DNA sequences of genomic islands  

Order of files for each genome: **.svg, .out, .fas**


## **4. Run the application**
```bash
python app.py
```
Open your browser and navigate to:
http://127.0.0.1:5002


## **5. Using the Web App**
 
- **Home Page**: Displays the total number of genomes and GIs per domain (Archaea/Bacteria).  
- **Genome Table**: Lists all genomes for the selected domain with Sequence ID, Organism name, and number of GIs.  
- **Genome Page**: Click a Sequence ID to browse .svg visualizations, view .out reports, and inspect .fas sequences.  
- **File Viewer**: Renders .svg visualizations, displays .out reports and .fas sequences, and allows filtering of genomic islands by ID or coordinate.
- **BLAST Functionality**: Select a GI sequence block from a .fas file and click "BLAST Selected GI" to run an NCBI BLAST search against the nucleotide (nt) database. The results shown in a table, as well as XML format (which can be accessed for detailed BLAST outputs).


## **6. Dependencies**
```text
Python: 3.13.3
Flask: 3.1.2
Biopython 1.8.5

Install all required packages via:
pip install -r requirements.txt
```

## **7. "Mock Test" Example**

- **STEP 1:** Download "BIF703.zip" folder 
- **STEP 2:** Uncompress folder "BIF703.zip"
- **STEP 3:** Open "Sniffer" folder in the terminal 
- **STEP 4:** Create a virtual environment → python3 -m venv venv
- **STEP 5:** Activate the virtual environment → source venv/bin/activate  
- **STEP 6:** Install dependencies → pip install flask biopython
- **STEP 7:** Run GeNOMic Island → python app.py

