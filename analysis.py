from flask import Flask, request, jsonify
import os
import time
import google.generativeai as genai

app = Flask(__name__)

# Configure the Gemini model
genai.configure(api_key="AIzaSyAUBC5uZvEEv2O1e6tB_06P3tPZk5R2oK4")

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

files = [
    upload_to_gemini("SCOGS.csv", mime_type="text/csv"),
    upload_to_gemini("coloraddatives.csv", mime_type="text/csv"),
    upload_to_gemini("Nurti data.csv", mime_type="text/csv"),
]

wait_for_files_active(files)

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "You are SafeIngredientChecker, an expert in analyzing food ingredients for long-term health risks and checking their regulatory status. You are capable of reading and interpreting ingredient lists provided in any format, whether it’s JSON, plain text, or a different structure.\nYou are a critic of ingredients.\n\nYour key tasks include:\n\nChronic Disease Risk Analysis: Assess each ingredient to identify potential risks for causing chronic diseases in the long term (e.g., cancer, heart disease, diabetes). Focus on common harmful additives, preservatives, and chemicals.\n\nRegulatory Compliance Check: Cross-check every ingredient against the banned or restricted lists from the Food Safety and Standards Authority of India (FSSAI), the European Food Safety Authority (EFSA), and the Food and Drug Administration (FDA).\n\nSimplified Reporting: \nProvide a clear summary that identifies any harmful or banned ingredients. If any risky ingredients are found, provide details on the potential health risks.\nIf an ingredient is considered safe and is approved by regulatory bodies, do not raise unnecessary alerts.\n\nInput Flexibility: The input format for ingredient data can be JSON, plain text, or any other structured format. You should be able to handle the input efficiently regardless of its format.\n\nFeel free to provide the ingredient list in any format, and I’ll conduct a thorough analysis to ensure safe consumption and regulatory compliance. Let’s get started!\n\n",
                files[0],
                "Learn from the Data I am feeding you\nDefinitions of labels\nGRAS Substances: A food substance that is not subject to premarket review and approval by FDA because it is generally recognized, by qualified experts, to be safe under the intended conditions of use.\nSCOGS Report Number: Number of the report that contains details of the safety studies that formed the basis of the opinion made by the committee.\nCAS Reg. No. or other ID Code: Chemical Abstract Services (CAS) Registry Number for the substance or a numerical code assigned by CFSAN to those substances that do not have a CAS Registry Number (977nnn-nn-n series).\nYear of Report: The year that the SCOGS report was issued.\nSCOGS Type of Conclusion: Opinion and Conclusion by the Select Committee on GRAS Substance Review about the safety of a GRAS substance. See SCOGS Conclusions.\n21 CFR Regulation: Citation in Title 21 of the U.S. Code of Federal Regulations if the substance is subject to a regulation.\n*NTIS Accession Number: Order number of the full report containing details of the safety studies that formed the basis of the opinions and conclusions that is available from the National Technical Information Service (NTIS); search the accession number in the NTRL (National Technical Reports Library).\n\n**SCOGS Type of Conclusion\tDefinition\n1\tThere is no evidence in the available information on [substance] that demonstrates, or suggests reasonable grounds to suspect, a hazard to the public when they are used at levels that are now current or might reasonably be expected in the future.\n2\tThere is no evidence in the available information on [substance] that demonstrates a hazard to the public when it is used at levels that are now current and in the manner now practiced. However, it is not possible to determine, without additional data, whether a significant increase in consumption would constitute a dietary hazard.\n3\tWhile no evidence in the available information on [substance] demonstrates a hazard to the public when it is used at levels that are now current and in the manner now practiced, uncertainties exist requiring that additional studies be conducted.\n4\tThe evidence on [substance] is insufficient to determine that the adverse effects reported are not deleterious to the public health should it be used at former levels and in the manner formerly practiced.\n5\tIn view of the almost complete lack of biological studies, the Select Committee has insufficient data upon which to evaluate the safety of [substance] as a [intended use].\n",
                files[1],
                "Definitions of Terms Used\nFID\nFood Inspection Decision (issued by USDA prior to 1927)\nCAS Reg. No. or other ID\nChemical Abstract Service (CAS) Registry® Number for the substance or a numerical code assigned by CFSAN (977nnn-nn-n-series) to those substances that do not have a CAS Reg. No.\nOther names\nRecognized synonyms for color additives\nLakes\nInsoluble pigments formed by chemically reacting water-soluble straight colors with precipitants and substrata.\n \n\nEnd Notes\nThe color additives Antarctic krill meal, Astaxanthin, Astaxanthin dimethyldisuccinate, Ultramarine blue, Canthaxanthin, Haematococcus algae meal, Synthetic iron oxide, Dried algae meal, Tagetes (Aztec marigold) meal and extract, Corn endosperm oil, Paracoccus pigment, and Phaffia yeast are approved for specific uses in animal food (see 21 CFR 73.32. 73.35, 73.37, 73.50, 73.75, 73.185, 73.200, 73.275, 73.295, 73.315, 73.352, and 73.355, respectively).\nThe year approved is based on the date listed in the \"Confirmation of Effective Date\" notice for the action as published in the Federal Register.\nPetitioned for use after the 1960 amendments; never provisionally listed.\nColor additives listed in 21 CFR Parts 74 and 82 must be analyzed and batch certified by FDA before they can be used in any FDA-regulated product marketed in the U.S. This requirement applies to products imported into this country as well as those manufactured domestically. Manufacturers of certified color additives must include on the label the name of the certified color additive, a statement indicating general use limitations, any quantitative limitations in products, and the certification lot number assigned to the batch. Straight colors required to be certified are listed in 21 CFR Part 74. Most lakes are provisionally listed under 21 CFR 81.1 for use as listed in 21 CFR 82.51 (food, drugs, and cosmetics), 21 CFR 82.1051 (drugs and cosmetics), or 21 CFR 82.2051 (externally applied drugs and cosmetics). All FD&C Red No. 40 lakes are permanently listed under 21 CFR 74.340 (food), 74.1340 (drugs), and 74.2340 (cosmetics). FD&C Blue No. 1 and FD&C Yellow No. 5 aluminum lakes for drug and cosmetic use are permanently listed in 21 CFR sections 74.1101, 74.1705, 74.2101, and 74.2705.\nColor additives that are permitted for general use may not be used in the area of the eye, in injections, or in surgical sutures unless such use is specified in the color additive listing regulation. Currently no color additives are listed for use in injected products (such as tattoos or permanent makeup).\nColor additives that are permitted for external application may not be used in the area of the eye, in injections, or in surgical sutures unless such use is specified in the color additive listing regulation. Currently no color additives are listed for use in injected products (such as tattoos or permanent makeup). Some color additives that are permitted for external application also may be permitted in mouthwashes, dentifrices, or lipsticks in limited amounts specified in the color additive listing regulations.\nNTE - not to exceed.\nThe listed color additives are the reaction products produced by copolymerizing the reactive dyes with various monomers such that the dyes are chemically bound in the resulting polymer matrix.",
                files[2],
                "This is a list of food additives and their regulatory status you need to learn about\nABBREVIATIONS USED\nTechnical Effects\nType\tKind, effect or use of additive\nAC\tAnticaking agent\nAF\tAntifoaming (or defoaming) agent\nAOX\tAntioxidant\nBC\tBoiler compound\nBL\tBleaching agent or flour-maturing agent\nB&N\tBuffer and neutralizing agent\nCTG\tComponent or coating for fruits & vegetables\nDS\tDietary supplement\nEMUL\tEmulsifier\nENZ\tEnzyme\nESO\tEssential oil and/or oleoresin (solvent free)\nFEED\tSubstances under the Food Additives Amendment added directly to feed\nFLAV\tNatural flavoring agent\nFL/ADJ\tSubstance used in conjunction with flavors\nFUM\tFumigant\nFUNG\tFungicide\nHERB\tHerbicide\nHOR\tHormone\nINH\tInhibitor\nMISC\tMiscellaneous\nNAT\tNatural substances and extractives\nNNS\tNon-nutritive sweetener\nNUTR\tNutrient\nNUTRS\tNutritive Sweetener\nPEST\tPesticide other than fumigant\nPRES\tChemical preservative\nSANI\tSanitizing agent for food processing equipment\nSDA\tSolubilizing and dispersing agent\nSEQ\tSequestrant\nSOLV\tSolvent\nSP\tSpices, other natural seasonings & flavorings\nSP/ADJ\tSpray adjuvant\nSTAB\tStabilizer\nSY/FL\tSynthetic flavor\nVET\tVeterinary drug, which may leave residue in edible tissues of animals or in edible animal products\nRegulatory Status\nType\tKind, effect or use of additive\nBAN\tSubstances banned prior to the Food Additives Amendment (FAA) because of toxicity. These substances are bolded and italicized.\nFS\tSubstances permitted as optional ingredient in a standardized food.\nGRAS\tGenerally recognized as safe. Substances in this category are by definition, under Sec. 201(s) of the FD&C Act, not food additives. Most GRAS substances have no quantitative restrictions as to use, although their use must conform to good manufacturing practices. Some GRAS substances, such as sodium benzoate, do have a quantitative limit for use in foods.\nGRAS/FS\tSubstances generally recognized as safe in foods but limited in standardized foods where the standard provides for its use.\nILL\tSubstances used or proposed for use as direct additives in foods without required clearance under the FAA. Their use is illegal. These substances are bolded and italicized.\nPD\tSubstances for which a petition has been filed but denied because of lack of proof of safety. Substances in this category are illegal and may not be used in foods.\nPS\tSubstances for which prior sanction has been granted by FDA for specific uses. There are a number of substances in this category not listed herein because they have not been published in the FEDERAL REGISTER.\nREG\tFood additives for which a petition has been filed and a regulation issued.\nREG/FS\tFood additives regulated under the FAA and included in a specific food standard.",
                "Now you are ready with all the information. In my next messages I will share with you an object that has ingredients of a product. You are expected to analyze each ingredient and return a json object that has keys- allergens(value includes list of all the allergens), pet_safe(string about if the product whose ingredients you just analyzed is safe to eat for pets like dogs and cats and how is it harmful ), regulations(if regulatory compliance of any of the ingredients is concerning mention about that) and keys related to your key tasks",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Okay, I am ready to analyze ingredient lists and provide you with a critical assessment.  \n\nPlease share the ingredient list in any format (JSON, plain text, or a different structured format) and I will do my best to:\n\n1. **Identify potential chronic disease risks:** I will scrutinize each ingredient for potential long-term health risks, including those associated with common harmful additives, preservatives, and chemicals.\n2. **Check regulatory compliance:** I will compare each ingredient against banned or restricted lists from FSSAI, EFSA, and the FDA. \n3. **Summarize my findings:** I will present my analysis in a clear and concise JSON object, highlighting any harmful or banned ingredients and detailing potential health risks.  \n\nLet's get started! \n",
            ],
        },
    ]
)
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the JSON data from the request
    data = request.json

    # Validate the data
    if not data or "Ingredients" not in data:
        return jsonify({"error": "Invalid input"}), 400

    # Convert the JSON data to a string
    input_text = str(data)

    # Send the input to the Gemini model
    response = chat_session.send_message(input_text)

    # Extract the response content
    response_content = response.text
    
    # Return the response from the Gemini model
    return jsonify(response_content)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=3001)
