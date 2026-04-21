NAME = npuzzle

run:
	python3 main.py

clean:
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +

fclean : clean

re: fclean run

.PHONY: run clean fclean re
