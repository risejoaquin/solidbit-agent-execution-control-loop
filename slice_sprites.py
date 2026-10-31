import os
import glob
from PIL import Image

def slice_spritesheet(image_path, output_dir, tile_width=24, tile_height=24, prefix="agent_skin", skip_empty=True):
    os.makedirs(output_dir, exist_ok=True)
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        img_width, img_height = img.size
        
        index = 0
        saved_count = 0
        for y in range(0, img_height, tile_height):
            for x in range(0, img_width, tile_width):
                # Evitar desbordamientos si el último tile es menor
                box = (x, y, min(x + tile_width, img_width), min(y + tile_height, img_height))
                tile = img.crop(box)
                
                # Descartar tiles completamente transparentes si skip_empty es True
                if skip_empty:
                    extrema = tile.getextrema()
                    # extrema[3] corresponde al canal alpha (min_alpha, max_alpha)
                    if len(extrema) >= 4 and extrema[3][1] == 0:
                        index += 1
                        continue
                
                output_filename = f"{prefix}_{saved_count:03d}.png"
                tile.save(os.path.join(output_dir, output_filename))
                saved_count += 1
                index += 1
                
        print(f"[OK] {saved_count} sprites extraídos exitosamente desde {image_path} hacia {output_dir}")
        return saved_count
    except Exception as e:
        print(f"[ERROR] Falló el procesamiento de {image_path}: {e}")
        return 0

def process_all_sprites(input_folder, output_folder, tile_width=24, tile_height=24):
    valid_exts = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    found_files = []
    for ext in valid_exts:
        found_files.extend(glob.glob(os.path.join(input_folder, ext)))
        found_files.extend(glob.glob(os.path.join(input_folder, ext.upper())))

    if not found_files:
        print(f"[INFO] No se encontraron archivos de sprites en {input_folder}")
        return 0

    total_extracted = 0
    for file_path in found_files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        sub_output = os.path.join(output_folder, base_name)
        extracted = slice_spritesheet(file_path, sub_output, tile_width, tile_height, prefix=base_name)
        total_extracted += extracted

    return total_extracted

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rebanador determinístico de Sprite Sheets para EOP")
    parser.add_argument("--input_sheet", default="./docs/sprites/bomberman_sheet.png", help="Ruta de la hoja de sprites")
    parser.add_argument("--input_dir", default="./docs/sprites", help="Directorio con hojas de sprites")
    parser.add_argument("--output_dir", default="./apps/web/public/assets/sprites/bomberman", help="Directorio destino")
    parser.add_argument("--width", type=int, default=24, help="Ancho de cada tile en px")
    parser.add_argument("--height", type=int, default=24, help="Alto de cada tile en px")
    args = parser.parse_args()

    if os.path.isfile(args.input_sheet):
        slice_spritesheet(args.input_sheet, args.output_dir, args.width, args.height)
    else:
        # Si no existe el archivo puntual, procesar todos los presentes en input_dir
        count = process_all_sprites(args.input_dir, "./apps/web/public/assets/sprites", args.width, args.height)
        if count == 0:
            print(f"[PENDING] Esperando que se deposite la imagen en {args.input_sheet} o en {args.input_dir}/")
