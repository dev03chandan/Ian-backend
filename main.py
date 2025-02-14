import os
import io
import zipfile
import requests
import xml.etree.ElementTree as ET

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from pdf2image import convert_from_bytes
import pytesseract
from openai import OpenAI

# Initialize OpenAI API client.
app = FastAPI()

# Global variable to store regulatory data.
regulatory_data = {}


def extract_text_from_dita(file_path: str) -> str:
    """
    Parse a DITA XML file and return its complete text content.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Join all text (including tail) with a single space.
        full_text = " ".join(text.strip() for text in root.itertext() if text.strip())
        return full_text
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"


def load_far_regulatory_data() -> dict:
    """
    Downloads FAR regulatory DITA ZIP files, extracts designated files,
    and returns a mapping of file names to their extracted text content.
    """
    base_url = (
        "https://www.acquisition.gov/sites/default/files/current/far/compiled_dita/"
    )
    dita_files = [
        # Pricing & Payment Terms
        "part_52/52.232-25.dita",
        # Subcontracting Restrictions
        "part_52/52.244-2.dita",
        # Penalties for Non-Performance
        "part_52/52.249-8.dita",
        "part_52/52.249-9.dita",
        "part_52/52.249-10.dita",
        # Vendor Eligibility & Registration
        "part_9/9.103.dita",
        "part_52/52.209-5.dita",
        # Conflict of Interest & Undisclosed Relationships
        "part_3/3.101-1.dita",
        "part_9/9.505.dita",
    ]

    # Determine unique parts to download the respective ZIP files.
    parts = set(f.split("/")[0] for f in dita_files)
    zip_files = {}
    for part in parts:
        zip_url = f"{base_url}{part}.zip"
        response = requests.get(zip_url)
        if response.status_code == 200:
            zip_files[part] = zipfile.ZipFile(io.BytesIO(response.content))
            print(f"Downloaded {part}.zip successfully.")
        else:
            print(f"Error downloading {part}.zip: Status code {response.status_code}")

    # Create an output folder for extraction.
    output_folder = "extracted_dita"
    os.makedirs(output_folder, exist_ok=True)

    extracted_texts = {}
    for file_name in dita_files:
        part = file_name.split("/")[0]
        if part in zip_files:
            zip_ref = zip_files[part]
            if file_name in zip_ref.namelist():
                # Extract file to output folder.
                zip_ref.extract(file_name, output_folder)
                dita_file_path = os.path.join(output_folder, file_name)
                extracted_texts[file_name] = extract_text_from_dita(dita_file_path)
            else:
                extracted_texts[file_name] = "Error: File not found in ZIP."
        else:
            extracted_texts[file_name] = "Error: No ZIP available for this part."
    return extracted_texts


def analyze_contract(contract_text: str, regulatory_data: dict) -> str:
    """
    Constructs a prompt that includes the FAR regulatory details and the contract text.
    Sends the prompt to OpenAI and returns the analysis result.
    """
    # Combine regulatory texts into a single block.
    regulatory_info = "\n\n".join(
        [f"{key}:\n{value}" for key, value in regulatory_data.items()]
    )

    # System message with detailed instructions.
    system_message = (
        "You are a contract compliance analyst specialized in evaluating contracts against Federal Acquisition Regulations (FAR). "
        "Your responsibilities include:\n"
        "1. Breaking down the contract into key sections.\n"
        "2. Extracting key clauses and comparing them to the regulatory reference data.\n"
        "3. Focusing on these five compliance areas:\n"
        "   - Pricing & Payment Terms (FAR 52.232-25)\n"
        "   - Subcontracting Restrictions (FAR 52.244-2)\n"
        "   - Penalties for Non-Performance\n"
        "   - Vendor Eligibility & Registration (verify against SAM.gov requirements)\n"
        "   - Conflict of Interest & Undisclosed Relationships\n"
        "4. Flagging any missing or incomplete clauses.\n"
        "5. Assigning a risk level for each area: Low (fully compliant), Medium (minor issues), or High (major non-compliance).\n"
        "6. Calculating an overall compliance risk score (0-100%) and providing a concise summary of issues.\n"
        "Ensure that your analysis is clear, structured, and concise."
    )

    # User message including the FAR reference and the contract text.
    user_message = (
        f"Below is the regulatory reference information:\n\n{regulatory_info}\n\n"
        f'Below is the contract text to be analyzed:\n"""\n{contract_text}\n"""'
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # You can change this model as needed.
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        analysis_result = response.choices[0].message.content
    except Exception as e:
        analysis_result = f"Error in OpenAI API call: {e}"
    return analysis_result


@app.on_event("startup")
def startup_event():
    """
    On startup, load the FAR regulatory data and set the OpenAI API key.
    """
    global regulatory_data
    global client
    regulatory_data = load_far_regulatory_data()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Set your OpenAI API key (make sure to have it in your environment variables)
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set in environment variables.")


@app.post("/analyze_contract/")
async def analyze_contract_endpoint(file: UploadFile = File(...)):
    """
    Endpoint that accepts a PDF file, performs OCR to extract its text, and returns
    the analysis comparing the contract text to the FAR regulatory details.
    """
    # Read the uploaded file.
    file_bytes = await file.read()

    # Convert PDF bytes to images. Requires poppler (used by pdf2image).
    try:
        images = convert_from_bytes(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting PDF: {e}")

    # Perform OCR on each image to extract text.
    contract_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        contract_text += text + "\n"

    print(f"Contract text:\n{contract_text}")

    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    # Call OpenAI API to analyze the contract against the FAR regulatory data.
    analysis_result = analyze_contract(contract_text, regulatory_data)

    return {"analysis": analysis_result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
