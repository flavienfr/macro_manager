from abc import abstractmethod
from tkinter import *
import subprocess
import json
from tkinter.filedialog import askopenfilename
from os.path import exists

macros = []
hasEditMode = False
WHITE = "#ffffff"

ADD_MACRO = "Ajouter une macro"
EDIT_UNABLE = "Mode édition"
EDIT_DISABLE = "Quitter l'édition"
MACRO_NAME_LABEL = "Nom de la macro"
MACRO_PATH_LABEL = "Chemin de la macro"
BROWSE = "Parcourir"
EDIT = "Modifier"
CREATE = "Créer"
REMOVE = "Retirer"
REMOVE_ICON_PATH = "delete.png"
EDIT_ICON_PATH = "edit.png"

WINDOW_CONF_FILE = "window.conf"


class MacroWindowBase:

    @property
    @abstractmethod
    def confirmBtnTxt(self):
        pass

    @abstractmethod
    def getNameLabel(self):
        pass

    @abstractmethod
    def getPathLabel(self):
        pass

    def setMacroPathEntry(self, macroPathEntry):
        newPath = askopenfilename(filetypes=[("Python files", ".py")])
        if newPath:
            macroPathEntry.delete(0, 'end')
            macroPathEntry.insert(0, newPath)

    @abstractmethod
    def callback():
        pass

    def __init__(self):
        macroWindow = Toplevel(window)
        macroWindow.grab_set()
        macroWindow.geometry("500x150")
        macroWindow.maxsize(width=500, height=150)
        macroWindow.minsize(width=200, height=150)

        macroWindow.columnconfigure(0, weight=3)
        macroWindow.columnconfigure(1, weight=1)

        macroNameLabel = Label(macroWindow, text=MACRO_NAME_LABEL)
        macroNameLabel.grid(column=0, row=0, sticky=W, padx=10, pady=2)

        macroNameInputbox = Entry(macroWindow, width=30)
        macroNameEntryText = self.getNameLabel()
        macroNameInputbox.insert('end', macroNameEntryText)
        macroNameInputbox.grid(column=0, row=2, sticky=W, padx=13)

        macroPathLabel = Label(macroWindow, text=MACRO_PATH_LABEL)
        macroPathLabel.grid(column=0, row=3, sticky=W, padx=10, pady=2)

        macroPathInput = Entry(macroWindow, width=70)
        macroPathEntryText = self.getPathLabel()
        macroPathInput.insert('end', macroPathEntryText)
        macroPathInput.grid(column=0, row=4, sticky=W, padx=13)

        browseBtn = Button(macroWindow, text=BROWSE, width=10,
                           command=lambda: self.setMacroPathEntry(macroPathInput))
        browseBtn.grid(column=1, row=4, sticky=W, padx=(0, 10))

        confirmBtn = Button(macroWindow, text=self.confirmBtnTxt, width=15, command=lambda: self.callback(
            macroWindow, macroNameInputbox.get(), macroPathInput.get()))
        confirmBtn.grid(column=0, row=5, pady=10, columnspan=2)


class EditMacroWindow(MacroWindowBase):

    row = None

    @property
    def confirmBtnTxt(self):
        return EDIT

    def getNameLabel(self):
        return macros[self.row]['name']

    def getPathLabel(self):
        return macros[self.row]['path']

    def callback(self, window, newName, newPath):
        macros[self.row]["name"] = newName
        macros[self.row]["path"] = newPath
        saveMacros()
        window.destroy()
        macrosBtns.reloadMacrosFrame()

    def __init__(self, row):
        self.row = row
        super().__init__()


class CreateMacroWindow(MacroWindowBase):

    @property
    def confirmBtnTxt(self):
        return CREATE

    def getNameLabel(self):
        return ""

    def getPathLabel(self):
        return ""

    def callback(self, window, newName, newPath):
        macros.append({"name": newName, "path": newPath})
        saveMacros()
        window.destroy()
        macrosBtns.reloadMacrosFrame()

    def __init__(self):
        super().__init__()


class DynamicGrid(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.text = Text(self, wrap="char", borderwidth=0, highlightthickness=0,
                         state="disabled")
        vsb = Scrollbar(orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=True)
        self.boxes = []
        self.editIcon = getImageIfExists(EDIT_ICON_PATH)
        self.deleteIcon = getImageIfExists(REMOVE_ICON_PATH)

    def displayMacros(self):
        for i in range(len(macros)):
            self.macroBtns(i)

    def macroBtns(self, row):
        macroLigneBtns = Frame(self.text, width=100,
                               height=100, background=WHITE)

        macro = macros[row]

        if (hasEditMode):
            btnRun = Button(macroLigneBtns, text=macro["name"], command=lambda: executeMacro(
                macro["path"]), width=25, height=2)
            btnRun.grid(column=0, row=0, padx=(5, 5))
            if (self.editIcon):
                btnEdit = Button(macroLigneBtns, text=EDIT,
                                 image=self.editIcon, command=lambda: EditMacroWindow(row))
                btnEdit.grid(column=0, row=1, sticky=W,
                             pady=(5, 10), padx=(65, 0))
            else:
                btnEdit = Button(macroLigneBtns, text=EDIT,
                                 command=lambda: EditMacroWindow(row), width=7)
                btnEdit.grid(column=0, row=1, sticky=W,
                             pady=(5, 10), padx=(35, 0))
            if (self.deleteIcon):
                btnDelete = Button(
                    macroLigneBtns, image=self.deleteIcon, command=lambda: self.deleteMacro(row))
                btnDelete.grid(column=0, row=1, sticky=E,
                               pady=(5, 10), padx=(0, 65))
            else:
                btnDelete = Button(macroLigneBtns, text=REMOVE,
                                   command=lambda: self.deleteMacro(row), width=7)
                btnDelete.grid(column=0, row=1, sticky=E,
                               pady=(5, 10), padx=(0, 35))
        else:
            btnRun = Button(macroLigneBtns, text=macro["name"], command=lambda: executeMacro(
                macro["path"]), width=25, height=2)
            btnRun.grid(column=0, row=0, padx=(5, 5), pady=(0, 41))

        self.text.tag_configure("center", justify='center')
        self.boxes.append(macroLigneBtns)
        self.text.tag_add("center", "1.0", "end")
        self.text.configure(state="normal")
        self.text.window_create("end", window=macroLigneBtns)
        self.text.configure(state="disabled")

    def deleteMacro(self, row):
        macros.pop(row)
        saveMacros()
        self.reloadMacrosFrame()

    def reloadMacrosFrame(self):
        self.clearDynamicGrid()
        self.displayMacros()

    def clearDynamicGrid(self):
        self.text.configure(state="normal")
        self.text.delete(1.0, "end")
        self.text.configure(state="disabled")


def getImageIfExists(imagePath):
    if (exists(imagePath)):
        editImage = PhotoImage(file=imagePath)
        return editImage.subsample(30, 30)
    return False


def executeMacro(path):
    subprocess.call(["py", path])


def saveMacros():
    file = open("macros.json", "w")
    json.dump(macros, file)
    file.close()


def getMacrosFromFileOrCreateIt():
    if not exists("macros.json"):
        file = open("macros.json", "w")
        json.dump([], file)
        file.close()
        return []
    file = open("macros.json", "r")
    macros = json.load(file)
    file.close()
    return macros


def EditMode(editBtn, createBtn):
    global hasEditMode
    hasEditMode = not hasEditMode

    if (hasEditMode):
        editBtn.pack_forget()
        editBtn.pack(side=TOP, pady=(5, 5))
        createBtn.pack(side=TOP, pady=(0, 10))
    else:
        editBtn.pack_forget()
        createBtn.pack_forget()
        editBtn.pack(side=TOP, pady=(5, 41))

    if editBtn.config('text')[-1] == EDIT_UNABLE:
        editBtn.config(text=EDIT_DISABLE)
    else:
        editBtn.config(text=EDIT_UNABLE)
    macrosBtns.reloadMacrosFrame()


def displayEditAndCreateMacroBtn(frame):
    gui = Frame(frame, background=WHITE)
    gui.pack()
    editBtn = Button(gui, text=EDIT_UNABLE, width=15, height=2,
                     command=lambda: EditMode(editBtn, createBtn))
    createBtn = Button(gui, text=ADD_MACRO,
                       width=15, command=lambda: CreateMacroWindow())
    editBtn.pack(side=TOP, pady=(5, 41))


def saveWindowConf(event):
    with open(WINDOW_CONF_FILE, "w") as conf:
        conf.write(window.geometry())


def readWindowConf():
    if exists(WINDOW_CONF_FILE):
        file = open(WINDOW_CONF_FILE, "r")
        conf = file.read()
        file.close()
        return conf.split("+")[0]
    return "750x500"

# Main


window = Tk()
windowConf = readWindowConf()
window.geometry(windowConf)
window.title("Macro Manager")
window.bind("<Configure>", saveWindowConf)
window.configure(bg=WHITE)

displayEditAndCreateMacroBtn(window)

macrosBtns = DynamicGrid(window)
macrosBtns.pack(side="top", fill="both", expand=True)

macros = getMacrosFromFileOrCreateIt()
macrosBtns.displayMacros()

window.mainloop()
