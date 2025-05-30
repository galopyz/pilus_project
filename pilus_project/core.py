"""Core utilities"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['show_im', 'calc_corners', 'imshow_with_boxes', 'apply_clahe', 'compare_ims', 'compare_ims_with_boxes', 'plot_image']

# %% ../nbs/00_core.ipynb 4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
import cv2
import nd2
import torch
import fastcore.all as fc

plt.rcParams['image.cmap'] = 'gray'

# %% ../nbs/00_core.ipynb 17
@fc.delegates(plt.Axes.imshow)
def show_im(path, figsize=(10, 8), **kwargs):
    """Show an image from the path."""
    plt.figure(figsize=figsize)
    plt.imshow(Image.open(path), **kwargs)
    plt.axis('off')

# %% ../nbs/00_core.ipynb 24
def calc_corners(csv, max_pos = 8.458666666666666e-05):
    df = pd.read_csv(csv)
    results = []
    for _, row in df.iterrows():
        length = row['Length']
        width = row['Width']
        angle = row['Angle']
        pos_x = row['Position X']
        pos_y = row['Position Y']

        x1 = pos_x + length/2 * np.cos(angle) - width/2 * np.sin(angle)
        y1 = pos_y + length/2 * np.sin(angle) + width/2 * np.cos(angle)
        x2 = pos_x - length/2 * np.cos(angle) - width/2 * np.sin(angle)
        y2 = pos_y - length/2 * np.sin(angle) + width/2 * np.cos(angle)
        x3 = pos_x - length/2 * np.cos(angle) + width/2 * np.sin(angle)
        y3 = pos_y - length/2 * np.sin(angle) - width/2 * np.cos(angle)
        x4 = pos_x + length/2 * np.cos(angle) + width/2 * np.sin(angle)
        y4 = pos_y + length/2 * np.sin(angle) - width/2 * np.cos(angle)
        results.append([row['Type'], x1, y1, x2, y2, x3, y3, x4, y4])

    df = pd.DataFrame(results, columns=['class_index', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4'])
    df = pd.concat([df.iloc[:, 0], df.iloc[:, 1:] / max_pos], axis=1)
    return torch.tensor(df.to_numpy())

# %% ../nbs/00_core.ipynb 27
@fc.delegates(plt.Axes.imshow)
def imshow_with_boxes(im, boxes, figsize=(8,8), ax=None, legend=None, legend_loc='upper left', **kwargs):
    """Display image with bounding boxes for different cell types, returns fig and ax for further customization"""
    import matplotlib.patches as patches
    colors = dict([(1, 'red'), (2, 'blue'), (3, 'green'), (4, 'yellow'), (5, 'purple'), (6, 'orange')])
    class_names = dict([(1, 'Type 1 - Both poles free'), (2, 'Type 2 - One pole occluded'), 
                        (3, 'Type 3 - Both poles occluded'), (4, 'Type 4 - Super bright cell'), 
                        (5, 'Type 5 - Very dim cell'), (6, 'Type 6 - Partial cell')])
    fig = None if ax is not None else plt.figure(figsize=figsize)
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    if fc.hasattrs(im, ('cpu','permute','detach')):
        im = im.detach().cpu()
        if len(im.shape)==3 and im.shape[0]<5: im=im.permute(1,2,0)
    elif isinstance(im, Path): im=np.array(Image.open(im))
    elif not isinstance(im,np.ndarray): im=np.array(im)
    height, width = im.shape[:2]
    if im.shape[-1]==1: im=im[...,0]
    ax.imshow(im, **kwargs)
    ax.axis('off')

    unique_classes = boxes[:,0].unique().int().tolist()
    legend_elements = [patches.Patch(facecolor='none', edgecolor=colors[class_idx], label=class_names[class_idx])
                      for class_idx in unique_classes]

    for box in boxes:
        class_idx = box[0].item()
        corners = [[box[1].item() * width, box[2].item() * height],
                  [box[3].item() * width, box[4].item() * height],
                  [box[5].item() * width, box[6].item() * height],
                  [box[7].item() * width, box[8].item() * height]]

        color = colors.get(box[0].item(), 'white')
        polygon = patches.Polygon(corners, fill=False, edgecolor=color, linewidth=1)
        ax.add_patch(polygon)

    if legend: ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc=legend_loc)
    plt.tight_layout()
    return fig, ax

# %% ../nbs/00_core.ipynb 35
def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8,8)):
    if image.dtype != np.uint8:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(image)
    return enhanced

# %% ../nbs/00_core.ipynb 36
def compare_ims(img1, img2, im1_title='img1', im2_title='img2', cmap='gray'):
    plt.figure(figsize=(12,6))
    plt.subplot(121)
    plt.imshow(img1, cmap=cmap)
    plt.title(im1_title)
    plt.axis('off')

    plt.subplot(122)
    plt.imshow(img2, cmap=cmap)
    plt.title(im2_title)
    plt.axis('off')

    plt.show()

# %% ../nbs/00_core.ipynb 37
def compare_ims_with_boxes(img1, img2, boxes1=None, boxes2=None, im1_title='img1', im2_title='img2', 
                           legend=None, legend_loc='best'):
    fig, axs = plt.subplots(1, 2, figsize=(12,6))
    
    if boxes1 is not None: 
        imshow_with_boxes(img1, boxes1, ax=axs[0], legend=legend, legend_loc=legend_loc)
    else:
        axs[0].imshow(img1, cmap='gray')
        axs[0].axis('off')
    axs[0].set_title(im1_title)
    
    if boxes2 is not None:
        imshow_with_boxes(img2, boxes2, ax=axs[1], legend=legend, legend_loc=legend_loc)
    else:
        axs[1].imshow(img2, cmap='gray')
        axs[1].axis('off')
    axs[1].set_title(im2_title)
    
    plt.tight_layout()
    plt.show()
    return fig, axs

# %% ../nbs/00_core.ipynb 41
def plot_image(image, boxes):
    """Plots predicted bounding boxes on the image"""
    im = np.array(image)
    if len(im.shape)==3 and im.shape[0]<5: im=im.transpose(1,2,0)
    height, width, _ = im.shape

    fig, ax = plt.subplots(1)
    ax.imshow(im)

    # boxes is a tensor, which is in cellboxes format
    if not isinstance(boxes, list):
        boxes = cellboxes_to_boxes(boxes.unsqueeze(0))[0]
        
    # box format is [x_mid, y_mid, width, height]
    for box in boxes:
        box = box[2:]
        assert len(box) == 4, "Got more values than in x, y, w, h, in a box!"
        upper_left_x = box[0] - box[2] / 2
        upper_left_y = box[1] - box[3] / 2
        rect = patches.Rectangle(
            (upper_left_x * width, upper_left_y * height),
            box[2] * width,
            box[3] * height,
            linewidth=1,
            edgecolor="r",
            facecolor="none",
        )
        ax.add_patch(rect)

    plt.show()
