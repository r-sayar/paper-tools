import requests

def download_pdf_from_doi(doi, output_path):
    # Use Unpaywall API to find open access PDF
    api_url = f"https://api.unpaywall.org/v2/{doi}?email=robin.sayar@fu-berlin.de"
    resp = requests.get(api_url)
    if resp.status_code != 200:
        raise Exception("DOI not found or Unpaywall API error.")
    data = resp.json()
    pdf_url = data.get("best_oa_location", {}).get("url_for_pdf")
    if not pdf_url:
        raise Exception("No open access PDF found for this DOI.")
    pdf_resp = requests.get(pdf_url)
    if pdf_resp.status_code != 200:
        raise Exception("Failed to download PDF.")
    with open(output_path, "wb") as f:
        f.write(pdf_resp.content)
    print(f"Downloaded PDF to {output_path}")

