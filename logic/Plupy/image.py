import os
import imageio as iio
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class image:
    def __init__(self):
        """
        class for things invloving reformatting and making videos from numpy arrays
        
        CLASS ELEMENTS: 
            None
        """   
        pass 
    
    def create_tiff_name(self,filename):
        """
        DESCRIPTION:
            takes the current filename and creates a new name with the desired nametype in .tiff format
        
        PARAMETERS:
            filename(string):
                name of the file (probably nmumpy) to be converted

        RETURNS:
            tiffname(string):
                the filename with .tiff 
        """
        
        # Extract parameters from filename
        name, npy = filename.split(".")
        tiffname = name + ".tiff"

            
        return tiffname
    
    def add_scale_bar(self,im_array, white = 65535):
        '''e
        DESCRIPTION:
            Adds a white 200um/ 339 pixel scale bar to the bottom left side of the image
        '''
        scale_bar_start = 200
        scale_bar_end = 539
        
        line1_width = list(range(scale_bar_start,scale_bar_end))
        line1_height = list(range(2200,2210))
        
        line2_width = list(range(scale_bar_start,scale_bar_start +10))
        line2_height = list(range(2175,2230))
        
        line3_width = list(range(scale_bar_end -10, scale_bar_end))
        line3_height = list(range(2175,2230))
        
        
        # Add horizontal line
        for x_pixel in line1_width:
            for y_pixel in line1_height:
                im_array[y_pixel,x_pixel] = white
        
        # Add vertical line left
        for x_pixel in line2_width:
            for y_pixel in line2_height:
                im_array[y_pixel,x_pixel] = white
             
        # Add vertical ine right
        for x_pixel in line3_width:
            for y_pixel in line3_height:
                im_array[y_pixel,x_pixel] = white
        
        # Adding scale  
        # Convert to pill image
        image_pil = Image.fromarray(im_array) 
        draw = ImageDraw.Draw(image_pil)
        
        # Define font
        font = ImageFont.truetype("verdana.ttf", 80)
        
        draw.text((575, 2100), "200 um", fill=white, font=font)  # White text for 16-bit image

        # Convert the PIL image back to a NumPy array
        final_array = np.array(image_pil)
        
        return final_array
    
    def add_delay_num(self,im_array, delay_ns):
        '''
        '''
        # Convert to pill image
        image_pil = Image.fromarray(im_array) 
        draw = ImageDraw.Draw(image_pil)
        
        # Define font
        font = ImageFont.truetype("verdana.ttf", 80)
        
        delay_s = delay_ns*1e-9
        
        draw.text((350, 150), f"Delay = {delay_s:.2e}s", fill=65535, font=font)  # White text for 16-bit image

        # Convert the PIL image back to a NumPy array
        final_array = np.array(image_pil)
        
        return final_array
    

    
    def convert_to_tiff(self, in_folderpath, out_folder = r'tiff_images'):
        """
        DESCRIPTION:
            Takes numpy arrays and converst to tiff files and then saves 
            
        PARAMETERS:
            in_folderpath(string):
                the folderpath of the numpy arrays
            out_folder(string):
                the folder where the images should be saved
            nametype(enum):
                refer to datatype definition above
        RETURNS:
            None
        
        """
        # Make sure the folder exists
        #os.makedirs(in_folderpath, exist_ok=True)
        os.makedirs(out_folder, exist_ok=True)
        
        # List all files in the folder
        
        file_list = os.listdir(in_folderpath)
        
        for file in file_list:
            filepath = os.path.join(in_folderpath, file) 
            im_array = np.load(filepath)
            im_array = (im_array*16).astype(np.uint16)
            im_array_scale = self.add_scale_bar(im_array)
            im_final = self.add_delay_num(im_array_scale, self.extract_true_delay(file))
            
            #create new name
            tiffname = self.create_tiff_name(file)
            
            # Make sure the save folder exists
            os.makedirs(out_folder, exist_ok=True)
            
            # Save tiff
            im = Image.fromarray(im_final, mode='I;16') 
            
            im.save(os.path.join(out_folder, tiffname), format = "TIFF")
            
        return None

    # Sort the files numerically by extracting the numeric value from the filename
    def extract_true_delay(self,filename):
        """
        DESCRIPTION:
            extracts the true delay for
        
        PARAMETERS:
            filename(string):
                filename for the file
                
        RETURNS:
            ordernum(int):
                the number of true delay or set delay which can be used to order the files
            
        """ 
        # Extract the numeric part (assumes filenames are purely numbers with optional negative sign and .tiff extension)
        basename = os.path.splitext(filename)[0]  # Remove ".tiff"
        
        time, setd, trued = basename.split("_")
        ordernum = trued
        
        return int(ordernum)  # Convert to integer for proper numeric sorting
    

    def tiff_to_mp4_imageio(self, tiff_folder, output_namepath, fps=5):
        """
        DESCRIPTION:
            Takes tiff images from tiff_folder anc compiles them into a mp4 video using imageio library
        PARAMETERS:
            tiff_folder(string):
                full path to folder with tiff images
            output_namepath(string):
                full path, incluing the name of the video for the output video
            fps(optional int):
                frames per second for the video, default to 5
        RETURNS:
            True and the video with the correct name should apear in the location provided

        """
        # List all files in folder dirctory
        file_list = os.listdir(tiff_folder)
        
        # Finds only ones which are tiff files
        tiff_files = [f for f in file_list if f.lower().endswith(".tiff")]
        
        #sorts files based off the true delay time
        tiff_files_sorted = sorted(tiff_files, key=self.extract_true_delay)

        # Iterates through files and adds them as frames
        frames = []
        for idx, tiff_file in enumerate(tiff_files_sorted):
            file_path = os.path.join(tiff_folder, tiff_file)
            img = iio.imread(file_path)
    
            # Normalize to 8-bit
            img_normalized = (img - img.min()) / (img.max() - img.min()) * 255
            img_8bit = img_normalized.astype(np.uint8)
            frames.append(img_8bit)
    
            # Debug
            debug_path = f"Z:/Users/coop/Chloe_Enzo_2024/videos/debugging/{idx:03d}_{self.extract_true_delay(tiff_file)}.png"
            iio.imwrite(debug_path, img_8bit)

        iio.mimwrite(output_namepath, frames, fps=fps)
        print("Video written successfully.")

        return True