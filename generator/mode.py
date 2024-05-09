import math
import random
from . import massives


class Mode:
    @staticmethod
    def parse_mode(mode: int, text: str):
        match mode:
            case 0:
                return Mode.not_normal(text)
            case 1:
                return Mode.upper(text)
            case 2:
                return Mode.lower(text)
            case 3:
                return Mode.hachimuchi(text)
            case 4:
                return Mode.smiles(text)
            case 5:
                return Mode.reverse(text)
            case 6:
                return Mode.illiterate(text)
            case 7:
                return Mode.rap(text)
            case _:
                return text

    @staticmethod
    def not_normal(text: str):
        return ''.join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text)])

    @staticmethod
    def upper(text: str):
        return text.upper()

    @staticmethod
    def lower(text: str):
        return text.lower()

    @staticmethod
    def hachimuchi(text: str):
        return Mode.replace_massive(text, massives.dungeon_list)

    @staticmethod
    def smiles(text: str):
        all_words = text.split()
        newline = f"{random.choice(massives.smiles_list)}"

        for word in all_words:
            newline += f"{word}{random.choice(massives.smiles_list)}"

        return newline

    @staticmethod
    def reverse(text: str):
        return text[::-1]

    @staticmethod
    def illiterate(text: str):
        return Mode.add_errors(text, massives.errors_dict)

    @staticmethod
    def rap(text: str):
        words = text.split()
        new_words = []
        for word in words:
            if word in massives.rap_massive:
                new_words.append(massives.rap_massive[word])
            else:
                new_words.append(word)

            if random.random() > 0.7:
                new_words[-1] += ' e'

        rap_text = ' '.join(new_words) + ' e.'

        return rap_text

    @staticmethod
    def add_errors(text: str, massive):
        result = []
        for c in text:
            replacement = massive.get(c, [c])
            result.append(random.choice(replacement))
        return ''.join(result)

    @staticmethod
    def replace_massive(text: str, massive):
        words = text.split()
        unique_indexes = set(range(len(words)))
        num_unique_indexes = math.ceil(len(unique_indexes) / 3)

        if num_unique_indexes == 0:
            return random.choice(words)

        random_indexes = random.sample(unique_indexes, num_unique_indexes)
        for i in random_indexes:
            words[i] = random.choice(massive)

        return ' '.join(words)
