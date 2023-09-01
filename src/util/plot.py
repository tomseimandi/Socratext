"""
Plotting utils.
"""
from typing import Tuple
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from mappings import id2label


palette_length = len(id2label)
palette = list(mcolors.TABLEAU_COLORS.keys())[:palette_length]
color2label = {}
for (id, label) in id2label.items():
    color = palette[id]
    color2label[color] = label


def resize_box(box, image_shape: Tuple[int, int], bbox_format=(1000, 1000)):
    bounding_box_max_width, bounding_box_max_height = bbox_format
    x0, y0, x1, y1 = box
    width, height = image_shape

    width_ratio = width / bounding_box_max_width
    height_ratio = height / bounding_box_max_height

    resized_x0 = int(x0 * width_ratio)
    resized_y0 = int(y0 * height_ratio)
    resized_x1 = int(x1 * width_ratio)
    resized_y1 = int(y1 * height_ratio)
    return resized_x0, resized_y0, resized_x1, resized_y1


def plot_predictions(image, boxes, predictions, save_path):
    # boxes: torch.Size([n, 4])
    # predictions: torch.Size([n, 9]) since there are 9 labels
    # Create figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    for box, prediction in zip(boxes, predictions):
        resized_box = resize_box(box, image.size)
        color = palette[prediction]
        # Create a Rectangle patch
        rect = patches.Rectangle(
            (resized_box[0], resized_box[1]),
            resized_box[2] - resized_box[0],
            resized_box[3] - resized_box[1],
            linewidth=1,
            edgecolor=color,
            facecolor=color,
            alpha=0.3
        )

        # Add the patch to the Axes
        ax.add_patch(rect)

    handles = [patches.Patch(color=color, label=label) for color, label in color2label.items()]
    plt.legend(handles=handles, bbox_to_anchor=(1, 0.5))

    plt.savefig(save_path, dpi=300)


def plot_boxes(image, boxes, save_path, bbox_format=(1000, 1000)):
    # boxes: torch.Size([n, 4])
    # Create figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    for box in boxes:
        resized_box = resize_box(box, image.size, bbox_format=(1000, 1000))
        # Create a Rectangle patch
        rect = patches.Rectangle(
            (resized_box[0], resized_box[1]),
            resized_box[2] - resized_box[0],
            resized_box[3] - resized_box[1],
            linewidth=1,
            alpha=0.3
        )

        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.savefig(save_path, dpi=300)


def plot_doctr_box(image, box, save_path):
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    x0 = box["value"]["x"]
    y0 = box["value"]["y"]
    x1 = x0 + box["value"]["width"]
    y1 = y0 + box["value"]["height"]

    box_coordinates = (x0, y0, x1, y1)
    resized_box = resize_box(box_coordinates, image.size, bbox_format=(100, 100))
    # Create a Rectangle patch
    rect = patches.Rectangle(
        (resized_box[0], resized_box[1]),
        resized_box[2] - resized_box[0],
        resized_box[3] - resized_box[1],
        linewidth=1,
        edgecolor=palette[0],
        facecolor=palette[0],
        alpha=0.3
    )

    # Add the patch to the Axes
    ax.add_patch(rect)

    plt.savefig(save_path, dpi=300)


def plot_doctr_boxes(image, boxes, save_path):
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    for box in boxes:
        x0 = box["value"]["x"]
        y0 = box["value"]["y"]
        x1 = x0 + box["value"]["width"]
        y1 = y0 + box["value"]["height"]

        box_coordinates = (x0, y0, x1, y1)
        resized_box = resize_box(box_coordinates, image.size, bbox_format=(100, 100))

        # Create a Rectangle patch
        rect = patches.Rectangle(
            (resized_box[0], resized_box[1]),
            resized_box[2] - resized_box[0],
            resized_box[3] - resized_box[1],
            linewidth=1,
            edgecolor=palette[0],
            facecolor=palette[0],
            alpha=0.3
        )

        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.savefig(save_path, dpi=300)


def plot_predictions_with_filter(image, boxes, box_filter, predictions, save_path):
    """
    Plot predictions but we keep only the first bounding box 
    for each word.
    """

    # boxes: torch.Size([n, 4])
    # predictions: torch.Size([n, 9]) since there are 9 labels
    # Create figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    print(f'Nombre total de tokens: {len(boxes)}')
    i = 0
    for box, prediction, label in zip(boxes, predictions, box_filter):
        if label == -100:
            continue
        else:
            i += 1
            resized_box = resize_box(box, image.size)
            color = palette[prediction]
            # Create a Rectangle patch
            rect = patches.Rectangle(
                (resized_box[0], resized_box[1]),
                resized_box[2] - resized_box[0],
                resized_box[3] - resized_box[1],
                linewidth=1,
                edgecolor=color,
                facecolor=color,
                alpha=0.3
            )

            # Add the patch to the Axes
            ax.add_patch(rect)
    print(f'Nombre de tokens après filtre: {i}')

    handles = [patches.Patch(color=color, label=label) for color, label in color2label.items()]
    plt.legend(handles=handles, bbox_to_anchor=(1, 0.5))

    plt.savefig(save_path, dpi=300)
