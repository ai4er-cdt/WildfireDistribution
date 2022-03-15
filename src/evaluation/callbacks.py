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
        
        # Log the input, ground truth and prediction for the nth sample,
        # once per epoch, on the first batch in epoch
        n = 0
        if batch_idx == 0:
            orig_image = batch["image"][n]
            ground_truth = batch["mask"][n].detach().numpy()
            prediction_mask = batch["prediction"][n].detach().numpy()

            wandb.log(
                {"my_image_key" : wandb.Image(orig_image, masks={
                    "predictions" : {
                        "mask_data" : prediction_mask,
                        "class_labels" : class_labels
                    },
                    "ground_truth" : {
                        "mask_data" : ground_truth,
                        "class_labels" : class_labels
                    }
                })})
