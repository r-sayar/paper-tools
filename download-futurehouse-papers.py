import download_papers

downloaded_papers = set()

with open("markdowncopypasta") as f:
    lines = f.readlines()

references_index = None
for i, line in enumerate(lines):
    if "references" in line.lower():
        references_index = i
        break

if references_index is not None:
    print(f"References start at line {references_index + 1}")
    i = references_index + 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if "(" in line:
            # Extract paper name
            paper_name = line.split("(")[1].split(" ")[0]
            if paper_name in downloaded_papers:
                i += 2  # skip next line as per instructions
                continue
            downloaded_papers.add(paper_name)
            # Skip next line
            i += 2
            if i < len(lines):
                doi_line = lines[i].strip()
                if "doi:" in doi_line and ". " in doi_line:
                    doi = doi_line.split("doi:")[1].split(". ")[0].strip()
                    download_papers.download_pdf_from_doi(doi, f"results/markdowncopypasta/{paper_name}.pdf")
        else:
            i += 1