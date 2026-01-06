from random import choice, randint

DEFAULT_LOCALE = 'en'
LOCALES = ('en', 'ru')
MIN_LENGTH = 6
MAX_LENGTH = 12

en_vowels = ('a', 'e', 'i', 'o', 'u', 'y')
en_consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z',
                 'sh', 'zh', 'ch', 'kh', 'th')
ru_vowels = ('а', 'е', 'и', 'о', 'у', 'э', 'ю', 'я')
ru_consonants = ('б', 'в', 'г', 'д', 'ж', 'з', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ')


def generate_nick(locale=None):
    """
    Generates nickname

    :param str locale:
    :rtype: str
    :return:
    """
    if locale is None or locale not in LOCALES:
        locale = DEFAULT_LOCALE

    vowels = globals()['{}_vowels'.format(locale)]
    consonants = globals()['{}_consonants'.format(locale)]

    is_vowels_first = bool(randint(0, 1))
    result = ''
    for i in range(0, randint(MIN_LENGTH, MAX_LENGTH)):
        is_even = i % 2 == 0
        if (is_vowels_first and is_even) or (not is_vowels_first and not is_even):
            result += choice(vowels)
        else:
            result += choice(consonants)

    return result.title()


actions = ["discovered", "invented", "built", "destroyed", "saved", "found", "lost", "created", "stole", "ate", "drank",
           "wrote", "read", "painted", "sold", "bought", "killed", "rescued", "captured", "released", "won", "lost",
           "broke", "fixed", "learned", "taught", "sang", "danced", "fought", "escaped"]
quantities = ["three", "five", "seven", "a dozen", "hundreds of", "countless", "several", "two giant", "three tiny",
              "four ancient", "five magical", "six golden", "seven silver", "eight crystal", "nine wooden", "ten stone",
              "an army of", "a flock of", "a herd of", "a swarm of", "a pack of", "a school of", "a pride of",
              "a murder of", "a parliament of", "a business of", "a conspiracy of", "an embarrassment of",
              "a pandemonium of", "a kaleidoscope of"]
objects = ["dragons", "unicorns", "wizards", "fairies", "robots", "aliens", "ghosts", "pirates", "ninjas", "vampires",
           "werewolves", "zombies", "mermaids", "elves", "dwarves", "trolls", "goblins", "phoenixes", "griffins",
           "sphinxes", "artifacts", "scrolls", "potions", "spells", "treasures", "kingdoms", "castles", "spaceships",
           "planets", "galaxies"]


def generate_event():
    global actions
    global quantities
    global objects
    """Генерирует случайное событие"""
    action = choice(actions)
    quantity = choice(quantities)
    obj = choice(objects)

    return f"{action.capitalize()} {quantity} {obj}"
