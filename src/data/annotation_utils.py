from pathlib import Path
from typing import List
import json
import os
import pandas as pd
from doctr.io import Document

from preprocessing.doctr_utils import get_list_words_in_page


class AnnotationJsonCreator:
    """class for generating json files in the LabelStudio json format containing the bboxes from doctr"""
    def __init__(self, raw_documents: List[Path], output_path: Path = None, predictions: List = None):
        self.output_path = output_path
        self.raw_documents = raw_documents
        self.predictions = predictions

    def fit(self, doctr_documents: List[Path], **kwargs):
        return self

    def transform(self, doctr_documents: List[Document], upload: bool = False):
        
        annotations = []
        counter = 0
        for doc_id, doc in enumerate(doctr_documents):
            image_path = self.raw_documents[doc_id]
            image_name = Path(image_path).stem

            dict_image = {
                "data": {"image": os.path.join("s3://", image_path)},
                "predictions": [{"result": [], "score": None}],
            }  # result: list de dict pour chaque BBox

            page = doc.pages[0]
            list_words_in_page = get_list_words_in_page(page)
            height, width = page.dimensions[0], page.dimensions[1]
            id_annotation = 0
            for word in list_words_in_page:
                prediction = self.predictions[counter] if self.predictions is not None else None
                id_annotation += 1
                label = word.value
                xmin, ymin = word.geometry[0][0], word.geometry[0][1]
                xmax, ymax = word.geometry[1][0],  word.geometry[1][1]
                width_a, height_a = xmax - xmin, ymax - ymin
                dict_annotation = {'id': 'result{}'.format(id_annotation),
                                   "meta": {"text": [label]},
                                   'type': 'rectanglelabels', 'from_name': 'label', 'to_name': 'image',
                                   'original_width': width, 'original_height': height, 'image_rotation': 0,
                                   'value': {'rotation': 0, 'x': xmin*100, 'y': ymin*100,
                                          'width': width_a*100, 'height': height_a*100,
                                          'rectanglelabels': [prediction]}}
                dict_image["predictions"][0]["result"].append(dict_annotation)
                counter += 1
            annotations.append(dict_image)

            if self.output_path is not None:
                json_path = os.path.join(
                    self.output_path,
                    f"{image_name}.json"
                )
                with open(json_path, 'w') as fp:
                    json.dump(dict_image, fp)

        return annotations


class LabelStudioConvertor:
    """class for converting label studio json files into dataframe
    By defautl, annotations = True, meaning that the json is the output file of label studio
    If annotations = False, the json is the output file of the class AnnotationJsonCreator"""

    def __init__(self, jsonfile: Path, output_path: Path = None, annotations: bool = True):
        self.jsonfile = jsonfile
        self.output_path = output_path
        self.annotations = annotations
        self.type = "annotations" if self.annotations else "predictions"


    def transform(self, all_columns: bool = False, sep: str = "\t"):
        self.sep = sep
        data_file = open(self.jsonfile)
        data = json.load(data_file)

        df_annotations = pd.DataFrame()
        df = pd.json_normalize(data)
        df_col = ["file_upload", "created_at", "updated_at", "project", "data.image"]
        if self.type == "predictions":
            df_col = ["data.image"]
        for index, row in df.iterrows():
            df_temp = pd.json_normalize(row[self.type])
            df_temp_col = [x for x in df_temp.columns if "result" not in x]
            for index2, row2 in df_temp.iterrows():

                df2temp = pd.json_normalize(row2["result"])
                for col in df_col:
                    df2temp[col] = df._get_value(index, col)
                for col in df_temp_col:
                    df2temp[col] = df_temp._get_value(index2, col)
                if self.type == "annotations":
                    if "value.choices" in df2temp.columns:
                        df2temp["document_class"] = df2temp["value.choices"].map(
                            lambda x: x[0] if (pd.isna(x) == False and len(x) > 0) else 'O')
                        df2temp["document_class"] = df2temp["document_class"].max()
                df_annotations = pd.concat([df_annotations, df2temp])

        df_annotations["label"] = df_annotations["value.rectanglelabels"].map(
            lambda x: x[0] if (pd.isna(x)==False and len(x)>0) else 'O')

        # rename col names
        dict_rename = {'value.x': 'min_x', 'value.y': 'min_y'}
        df_annotations.rename(columns=dict_rename, inplace=True)

        # clean columns
        df_annotations["word"] = df_annotations["meta.text"].apply(lambda x: x[0] if isinstance(x, list) else x)
        df_annotations["page_id"] = 0
        df_annotations["max_x"] = df_annotations["min_x"] + df_annotations["value.width"]
        df_annotations["max_y"] = df_annotations["min_y"] + df_annotations["value.height"]
        df_annotations["document_name"] = df_annotations["data.image"].apply(lambda x: x.split("/")[-1])

        # keep only minimal columns
        if all_columns == False:
            minimal_col_list = ['word', 'min_x', 'min_y', 'max_x', 'max_y', 'page_id', 'document_name', 'label',
                                'document_class',
                                "completed_by.email",
                                'original_width', 'original_height']
            if self.type == "predictions":
                minimal_col_list = [x for x in minimal_col_list if x not in ['document_class', "completed_by.email"]]

            df_annotations = df_annotations[minimal_col_list]

        for col in ['min_x','min_y','max_x','max_y']:
            df_annotations[col] = df_annotations[col] / 100

        if self.output_path is not None:
            df_annotations.to_csv(self.output_path, index=False, sep=self.sep)

        return df_annotations
