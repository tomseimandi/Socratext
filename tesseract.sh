#!/bin/bash
# Installing packages
sudo apt-get update
sudo apt-get upgrade -y
sudo apt install software-properties-common
sudo apt-get update
sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel
sudo apt -y install python3-opencv
sudo apt -y install tesseract-ocr
sudo apt -y install tesseract-ocr-fra
sudo apt -y install poppler-utils
sudo apt -y install ghostscript python3-tk