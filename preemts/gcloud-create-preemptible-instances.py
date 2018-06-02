import os

type = 'n1-highcpu-64'
image = 'nardtree-jupyter-1'

for i in range(0, 3):
  name = f'adhoc-preemptible-{i:03d}'
  ctx = f'gcloud compute instances create {name} --machine-type {type} --image {image} --preemptible'
  os.system(ctx)
