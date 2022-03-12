from torchvision.utils import make_grid
import torchvision.transforms as T

### THIS IS STILL WIP, NEEDS MORE WORK BEFORE WE CAN GET EASY TO UNDERSTAND FIGURES WHILE TRAINING

class LogPredictionsCallback(Callback):
    
    def on_validation_batch_end(
        self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        """Called when the validation batch ends."""
 
        # `outputs` comes from `LightningModule.validation_step`
        # which corresponds to our model predictions in this case
        
        # Let's log 20 sample image predictions from first batch
        if batch_idx == 0:
            # print(batch)
            n = 2
            y = batch["mask"]
            out = batch["prediction"]
            # print(y)
            # print(f"Type of y is:{type(y)}")
            # print(out)
            # print(f"Type of out is:{type(out)}")
            # images = [img for img in x[:n]]
            # captions = [f'Ground Truth: {y_i} - Prediction: {y_pred}' for y_i, y_pred in zip(y[:n], outputs[:n])]
            
            # Option 1: log images with `WandbLogger.log_image`
            gtruth = [img for img in y[:n]]
            preds = [pred for pred in out[:n]]
            print(len(gtruth))
            print(len(preds))
            image_array = make_grid(gtruth+preds)
            # print(image_array)
            print(f"Shape of torch image array is:{image_array.shape}")
            image_array = [T.ToPILImage()(image.to(torch.uint8).to('cpu')) for image in image_array]
            # wandb_logger.log_image(key="sample_images", images=image_array, caption="TBA")
            wandb.log({"examples": [wandb.Image(image) for image in image_array]})
            # wandb_logger.log_image(key='sample_images', images=images, caption=captions)

            # Option 2: log predictions as a Table
            # columns = ['image', 'ground truth', 'prediction']
            # data = [[wandb.Image(x_i), y_i, y_pred] for x_i, y_i, y_pred in list(zip(x[:n], y[:n], outputs[:n]))]
            # wandb_logger.log_table(key='sample_table', columns=columns, data=data)
