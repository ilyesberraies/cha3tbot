import os
import json
from kiutils.symbol import SymbolLib
from kiutils.footprint import Footprint

def extract_symbol_data(symbol_file_path):
    try:
        lib = SymbolLib().from_file(symbol_file_path)
        extracted_data = []

        for symbol in lib.symbols:
            symbol_info = {
                "library_name": os.path.basename(symbol_file_path).replace(".kicad_sym", ""),
                "symbol_name": symbol.libId,
                "description": symbol.description if hasattr(symbol, 'description') else '',
                "properties": {prop.key: prop.value for prop in symbol.properties},
                "pins": []
            }

            for pin in symbol.pins:
                symbol_info["pins"].append({
                    "number": pin.number,
                    "name": pin.name,
                    "type": pin.electricalType,
                    "electrical_type": pin.electricalType
                })

            extracted_data.append(symbol_info)

        return extracted_data

    except Exception as e:
        print(f"Erreur lors de l'extraction des données du symbole {symbol_file_path}: {e}")
        return None

def extract_footprint_data(footprint_file_path):
    try:
        footprint = Footprint().from_file(footprint_file_path)
        footprint_info = {
            "library_name": os.path.basename(os.path.dirname(footprint_file_path)),
            "footprint_name": footprint.libId,
            "pads": []
        }

        for pad in footprint.pads:
            footprint_info["pads"].append({
                "number": pad.number,
                "type": pad.type,
                "shape": pad.shape
            })

        return [footprint_info]

    except Exception as e:
        print(f"Erreur lors de l'extraction des données de l'empreinte {footprint_file_path}: {e}")
        return None

def main():
    kicad_symbols_path = "c:\Program Files\KiCad\9.0\share\kicad\symbols"
    kicad_footprints_path = "C:\Program Files\KiCad\9.0\share\kicad\footprints"

    all_extracted_symbols = []
    all_extracted_footprints = []

    if os.path.exists(kicad_symbols_path):
        print(f"\nExtraction des symboles de {kicad_symbols_path}:")
        for root, _, files in os.walk(kicad_symbols_path):
            for file in files:
                if file.endswith(".kicad_sym"):
                    symbol_file_path = os.path.join(root, file)
                    data = extract_symbol_data(symbol_file_path)
                    if data:
                        all_extracted_symbols.extend(data)
    else:
        print(f"Le chemin des symboles KiCad {kicad_symbols_path} n'existe pas.")

    if os.path.exists(kicad_footprints_path):
        print(f"\nExtraction des empreintes de {kicad_footprints_path}:")
        for root, _, files in os.walk(kicad_footprints_path):
            for file in files:
                if file.endswith(".kicad_mod"):
                    footprint_file_path = os.path.join(root, file)
                    data = extract_footprint_data(footprint_file_path)
                    if data:
                        all_extracted_footprints.extend(data)
    else:
        print(f"Le chemin des empreintes KiCad {kicad_footprints_path} n'existe pas.")

    with open("kicad_symbols_data.json", "w", encoding="utf-8") as f:
        json.dump(all_extracted_symbols, f, indent=2, ensure_ascii=False)
        print(f"Données des symboles sauvegardées dans kicad_symbols_data.json ({len(all_extracted_symbols)} symboles).")

    with open("kicad_footprints_data.json", "w", encoding="utf-8") as f:
        json.dump(all_extracted_footprints, f, indent=2, ensure_ascii=False)
        print(f"Données des empreintes sauvegardées dans kicad_footprints_data.json ({len(all_extracted_footprints)} empreintes).")

if __name__ == "__main__":
    main()
