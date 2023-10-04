#!/bin/bash
mc cp s3/projet-socratext/tickets/labeled_sample.json data/
mc cp s3/projet-socratext/tickets/new_labeled_sample.json data/
mc cp s3/projet-socratext/tickets/images.zip data/sample/
mc cp -r s3/projet-socratext/labelstudio/ls_data/ data/sample/
cd data/sample
unzip images.zip

python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

# s3 config for Pytorch Lightning
# mkdir -p ~/.config/fsspec && touch ~/.config/fsspec/conf.json
# echo '{"s3": {"client_kwargs": {"endpoint_url": "https://minio.lab.sspcloud.fr"}}}' > ~/.config/fsspec/conf.json
