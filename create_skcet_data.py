import os

# 1️⃣ Create the data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# 2️⃣ Dictionary of filenames and their content
files_content = {
    "institution.txt": """Institution Name: Sri Krishna College of Engineering and Technology (SKCET)
Location: Coimbatore, Tamil Nadu, India
Established: 1998
Autonomous Status: Yes
Affiliation: Anna University, Chennai
Accreditations: NAAC 'A+', NBA
Programs Offered: Undergraduate (UG), Postgraduate (PG), Research""",

    "programs.txt": """UG Programs: B.Tech in CSE, IT, ECE, EEE, Mechanical, Civil
PG Programs: M.Tech in CSE, IT, ECE, Mechanical
Research Programs: PhD in Engineering and Technology""",

    "dept_ai_ds.txt": """Department: AI & Data Science
Programs Offered: B.Tech AI & DS
Faculty: List of faculty members
Labs: AI Lab, ML Lab""",

    "dept_cse.txt": """Department: Computer Science and Engineering
Programs Offered: B.Tech CSE, M.Tech CSE
Faculty: List of faculty members
Labs: Software Lab, DB Lab""",

    "dept_ece.txt": """Department: Electronics and Communication Engineering
Programs Offered: B.Tech ECE, M.Tech ECE
Faculty: List of faculty members
Labs: VLSI Lab, Embedded Systems Lab""",

    "placements.txt": """Placement Statistics:
Top Recruiters: Infosys, TCS, Cognizant, Wipro
Placement Percentage: 85%
Highest Package: 12 LPA""",

    "news_events.txt": """Recent News:
- SKCET organized TechFest 2025
- Alumni Meet 2024
Upcoming Events:
- AI Workshop
- Hackathon""",

    # Add more files as needed
}

# 3️⃣ Write the files
for filename, content in files_content.items():
    filepath = os.path.join("data", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ All files created inside 'data/' folder.")
