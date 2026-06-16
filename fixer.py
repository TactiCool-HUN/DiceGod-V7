from pathlib import Path
import string
import json
import re


input_path = Path('databases/markov_studies/562373378967732226.txt')
output_path = Path('databases/markov_studies/562373378967732226.txt')


def write(my_dict):
	with open("fixer_words.json", "w", encoding="utf-8") as f:
		json.dump(my_dict, f, ensure_ascii = False, indent = 2)


def load():
	try:
		with open("fixer_words.json", encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		with open("fixer_words.json", "w", encoding="utf-8") as f:
			json.dump(dict(), f)
		return load()


def fix(counter: bool):
	my_dict = load()
	text = input_path.read_text(encoding='utf-8')
	try:
		lines = text.split('\n')
		for i, line in enumerate(lines):
			if 'ï¿½' in line:
				punctuation = re.escape(string.punctuation.replace("'", ""))
				words = re.split(rf'([{punctuation}]| )', line)
				for j, word in enumerate(words):
					if 'ï¿½' in word:
						if not counter:
							print('-------------------')
						if j == 0 and word == 'ï¿½':
							if len(words) > 1 and words[j + 1][0].isupper():
								word = '-'
							else:
								word = '[?]'
						elif word in my_dict.keys() or word[0].lower() + word[1:] in my_dict.keys():
							lookup_key = word if word in my_dict else word[0].lower() + word[1:]
							if isinstance(my_dict[lookup_key], str):
								if not counter:
									print(f'Line: {line.replace("ï¿½", "_")}\nWord: {word.replace("ï¿½", "_")}\nAuto fixed with: {my_dict[lookup_key]}')
								if word[0].isupper() == my_dict[lookup_key][0].isupper() or word[0] == 'ï':
									word = my_dict[lookup_key]
								else:
									if word[0].isupper():
										word = my_dict[lookup_key][0].upper() + my_dict[lookup_key][1:]
									else:
										word = my_dict[lookup_key][0].lower() + my_dict[lookup_key][1:]
							elif not counter:
								response = input(f'Line: {line.replace("ï¿½", "_")}\nWord: {word.replace("ï¿½", "_")}\nOptions: {", ".join(my_dict[lookup_key])}\nWrite order number or fixed word: ')
								if response.isnumeric():
									word = my_dict[lookup_key][int(response)-1]
								else:
									my_dict[lookup_key] = response
									word = response
									write(my_dict)
						elif not counter:
							for k in range(1, len(word)):
								if word[:len(word) - k] in my_dict.keys():
									response = input(f'Line: {line.replace("ï¿½", "_")}\nWord: {word.replace("ï¿½", "_")}\nFix: {my_dict[word[:len(word) - k]]}{word[len(word) - k:]}\nWrite "1" to approve or the fixed FULL WORD: ')
									if response.lower() == '1':
										my_dict[word] = my_dict[word[:len(word) - k]] + word[len(word) - k:]
										word = my_dict[word[:len(word) - k]] + word[len(word) - k:]
										write(my_dict)
										break
									else:
										my_dict[word] = response
										word = response
										write(my_dict)
										break
							else:
								response = input(f'Line: {line.replace("ï¿½", "_")}\nWord: {word.replace("ï¿½", "_")}\nWrite fixed word: ')
								my_dict[word] = response
								word = response
								write(my_dict)
						words[j] = word
						line = ''.join(words)
				line = ''.join(words)
				lines[i] = line
		text = '\n'.join(lines)
		
		
		print(text.count('ï¿½'))
		if not counter:
			output_path.write_text(text, encoding='utf-8')
	except KeyboardInterrupt or Exception:
		if not counter:
			print("\nInterrupted — saving progress...")
			words[j] = word
			line = ''.join(words)
			lines[i] = line
			text = '\n'.join(lines)
			fix(True)
			output_path.write_text(text, encoding='utf-8')
			print("Saved.")
			return 'out'


if __name__ == '__main__':
	while True:
		response_outer = input('f for fix, c for count, else for exit\n')
		if response_outer == 'f':
			if fix(False) == 'out':
				break
		elif response_outer == 'c':
			fix(True)
		else:
			break


pass
