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
