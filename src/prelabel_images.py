"""
Script to prelabel images
"""
from data.annotation_utils import AnnotationJsonCreator
from preprocessing.doctr_utils import DoctrTransformer
from data.utils import fs
from pathlib import Path
import os
import sys
import tempfile


def main(data_path, output_path):
    # For now we assume images

    with tempfile.TemporaryDirectory() as tmpdirname:
        remote_paths = [
            Path(path)
            for path in fs.ls(data_path)
            if path.endswith((".jpg", ".jpeg", ".png"))
        ]
        # Download data from s3
        extensions = (".png", ".jpg", ".jpeg")
        for extension in extensions:
            try:
                fs.get(
                    data_path + "/*" + extension,
                    tmpdirname + "/",
                    recursive=True,
                )
            except FileNotFoundError:
                pass

        image_paths = [
            Path(os.path.join(tmpdirname + "/ls_data/", x))
            for x in os.listdir(tmpdirname + "/ls_data/")
            if x.endswith(extensions)
        ]
        image_paths.sort()

        list_doctr_docs = DoctrTransformer().transform(image_paths)
        annotations = AnnotationJsonCreator(
            remote_paths,
            output_path=tmpdirname
        ).transform(
            list_doctr_docs,
        )
        del annotations

        # Upload to s3
        try:
            fs.put(tmpdirname + "/*.json", output_path, recursive=True)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    data_path = sys.argv[1]
    output_path = sys.argv[2]

    main(data_path, output_path)
