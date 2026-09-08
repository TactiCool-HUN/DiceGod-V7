VERSION: int = 0

TEST_GUILD: int = 953258116496097340
CORNER: int = 562373378967732226
SYNC: bool = False
LAUNCH_GOD: bool = True
SILENT_DB: bool = False

ALPHABET_UPPER: list[str] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ALPHABET_LOWER: list[str] = [letter.lower() for letter in ALPHABET_UPPER]

EMOJIS = [  # that dicegod likes :3
	'✨',
	'❤️',
	'💖',
	'💜',
	'🐸',
	'<:idek:694605001502228540>',
	'<:zorablush:1021403403768844308>',
	'<:UwU:959931778905276456>',
	'<:Kyrihihihi:1058348961523576872>',
	'<:point:951578243415302235>',
	'<:diebish:694527515921743883>',
	'<:suneannoyed:1240006684504752199>',
]

COLOR: dict[str, str] = {
	'red_dark': '0x7C0A02',
	'yellow_dark': '0xFFD300',
	'green_moss': '0x466D1D',
	'orange_burnt_amber': '0x8A3324',
	'blue_yale': '0x0E4C92',
	'black': '0x000000',
	'white': '0xFFFFFF',
	'tactical_blue': '0x4177B3',
}
DAMAGE_TYPES = {
	"piercing": "🗡️",
	"bludgeoning": "🔨",
	"slashing": "🪓",
	"acid": "🧪",
	"fire": "🔥",
	"necrotic": "💀",
	"void": "💀",
	"poison": "🐍",
	"cold": "❄️",
	"radiant": "☀️",
	"vitality": "☀️",
	"force": "☄️",
	"thunder": "🔊",
	"sonic": "🔊",
	"lightning": "⚡",
	"electricity": "⚡",
	"psychic": "🧠",
	"healing": "❤️‍🩹"
}
DG_FAVOURITE_EMOJIS = {
	"✨": 1,
	"❤️": 1,
	"💖": 1,
	"💜": 1,
	"🐸": 1,
	"<:idek:694605001502228540>": 1,
	"<:zorablush:1021403403768844308>": 1,
	"<:UwU:959931778905276456>": 1,
	"<:Kyrihihihi:1058348961523576872>": 1,
	"<:point:951578243415302235>": 1,
	"<:diebish:694527515921743883>": 1,
}

VETERANCY_ROLES = {
	0: 1170854299786563735,
	1: 562619225928105984,
	2: 562618251079712796,
	6: 695250745276235807,
	11: 869611219693236234,
	16: 1170854863068991528,
	21: 1170854843611615252,
	26: 1524666095351500820,
	31: 1524666217002958882,
}
_sorted_thresholds = sorted(VETERANCY_ROLES.keys())
_max_threshold = _sorted_thresholds[-1]
_expanded = {}
for _n in range(_max_threshold + 1):
	_current_role = VETERANCY_ROLES[_sorted_thresholds[0]]
	for threshold in _sorted_thresholds:
		if threshold <= _n:
			_current_role = VETERANCY_ROLES[threshold]
		else:
			break
	_expanded[_n] = _current_role
VETERANCY_ROLE_BY_POINT = _expanded
VETERANCY_ROLES = list(VETERANCY_ROLES.values())
