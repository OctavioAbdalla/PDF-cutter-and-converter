import re
import tkinter
import pandas as pd

class Create_Xslx_File:
    def __init__(self):
        self.table_name = ''
    
    def create_table(self, texts, file_name):
        result0 = []
        result1 = []
        
        for i, value in enumerate(texts):
            
            if i == 0:
                filtered_lines = [line for line in value.splitlines() if line.startswith(" ")]
                filtered_text = "\n".join(line.lstrip() for line in filtered_lines if line.strip())
                current_line = ''
                for i, line in enumerate(filtered_text.splitlines()):
                    
                    if line[0].isupper():    
                        
                        if i+1 < len(filtered_text.splitlines()) and not filtered_text.splitlines()[i+1][0].isupper():
                            current_line = line
 
                        else: 
                            result0.append(' '.join(line.split()))  
                            
                    else: 
                        result0.append(' '.join(f'{current_line}{line}'.split()))
       
            elif i == 1:
                filtered_text = "\n".join(line.strip() for line in value.splitlines() if line.strip())
                
                for line in filtered_text.splitlines():
                    line = line.lower()
                    line = line.replace('z', '2').replace('t', '7').replace('/', '7').replace('õ', '6')
                    line = re.sub(r'(\d)([a-zA-ZçÇ])', r'\1 \2', line)
                    line = line.replace('ppç', 'Pç').replace('pe', 'Pç').replace('pç', 'Pç').replace('pc', 'Pç')
                    line = line.replace('dç', 'Pç').replace('dc', 'Pç')
                    if 'Pç' in line or 'm' in line: 
                        result1.append(line)
            
        self.table_name = file_name.split('.')[0]            
                
        max_length = max(len(result0), len(result1))
        result0 += [None] * (max_length - len(result0))
        result1 += [None] * (max_length - len(result1))
       
        df = pd.DataFrame({'Produto': result0, 'Quantidade': result1})
        df.to_excel(f'{self.table_name}.xlsx', index=False)                
        tkinter.messagebox.showinfo("Sucesso", "Tabela salva com sucesso!")