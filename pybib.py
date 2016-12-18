# -*- coding: UTF-8 -*-

import sys
import time
import copy

from PyQt4 import QtGui  # , QtCore
import pybtex
import pybtex.database

import formatting

"""
This is a test app to learn GUI programming in Python using PyQT4
"""

__author__ = 'Jens-Kristian Krogager'


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 700, 600)
        self.setWindowTitle("PyQt4 GUI Test")
        self.setWindowIcon(QtGui.QIcon('icons/pythonlogo.png'))

        exitAction = QtGui.QAction("&Close Application", self)
        exitAction.setStatusTip("Leave the Application")
        exitAction.triggered.connect(self.close_application)

        openFile = QtGui.QAction("&Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open File")
        openFile.triggered.connect(self.file_open)

        saveFile = QtGui.QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip("Save File")
        saveFile.triggered.connect(self.file_save)

        newFile = QtGui.QAction("&New File", self)
        newFile.setShortcut("Ctrl+N")
        newFile.setStatusTip("New File")
        newFile.triggered.connect(self.file_new)

        self.searchContent = QtGui.QAction(QtGui.QIcon('icons/search_content-icon.png'),
                                           "&Search Content", self)
        self.searchContent.setShortcut("Ctrl+Shift+F")
        self.searchContent.setStatusTip("Search in the bibliography content")
        self.searchContent.triggered.connect(self.create_search_window)

        self.editEntry = QtGui.QAction(QtGui.QIcon('icons/edit_content-icon.png'),
                                       "&Edit Current Entry", self)
        self.editEntry.setShortcut("Ctrl+E")
        self.editEntry.setStatusTip("Edit the content of the current entry")
        self.editEntry.triggered.connect(self.create_edit_window)

        self.statusBar()

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu("&File")
        self.fileMenu.addAction(newFile)
        self.fileMenu.addAction(openFile)
        self.fileMenu.addAction(saveFile)
        self.fileMenu.addAction(exitAction)
        self.searchMenu = self.mainMenu.addMenu("&Search")
        self.searchMenu.addAction(self.searchContent)
        self.editMenu = self.mainMenu.addMenu("&Edit")
        self.editMenu.addAction(self.editEntry)

        # Define empty data containers
        self.search_form_fields = dict()
        self.entryID_list = list()
        self.bib_database = pybtex.database.BibliographyData()

        self.home()

    def home(self):
        # btn = QtGui.QPushButton("Quit", self)
        # btn.clicked.connect(self.close_application)
        # # btn.resize(btn.sizeHint())                # optimized automated size
        # btn.resize(btn.minimumSizeHint())           # minimum automated size
        # btn.move(0, 100)
        self.main_frame = QtGui.QWidget()

        # Setup the toolbar:
        exitAction = QtGui.QAction(QtGui.QIcon('icons/quit-icon.png'), "Exit Application", self)
        exitAction.triggered.connect(self.close_application)

        newFile = QtGui.QAction(QtGui.QIcon('icons/newfile-icon.png'), "New File", self)
        newFile.triggered.connect(self.file_new)

        openFile = QtGui.QAction(QtGui.QIcon('icons/open-icon.png'), "Open New File", self)
        openFile.triggered.connect(self.file_open)

        saveFile = QtGui.QAction(QtGui.QIcon('icons/save-icon.png'), "Save File", self)
        saveFile.triggered.connect(self.file_save)

        self.toolbar = self.addToolBar("Tools")
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(newFile)
        self.toolbar.addAction(openFile)
        self.toolbar.addAction(saveFile)
        self.toolbar.addAction(self.searchContent)
        self.toolbar.addAction(self.editEntry)

        # Search Bar for articles in listView
        self.searchBar = QtGui.QLineEdit()
        self.searchBar.textChanged.connect(self.search_entries)
        self.searchBar.returnPressed.connect(self.activate_list)
        self.searchBar.setFixedWidth(100)
        self.searchBar.setFixedHeight(22)
        self.currentList = list()
        self.reset_list_button = QtGui.QPushButton("Reset")
        self.reset_list_button.clicked.connect(self.reset_list_view)
        self.reset_list_button.setFixedWidth(40)
        self.reset_list_button.setFixedHeight(22)

        self.searchBar_layout = QtGui.QHBoxLayout()
        self.searchBar_layout.addWidget(self.searchBar)
        self.searchBar_layout.addWidget(self.reset_list_button)

        searchAction = QtGui.QAction(QtGui.QIcon('icons/search-icon.png'), "Search Entries", self)
        searchAction.setShortcut("Ctrl+F")
        searchAction.triggered.connect(self.searchBar.setFocus)
        self.toolbar.addAction(searchAction)
        self.searchMenu.addAction(searchAction)

        # List of Article Entries:
        self.listView = QtGui.QListWidget(self.main_frame)
        # listView.resize(70, 250)
        self.listView.setFixedWidth(140)
        self.listView.itemClicked.connect(self.show_entry)
        self.listView.currentItemChanged.connect(self.show_entry)

        # Collect Search Bar and List View:
        list_panel = QtGui.QVBoxLayout()
        list_panel.addLayout(self.searchBar_layout)
        list_panel.addWidget(self.listView)

        # entryLayout = QtGui.QFormLayout()
        entryLayout = QtGui.QGridLayout()
        boundary = QtGui.QVBoxLayout()
        self.form_entries = ['Author', 'Journal', 'Year', 'Title', 'Volume', 'Keyword', 'AdsURL']
        self.form_fields = list()
        row = 0
        for name in self.form_entries:
            if name.lower() == 'adsurl':
                this_field = QtGui.QLabel()
                this_field.setOpenExternalLinks(True)
            else:
                this_field = QtGui.QLineEdit()
                this_field.setReadOnly(True)
            self.form_fields.append(this_field)
            entryLayout.addWidget(QtGui.QLabel(name + ': '), row, 0)
            entryLayout.addWidget(this_field, row, 1)
            row += 1
        boundary.addStretch(1)
        entryLayout.addLayout(boundary, row, 0, 1, 2)

        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(list_panel)
        hbox.addLayout(entryLayout)
        self.main_frame.setLayout(hbox)

        self.setCentralWidget(self.main_frame)

        # checkBox = QtGui.QCheckBox('Enlarge Window', self)
        # checkBox.move(70, 50)
        # checkBox.stateChanged.connect(self.enlarge_window)
        #
        # self.progress = QtGui.QProgressBar(self)
        # self.progress.setGeometry(200, 80, 250, 20)
        #
        # self.btn = QtGui.QPushButton("Download", self)
        # self.btn.move(200, 120)
        # self.btn.clicked.connect(self.download)

        # self.show()

    def activate_list(self):
        self.listView.setCurrentRow(0)
        self.listView.setFocus()

    def search_entries(self, text):
        QtGui.QApplication.processEvents()
        text = str(text)

        if text:
            listToShow = list()
            for articleID in self.currentList:
                if text.lower() in articleID.lower():
                    listToShow.append(articleID)
            self.listView.clear()
            self.listView.addItems(listToShow)

        else:
            self.listView.clear()
            self.listView.addItems(self.currentList)

    def create_search_window(self):
        self.Spline_dialog = SearchWindow(self)

    def create_edit_window(self):
        self.editor = EditWindow(self)

    def search_content(self):
        matches = list()

        # Go through criteria and collect matching entries:
        for entry in self.bib_database.entries.values():
            criteria = 1
            for search_field_name in self.search_form_fields.keys():
                query = str(self.search_form_fields[search_field_name].text())
                if query:
                    if search_field_name == 'author':
                        content = entry.fields[search_field_name]
                        criteria *= query.lower() in content.lower()

                    elif search_field_name in entry.fields.keys():
                        content = entry.fields[search_field_name]
                        if search_field_name in ['title', 'keywords']:
                            # split query and search for individual words:
                            words = query.split()
                            for word in words:
                                if word.lower() in content.lower():
                                    criteria *= True
                                else:
                                    criteria *= False
                        else:
                            criteria *= query.lower() in content.lower()
                    else:
                        criteria *= False
            if criteria:
                matches.append(entry.key)

        # Present matching entries in self.listView:
        self.listView.clear()
        self.listView.addItems(matches)
        self.currentList = matches

    def reset_search_form(self):
        for search_field in self.search_form_fields.values():
            search_field.clear()
        self.listView.clear()
        self.currentList = self.entryID_list
        self.listView.addItems(self.currentList)

    def reset_list_view(self):
        self.currentList = self.entryID_list
        self.listView.clear()
        self.listView.addItems(self.currentList)
        self.searchBar.clear()

    def show_entry(self, item):
        if item:
            entryID = str(item.text())
            for i, name in enumerate(self.form_entries):
                bib_entry = self.bib_database.entries[entryID]
                if name.lower() == 'author':
                    field_text = formatting.format_author_list(bib_entry, showAll=True)

                elif name.lower() in bib_entry.fields.keys():
                    if name.lower() == 'journal':
                        # Convert the LaTeX shorthand to real text:
                        field_text = formatting.format_journal_name(bib_entry)

                    elif name.lower() == 'adsurl':
                        urlLink = bib_entry.fields[name.lower()].replace('\n', ' ')
                        urlText = formatting.format_reference(bib_entry, 1, 2)
                        field_text = "<a href=\"%s\">%s</a>" % (urlLink, urlText)

                    else:
                        field_text = bib_entry.fields[name.lower()].replace('\n', ' ')
                        field_text = formatting.clean_string(field_text)

                else:
                    field_text = ''

                self.form_fields[i].setText(field_text)

    def file_new(self):
        pass

    def file_open(self):
        filters = "BibTeX files (*.bib);;All files (*.*)"
        selected_filter = "BibTeX (*.bib)"
        database_file = QtGui.QFileDialog.getOpenFileName(self, 'Open File', filter=filters,
                                                          selectedFilter=selected_filter)

        database_file = str(database_file)
        if database_file:
            self.statusBar().showMessage('Opened BibTeX database: ' + database_file, 8000)
        else:
            return

        with open(database_file, 'r') as bibtex_file:
            self.bib_database = pybtex.database.parse_file(bibtex_file)
        self.entryID_list = sorted(self.bib_database.entries.keys())
        self.currentList = self.entryID_list
        self.listView.addItems(self.entryID_list)

        self.listView.setCurrentRow(0)
        self.listView.setFocus()
        self.raise_()
        self.activateWindow()

    def file_save(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')

        with open(str(name), 'w') as bibtex_file:
            self.bib_database.to_file(bibtex_file)
        new_msg = 'Saved current BibTeX database to file: ' + name
        self.statusBar().showMessage(new_msg, 8000)

    def update_entry(self):
        edit_fields = self.editor.edit_fields
        entryID = self.editor.original_entry.key
        for field in edit_fields.keys():
            if field not in self.editor.original_entry.persons.keys():
                changed_data = str(edit_fields[field].text())
                self.bib_database.entries[entryID].fields[field] = changed_data
            else:
                changed_data = str(edit_fields[field].text())
                person_list = changed_data.split(' and ')
                new_person_list = list()
                for name in person_list:
                    person = pybtex.database.Person(name)
                    new_person_list.append(person)
                self.bib_database.entries[entryID].persons[field] = new_person_list
        self.editor.close()
        ID_as_listViewItem = QtGui.QListWidgetItem(entryID)
        self.show_entry(ID_as_listViewItem)

    def download(self):
        self.completed = 0

        while self.completed < 100 and self.completed > 0:
            time.sleep(0.01)
            self.completed += 1
            QtGui.QApplication.processEvents()
            self.progress.setValue(self.completed)

    def close_application(self):
        choice = QtGui.QMessageBox.question(self, 'Exit!',
                                            "Do you really want to quit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            # print "Quitting Application"
            sys.exit()
        else:
            pass


class SearchWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SearchWindow, self).__init__(parent)
        self.setWindowTitle("Search Bibliography")
        self.search_button = QtGui.QPushButton("Search")
        self.search_button.clicked.connect(parent.search_content)
        self.quit_button = QtGui.QPushButton("Close")
        self.quit_button.clicked.connect(self.close)
        self.reset_button = QtGui.QPushButton("Reset")
        self.reset_button.clicked.connect(parent.reset_search_form)

        # search_terms = ['author', 'journal', 'year', 'title', 'abstract', 'volume']
        search_terms = ['author', 'title', 'journal', 'keyword']

        searchGrid = QtGui.QGridLayout()
        for row, term in enumerate(search_terms):
            label = QtGui.QLabel(term.capitalize())
            if term in parent.search_form_fields.keys():
                edit = parent.search_form_fields[term]
            else:
                edit = QtGui.QLineEdit()
                parent.search_form_fields[term] = edit
            searchGrid.addWidget(label, row, 0)
            searchGrid.addWidget(edit, row, 1)

        vbox = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.search_button)
        hbox.addWidget(self.reset_button)
        hbox.addWidget(self.quit_button)

        vbox.addLayout(searchGrid)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.show()


class EditWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(EditWindow, self).__init__(parent)
        self.setWindowTitle("Edit Bib Entry")
        self.save_button = QtGui.QPushButton("Update Entry")
        self.save_button.clicked.connect(parent.update_entry)
        self.quit_button = QtGui.QPushButton("Cancel")
        self.quit_button.clicked.connect(self.close)
        self.reset_button = QtGui.QPushButton("Recover Original")
        self.reset_button.clicked.connect(self.recover_entry)

        entryID = str(parent.listView.currentItem().text())
        self.original_entry = copy.deepcopy(parent.bib_database.entries[entryID])
        self.edit_fields = dict()

        grid_layout = self.display_all_fields(parent.bib_database.entries[entryID])

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.quit_button)
        hbox.addWidget(self.reset_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid_layout)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.show()

    def display_all_fields(self, bib_entry):
        fields_in_entry = bib_entry.fields.keys() + bib_entry.persons.keys()
        # all_fields = formatting.all_bibtex_fields
        # for field in fields_in_entry:
        #     if field not in all_fields:
        #         all_fields.append(field)
        #
        grid_layout = QtGui.QGridLayout()
        # for field in bib_entry.fields.keys():
        #     if field.lower() not in all_fields:
        #         all_fields.append(field)

        for row, field in enumerate(fields_in_entry):
            data = bib_entry.fields[field]

            label = QtGui.QLabel(field.capitalize() + ': ')
            line_edit = QtGui.QLineEdit(data)
            self.edit_fields[field] = line_edit
            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(line_edit, row, 1)

        return grid_layout

    def recover_entry(self):
        fields_in_entry = self.original_entry.fields.keys()
        fields_in_entry += self.original_entry.persons.keys()
        for field in fields_in_entry:
            orig_data = self.original_entry.fields[field]
            self.edit_fields[field].clear()
            self.edit_fields[field].setText(orig_data)


def main():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    GUI.raise_()
    sys.exit(app.exec_())


main()
