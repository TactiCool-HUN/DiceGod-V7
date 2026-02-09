from collections import defaultdict
import random
from pathlib import Path
import asyncio

folder = Path("databases/markov_studies")
files_dict = {
	int(f.stem): f.read_text(encoding="cp1252")
	for f in folder.iterdir()
	if f.is_file() and f.suffix == ".txt"
}

max_order = 3


async def markov_learner(text: str, guild: int):
	text = text.replace("<@953258800759070720> ", "")
	files_dict[guild] = f"{files_dict.get(guild, '')}\n{text}"


async def markov_saver():
	while True:
		await asyncio.sleep(300)
		for guild in files_dict:
			with open(f"databases/markov_studies/{guild}.txt", "w", encoding="cp1252") as f:
				f.write(files_dict[guild])


# noinspection SpellCheckingInspection
def markovifier(guild: int):
	text = files_dict[guild]
	return _markov_from_text(text, 100)


def _markov_from_text(text: str, max_words = 100) -> str:
	chain = _build_chain(text)
	return _generate_message(chain, max_words)
	

def _build_chain(text):
	words = text.split()
	chain = defaultdict(list)

	for i in range(len(words)):
		for k in range(1, max_order + 1):
			if i - k < 0:
				continue
			key = tuple(words[i - k:i])
			chain[key].append(words[i])

	return chain


def _next_word(chain, context):
	for k in range(max_order, 0, -1):
		key = tuple(context[-k:])
		if key in chain:
			return random.choice(chain[key])
	return random.choice(random.choice(list(chain.values())))


def _generate_message(chain, max_words):
	start = random.choice(list(chain.keys()))
	message = list(start)

	while len(message) < max_words:
		word = _next_word(chain, message)
		message.append(word)

	return ' '.join(message)


pass
