
from pathlib import Path
import random
from concurrent.futures  import ProcessPoolExecutor as PPE
def deal(path):
  target = Path( f'target_dir/' + str(path).split('/').pop() )
  if target.exists():
    # do nothing
    return  
  # do some heavy process
  target.open('w').write( 'some_heavy_output' )

paths = [path for path in Path('source_dir/').glob('*')]
random.shuffle(paths) # shuffle
with PPE(max_workers=64) as exe:
  exe.map(deal, paths)
