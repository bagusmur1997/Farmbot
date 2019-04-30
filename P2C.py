"""Image Pixel Location to Machine Coordinate Conversion."""

import sys
import os
import json
import numpy as np
from Parameters import Parameters
from Image import Image
from DB import DB
import ENV
from CeleryPy import log


def _round(number, places):
    """Round number to given number of decimal places."""
    factor = 10 ** places
    return int(number * factor) / float(factor)


class Pixel2coord(object):
    """Image pixel to machine coordinate conversion.

    Calibrates the conversion of pixel locations to machine coordinates
    in images. Finds object coordinates in image.
    """

    def __init__(self, plant_db,
                 calibration_image=None,
                 calibration_data=None, load_data_from=None):
        """Set initial attributes.

        Arguments:
            Database() instance

        Optional Keyword Arguments:
            calibration_image (str): filename (default: None)
            calibration_data: P2C().calibration_params JSON,
                              or 'file' or 'env_var' string
                              (default: None)
        """
        self.dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
        self.parameters_file = "plant-detection_calibration_parameters.json"

        self.calibration_params = {}
        self.debug = False
        self.env_var_name = 'PLANT_DETECTION_calibration'
        self.plant_db = plant_db
        self.defaults = Parameters().cdefaults

        # Data and parameter preparation
        self.cparams = Parameters()
        self._calibration_data_preparation(calibration_data, load_data_from)
        # Image preparation
        self.image = None
        self._calibration_image_preparation(calibration_image)

        self.rotationangle = 0
        self.test_rotation = 5  # for testing, add some image rotation
        self.viewoutputimage = False  # overridden as True if running script
        self.json_calibration_data = None
