from PIL import Image, ImageDraw, ImageFont
import random

# Define image size
WIDTH, HEIGHT = 256, 256

# Define color palette (8-bit style)
PALETTE = {
    'background': (34, 34, 34),       # Dark gray
    'platform': (70, 130, 180),       # Steel Blue
    'character': (255, 165, 0),       # Orange
    'title_text': (255, 255, 255),    # White
    'accent': (255, 215, 0),          # Gold
}

def draw_background(draw):
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=PALETTE['background'])

def draw_platforms(draw, num_platforms=5):
    platform_height = 10
    for _ in range(num_platforms):
        platform_width = random.randint(40, 80)
        x = random.randint(0, WIDTH - platform_width)
        y = random.randint(HEIGHT // 2, HEIGHT - platform_height - 10)
        draw.rectangle([x, y, x + platform_width, y + platform_height], fill=PALETTE['platform'])
        # Add some blocks on the platform
        block_size = 8
        num_blocks = platform_width // block_size
        for i in range(num_blocks):
            block_x = x + i * block_size
            block_y = y
            draw.rectangle([block_x, block_y, block_x + block_size - 1, block_y + block_size -1], fill=PALETTE['accent'])

def draw_character(draw):
    # Simple pixelated character
    character_size = 16
    character_x = WIDTH // 2 - character_size // 2
    character_y = HEIGHT // 2 - character_size // 2
    for y in range(character_size):
        for x in range(character_size):
            # Simple pattern for the character (e.g., a square with eyes)
            if (x in [3, 4, 11, 12] and y in [4,5]) or (x >=2 and x <=13 and y >=2 and y <=13):
                draw.point((character_x + x, character_y + y), fill=PALETTE['character'])

def draw_title(draw):
    try:
        # Attempt to use a pixel font
        font = ImageFont.truetype("PressStart2P.ttf", 32)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()

    text = "R O T A N D E R"
    # Get the bounding box of the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Center the text
    x = (WIDTH - text_width) // 2
    y = 10

    draw.text((x, y), text, font=font, fill=PALETTE['title_text'])

def add_effects(image):
    # Optional: Add a pixelated filter or other effects
    return image

def create_cover_art():
    # Create a new image with background color
    image = Image.new('RGB', (WIDTH, HEIGHT), PALETTE['background'])
    draw = ImageDraw.Draw(image)

    # Draw elements
    draw_background(draw)
    draw_platforms(draw)
    draw_character(draw)
    draw_title(draw)

    # Add effects if any
    image = add_effects(image)

    # Save the image
    image.save('rotander_cover_art.png')
    print("Cover art generated and saved as 'rotander_cover_art.png'.")

if __name__ == "__main__":
    create_cover_art()
