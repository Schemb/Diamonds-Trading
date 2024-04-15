message ?= $(shell bash -c 'read -p "Enter commit message: " message; echo $$message')
git:
	git add .
	git commit . -m "$(message)"
	git push -u origin round2_template