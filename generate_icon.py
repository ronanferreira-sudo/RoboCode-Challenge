import os
from PIL import Image, ImageDraw

def create_robot_icon(output_path="robot.ico"):
    size = 256
    # Criar imagem transparente com canal Alpha
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo estilo Badge Cyber (Quadrado arredondado com degradê escuro)
    margin = 12
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=48,
        fill=(10, 13, 20, 255),
        outline=(0, 255, 204, 255),
        width=8
    )

    # Brilho de Fundo Neon (Círculo Roxo/Ciano)
    draw.ellipse([50, 50, size - 50, size - 50], fill=(168, 85, 247, 40))

    # --- DESENHO DO ROBÔ ---
    # Antena do Robô (Haste e Esfera no topo)
    draw.line([128, 45, 128, 75], fill=(0, 255, 204, 255), width=8)
    draw.ellipse([116, 33, 140, 57], fill=(236, 72, 153, 255), outline=(0, 255, 204, 255), width=4)

    # Orelhas / Conectores laterais do Robô
    draw.rounded_rectangle([45, 110, 65, 150], radius=8, fill=(31, 41, 61, 255), outline=(0, 255, 204, 255), width=4)
    draw.rounded_rectangle([191, 110, 211, 150], radius=8, fill=(31, 41, 61, 255), outline=(0, 255, 204, 255), width=4)

    # Cabeça do Robô (Bloco principal)
    draw.rounded_rectangle([60, 75, 196, 185], radius=28, fill=(18, 24, 36, 255), outline=(0, 255, 204, 255), width=8)

    # Painel dos Olhos / Visor do Robô
    draw.rounded_rectangle([80, 95, 176, 140], radius=14, fill=(10, 13, 20, 255), outline=(168, 85, 247, 255), width=5)

    # Olhos Neon brilhantes (Ciano com ponto de luz)
    draw.ellipse([92, 107, 116, 131], fill=(0, 255, 204, 255))
    draw.ellipse([140, 107, 164, 131], fill=(0, 255, 204, 255))
    # Brilho branco nos olhos
    draw.ellipse([96, 110, 104, 118], fill=(255, 255, 255, 255))
    draw.ellipse([144, 110, 152, 118], fill=(255, 255, 255, 255))

    # Boca de Led do Robô (Grade Cyber)
    for x in range(95, 165, 12):
        draw.line([x, 155, x, 168], fill=(0, 255, 204, 255), width=4)

    # Corpo / Ombro do Robô (Parte inferior)
    draw.rounded_rectangle([75, 190, 181, 235], radius=16, fill=(31, 41, 61, 255), outline=(168, 85, 247, 255), width=6)
    # Núcleo de Energia (Peito)
    draw.polygon([(128, 198), (140, 215), (116, 215)], fill=(234, 179, 8, 255))

    # Salva nos formatos .ico e .png
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, format="ICO", sizes=ico_sizes)
    img.save("robot.png", format="PNG")
    
    # Salva também como favicon.ico para o navegador
    static_ico = os.path.join("app", "static", "favicon.ico")
    os.makedirs(os.path.dirname(static_ico), exist_ok=True)
    img.save(static_ico, format="ICO", sizes=ico_sizes)
    print(f"[OK] Icone do robo gerado com sucesso em: {output_path}")

if __name__ == "__main__":
    create_robot_icon()
