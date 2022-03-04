import numpy as np
import random
import math
from typing import Optional, Iterator, Union, Tuple, List
from torchgeo.datasets import BoundingBox, IntersectionDataset
from torchgeo.samplers import RandomBatchGeoSampler
from torchgeo.samplers.utils import get_random_bounding_box
from torchgeo.samplers.constants import Units


class ConstrainedRandomBatchGeoSampler(RandomBatchGeoSampler):
    """Returns batches of samples that meet the constraints specified:
        1. Proportion of samples with a burn proportion = 0 : 'no_burn_prop'
        2. The rest of the samples will make up 1-'no_burn_prop' proportion and have a burn proportion > 0
    Args:
        dataset: the dataset to take samples from.
        size: size of patch in lat/lon.
        batch_size: the number of samples per batch.
        length: number of samples (in total) to take per epoch. Note: this means no. of batches = length/batch_size.
        not_burned_prop: proportion of returned samples present that are "not burned". This may be no burn/some burn.
        roi: region of interest to take samples from.
        units: Units.<PIXELS/CRS> depending on if patch size is in pixels or lat/lon
    Returns:
        constrained_samples: set of samples that meet the specified constraints.
    """

    # Setup the attributes required for constraint implementation
    not_burned_samples_required = None
    burn_samples_required = None
    not_burned_prop = None

    # Define the constructor
    def __init__(
        self,
        dataset: IntersectionDataset,
        size: Union[Tuple[float, float], float],
        batch_size: int,
        length: int,
        not_burned_prop: float,
        roi: Optional[BoundingBox] = None,
        units: Units = Units.PIXELS,
    ) -> None:
        
        # Ensures that the input dataset is of type: IntersectionDataset
        if not isinstance(dataset, IntersectionDataset):
            raise TypeError("Input dataset to sampler must be of type: IntersectionDataset.")

        # Use init from RandomBatchGeoSampler parent class
        super().__init__(dataset, size, batch_size, length, roi, units)

        # Save the dataset and input constraints to the object
        self.dataset = dataset
        self.not_burned_prop = not_burned_prop

        # Set the number of samples required of not burned/burned types
        self.not_burned_samples_required = math.floor(not_burned_prop * self.batch_size)
        self.burn_samples_required = self.batch_size - self.not_burned_samples_required

    def __iter__(self) -> Iterator[List[BoundingBox]]:
        """Defines a generator function to produce batches of areas to sample next.

        Returns:
            List((minx, maxx, miny, maxy, mint, maxt)) coordinates to index a dataset
        """

        # Generate samples in len(self) = length/batch_size = number of batches required
        for _ in range(len(self)):

            # Choose a random tile
            hit = random.choice(self.hits)
            bounds = BoundingBox(*hit.bounds)

            # Fill a new batch of samples
            batch = []
            while self.not_burned_samples_required != 0 or self.burn_samples_required != 0:
            
                # Choose a random sample within that tile
                bounding_box = get_random_bounding_box(bounds, self.size, self.res)
                burn_prop = self.get_burn_proportion(bounding_box)
                
                # If we have a "not-burned" sample and we require "not-burned" samples
                if burn_prop == 0 and self.not_burned_samples_required != 0:
                    self.not_burned_samples_required -= 1
                    batch.append(bounding_box)

                # If we have a "burn" sample and we require "burn" samples
                elif burn_prop > 0 and self.burn_samples_required != 0:
                    self.burn_samples_required -= 1
                    batch.append(bounding_box)

                # If we have found no "burn" samples so far, assume we need to change tile (speed)
                elif self.burn_samples_required == (self.batch_size - math.floor(self.not_burned_prop*self.batch_size)):
                    hit = random.choice(self.hits)
                    bounds = BoundingBox(*hit.bounds)
            
            # Return the batch of balanced samples we have gathered
            yield batch

            # Reset requirements for next batch generation
            self.not_burned_samples_required = math.floor(self.not_burned_prop * self.batch_size)
            self.burn_samples_required = self.batch_size - self.not_burned_samples_required

    def get_burn_proportion(self, bounding_box):
        """Returns the burn proportion found within a given bounding box.

        Returns:
            burn_prop: the burn proportion present within the bounding box.
        """

        # Obtain the burn data within the bounding box
        burn_data = self.dataset[bounding_box]["mask"]

        # Get burn proportion within the bounding box
        non_zero_count = int((np.array(burn_data) > 0).sum())
        burn_prop = non_zero_count / burn_data.numel()
        return burn_prop
