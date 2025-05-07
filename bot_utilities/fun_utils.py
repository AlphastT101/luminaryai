from PIL import Image, ImageDraw, ImageFont

facts = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "Cows have best friends and can become stressed when they are separated from them.",
    "Bananas are berries, but strawberries aren't.",
    "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion.",
    "A 'jiffy' is an actual unit of time, equivalent to 1/100th of a second.",
    "The first recorded game of baseball was played in 1846 in Hoboken, New Jersey.",
    "The smell of freshly cut grass is actually a plant distress call.",
    "Humans and giraffes have the same number of neck vertebrae (seven).",
    "A group of flamingos is called a 'flamboyance.'",
    "The dot over the letters 'i' and 'j' is called a tittle.",
    "The longest word without a vowel is 'rhythms.'",
    "The first known contraceptive was crocodile dung, used by ancient Egyptians.",
    "Cows have regional accents.",
    "There are more possible iterations of a game of chess than there are atoms in the known universe.",
    "The average person will spend six months of their life waiting for red lights to turn green.",
    "The world's largest desert is Antarctica.",
    "The 'Waffle House Index' is an informal measure used by FEMA to determine the severity of a storm and the likely scale of assistance required for disaster recovery.",
]

words_list = [
    "Apple", "Bacon", "Carry", "Doggy", "Eleph", "Flame", "Grass", "Happy", "Icing", "Jolly",
    "Kitty", "Lemon", "Mango", "Noble", "Olive", "Pizza", "Queen", "Radar", "Sweet", "Tango",
    "Umbra", "Venom", "Water", "Xenon", "Yacht", "Zebra", "Adept", "Bliss", "Candy", "Dwarf",
    "Eagle", "Fairy", "Gears", "Hatch", "Icily", "Jelly", "Kazoo", "Lunar", "Magic", "Nerdy",
    "Oasis", "Puppy", "Quick", "Rover", "Savvy", "Tiger", "Unity", "Vital", "Waltz", "Xerox",
    "Yield", "Zesty", "Amigo", "Baker", "Cutey", "Daisy", "Evoke", "Fudge", "Giant", "Haven",
    "Inked", "Juicy", "Kiosk", "Lemon", "Mocha", "Nymph", "Olive", "Piano", "Quota", "Rusts",
    "Scone", "Table", "Unity", "Vocal", "Whirl", "Xylan", "Yogis", "Zappy", "Angel", "Beach",
    "Candy", "Disco", "Earth", "Fable", "Globe", "Hasty", "Ivory", "Juice", "Kitty", "Lemon",
    "Mocha", "Nylon", "Omega", "Panda", "Queen", "Ruler", "Sunny", "Table", "Unity", "Velum",
    "Whisk", "Xerox", "Yogis", "Zebra"
]
choices = ["rock", "paper", "scissors"]
outcomes = {
    "rock": {"rock": "tie", "paper": "lose", "scissors": "win"},
    "paper": {"rock": "win", "paper": "tie", "scissors": "lose"},
    "scissors": {"rock": "lose", "paper": "win", "scissors": "tie"}
}


def wordleScore(target, guess):
    # score_name = {2: 'green', 1: 'amber', 0: 'gray'}
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