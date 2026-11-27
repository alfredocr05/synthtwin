"""THE TEXT ZONE OF THE INSIDE RECORD (lane TYPES-24): a cell that carries a structure of its own is written in the real column's own templates.

WHY. The description publishes no value of free text, and none of a
label's rare tail, so its twin writes filler there (`!!!!! !!!!`) and
stand-ins (`group-7`); it writes record numbers off the real by an
opening figure no real one uses, whatever else the layout asks (an
IPv4 octet past 255, a UUID's version figure moved, a key's check
figure wrong). Code written on the real table then fails on the twin:
a script that splits `sys=141;dia=74;hr=81` on its marks, parses a
JSON cell or a waveform `[0.512, -0.034, ...]`, reads `BP 141/74 L
arm`, maps `5 mars 2023` to a date, checks a key's Luhn figure or
reads a URL's path finds nothing it can read. The inside record never
leaves the computer and the twin is the only thing Safe Harbor binds
(the owner, 2026-11-18), so the record may hold what such a cell is
made of, and the twin may wear it.

WHAT THE ZONE HOLDS, a column at a time (`entry_of`):

* THE WORDS EVERY TEMPLATE IS BUILT FROM: a run of letters is kept only
  where `floor` different people (rows, where no column names a person)
  write it; every other run of letters is a slot the twin fills with
  letters of its own, and every number is a slot. A person's name, held
  by one person's rows, is never kept.
* THE TEMPLATES: a cell with its kept words and marks as written and
  each slot in its place (`sys=<n>;dia=<n>;hr=<n>`), kept only where
  `floor` different people write it, with how many rows wear it; each
  slot's numbers (their census where they are few, else their quantile
  function on `GRID` points, never past the real ends), the ranks of
  each row's numbers together (so the numbers of one cell keep their
  relation: a pressure's two readings, a waveform's shape), and the
  lengths and letters of its made-up words. A DATE IN A TEMPLATE -- a
  day, a month's name in English, French, German, Spanish, Italian,
  Portuguese or Dutch, and a year -- is a slot of its own: the zone
  holds how many rows hold each year, month and weekday, and the twin
  draws a year, month and weekday by those counts and makes up the day
  of the month (the owner's rule of 2026-11-18), written with the
  column's own spelling of the month.
* THE FREE CELLS: a cell no kept template fits is drawn from a chain of
  kept words, marks and slots, two tokens of context, cut at the length
  the description's twin gave it.
* FOR A COLUMN OF RECORD NUMBERS (`MODE_IDENTIFIER`): the templates of
  its runs of figures, letters, hexadecimal or base-64 characters, each
  place's characters, a short run's census (a line number `01` to
  `12`), a template every real cell of which passes the Luhn check or
  reads as an IPv4 address, and THE MARK THAT KEEPS EVERY TWIN VALUE OFF
  THE REAL: the first run of figures whose first figure takes a value no
  real cell of the template opens it with (read over every row, not the
  sample), or, for an IPv4 address, a first number no real cell holds;
  a template with no such place is written only where its free places
  hold at least `ENTROPY_BITS` bits, and the twin checks still read
  every twin value against every real one. A key of figures alone
  whose every opening figure is a real key's is written at its own
  width as a number no real key is (`ABSENT_KEY_WIDTH`).
* FOR A COLUMN OF A PERSON'S DETAILS (`MODE_DETAIL`, lane TEXTZONE):
  street addresses, telephone numbers, e-mail and web addresses, names
  and record numbers holding a key, written in their real layouts with
  only the column's layout words kept (`_detail_kept`) and every other
  word made up from `NEUTRAL_WORDS` that no real cell writes; each value
  exactly as long as the description's twin's and holding a piece no
  real cell holds (`_detail_plan`): such a made-up word, a long run
  opening off the real, or a short number no real cell of its template
  holds there -- a telephone number's area code and exchange always.

HOW THE TWIN USES IT (`write_column`): each different value of the
description's twin's column (outside the spellings it keeps: the
published levels and missing spellings) is written again as one new
value, so the column keeps how many different values it has, how many
rows hold each, which rows share one, how many of its cells are all
figures or of a code's alphabet, and each value's length (the
description's own facts of free text); a column whose cells the
description held as dates in disguise (`MODE_HELD`) has as many of its
blank cells filled as the real column held values there. Every number
is drawn inside the real column's ends, every made-up word differs
from every kept word, a run of five figures or more opens with a figure
no real run of its width opens with, and a template's tail value that a
label column writes stays under the floor (it never becomes a level the
description does not publish).

Nothing here prints, logs or raises a value of the zone. No randomness
is imported: the draws are SplitMix64 streams of the seed and the
column's name, so the same zone and seed write the same bytes.
"""

import dataclasses
import typing

from synthtwin import date_counts, parsing

ZONE = "text"
VERSION = 1
MODE_FREE = "free"
MODE_TAIL = "tail"
MODE_IDENTIFIER = "identifier"
MODE_HELD = "held"
MODE_CENSUS = "census"
MODE_DETAIL = "detail"
MODES = (MODE_FREE, MODE_TAIL, MODE_IDENTIFIER, MODE_HELD, MODE_CENSUS, MODE_DETAIL)
# A measurement column's spellings are dealt from the real census where it holds at most this many (`MODE_CENSUS`).
CENSUS_SPELLINGS = 1000
# The rows a column's templates are learned from: every row up to this many, else rows at an even stride.
SAMPLE_CAP = 20000
# The rows of a template whose numbers are kept; the ranks of a cell's numbers kept together, at most.
SLOT_SAMPLE = 4000
JOINT_CAP = 1000
# How far each rank of a cell's numbers is moved from the real row's it is drawn beside (`_ranks`).
BANDWIDTH = 0.04
# A slot's numbers kept as a census where they hold at most this many different spellings, else on a grid.
CENSUS_CAP = 200
GRID = 201
RANK = 1000
# The free cells a chain is learned from, and the tokens of one cell it reads.
FREE_CAP = 5000
TOKENS_CAP = 4000
# Draws of one value before the zone takes the nearest it found, then searches a template's census.
TRIES = 24
FREE_TRIES = 3
# Values longer than this are not held to keep the column's values apart (`_fresh`).
FRESH_CAP = 200
BALANCE_TRIES = 200000
SEARCH_CAP = 200000
# A template with no place to keep its values off the real is written only with at least this much room.
ENTROPY_BITS = 64
# The most words a column's templates keep as written (the record holds lists no longer than its grid).
KEPT_WORDS = 1000
# A template's share of a label's tail rows below which the tail keeps its stand-ins.
TAIL_SHARE = 0.5
# A tail of lists (`M54.5;I10;K21.9`): the marks between items, the spaced ones first; the share of the tail's cells
# that hold the mark and of its items the floor of people write, below which the tail is no list.
LIST_MARKS = ("; ", ";", " | ", "|", ", ", ",")
LIST_SHARE = 0.9
# The most runs of the items each value holds, in the real order, the record keeps (past them: a census by size).
LIST_RUNS = 2000
# A short run of figures a key repeats (a line number) is drawn from its census when it holds at most this many.
RUN_CENSUS_CAP = 32
RUN_CENSUS_WIDTH = 3
# A run of figures this long or longer opens with a figure no real run of its width opens with.
OPENING_RUN = 5
_GOLDEN = 0x9E3779B97F4A7C15
_MASK = (1 << 64) - 1
_DIGITS = "0123456789"
_HEX_LOWER = "0123456789abcdef"
_HEX_UPPER = "0123456789ABCDEF"
_BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# The marks a template's key is joined with; a cell holding one is read as no template.
_SEP = "\x00"
_LIT = "\x01"
_NUM = "\x02"
_WORD = "\x03"
_DATE = "\x04"
_RUN = "\x05"
_START = "\x06"
_END = "\x07"
_MARKS = (_SEP, _LIT, _NUM, _WORD, _DATE, _RUN, _START, _END)
# The words a date's day, month and year may stand apart by, and the marks.
_DATE_FILLERS = ("de", "del", "do", "da", "of", "le", "the")

# A PERSON'S DETAILS (`MODE_DETAIL`): a column the twin checks read as a person's details -- street addresses, e-mail
# addresses, telephone numbers, web addresses, record numbers holding a key -- is written in its real layouts with every
# word that could name somebody made up from `NEUTRAL_WORDS`. A word is kept as written only where it is the column's
# layout: a word of `DETAIL_VOCABULARY` (a street's suffix, a web scheme, a top-level domain, a unit), a label of a
# reserved domain (`RESERVED_DOMAINS`, `RESERVED_TOP`: no person's and no employer's), or a word at least
# `LAYOUT_SHARE` of the rows read write outside any host or mail domain (`chart` in every chart link) -- and in every
# case at least the floor of different people write it.
LAYOUT_SHARE = 0.5
DETAIL_VOCABULARY = frozenset((
    "http", "https", "ftp", "sftp", "mailto", "www",
    "com", "org", "net", "edu", "gov", "mil", "int", "info", "biz", "io", "co", "us", "uk", "ca", "au", "de", "fr", "nl",
    "es", "it", "ie", "nz", "in", "jp", "br", "mx", "ch", "se", "no", "dk", "fi", "be", "at", "pl", "pt",
    "st", "street", "ave", "avenue", "av", "rd", "road", "blvd", "boulevard", "dr", "drive", "ln", "lane", "ct",
    "court", "place", "ter", "terrace", "way", "cir", "circle", "pkwy", "parkway", "hwy", "highway", "sq",
    "square", "trl", "trail", "pike", "loop", "aly", "alley", "plz", "plaza", "cres", "crescent", "row", "walk",
    "n", "s", "e", "w", "ne", "nw", "sw", "north", "south", "east", "west", "northeast", "northwest",
    "southeast", "southwest", "apt", "apartment", "unit", "ste", "suite", "fl", "floor", "bldg", "building", "rm",
    "room", "po", "box", "p", "o", "pob",
))
RESERVED_DOMAINS = (("example", "com"), ("example", "org"), ("example", "net"))
# The marks a word of a link's path or query stands after (`_detail_entry`'s layout share).
_LINK_MARKS = ("/", "?", "&", "=", "#")
RESERVED_TOP = frozenset(("example", "test", "invalid", "localhost"))
# The made-up words a person's detail is written with: everyday things, no person's or place's name (none a common
# given name), no month, no word of `DETAIL_VOCABULARY`; a column keeps only those none of its real cells writes (`_neutral_left`).
NEUTRAL_WORDS = (
    "ant", "bay", "bee", "bog", "bud", "bun", "cob", "cod", "cog", "cot", "cub", "cup", "den", "dew", "dot", "eel",
    "elk", "emu", "fen", "fig", "fir", "fob", "fox", "gem", "gnu", "gum", "hay", "hen", "hob", "hub", "hut", "ink",
    "jar", "jet", "jib", "keg", "koi", "lea", "lid", "lob", "log", "mop", "mug", "nib", "nog", "nut", "oar", "oat",
    "orb", "owl", "pan", "paw", "pea", "peg", "pod", "pot", "rim", "rug", "rye", "sap", "sod", "tin", "tor", "tub",
    "urn", "vat", "vim", "wad", "wax", "web", "wok", "yak", "yam", "yew",
    "acre", "aloe", "apex", "arch", "axle", "bark", "barn", "bass", "bead", "bean", "beet", "bell", "bolt", "bran",
    "brew", "brim", "bulb", "buoy", "calf", "cart", "cask", "cave", "chip", "clam", "coal", "coin", "colt", "cone",
    "cork", "crab", "crag", "crow", "cube", "cusp", "dais", "dart", "disc", "dock", "dome", "drum", "duck", "dune",
    "dusk", "fawn", "felt", "fern", "flag", "flax", "foal", "foam", "fork", "gale", "glen", "goat", "gong", "gulf",
    "gull", "hail", "hare", "harp", "hawk", "haze", "heap", "helm", "hemp", "hilt", "hive", "hoop", "horn", "husk",
    "isle", "jute", "kale", "kelp", "kiln", "kiwi", "knot", "lamp", "leaf", "lens", "lime", "loam", "loft", "lute",
    "lynx", "malt", "mane", "mast", "mesa", "mica", "mink", "mint", "mist", "moat", "mole", "moss", "moth", "mule",
    "nest", "newt", "oboe", "orca", "oven", "palm", "peak", "pear", "plow", "plum", "pond", "puma", "quay", "rake",
    "reed", "reef", "reel", "rind", "robe", "rope", "ruff", "rush", "sail", "salt", "sand", "seal", "seed", "shed",
    "silk", "sill", "silt", "sink", "slab", "sled", "sloe", "slug", "snow", "sock", "soil", "soup", "spur", "stag",
    "stem", "swan", "tack", "tank", "tarn", "teal", "tent", "thaw", "tide", "toad", "tray", "tuba", "tuft", "tusk",
    "twig", "vane", "vase", "vine", "vole", "wasp", "weed", "wick", "wing", "wisp", "wool", "yarn", "yolk", "zinc",
    "acorn", "agate", "alder", "anvil", "apple", "aster", "atoll", "attic", "badge", "bagel", "banjo", "basin",
    "beach", "berry", "birch", "bison", "blaze", "bloom", "brick", "brook", "brush", "bugle", "cabin", "cairn",
    "camel", "canal", "cedar", "cello", "chalk", "chord", "churn", "cider", "cliff", "cloud", "clove", "cocoa",
    "comet", "crane", "cream", "creek", "crest", "crumb", "delta", "dingo", "drift", "eagle", "easel", "ember",
    "fable", "fence", "ferry", "finch", "fjord", "flame", "flint", "flute", "frost", "fruit", "gable", "gecko",
    "glade", "globe", "goose", "gourd", "grain", "grape", "grass", "grove", "heath", "hedge", "heron", "hinge",
    "igloo", "inlet", "jetty", "kayak", "kazoo", "koala", "krill", "larch", "latch", "ledge", "lemon", "lemur",
    "lilac", "linen", "llama", "lodge", "lotus", "mango", "maple", "marsh", "melon", "mocha", "moose", "nacre",
    "oasis", "ocean", "okapi", "onion", "orbit", "otter", "panel", "pansy", "peach", "pecan", "petal", "piano",
    "plaid", "plank", "plume", "porch", "prism", "quail", "quill", "quilt", "raven", "rhino", "ridge", "sable",
    "scarf", "scone", "sedge", "shale", "shell", "shore", "shrub", "skiff", "skunk", "slate", "sloop", "slope",
    "sloth", "snail", "spade", "spire", "spoon", "spray", "squid", "stalk", "steam", "stone", "stork", "storm",
    "straw", "sugar", "swale", "tango", "tapir", "thyme", "tiger", "topaz", "torch", "tower", "trout", "tulip",
    "tweed", "umber", "vapor", "vault", "viper", "wagon", "waltz", "whale", "wharf", "wheat", "wheel", "yeast",
    "acacia", "almond", "anchor", "antler", "badger", "bamboo", "barley", "basalt", "beacon", "beaver", "bobcat",
    "bonnet", "bonsai", "breeze", "bridge", "bronze", "burrow", "button", "cactus", "candle", "canopy", "canyon",
    "carbon", "cashew", "castle", "cicada", "citrus", "clover", "cobalt", "coffee", "condor", "copper", "cotton",
    "cougar", "coyote", "cradle", "crayon", "desert", "dinghy", "falcon", "fennel", "fiddle", "flower", "forest",
    "fossil", "garden", "garnet", "gopher", "gravel", "guitar", "harbor", "hearth", "hollow", "iguana", "indigo",
    "island", "jaguar", "jungle", "kettle", "lagoon", "lichen", "lizard", "locket", "lupine", "magnet", "mallow",
    "marble", "marlin", "meadow", "meteor", "mitten", "mussel", "nectar", "nutmeg", "orchid", "oriole", "osprey",
    "oyster", "paddle", "papaya", "parrot", "pebble", "pepper", "pigeon", "pillar", "pollen", "poplar", "puffin",
    "quartz", "quince", "rabbit", "radish", "raisin", "ribbon", "ripple", "saddle", "salmon", "sandal", "sesame",
    "shrimp", "sorbet", "sorrel", "sponge", "spruce", "squash", "stream", "summit", "sunset", "teapot", "thatch",
    "timber", "tinder", "tomato", "toucan", "tunnel", "turnip", "turtle", "velvet", "walnut", "walrus", "window",
    "wombat", "yarrow", "yogurt", "zephyr",
    "avocado", "balloon", "biscuit", "blossom", "bramble", "buffalo", "cabbage", "cabinet", "caramel", "caravan",
    "cassava", "catfish", "chamber", "chimney", "coconut", "compass", "cornice", "cottage", "cricket", "crystal",
    "cypress", "diamond", "dolphin", "emerald", "feather", "firefly", "gazelle", "giraffe", "glacier", "gondola",
    "granite", "hammock", "harvest", "hickory", "juniper", "kestrel", "lantern", "leather", "lettuce", "lobster",
    "mammoth", "meerkat", "mustard", "oatmeal", "octopus", "orchard", "oregano", "origami", "ostrich", "pancake",
    "panther", "paprika", "parsley", "peacock", "pelican", "penguin", "plateau", "pottery", "prairie", "pudding",
    "pumpkin", "raccoon", "rainbow", "saffron", "sapling", "satchel", "seagull", "seaweed", "sherbet", "snapper",
    "sparrow", "spatula", "spinach", "sunbeam", "sundial", "tadpole", "termite", "thistle", "thunder", "tractor",
    "trellis", "trinket", "truffle", "trumpet", "vanilla", "verbena", "vintage", "warbler", "weather", "wetland",
    "whisker",
    "aardvark", "antelope", "blizzard", "bluebell", "bluebird", "broccoli", "bullfrog", "capybara", "cardigan",
    "cardinal", "carousel", "chestnut", "cinnamon", "clematis", "cucumber", "daffodil", "dumpling", "eggplant",
    "elephant", "feldspar", "fireside", "fishbowl", "flamingo", "foxglove", "gemstone", "goldfish", "hazelnut",
    "hedgehog", "hillside", "honeybee", "kangaroo", "keyboard", "lakeside", "lavender", "lemonade", "mackerel",
    "mandolin", "marigold", "mongoose", "moonbeam", "mosquito", "mountain", "mulberry", "nightjar", "notebook",
    "nuthatch", "obsidian", "oleander", "overcast", "parakeet", "pheasant", "pinafore", "pinecone", "porpoise",
    "primrose", "reindeer", "riverbed", "sandbank", "sapphire", "scorpion", "seahorse", "seashell", "snowfall",
    "sombrero", "squirrel", "starfish", "starling", "stingray", "sunlight", "sunshine", "tamarind", "teaspoon",
    "toboggan", "tortoise", "umbrella", "windmill", "woodland", "woodpile", "zucchini",
    "alligator", "arrowroot", "artichoke", "asparagus", "avalanche", "blackbird", "blueberry", "bumblebee",
    "buttercup", "butterfly", "chameleon", "chickadee", "cormorant", "crocodile", "dandelion", "dragonfly",
    "driftwood", "evergreen", "fireplace", "flagstone", "goldfinch", "grapevine", "heartwood", "honeycomb",
    "jellyfish", "limestone", "marmalade", "moonstone", "nectarine", "nightfall", "pineapple", "pinstripe",
    "pistachio", "porcupine", "rainstorm", "raspberry", "sandpiper", "sandstone", "saxophone", "snowflake",
    "starlight", "sunflower", "sweetcorn", "tangerine", "toadstool", "turquoise", "waterfall", "waterlily",
    "whirlwind",
    "blackberry", "bluebonnet", "bluebottle", "butterfish", "cloudberry", "cornflower", "cottonwood", "gooseberry",
    "kingfisher", "lemongrass", "lighthouse", "meadowlark", "peppercorn", "peppermint", "riverstone", "salamander",
    "silverfish", "starflower", "strawberry", "tumbleweed", "watercress", "wildflower", "woodpecker",
    "bottlebrush", "candlelight", "cherrystone", "copperplate", "grasshopper", "honeysuckle", "hummingbird",
    "marshmallow", "nightingale", "pomegranate", "rattlesnake", "silverberry", "thunderbolt", "thunderhead",
    "butterscotch", "pumpernickel", "thunderstorm",
)
# A template's cells are drawn to an exact length over at most this many slots and this many characters of them.
DETAIL_SLOTS = 16
DETAIL_REACH = 400
# A short whole number that keeps a template's cells off the real (a house number beside kept words alone, a telephone
# number's area code and exchange) holds at most this many figures.
ABSENT_WIDTH = 4
# The longest made-up word a slot is written at, and how far from its own length a value is written where no template
# can be that long.
DETAIL_WORD_LONGEST = 24
DETAIL_NEAREST = 64
# A key of figures alone no opening figure keeps off the real is written at its own width, as a number no real key is,
# where it holds at most this many figures (the real keys' numbers kept as a bitmap of ten to this power).
ABSENT_KEY_WIDTH = 5


class TextError(ValueError):
    """A text zone the writer cannot read (another version, a damaged entry): the twin keeps the description's cells."""


# -- the draws: SplitMix64, no random source imported -------------------------------------------------


def _mixed(value: int) -> int:
    z = (value + _GOLDEN) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    return z ^ (z >> 31)


def _stream(seed: int, name: object, purpose: str) -> "list[int]":
    """A stream's state: the seed, the column's name and the draw's purpose, mixed character by character."""
    state = _mixed(seed & _MASK)
    for character in _text(name):
        state = _mixed(state ^ ord(character))
    state = _mixed(state ^ 0x5F)
    for character in purpose:
        state = _mixed(state ^ ord(character))
    return [state]


def _uniform(state: "list[int]") -> float:
    """The stream's next number in (0, 1)."""
    state[0] = (state[0] + _GOLDEN) & _MASK
    return ((_mixed(state[0]) >> 11) + 0.5) / 9007199254740992.0


def _below(state: "list[int]", count: int) -> int:
    """A whole number from 0 to `count` - 1, evenly."""
    if count <= 1:
        return 0
    return min(count - 1, int(_uniform(state) * count))


def _weighted(state: "list[int]", weights: "list[int]") -> int:
    """A place in `weights`, each as likely as its weight (all of them evenly where they sum to nought)."""
    total = 0
    for weight in weights:
        total = total + max(0, weight)
    if total <= 0:
        return _below(state, len(weights))
    point = _uniform(state) * total
    running = 0.0
    for place in range(len(weights)):
        running = running + max(0, weights[place])
        if point < running:
            return place
    return len(weights) - 1


def _digest(text: str) -> int:
    """A 64-bit digest of a text (SplitMix64 over its characters), for the zone's sets of values written."""
    state = _GOLDEN
    for character in text:
        state = _mixed(state ^ ord(character))
    return state


# -- reading a cell ------------------------------------------------------------------------------------


def _text(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell


def _is_digit(character: str) -> bool:
    return "0" <= character <= "9"


def _is_ascii_letter(character: str) -> bool:
    return "a" <= character <= "z" or "A" <= character <= "Z"


_SPACES = frozenset(" \t\n\r\x0b\x0c\xa0            "
                    "    　")
# Characters past ASCII read as marks, not letters, in a run of letters.
_MARKS_ABOVE_ASCII = frozenset("\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6"
                               "\xb7\xb8\xb9\xbb\xbc\xbd\xbe\xbf\xd7\xf7‐‑‒–—―‘"
                               "’‚“”„†‡•…‰′″‹›"
                               "€™←↑→↓−≤≥﻿")


def _is_space(character: str) -> bool:
    return character in _SPACES


def _is_letter(character: str) -> bool:
    """A letter of a word: an ASCII letter, or any character past ASCII that is no space and no common mark."""
    if _is_ascii_letter(character):
        return True
    return ord(character) > 127 and character not in _SPACES and character not in _MARKS_ABOVE_ASCII


def _lowered(word: str) -> str:
    """A word in small letters (`parsing.folded`, the package's one folding rule)."""
    return parsing.folded(word)


def _sign_may_open(tokens: "list[tuple[str, str]]") -> bool:
    """Whether a minus or plus before a figure here is a number's sign: at the start, after a space or an opening mark."""
    if not tokens:
        return True
    kind, written = tokens[len(tokens) - 1]
    return kind == "s" or (kind == "o" and written in "([{=:,;<>~")


def word_tokens(text: str) -> "list[tuple[str, str]]":
    """A cell as words, numbers, runs of space and single marks: ('w', word), ('n', number), ('s', space), ('o', mark).

    A number is a run of figures with its sign where one may open
    (`_sign_may_open`) and its figures after one point, unless the point
    is one of a dotted chain (`192.0.2.12`, `1.2.3`), whose runs stay
    apart. Raises TypeError for anything but text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    tokens: "list[tuple[str, str]]" = []
    count = len(text)
    at = 0
    while at < count:
        character = text[at]
        signed = (character == "-" or character == "+") and at + 1 < count and _is_digit(text[at + 1]) and \
            _sign_may_open(tokens)
        if _is_digit(character) or signed:
            end = at + 1
            while end < count and _is_digit(text[end]):
                end = end + 1
            dotted_before = at >= 2 and text[at - 1] == "." and _is_digit(text[at - 2])
            if end + 1 < count and text[end] == "." and _is_digit(text[end + 1]) and not dotted_before:
                after = end + 1
                while after < count and _is_digit(text[after]):
                    after = after + 1
                if not (after + 1 < count and text[after] == "." and _is_digit(text[after + 1])):
                    end = after
            tokens += [("n", text[at:end])]
            at = end
            continue
        if _is_letter(character):
            end = at + 1
            while end < count and _is_letter(text[end]):
                end = end + 1
            tokens += [("w", text[at:end])]
            at = end
            continue
        if _is_space(character):
            end = at + 1
            while end < count and _is_space(text[end]):
                end = end + 1
            tokens += [("s", text[at:end])]
            at = end
            continue
        tokens += [("o", character)]
        at = at + 1
    return tokens


def _run_style(cells: "list[str]") -> str:
    """How a column of keys is cut into runs: 'b64' (one base-64 run a cell), 'hex' (runs of hexadecimal) or 'plain'."""
    seen = 0
    base64 = 0
    hexadecimal = 0
    mixed_hex = 0
    for cell in cells:
        if not cell:
            continue
        seen = seen + 1
        body = cell
        while body[len(body) - 1:] == "=":
            body = body[: len(body) - 1]
        classes = 0
        lower = upper = digit = False
        only64 = len(body) >= 16 and len(cell) % 4 == 0
        only_hex = True
        alnum_run_mixed = False
        run_letter = run_digit = False
        for character in body:
            if "a" <= character <= "z":
                lower = True
            elif "A" <= character <= "Z":
                upper = True
            elif _is_digit(character):
                digit = True
            elif character != "+" and character != "/":
                only64 = False
            if not (_is_digit(character) or "a" <= character <= "f" or "A" <= character <= "F"):
                if _is_ascii_letter(character):
                    only_hex = False
                run_letter = run_digit = False
            elif _is_digit(character):
                run_digit = True
            else:
                run_letter = True
            if run_letter and run_digit:
                alnum_run_mixed = True
        classes = (1 if lower else 0) + (1 if upper else 0) + (1 if digit else 0)
        if only64 and classes >= 3:
            base64 = base64 + 1
        if only_hex:
            hexadecimal = hexadecimal + 1
            if alnum_run_mixed:
                mixed_hex = mixed_hex + 1
    if seen and base64 * 10 >= seen * 9:
        return "b64"
    if seen and hexadecimal == seen and mixed_hex * 2 >= seen:
        return "hex"
    return "plain"


def _key_shaped(cells: "list[str]") -> bool:
    """Whether nine cells in ten are keys: letters and figures, a run of four figures or more, joined by `-`, `_` or `/` alone."""
    seen = 0
    keys = 0
    for cell in cells:
        if not cell:
            continue
        seen = seen + 1
        figures = False
        shaped = True
        for kind, written in run_tokens(cell, "plain"):
            if kind == "d" and len(written) >= 4:
                figures = True
            elif kind == "o" and written not in ("-", "_", "/"):
                shaped = False
            elif kind == "s":
                shaped = False
        if shaped and figures:
            keys = keys + 1
    return seen > 0 and keys * 10 >= seen * 9


def run_tokens(text: str, style: str) -> "list[tuple[str, str]]":
    """A key cut into runs: ('d', figures), ('l', letters), ('h', hexadecimal), ('b', base 64), ('s', space), ('o', mark).

    Raises TypeError for anything but text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    tokens: "list[tuple[str, str]]" = []
    count = len(text)
    if style == "b64":
        body = text
        while body[len(body) - 1:] == "=":
            body = body[: len(body) - 1]
        if body:
            tokens += [("b", body)]
        for _place in range(count - len(body)):
            tokens += [("o", "=")]
        return tokens
    at = 0
    while at < count:
        character = text[at]
        if style == "hex" and (_is_digit(character) or "a" <= character <= "f" or "A" <= character <= "F"):
            end = at + 1
            while end < count and (_is_digit(text[end]) or "a" <= text[end] <= "f" or "A" <= text[end] <= "F"):
                end = end + 1
            tokens += [("h", text[at:end])]
            at = end
            continue
        if _is_digit(character):
            end = at + 1
            while end < count and _is_digit(text[end]):
                end = end + 1
            tokens += [("d", text[at:end])]
            at = end
            continue
        if _is_letter(character):
            end = at + 1
            while end < count and _is_letter(text[end]) and not _is_digit(text[end]):
                end = end + 1
            tokens += [("l", text[at:end])]
            at = end
            continue
        if _is_space(character):
            end = at + 1
            while end < count and _is_space(text[end]):
                end = end + 1
            tokens += [("s", text[at:end])]
            at = end
            continue
        tokens += [("o", character)]
        at = at + 1
    return tokens


def _joined(pieces: "list[str]", mark: str) -> str:
    """Pieces of text joined by a mark, written out (the offline audit reads a join of computed text as untraced)."""
    text = ""
    for place in range(len(pieces)):
        text = text + (mark if place else "") + f"{pieces[place]}"
    return text


def _padded(figures: str, width: int) -> str:
    """Figures with noughts in front up to a width."""
    while len(figures) < width:
        figures = "0" + figures
    return figures


def _holds_a_mark(text: str) -> bool:
    for character in text:
        if character in _MARKS:
            return True
    return False


# -- numbers ---------------------------------------------------------------------------------------------


def _number_parts(written: str) -> "tuple[str, str, str]":
    """A number token's sign, whole figures and figures after the point."""
    if not isinstance(written, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    sign = ""
    body = written
    if body[:1] == "-" or body[:1] == "+":
        sign = body[:1]
        body = body[1:]
    point = body.find(".")
    if point < 0:
        return sign, body, ""
    return sign, body[:point], body[point + 1:]


def _number_key(written: str) -> str:
    """A number slot's key: its figures after the point, and its whole width where it opens with a nought."""
    _sign, whole, after = _number_parts(written)
    padded = len(whole) if len(whole) > 1 and whole[:1] == "0" else 0
    return f"{len(after)}.{padded}"


def _number_value(written: str) -> float:
    sign, whole, after = _number_parts(written)
    value = float(int(whole or "0"))
    if after:
        value = value + int(after) / (10 ** len(after))
    return -value if sign == "-" else value


def _written_number(value: float, key: str, signed_plus: bool) -> str:
    """A number written with the slot's figures after the point and its padded width."""
    if not isinstance(key, str):
        raise TypeError("internal check: a slot's key is text")
    point = key.find(".")
    after = int(key[:point])
    padded = int(key[point + 1:])
    negative = value < 0
    magnitude = -value if negative else value
    scale = 10 ** after
    units = int(magnitude * scale + 0.5)
    whole = f"{units // scale}"
    while len(whole) < padded:
        whole = "0" + whole
    text = whole + ("." + _padded(f"{units % scale}", after) if after else "")
    if negative and units > 0:
        return "-" + text
    if negative and units == 0:
        return "-" + text
    return ("+" + text) if signed_plus and units > 0 else text


# -- the dates a template holds ---------------------------------------------------------------------------


def _month_of(word: str) -> int:
    """A month's number from its name, or from one or two figures 1 to 12; 0 for anything else."""
    if word and len(word) <= 2 and parsing.is_digit_text(word):
        value = int(word)
        return value if 1 <= value <= 12 else 0
    return date_counts.month_word(word)


def _named_month(word: str) -> int:
    """A month's number from its name alone (`date_counts.month_word`: English, short or full, and six languages more)."""
    return date_counts.month_word(word)


def _figures_dated(tokens: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
    """A cell's tokens with its first date in figures as three slots (`2023-01-05`, `01/05/2023`, `5.3.2023`); else as they are.

    Three runs of figures behind one mark, the same both times (`-`, `/`
    or `.`): year, month and day, or a day and a month either way round
    (month first where both could be) and a year of four figures, naming
    a day of the calendar.
    """
    for place in range(len(tokens) - 4):
        kinds = [tokens[place + at][0] for at in range(5)]
        if kinds != ["n", "o", "n", "o", "n"]:
            continue
        mark = tokens[place + 1][1]
        if mark != tokens[place + 3][1] or mark not in ("-", "/", "."):
            continue
        first, second, third = tokens[place][1], tokens[place + 2][1], tokens[place + 4][1]
        if not (parsing.is_digit_text(first) and parsing.is_digit_text(second) and parsing.is_digit_text(third)):
            continue
        roles: "tuple[str, str, str]" = ("", "", "")
        if _a_year(first) and _month_of(second) and _a_day(third):
            roles = ("dy", "dm", "dd")
        elif _a_year(third) and len(first) <= 2 and len(second) <= 2:
            if _a_day(first) > 12 and _month_of(second):
                roles = ("dd", "dm", "dy")
            elif _month_of(first) and _a_day(second):
                roles = ("dm", "dd", "dy")
        if not roles[0]:
            continue
        values = {roles[0]: first, roles[1]: second, roles[2]: third}
        if not parsing.valid_date(_a_year(values["dy"]), _month_of(values["dm"]), _a_day(values["dd"])):
            continue
        changed = [token for token in tokens]
        changed[place] = (roles[0], first)
        changed[place + 2] = (roles[1], second)
        changed[place + 4] = (roles[2], third)
        return changed
    return tokens


def _days_in(year: int, month: int) -> int:
    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return 29 if leap else 28
    return 30 if month in (4, 6, 9, 11) else 31


def _weekday(year: int, month: int, day: int) -> int:
    """Monday 0 to Sunday 6 (Zeller's congruence)."""
    if month < 3:
        month = month + 12
        year = year - 1
    zeller = (day + (13 * (month + 1)) // 5 + year + year // 4 - year // 100 + year // 400) % 7
    return (zeller + 5) % 7


def _a_day(written: str) -> int:
    if not written or len(written) > 2 or not parsing.is_digit_text(written):
        return 0
    value = int(written)
    return value if 1 <= value <= 31 else 0


def _a_year(written: str) -> int:
    if len(written) != 4 or not parsing.is_digit_text(written):
        return 0
    value = int(written)
    return value if 1900 <= value <= 2099 else 0


def _between_parts(tokens: "list[tuple[str, str]]", start: int, end: int) -> bool:
    """Whether the tokens strictly between two places are only spaces, marks and a date's filler words, at most four."""
    if end - start - 1 > 4:
        return False
    for place in range(start + 1, end):
        kind, written = tokens[place]
        if kind == "n":
            return False
        if kind == "w" and _lowered(written) not in _DATE_FILLERS:
            return False
    return True


def dated(tokens: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
    """A cell's tokens with EVERY date as three slots: ('dd', day), ('dm', month), ('dy', year); else as they are.

    `_first_dated` again until no date is left (batch 4zz's fix round, the
    outside review's item 5: only a note's first date was made up, and a
    second, `discharge 2023-01-20`, kept its real figures as numbers).
    """
    for _round in range(len(tokens) + 1):
        changed = _first_dated(tokens)
        if changed == tokens:
            return tokens
        tokens = changed
    return tokens


def _first_dated(tokens: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
    """A cell's tokens with its first date not yet read as three slots: ('dd', day), ('dm', month), ('dy', year).

    A month's name (`date_counts.month_word`) with a day of one or two figures and a
    year of four (1900 to 2099) beside it, apart only by spaces, marks
    and a date's filler words (`5 mars 2023`, `5. März 2023`, `5 de marzo
    de 2023`, `March 5, 2023`), naming a day of the calendar.
    """
    for place in range(len(tokens)):
        kind, written = tokens[place]
        if kind != "w" or not _named_month(written):
            continue
        month = _named_month(written)
        numbers = [at for at in range(max(0, place - 5), min(len(tokens), place + 6)) if tokens[at][0] == "n"]
        before = [at for at in numbers if at < place]
        after = [at for at in numbers if at > place]
        pairs: "list[tuple[int, int]]" = []
        if before and after:
            pairs += [(before[len(before) - 1], after[0])]
        if len(after) >= 2:
            pairs += [(after[0], after[1])]
        for day_at, year_at in pairs:
            day = _a_day(tokens[day_at][1])
            year = _a_year(tokens[year_at][1])
            if not day or not year or not parsing.valid_date(year, month, day):
                continue
            low = min(day_at, place)
            high = max(day_at, place)
            if not _between_parts(tokens, low, high) or not _between_parts(tokens, min(place, year_at),
                                                                              max(place, year_at)):
                continue
            changed = [token for token in tokens]
            changed[day_at] = ("dd", tokens[day_at][1])
            changed[place] = ("dm", written)
            changed[year_at] = ("dy", tokens[year_at][1])
            return changed
    return _figures_dated(tokens)


# -- learning a column -----------------------------------------------------------------------------------


# The forms of a cell the twin checks read as a telephone number or a person's name (`taxonomy.identifier_words_form`):
# a cell of words holding one is learned as no template and no chain (batch 4zz's fix round, the outside review's items
# 3 and 4: a note's telephone number was drawn back from its figures' census, and a titled name kept as a word).
_NAMES_OR_CALLS = ("a telephone number", "a title before a name", "a family name and an initial",
                   "a family name and a given name", "a name after a word naming a relative")


def _names_or_calls(cell: str) -> bool:
    """Whether a cell of words writes a telephone number or a person's name as the twin checks read them (C4)."""
    from synthtwin import taxonomy

    return taxonomy.identifier_words_form(cell, False) in _NAMES_OR_CALLS


def _rows_read(count: int) -> "list[int]":
    """The rows a column's templates are learned from: every row, or `SAMPLE_CAP` at an even stride."""
    if count <= SAMPLE_CAP:
        return [row for row in range(count)]
    return [(place * count) // SAMPLE_CAP for place in range(SAMPLE_CAP)]


def _people_add(held: "dict[str, list[int]]", key: str, person: int, floor: int) -> None:
    """Count one more person beside a key, up to `floor` different ones (the rest need not be told apart)."""
    if key not in held:
        held[key] = [person]
        return
    known = held[key]
    if len(known) >= floor or person in known:
        return
    held[key] = known + [person]


def _word_key(tokens: "list[tuple[str, str]]", kept: "set[str]") -> "tuple[str, list[tuple[str, str]]]":
    """A cell's template key under the kept words, and its slots in order: ('n', number), ('w', word), ('dd'|'dm'|'dy', ...)."""
    parts: "list[str]" = []
    slots: "list[tuple[str, str]]" = []
    for kind, written in tokens:
        if kind == "n":
            parts += [_NUM + _number_key(written)]
            slots += [("n", written)]
        elif kind == "w" and written not in kept:
            parts += [_WORD]
            slots += [("w", written)]
        elif kind == "dd" or kind == "dm" or kind == "dy":
            parts += [_DATE + kind]
            slots += [(kind, written)]
        else:
            parts += [_LIT + written]
    return _joined(parts, _SEP), slots


def _run_key(tokens: "list[tuple[str, str]]", kept: "set[str]") -> "tuple[str, list[tuple[str, str]]]":
    """A key's template under the kept letter runs, and its runs in order as slots."""
    parts: "list[str]" = []
    slots: "list[tuple[str, str]]" = []
    for kind, written in tokens:
        if kind == "o" or kind == "s" or (kind == "l" and written in kept):
            parts += [_LIT + written]
        else:
            parts += [_RUN + kind + f"{len(written)}"]
            slots += [(kind, written)]
    return _joined(parts, _SEP), slots


def _grid(values: "list[float]") -> "list[float]":
    ordered = sorted(values)
    last = len(ordered) - 1
    return [ordered[(point * last) // (GRID - 1)] for point in range(GRID)]


def _number_slot(written: "list[str]") -> "dict[str, object]":
    """A number slot: its key, whether its gains carry a plus, and its census or its quantile grid."""
    counts: "dict[str, int]" = {}
    for each in written:
        counts[each] = (counts[each] if each in counts else 0) + 1
    plus = False
    for each in counts:
        if each[:1] == "+":
            plus = True
    slot: "dict[str, object]" = {"k": "n", "key": _number_key(written[0]), "plus": plus}
    if len(counts) <= CENSUS_CAP:
        ordered = sorted((_number_value(each), each) for each in counts)
        slot["census"] = [[each, counts[each]] for _value, each in ordered]
    else:
        slot["grid"] = _grid([_number_value(each) for each in written])
    return slot


def _word_slot(written: "list[str]") -> "dict[str, object]":
    """A made-up word's slot: the lengths its real words take, their case and the letters they are made of."""
    lengths: "dict[str, int]" = {}
    cases: "dict[str, int]" = {}
    letters: "set[str]" = set()
    for each in written:
        size = f"{len(each)}"
        lengths[size] = (lengths[size] if size in lengths else 0) + 1
        case = _case_of(each)
        cases[case] = (cases[case] if case in cases else 0) + 1
        for character in each:
            if not _is_ascii_letter(character):
                letters |= {character}
    return {"k": "w", "lengths": lengths, "cases": cases, "letters": _joined(sorted(letters), "")[:64]}


def _case_of(word: str) -> str:
    upper = lower = 0
    for character in word:
        if "A" <= character <= "Z":
            upper = upper + 1
        elif "a" <= character <= "z":
            lower = lower + 1
    if upper and not lower:
        return "upper"
    if word[:1] and "A" <= word[:1] <= "Z" and upper == 1:
        return "title"
    return "lower"


def _rank_of(slot: "dict[str, object]", written: str) -> int:
    """A number's rank in its slot, 0 to `RANK`."""
    value = _number_value(written)
    if "census" in slot:
        census = typing.cast("list[list[object]]", slot["census"])
        total = 0
        below = 0
        found = 0
        for each, count in census:
            weight = int(f"{count}")
            if _number_value(f"{each}") < value:
                below = below + weight
            elif f"{each}" == written:
                found = weight
            total = total + weight
        return (RANK * (2 * below + found)) // max(1, 2 * total)
    grid = typing.cast("list[float]", slot["grid"])
    low = 0
    high = len(grid)
    while low < high:
        middle = (low + high) // 2
        if grid[middle] < value:
            low = middle + 1
        else:
            high = middle
    return min(RANK, (RANK * low) // max(1, len(grid) - 1))


def _calendar(rows: "list[list[tuple[str, str]]]") -> "dict[str, object]":
    """A date slot's counts by year, month and weekday, the month's own spelling and whether days are padded.

    Every date of a row is counted (each its three slots), and NONE IN A
    YEAR AT OR BEFORE THE YEAR CUT (`taxonomy.year_cutoff` of the
    reference year, 1937 for 2027; batch 4zz's fix round, the outside
    review's item 6: a held birth date `15 mars 1910` was written again in
    1910, a year that shows an age over 89), so no date is drawn in one.
    """
    from synthtwin import taxonomy

    cut = taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR)
    cells: "dict[str, int]" = {}
    spellings: "dict[str, dict[str, int]]" = {}
    padded = 0
    short = 0
    for slots in rows:
        day = month = year = 0
        word = ""
        for kind, written in slots:
            if kind == "dd":
                day = _a_day(written)
                if day < 10:
                    if len(written) == 2:
                        padded = padded + 1
                    else:
                        short = short + 1
            elif kind == "dm":
                month = _month_of(written)
                word = written
            elif kind == "dy":
                year = _a_year(written)
            if not (day and month and year):
                continue
            if year > cut:
                key = f"{year}.{month}.{_weekday(year, month, day)}"
                cells[key] = (cells[key] if key in cells else 0) + 1
                name = f"{month}"
                if name not in spellings:
                    spellings[name] = {}
                known = spellings[name]
                known[word] = (known[word] if word in known else 0) + 1
            day = month = year = 0
            word = ""
    months: "dict[str, str]" = {}
    for name in spellings:
        known = spellings[name]
        months[name] = sorted((-known[each], each) for each in known)[0][1]
    # ...and where no day below ten was seen, a day is padded as the months are: two figures where every month is
    # written in two (`2023-03-15` beside no early day; batch 4zz's fix round, the outside review's item 14: 416 of
    # 1,000 dates were written `2023-03-1`, which an ISO reader refuses).
    if padded == 0 and short == 0 and months:
        padded = 1 if all(len(months[name]) == 2 and parsing.is_digit_text(months[name]) for name in months) else 0
    return {"cells": cells, "months": months, "padded": padded > short}


def _template(rows: "list[list[tuple[str, str]]]", count: int) -> "dict[str, object]":
    """A template's slots learned from the slots of the rows that wear it."""
    width = len(rows[0])
    slots: "list[dict[str, object]]" = []
    for place in range(width):
        kind = rows[0][place][0]
        written = [row[place][1] for row in rows]
        if kind == "n":
            slots += [_number_slot(written)]
        elif kind == "w":
            slots += [_word_slot(written)]
        else:
            slots += [{"k": kind}]
    joint: "list[list[int]]" = []
    numbered = [place for place in range(width) if slots[place]["k"] == "n"]
    if numbered:
        stride = max(1, len(rows) // JOINT_CAP)
        for at in range(0, len(rows), stride):
            if len(joint) >= JOINT_CAP:
                break
            joint += [[_rank_of(slots[place], rows[at][place][1]) for place in numbered]]
    entry: "dict[str, object]" = {"rows": count, "slots": slots, "joint": joint}
    if any(kind in ("dd", "dm", "dy") for kind, _written in rows[0]):
        entry["calendar"] = _calendar(rows)
    return entry


def _free_chain(free: "list[list[tuple[str, str]]]", kept: "set[str]") -> "dict[str, object]":
    """The chain the free cells are drawn from: two tokens of context, kept words and marks as written, slots as kinds."""
    follow: "dict[str, dict[str, int]]" = {}
    numbers: "dict[str, list[str]]" = {}
    words: "list[str]" = []
    for tokens in free[:FREE_CAP]:
        before = _START
        last = _START
        for kind, written in tokens[:TOKENS_CAP]:
            if kind == "n" or kind == "dd" or kind == "dy":
                symbol = _NUM + _number_key(written)
                if symbol not in numbers:
                    numbers[symbol] = []
                if len(numbers[symbol]) < SLOT_SAMPLE:
                    numbers[symbol] += [written]
            elif (kind == "w" or kind == "dm") and written not in kept:
                symbol = _WORD
                if len(words) < SLOT_SAMPLE:
                    words += [written]
            else:
                symbol = _LIT + written
            context = before + _SEP + last
            if context not in follow:
                follow[context] = {}
            known = follow[context]
            known[symbol] = (known[symbol] if symbol in known else 0) + 1
            before = last
            last = symbol
        context = before + _SEP + last
        if context not in follow:
            follow[context] = {}
        known = follow[context]
        known[_END] = (known[_END] if _END in known else 0) + 1
    slots: "dict[str, object]" = {}
    for symbol in numbers:
        slots[symbol] = _number_slot(numbers[symbol])
    chain: "dict[str, object]" = {"follow": follow, "numbers": slots}
    if words:
        chain["word"] = _word_slot(words)
    return chain


def entry_of(cells: "list[str]", mode: str, keep: "list[str]", persons: "list[int] | None", floor: int,
             held: "list[bool] | None" = None) -> "dict[str, object] | None":
    """One column's entry of the text zone, read from its real cells; None where no template is worth keeping.

    ``mode`` is one of `MODES`; ``keep`` the spellings the description's
    twin writes and the zone leaves as they are (its published levels'
    spellings, its missing spellings; '' always); ``persons`` each row's
    person (or None: each row its own); ``floor`` the description's
    smallest group; ``held``, for `MODE_HELD`, which cells the
    description read as dates in disguise and held. The real cells are
    read here, inside, and only the zone's model of them is returned.
    Raises TypeError for a cell that is not text; nothing else.
    """
    if mode not in MODES:
        return None
    if mode == MODE_CENSUS:
        return _census_entry(cells, keep)
    if mode == MODE_DETAIL:
        return _detail_entry(cells, keep, persons, floor)
    kept_spellings = set(keep) | {""}
    rows = len(cells)
    values: "list[int]" = []
    present = 0
    for row in range(rows):
        cell = _text(cells[row])
        if parsing.trimmed(cell):
            present = present + 1
        if mode == MODE_HELD:
            if held is not None and row < len(held) and held[row]:
                values += [row]
        elif cell not in kept_spellings and parsing.trimmed(cell):
            values += [row]
    if not values:
        return None
    read = [values[place] for place in _rows_read(len(values))]
    if mode == MODE_TAIL:
        listed = _list_facts(cells, values, persons, floor)
        if listed is not None:
            return {
                "mode": mode, "style": "words", "rows": rows, "values": len(values), "present": present,
                "read": len(read), "keep": _joined(sorted(kept_spellings), _SEP), "kept": "", "templates": {},
                "list": listed,
            }
    style = "words"
    if mode == MODE_IDENTIFIER:
        style = _run_style([cells[row] for row in read[:2000]])
    elif mode == MODE_FREE:
        spaced = 0
        different: "set[str]" = set()
        for row in read[:2000]:
            for character in cells[row]:
                if _is_space(character):
                    spaced = spaced + 1
                    break
            different |= {cells[row]}
        if spaced == 0 and len(different) * 2 >= min(2000, len(read)):
            found_style = _run_style([cells[row] for row in read[:2000]])
            # ...a token of base 64 or hexadecimal alone, or a key's letters and figures (`P2162179`, `S23-012345`),
            # is written as record numbers, off the real; marks and words between numbers (`sys=141;dia=74`) stay words.
            if found_style != "plain" or _key_shaped([cells[row] for row in read[:2000]]):
                style = found_style
    # THE WORDS KEPT: a run of letters `floor` different people write.
    people: "dict[str, list[int]]" = {}
    written_times: "dict[str, int]" = {}
    tokens_of: "list[list[tuple[str, str]]]" = []
    for row in read:
        cell = cells[row]
        if _holds_a_mark(cell) or (style == "words" and _names_or_calls(cell)):
            tokens_of += [[]]
            continue
        tokens = word_tokens(cell) if style == "words" else run_tokens(cell, style)
        if style == "words":
            tokens = dated(tokens)
        tokens_of += [tokens]
        person = persons[row] if persons is not None and row < len(persons) else row
        for kind, written in tokens:
            if kind == "w" or kind == "l":
                _people_add(people, written, person, floor)
                written_times[written] = (written_times[written] if written in written_times else 0) + 1
    # ...at most `KEPT_WORDS` of them, the most written first (a word past them is made up where it stands).
    ranked = sorted((-written_times[word], word) for word in people if len(people[word]) >= floor)
    kept: "set[str]" = {word for _times, word in ranked[:KEPT_WORDS]}
    # THE TEMPLATES: a key `floor` different people wear.
    holders: "dict[str, list[int]]" = {}
    worn: "dict[str, int]" = {}
    slotted: "dict[str, list[list[tuple[str, str]]]]" = {}
    keys: "list[str]" = []
    for place in range(len(read)):
        tokens = tokens_of[place]
        if not tokens:
            keys += [""]
            continue
        key, slots = _word_key(tokens, kept) if style == "words" else _run_key(tokens, kept)
        keys += [key]
        row = read[place]
        person = persons[row] if persons is not None and row < len(persons) else row
        _people_add(holders, key, person, floor)
        worn[key] = (worn[key] if key in worn else 0) + 1
        if key not in slotted:
            slotted[key] = []
        if len(slotted[key]) < SLOT_SAMPLE:
            slotted[key] += [slots]
    templates: "dict[str, object]" = {}
    covered = 0
    for key in sorted(worn):
        if not key or len(holders[key]) < floor:
            continue
        if mode == MODE_TAIL and _WORD in key:
            continue
        built = _template(slotted[key], worn[key])
        # ...a template whose dates all lie at or before the year cut draws none: not kept (its cells are left).
        if "calendar" in built and not typing.cast("dict[str, object]", built["calendar"])["cells"]:
            continue
        templates[key] = built
        covered = covered + worn[key]
    if mode == MODE_TAIL and covered < TAIL_SHARE * len(read):
        return None
    entry: "dict[str, object]" = {
        "mode": mode, "style": style, "rows": rows, "values": len(values), "present": present, "read": len(read),
        "keep": _joined(sorted(kept_spellings), _SEP), "kept": _joined(sorted(kept), _SEP), "templates": templates,
    }
    if mode == MODE_IDENTIFIER or style != "words":
        if not templates:
            return None
        _identifier_facts(entry, cells, values, style, kept, floor, persons)
        entry["longest"] = max(len(cells[row]) for row in values)
        return entry
    free_at = [place for place in range(len(read)) if keys[place] and keys[place] not in templates]
    if free_at and mode != MODE_TAIL:
        entry["free"] = _free_chain([tokens_of[place] for place in free_at], kept)
        # ...and the free cells' own lengths, which a free value of the twin is drawn at (the description's twin packs
        # its lengths to four published facts, not to the real spread).
        entry["free_lengths"] = [int(each) for each in _grid([float(len(cells[read[place]])) for place in free_at])]
    if not templates and "free" not in entry:
        return None
    entry["openings"] = _openings(cells, values) if _openings(cells, read) else {}
    return entry


# -- a person's details ------------------------------------------------------------------------------------


def _detail_entry(cells: "list[str]", keep: "list[str]", persons: "list[int] | None",
                  floor: int) -> "dict[str, object] | None":
    """A person's detail column's entry (`MODE_DETAIL`): its real layouts, every word that could name somebody a slot.

    THE LEAK IT REPLACES THE FILLER OF (lane LEDGER, HIPAA; release 36):
    street addresses, e-mail addresses and telephone numbers written in
    their real templates, every word the floor's people write kept and
    every number drawn inside the real ends, reproduced 1,548 real
    addresses and 72 real e-mail addresses in the twin; release 36 left
    such a column the description's filler, so code that parses it found
    nothing. Here a word is kept as written only where it is the
    column's layout (`_detail_kept`: a word of `DETAIL_VOCABULARY`, a
    label of a reserved domain, a word half the rows write outside any
    host or mail domain); every other word is a slot the twin fills from
    the column's own `NEUTRAL_WORDS` (`_neutral_left`: those no real
    cell writes), and every template keeps its cells off every real one
    by a piece no real cell holds (`_detail_options`): such a made-up
    word, a long run of figures opening with a figure no real run of its
    width opens with, or a short number no real cell of the template
    holds there -- a telephone number's area code and exchange always
    (`_telephone_templates`). Cells without spaces read as keys
    (`P0001234-03`) are written as record numbers off the real by their
    mark (`_identifier_facts`), their layout's letters kept as above.
    Raises TypeError for a cell that is not text; nothing else.
    """
    kept_spellings = set(keep) | {""}
    rows = len(cells)
    values: "list[int]" = []
    present = 0
    for row in range(rows):
        cell = _text(cells[row])
        if parsing.trimmed(cell):
            present = present + 1
            if cell not in kept_spellings:
                values += [row]
    if not values:
        return None
    read = [values[place] for place in _rows_read(len(values))]
    style = "words"
    spaced = 0
    different: "set[str]" = set()
    for row in read[:2000]:
        for character in cells[row]:
            if _is_space(character):
                spaced = spaced + 1
                break
        different |= {cells[row]}
    sample = [cells[row] for row in read[:2000]]
    if spaced == 0 and len(different) * 2 >= min(2000, len(read)) and not _telephones(sample[:400]):
        found_style = _run_style(sample)
        if found_style != "plain" or _key_shaped(sample):
            style = found_style
    people: "dict[str, list[int]]" = {}
    rows_with: "dict[str, int]" = {}
    hosted: "set[str]" = set()
    reserved: "set[str]" = set()
    # ...a host's or mail domain's naming labels (every label but its last and a leading `www`, under no reserved
    # name): never kept, a word of `DETAIL_VOCABULARY` among them (the outside review of release 37, item 1).
    named: "set[str]" = set()
    tokens_of: "list[list[tuple[str, str]]]" = []
    for row in read:
        cell = cells[row]
        if _holds_a_mark(cell):
            tokens_of += [[]]
            continue
        tokens = dated(word_tokens(cell)) if style == "words" else run_tokens(cell, style)
        tokens_of += [tokens]
        person = persons[row] if persons is not None and row < len(persons) else row
        marks = _host_marks(tokens) if style == "words" else [0 for _token in tokens]
        seen_here: "set[str]" = set()
        for at in range(len(tokens)):
            kind, written = tokens[at]
            if kind != "w" and kind != "l":
                continue
            _people_add(people, written, person, floor)
            # ...a word counts toward the layout share only where it stands in a link's path or query (after `/`,
            # `?`, `&`, `=` or `#`, outside every host) or in a key: a word most rows of an address write (a street, a
            # city) is a place, not the layout (the outside review of release 37, item 1).
            placed = style != "words" or (marks[at] == 0 and at > 0 and tokens[at - 1][0] == "o"
                                          and tokens[at - 1][1] in _LINK_MARKS)
            if written not in seen_here and placed:
                seen_here |= {written}
                rows_with[written] = (rows_with[written] if written in rows_with else 0) + 1
            if marks[at] == 1 or marks[at] == 3:
                hosted |= {written}
            elif marks[at] == 2:
                reserved |= {written}
            if marks[at] == 3:
                named |= {written}
    kept = {word for word in _detail_kept(people, rows_with, hosted, reserved, floor, len(read)) if word not in named}
    holders: "dict[str, list[int]]" = {}
    worn: "dict[str, int]" = {}
    slotted: "dict[str, list[list[tuple[str, str]]]]" = {}
    for place in range(len(read)):
        tokens = tokens_of[place]
        if not tokens:
            continue
        key, slots = _word_key(tokens, kept) if style == "words" else _run_key(tokens, kept)
        row = read[place]
        _people_add(holders, key, persons[row] if persons is not None and row < len(persons) else row, floor)
        worn[key] = (worn[key] if key in worn else 0) + 1
        if key not in slotted:
            slotted[key] = []
        if len(slotted[key]) < SLOT_SAMPLE:
            slotted[key] += [slots]
    templates: "dict[str, object]" = {}
    for key in sorted(worn):
        if key and len(holders[key]) >= floor:
            templates[key] = _template(slotted[key], worn[key])
    if not templates:
        return None
    entry: "dict[str, object]" = {
        "mode": MODE_DETAIL, "style": style, "rows": rows, "values": len(values), "present": present,
        "read": len(read), "keep": _joined(sorted(kept_spellings), _SEP), "kept": _joined(sorted(kept), _SEP),
        "templates": templates,
    }
    if style != "words":
        _identifier_facts(entry, cells, values, style, kept, floor, persons)
        entry["longest"] = max(len(cells[row]) for row in values)
        return entry
    for key in sorted(templates):
        template = typing.cast("dict[str, object]", templates[key])
        if any(f"{slot['k']}" not in ("n", "w") for slot in typing.cast("list[dict[str, object]]", template["slots"])):
            del templates[key]
    if not templates:
        return None
    _absent_facts(typing.cast("dict[str, dict[str, object]]", templates), cells, values, kept, slotted)
    entry["openings"] = _openings(cells, values)
    entry["neutral"] = _neutral_left(cells)
    entry["real_runs"] = _joined(_runs_at_lengths(cells, {len(word) for word in typing.cast("list[str]", entry["neutral"])}),
                             _SEP)
    return entry


def _detail_kept(people: "dict[str, list[int]]", rows_with: "dict[str, int]", hosted: "set[str]",
                 reserved: "set[str]", floor: int, read: int) -> "set[str]":
    """The words a person's detail column keeps as written: each at least `floor` different people write, and a word
    of `DETAIL_VOCABULARY`, a label of a reserved domain seen in no other host, or a word `LAYOUT_SHARE` of the rows
    read write in a link's path or query or a key (`rows_with`), outside every host and mail domain (a host or a
    domain names a person's employer or their own site). A host's naming labels are set aside by the caller."""
    kept: "set[str]" = set()
    for word in people:
        if len(people[word]) < floor:
            continue
        layout = word in rows_with and rows_with[word] >= LAYOUT_SHARE * read and word not in hosted
        if _lowered(word) in DETAIL_VOCABULARY or layout or (word in reserved and word not in hosted):
            kept |= {word}
    return kept


def _host_marks(tokens: "list[tuple[str, str]]") -> "list[int]":
    """Each token's place in a web host or a mail domain: 0 outside one, 1 inside one, 2 inside one under a reserved
    name (`RESERVED_DOMAINS`, `RESERVED_TOP`: documentation names that are nobody's, read on each label whole), 3 in a
    naming label of one under no reserved name (every label but the last and a leading `www`: the name of an
    employer or a person's own site, never kept). A host opens after `://`, a mail domain after `@`, and `www.` opens
    one where it starts a word; each runs over words, numbers, `.` and `-`."""
    marks = [0 for _token in tokens]
    for place in range(len(tokens)):
        kind, written = tokens[place]
        start = -1
        if kind == "o" and written == "@":
            start = place + 1
        elif (kind == "o" and written == ":" and place + 2 < len(tokens) and tokens[place + 1] == ("o", "/")
              and tokens[place + 2] == ("o", "/")):
            start = place + 3
        elif (kind == "w" and _lowered(written) == "www" and place + 1 < len(tokens) and tokens[place + 1] == ("o", ".")
              and (place == 0 or tokens[place - 1][0] == "s")):
            start = place
        if start < 0:
            continue
        end = start
        while end < len(tokens) and (tokens[end][0] in ("w", "n") or tokens[end] == ("o", ".")
                                     or tokens[end] == ("o", "-")):
            end = end + 1
        # ...each label whole, its words, numbers and dashes together (the outside review of release 37, item 1:
        # `example1.com` read as `example.com` by its words alone, so a real domain was kept as a reserved one).
        labels: "list[str]" = []
        label_of: "list[int]" = []
        label = ""
        for at in range(start, end):
            if tokens[at] == ("o", "."):
                labels += [label]
                label = ""
            else:
                label = label + _lowered(tokens[at][1])
            label_of += [len(labels)]
        labels += [label]
        under = bool(labels) and (labels[len(labels) - 1] in RESERVED_TOP or (
            len(labels) >= 2 and (labels[len(labels) - 2], labels[len(labels) - 1]) in RESERVED_DOMAINS))
        last = len(labels) - 1
        for at in range(start, end):
            place = label_of[at - start]
            naming = not under and place != last and not (place == 0 and labels[0] == "www")
            marks[at] = max(marks[at], 2 if under else (3 if naming else 1))
    return marks


def _telephones(cells: "list[str]") -> bool:
    """Whether half or more of the cells read as telephone numbers to the twin checks (`taxonomy.identifier_words_form`)."""
    from synthtwin import taxonomy

    seen = 0
    calls = 0
    for cell in cells:
        if not parsing.trimmed(cell):
            continue
        seen = seen + 1
        if taxonomy.identifier_words_form(cell, False) == taxonomy.WORDS_TELEPHONE:
            calls = calls + 1
    return seen > 0 and calls * 2 >= seen


def _whole_widths(slot: "dict[str, object]") -> "set[int]":
    """The widths of a number slot's whole figures, over its census or its grid."""
    widths: "set[int]" = set()
    if "census" in slot:
        for each, _count in typing.cast("list[list[object]]", slot["census"]):
            widths |= {len(_number_parts(f"{each}")[1])}
        return widths
    key = f"{slot['key']}"
    for value in typing.cast("list[float]", slot["grid"]):
        widths |= {len(_number_parts(_written_number(value, key, False))[1])}
    return widths


def _absent_facts(templates: "dict[str, dict[str, object]]", cells: "list[str]", values: "list[int]", kept: "set[str]",
                  slotted: "dict[str, list[list[tuple[str, str]]]]") -> None:
    """THE SHORT NUMBERS NO REAL CELL HOLDS: for a telephone template, every whole number of three figures (its area
    code and its exchange: they name a place and a line, so the twin writes none a real number holds); for a template
    with no made-up word and no run of `OPENING_RUN` figures, its first whole number of at most `ABSENT_WIDTH` figures
    (`12 North St` beside kept words alone). The numbers each holds are read over every row, kept as a bitmap."""
    needs: "dict[str, list[int]]" = {}
    phones = _telephone_templates(templates, slotted)
    for key in sorted(templates):
        template = templates[key]
        slots = typing.cast("list[dict[str, object]]", template["slots"])
        template["phone"] = key in phones
        places: "list[int]" = []
        if key in phones:
            places = [at for at in range(len(slots)) if slots[at]["k"] == "n" and f"{slots[at]['key']}"[:2] == "0."
                      and _whole_widths(slots[at]) == {3}]
        elif not any(slot["k"] == "w" for slot in slots) and not any(
                slot["k"] == "n" and max(_whole_widths(slot)) >= OPENING_RUN for slot in slots):
            places = [at for at in range(len(slots)) if slots[at]["k"] == "n" and f"{slots[at]['key']}"[:2] == "0."
                      and max(_whole_widths(slots[at])) <= ABSENT_WIDTH][:1]
        if places:
            needs[key] = places
    if not needs:
        return
    # ...a telephone number's parts pooled over every telephone template of the column, by their order (the area
    # code no real number of the column holds, whether its line number opens with a nought or not).
    used: "dict[str, dict[int, set[int]]]" = {key: {at: set() for at in needs[key]} for key in needs}
    pooled: "dict[int, set[int]]" = {}
    for row in values:
        cell = cells[row]
        if _holds_a_mark(cell):
            continue
        key, slots_of = _word_key(dated(word_tokens(cell)), kept)
        if key not in needs:
            continue
        for order in range(len(needs[key])):
            at = needs[key][order]
            _sign, whole, _after = _number_parts(slots_of[at][1])
            if key in phones:
                pooled[order] = (pooled[order] if order in pooled else set()) | {int(whole or "0")}
            else:
                used[key][at] |= {int(whole or "0")}
    for key in needs:
        absent: "dict[str, str]" = {}
        for order in range(len(needs[key])):
            at = needs[key][order]
            held = (pooled[order] if order in pooled else set()) if key in phones else used[key][at]
            absent[f"{at}"] = _bitmap_of(held, 10 ** ABSENT_WIDTH)
        templates[key]["absent"] = absent


def _telephone_templates(templates: "dict[str, dict[str, object]]",
                         slotted: "dict[str, list[list[tuple[str, str]]]]") -> "set[str]":
    """The templates nine in ten of whose cells read as telephone numbers to the twin checks."""
    from synthtwin import taxonomy

    found: "set[str]" = set()
    for key in templates:
        parts = _parts_of(key)
        rows = slotted[key][:200]
        calls = 0
        for slots in rows:
            text = ""
            at = 0
            for part in parts:
                if part[:1] == _LIT:
                    text = text + part[1:]
                else:
                    text = text + slots[at][1]
                    at = at + 1
            if taxonomy.identifier_words_form(text, False) == taxonomy.WORDS_TELEPHONE:
                calls = calls + 1
        if rows and calls * 10 >= len(rows) * 9:
            found |= {key}
    return found


def _bitmap_of(numbers: "set[int]", size: int) -> str:
    """The numbers below `size` as a bitmap written in hexadecimal, four numbers a character."""
    figures = [0 for _place in range((size + 3) // 4)]
    for number in numbers:
        if 0 <= number < size:
            figures[number // 4] = figures[number // 4] | (1 << (number % 4))
    return _joined([_HEX_LOWER[figure] for figure in figures], "")


def _in_bitmap(bitmap: str, number: int) -> bool:
    """Whether a number is set in a bitmap of `_bitmap_of` (a number past it is not)."""
    if not isinstance(bitmap, str):
        raise TypeError("internal check: a bitmap is text")
    place = number // 4
    if number < 0 or place >= len(bitmap):
        return False
    return (int(bitmap[place:place + 1], 16) >> (number % 4)) & 1 == 1


def _neutral_left(cells: "list[str]") -> "list[str]":
    """The words of `NEUTRAL_WORDS` that no cell of the column writes as a run of letters, in any case: a twin cell
    holding one of them as a run of its own is no real cell (every row read, not a sample)."""
    pool = set(NEUTRAL_WORDS)
    found: "set[str]" = set()
    for cell in cells:
        text = _text(cell)
        start = -1
        for at in range(len(text) + 1):
            if at < len(text) and _is_letter(text[at]):
                if start < 0:
                    start = at
                continue
            if start >= 0:
                run = parsing.folded(text[start:at])
                if run in pool:
                    found |= {run}
                start = -1
    return [word for word in NEUTRAL_WORDS if word not in found]


def _runs_at_lengths(cells: "list[str]", lengths: "set[int]") -> "list[str]":
    """Every run of letters a cell of the column writes, folded, whose length is NONE of `lengths` (the lengths of the
    made-up words left to it), sorted: a word made up by running such words together and cutting it at another
    length is drawn again where it is one of these (`_neutral_drawn`; the outside review of release 37, item 2: on
    addresses whose street words were two letters long, 803 of 20,000 twin cells held a real street word). Kept in the
    inside record only."""
    found: "set[str]" = set()
    for cell in cells:
        text = _text(cell)
        start = -1
        for at in range(len(text) + 1):
            if at < len(text) and _is_letter(text[at]):
                if start < 0:
                    start = at
                continue
            if start >= 0 and at - start not in lengths:
                found |= {parsing.folded(text[start:at])}
            start = -1
    return sorted(found)


def _split_on(text: str, mark: str) -> "list[str]":
    """A text's pieces between each `mark` (read out here: the offline audit takes no mark it cannot trace)."""
    if not isinstance(text, str) or not isinstance(mark, str) or not mark:
        raise TypeError("internal check: a cell and its mark are text")
    pieces: "list[str]" = []
    start = 0
    at = 0
    width = len(mark)
    while at + width <= len(text):
        if text[at:at + width] == mark:
            pieces += [text[start:at]]
            at = at + width
            start = at
        else:
            at = at + 1
    return pieces + [text[start:]]


def _list_facts(cells: "list[str]", values: "list[int]", persons: "list[int] | None",
                floor: int) -> "dict[str, object] | None":
    """A label's tail of lists (`M54.5;I10;K21.9`, several codes a cell): the mark between items that `LIST_SHARE` of
    the tail's cells hold, each item `floor` different people write (in any cell of the column) with how many times it
    is written, whether a cell ever repeats an item or writes its items out of order, and how many items each different
    value of the tail holds, in the real order of the values (the commonest first); None where the items so kept are
    fewer than `LIST_SHARE` of the tail's."""
    tail: "list[str]" = []
    for row in values:
        tail += [_text(cells[row])]
    mark = ""
    for each in LIST_MARKS:
        holding = 0
        for cell in tail:
            if each in cell:
                holding = holding + 1
        if tail and holding >= LIST_SHARE * len(tail):
            mark = each
            break
    if not mark:
        return None
    people: "dict[str, list[int]]" = {}
    times: "dict[str, int]" = {}
    repeats = False
    in_order = True
    for row in range(len(cells)):
        cell = _text(cells[row])
        if not parsing.trimmed(cell):
            continue
        items = _split_on(cell, mark)
        person = persons[row] if persons is not None and row < len(persons) else row
        seen: "set[str]" = set()
        for place in range(len(items)):
            item = items[place]
            repeats = repeats or item in seen
            seen |= {item}
            in_order = in_order and not (place and items[place - 1] > item)
            _people_add(people, item, person, floor)
            times[item] = (times[item] if item in times else 0) + 1
    kept = {item for item in people if len(people[item]) >= floor and parsing.trimmed(item)}
    covered = 0
    total = 0
    counts: "dict[str, int]" = {}
    for cell in tail:
        counts[cell] = (counts[cell] if cell in counts else 0) + 1
        for item in _split_on(cell, mark):
            total = total + 1
            covered = covered + (1 if item in kept else 0)
    if not kept or covered < LIST_SHARE * total:
        return None
    runs: "list[list[int]]" = []
    for _count, cell in sorted((-counts[cell], cell) for cell in counts):
        size = len(_split_on(cell, mark))
        if runs and runs[len(runs) - 1][0] == size:
            runs[len(runs) - 1] = [size, runs[len(runs) - 1][1] + 1]
        else:
            runs += [[size, 1]]
    if len(runs) > LIST_RUNS:
        by_size: "dict[int, int]" = {}
        for size, run in runs:
            by_size[size] = (by_size[size] if size in by_size else 0) + run
        runs = [[size, by_size[size]] for size in sorted(by_size)]
    return {"mark": mark, "items": [[item, times[item]] for item in sorted(kept)], "sizes": runs,
            "repeats": repeats, "in_order": in_order}


def _census_entry(cells: "list[str]", keep: "list[str]") -> "dict[str, object] | None":
    """A measurement column's real spellings and how many cells write each (`MODE_CENSUS`); None past `CENSUS_SPELLINGS`."""
    kept_spellings = set(keep) | {""}
    counts: "dict[str, int]" = {}
    for cell in cells:
        text = _text(cell)
        if text in kept_spellings or not parsing.trimmed(text):
            continue
        counts[text] = (counts[text] if text in counts else 0) + 1
        if len(counts) > CENSUS_SPELLINGS:
            return None
    if not counts:
        return None
    ordered = sorted((_sort_value(each), each) for each in counts)
    return {"mode": MODE_CENSUS, "style": "census", "rows": len(cells), "keep": _joined(sorted(kept_spellings), _SEP),
            "kept": "",
            "templates": {}, "census": [[each, counts[each]] for _value, each in ordered],
            "values": sum(counts[each] for each in counts)}


def _sort_value(text: str) -> float:
    """A cell's number for the census's order: the whole cell read as a number, else its first number; past every
    number where it holds none."""
    whole = parsing.parse_number(text)
    if whole is not None:
        return whole
    for kind, written in word_tokens(text):
        if kind == "n":
            return _number_value(written)
    return 1e300


def _census_dealt(entry: "dict[str, object]", cells: "list[str]") -> "list[str] | None":
    """The twin's value cells dealt the real census in order: the least value the least spelling, so their order stands.

    The description's twin's cells of a measurement column are sorted by
    their number (each tie by its row), the real census is spread over as
    many cells as they are (each spelling its share, the largest
    remainders rounded up, in the census's order), and each cell takes the
    spelling of its place: the column then writes the real column's own
    spellings at the real column's own counts, and a row that held a
    larger number than another still does (the relations the inside record
    drew between columns stand). Blank cells and the kept spellings (the
    missing ones) stay where they are.
    """
    keep = _spellings_of(entry["keep"])
    census = typing.cast("list[list[object]]", entry["census"])
    places = [row for row in range(len(cells)) if _text(cells[row]) not in keep and parsing.trimmed(cells[row])]
    if not places or not census:
        return None
    total = 0
    for _each, count in census:
        total = total + int(f"{count}")
    wanted = len(places)
    shares = [(int(f"{count}") * wanted) // total for _each, count in census]
    left = wanted - sum(shares)
    order = sorted((-((int(f"{census[at][1]}") * wanted) % total), at) for at in range(len(census)))
    for _remainder, at in order[:left]:
        shares[at] = shares[at] + 1
    dealt: "list[str]" = []
    for at in range(len(census)):
        dealt += [f"{census[at][0]}"] * shares[at]
    ranked = sorted((_sort_value(cells[row]), row) for row in places)
    written = [cell for cell in cells]
    for place in range(len(ranked)):
        written[ranked[place][1]] = dealt[place]
    return written


def _openings(cells: "list[str]", values: "list[int]") -> "dict[str, str]":
    """For each width of a run of `OPENING_RUN` figures or more, the figures that open some real run of it (every row)."""
    found: "dict[str, set[str]]" = {}
    for row in values:
        cell = cells[row]
        run = 0
        for at in range(len(cell) + 1):
            if at < len(cell) and _is_digit(cell[at]):
                run = run + 1
                continue
            if run >= OPENING_RUN:
                width = f"{run}"
                if width not in found:
                    found[width] = set()
                found[width] |= {cell[at - run]}
            run = 0
    return {width: _joined(sorted(found[width]), "") for width in found}


def _identifier_facts(entry: "dict[str, object]", cells: "list[str]", values: "list[int]", style: str,
                      kept: "set[str]", floor: int, persons: "list[int] | None") -> None:
    """Each key template's places, census of short runs, check rules and the mark that keeps it off the real."""
    templates = typing.cast("dict[str, dict[str, object]]", entry["templates"])
    # The real values of every row, read once, for each template's mark.
    openings: "dict[str, dict[int, set[str]]]" = {}
    firsts: "dict[str, set[int]]" = {}
    # ...and every key of figures alone, read as a number, for a template no opening figure keeps off the real.
    numbers: "set[int]" = set()
    for row in values:
        cell = cells[row]
        if _holds_a_mark(cell):
            continue
        if cell and parsing.is_digit_text(cell):
            # ...read as a number at any width: a real `000201` is the number 201 (the outside review of release 37,
            # item 4: a key held only at six figures or more was left out, so a made-up `201` equalled it as read).
            lead = 0
            while lead < len(cell) - 1 and cell[lead:lead + 1] == "0":
                lead = lead + 1
            if len(cell) - lead <= ABSENT_KEY_WIDTH:
                numbers |= {int(cell[lead:])}
        key, slots = _run_key(run_tokens(cell, style), kept)
        if key not in templates:
            continue
        if key not in openings:
            openings[key] = {}
            firsts[key] = set()
        seen = openings[key]
        for place in range(len(slots)):
            kind, written = slots[place]
            if place not in seen:
                seen[place] = set()
            seen[place] |= {written[:1]}
            # ...and, for a template that may be an IPv4 address (four short runs of figures), its first numbers.
            if place == 0 and kind == "d" and len(slots) == 4 and len(written) <= 3:
                firsts[key] |= {int(written)}
    for key in templates:
        template = templates[key]
        learned = typing.cast("list[dict[str, object]]", template["slots"])
        template["slots"] = [{"k": "r", "class": f"{each['k']}"} for each in learned]
    for key in templates:
        _key_template(templates[key], key, cells, values, style, kept, floor, persons,
                      openings[key] if key in openings else {}, firsts[key] if key in firsts else set(), numbers)


def _class_alphabet(kind: str) -> str:
    if kind == "d":
        return _DIGITS
    if kind == "b":
        return _BASE64
    return ""


def _key_template(template: "dict[str, object]", key: str, cells: "list[str]", values: "list[int]", style: str,
                  kept: "set[str]", floor: int, persons: "list[int] | None", openings: "dict[int, set[str]]",
                  firsts: "set[int]", numbers: "set[int] | None" = None) -> None:
    slots = typing.cast("list[dict[str, object]]", template["slots"])
    # Each place's characters and each short run's census, from the rows read.
    sample: "list[list[tuple[str, str]]]" = []
    who: "list[int]" = []
    for row in _rows_read(len(values)):
        cell = cells[values[row]]
        if _holds_a_mark(cell):
            continue
        found, runs = _run_key(run_tokens(cell, style), kept)
        if found == key:
            sample += [runs]
            who += [persons[values[row]] if persons is not None and values[row] < len(persons) else values[row]]
            if len(sample) >= SLOT_SAMPLE:
                break
    if not sample:
        return
    for place in range(len(slots)):
        kind = sample[0][place][0]
        width = len(sample[0][place][1])
        places: "list[set[str]]" = [set() for _at in range(width)]
        census: "dict[str, int]" = {}
        people: "dict[str, list[int]]" = {}
        for at in range(len(sample)):
            written = sample[at][place][1]
            for spot in range(min(width, len(written))):
                places[spot] = places[spot] | {written[spot]}
            census[written] = (census[written] if written in census else 0) + 1
            _people_add(people, written, who[at], floor)
        slot: "dict[str, object]" = {"k": "r", "class": kind, "width": width,
                                     "places": [_joined(sorted(each), "") for each in places]}
        if (kind == "d" and width <= RUN_CENSUS_WIDTH and len(census) <= RUN_CENSUS_CAP
                and all(len(people[each]) >= floor for each in census)):
            slot["census"] = [[each, census[each]] for each in sorted(census)]
        slots[place] = slot
    template["slots"] = slots
    digits_all = [_joined_digits(runs) for runs in sample]
    template["luhn"] = len(sample) >= 200 and all(len(each) >= 6 and _luhn_ok(each) for each in digits_all)
    figures = [place for place in range(len(slots)) if sample[0][place][0] == "d"]
    ipv4 = (len(slots) == 4 and len(figures) == 4 and sum(1 for part in _parts_of(key) if part == _LIT + ".") == 3
            and all(int(runs[place][1]) <= 255 for runs in sample for place in range(4)))
    template["ipv4"] = ipv4
    if ipv4:
        template["ranges"] = [[min(int(runs[place][1]) for runs in sample), max(int(runs[place][1]) for runs in sample)]
                              for place in range(4)]
    # THE MARK: the first run of figures no census draws whose first figure leaves a value no real cell opens it with.
    mark: "list[object]" = []
    if ipv4:
        width = len(sample[0][0][1])
        low = 10 ** (width - 1) if width > 1 else 1
        high = min(10 ** width - 1, 223)
        free = [value for value in range(low, high + 1) if value not in firsts]
        if free:
            mark = [0, -1, [f"{value}" for value in free]]
    else:
        last_figure = -1
        if template["luhn"]:
            for place in range(len(slots)):
                if sample[0][place][0] == "d":
                    last_figure = place
        for place in range(len(slots)):
            slot = slots[place]
            kind = f"{slot['class']}"
            if kind != "d" or "census" in slot:
                continue
            if place == last_figure and int(f"{slot['width']}") <= 1:
                continue
            opened = openings[place] if place in openings else set()
            free_figures = _joined([figure for figure in _DIGITS if figure not in opened], "")
            if free_figures:
                # ...a figure other than nought where one is free: a key opening with a nought only where every other
                # opening figure is a real key's.
                others = [figure for figure in free_figures if figure != "0"]
                # ...AND NEVER A NOUGHT WHERE THE KEY IS ITS FIGURES ALONE (lane LEDGER, HIPAA): `0456` is the real key
                # `456` written another way -- read as a number it IS that key -- so a key of figures alone whose every
                # other opening figure is a real key's has no mark here. Measured on the health data zoo's
                # `i2b2_facts` at 20,000 rows on the shipped route: the encounter numbers of two to four figures
                # opened with a nought, and 233 real encounter numbers (491 cells) stood in the twin as numbers.
                # FIGURES ALONE IS READ OFF THE WHOLE KEY (batch 4zy's landing, the outside review's item 2): a letter
                # the floor's people write is a literal part of the key, outside its slots, so `L` and six figures has
                # one slot too -- and `L012345` is no real key either way. Read by its slots alone, such a class lost
                # its mark, fell to the room rule and was written in another class's template (400 `K` keys of four
                # figures beside 19,600 `L` keys of six: no `L` key left in the twin).
                if not others and len(_parts_of(key)) == 1:
                    continue
                # ...NOR WHERE THE RUN STANDS AS A WORD OF ITS OWN (lane TEXTZONE): `0567 River Ave` is the real
                # address `567 River Ave` read as a number and a street, as `0456` is the key `456`.
                if not others and _standing_alone(key, place):
                    continue
                mark = [place, 0, others if others else ["0"]]
                break
    template["mark"] = mark
    template["room"] = _room_bits(slots, mark)
    # A KEY OF FIGURES ALONE WHOSE EVERY OPENING FIGURE IS A REAL KEY'S (lane TEXTZONE): no mark keeps it off the real,
    # and the room rule wrote every such key one template wider -- the encounter numbers of two to four figures of the
    # health data zoo's `i2b2_facts` all came out five figures wide (the published count of five-figure keys missed). Of
    # at most `ABSENT_KEY_WIDTH` figures, it is written at its own width as a number no real key of the column is,
    # read as a number at any width (`_absent_key`): the real keys' numbers are kept as a bitmap.
    if (not mark and numbers is not None and len(_parts_of(key)) == 1 and len(slots) == 1
            and f"{slots[0]['class']}" == "d" and "census" not in slots[0]
            and int(f"{slots[0]['width']}") <= ABSENT_KEY_WIDTH):
        width = int(f"{slots[0]['width']}")
        below = 10 ** width
        held = {number for number in numbers if number < below}
        if any(number not in held for number in range(10 ** (width - 1) if width > 1 else 0, below)):
            template["absent"] = {"0": _bitmap_of(held, below)}


def _standing_alone(key: str, place: int) -> bool:
    """Whether a key template's slot `place` stands as a word of its own: the cell's start or a space before it, and
    its end or a space after it (`12 Oak St`'s house number), so a nought before it reads as nothing."""
    parts = _parts_of(key)
    slot = -1
    for at in range(len(parts)):
        if parts[at][:1] == _LIT:
            continue
        slot = slot + 1
        if slot != place:
            continue
        before = parts[at - 1][1:] if at > 0 and parts[at - 1][:1] == _LIT else ""
        after = parts[at + 1][1:] if at + 1 < len(parts) and parts[at + 1][:1] == _LIT else ""
        opens = at == 0 or (before != "" and _is_space(before[len(before) - 1:]))
        closes = at == len(parts) - 1 or (after != "" and _is_space(after[:1]))
        return opens and closes
    return False


def _absent_key(writer: "_Writer", template: "dict[str, object]", width: int) -> str:
    """A key of figures alone `width` figures wide, opening with no nought (but a key of one figure), that no real key
    of the column is as a number (`_key_template`'s bitmap); '' where none is left."""
    bitmap = _absent_bitmap(template, 0)
    low = 10 ** (width - 1) if width > 1 else 0
    span = 10 ** width - low
    for _attempt in range(64):
        value = low + _below(writer.state, span)
        if not _in_bitmap(bitmap, value):
            return f"{value}"
    start = _below(writer.state, span)
    for step in range(span):
        value = low + (start + step) % span
        if not _in_bitmap(bitmap, value):
            return f"{value}"
    return ""


def _joined_digits(runs: "list[tuple[str, str]]") -> str:
    joined = ""
    for kind, written in runs:
        if kind == "d":
            joined = joined + written
    return joined


def _luhn_ok(figures: str) -> bool:
    total = 0
    for place in range(len(figures)):
        value = int(figures[len(figures) - 1 - place])
        if place % 2 == 1:
            value = value * 2
            if value > 9:
                value = value - 9
        total = total + value
    return total % 10 == 0


def _luhn_figure(figures: str) -> str:
    """The figure that makes `figures` + it pass the Luhn check."""
    for figure in _DIGITS:
        if _luhn_ok(figures + figure):
            return figure
    return "0"


def _room_bits(slots: "list[dict[str, object]]", mark: "list[object]") -> float:
    """The bits of room a key template's free places hold (the mark's place counted by its own choices)."""
    bits = 0.0
    for place in range(len(slots)):
        slot = slots[place]
        if "census" in slot:
            continue
        alphabets = typing.cast("list[str]", slot["places"]) if "places" in slot else []
        for spot in range(len(alphabets)):
            size = len(alphabets[spot])
            if mark and mark[0] == place and mark[1] == spot:
                size = len(typing.cast("list[str]", mark[2]))
            if size > 1:
                bits = bits + _log2(size)
    return bits


def _log2(value: int) -> float:
    """The base-two logarithm of a whole number, near enough, by halving (no library float)."""
    bits = 0.0
    left = float(value)
    while left >= 2:
        left = left / 2
        bits = bits + 1.0
    return bits + (left - 1.0)


def zone_of(entries: "dict[str, dict[str, object]]") -> "dict[str, object]":
    """The text zone of a record: its version and each column's entry."""
    return {"version": VERSION, "columns": entries}


# -- reading the zone ------------------------------------------------------------------------------------


def _entries(zone: object) -> "dict[str, dict[str, object]]":
    if not isinstance(zone, dict) or "version" not in zone or zone["version"] != VERSION or "columns" not in zone:
        raise TextError("The inside record's text zone is of another version; the twin keeps the description's cells.")
    columns = zone["columns"]
    if not isinstance(columns, dict):
        raise TextError("The inside record's text zone is damaged; the twin keeps the description's cells.")
    return typing.cast("dict[str, dict[str, object]]", columns)


def columns_of(zone: object) -> "tuple[str, ...]":
    """The columns the zone writes, in name order. Raises `TextError` for a zone of another version."""
    return tuple(sorted(_entries(zone)))


def mode_of(zone: object, name: str) -> str:
    """The mode the zone writes a column in ('' where it names none). Raises `TextError` for a zone of another version."""
    entries = _entries(zone)
    if name not in entries:
        return ""
    entry = entries[name]
    return f"{entry['mode']}" if isinstance(entry, dict) and "mode" in entry else ""


def dealt_in_order(zone: object, name: str) -> bool:
    """Whether the zone deals a column's real census in the order its cells stand (`MODE_CENSUS`), so a column the
    relations zone drew may be written by it. Raises `TextError` for a zone of another version."""
    entries = _entries(zone)
    if name not in entries:
        return False
    entry = entries[name]
    return isinstance(entry, dict) and "mode" in entry and entry["mode"] == MODE_CENSUS


def held_of(zone: object) -> "set[str]":
    """The columns whose dates in disguise the description held and the zone fills (`MODE_HELD`)."""
    found: "set[str]" = set()
    try:
        entries = _entries(zone)
    except TextError:
        return found
    for name in entries:
        entry = entries[name]
        if isinstance(entry, dict) and "mode" in entry and entry["mode"] == MODE_HELD:
            found |= {name}
    return found


# -- writing a column ------------------------------------------------------------------------------------


@dataclasses.dataclass
class _Writer:
    """One column's draws: its entry, its stream, the values written so far and what each must keep."""

    entry: "dict[str, object]"
    state: "list[int]"
    style: str
    mode: str
    kept: "set[str]"
    keep: "set[str]"
    templates: "dict[str, dict[str, object]]"
    keys: "list[str]"
    parts: "dict[str, list[str]]"
    openings: "dict[str, str]"
    loose: "dict[str, set[int]]"
    written: "set[str]"
    folded: "set[str]"
    chain: "dict[str, tuple[list[str], list[int], list[str], list[int]]]"
    # A person's detail column (`MODE_DETAIL`): its made-up words by length, and each template's plan of lengths.
    neutral: "dict[int, list[str]]" = dataclasses.field(default_factory=dict)
    plans: "dict[str, object]" = dataclasses.field(default_factory=dict)
    # ...and the real column's runs of letters at the lengths no made-up word is left at (`_runs_at_lengths`).
    taken: "set[str]" = dataclasses.field(default_factory=set)


def _writer_of(entry: "dict[str, object]", state: "list[int]") -> _Writer:
    """A column's writer, read off its entry."""
    templates = typing.cast("dict[str, dict[str, object]]", entry["templates"])
    keys = sorted(key for key in templates if _off_the_real(f"{entry['style']}", templates[key]))
    parts = {key: _parts_of(key) for key in keys}
    writer = _Writer(
        entry=entry, state=state, style=f"{entry['style']}", mode=f"{entry['mode']}",
        kept=_spellings_of(entry["kept"]), keep=_spellings_of(entry["keep"]),
        templates=templates, keys=keys, parts=parts,
        openings=typing.cast("dict[str, str]", entry["openings"]) if "openings" in entry else {},
        loose={key: _loose_numbers(parts[key]) for key in keys}, written=set(), folded=set(), chain={},
    )
    if writer.mode == MODE_DETAIL and writer.style == "words":
        # ...A PERSON'S DETAIL IS WRITTEN ONLY IN A TEMPLATE THAT CAN KEEP IT OFF EVERY REAL CELL (`_detail_plan`).
        words = entry["neutral"] if "neutral" in entry else []
        for word in typing.cast("list[str]", words if isinstance(words, list) else []):
            text = f"{word}"
            writer.neutral[len(text)] = (writer.neutral[len(text)] if len(text) in writer.neutral else []) + [text]
        writer.taken = _spellings_of(entry["real_runs"]) - {""} if "real_runs" in entry else set()
        writer.keys = [key for key in keys if _detail_plan(writer, key) is not None]
    return writer


def _spellings_of(joined: object) -> "set[str]":
    """The spellings an entry keeps, written as one text (its size is the description's, not the table's)."""
    if not isinstance(joined, str):
        raise TextError("The inside record's text zone is damaged; the twin keeps the description's cells.")
    return set(joined.split(_SEP))


def _off_the_real(style: str, template: "dict[str, object]") -> bool:
    """Whether a key template's values are kept off every real one: by its mark, or by `ENTROPY_BITS` bits of room."""
    if style == "words":
        return True
    mark = template["mark"] if "mark" in template else []
    room = template["room"] if "room" in template else 0
    return bool(mark) or "absent" in template or (isinstance(room, (int, float)) and room >= ENTROPY_BITS)


def _parts_of(key: str) -> "list[str]":
    if not isinstance(key, str):
        raise TypeError("internal check: a template's key is text")
    return key.split(_SEP)


def _loose_numbers(parts: "list[str]") -> "set[int]":
    """The numbers of a template drawn each alone: whole numbers in a chain joined by single marks that may write an
    identifier or a date's figures (`555-0123`, `123-45-6789`, `10.0.0.1`, three or more by any of `-./:`); a pair
    joined by `/` or `:` (a pressure, a time) keeps the ranks of one real cell together."""
    loose: "set[int]" = set()
    ordinal = -1
    chain: "list[int]" = []
    joiner = ""
    gap = ""
    state = "none"
    for part in parts:
        head = part[:1]
        if head == _NUM:
            ordinal = ordinal + 1
            whole = part[1:3] == "0."
            if state == "mark" and whole and chain:
                if len(chain) == 1:
                    joiner = gap
                chain += [ordinal]
            else:
                loose |= _chain_loose(chain, joiner)
                chain = [ordinal] if whole else []
                joiner = ""
            state = "number"
        elif state == "number" and head == _LIT and len(part) == 2 and part[1:] in ("-", ".", "/", ":"):
            gap = part[1:]
            state = "mark"
        else:
            loose |= _chain_loose(chain, joiner)
            chain = []
            joiner = ""
            state = "none"
    return loose | _chain_loose(chain, joiner)


def _chain_loose(chain: "list[int]", joiner: str) -> "set[int]":
    """A chain's numbers where it may write an identifier's figures: three or more, or two joined by `-` or `.`."""
    if len(chain) >= 3 or (len(chain) == 2 and joiner in ("-", ".")):
        return set(chain)
    return set()


def _number_drawn(writer: _Writer, slot: "dict[str, object]", rank: float, wider: bool = True) -> str:
    """A number of the slot at a rank in (0, 1): a spelling of its census, or a value of its grid at its key."""
    key = f"{slot['key']}"
    if "census" in slot:
        census = typing.cast("list[list[object]]", slot["census"])
        total = 0
        for _each, count in census:
            total = total + int(f"{count}")
        point = rank * total
        running = 0
        for each, count in census:
            running = running + int(f"{count}")
            if point < running:
                return _opened_off(writer, f"{each}", wider)
        return _opened_off(writer, f"{census[len(census) - 1][0]}", wider)
    grid = typing.cast("list[float]", slot["grid"])
    position = rank * (len(grid) - 1)
    low = min(len(grid) - 2, int(position)) if len(grid) > 1 else 0
    if len(grid) == 1:
        value = grid[0]
    else:
        share = position - low
        value = grid[low] + (grid[low + 1] - grid[low]) * share
    written = _written_number(value, key, slot["plus"] is True)
    return _opened_off(writer, written, wider)


def _run_off(writer: _Writer, written: str) -> "bool | None":
    """Whether a number's run of `OPENING_RUN` figures or more opens with a figure no real run of its width opens with
    (None for a shorter run, or a width no real run has)."""
    if not isinstance(written, str):
        raise TypeError("internal check: a number is text")
    _sign, whole, _after = _number_parts(written)
    width = f"{len(whole)}"
    if len(whole) < OPENING_RUN or width not in writer.openings:
        return None
    return whole[:1] not in writer.openings[width]


def _opened_off(writer: _Writer, written: str, wider: bool = True) -> str:
    """A number whose run of `OPENING_RUN` figures or more opens with a figure no real run of its width opens with."""
    if not isinstance(written, str):
        raise TypeError("internal check: a number is text")
    sign, whole, after = _number_parts(written)
    width = f"{len(whole)}"
    if len(whole) < OPENING_RUN or width not in writer.openings:
        return written
    taken = writer.openings[width]
    if whole[:1] not in taken:
        return written
    free = [figure for figure in "987654321" if figure not in taken]
    if free:
        whole = free[_below(writer.state, len(free))] + whole[1:]
        return sign + whole + ("." + after if after else "")
    if not wider:
        return written
    # EVERY OPENING OF ITS WIDTH IS A REAL RUN'S: the run is written one figure wider, at an opening no real run of
    # that width takes (a record number inside a note is never a real one).
    width_wider = f"{len(whole) + 1}"
    taken_wider = writer.openings[width_wider] if width_wider in writer.openings else ""
    free_wider = [figure for figure in "987654321" if figure not in taken_wider]
    if not free_wider:
        return sign + "0" + whole + ("." + after if after else "")
    return sign + free_wider[_below(writer.state, len(free_wider))] + whole + ("." + after if after else "")


def _word_drawn(writer: _Writer, slot: "dict[str, object]") -> str:
    """A made-up word of the slot's lengths and case, never a kept word."""
    lengths = typing.cast("dict[str, int]", slot["lengths"])
    cases = typing.cast("dict[str, int]", slot["cases"])
    sizes = sorted(lengths)
    size = int(sizes[_weighted(writer.state, [int(f"{lengths[each]}") for each in sizes])])
    kinds = sorted(cases)
    case = kinds[_weighted(writer.state, [int(f"{cases[each]}") for each in kinds])]
    letters = f"{slot['letters']}" if "letters" in slot else ""
    pool = letters if letters and _uniform(writer.state) < 0.5 else ""
    for _attempt in range(TRIES):
        word = ""
        for place in range(size):
            if pool:
                word = word + pool[_below(writer.state, len(pool))]
                continue
            source = _UPPER if case == "upper" or (case == "title" and place == 0) else _LOWER
            word = word + source[_below(writer.state, len(source))]
        if word not in writer.kept:
            return word
    return word


def _date_drawn(writer: _Writer, calendar: "dict[str, object]") -> "tuple[str, str, str]":
    """A made-up date: a year, month and weekday by the template's counts, the day of the month made up."""
    cells = typing.cast("dict[str, int]", calendar["cells"])
    keys = sorted(cells)
    chosen = keys[_weighted(writer.state, [int(f"{cells[each]}") for each in keys])]
    pieces = _parts_dotted(chosen)
    year, month, weekday = int(pieces[0]), int(pieces[1]), int(pieces[2])
    days = [day for day in range(1, _days_in(year, month) + 1) if _weekday(year, month, day) == weekday]
    day = days[_below(writer.state, len(days))]
    months = typing.cast("dict[str, str]", calendar["months"])
    word = months[f"{month}"] if f"{month}" in months else months[sorted(months)[0]]
    written_day = f"{day}"
    if calendar["padded"] is True and day < 10:
        written_day = "0" + written_day
    return written_day, f"{word}", f"{year}"


def _parts_dotted(text: str) -> "list[str]":
    if not isinstance(text, str):
        raise TypeError("internal check: a key is text")
    return text.split(".")


def _ranks(writer: _Writer, template: "dict[str, object]", count: int) -> "list[float]":
    """A cell's numbers' ranks together: one real row's ranks, each moved by up to `BANDWIDTH` of its own ranks.

    The ranks of one cell's numbers keep their relation (a pressure's two
    readings, a waveform's shape) as a copula of the real cells, widened:
    each rank is moved evenly within the bandwidth and turned back at the
    ends, so no twin cell is a real cell's numbers copied, and the cells
    drawn are as varied as the real column's.
    """
    joint = typing.cast("list[list[int]]", template["joint"]) if "joint" in template else []
    if not joint or len(joint[0]) != count:
        return [_uniform(writer.state) for _place in range(count)]
    row = joint[_below(writer.state, len(joint))]
    ranks: "list[float]" = []
    for value in row:
        moved = value / RANK + (2.0 * _uniform(writer.state) - 1.0) * BANDWIDTH
        if moved < 0:
            moved = -moved
        if moved > 1:
            moved = 2.0 - moved
        ranks += [min(0.999999, max(0.000001, moved))]
    return ranks


def _cell_of(writer: _Writer, key: str) -> str:
    """One cell drawn in a template."""
    template = writer.templates[key]
    slots = typing.cast("list[dict[str, object]]", template["slots"])
    if writer.style != "words":
        return _key_drawn(writer, key, template, slots)
    numbered = [slot for slot in slots if slot["k"] == "n"]
    ranks = _ranks(writer, template, len(numbered))
    for place in writer.loose[key]:
        if place < len(ranks):
            ranks[place] = _uniform(writer.state)
    date: "tuple[str, str, str]" = ("", "", "")
    if "calendar" in template:
        date = _date_drawn(writer, typing.cast("dict[str, object]", template["calendar"]))
    # ...each date of the cell its own (a date's three slots each once; a slot met again opens the next date).
    used: "set[str]" = set()
    pieces: "list[str]" = []
    at = 0
    number = 0
    owed: "list[int]" = []
    off = False
    for part in writer.parts[key]:
        head = part[:1]
        if head == _LIT:
            pieces += [part[1:]]
            continue
        slot = slots[at]
        at = at + 1
        if head == _NUM:
            piece = _number_drawn(writer, slot, ranks[number], False)
            number = number + 1
            standing = _run_off(writer, piece)
            if standing is True:
                off = True
            elif standing is False:
                owed += [len(pieces)]
            pieces += [piece]
        elif head == _WORD:
            pieces += [_word_drawn(writer, slot)]
        elif part[:1] == _DATE:
            if part in used:
                date = _date_drawn(writer, typing.cast("dict[str, object]", template["calendar"]))
                used = set()
            used = used | {part}
            if part == _DATE + "dd":
                pieces += [date[0]]
            elif part == _DATE + "dm":
                pieces += [date[1]]
            elif part == _DATE + "dy":
                pieces += [date[2]]
    # ONE LONG RUN OFF THE REAL KEEPS THE CELL OFF IT: a run whose every opening of its width is real is written one
    # figure wider only when no other run of the cell opens off the real (`/chart/A1234567/123456` keeps its form).
    if owed and not off:
        place = owed[len(owed) - 1]
        pieces[place] = _opened_off(writer, pieces[place])
    return _joined(pieces, "")


def _key_drawn(writer: _Writer, key: str, template: "dict[str, object]", slots: "list[dict[str, object]]") -> str:
    """One key drawn in a key template: each place from its characters, the mark off the real, the check figure computed."""
    mark = typing.cast("list[object]", template["mark"]) if "mark" in template else []
    ranges = typing.cast("list[list[int]]", template["ranges"]) if "ranges" in template else []
    if not mark and "absent" in template:
        return _absent_key(writer, template, int(f"{slots[0]['width']}"))
    runs: "list[str]" = []
    for place in range(len(slots)):
        slot = slots[place]
        if template["ipv4"] is True:
            width = int(f"{slot['width']}")
            if mark and mark[0] == place:
                free = typing.cast("list[str]", mark[2])
                runs += [free[_below(writer.state, len(free))]]
                continue
            low, high = ranges[place][0], ranges[place][1]
            low = max(low, 10 ** (width - 1) if width > 1 else 0)
            high = min(high, 10 ** width - 1, 255)
            runs += [f"{low + _below(writer.state, high - low + 1)}"]
            continue
        if "census" in slot:
            census = typing.cast("list[list[object]]", slot["census"])
            runs += [f"{census[_weighted(writer.state, [int(f'{count}') for _each, count in census])][0]}"]
            continue
        alphabets = typing.cast("list[str]", slot["places"])
        written = ""
        for spot in range(len(alphabets)):
            alphabet = alphabets[spot]
            if mark and mark[0] == place and mark[1] == spot:
                alphabet = _joined(typing.cast("list[str]", mark[2]), "")
            if not alphabet:
                alphabet = _class_alphabet(f"{slot['class']}") or _LOWER
            written = written + alphabet[_below(writer.state, len(alphabet))]
        runs += [written]
    if template["luhn"] is True:
        figures = ""
        for place in range(len(slots)):
            if f"{slots[place]['class']}" == "d":
                figures = figures + runs[place]
        last = -1
        for place in range(len(slots)):
            if f"{slots[place]['class']}" == "d":
                last = place
        if last >= 0 and figures:
            checked = _luhn_figure(figures[:len(figures) - 1])
            run = runs[last]
            runs[last] = run[:len(run) - 1] + checked
    text = ""
    at = 0
    for part in writer.parts[key]:
        if part[:1] == _LIT:
            text = text + part[1:]
        else:
            text = text + runs[at]
            at = at + 1
    return text


def _free_drawn(writer: _Writer, length: int) -> str:
    """A free cell drawn from the chain, cut at `length` characters (a made-up word or a mark filling the last ones)."""
    return _cut(writer, _chain_text(writer, length, 0), length)


def _free_words(writer: _Writer, words: int) -> str:
    """A free cell drawn from the chain, cut after its `words`-th word."""
    text = _chain_text(writer, 0, words)
    counted = 0
    inside = False
    for at in range(len(text)):
        if _is_space(text[at]):
            if inside and counted == words:
                return text[:at]
            inside = False
        elif not inside:
            inside = True
            counted = counted + 1
    return text


def _chain_text(writer: _Writer, length: int, words: int) -> str:
    """Text drawn from the free cells' chain until it holds `length` characters, or `words` words."""
    chain = typing.cast("dict[str, object]", writer.entry["free"])
    follow = typing.cast("dict[str, dict[str, int]]", chain["follow"])
    numbers = typing.cast("dict[str, dict[str, object]]", chain["numbers"])
    word = typing.cast("dict[str, object]", chain["word"]) if "word" in chain else None
    text = ""
    before = _START
    last = _START
    steps = 0
    counted = 0
    spaced = True
    while ((length and len(text) < length) or (words and counted <= words)) and steps < TOKENS_CAP:
        steps = steps + 1
        context = before + _SEP + last
        if context not in follow:
            context = _START + _SEP + _START
        if context not in writer.chain:
            options = follow[context]
            names = sorted(options)
            going = [name for name in names if name != _END] or names
            writer.chain[context] = (names, [int(f"{options[name]}") for name in names], going,
                                     [int(f"{options[name]}") for name in going])
        _names, _weights, going, weights = writer.chain[context]
        symbol = going[_weighted(writer.state, weights)]
        if symbol == _END:
            before = _START
            last = _START
            text = text + " "
            spaced = True
            continue
        head = symbol[:1]
        if head == _LIT:
            piece = symbol[1:]
        elif head == _NUM and symbol in numbers:
            piece = _number_drawn(writer, numbers[symbol], _uniform(writer.state))
        elif head == _WORD and word is not None:
            piece = _word_drawn(writer, word)
        else:
            piece = "x"
        text = text + piece
        if piece and _is_space(piece[:1]):
            spaced = True
        elif piece:
            if spaced:
                counted = counted + 1
            spaced = False
        before = last
        last = symbol
    return text


def _cut(writer: _Writer, text: str, length: int) -> str:
    """A text cut to exactly `length` characters, ending on a letter or a mark rather than a space."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell is text")
    if len(text) < length:
        text = text + "x" * (length - len(text))
    text = text[:length]
    if length and _is_space(text[length - 1:]):
        text = text[: length - 1] + "."
    if length and _is_space(text[:1]):
        text = "." + text[1:]
    return text


def _class_of(text: str) -> "tuple[bool, bool, int]":
    """What the description counts of a value: whether it is all figures, whether it is of a code's alphabet, its words."""
    trimmed = parsing.trimmed(text)
    return parsing.is_digit_text(trimmed), parsing.is_code_text(trimmed), parsing.token_count(text)


def _fresh(writer: _Writer, text: str) -> bool:
    """Whether a value is none the column already writes (nor one of its kept spellings), in its case or folded.

    A value longer than `FRESH_CAP` characters is drawn from the chain and
    repeats no other in practice; it is not held (a column of two million
    notes would hold a folded copy of each).
    """
    if text in writer.keep:
        return False
    if len(text) > FRESH_CAP:
        return True
    return text not in writer.written and parsing.folded(text) not in writer.folded


def _take(writer: _Writer, text: str) -> str:
    if len(text) <= FRESH_CAP:
        writer.written |= {text}
        writer.folded |= {parsing.folded(text)}
    return text


def _value_for(writer: _Writer, original: str, key: str, bounds: "tuple[int, int, int, int]",
               anchor: "tuple[int, ...]" = (), target: int = 0) -> str:
    """The new value of one different value of the description's twin, in a template (or the chain where key is '').

    It keeps the old value's counts of figures and of a code's alphabet
    where a draw allows; an ``anchor`` -- the value written to carry the
    column's least length (0), greatest length (1), fewest words (2) or
    most words (3), of ``bounds`` (the twin's least and greatest length,
    least and greatest words), one value perhaps carrying two -- keeps
    that length and that count exactly where a draw allows (a value of
    the chain short of its length is lengthened inside its last word),
    and no value goes past them. The other
    values' lengths are their templates' own, as the real cells' are, or,
    drawn from the chain, ``target`` (a length the real free cells hold).
    """
    if not isinstance(original, str):
        raise TypeError("internal check: a cell is text")
    wanted = _class_of(original)
    by_length = 0 in anchor or 1 in anchor
    by_words = 2 in anchor or 3 in anchor
    length = len(original) if by_length or not target else target
    shortest, longest, fewest, most = bounds
    best = ""
    best_distance = -1
    for attempt in range(TRIES * (4 if by_length and by_words else 1)):
        # A free value takes `FREE_TRIES` draws, and more only while none of them stays inside the column's ends.
        if not key and not anchor and attempt >= FREE_TRIES and 0 <= best_distance < 50:
            break
        if key:
            drawn = _cell_of(writer, key)
        elif by_words:
            drawn = _free_words(writer, wanted[2])
            if by_length and len(drawn) < length:
                drawn = _lengthened(drawn, length)
        else:
            drawn = _free_drawn(writer, length)
        if not _fresh(writer, drawn):
            continue
        found = _class_of(drawn)
        distance = (0 if found[0] == wanted[0] else 1000) + (0 if found[1] == wanted[1] else 100)
        # Lengths and words are free text's own facts: a label's stand-ins say nothing of its tail's lengths.
        if writer.style == "words" and writer.mode == MODE_FREE:
            if by_length:
                distance = distance + abs(len(drawn) - length) * 4
            if by_words:
                distance = distance + abs(found[2] - wanted[2]) * 4
            if len(drawn) < shortest or len(drawn) > longest or found[2] < fewest or found[2] > most:
                distance = distance + 50
        if best_distance < 0 or distance < best_distance:
            best = drawn
            best_distance = distance
        if distance == 0:
            break
    if best:
        return _take(writer, best)
    searched = _searched(writer, key, length) if key else ""
    if searched:
        return _take(writer, searched)
    return original


def _lengthened(text: str, length: int) -> str:
    """A text lengthened to `length` characters inside its last word (its count of words kept)."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell is text")
    end = len(text)
    while end > 0 and not _is_letter(text[end - 1]):
        end = end - 1
    if end == 0:
        return text
    return text[:end] + "e" * (length - len(text)) + text[end:]


def _searched(writer: _Writer, key: str, length: int) -> str:
    """A fresh value of a template whose slots are all census numbers, found by counting through them."""
    template = writer.templates[key]
    slots = typing.cast("list[dict[str, object]]", template["slots"])
    if writer.style != "words" or "calendar" in template:
        return ""
    choices: "list[list[str]]" = []
    room = 1
    for slot in slots:
        if slot["k"] != "n" or "census" not in slot:
            return ""
        census = typing.cast("list[list[object]]", slot["census"])
        choices += [[f"{each}" for each, _count in census]]
        room = room * len(census)
    if room > SEARCH_CAP:
        return ""
    start = _below(writer.state, room)
    nearest = ""
    for step in range(room):
        index = (start + step) % room
        picked: "list[str]" = []
        for options in choices:
            picked += [options[index % len(options)]]
            index = index // len(options)
        text = ""
        at = 0
        for part in writer.parts[key]:
            if part[:1] == _LIT:
                text = text + part[1:]
            else:
                text = text + picked[at]
                at = at + 1
        if not _fresh(writer, text):
            continue
        if len(text) == length:
            return text
        if not nearest:
            nearest = text
    return nearest


def _budgets(writer: _Writer, total: int) -> "tuple[list[str], list[int]]":
    """Each template's share of the rows to write (the chain's under ''), by the real rows that wear each."""
    keys = [key for key in writer.keys]
    weights = [int(f"{writer.templates[key]['rows']}") for key in keys]
    read = int(f"{writer.entry['read']}")
    if "free" in writer.entry:
        keys += [""]
        weights += [max(0, read - sum(weights))]
    whole = max(1, sum(weights))
    shares = [(weight * total) // whole for weight in weights]
    left = total - sum(shares)
    order = sorted((-((weights[place] * total) % whole), place) for place in range(len(weights)))
    for _remainder, place in order[:left]:
        shares[place] = shares[place] + 1
    return keys, shares


def _listed(writer: _Writer, counts: "dict[str, int]") -> "dict[str, str]":
    """Each different value of a tail of lists written anew: as many items as the real value of its rank holds (the
    commonest first), drawn by how often each is written, apart and in order where the real's are, and a list no other
    value and no kept spelling is; a value no draw finds one for keeps its old spelling."""
    facts = typing.cast("dict[str, object]", writer.entry["list"])
    mark = f"{facts['mark']}"
    pairs = typing.cast("list[list[object]]", facts["items"])
    items = [f"{item}" for item, _times in pairs]
    weights = [int(f"{times}") for _item, times in pairs]
    runs = typing.cast("list[list[int]]", facts["sizes"])
    repeats = facts["repeats"] is True
    in_order = facts["in_order"] is True
    sizes = sorted({int(f"{size}") for size, _run in runs})
    renamed: "dict[str, str]" = {}
    run_at = 0
    taken = 0
    for _count, cell in sorted((-counts[cell], cell) for cell in counts):
        size = int(f"{runs[min(run_at, len(runs) - 1)][0]}")
        taken = taken + 1
        if run_at < len(runs) and taken >= int(f"{runs[run_at][1]}"):
            run_at = run_at + 1
            taken = 0
        value = cell
        for wanted in [size] + [other for _gap, other in sorted((abs(other - size), other) for other in sizes)]:
            for _attempt in range(TRIES):
                picked = _items_drawn(writer, items, weights, wanted, repeats)
                text = _joined(sorted(picked) if in_order else picked, mark)
                if _fresh(writer, text):
                    value = _take(writer, text)
                    break
            # ...and where no draw finds a fresh list of that size, every list of it is counted through.
            searched = "" if value != cell else _list_searched(writer, items, wanted, mark, repeats, in_order)
            if searched:
                value = _take(writer, searched)
            if value != cell:
                break
        renamed[cell] = value
    return renamed


def _list_searched(writer: _Writer, items: "list[str]", size: int, mark: str, repeats: bool, in_order: bool) -> str:
    """A fresh list of `size` items found by counting through every list of them, from a drawn start ('' for none, or
    past `SEARCH_CAP` lists)."""
    room = len(items) ** size
    if not items or size < 1 or room > SEARCH_CAP:
        return ""
    start = _below(writer.state, room)
    for step in range(room):
        index = (start + step) % room
        picked: "list[str]" = []
        for _place in range(size):
            picked += [items[index % len(items)]]
            index = index // len(items)
        if not repeats and len(set(picked)) < size:
            continue
        if in_order and picked != sorted(picked):
            continue
        text = _joined(picked, mark)
        if _fresh(writer, text):
            return text
    return ""


def _items_drawn(writer: _Writer, items: "list[str]", weights: "list[int]", size: int, repeats: bool) -> "list[str]":
    """`size` items drawn by their weights, each at most once where the real never repeats one in a cell."""
    picked: "list[str]" = []
    left = [weight for weight in weights]
    for _place in range(min(size, len(items)) if not repeats else size):
        at = _weighted(writer.state, left)
        picked += [items[at]]
        if not repeats:
            left[at] = 0
    return picked


def _detail_plan(writer: _Writer, key: str) -> "tuple[list[list[tuple[int, int, bool]]], list[list[list[int]]], int, int] | None":
    """THE LENGTHS A DETAIL TEMPLATE'S CELLS MAY TAKE, EACH KEPT OFF EVERY REAL CELL: each slot's lengths
    (`_detail_options`), and for each slot and each number of characters still to write, the weight of every way the
    slots left may fill them -- once with a piece no real cell holds already written, once without -- so a draw at a
    length is exact and keeps the cell off the real, or is not made. None for a template whose cells cannot be kept off
    the real (every slot kept, no made-up word, no long run and no short number no real cell holds there), for one
    holding a date, and past `DETAIL_SLOTS` slots."""
    if key in writer.plans:
        known = writer.plans[key]
        return None if known is None else typing.cast(
            "tuple[list[list[tuple[int, int, bool]]], list[list[list[int]]], int, int]", known)
    slots = typing.cast("list[dict[str, object]]", writer.templates[key]["slots"])
    plan: "tuple[list[list[tuple[int, int, bool]]], list[list[list[int]]], int, int] | None" = None
    if len(slots) <= DETAIL_SLOTS and all(f"{slot['k']}" in ("n", "w") for slot in slots):
        options = [_detail_options(writer, key, at) for at in range(len(slots))]
        if all(options):
            reach = 0
            for each in options:
                reach = reach + max(size for size, _weight, _off in each)
            reach = min(DETAIL_REACH, reach)
            count = len(options)
            table = [[[0, 0] for _left in range(reach + 1)] for _at in range(count + 1)]
            table[count][0][1] = 1
            for at in range(count - 1, -1, -1):
                for left in range(reach + 1):
                    for done in (0, 1):
                        total = 0
                        for size, weight, off in options[at]:
                            if size <= left:
                                total = total + weight * table[at + 1][left - size][1 if (done or off) else 0]
                        table[at][left][done] = total
            if any(table[0][left][0] > 0 for left in range(reach + 1)):
                literal = 0
                for part in writer.parts[key]:
                    if part[:1] == _LIT:
                        literal = literal + len(part) - 1
                plan = (options, table, literal, reach)
    writer.plans[key] = plan
    return plan


def _detail_options(writer: _Writer, key: str, at: int) -> "list[tuple[int, int, bool]]":
    """The lengths slot `at` of a detail template may be written at: (length, weight, whether a piece of that length
    keeps the cell off every real one). A word: each length the real words of the slot take or a made-up word of the
    column has (`NEUTRAL_WORDS` left by `_neutral_left`), off where it has one. A number: each length its real numbers
    are written at, off where its whole figures are a run of `OPENING_RUN` or more that can open with a figure no real
    run of its width opens with, or, for a short number held off the real (`_absent_facts`), where some number of that
    width no real cell of the template holds there is left."""
    template = writer.templates[key]
    slot = typing.cast("list[dict[str, object]]", template["slots"])[at]
    options: "list[tuple[int, int, bool]]" = []
    if f"{slot['k']}" == "w":
        lengths = typing.cast("dict[str, int]", slot["lengths"])
        for size in range(1, DETAIL_WORD_LONGEST + 1):
            real = int(f"{lengths[f'{size}']}") if f"{size}" in lengths else 0
            off = size in writer.neutral
            if real or off:
                options += [(size, 1000 * min(real, 100000) + 1, off)]
        return options
    bitmap = _absent_bitmap(template, at)
    spellings = _number_spellings(slot)
    counted: "dict[int, int]" = {}
    for written, count in spellings:
        counted[len(written)] = (counted[len(written)] if len(written) in counted else 0) + count
    for size in sorted(counted):
        if bitmap:
            off = _absent_number(writer, key, at, size, False) != ""
        else:
            off = all(_run_can_be_off(writer, written) for written, _count in spellings if len(written) == size)
        options += [(size, min(counted[size], 100000), off)]
    return options


def _number_spellings(slot: "dict[str, object]") -> "list[tuple[str, int]]":
    """A number slot's real spellings with their counts (its census), or its grid's points as written, one each."""
    if "census" in slot:
        return [(f"{each}", int(f"{count}")) for each, count in typing.cast("list[list[object]]", slot["census"])]
    key = f"{slot['key']}"
    plus = slot["plus"] is True
    return [(_written_number(value, key, plus), 1) for value in typing.cast("list[float]", slot["grid"])]


def _run_can_be_off(writer: _Writer, written: str) -> bool:
    """Whether a number's whole figures are a run `_opened_off` keeps off every real run: `OPENING_RUN` figures or
    more, of a width no real run has or with an opening figure no real run of its width takes."""
    _sign, whole, _after = _number_parts(written)
    if len(whole) < OPENING_RUN:
        return False
    width = f"{len(whole)}"
    if width not in writer.openings:
        return True
    taken = writer.openings[width]
    return any(figure not in taken for figure in "987654321")


def _absent_bitmap(template: "dict[str, object]", at: int) -> str:
    """The bitmap of the numbers the real cells of a template hold at slot `at` ('' where it keeps none)."""
    absent = template["absent"] if "absent" in template else None
    if not isinstance(absent, dict) or f"{at}" not in absent:
        return ""
    return f"{absent[f'{at}']}"


def _absent_number(writer: _Writer, key: str, at: int, size: int, drawn: bool) -> str:
    """A short whole number `size` characters wide that no real cell of template `key` holds at its slot `at`, in the
    slot's padding; a telephone number's part opens with 2 to 9 and is no `N11` service number. Taken evenly from every
    such number (counted once a template, a slot and a width) where ``drawn``, else the first (whether one is left);
    '' where none is."""
    template = writer.templates[key]
    slot = typing.cast("list[dict[str, object]]", template["slots"])[at]
    bitmap = _absent_bitmap(template, at)
    pieces = _parts_dotted(f"{slot['key']}")
    written_key = f"{slot['key']}"
    padded = int(pieces[1]) if len(pieces) > 1 and pieces[1] else 0
    phone = "phone" in template and template["phone"] is True
    if not bitmap or (padded and padded != size):
        return ""
    low = 0 if padded or size == 1 else 10 ** (size - 1)
    high = min(10 ** size, 10 ** ABSENT_WIDTH) - 1
    if high < low:
        return ""
    known = _SEP + "absent" + _SEP + key + _SEP + f"{at}" + _SEP + f"{size}"
    if known not in writer.plans:
        writer.plans[known] = [value for value in range(low, high + 1) if _absent_allowed(bitmap, value, phone)]
    left = typing.cast("list[int]", writer.plans[known])
    if not left:
        return ""
    key = written_key
    return _written_number(float(left[_below(writer.state, len(left)) if drawn else 0]), key, False)


def _absent_allowed(bitmap: str, value: int, phone: bool) -> bool:
    """Whether a short number is free of the real (not in the bitmap) and, in a telephone number, a valid part."""
    if _in_bitmap(bitmap, value):
        return False
    return not phone or (value >= 200 and value % 100 != 11)


def _detail_drawn(writer: _Writer, key: str, length: int) -> str:
    """One cell of a detail template exactly `length` characters long, holding a piece no real cell holds (a made-up
    word of the column, a long run opening off the real, or a short number off the real); '' where the template has
    no such cell of that length (`_detail_plan`)."""
    plan = _detail_plan(writer, key)
    if plan is None:
        return ""
    options, table, literal, reach = plan
    left = length - literal
    if left < 0 or left > reach or table[0][left][0] <= 0:
        return ""
    sizes: "list[int]" = []
    done = 0
    for at in range(len(options)):
        weights: "list[int]" = []
        for size, weight, off in options[at]:
            weights += [weight * table[at + 1][left - size][1 if (done or off) else 0] if size <= left else 0]
        size, _weight, off = options[at][_weighted(writer.state, weights)]
        sizes += [size]
        done = 1 if (done or off) else 0
        left = left - size
    template = writer.templates[key]
    slots = typing.cast("list[dict[str, object]]", template["slots"])
    pieces: "list[str]" = []
    at = 0
    for part in writer.parts[key]:
        if part[:1] == _LIT:
            pieces += [part[1:]]
            continue
        slot = slots[at]
        if f"{slot['k']}" == "w":
            pieces += [_neutral_drawn(writer, slot, sizes[at])]
        else:
            # ...a short number off the real where one of that width is left; where every one is a real cell's (a
            # column using every exchange), a number of the slot's own, the cell kept off the real by another piece.
            absent = _absent_number(writer, key, at, sizes[at], True) if _absent_bitmap(template, at) else ""
            pieces += [absent if absent else _number_sized(writer, key, at, sizes[at])]
        at = at + 1
    return _joined(pieces, "")


def _neutral_drawn(writer: _Writer, slot: "dict[str, object]", size: int) -> str:
    """A made-up word of `size` letters in a case the slot's real words take: one of the column's words left
    (`_neutral_left`) where one is that long, else such words run together and cut at the length."""
    cases = typing.cast("dict[str, int]", slot["cases"])
    kinds = sorted(cases)
    case = kinds[_weighted(writer.state, [int(f"{cases[each]}") for each in kinds])] if kinds else "lower"
    if size in writer.neutral:
        words = writer.neutral[size]
        word = words[_below(writer.state, len(words))]
    else:
        pool: "list[str]" = []
        for length in sorted(writer.neutral):
            pool += writer.neutral[length]
        word = ""
        for _attempt in range(_WORD_TRIES):
            word = ""
            while len(word) < size:
                word = word + (pool[_below(writer.state, len(pool))] if pool else _LOWER[_below(writer.state, 26)])
            word = word[:size]
            # ...never a run of letters a real cell of the column writes (`_runs_at_lengths`; one letter names nobody)
            if size < 2 or parsing.folded(word) not in writer.taken:
                break
        if size >= 2 and parsing.folded(word) in writer.taken:
            word = _word_off(writer, size)
    written = ""
    for place in range(len(word)):
        character = word[place:place + 1]
        written = written + (_capital(character) if case == "upper" or (case == "title" and place == 0) else character)
    return written


# How many made-up words of a length no made-up word has are drawn before the letters are walked (`_word_off`).
_WORD_TRIES = 64


def _word_off(writer: _Writer, size: int) -> str:
    """A word of `size` small letters no real cell writes as a run (`writer.taken`), walked in order of the letters
    from a drawn start: for a size of more than three letters, a drawn word whose last three letters are walked."""
    head = ""
    for _place in range(max(0, size - 3)):
        head = head + _LOWER[_below(writer.state, 26)]
    tail = min(size, 3)
    span = 26 ** tail
    start = _below(writer.state, span)
    for step in range(span):
        value = (start + step) % span
        letters = ""
        for _place in range(tail):
            letters = _LOWER[value % 26] + letters
            value = value // 26
        word = head + letters
        if parsing.folded(word) not in writer.taken:
            return word
    return head + _LOWER[0] * tail


def _capital(character: str) -> str:
    """A small ASCII letter as its capital; any other character as it is."""
    if not isinstance(character, str):
        raise TypeError("internal check: a letter is text")
    found = _LOWER.find(character)
    return _UPPER[found] if found >= 0 and len(character) == 1 else character


def _number_sized(writer: _Writer, key: str, at: int, size: int) -> str:
    """A number of template `key`'s slot `at` written in `size` characters: a census spelling of that length by its
    count, or a value between two grid points of that length (the grid's places of each length counted once); its long
    run opened off the real (`_opened_off`, never wider)."""
    slot = typing.cast("list[dict[str, object]]", writer.templates[key]["slots"])[at]
    written = ""
    if "census" in slot:
        found = [(each, count) for each, count in _number_spellings(slot) if len(each) == size]
        if found:
            written = found[_weighted(writer.state, [count for _each, count in found])][0]
    else:
        slot_key = f"{slot['key']}"
        plus = slot["plus"] is True
        grid = typing.cast("list[float]", slot["grid"])
        known = _SEP + "grid" + _SEP + key + _SEP + f"{at}" + _SEP + f"{size}"
        if known not in writer.plans:
            writer.plans[known] = [place for place in range(len(grid))
                                   if len(_written_number(grid[place], slot_key, plus)) == size]
        places = typing.cast("list[int]", writer.plans[known])
        if places:
            place = places[_below(writer.state, len(places))]
            written = _written_number(grid[place], slot_key, plus)
            if place + 1 < len(grid):
                between = _written_number(grid[place] + (grid[place + 1] - grid[place]) * _uniform(writer.state),
                                          slot_key, plus)
                if len(between) == size:
                    written = between
    return _opened_off(writer, written, False) if written else written


def _detail_shape(writer: _Writer, key: str) -> "tuple[int, bool, bool]":
    """A detail template's words (cut by spaces), whether its cells are all figures and whether of a code's alphabet."""
    text = ""
    for part in writer.parts[key]:
        head = part[:1]
        if head == _LIT:
            text = text + part[1:]
        elif head == _NUM:
            text = text + ("9" if part[1:3] == "0." else "9.9")
        else:
            text = text + "a"
    figures, code, words = _class_of(text)
    return words, figures, code


def _detail_fresh(writer: _Writer, key: str, length: int) -> str:
    """A fresh cell of a detail template at `length` characters (`_detail_drawn`, `_fresh`), '' where none is found."""
    for _attempt in range(TRIES):
        drawn = _detail_drawn(writer, key, length)
        if not drawn:
            return ""
        if _fresh(writer, drawn):
            return drawn
    return ""


def _detail_written(writer: _Writer, counts: "dict[str, int]") -> "dict[str, str]":
    """EACH DIFFERENT VALUE OF THE DESCRIPTION'S TWIN WRITTEN ANEW AS A PERSON'S DETAIL OF ITS OWN LENGTH.

    The commonest values first, each in the template with the most rows
    still owed (templates in proportion to the real rows each covers)
    whose cells can be that long, hold as many words and are as often all
    figures or of a code's alphabet; failing that, as many words; failing
    that, any template; and only where no template can be that long, the
    nearest length one can (at most `DETAIL_NEAREST` away). So the column
    keeps the description's own facts of free text -- how many different
    values, how many rows hold each, each value's length and words --
    while every value wears a real layout with every word that could name
    somebody made up, and is no real cell (`_detail_drawn`). A value no
    template can write keeps the description's own made-up spelling.
    """
    keys = writer.keys
    weights = [int(f"{writer.templates[key]['rows']}") for key in keys]
    total = sum(counts[cell] for cell in counts)
    whole = max(1, sum(weights))
    left = [(weight * total) // whole for weight in weights]
    shapes = [_detail_shape(writer, key) for key in keys]
    renamed: "dict[str, str]" = {}
    for _count, cell in sorted((-counts[cell], cell) for cell in counts):
        wanted = _class_of(cell)
        ranked = [at for _left, at in sorted((-left[at], at) for at in range(len(keys)))]
        value = ""
        chosen = -1
        for tier in range(3):
            for at in ranked:
                words, figures, code = shapes[at]
                if (tier < 2 and words != wanted[2]) or (tier < 1 and (figures != wanted[0] or code != wanted[1])):
                    continue
                value = _detail_fresh(writer, keys[at], len(cell))
                if value:
                    chosen = at
                    break
            if value:
                break
        gap = 0
        while not value and gap < DETAIL_NEAREST:
            gap = gap + 1
            for near in (len(cell) - gap, len(cell) + gap):
                for at in ranked:
                    value = _detail_fresh(writer, keys[at], near) if near > 0 else ""
                    if value:
                        chosen = at
                        break
                if value:
                    break
        if value:
            left[chosen] = left[chosen] - counts[cell]
            renamed[cell] = _take(writer, value)
        else:
            renamed[cell] = cell
    return renamed


def write_column(zone: object, name: str, cells: "list[str]", seed: int) -> "list[str] | None":
    """A column of the description's twin written again in the real column's templates; None where the zone leaves it.

    ``cells`` are the description's twin's cells of the column. Each
    different value outside the spellings the entry keeps is written once
    anew, by templates in proportion to the real rows each covers, the
    commonest values first (`_budgets`): so how many different values
    the column holds, how many rows hold each and which rows share one
    stand; each new value keeps the old one's length where its template
    can, and its counts of figures and of a code's alphabet. A column of
    record numbers is left as it is where every cell already wears a
    template and its rules (`_already_written`). A held column
    (`MODE_HELD`) has as many blank cells filled as the real column
    held. A column of a person's details (`MODE_DETAIL`) has each value
    written at its own length (`_detail_written`). Determinism: a function of the zone, the name, the cells and
    the seed. Raises `TextError` for a zone of another version; nothing
    else.
    """
    entries = _entries(zone)
    if name not in entries:
        return None
    entry = entries[name]
    if not isinstance(entry, dict) or "mode" not in entry or entry["mode"] not in MODES:
        return None
    if entry["mode"] == MODE_CENSUS:
        return _census_dealt(entry, cells)
    writer = _writer_of(entry, _stream(seed, name, "text"))
    if writer.mode == MODE_HELD:
        return _held_filled(writer, cells, name, seed)
    if writer.style != "words" and not writer.keys:
        return None
    if writer.mode == MODE_IDENTIFIER and (_already_written(writer, cells) or _wider_than_real(writer, cells)):
        return None
    counts: "dict[str, int]" = {}
    for row in range(len(cells)):
        cell = _text(cells[row])
        if cell in writer.keep or not parsing.trimmed(cell):
            continue
        counts[cell] = (counts[cell] if cell in counts else 0) + 1
    if not counts:
        return None
    for cell in writer.keep:
        writer.written |= {cell}
        writer.folded |= {parsing.folded(cell)}
    if "list" in writer.entry:
        listed = _listed(writer, counts)
        return [listed[cell] if cell in listed else cell for cell in cells]
    if writer.mode == MODE_DETAIL and writer.style == "words":
        if not writer.keys:
            return None
        detailed = _detail_written(writer, counts)
        return [detailed[cell] if cell in detailed else cell for cell in cells]
    total = sum(counts[cell] for cell in counts)
    lengths = [len(cell) for cell in counts]
    words = [parsing.token_count(cell) for cell in counts]
    bounds = (min(lengths), max(lengths), min(words), max(words))
    keys, budgets = _budgets(writer, total)
    # The commonest values first, a tie by the value: the same values and counts are written alike whatever rows hold
    # them (a key column the keyed zone dealt and the same column it did not).
    order = [cell for _count, cell in sorted((-counts[cell], cell) for cell in counts)]
    renamed: "dict[str, str]" = {}
    assigned: "dict[str, str]" = {}
    left = [budget for budget in budgets]
    # ONE VALUE AT EACH END: the first value of the column's least length, of its greatest, of its fewest words and of
    # its most is written to keep that end; every other value's length is its template's own (`_value_for`).
    anchors: "dict[str, tuple[int, ...]]" = {}
    for wanted_at in range(4):
        for cell in order:
            measure = len(cell) if wanted_at < 2 else parsing.token_count(cell)
            if measure == bounds[wanted_at]:
                anchors[cell] = (anchors[cell] if cell in anchors else ()) + (wanted_at,)
                break
    free_lengths = typing.cast("list[int]", writer.entry["free_lengths"]) if "free_lengths" in writer.entry else []
    worn = _worn_templates(writer, keys, order)
    worn_places = {worn[cell] for cell in worn}
    for cell in order:
        place = 0
        for at in range(len(keys)):
            if left[at] > left[place]:
                place = at
        # ...A RECORD NUMBER THE DESCRIPTION'S TWIN WROTE IN A REAL TEMPLATE STAYS IN IT (lane TEXTZONE): that twin
        # holds the published count of each layout exactly, so a value keeps its layout, and a value it wrote in no
        # real template (wider than the real) goes to a template none of its values wears (`_worn_templates`).
        if cell in worn:
            place = worn[cell]
        elif worn:
            spare = [at for at in range(len(keys)) if at not in worn_places]
            if spare:
                place = sorted((-left[at], at) for at in spare)[0][1]
        key = keys[place]
        if key and not _slotted(writer, key) and _used_once(writer, key):
            others = [at for at in range(len(keys)) if keys[at] == "" or _slotted(writer, keys[at])
                      or not _used_once(writer, keys[at])]
            if others:
                place = sorted((-left[at], at) for at in others)[0][1]
                key = keys[place]
        left[place] = left[place] - counts[cell]
        target = 0
        if not key and free_lengths and writer.mode == MODE_FREE:
            drawn_length = free_lengths[_below(writer.state, len(free_lengths))]
            target = min(bounds[1], max(bounds[0], int(f"{drawn_length}")))
        renamed[cell] = _value_for(writer, cell, key, bounds, anchors[cell] if cell in anchors else (), target)
        # ...A TEMPLATE WITH NO FRESH VALUE LEFT (a short one, `<n>m`, most of whose values are published levels)
        # hands the value to the others, the most rows still owed first.
        if renamed[cell] == cell and key:
            for _left, at in sorted((-left[other], other) for other in range(len(keys)) if keys[other] != key):
                if keys[at] and not _slotted(writer, keys[at]) and _used_once(writer, keys[at]):
                    continue
                renamed[cell] = _value_for(writer, cell, keys[at], bounds, (), target)
                if renamed[cell] != cell:
                    key = keys[at]
                    left[at] = left[at] - counts[cell]
                    break
        assigned[cell] = key
    if writer.style == "words" and writer.mode == MODE_FREE:
        _balanced(writer, counts, renamed, assigned, bounds, anchors)
    written: "list[str]" = []
    for cell in cells:
        written += [renamed[cell] if cell in renamed else cell]
    return written


def _balanced(writer: _Writer, counts: "dict[str, int]", renamed: "dict[str, str]", assigned: "dict[str, str]",
              bounds: "tuple[int, int, int, int]", anchors: "dict[str, tuple[int, ...]]") -> None:
    """THE COLUMN'S LENGTH IN ALL KEPT: the values written anew, taken together, as long as the description's twin's.

    The description publishes a free-text column's average length, and
    where its values are each held once it holds it exactly. The new
    values' lengths are their templates' own, so their sum lands near
    the old one, not on it; values held by fewest rows (a value at the
    column's ends' anchors aside) are then drawn again, each one step
    longer or shorter in its own template and never past an end, until
    the sums agree or `BALANCE_TRIES` draws are spent.
    """
    shortest, longest, fewest, most = bounds
    gap = 0
    for cell in counts:
        gap = gap + counts[cell] * (len(cell) - len(renamed[cell]))
    if gap == 0:
        return
    order = [cell for _count, _length, cell in sorted((counts[cell], len(cell), cell) for cell in counts)]
    order = order + order + order
    spent = 0
    for cell in order:
        if gap == 0 or spent >= BALANCE_TRIES:
            return
        count = counts[cell]
        key = assigned[cell] if cell in assigned else ""
        old = renamed[cell]
        if count > abs(gap) or old == cell or (key and not _slotted(writer, key)) or cell in anchors:
            continue
        wanted_class = _class_of(old)
        step = 1 if gap > 0 else -1
        if not key:
            # A cell of the chain is cut at any length: it takes as much of the gap as stays inside the ends.
            reach = max(1, len(old) // 10)
            room = (longest - len(old)) if gap > 0 else (len(old) - shortest)
            step = step * max(0, min(abs(gap) // count, reach, room))
            if step == 0:
                continue
        for _attempt in range(8):
            spent = spent + 1
            drawn = _cell_of(writer, key) if key else _free_drawn(writer, len(old) + step)
            found = _class_of(drawn)
            if (len(drawn) != len(old) + step or not _fresh(writer, drawn) or found[0] != wanted_class[0]
                    or found[1] != wanted_class[1] or not shortest <= len(drawn) <= longest
                    or not fewest <= found[2] <= most):
                continue
            if len(old) <= FRESH_CAP:
                writer.written -= {old}
                writer.folded -= {parsing.folded(old)}
            renamed[cell] = _take(writer, drawn)
            gap = gap - count * step
            break


def _worn_templates(writer: _Writer, keys: "list[str]", cells: "list[str]") -> "dict[str, int]":
    """For a column of record numbers, each different value of the description's twin that already wears one of the
    zone's templates (its runs read as the real cells' are), and that template's place in ``keys``; nothing for words."""
    worn: "dict[str, int]" = {}
    if writer.style == "words":
        return worn
    for cell in cells:
        if _holds_a_mark(cell):
            continue
        key, _runs = _run_key(run_tokens(cell, writer.style), writer.kept)
        for at in range(len(keys)):
            if keys[at] == key:
                worn[cell] = at
    return worn


def _slotted(writer: _Writer, key: str) -> bool:
    """Whether a template holds a slot (one without slots is one value, written once)."""
    return len(typing.cast("list[object]", writer.templates[key]["slots"])) > 0


def _used_once(writer: _Writer, key: str) -> bool:
    """Whether a template without slots has had its one value written."""
    template_text = ""
    for part in writer.parts[key]:
        template_text = template_text + part[1:]
    return template_text in writer.written


def _wider_than_real(writer: _Writer, cells: "list[str]") -> bool:
    """Whether every key of the description's twin is longer than every real key: those keys are off the real by their
    width alone, and a twin linked to this table joins it only by keys that clear that width (`inside_links.link`
    refuses a linked twin's key shorter than the bound), so the zone leaves them as they are."""
    longest = writer.entry["longest"] if "longest" in writer.entry else None
    if not isinstance(longest, int) or isinstance(longest, bool):
        return False
    shortest = -1
    for cell in cells:
        text = _text(cell)
        if not parsing.trimmed(text) or text in writer.keep:
            continue
        shortest = len(text) if shortest < 0 else min(shortest, len(text))
    return shortest > longest


def _already_written(writer: _Writer, cells: "list[str]") -> bool:
    """Whether every cell of a key column already wears a template and keeps its rules (the zone then leaves it)."""
    seen = 0
    for cell in cells:
        text = _text(cell)
        if not parsing.trimmed(text) or text in writer.keep or _holds_a_mark(text):
            continue
        seen = seen + 1
        if seen > 2000:
            break
        key, runs = _run_key(run_tokens(text, writer.style), writer.kept)
        if key not in writer.templates:
            return False
        template = writer.templates[key]
        slots = typing.cast("list[dict[str, object]]", template["slots"])
        if template["luhn"] is True and not _luhn_ok(_joined_digits(runs)):
            return False
        if template["ipv4"] is True and any(int(written) > 255 for _kind, written in runs):
            return False
        for place in range(len(slots)):
            # A place of a run of hexadecimal or base 64 that the real writes in four characters or fewer is a rule of
            # the layout (a UUID's version and variant); a run of figures' narrow places are the range of numbers
            # issued, which the description's twin keeps off the real on purpose (its rules, a check figure and an
            # IPv4 address's bound, are read above).
            if f"{slots[place]['class']}" not in ("h", "b"):
                continue
            alphabets = typing.cast("list[str]", slots[place]["places"]) if "places" in slots[place] else []
            written = runs[place][1]
            for spot in range(min(len(alphabets), len(written))):
                if 1 <= len(alphabets[spot]) <= 4 and written[spot] not in alphabets[spot]:
                    return False
    return True


def _held_filled(writer: _Writer, cells: "list[str]", name: str, seed: int) -> "list[str] | None":
    """A held column's blank cells filled, as many as the real column held values the description held."""
    blanks = [row for row in range(len(cells)) if not parsing.trimmed(_text(cells[row]))]
    present = len(cells) - len(blanks)
    real_present = int(f"{writer.entry['present']}")
    wanted = min(len(blanks), max(0, real_present - present))
    if wanted <= 0 or not writer.keys:
        return None
    state = _stream(seed, name, "held rows")
    chosen = [row for row in blanks]
    for place in range(wanted):
        other = place + _below(state, len(chosen) - place)
        chosen[place], chosen[other] = chosen[other], chosen[place]
    filled = [cell for cell in cells]
    keys, budgets = _budgets(writer, wanted)
    queue: "list[str]" = []
    for place in range(len(keys)):
        for _row in range(budgets[place]):
            queue += [keys[place]]
    for at in range(len(queue)):
        other = at + _below(writer.state, len(queue) - at)
        queue[at], queue[other] = queue[other], queue[at]
    for place in range(wanted):
        key = queue[place] if place < len(queue) else writer.keys[0]
        filled[chosen[place]] = _cell_of(writer, key) if key else _free_drawn(writer, 12)
    return filled
