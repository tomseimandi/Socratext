import mlflow
import sys
from transformers import (
    LayoutXLMTokenizerFast,
    LayoutXLMProcessor,
    LayoutLMv2ImageProcessor
)
from PIL import Image, ImageOps
from torch.nn.functional import softmax
from util.plot import plot_predictions
import torch


def test_no_ocr(remote_server_uri, run_id, image_path):
    """_summary_

    Args:
        remote_server_uri (_type_): _description_
        run_id (_type_): _description_
        image_path (_type_): _description_
    """
    # Engine mode
    engine_mode = 3
    custom_config = f'--oem {engine_mode}'

    # Set page segmentation mode
    page_segmentation_mode = 3
    custom_config += f' --psm {page_segmentation_mode}'

    # Specify language
    language = 'fra'
    custom_config += f' -l {language}'
    # Need custom config OR a way to filter on confidence level ? 

    tokenizer = LayoutXLMTokenizerFast.from_pretrained(
        "microsoft/layoutxlm-base"
        )
    processor = LayoutXLMProcessor(
        LayoutLMv2ImageProcessor(
            apply_ocr=True,
            ocr_lang="fra",
            tesseract_config=custom_config
        ),
        tokenizer
    )
    # This method first forwards the images argument to LayoutLMv2ImageProcessor.__call__.
    # In case LayoutLMv2ImagePrpcessor was initialized with apply_ocr set to True,
    # it passes the obtained words and bounding boxes along with the additional arguments
    # to call() and returns the output, together with resized images. In case
    # LayoutLMv2ImageProcessor was initialized with apply_ocr set to False, it
    # passes the words (`text/text_pair`) and `boxes` specified by the user along
    # with the additional arguments to [__call__()]
    # (/docs/transformers/v4.32.1/en/model_doc/layoutxlm#transformers.LayoutXLMTokenizer.__call__)
    # and returns the output, together with resized `images`.

    # Get path and image
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)

    # Use processor to prepare everything
    encoded_inputs = processor(
        image,
        max_length=512,
        # padding="max_length",
        truncation=True,
        return_token_type_ids=True,
        return_tensors="pt",
    )
    # 4 keys: 'input_ids', 'attention_mask', 'bbox', 'image'

    model_uri = "runs:/{}/model".format(run_id)
    model = mlflow.pytorch.load_model(model_uri)
    model.eval()
    outputs = model(batch=encoded_inputs)

    predictions = softmax(outputs["logits"].squeeze(), dim=1)
    predictions = torch.argmax(predictions, dim=1)

    plot_predictions(
        image,
        boxes=encoded_inputs["bbox"].squeeze(),
        predictions=predictions,
        save_path="test.png"
    )
    return


if __name__ == "__main__":
    # MLFlow params
    remote_server_uri = sys.argv[1]
    run_id = sys.argv[2]
    image_path = sys.argv[3]

    remote_server_uri = "https://projet-socratext-204045.user.lab.sspcloud.fr"
    run_id = "fbf483cc5043420bbc053fc8b1c4d1a4"
    image_path = "data/sample/20221108_230524.jpg"

    test_no_ocr(remote_server_uri, run_id, image_path)
