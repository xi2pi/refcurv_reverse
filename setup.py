import sys
import os
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'


packages = ["sip","re","shutil", "os", "PyQt4.QtCore", "PyQt4.QtGui", "shutil", "numpy", "pandas", "scipy", "scipy.sparse.csgraph._validation"]
  

include_files=["tmp/"]

    
setup(
    name = "RefCurv - Reverse comp",
    version = "0.0.1",
    description = "RefCurv - Reverse comp",
    options = {'build_exe': {'packages': packages, 
                             "excludes": ["tkinter", "sqlite3", 
                                  "numpy.core._dotblas", 
                                  "PyQt5"],
                                  "include_files": include_files}},
    executables = [Executable("reverse_computation.py", base = None)]   
)

os.rename("build\exe.win32-3.4\lib\scipy\spatial\cKDTree.pyd", "build\exe.win32-3.4\lib\scipy\spatial\ckdtree.pyd")