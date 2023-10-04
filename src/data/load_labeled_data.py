"""
In this script we load data that was labeled with LabelStudio.
"""
from utils import fs
import json
import tempfile
from pathlib import Path


def main():
    """
    Main method.
    """
    formatted_annotations = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for remote_path in fs.ls("projet-socratext/labelstudio/ls_labels"):
            file_id = Path(remote_path).stem
            if file_id == ".keep":
                continue
            local_path = tmpdir + f"/{file_id}.json"
            fs.get(remote_path, local_path)
            formatted_annotation = {}
            with open(local_path) as f:
                single_annotation = json.load(f)
                file_name = Path(single_annotation["task"]["data"]["image"]).name
                formatted_annotation["data"] = {
                    "image": file_name
                }
                formatted_annotation["annotations"] = [{
                    "result": single_annotation["result"]
                }]
                formatted_annotations.append(formatted_annotation)

    with open('data/new_labeled_sample.json', 'w') as fout:
        json.dump(formatted_annotations, fout)


if __name__ == "__main__":
    main()
