<h1 align="center"> GeNOMic Island: Prokaryotic Genomic Analysis Hub </h1>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fe301491-6d45-4fb9-81af-1d737f47e3b5" alt="Project Banner" width="100%">
</p>

<h2 align="center">🧬 GeNOMic Island Viewer</h2>
<p align="center">
  A Flask-based web app for analyzing and visualizing genomic island predictions.
</p>

GeNOMic Island is a **Flask-based web application** designed for the exploration, visualization, and analysis of **prokaryotic genomic islands (GIs)**. It provides a user-friendly interface for inspecting outputs from the **SeqWord Genomic Island Sniffer (SWGIS)**, including .svg visualizations, .out GI reports, and .fas sequences. The platform supports both **archaeal and bacterial genomes**, allowing researchers to quickly summarize GI counts, explore GI content, and navigate between genome-level data and individual GI annotations.

---

## Features

- View **archaeal and bacterial genomes** with GI summaries.
- Inspect **Number of Genomic Islands (GIs)** per genome.
- Browse **.svg visualizations**, **`.out` reports**, and **`.fas` sequences**.
- Select specific GIs by **ID** or **coordinates**.
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


## **6. Dependencies**
```text
Python: 3.13.3
Flask: 3.1.2

Install all required packages via:
pip install -r requirements.txt
```

