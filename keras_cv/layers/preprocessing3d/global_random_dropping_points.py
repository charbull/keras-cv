# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tensorflow as tf

from keras_cv.layers.preprocessing3d import base_augmentation_layer_3d

POINT_CLOUDS = base_augmentation_layer_3d.POINT_CLOUDS
BOUNDING_BOXES = base_augmentation_layer_3d.BOUNDING_BOXES


class GlobalRandomDroppingPoints(base_augmentation_layer_3d.BaseAugmentationLayer3D):
    """A preprocessing layer which randomly drops point during training.

    This layer will randomly drop points based on keep_probability.
    During inference time, the output will be identical to input. Call the layer with `training=True` to drop the input points.

    Input shape:
      point_clouds: 3D (multi frames) float32 Tensor with shape
        [num of frames, num of points, num of point features].
        The first 5 features are [x, y, z, class, range].
      bounding_boxes: 3D (multi frames) float32 Tensor with shape
        [num of frames, num of boxes, num of box features].
        The first 7 features are [x, y, z, dx, dy, dz, phi].

    Output shape:
      A dictionary of Tensors with the same shape as input Tensors.

    Arguments:
      drop_rate: A float scalar sets the probability threshold for dropping the points.
    """

    def __init__(self, drop_rate=None, **kwargs):
        super().__init__(**kwargs)
        drop_rate = drop_rate if drop_rate else 0.0

        if drop_rate > 1:
            raise ValueError("drop_rate must be <=1.")
        keep_probability = 1 - drop_rate
        self._keep_probability = keep_probability

    def get_random_transformation(self, point_clouds, **kwargs):
        random_point_mask = (
            self._random_generator.random_uniform(
                tf.shape(point_clouds), minval=0.0, maxval=1
            )
            < self._keep_probability
        )

        return {"point_mask": random_point_mask}

    def augment_point_clouds_bounding_boxes(
        self, point_clouds, bounding_boxes, transformation, **kwargs
    ):
        point_mask = transformation["point_mask"]
        point_clouds = tf.where(point_mask, point_clouds, 0.0)
        return (point_clouds, bounding_boxes)
