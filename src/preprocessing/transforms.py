import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict


class Binarize(nn.Module):
    """Maps any data points which are: 1. greater than zero -> 1
    2. less than zero -> 0
    """

    # def __init__(self) -> None:
    #     super().__init__()

    def forward(self, inputs: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Defines the forward pass behaviour.

        Args:
           'inputs': the sample or batch samples obtained from the DataLoader
        """

        # Make a copy of the samples
        outputs = inputs

        # Binarize the samples
        outputs["mask"] = torch.where(
            inputs["mask"] > 0,
            torch.ones(inputs["mask"].shape, dtype=torch.int32),
            inputs["mask"],
        )
        outputs["mask"] = torch.where(
            inputs["mask"] < 0,
            torch.zeros(inputs["mask"].shape, dtype=torch.int32),
            inputs["mask"],
        )
        return outputs


class OneHotEncode(nn.Module):
    """Transforms single layer classification inputs into multiple one-hot encoded bands."""

    def __init__(self, classes: Dict[str, int]) -> None:
        """Initialises the transform.

        Args:
            'classes': a dict containing the different classes found in the input raster.
        """

        super().__init__()
        self.classes = classes

    def forward(self, inputs: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Defines the forward pass behaviour.

        Args:
           'inputs': the sample or batch samples obtained from the DataLoader
        """

        x_shape = inputs["mask"].shape

        # Minimum class value must be equal to zero
        inputs["mask"] = inputs["mask"] - min(self.classes.values())

        # Remove the 'band' dimension since this is always of dimension 1
        input_mask = torch.reshape(inputs["mask"], (x_shape[0], x_shape[2], x_shape[3]))

        # Get the one-hot encodings, which are a tensor of: (batch_idx, lat, lon, band_idx)
        encodings = F.one_hot(input_mask.to(torch.int64), num_classes=len(self.classes))

        # Create a new mask, which is a tensor of: (batch_idx, band_idx, lat, lon)
        new_mask = torch.zeros([x_shape[0], len(self.classes), x_shape[2], x_shape[3]])
        for band_idx in range(0, len(self.classes)):
            new_mask[:, band_idx, :, :] = encodings[:, :, :, band_idx]

        # Write one-hot encodings to the output tensor
        outputs = inputs
        outputs["mask"] = new_mask.to(torch.int32)
        return outputs
