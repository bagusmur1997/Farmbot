import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

df = pd.DataFrame([['a', 'b'], ['c', 'd']], index=['Row 1', 'Row 2'], columns=['Tes 1', 'Tes 2'])
sf = pd.DataFrame([['a', 'b'], ['c', 'd']], index=['Row 3', 'Row 4'])

'''writer = ExcelWriter('Data_Farmbot_Test.xlsx')
df.to_excel(writer,'Sheet1', index=True, startrow=0, startcol= 0)
writer.save()

sf.to_excel(writer, 'Sheet1', index=True, startrow=3, startcol=0, header=False)
writer.save()'''
writer = ExcelWriter('Data_Farmbot_Test.xlsx')
