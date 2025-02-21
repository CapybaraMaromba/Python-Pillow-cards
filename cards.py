from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

class UnoCardDesign:
    CARD_SIZE = (630, 880)
    CORNER_RADIUS = 45
    SHADOW_BLUR = 45
    SHADOW_OFFSET = (35, 35)
    GRADIENT_LAYERS = 100  # Aumentado para gradiente mais suave
    
    COLORS = {
        "red": {"main": (230, 50, 50), "secondary": (180, 30, 30)},
        "blue": {"main": (50, 120, 230), "secondary": (30, 90, 200)},
        "green": {"main": (50, 180, 90), "secondary": (30, 140, 70)},
        "yellow": {"main": (250, 210, 50), "secondary": (230, 180, 30)},
        "wild": {"rainbow": [
            (255, 0, 0), (255, 69, 0), (255, 165, 0),
            (255, 255, 0), (0, 128, 0), (0, 0, 255),
            (75, 0, 130), (238, 130, 238)
        ]}
    }
    
    SYMBOLS = {
        "Skip": "🚫",  # Símbolo Unicode alternativo
        "Reverse": "🔄",
        "Draw +2": "+2",
        "Wild": "💠",  # Símbolo mais visível
        "Wild +4": "+4"
    }
    
    FONT_PATHS = {
        "main": "ArialBold.ttf",
        "symbols": "seguiemj.ttf",
        "fallback": "arial.ttf"
    }

def create_radial_rainbow(size):
    """Cria gradiente radial de arco-íris com preenchimento completo"""
    img = Image.new('RGB', size)
    center_x, center_y = size[0]//2, size[1]//2
    max_radius = math.hypot(center_x, center_y)
    
    for y in range(size[1]):
        for x in range(size[0]):
            dx = x - center_x
            dy = y - center_y
            angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            radius = math.hypot(dx, dy) / max_radius
            
            # Mapeia para o espectro do arco-íris
            hue = angle
            color = UnoCardDesign.COLORS["wild"]["rainbow"][int(hue * (len(UnoCardDesign.COLORS["wild"]["rainbow"])-1))]
            
            # Aplica transparência radial
            alpha = int(255 * (1 - radius))
            img.putpixel((x, y), color)
    return img

def load_font(font_type, size):
    """Carrega fontes com fallback automático"""
    try:
        return ImageFont.truetype(UnoCardDesign.FONT_PATHS[font_type], size)
    except:
        try:
            return ImageFont.truetype(UnoCardDesign.FONT_PATHS["fallback"], size)
        except:
            return ImageFont.load_default()

def create_card(card_type, color, value):
    # Configuração base
    card = Image.new('RGBA', UnoCardDesign.CARD_SIZE, (0,0,0,0))
    draw = ImageDraw.Draw(card)
    
    # Sombra exterior
    shadow = Image.new('RGBA', UnoCardDesign.CARD_SIZE, (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_coords = [
        UnoCardDesign.SHADOW_OFFSET,
        (UnoCardDesign.CARD_SIZE[0] + UnoCardDesign.SHADOW_OFFSET[0],
         UnoCardDesign.CARD_SIZE[1] + UnoCardDesign.SHADOW_OFFSET[1])
    ]
    shadow_draw.rounded_rectangle(
        shadow_coords,
        fill=(0,0,0,80),
        radius=UnoCardDesign.CORNER_RADIUS
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(UnoCardDesign.SHADOW_BLUR))
    
    # Fundo da carta
    if color == "wild":
        bg = create_radial_rainbow(UnoCardDesign.CARD_SIZE)
    else:
        bg = create_gradient(
            UnoCardDesign.COLORS[color]["main"],
            UnoCardDesign.COLORS[color]["secondary"],
            UnoCardDesign.CARD_SIZE
        )
    
    # Máscara com bordas arredondadas
    mask = Image.new('L', UnoCardDesign.CARD_SIZE, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0,0), UnoCardDesign.CARD_SIZE],
        fill=255,
        radius=UnoCardDesign.CORNER_RADIUS
    )
    card.paste(bg, mask=mask)
    
    # Elemento central
    if card_type == "number":
        draw_centered_element(draw, str(value), color, 350)
    elif card_type in ["action", "wild"]:
        symbol = UnoCardDesign.SYMBOLS[value]
        draw_centered_element(draw, symbol, color, 400, is_symbol=True)
    
    # Combinar elementos
    final = Image.alpha_composite(shadow, card)
    return final

def draw_centered_element(draw, text, color, font_size, is_symbol=False):
    """Desenha elementos centrais com sombra e contorno"""
    font_type = "symbols" if is_symbol else "main"
    font = load_font(font_type, font_size)
    
    # Posição central
    bbox = draw.textbbox((0,0), text, font=font, anchor='mm')
    position = (
        UnoCardDesign.CARD_SIZE[0]//2,
        UnoCardDesign.CARD_SIZE[1]//2
    )
    
    # Efeito de sombra
    for offset in [(-4,-4), (4,4)]:
        draw.text(
            (position[0]+offset[0], position[1]+offset[1]),
            text,
            font=font,
            fill=(0,0,0,120),
            anchor='mm'
        )
    
    # Cor do contorno
    stroke_color = (
        UnoCardDesign.COLORS[color]["secondary"] 
        if color != "wild" else 
        (30, 30, 30)
    )
    
    # Texto principal
    draw.text(
        position,
        text,
        font=font,
        fill='white',
        stroke_width=15,
        stroke_fill=stroke_color,
        anchor='mm'
    )

def create_gradient(color1, color2, size):
    """Cria gradiente vertical suave"""
    gradient = Image.new('RGB', size, color1)
    draw = ImageDraw.Draw(gradient)
    
    for y in range(size[1]):
        alpha = y / size[1]
        r = int(color1[0] + (color2[0] - color1[0]) * alpha)
        g = int(color1[1] + (color2[1] - color1[1]) * alpha)
        b = int(color1[2] + (color2[2] - color1[2]) * alpha)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return gradient

def generate_uno_deck():
    os.makedirs("uno_deck", exist_ok=True)
    
    # Cartas numéricas
    for color in ["red", "blue", "green", "yellow"]:
        for number in range(10):
            card = create_card("number", color, number)
            card.save(f"uno_deck/{color}_{number}.png")
    
    # Cartas de ação
    for color in ["red", "blue", "green", "yellow"]:
        for action in ["Skip", "Reverse", "Draw +2"]:
            for _ in range(2):
                card = create_card("action", color, action)
                card.save(f"uno_deck/{color}_{action}.png")
    
    # Cartas curinga
    for wild in ["Wild", "Wild +4"]:
        for _ in range(4):
            card = create_card("wild", "wild", wild)
            card.save(f"uno_deck/wild_{wild}.png")

if __name__ == "__main__":
    generate_uno_deck()
    print("Baralho UNO premium gerado com sucesso!")
