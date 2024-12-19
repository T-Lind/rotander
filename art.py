from PIL import Image, ImageDraw

# Define sprite size and palette
SPRITE_SIZE = 16  # 16x16 pixels
PALETTE = {
    "background": (0, 0, 0),         # Black
    "skin": (255, 204, 153),         # Skin color
    "clothing": (0, 102, 204),       # Blue
    "accent": (255, 0, 0),           # Red
}

def create_regular_stance():
    """Draws the regular stance of the character."""
    image = Image.new('RGB', (SPRITE_SIZE, SPRITE_SIZE), PALETTE["background"])
    draw = ImageDraw.Draw(image)

    # Draw the head
    draw.rectangle([5, 1, 10, 6], fill=PALETTE["skin"])  # Head
    # Draw the body
    draw.rectangle([6, 7, 9, 12], fill=PALETTE["clothing"])  # Torso
    # Draw the arms
    draw.rectangle([4, 7, 5, 11], fill=PALETTE["clothing"])  # Left arm
    draw.rectangle([10, 7, 11, 11], fill=PALETTE["clothing"])  # Right arm
    # Draw the legs
    draw.rectangle([6, 13, 7, 15], fill=PALETTE["accent"])  # Left leg
    draw.rectangle([8, 13, 9, 15], fill=PALETTE["accent"])  # Right leg

    return image

def create_jump_stance():
    """Draws the jump stance of the character."""
    image = Image.new('RGB', (SPRITE_SIZE, SPRITE_SIZE), PALETTE["background"])
    draw = ImageDraw.Draw(image)

    # Draw the head
    draw.rectangle([5, 0, 10, 5], fill=PALETTE["skin"])  # Head raised slightly
    # Draw the body
    draw.rectangle([6, 6, 9, 11], fill=PALETTE["clothing"])  # Torso
    # Draw the arms
    draw.rectangle([4, 6, 5, 10], fill=PALETTE["clothing"])  # Left arm
    draw.rectangle([10, 6, 11, 10], fill=PALETTE["clothing"])  # Right arm
    # Draw the legs (slightly bent for jump)
    draw.rectangle([5, 12, 7, 13], fill=PALETTE["accent"])  # Left leg
    draw.rectangle([8, 12, 10, 13], fill=PALETTE["accent"])  # Right leg

    return image

def save_sprites():
    """Saves the sprites to PNG files."""
    regular_stance = create_regular_stance()
    jump_stance = create_jump_stance()

    regular_stance.save('regular_stance.png')
    jump_stance.save('jump_stance.png')
    print("Sprites saved as 'regular_stance.png' and 'jump_stance.png'.")

if __name__ == "__main__":
    save_sprites()
