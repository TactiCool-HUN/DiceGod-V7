import markovify


def markov_learner(text: str):
	with open('databases/markov_studies.txt', 'a') as f:
		f.write(f'{text}\n')


def markovifier():
	with open('databases/markov_studies.txt', 'r') as f:
		markov_chain_model = markovify.Text(f, retain_original = False)

	return markov_chain_model.make_short_sentence(50, 20, tries = 20)


pass
