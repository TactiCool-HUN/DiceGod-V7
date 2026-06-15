from pathlib import Path
import json


input_path = Path('databases/markov_studies/562373378967732226.txt')
output_path = Path('databases/markov_studies/562373378967732226.txt')


def write(my_dict):
	with open("fixer_words.json", "w") as f:
		json.dump(my_dict, f)


def load():
	with open("fixer_words.json") as f:
		return json.load(f)


def fix():
	my_dict = load()
	text = input_path.read_text(encoding='utf-8')
	
	lines = text.split('\n')
	for i, line in enumerate(lines):
		if 'ï¿½' in line:
			words = line.split(' ')
			for j, word in enumerate(words):
				if 'ï¿½' in word:
					if word in my_dict.keys():
						word = my_dict[word]
					else:
						for k in range(1, len(word)):
							if word[:len(word) - k] in my_dict.keys():
								response = input(f'Line: {line}\nWord: {word} ({word[:len(word) - k]})\nFix: {my_dict[word[:len(word) - k]]}?\nWrite approve or the fixed wordSLICE.')
								if response.lower() == 'approve':
									word = my_dict[word[:len(word) - k]] + word[len(word) - k:]
									break
								else:
									my_dict[word[:len(word) - k]] = response
									word = response + word[len(word) - k:]
									write(my_dict)
									break
						else:
							response = input(f'Line: {line}\nWord: {word}\nWrite fixed word.')
							my_dict[word] = response
							word = response
							write(my_dict)
					words[j] = word
			line = ' '.join(words)
			lines[i] = line
	text = '\n'.join(lines)

	output_path.write_text(text, encoding='utf-8')


if __name__ == '__main__':
	fix()


pass
