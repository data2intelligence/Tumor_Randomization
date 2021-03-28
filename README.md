Prerequisite:  
python3: most MacOS or Linux operating system should have python3 installed by default. Then, please type:  
pip install --upgrade pandas numpy scipy matplotlib xlrd openpyxl  

Usage:  
Please open a terminal and run it as:  
./randomization.py initial_size.xlsx  

You can replace the excel file name. However, the structure of excel should be extractly the same as the current example. In the first tab "Group", please input the group name and size. In the second tab "Size", please input the mouse ID and tumor measurements. Then, the program will randomize mice by their tumor area (long x short) and get one sample with minimized inter-group difference and intra-group variance.  

Output:  
initial_size.pdf: diagnostic plot in two pages. The first page presents sample selection criteria. Each dot represents one randomization. X-axis shows the minimum p-value of inter-group difference, and Y-axis shows the maximum intra-group variance. The second page is the box-plots of group distribution results. If you don't like this result, please simply run the program again to get a new one.  

initial_size.group.xlsx: randomization results. Each tab represents one group with mice ID.  
