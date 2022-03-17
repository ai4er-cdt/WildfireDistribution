from pytorch_lightning.callbacks import Callback
import wandb


class LogPredictionsCallback(Callback):
    
    def on_validation_batch_end(
        self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        """Called when the validation batch ends."""

        # Dict of possible classes
        class_labels = {
              0: "no burn",
              1: "burn",
            }
        
        # Log the input(s), ground truth and prediction for the nth sample,
        # once per epoch, on the first batch in epoch
        n = 0
        if batch_idx == 0:
            orig_image = batch["image"][n]
            ground_truth = batch["mask"][n].detach().numpy()
            prediction_mask = batch["prediction"][n].detach().numpy()

            # If using only landcover
            if orig_image.shape[0] == 1:
                wandb.log(
                    {"Landcover / Prediction / Ground Truth" : wandb.Image(orig_image[0,:,:], masks={
                          "predictions" : {
                              "mask_data" : prediction_mask,
                              "class_labels" : class_labels
                          },
                          "ground_truth" : {
                              "mask_data" : ground_truth,
                              "class_labels" : class_labels
                          }
                     })
                 })

            # If using the Sentinel data then log this too
            else:
                wandb.log(
                    {"1. Sentinel Bands" : [wandb.Image(orig_image[1,:,:], caption="Band 3"), 
                                        wandb.Image(orig_image[2,:,:], caption="Band 8"),
                                        wandb.Image(orig_image[3,:,:], caption="Band 11")],
                    "2. Landcover / Prediction / Ground Truth" : wandb.Image(orig_image[0,:,:], masks={
                          "predictions" : {
                              "mask_data" : prediction_mask,
                              "class_labels" : class_labels
                          },
                          "ground_truth" : {
                              "mask_data" : ground_truth,
                              "class_labels" : class_labels
                          }
                     })
                })
