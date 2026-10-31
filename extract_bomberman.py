import os
from PIL import Image

def analyze_and_extract_heroes():
    src = "C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/sprites/super_bomberman_1_characters.png"
    out_dir = "C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/apps/web/public/assets/sprites/bomberman"
    os.makedirs(out_dir, exist_ok=True)
    
    img = Image.open(src).convert("RGBA")
    
    # Cuadrantes en super_bomberman_1_characters:
    # Arriba-Izq: White Bomberman (Atlas - Coordinador)
    # Arriba-Der: Black Bomberman (Centinela - Hard Deny)
    # Abajo-Izq: Blue Bomberman (Vega - Contratos/Datos)
    # Abajo-Der: Red/Green Bomberman (Nova - QA/Inspectora)
    
    quadrants = {
        "atlas_white": (0, 250, 236, 560),
        "centinela_black": (236, 250, 473, 560),
        "vega_blue": (0, 560, 236, 870),
        "nova_red": (236, 560, 473, 870),
    }
    
    # Extraer representaciones limpias de cada personaje
    for name, box in quadrants.items():
        q_img = img.crop(box)
        q_img.save(os.path.join(out_dir, f"{name}_quadrant.png"))
        
        # En cada cuadrante, la primera fila de 'Walk' contiene los sprites frontales y de perfil
        # Vamos a recortar los primeros 3 sprites frontales de 24x32 aproximados
        # Medidas estimadas dentro de cada cuadrante:
        # Walk comienza en y ~ 35 relativo al cuadrante
        walk_front = q_img.crop((10, 35, 45, 75))
        walk_front.save(os.path.join(out_dir, f"{name}_idle.png"))
        
        cheering = q_img.crop((10, 180, 45, 220))
        cheering.save(os.path.join(out_dir, f"{name}_cheering.png"))
        
    print("[OK] Avatares y cuadrantes de personajes extraídos exitosamente.")

def slice_all_characters():
    src = "C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/sprites/super_bomberman_1_characters.png"
    out_dir = "C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/apps/web/public/assets/sprites/bomberman/slices"
    os.makedirs(out_dir, exist_ok=True)
    
    img = Image.open(src).convert("RGBA")
    
    # Zona de juego principal donde están los personajes: y=250 a y=870
    characters_area = img.crop((0, 250, 473, 870))
    w, h = characters_area.size
    
    # Rebanar en tiles de 24x32
    tw, th = 24, 32
    count = 0
    for y in range(0, h, th):
        for x in range(0, w, tw):
            tile = characters_area.crop((x, y, min(x+tw, w), min(y+th, h)))
            # Filtrar si casi todo es fondo verde sólido (#3f7f50 aprox)
            colors = tile.getcolors(maxcolors=1000)
            if colors:
                # Si un solo color domina más del 92% del tile, omitir
                most_freq = max(colors, key=lambda c: c[0])
                if most_freq[0] > (tile.size[0] * tile.size[1] * 0.92):
                    continue
            tile.save(os.path.join(out_dir, f"char_tile_{count:03d}.png"))
            count += 1
            
    print(f"[OK] {count} tiles individuales de personajes guardados en {out_dir}")

if __name__ == "__main__":
    analyze_and_extract_heroes()
    slice_all_characters()
