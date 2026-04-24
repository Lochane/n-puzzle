import sys
from pathlib import Path
from algo import A_star

# if not sys.argv[1]:
# 	print ("Missing file!\nUsage: python3 main.py <path/to/puzzle/file.txt>")
# 	exit(1)

# file_path = Path(sys.argv[1])
# if file_path.suffix != ".txt":
# 	print(f"'{file_path.name}' is something else than a .txt file.")
# 	exit(1)

# try:
# 	with open(file_path) as file:
# 		print(file)
# except Exception as e:
# 	print(f"Unexpected error: {e}")
# 	exit(1)

algo = A_star()
algo.run()