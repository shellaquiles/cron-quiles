import json
import os
import sys
from pathlib import Path

# Import fix_encoding from the project models to ensure consistency (Rule #1)
try:
    from src.cronquiles.models import fix_encoding
except ImportError:
    # Fallback to a basic version if not in path, or add to path
    import sys
    sys.path.append(os.getcwd())
    from src.cronquiles.models import fix_encoding

def sanitize_value(v):
    if isinstance(v, dict):
        return {fix_encoding(k): sanitize_value(val) for k, val in v.items()}
    elif isinstance(v, list):
        return [sanitize_value(i) for i in v]
    elif isinstance(v, str):
        return fix_encoding(v)
    return v

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 tools/fix_cache_encoding.py <file_path>")
        # Default to geocoding_cache if no arg
        files = ["data/geocoding_cache.json"]
    else:
        files = sys.argv[1:]

    for file_path_str in files:
        path = Path(file_path_str)
        if not path.exists():
            print(f"Error: {path} no encontrado.")
            continue

        print(f"\nProcesando {path}...")
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error al leer JSON: {e}")
                continue

        print("Saneando entradas...")
        fixed_data = sanitize_value(data)

        # En el caso de diccionarios (como el cache), podemos contar diferencias
        if isinstance(data, dict):
            fixed_count = sum(1 for k in data if k != fix_encoding(k))
            print(f"- Llaves corregidas: {fixed_count}")
            print(f"- Total entradas: {len(fixed_data)}")
        elif isinstance(data, list):
            print(f"- Total eventos en lista: {len(fixed_data)}")

        # Guardar (sin backup para simplificar, ya que confiamos en git o el backup previo)
        print(f"Guardando {path}...")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print("\n¡Hecho!")

if __name__ == "__main__":
    main()
