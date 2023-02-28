"""
Python EZ Backup

This is a simple, zero-bloat Python application for backing up data.

It uses the following technologies and libraries:
- Python 3.7
- PyQt 5
- qtmodern

The app is intended for educational or demonstration purposes only and should not be used in a production environment
without further testing and security measures.

To run the app, you will need to have Python and the required libraries installed.
You can run the app by running the command:
    'python, python3, or py (depending on your setup) main.py' in the terminal.

This project is released under the MIT License.

This script contains the layout of all ui elements.

Author: 0xtommyOfficial, Molmez LTD (www.molmez.io)
Date Published: 28 February 2023
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRegExp
import resources  # Do Not Remove


def critical_message(message: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle("Critical Error")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def informational_message(message: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def warning_message(message: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Warning!")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def question_message(message: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(message)
    msg.setWindowTitle("Question")
    msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    msg.exec_()


class AboutUI(object):
    def setup_ui(self, about):
        about.setObjectName("about")
        about.resize(300, 250)
        about.setMinimumSize(QtCore.QSize(300, 250))
        about.setMaximumSize(QtCore.QSize(300, 250))
        about.setWhatsThis("")

        self.central_widget = QtWidgets.QWidget(about)
        self.central_widget.setObjectName('central_widget')

        self.logo = QtWidgets.QLabel(self.central_widget)
        self.logo.setGeometry(QtCore.QRect(75, 0, 150, 150))
        self.logo.setToolTip('')
        self.logo.setWhatsThis('')
        self.logo.setObjectName('label_logo')

        self.description = QtWidgets.QLabel(self.central_widget)
        self.description.setGeometry(QtCore.QRect(25, 120, 250, 60))
        self.description.setToolTip('')
        self.description.setWhatsThis('')
        self.description.setObjectName('label_description')
        self.description.setAlignment(QtCore.Qt.AlignCenter)
        self.description.setFont(QtGui.QFont('Helvetica', 12))
        self.description.setStyleSheet("font-weight: bold")

        self.web_url = QtWidgets.QLabel(self.central_widget)
        self.web_url.setGeometry(QtCore.QRect(25, 175, 250, 25))
        self.web_url.setToolTip('')
        self.web_url.setWhatsThis('')
        self.web_url.setObjectName('label_url')
        self.web_url.setAlignment(QtCore.Qt.AlignCenter)
        self.web_url.setFont(QtGui.QFont('Helvetica', 12))

        self.ok_button = QtWidgets.QPushButton(self.central_widget)
        self.ok_button.setGeometry(QtCore.QRect(100, 210, 100, 30))
        self.ok_button.setToolTip('')
        self.ok_button.setWhatsThis('')
        self.ok_button.setObjectName('btn_ok')
        self.ok_button.setFont(QtGui.QFont('Helvetica', 12))
        self.ok_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.retranslate_ui(about)
        QtCore.QMetaObject.connectSlotsByName(about)

    def retranslate_ui(self, about):
        _translate = QtCore.QCoreApplication.translate
        about.setWindowTitle(_translate('about', 'About'))
        # self.logo.setText(_translate('about', 'MOLMEZ LOGO'))
        self.logo.setPixmap(QtGui.QPixmap(':/images/logo1.png'))
        self.description.setText(_translate('about', 'Molmez LTD\nEZ Backup Tool'))
        self.web_url.setText(_translate('about', '<a href=\"http://www.molmez.io\">www.molmez.io</a>'))
        self.web_url.setOpenExternalLinks(True)
        self.ok_button.setText(_translate('about', 'OK'))
        self.ok_button.clicked.connect(self.close)


class UiMainWindow(object):

    def setup_ui(self, main_window):
        main_window.setObjectName('main_window')
        main_window.setEnabled(True)
        main_window.resize(550, 450)
        main_window.setMinimumSize(QtCore.QSize(550, 450))
        main_window.setMaximumSize(QtCore.QSize(550, 450))
        main_window.setWhatsThis('')

        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName('central_widget')

        self.label_included_list = QtWidgets.QLabel(self.central_widget)
        self.label_included_list.setGeometry(QtCore.QRect(10, 10, 100, 23))
        self.label_included_list.setToolTip('')
        self.label_included_list.setWhatsThis('')
        self.label_included_list.setObjectName('label_included_list')

        self.list_view_include = QtWidgets.QListView(self.central_widget)
        self.list_view_include.setGeometry(QtCore.QRect(10, 35, 400, 135))
        self.list_view_include.setMinimumSize(QtCore.QSize(400, 135))
        self.list_view_include.setMaximumSize(QtCore.QSize(400, 135))
        self.list_view_include.setToolTip('')
        self.list_view_include.setWhatsThis('')
        self.list_view_include.setObjectName('list_view_include')

        self.label_excluded_list = QtWidgets.QLabel(self.central_widget)
        self.label_excluded_list.setGeometry(QtCore.QRect(10, 175, 100, 23))
        self.label_excluded_list.setToolTip('')
        self.label_excluded_list.setWhatsThis('')
        self.label_excluded_list.setObjectName('label_excluded_list')

        self.list_view_exclude = QtWidgets.QListView(self.central_widget)
        self.list_view_exclude.setGeometry(QtCore.QRect(10, 200, 400, 135))
        self.list_view_exclude.setMinimumSize(QtCore.QSize(400, 135))
        self.list_view_exclude.setMaximumSize(QtCore.QSize(400, 135))
        self.list_view_exclude.setToolTip('')
        self.list_view_exclude.setWhatsThis('')
        self.list_view_exclude.setObjectName('list_view_exclude')

        self.button_reset = QtWidgets.QPushButton(self.central_widget)
        self.button_reset.setGeometry(QtCore.QRect(440, 10, 75, 23))
        self.button_reset.setToolTip('clear current settings')
        self.button_reset.setWhatsThis('reset')
        self.button_reset.setObjectName('button_reset')
        self.button_reset.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_save = QtWidgets.QPushButton(self.central_widget)
        self.button_save.setGeometry(QtCore.QRect(440, 40, 75, 23))
        self.button_save.setToolTip('save current settings')
        self.button_save.setWhatsThis('save settings')
        self.button_save.setObjectName('button_save')
        self.button_save.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_load = QtWidgets.QPushButton(self.central_widget)
        self.button_load.setGeometry(QtCore.QRect(440, 70, 75, 23))
        self.button_load.setToolTip('load previous settings')
        self.button_load.setWhatsThis('load settings')
        self.button_load.setObjectName('button_load')
        self.button_load.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_add_dir = QtWidgets.QPushButton(self.central_widget)
        self.button_add_dir.setGeometry(QtCore.QRect(440, 100, 75, 23))
        self.button_add_dir.setToolTip('select directory to include')
        self.button_add_dir.setWhatsThis('include directory')
        self.button_add_dir.setObjectName('button_add_dir')
        self.button_add_dir.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_add_files = QtWidgets.QPushButton(self.central_widget)
        self.button_add_files.setGeometry(QtCore.QRect(440, 130, 75, 23))
        self.button_add_files.setToolTip('select file(s) to include')
        self.button_add_files.setWhatsThis('include file(s)')
        self.button_add_files.setObjectName('button_add_files')
        self.button_add_files.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_exclude_dir = QtWidgets.QPushButton(self.central_widget)
        self.button_exclude_dir.setGeometry(QtCore.QRect(440, 160, 75, 23))
        self.button_exclude_dir.setToolTip('select directory to exclude')
        self.button_exclude_dir.setWhatsThis('exclude directory')
        self.button_exclude_dir.setObjectName('button_exclude_dir')
        self.button_exclude_dir.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_exclude_files = QtWidgets.QPushButton(self.central_widget)
        self.button_exclude_files.setGeometry(QtCore.QRect(440, 190, 75, 23))
        self.button_exclude_files.setToolTip('select file(s) to exclude')
        self.button_exclude_files.setWhatsThis('exclude file(s)')
        self.button_exclude_files.setObjectName('button_exclude_files')
        self.button_exclude_files.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_remove = QtWidgets.QPushButton(self.central_widget)
        self.button_remove.setGeometry(QtCore.QRect(440, 220, 75, 23))
        self.button_remove.setToolTip('remove selected')
        self.button_remove.setWhatsThis('remove')
        self.button_remove.setObjectName('button_remove')
        self.button_remove.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.button_exit = QtWidgets.QPushButton(self.central_widget)
        self.button_exit.setGeometry(QtCore.QRect(440, 250, 75, 23))
        self.button_exit.setToolTip('exit application')
        self.button_exit.setWhatsThis('exit')
        self.button_exit.setObjectName('button_exit')
        self.button_exit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.label_exclude_by = QtWidgets.QLabel(self.central_widget)
        self.label_exclude_by.setGeometry(QtCore.QRect(430, 280, 100, 23))
        self.label_exclude_by.setToolTip('exclude by file extension')
        self.label_exclude_by.setWhatsThis('exclude by')
        self.label_exclude_by.setObjectName('label_exclude_by')

        self.input_exclude_by = QtWidgets.QLineEdit(self.central_widget)
        self.input_exclude_by.setGeometry(QtCore.QRect(420, 305, 118, 23))
        self.input_exclude_by.setToolTip('eg: jpg,png,txt,py')
        self.input_exclude_by.setWhatsThis('excluded file extensions')
        self.input_exclude_by.setObjectName('input_exclude_by')

        # limit input to letters seperated by commas
        reg_expression = QRegExp('^([a-zA-Z\s]+,[a-zA-Z\s]+,)*$')
        validator = QtGui.QRegExpValidator(reg_expression)

        self.input_exclude_by.setValidator(validator)

        self.button_set_backup_dir = QtWidgets.QPushButton(self.central_widget)
        self.button_set_backup_dir.setGeometry(QtCore.QRect(210, 350, 125, 23))
        self.button_set_backup_dir.setToolTip('set backup location')
        self.button_set_backup_dir.setWhatsThis('set backup location')
        self.button_set_backup_dir.setObjectName('button_set_backup_dir')
        self.button_set_backup_dir.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.label_root_backup_dir = QtWidgets.QLabel(self.central_widget)
        self.label_root_backup_dir.setGeometry(QtCore.QRect(15, 380, 520, 23))
        self.label_root_backup_dir.setToolTip('current backup location')
        self.label_root_backup_dir.setWhatsThis('')
        self.label_root_backup_dir.setObjectName('label_root_backup_dir')

        self.button_run = QtWidgets.QPushButton(self.central_widget)
        self.button_run.setGeometry(QtCore.QRect(340, 350, 75, 23))
        self.button_run.setToolTip('run backup')
        self.button_run.setWhatsThis('run backup')
        self.button_run.setObjectName('button_run')
        self.button_run.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.progress_bar = QtWidgets.QProgressBar(self.central_widget)
        self.progress_bar.setGeometry(QtCore.QRect(420, 350, 118, 23))
        self.progress_bar.setToolTip('backup progress')
        self.progress_bar.setWhatsThis('backup progress')
        self.progress_bar.setProperty('value', 0)
        self.progress_bar.setObjectName('progress_bar')

        main_window.setCentralWidget(self.central_widget)

        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName('statusbar')

        main_window.setStatusBar(self.status_bar)

        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 550, 20))
        self.menu_bar.setObjectName('menubar')

        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_file.setObjectName('menuFile')
        self.menu_help = QtWidgets.QMenu(self.menu_bar)
        self.menu_help.setObjectName('menuHelp')

        main_window.setMenuBar(self.menu_bar)

        self.action_about = QtWidgets.QAction(main_window)
        self.action_about.setWhatsThis('')
        self.action_about.setObjectName('action_about')

        self.action_save_settings = QtWidgets.QAction(main_window)
        self.action_save_settings.setWhatsThis('')
        self.action_save_settings.setObjectName('action_save_settings')

        self.action_load_settings = QtWidgets.QAction(main_window)
        self.action_load_settings.setWhatsThis('')
        self.action_load_settings.setObjectName('action_load_settings')

        self.action_exit = QtWidgets.QAction(main_window)
        self.action_exit.setWhatsThis('')
        self.action_exit.setObjectName('action_exit')

        self.menu_file.addAction(self.action_save_settings)
        self.menu_file.addAction(self.action_load_settings)
        self.menu_file.addAction(self.action_exit)
        self.menu_help.addAction(self.action_about)

        self.menu_bar.addAction(self.menu_file.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate

        main_window.setWindowTitle(_translate('MainWindow', 'Tom\'s easy backup tool'))

        self.label_included_list.setText(_translate('MainWindow', 'Selected files..'))
        self.label_excluded_list.setText(_translate('MainWindow', 'Excluded files..'))
        self.label_exclude_by.setText(_translate('MainWindow', 'Exclude by file ext..'))
        self.label_root_backup_dir.setText(_translate('MainWindow', ''))
        self.label_root_backup_dir.setAlignment(QtCore.Qt.AlignRight)

        self.button_reset.setText(_translate('MainWindow', 'Reset'))
        self.button_save.setText(_translate('MainWindow', 'Save'))
        self.button_load.setText(_translate('MainWindow', 'Load'))
        self.button_add_dir.setText(_translate('MainWindow', 'Add Dir'))
        self.button_add_files.setText(_translate('MainWindow', 'Add Files'))
        self.button_exclude_dir.setText(_translate('MainWindow', 'Exclude Dir'))
        self.button_exclude_files.setText(_translate('MainWindow', 'Exclude Files'))
        self.button_remove.setText(_translate('MainWindow', 'Remove'))
        self.button_exit.setText(_translate('MainWindow', 'Exit'))
        self.button_run.setText(_translate('MainWindow', 'Run'))
        self.button_set_backup_dir.setText(_translate('MainWindow', 'Set Backup Location..'))

        self.input_exclude_by.setPlaceholderText('eg: jpg,png,txt,py')

        self.menu_file.setTitle(_translate('MainWindow', 'File'))
        self.menu_help.setTitle(_translate('MainWindow', 'Help'))

        self.action_about.setText(_translate('MainWindow', 'About'))
        self.action_about.setToolTip(_translate('MainWindow', 'About'))
        self.action_save_settings.setText(_translate('MainWindow', 'Save Settings'))
        self.action_save_settings.setToolTip(_translate('MainWindow', 'Save Settings'))
        self.action_load_settings.setText(_translate('MainWindow', 'Load Settings'))
        self.action_load_settings.setToolTip(_translate('MainWindow', 'Load Settings'))
        self.action_exit.setText(_translate('MainWindow', 'Exit'))
        self.action_exit.setToolTip(_translate('MainWindow', 'Exit'))
