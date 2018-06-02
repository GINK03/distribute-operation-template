# distribute-operation-template
運用でカバーを前提とした、分散処理で重い操作を行うときの、オペレーション

## Kaggle Google Landmark　Recognission + Retrievalで必要となったテク

(概要を書く)

## SSHFSがファイルの破損がなく扱えて便利
sshfsはssh経由で、ファイルシステムをマウントする仕組みですが、安定性が、他のリモート経由のファイルシステムに対して高く、一つのハードディスクに対して、sshfs経由で多くのマシンからマウントしても、問題が比較的軽微に行えます。  
また、ホストから簡単に進捗状況をチェックすこともできます。  

この構造のメリットは、横展開するマシンの台数に応じて、早くできることと、あまりコードをいじらずに、分散処理できます。  
<div align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/40872867-ea2d8a0e-6690-11e8-942b-28dd83de2617.png">
</div>
<div align="center"> 図1. </div>

処理粒度を決定して、処理したデータはなにかキーとなる値か、なければ、hash値でファイルが処理済みかどうかを判断することで、効率的に分散処理することtができます。　　　

sshfs上の処理粒度に対してすでに、処理済みであれば、処理をスキップします。  

(sshfs上で行ったものは二度目はファイルが共有され、二度目は、処理されないので、効率的に処理できます)  
```python
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
```


## GCP Preemptible Instance(AWSのSpot Instance)を用いた効率的なスケールアウト
計算ノードは、全くの非同期で運用できるので、途中で唐突にシャットダウンされても問題がないので、　安いけどクラウド運営側の都合でシャットダウンされてしまう可能性があるけど、1/10 ~ 1/5の値段程度に収まる　GCP Preemptible InstanceやAWS　Spot　Instanceを用いることができます。  

Preemptibleインスタンスはgcloudコマンドでインストールできますが、このようにPythonなどのスクリプトでラップしておくとまとめて操作できて便利です。　　

**Preemptible インスタンスをまとめて作成**  
```python
import os

type = 'n1-highcpu-64'
image = 'nardtree-jupyter-1'

for i in range(0, 3):
  name = f'adhoc-preemptible-{i:03d}'
  ctx = f'gcloud compute instances create {name} --machine-type {type} --image {image} --preemptible'
  os.system(ctx)
```
このスクリプトでは、自分で作成した必要なライブラリがインストールされた状態のイメージ(nardtree-jupyter-1)からハイパフォーマンスのインスタンスを3大作成しています。

## GCPをMacBookなどのクライアントマシンから命令を送る
**Premptible インスタンスに必要なソフトをインストールして、sshfs経由でマウント**  
クライアントマシン（手元のMacBookなど）から、コマンドを実行させることができます。　　　

このオペレーションのなかに、学習用のスクリプトなどを入れておいても便利です。  

(GCP_NAME, GCP_KEY_NAMEは手元のパソコンの環境変数に設定しておくとよいです)  
```python
import os
GCP_NAME = os.environ['GCP_NAME']
GCP_KEY_NAME = os.environ['GCP_KEY_NAME']
names = [f'adhoc-preemptible-{i:03d}' for i in range(0, 3)]
commands = [  'sudo apt update', \
              'sudo apt-get install sshfs', \
              'mkdir machine', \
              f'sshfs 35.200.39.32:/home/{GCP_NAME} /home/{GCP_NAME}/machine -o IdentityFile=/home/{GCP_NAME}/.ssh/{GCP_KEY_NAME} -o StrictHostKeyChecking=no' ]

for name in names:
  for command in commands:
    base = f'gcloud compute ssh {GCP_NAME}@{name} --command "{command}"'
    os.system(base)
```

## Overheadを見極める
高速化の余地があるプログラムの最適化はどうされていますでしょうか。　　
私のつかっているヒューリスティックは、以下のプロセスで全体のプロセスを最適化します。　　　
1. コードの大まかな把握
2. htopを利用して、すべてのCPUのスレッドが100%使用されているか把握  

  \- **100%でない場合** -> ネットワーク or ディスクにオーバヘッドが存在するので最適化する　　

  \- **赤が支配的な場合** -> システムのオーバヘッドが大きくなっているので、結合方式がオーバーヘッドなので見直す 

  \- **緑が支配的な場合** -> CPU使用法はOK　　

3. アルゴリズムの最適化
  何らかのメジャーな方法でうまくやれる方法がないか探す
<div align="center">
  <img width="700px" src="https://user-images.githubusercontent.com/4949982/40873723-fda0e814-66a0-11e8-84d2-7da34da281e9.png">
</div>
<div align="center"> 図2.　 </div>

図2の例では、CPUはだいぶ空いており、コードとこの観測結果から、DISKのアクセスが間に合ってないと分かります。オンメモリで読み込むことや、よりアクセスの速いDISKを利用することが検討されます。  

## Forkコスト最小化とキャッシュ化
 マルチプロセッシングによるリソースの最大利用は便利な方法ですが、[spawn, fork, forkserverの方法が提供](https://docs.python.jp/3/library/multiprocessing.html)されています。  
 使っていて最もコスト安なのはforkなのですが、これでうまく動作しないことが稀にあって、spawnやforkserverに切り替えて用いることがあります。spawnが一番重いです。　　　
 
　forkでは親プロセスのメモリ内容をコピーしてしまうので、大きなデータを並列処理しようとすると、丸ごとコピーコストがかかり、小さい処理を行うためだけにメモリがいくら高速と言えど、細かく行いすぎるのは、かなりのコストになるので、バッチ的に処理する内容をある程度固めて行うべきです。　　　
 
 例えば、次のランダムな値を100万回、二乗するのをマルチプロセスで行うと、おおよそ、30秒かかります。  
```python
from concurrent.futures import ProcessPoolExecutor as PPE
import time
import random
args = [random.randint(0, 1_000) for i in range(100_000)]

def normal(i):
  ans = i*i
  return ans

start = time.time()
with PPE(max_workers=16) as exe:
  exe.map(normal, args)

print(f'elapsed time {time.time() - start}')
```
```console
$ python3 batch.py 
elapsed time 32.37867593765259
```
では、単純にある程度、データをチャンクしてマルチプロセスにします。  

すると、0.04秒程度になり、ほぼ一瞬で処理が完了します  

これはおおよそ、もとの速度の800倍です
```python
from concurrent.futures import ProcessPoolExecutor as PPE
import time
import random
data = [random.randint(0, 1_000) for i in range(100_000)]

tmp = {}
for index, rint in enumerate(data):
  key = index%16
  if tmp.get(key) is None:
    tmp[key] = []
  tmp[key].append( rint )

args = [ rints for key, rints in tmp.items() ] 
def batch(rints):
  return [rint*rint for rint in rints ]

start = time.time()
with PPE(max_workers=16) as exe:
  exe.map(batch, args)

print(f'elapsed time {time.time() - start}')
```python
$ python3 batch2.py 
elapsed time 0.035398244857788086
```


