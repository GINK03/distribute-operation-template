# distribute-operation-template
運用でカバーを前提とした、分散処理で重い操作を行うときの、オペレーション

## Kaggle Google Landmark　Recognission + Retrievalで必要となったテク

(概要を書く)

## SSHFSがファイルの破損がなく扱えて便利
sshfsはssh経由で、ファイルシステムをマウントする仕組みですが、安定性が、他のリモート経由のファイルシステムに対して高く、一つのハードディスクに対して、sshfs経由で多くのマシンからマウントしても、問題が比較的軽微に行えます。  
また、ホストから簡単に進捗状況をチェックすこともできます。  

この構造のメリットは、横展開するマシンの台数に応じて、早くできることと、あまりコードをいじらずに、分散処理できます。  

```python
...
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

## Overheadを見極める

## Forkコスト最小化とキャッシュ化
