import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# Estensioni immagine supportate da input comuni
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.heic', '.webp'}
OUTPUT_EXTENSION = '.webp'

def convert_images(source_dir, output_dir=None, quality=80):
    """
    Converte tutte le immagini in una directory in formato WebP.
    
    Args:
        source_dir: Percorso della cartella di partenza.
        output_dir: Percorso di salvataggio (se None, sovrascrive nella stessa posizione con estensione .webp).
        quality: Qualità del WebP (0-100). Default 80.
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Errore: La directory '{source_dir}' non esiste.")
        return

    # Se output_dir non è specificato, usiamo la stessa directory
    if output_dir is None:
        output_path = source_path
    else:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    print(f"Ricerca immagini in: {source_path}")
    print(f"Salvataggio in: {output_path}")
    print(f"Qualità impostata a: {quality}%\n")

    found_count = 0
    converted_count = 0
    
    # Cerca ricorsivamente tutti i file
    files = list(source_path.rglob('*'))
    
    with tqdm(files, desc="Scansione...") as pbar:
        for file in pbar:
            if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                found_count += 1
                pbar.set_description(f"Elaborando: {file.name}")
                
                try:
                    # Calcola il percorso di output
                    relative_path = file.relative_to(source_path)
                    output_file = output_path / relative_path.with_suffix(OUTPUT_EXTENSION)
                    
                    # Crea le sottocartelle se non esistono nel target
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Evita loop infiniti se l'output è lo stesso folder e già webp
                    if str(file.resolve()) == str(output_file.resolve()):
                        continue

                    # Apri e converte l'immagine
                    with Image.open(file) as img:
                        # Gestione della trasparenza (Alpha channel)
                        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                            img = img.convert("RGBA")
                        else:
                            img = img.convert("RGB")
                        
                        # Salva come WebP
                        img.save(output_file, 'WEBP', quality=quality, method=6)
                        
                    converted_count += 1
                    pbar.write(f"✓ Convertito: {file.name} -> {output_file.name}")

                except Exception as e:
                    pbar.write(f"✗ Errore su {file.name}: {str(e)}")

    print(f"\nOperazione completata!")
    print(f"Trovate: {found_count} immagini")
    print(f"Convertite con successo: {converted_count}")

if __name__ == "__main__":
    # Esempio di utilizzo
    # Sostituisci './immagini' con la tua cartella
    src = input("Inserisci il percorso della cartella da analizzare (o premi Invio per '.'): ").strip() or "."
    
    # Opzionale: inserisci una cartella di destinazione diversa
    dst_input = input("Cartella di destinazione (lascia vuota per sovrascrivere/uso stesso folder): ").strip()
    dst = dst_input if dst_input else None
    
    q_input = input("Qualità WebP (0-100, default 80): ").strip()
    quality = int(q_input) if q_input.isdigit() else 80
    
    convert_images(src, dst, quality)