NAME = npuzzle

venv:
	python3 -m venv .venv

install:
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python main.py

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

fclean: clean

re: fclean run

.PHONY: venv install run clean fclean re