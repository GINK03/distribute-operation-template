import random
from pathlib import Path
for i in range(100000):
  Path(f'source_dir/{i:09d}').open('w').write( str(random.random()) )
