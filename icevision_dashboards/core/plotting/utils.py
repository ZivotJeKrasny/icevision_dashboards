# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/core/plotting/utils.ipynb (unless otherwise specified).

__all__ = ['calculate_mixing_matrix', 'get_min_and_max_dates', 'convert_rgb_image_to_bokeh_rgb_image',
           'draw_record_with_bokeh']

# Cell
import datetime
from typing import Union, Tuple, Iterable

import numpy as np
import pandas as pd

from bokeh.plotting import figure

from icevision.visualize.draw_data import draw_record

# Cell
def calculate_mixing_matrix(data: pd.DataFrame, mixing_col: str, mixing_objects: str, return_df: bool = True) -> Union[Tuple[np.ndarray, dict], pd.DataFrame]:
    """Calculates mixing matrix for the mixing_objects column where they mix in the mixing_col.
    By standard the object class mixing matrix over the images is calculated.
    Returns the mixing matrix and the mapping between label and mixing matrix index.
    If return_df is True (default) a dataframe (instead of the mixing matrix) will be returned that can be directly consumed by histogram_2d."""
    # map labels to the mixing matrix index
    mapping = {i:j for j,i in enumerate(np.sort(data[mixing_objects].unique()))}
    num_unique_mixing_objects = data[mixing_objects].nunique()
    mixing_matrix = np.zeros([num_unique_mixing_objects, num_unique_mixing_objects])
    mixing_groups = data.groupby(mixing_col)
    # iterate over each individual element with the same mixing_col to calculate the mixing based on the mixing_objects
    for group_key, group in mixing_groups:
        # handel self mixing
        for value, count in group[mixing_objects].value_counts().iteritems():
            if count > 1:
                mixing_matrix[mapping[value], mapping[value]] += 1
        # handel mixing of different objects
        permutations = np.array(np.meshgrid(group[mixing_objects].unique(), group[mixing_objects].unique())).T.reshape(-1,2)
        for permutation in permutations:
            # avoid double counting in the self mixing
            if permutation[0] != permutation[1]:
                mixing_matrix[mapping[permutation[0]], mapping[permutation[1]]] += 1

    if return_df:
        df_dict = {"values": [], "col_name": [], "row_name": []}
        for row_name, row in zip(mapping, mixing_matrix):
            df_dict["values"] += row.tolist()
            df_dict["row_name"] += [row_name]*len(mapping)
            df_dict["col_name"] += mapping
        return pd.DataFrame(df_dict)
    return mixing_matrix, mapping

# Cell
def get_min_and_max_dates(dates: Iterable[datetime.datetime]) -> Tuple[datetime.datetime, datetime.datetime]:
    """Returns the min and max date. If all dates are the same the max date is moved one day forward."""
    min_date = min(dates).replace(microsecond=0, second=0, minute=0, hour=0)
    max_date = max(dates).replace(microsecond=0, second=0, minute=0, hour=0)
    # make sure the min and max values are at least a day appart
    if min_date == max_date:
        max_date = max_date.replace(day=max_date.day+1)
    return min_date, max_date

# Cell
def convert_rgb_image_to_bokeh_rgb_image(img: np.ndarray) -> np.ndarray:
    """Convertes a image in the form of a numpy array to an array that can be shown by bokeh."""
    img = np.flipud(img)
    img = img.astype(np.uint8)
    bokeh_img = np.empty((img.shape[0],img.shape[1]), dtype=np.uint32)
    view = bokeh_img.view(dtype=np.uint8).reshape((img.shape[0],img.shape[1], 4))
    view[:,:, 0] = img[:,:,0]
    view[:,:, 1] = img[:,:,1]
    view[:,:, 2] = img[:,:,2]
    view[:,:, 3] = 255
    return bokeh_img

# Cell
def draw_record_with_bokeh(
    record,
    class_map=None,
    display_label=True,
    display_bbox=False,
    display_mask=False,
    display_keypoints=False,
    return_figure=False,
    width=None,
    height=None
):
    """Draws a record or returns a bokeh figure containing the image."""
    img = draw_record(
            record=record,
            class_map=class_map,
            display_label=display_label,
            display_bbox=display_bbox,
            display_mask=display_mask,
            display_keypoints=display_keypoints,
        )

    # create bokeh figure with the plot
    bokeh_img = convert_rgb_image_to_bokeh_rgb_image(img)

    # make sure the aspect ratio of the image is retained, if only the width of hight is given
    if width is None and height is not None:
        plot_width = int(img.shape[1]/img.shape[0] * height)
        plot_height = height
    elif height is None and width is not None:
        plot_width = width
        plot_height = int(img.shape[0]/img.shape[1] * width)
    else:
        plot_width = img.shape[1] if width is None else width
        plot_height = img.shape[0] if height is None else height

    p = figure(tools="reset, wheel_zoom, box_zoom, save, pan", width=plot_width, height=plot_height, x_range=(0, img.shape[1]), y_range=(img.shape[0], 0), x_axis_location="above")
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.image_rgba([bokeh_img], x=0, y=img.shape[0], dw=img.shape[1], dh=img.shape[0], level="image")
    if return_figure:
        return p
    else:
        show(p)