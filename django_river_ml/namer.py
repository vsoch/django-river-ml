from random import choice


class Namer:

    _descriptors = [
        "chunky",
        "buttery",
        "delicious",
        "scruptious",
        "dinosaur",
        "boopy",
        "lovely",
        "carniverous",
        "hanky",
        "loopy",
        "doopy",
        "astute",
        "gloopy",
        "outstanding",
        "stinky",
        "conspicuous",
        "fugly",
        "frigid",
        "angry",
        "adorable",
        "sticky",
        "moolicious",
        "cowy",
        "spicy",
        "grated",
        "crusty",
        "stanky",
        "blank",
        "bumfuzzled",
        "fuzzy",
        "hairy",
        "peachy",
        "tart",
        "creamy",
        "arid",
        "strawberry",
        "butterscotch",
        "wobbly",
        "persnickety",
        "nerdy",
        "dirty",
        "placid",
        "bloated",
        "swampy",
        "pusheena",
        "hello",
        "goodbye",
        "milky",
        "purple",
        "rainbow",
        "bricky",
        "muffled",
        "anxious",
        "misunderstood",
        "eccentric",
        "quirky",
        "lovable",
        "reclusive",
        "faux",
        "evasive",
        "confused",
        "crunchy",
        "expensive",
        "ornery",
        "fat",
        "phat",
        "joyous",
        "expressive",
        "psycho",
        "chocolate",
        "salted",
        "gassy",
        "red",
        "blue",
    ]

    _nouns = [
        "squidward",
        "hippo",
        "butter",
        "animal",
        "peas",
        "lettuce",
        "carrot",
        "onion",
        "peanut",
        "cupcake",
        "muffin",
        "buttface",
        "leopard",
        "parrot",
        "parsnip",
        "poodle",
        "itch",
        "punk",
        "kerfuffle",
        "soup",
        "noodle",
        "avocado",
        "peanut-butter",
        "latke",
        "milkshake",
        "banana",
        "lizard",
        "lemur",
        "lentil",
        "bits",
        "house",
        "leader",
        "toaster",
        "signal",
        "pancake",
        "kitty",
        "cat",
        "cattywampus",
        "poo",
        "malarkey",
        "general",
        "rabbit",
        "chair",
        "staircase",
        "underoos",
        "snack",
        "lamp",
        "eagle",
        "hobbit",
        "diablo",
        "earthworm",
        "pot",
        "plant",
        "leg",
        "arm",
        "bike",
        "citrus",
        "dog",
        "puppy",
        "blackbean",
        "ricecake",
        "gato",
        "nalgas",
        "lemon",
        "caramel",
        "fudge",
        "cherry",
        "sundae",
        "truffle",
        "cinnamonbun",
        "pastry",
        "egg",
        "omelette",
        "fork",
        "knife",
        "spoon",
        "salad",
        "train",
        "car",
        "motorcycle",
        "bicycle",
        "platanos",
        "mango",
        "taco",
        "pedo",
        "nunchucks",
        "destiny",
        "hope",
        "despacito",
        "frito",
        "chip",
    ]

    def generate(self, delim="-", length=4, chars="0123456789"):
        """
        Generate a robot name. Inspiration from Haikunator, but much more
                 poorly implemented ;)

        Parameters
        ==========
        delim: Delimiter
        length: TokenLength
        chars: TokenChars
        """

        descriptor = self._select(self._descriptors)
        noun = self._select(self._nouns)
        return delim.join([descriptor, noun])

    def _select(self, select_from):
        """select an element from a list using random.choice

        Parameters
        ==========
        should be a list of things to select from
        """
        if len(select_from) <= 0:
            return ""

        return choice(select_from)


namer = Namer()
