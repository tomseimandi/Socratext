"""
Formatter for Label Studio annotations.
"""
import os
from typing import Dict, Tuple
from utils import get_project_root


class LabelStudioJsonFormatter:
    """
    Formatter for Label Studio json data.
    """

    def __init__(
        self,
        keep_unlabeled_boxes: bool = True
    ):
        """
        Constructor.

        keep_unlabeled_boxes (bool): If True, unlabeled boxes are
            kept in the data.
        """
        self.keep_unlabeled_boxes = keep_unlabeled_boxes

    def format_data(self, data):
        """
        Format raw Label Studio data.

        Args:
            data (List): Raw Label Studio data.
        """
        formatted_data = []
        substring_to_remove = "/data/local-files/?d="

        for image_data in data:
            image_path = os.path.join(
                get_project_root(),
                "data/sample/",
                image_data["data"]["image"].replace(substring_to_remove, "")
            )
            
            image_annotation = image_data["annotations"][0]
            image_words, image_labels, image_boxes = self.format_image_annotation(
                image_annotation
            )

            formatted_data.append(
                {
                    "path": image_path,
                    "words": image_words,
                    "boxes": image_boxes,
                    "labels": image_labels,
                }
            )

        return formatted_data

    def format_preannotated_data(self, data):
        """
        Format prelabeled Label Studio data which has not been
        annotated, for inference purposes. Prelabeling has been 
        done using DoctrTransformer() and AnnotationJsonCreator.

        Args:
            data (List): Label Studio format preannotated data.
        """
        formatted_data = []

        for image_data in data:
            image_path = os.path.join(
                get_project_root(),
                "data/sample/",
                image_data["data"]["image"]
            )

            image_annotation = image_data["predictions"][0]
            image_words, image_labels, image_boxes = self.format_image_annotation(
                image_annotation
            )

            formatted_data.append(
                {
                    "path": image_path,
                    "words": image_words,
                    "boxes": image_boxes,
                    "labels": image_labels,
                }
            )

        return formatted_data

    @staticmethod
    def filter_data(formatted_data):
        """
        Filter formatted data. Only keeps images for which paths exist.

        Args:
            formatted_data (List): Formatted Label Studio data.
        """
        filtered_data = []

        for image_data in formatted_data:
            exists = os.path.exists(image_data["path"])
            if exists:
                filtered_data.append(image_data)

        return filtered_data

    def format_image_annotation(self, image_annotation: Dict) -> Tuple:
        """
        Formats the annotation dictionary for a single image.

        Args:
            formatted_data (List): Formatted Label Studio data.
        """
        words = []
        boxes = []
        labels = []

        for single_annotation in image_annotation["result"]:
            value = single_annotation["value"]
            if "rectanglelabels" not in value.keys():
                if not self.keep_unlabeled_boxes:
                    continue
                else:
                    label = "other_element"
            else:
                label = value["rectanglelabels"][0]

            # x, y, width, height are already normalized and in 0-100
            # For LayoutLMv2 we want them in 0-1000
            x = value["x"]
            y = value["y"]
            width = value["width"]
            height = value["height"]

            # rotation = value["rotation"]
            # Ignoring the rotation parameter for now

            # TODO : clarify this section
            #  [x1, y1, x3, y3] format
            x1 = 10 * x
            # y1 = 10 * (100 - y - height)
            # y1 = 10 * (y + height)
            # y1 = 10 * (100 - y)
            y1 = 10 * y
            x3 = 10 * (x + width)
            # y3 = 10 * (100 - y)
            # y3 = 10 * y
            # y3 = 10 * (100 - y - height)
            y3 = 10 * (y + height)

            boxes.append([int(coord) for coord in [x1, y1, x3, y3]])
            try:
                words.append(single_annotation["meta"]["text"][0])
            except KeyError:
                words.append("")
            labels.append(label)

        return words, labels, boxes
