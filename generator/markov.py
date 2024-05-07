import random
import re

import markovify

from generator.mode import Mode


class MarkovGenerator:
    def __init__(self, text: str, length: int):
        empty_line_pattern = re.compile(r"^\s+", flags=re.M)
        self.text = empty_line_pattern.sub("", text).strip()
        self.length = length
        self.generated_text = None

    def generate(self):
        text_model = markovify.NewlineText(
            input_text=self.text,
            state_size=1,
            well_formed=False
        )
        generated_text = text_model.make_short_sentence(self.length)

        if not generated_text:
            random_sentence = random.choice(self.text)[:self.length]
            symbols_plus = [".", "~~", "!", "?"]
            generated_text = random_sentence + random.choice(symbols_plus)

        self.generated_text = generated_text

    def change_mode(self, mode):
        if self.generated_text:
            self.generated_text = Mode.parse_mode(int(mode), self.generated_text)
