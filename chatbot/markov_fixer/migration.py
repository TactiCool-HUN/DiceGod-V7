from pathlib import Path

folder = Path("databases/markov_studies")

for f in folder.iterdir():
	if f.is_file() and f.suffix == ".txt":
		# Read with cp1252, replacing undecodable bytes rather than crashing
		text = f.read_text(encoding="cp1252", errors="replace")
		# Write back as UTF-8
		f.write_text(text, encoding="utf-8")
		print(f"Migrated {f.name}")