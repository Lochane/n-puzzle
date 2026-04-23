NAME = npuzzle

venv:
	python3 -m venv .venv

install:
	source .venv/bin/activate;\
	pip install -r requirements.txt;\

run:
	python3 main.py

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

fclean : clean

re: fclean run

.PHONY: run clean fclean re
