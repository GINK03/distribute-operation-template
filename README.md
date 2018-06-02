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

## Forkコスト最小化とキャッシュ化
