from Tkinter import *
import Tkinter as tk
import Tix
import tkMessageBox
import os
import idlelib
from os import listdir
from os.path import isfile, join
import ttk
from demopanels import MsgPanel, SeeDismissPanel

# Constants for formatting file sizes
KB = 1024.0
MB = KB * KB
GB = MB * KB

# Get initial path
mypath = os.getcwd()

# Interface constants
framePadX=3
framePadY=3
fileSysX = 300
fileSysY=360

# Initialised variables
fileToSend = ""
slashcount = 0

# Set up window variables
window = Tix.Tk()
window.title("FTP Application")
window.resizable(0,0)

# Finds last backslach and removes everything after
# to get new directory
def getCdup():
	global mypath
	slashcount = mypath.count('\\')
	total = len(mypath)
	count = 0
	slashindex = 0
	index = -1
	for char in mypath:
		index = index + 1
		if char == '\\':
			count = count + 1
			if count == slashcount:
				slashindex = index
	mypath = mypath[:-(total-slashindex)]
	print mypath


# Function called when directory or file is selected
def doubleClick(object):
	global mypath
	# if starts with . remove from mypath list
	if object == '...':
		getCdup()
		terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
		terminalText.pack()
		showDirContents()
	elif "." not in object:
		mypath = mypath + '\\' + object
		terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
		terminalText.pack()
		showDirContents()
	else:
		fileToSend = mypath + '\\' + object
		terminalText.insert('1.0','Send file: ' + fileToSend + '\n')
		terminalText.pack()
		#																		<------------------------- Upload file 'fileToSend'

# Run terminal function
def run(event):
	os.system(event.widget.get())

# List contents in directory
def showDirContents():
	global mypath
	localAdd = Label(window, text=mypath,bg='black',fg='white',width=42,anchor=E).grid(column=0,row=2,columnspan=2)
	localFrame.delete("all")
	newlist = []
	newerlist = []
	contents = os.listdir(mypath)
	goUp = "..."
	contents.insert(0,goUp)
	for index,x in enumerate(contents):
		if "." not in x or x == "...":
			newlist.append(Button(window, text=x, relief='flat',command=lambda x = x: doubleClick(x),bg='blue'))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))
		else:
			newlist.append(Button(window, text=x, relief='flat',command=lambda x = x: doubleClick(x)))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))

# START SERVER
# *TO DO* Check if server is running OR exit server with exit of app
#os.system("start cmd /k python FTPserver.py")

# START CLIENT
def login():
	if userEntry.get() == 'Username' or passEntry.get() == 'Password' or addressEntry.get() == 'ServerAddress':
		tkMessageBox.showinfo("Login Error", "Please enter a username, password and address.")
	else:
		terminalText.insert('1.0', "Entered username:" + userEntry.get()+"\n")
		terminalText.pack()
		terminalText.insert('1.0', "Entered password:" + passEntry.get()+"\n")
		terminalText.pack()
		terminalText.insert('1.0', "Entered address:" + addressEntry.get()+"\n")
		terminalText.pack()
		terminalText.insert('1.0', "Entered port:" + portEntry.get()+"\n")
		terminalText.pack()
		
		# 										<----------------------------------------------- Run log in  with USR and PASS, etc





#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class App(tk.Frame):
    def __init__(self, master, path):
        tk.Frame.__init__(self, master)
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text=path, anchor='w')

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.grid()

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~








# TKINTER WIDGET SETUP

# Username Entry
userEntry = Entry(window)
userEntry.insert(0,"Username")
userEntry.grid(row=0,column=0,padx=10,pady=10)

# Password Entry
passEntry = Entry(window)
passEntry.insert(0,"Password")
passEntry.grid(row=0,column=1,padx=5,pady=10)

# Address Entry
addressEntry = Entry(window)
addressEntry.insert(0,"ServerAddress")
addressEntry.grid(row=0,column=2,padx=10,pady=10)
  
# Port Entry
portEntry = Entry(window)
portEntry.insert(0,"Port")
portEntry.grid(row = 0, column=3,padx=5,pady=10)

# Connect Button
connectBtn = Button(window, text="CONNECT", command=login)
connectBtn.grid(row=0,column=4,padx=50)

# Server Title
serverTitle = Label(window, text="Files Hosted Remotely").grid(column=2,row=1)
serverAdd = Label(window, text="",bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)

# Local Title
localTitle = Label(window, text="Files Hosted Locally").grid(column=0,row=1)
localAdd = Label(window, text=mypath,bg='black',fg='white',width=42).grid(column=0,row=2,columnspan=2)

# Frame with server files
serverFrame = Canvas(width=fileSysX*1.4, height=fileSysY,relief = SUNKEN,borderwidth=2)
serverFrame.grid(row=3,column=2,columnspan=3,padx=framePadX,pady=framePadY)

# Frame with terminal responses
terminalFrame = Frame(colormap="new",relief = SUNKEN,borderwidth=2,bg='black')
terminalFrame.grid(row=4,column=0,columnspan=5,padx=framePadX,pady=framePadY)
terminalText = Text(terminalFrame,bg='black',fg='white',height=14,width=90)
terminalText.pack()

# Terminal Entry
terminalEntry = Entry(window,width=120,bg='black',fg='white')
terminalEntry.insert(0,">Enter custon command>>")
terminalEntry.grid(row=5,column=0,columnspan=5)
terminalEntry.bind('<Return>',run)

# Frame with local files
localFrame = Canvas(width=fileSysX, height=fileSysY,relief = SUNKEN,borderwidth=2)
localFrame.grid(row=3,column=0,columnspan=2,padx=framePadX,pady=framePadY)


path_to_my_project = os.path.abspath('.')
app = App(localFrame, path=path_to_my_project)

#showDirContents()

window.mainloop()
