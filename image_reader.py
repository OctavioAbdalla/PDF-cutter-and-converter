import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import pandas as pd

class ImageReader:
    def __init__(self):
        self.custom_config = r'-c preserve_interword_spaces=1 --oem 0 --psm 1 -l por'
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.croped_image0 = None
        self.croped_image1 = None
        
    def split_and_clean_images(self, cropped_image):           
            image = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR)
            result_lines_off = image.copy()
            
            gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Remove horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
            remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(result_lines_off, [c], -1, (255,255,255), 5)

            # Remove vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
            remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
            cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(result_lines_off, [c], -1, (255,255,255), 5)

            width = result_lines_off.shape[1]

            self.croped_image0 = result_lines_off[:, :width-170]
            self.croped_image1 = result_lines_off[:, width-170:]
            
            #denoised_image = cv2.fastNlMeansDenoisingColored(self.croped_image0, None, 20, 20, 10, 60)
            
            
            return [self.croped_image0, self.croped_image1]
    
    
    def read_images(self, croped_images):
        text0 = ''
        text1 = ''
        
        for i, value in enumerate(croped_images):
            d = pytesseract.image_to_data(value, config=self.custom_config, output_type=Output.DICT)
            df = pd.DataFrame(d)
    
            # clean up blanks
            df1 = df[(df.conf!='-1')&(df.text!=' ')&(df.text!='')]
            # sort blocks vertically
            sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
            result = ''
            for block in sorted_blocks:
                curr = df1[df1['block_num']==block]
                sel = curr[curr.text.str.len()>3]
                char_w = (sel.width/sel.text.str.len()).mean()
                prev_par, prev_line, prev_left = 0, 0, 0
                text = ''
                for ix, ln in curr.iterrows():
                    # add new line when necessary
                    if prev_par != ln['par_num']:
                        text += '\n'
                        prev_par = ln['par_num']
                        prev_line = ln['line_num']
                        prev_left = 0
                    elif prev_line != ln['line_num']:
                        text += '\n'
                        prev_line = ln['line_num']
                        prev_left = 0

                    added = 0  # num of spaces that should be added
                    if ln['left']/char_w > prev_left + 1:
                        added = int((ln['left'])/char_w) - prev_left
                        text += ' ' * added 
                    text += ln['text'] + ' '
                    prev_left += len(ln['text']) + added + 1
                text += '\n'
                result += text
            if i == 0:
                text0 = result
            elif i == 1:
                text1 = result
        
        return [text0, text1]
          