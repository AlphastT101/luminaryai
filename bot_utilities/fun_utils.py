import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

def wordleScore(target, guess):
    score_name = {2: 'green', 1: 'amber', 0: 'gray'}
    if len(target) != 5:
        return f'{target}: Expected 5 character target.'
    elif len(guess) != 5:
        return f'{guess}: Expected 5 character guess.'

    score = []
    remaining_chars = target
    for tg, gg in zip(target, guess):
        if tg == gg:
            score.append(2)
            remaining_chars = remaining_chars.replace(tg, '', 1)
        elif gg in remaining_chars:
            score.append(1)
            remaining_chars = remaining_chars.replace(gg, '', 1)
        else:
            score.append(0)
    return score


def generate_wordle_image(input_string, colors):
    char_width = 40
    char_height = 60
    total_width = char_width * len(input_string)
    total_height = char_height

    image = Image.new('RGB', (total_width, total_height), color=(238, 238, 238))  # Light gray background
    draw = ImageDraw.Draw(image)

    color_map = {
        "1": (255, 187, 51),
        "2": (32, 193, 85),
        "0": (128, 128, 128),
    }

    font = ImageFont.truetype('arial.ttf', 40)

    for i, (char, color) in enumerate(zip(input_string, colors)):
        x_pos = i * char_width
        y_pos = 0
        char = char.upper()

        if color in color_map:
            bg_color = color_map[color]
            draw.rectangle([x_pos, y_pos, x_pos + char_width, y_pos + char_height], fill=bg_color)
        else:
            bg_color = (255, 255, 255)  # Default color is white
            draw.rectangle([x_pos, y_pos, x_pos + char_width, y_pos + char_height], fill=bg_color)

        char_width_offset, char_height_offset = 30,35
        draw.text((x_pos + (char_width - char_width_offset) / 2, (char_height - char_height_offset) / 3),
                  char, font=font, fill=(0, 0, 0))

    return image