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

Run this script to launch app

-- Populate the include/exclude lists
-- Add any extensions you need to exclude
-- Save your settings for future use
-- Run Backup

Author: 0xtommyOfficial, Molmez LTD (www.molmez.io)
Date Published: 28 February 2023
"""
import sys
import os
import traceback
import qtmodern.styles
import qtmodern.windows
import json
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDesktopWidget, QFileDialog
from pathlib import Path
from hurry.filesize import size, alternative
from backup_helpers import BackupSelection, BackupSettings, BackupLogEntry, count_total_files, get_date_and_time
from backup_logger import logger
import gui


# logging test:
# logger.info('backup application launched')
# logger.error('error test')
# try:
#     a = [1, 2, 3]
#     val = a[4]
# except Exception as error:
#     logger.exception(error)

# TODO:
#       Potential slow downs due to system specific..? file caches / threading??


def log_error(error_details: tuple):
    """
    receive an error message, log it, display error message box
    :param error_details: (error, traceback, log message)
    """
    logger.error(error_details[2])
    logger.error(error_details[0])
    logger.error(error_details[1])


def encode_backup_settings(o: object):
    """
    takes an instance of BackupSettings and generates a JSON serializable dictionary
    :param o: BackupSettings object
    :return: JSON serializable dictionary
    """
    if isinstance(o, BackupSettings):
        return {'included_paths': o.included_paths,
                'excluded_paths': o.excluded_paths,
                'excluded_extensions': o.excluded_file_extensions,
                'backup_root_directory': o.root_backup_directory,
                o.__class__.__name__: True}
    else:
        raise TypeError('object provided is not JSON serializable, object must be of type BackupSettings')


def decode_backup_settings(dct: dict):
    """
    takes a json dictionary and instantiates BackupSettings
    :param dct: input json dictionary
    :return: returns an instance of BackupSettings if successful, otherwise returns 0
    """
    if BackupSettings.__name__ in dct:
        try:
            settings = BackupSettings(included_paths=dct['included_paths'],
                                      excluded_paths=dct['excluded_paths'],
                                      excluded_file_extensions=dct['excluded_extensions'],
                                      root_backup_directory=dct['backup_root_directory'])
        except KeyError as key_error:
            log_error((key_error, traceback.format_exc(), 'error decoding backup settings'))
            gui.warning_message('Unable to load settings. See error log for more information')
            return 0
        else:
            return settings
    return 0


def encode_backup_log(o: object):
    """
    takes an instance of BackupLogEntry and generates a JSON serializable dictionary
    :param o: BackupLogEntry object
    :return: JSON serializable dictionary
    """
    if isinstance(o, BackupLogEntry):
        return {'date': o.backup_date,
                'time': o.backup_time,
                'file_count': o.total_count,
                'total_memory': o.total_memory,
                'included': o.included_in_backup,
                'excluded': o.excluded_from_backup,
                o.__class__.__name__: True}
    else:
        raise TypeError('object provided is not JSON serializable, object must be of type BackupLogEntry')


class AboutWindow(QWidget, gui.AboutUI):
    """
    initialises the "About" GUI, inherits from QWidget and a custom GUI class
    """

    def __init__(self, *args, obj=None, **kwargs):
        super(AboutWindow, self).__init__(*args, **kwargs)
        # layout the GUI
        self.setup_ui(self)


class MainWindow(QMainWindow, gui.UiMainWindow):
    """
    initialises the main GUI, inherits from QMainWindow and a custom GUI class
    """

    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # layout the GUI
        self.setup_ui(self)

        # center the application on the screen
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # setup threading
        self.threadpool = QtCore.QThreadPool()
        # print(f' maximum threads: {self.threadpool.maxThreadCount()}')
        self.workers = []
        self.progress = 0
        self.total_memory = 0

        # create instance of 'About' window
        self.about_window = AboutWindow()

        # initialise variable for backup directory
        self.root_backup_dir = None

        # initialise lists for saving settings
        self.included_paths_list = []
        self.excluded_paths_list = []
        self.excluded_extensions_list = []

        # set up menu actions
        self.action_save_settings.triggered.connect(self.save_settings)
        self.action_load_settings.triggered.connect(self.load_settings)
        self.action_exit.triggered.connect(self.exit_application)
        self.action_about.triggered.connect(self.show_about_window)

        # set up GUI buttons
        self.button_reset.clicked.connect(self.cleanup)
        self.button_save.clicked.connect(self.save_settings)
        self.button_load.clicked.connect(self.load_settings)
        self.button_add_dir.clicked.connect(self.add_directory)
        self.button_exclude_dir.clicked.connect(self.exclude_directory)
        self.button_add_files.clicked.connect(self.add_files)
        self.button_exclude_files.clicked.connect(self.exclude_files)
        self.button_remove.clicked.connect(self.remove_selected)
        self.button_exit.clicked.connect(self.exit_application)
        self.button_set_backup_dir.clicked.connect(self.set_backup_directory)
        self.button_run.clicked.connect(self.run_backup)

        # catch app quit command (top right corner 'x')
        app.aboutToQuit.connect(self.closeEvent)

        # set the data model for the included and excluded GUI list views
        self.files_to_include_model = QtGui.QStandardItemModel()
        self.list_view_include.setModel(self.files_to_include_model)
        self.files_to_exclude_model = QtGui.QStandardItemModel()
        self.list_view_exclude.setModel(self.files_to_exclude_model)

    def show_about_window(self):
        self.about_window.show()

    def exit_application(self):
        sys.exit(0)

    def closeEvent(self, event):
        """
        capture the clicking of 'x' or quit
        issue kill command to all running threads
        close all open windows
        :param event: click event
        """
        self.kill_all()
        if self.about_window.isVisible():
            self.about_window.close()
        event.accept()

    def save_settings(self):
        """
        user input desired file name
        collate and encode settings for saving as a JSON file
        """

        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter=self.tr('.json'))
        if not filename:
            return

        if '.json' not in filename:
            filename = f'{filename}.json'
        self.excluded_extensions_list = self.input_exclude_by.text().split(',') if self.input_exclude_by.text() else []
        root_backup_dir_string = str(self.root_backup_dir.resolve()) if self.root_backup_dir else ''
        try:
            backup_settings = BackupSettings(included_paths=self.included_paths_list,
                                             excluded_paths=self.excluded_paths_list,
                                             excluded_file_extensions=self.excluded_extensions_list,
                                             root_backup_directory=root_backup_dir_string)
        except (ValueError, TypeError) as error:
            log_error((error, traceback.format_exc(), 'error creating BackupSettings'))
            gui.informational_message('Unable to save settings. See error log for more information.')
        else:
            backup_settings_encoded = encode_backup_settings(backup_settings)
            try:
                with open(filename, 'w') as file:
                    json.dump(backup_settings_encoded, file, indent=4, sort_keys=False)
            except OSError as os_error:
                log_error((os_error, traceback.format_exc(), 'error saving settings'))
                gui.informational_message('Unable to save settings. See error log for more information.')

    def load_settings(self):
        """
        load selected JSON file and update the GUI
        """

        filename, _ = QFileDialog.getOpenFileName(self, 'Load File', filter=self.tr('*.json'))
        if not filename:
            return

        with open(filename, 'r') as f:
            try:
                loaded_json = json.load(f)
            except (OSError, json.JSONDecodeError) as json_load_error:
                log_error((json_load_error, traceback.format_exc(), f'error loading {filename}'))
                gui.informational_message('Unable to load settings. See error log for more information.')
                return
            else:
                loaded_backup_settings = decode_backup_settings(loaded_json)
                if not loaded_backup_settings:
                    return

                self.included_paths_list = loaded_backup_settings.included_paths
                self.excluded_paths_list = loaded_backup_settings.excluded_paths
                self.excluded_extensions_list = loaded_backup_settings.excluded_file_extensions

                self.root_backup_dir = Path(loaded_backup_settings.root_backup_directory)
                self.label_root_backup_dir.setText(f'backup location: {self.root_backup_dir}')

                self.files_to_include_model.clear()
                self.files_to_exclude_model.clear()
                self.input_exclude_by.clear()

                for _ in self.included_paths_list:
                    try:
                        item = QtGui.QStandardItem(_)
                        self.files_to_include_model.appendRow(item)
                    except TypeError as type_error:
                        log_error((type_error, traceback.format_exc(), 'error appending item to model row'))

                for _ in self.excluded_paths_list:
                    try:
                        item = QtGui.QStandardItem(_)
                        self.files_to_exclude_model.appendRow(item)
                    except TypeError as type_error:
                        log_error((type_error, traceback.format_exc(), 'error appending item to model row'))

                if self.excluded_extensions_list:

                    # iterate a shallow copy of the list
                    for item in self.excluded_extensions_list[:]:
                        if not item:
                            self.excluded_extensions_list.remove(item)
                            continue
                        # if string contains numbers or non-alphanumeric characters, remove from original list
                        if any(c.isdigit() for c in item) or not any(c.isalnum() for c in item):
                            self.excluded_extensions_list.remove(item)

                    # set GUI exclude by text
                    self.input_exclude_by.setText(','.join(self.excluded_extensions_list))

    def add_directory(self):
        """
        add selected directory to be included in the backup
        """

        selected_directory = QFileDialog.getExistingDirectory(self, 'Select Directory')

        if not selected_directory:
            return

        # append to list
        self.included_paths_list.append(selected_directory)
        # append to GUI list model
        item = QtGui.QStandardItem(selected_directory)
        self.files_to_include_model.appendRow(item)

    def add_files(self):
        """
        add selected file(s) to be included in the backup
        """

        selected_files, _ = QFileDialog.getOpenFileNames(self, 'Select File(s)')

        for _ in selected_files:
            # append to list
            self.included_paths_list.append(_)
            # append to GUI list model
            file = QtGui.QStandardItem(_)
            self.files_to_include_model.appendRow(file)

    def exclude_directory(self):
        """
        add selected directory to be excluded from the backup
        """

        selected_directory = QFileDialog.getExistingDirectory(self, 'Select Directory')

        if not selected_directory:
            return

        # append to list
        self.excluded_paths_list.append(selected_directory)
        # append to GUI list model
        item = QtGui.QStandardItem(selected_directory)
        self.files_to_exclude_model.appendRow(item)

    def exclude_files(self):
        """
        add selected file(s) to be excluded from the backup
        """

        selected_files, _ = QFileDialog.getOpenFileNames(self, 'Select File(s)')

        for _ in selected_files:
            # append to list
            self.excluded_paths_list.append(_)
            # append to GUI list model
            file = QtGui.QStandardItem(_)
            self.files_to_exclude_model.appendRow(file)

    def remove_selected(self):
        """
        remove selected item(s) from the GUI list models
        """

        for item in self.list_view_include.selectedIndexes():
            self.included_paths_list.remove(item.data())
            self.files_to_include_model.removeRow(item.row())

        for item in self.list_view_exclude.selectedIndexes():
            self.excluded_paths_list.remove(item.data())
            self.files_to_exclude_model.removeRow(item.row())

    def set_backup_directory(self):
        """
        set selected directory as the root backup directory
        """

        selected_directory = QFileDialog.getExistingDirectory(self, 'Select Root Backup Directory')

        if not selected_directory:
            return
        # set directory
        self.root_backup_dir = Path(selected_directory)
        # update GUI
        self.label_root_backup_dir.setText(f'backup location: {self.root_backup_dir.resolve()}')

    def save_backup_log(self):

        date_stamp, time_stamp = get_date_and_time()
        try:
            backup_log = BackupLogEntry(date_stamp=date_stamp.replace('-', ' '),
                                        time_stamp=time_stamp.replace('-', ':'),
                                        file_count=self.progress_bar.maximum(),
                                        total_memory=size(self.total_memory, alternative),
                                        included=self.included_paths_list,
                                        excluded=[self.excluded_paths_list, self.excluded_extensions_list])
        except (ValueError, TypeError) as backup_log_error:
            log_error((backup_log_error, traceback.format_exc(), 'error creating BackupLogEntry'))
            gui.informational_message('Unable to save backup log. See error log for more information.')
        else:
            encoded_backup_log = encode_backup_log(backup_log)

            file_name = f'Backup_Log_{date_stamp}_{time_stamp}.json'
            save_path = os.path.join(self.root_backup_dir, file_name)
            try:
                with open(save_path, 'w') as file:
                    json.dump(encoded_backup_log, file, indent=4, sort_keys=False)
            except OSError as os_error:
                log_error((os_error, traceback.format_exc(), 'error saving backup log'))
                gui.informational_message('Unable to save backup log. See error log for more information.')

    def set_max_progress_value(self, max_value: int):
        """
        set the total progress possible for the progress bar
        :param max_value: integer representing the maximum possible progress
        """
        self.progress_bar.setMaximum(max_value)

    def update_progress(self, progress: int):
        """
        update the progress bar, save backup log if complete, reset GUI
        :param progress: integer representing the current progress value
        """
        # increase progress
        self.progress += progress
        # update GUI
        self.progress_bar.setValue(self.progress)
        if self.progress == self.progress_bar.maximum():
            print('100% complete')
            print('saving backup log file..')
            self.save_backup_log()
            gui.informational_message('Backup Complete! See backup log file in backup directory for details.')
            self.cleanup()
            self.set_gui_state(1)

    def update_memory_count(self, increase_by: int):
        self.total_memory += increase_by

    def update_status(self, status_message: str):
        """
        update the status label
        :param status_message: string to display
        """
        self.label_root_backup_dir.setText(status_message)

    def process_error(self, error_message: tuple):
        """
        receive an error message, log it, display error message box
        :param error_message: (error, traceback, log message, window message)
        """
        log_error((error_message[0], error_message[1], error_message[2]))
        self.cancel_backup()
        gui.critical_message(error_message[3])

    def enqueue(self, worker):
        """
        set up a worker and pass it to the thread pool
        :param worker: QRunnable class
        """
        worker.worker_signals.error.connect(self.process_error)
        worker.worker_signals.progress.connect(self.update_progress)
        worker.worker_signals.memory_count.connect(self.update_memory_count)
        worker.worker_signals.status.connect(self.update_status)
        worker.worker_signals.new_thread.connect(self.enqueue)
        self.workers.append(worker)
        self.threadpool.start(worker)

    def kill_all(self):
        """
        issue kill command to all current threads
        """
        for worker in self.workers:
            worker.kill()

    def cancel_backup(self):
        """
        cancel the running backup process
        """
        self.button_exit.setEnabled(False)
        # disable GUI
        self.set_gui_state(0)
        # kill all threads
        self.kill_all()
        # reconnect exit button to quit application
        self.button_exit.clicked.connect(self.exit_application)
        self.button_exit.setText('Exit')
        # clear the status label
        self.update_status('')
        # enable GUI
        self.set_gui_state(1)

    def cleanup(self):
        """
        clear this session's inputs
        """
        self.root_backup_dir = ''
        self.included_paths_list = []
        self.excluded_paths_list = []
        self.excluded_extensions_list = []
        self.label_root_backup_dir.clear()
        self.included_paths_list.clear()
        self.files_to_include_model.clear()
        self.files_to_exclude_model.clear()
        self.input_exclude_by.clear()
        self.progress_bar.setValue(0)

    def set_gui_state(self, unlocked=1):
        """
        enables and disables GUI buttons and inputs
        :param unlocked: 0 = off, 1 = on
        """

        if unlocked:
            self.button_reset.setEnabled(True)
            self.button_run.setEnabled(True)
            self.button_load.setEnabled(True)
            self.button_save.setEnabled(True)
            self.button_remove.setEnabled(True)
            self.button_add_files.setEnabled(True)
            self.button_add_dir.setEnabled(True)
            self.button_exclude_dir.setEnabled(True)
            self.button_exclude_files.setEnabled(False)
            self.button_set_backup_dir.setEnabled(True)
            self.menu_file.setEnabled(True)
            self.input_exclude_by.setEnabled(True)
            self.button_exit.setEnabled(True)
        else:
            self.button_reset.setEnabled(False)
            self.button_run.setEnabled(False)
            self.button_load.setEnabled(False)
            self.button_save.setEnabled(False)
            self.button_remove.setEnabled(False)
            self.button_add_files.setEnabled(False)
            self.button_add_dir.setEnabled(False)
            self.button_exclude_dir.setEnabled(False)
            self.button_exclude_files.setEnabled(False)
            self.button_set_backup_dir.setEnabled(False)
            self.menu_file.setEnabled(False)
            self.input_exclude_by.setEnabled(False)
            self.button_exit.setEnabled(False)

    def run_backup(self):
        """
        collate inputs and assign workers to each for processing
        initialise queuing to the thread pool
        """

        if not self.root_backup_dir:
            gui.informational_message('Please choose a backup location.')
            return

        files_to_include = []
        files_to_exclude = []

        # lock gui
        self.set_gui_state(0)

        # creat a list of paths from the 'include' and 'exclude' file/dir gui inputs
        for item in range(self.files_to_include_model.rowCount()):
            files_to_include.append(Path(self.files_to_include_model.index(item, 0).data()))

        for item in range(self.files_to_exclude_model.rowCount()):
            files_to_exclude.append(Path(self.files_to_exclude_model.index(item, 0).data()))

        # get file count and set the progress bar maximum value
        self.set_max_progress_value(count_total_files(files_to_include))

        # create list of file types to exclude from gui input
        self.excluded_extensions_list = self.input_exclude_by.text().split(',') if self.input_exclude_by.text() else []

        for item in files_to_include:
            # create worker for threading
            worker = BackupSelection(source=item,
                                     destination=self.root_backup_dir,
                                     thread_pool=self.threadpool,
                                     ignore_files=files_to_exclude,
                                     ignore_extensions=self.excluded_extensions_list,
                                     root_input=True)
            # send worker to thread pool
            self.enqueue(worker)

        # enable exit button as cancel
        self.button_exit.clicked.connect(self.cancel_backup)
        self.button_exit.setText('Cancel')
        self.button_exit.setEnabled(True)


if __name__ == '__main__':

    # initialise the QT application
    app = QApplication(sys.argv)
    window = MainWindow()
    # apply qtmodern style
    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(window)
    # set fixed size of main window
    mw.setFixedSize(mw.size())
    # display GUI
    mw.show()
    # execute the application
    # capture response (0 = success, 1 = error)
    app_ref = app.exec_()
    # pass response to parent (shell)
    sys.exit(app_ref)
