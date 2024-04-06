print("""
  .oooooo.         .oooooo..o         .oooooo.              .o.             ooooooooo.        
 d8P'  `Y8b       d8P'    `Y8        d8P'  `Y8b            .888.            `888   `Y88.      
888      888      Y88bo.            888                   .8"888.            888   .d88'      
888      888       `"Y8888o.        888                  .8' `888.           888ooo88P'       
888      888           `"Y88b       888                 .88ooo8888.          888`88b.         
`88b    d88' .o.  oo     .d8P  .o.  `88b    ooo  .o.   .8'     `888.   .o.   888  `88b.   .o. 
 `Y8bood8P'  Y8P  8""88888P'   Y8P   `Y8bood8P'  Y8P  o88o     o8888o  Y8P  o888o  o888o  Y8P 

            Overwatch Screen Capture Analysis Recorder
""")

import os, sys
os.chdir('C:\\Users\\dim\\Documents\\Github\\OSCAR')
from PyQt6.QtWidgets import QApplication
#gui
from oscargui import reviewData, FileButtonApp


#start the gui:
# os.getcwd()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileButtonApp()  # the gui
    window.show()
    app.exec()
    # sys.exit(app.exec())



