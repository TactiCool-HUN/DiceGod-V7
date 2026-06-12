from chatbot.markov_fixer.migration import migrate
from chatbot.markov_fixer.uncorruptor import run_fix

while True:
	match input('Migrate: m\nFix: f\nExit: e\n\n'):
		case 'm':
			migrate()
		case 'f':
			run_fix()
		case 'e':
			break


pass
