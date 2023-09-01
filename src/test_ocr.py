"""
Script to test a model but using a custom OCR engine.
"""
from pathlib import Path
import mlflow
import sys
from transformers import (
    LayoutXLMTokenizerFast,
    LayoutXLMProcessor,
    LayoutLMv2ImageProcessor
)
from PIL import Image, ImageOps
from torch.nn.functional import softmax
from util.plot import plot_predictions, plot_boxes, plot_doctr_boxes, plot_predictions_with_filter
import torch
from preprocessing.doctr_utils import DoctrTransformer
from data.annotation_utils import AnnotationJsonCreator
from data.formatter import LabelStudioJsonFormatter


def test_ocr(remote_server_uri, run_id, image_path):
    """
    Test LayoutXLM model with custom OCR.

    Args:
        remote_server_uri (str): MLflow server UI.
        run_id (str): Run id.
        image_path (str): Image path.
    """
    tokenizer = LayoutXLMTokenizerFast.from_pretrained(
        "microsoft/layoutxlm-base"
        )
    processor = LayoutXLMProcessor(
        LayoutLMv2ImageProcessor(
            apply_ocr=False
        ),
        tokenizer
    )

    image_path = Path(image_path)
    # Get path and image
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)

    # Get path and image
    doctr_doc = DoctrTransformer().transform([image_path])
    annotations = AnnotationJsonCreator([image_path]).transform(doctr_doc, upload=False)

    # We want keys "image_path", "words", "boxes"
    formatter = LabelStudioJsonFormatter(
        keep_unlabeled_boxes=True
    )
    formatted_annotations = formatter.format_preannotated_data(annotations)
    formatted_annotations = formatter.filter_data(formatted_annotations)

    image_data = formatted_annotations[0]
    words = image_data["words"]
    boxes = image_data["boxes"]

    assert len(words) == len(boxes)
    # Use processor to prepare everything
    encoded_inputs = processor(
        image,
        words,
        boxes=boxes,
        word_labels=[0 for box in boxes],
        max_length=512,
        return_token_type_ids=True,
        # padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    model_uri = "runs:/{}/model".format(run_id)
    model = mlflow.pytorch.load_model(model_uri)
    model.eval()
    outputs = model(batch=encoded_inputs)

    predictions = softmax(outputs["logits"].squeeze(), dim=1)
    predictions = torch.argmax(predictions, dim=1)

    plot_predictions_with_filter(
        image,
        boxes=encoded_inputs["bbox"].squeeze(),
        box_filter=encoded_inputs["labels"].squeeze(),
        predictions=predictions,
        save_path="test.png"
    )
    return


if __name__ == "__main__":
    # MLFlow params
    remote_server_uri = sys.argv[1]
    run_id = sys.argv[2]
    image_path = sys.argv[3]

    remote_server_uri = "https://projet-socratext-288591.user.lab.sspcloud.fr"
    run_id = "fbf483cc5043420bbc053fc8b1c4d1a4"
    image_path = "data/sample/20221108_230524.jpg"

    test_ocr(remote_server_uri, run_id, image_path)