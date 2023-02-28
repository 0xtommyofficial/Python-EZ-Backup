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

This script provides helper functions and classes to the main application.

Author: 0xtommyOfficial, Molmez LTD (www.molmez.io)
Date Published: 28 February 2023
"""
import os
import shutil
import traceback
import datetime
from pathlib import Path
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject


def get_date_and_time():
    date = datetime.date.today().strftime("%d-%B-%Y")
    current_time = datetime.datetime.now().time().strftime("%H-%M-%S")
    return date, current_time


def check_existing_file(src: Path, dest: Path):
    if os.path.getmtime(src) > os.path.getmtime(dest):
        return True
    return False


def get_drive_letters():
    drives = ''.join(letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{letter}:/'))
    return drives


def count_total_files(input_select: list):
    """
    count files in each item from a list of directories and files
    :param input_select: list of directories and files
    :return: total number of files
    """
    count = 0
    for item in input_select:
        if os.path.isfile(item):
            count += 1
        elif os.path.isdir(item):
            for root_dir, cur_dir, files in os.walk(item):
                count += len(files)
    return count


class WorkerSignals(QObject):
    """
    defines the signals available from a running worker thread.
    signals:
        - error: tuple (exctype, value, traceback.format_exc() )
        - progress: int (processed file count)
        - memory_count: int (memory size of backed up file (bytes))
        - status: string (filename currently backing up, or skipping)
        - finished: No data
        - new_thread: object (QRunnable worker to enqueue)
    """
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int)
    memory_count = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    new_thread = pyqtSignal(object)


class WorkerKilledException(Exception):
    pass


class BackupSettings:

    def __init__(self, included_paths: list,
                 excluded_paths: list,
                 excluded_file_extensions: list,
                 root_backup_directory: str):
        self.included_paths = included_paths
        self.excluded_paths = excluded_paths
        self.excluded_file_extensions = excluded_file_extensions
        self.root_backup_directory = root_backup_directory


class BackupLogEntry:

    def __init__(self, date_stamp: str, time_stamp: str,
                 file_count: int,
                 total_memory: str,
                 included: list,
                 excluded: list):
        self.backup_date = date_stamp
        self.backup_time = time_stamp
        self.total_count = file_count
        self.total_memory = total_memory
        self.included_in_backup = included
        self.excluded_from_backup = excluded


class BackupSelection(QRunnable):

    def __init__(self, source: Path,
                 destination: Path,
                 thread_pool: QObject,
                 ignore_files: list,
                 ignore_extensions: list,
                 root_input: bool):
        """
        Backup selected file/directory
        :param source: file or directory to backup
        :param destination: output directory
        :param thread_pool: main thread pool
        :param ignore_files: list of files to ignore
        :param ignore_extensions: list of extensions to ignore
        :param root_input: True if the file or directory is one listed by the user, if False treated as subdir/contents
        """
        super(BackupSelection, self).__init__()
        self.src = source
        self.dst = destination
        self.worker_signals = WorkerSignals()
        self.root = root_input
        self.ignore_files = ignore_files
        self.ignore_extensions = ignore_extensions
        self.thread_pool = thread_pool
        self.is_killed = False

    def run(self):
        try:
            if os.path.isdir(self.src):

                if not os.path.isdir(self.dst):
                    # make the destination directory if it does not exist
                    os.makedirs(self.dst, exist_ok=True)

                if self.root:
                    # input is from the GUI list of inputs,
                    # it is a parent directory inside the root backup directory
                    parent_dir = self.src.name
                    try:
                        os.makedirs(os.path.join(self.dst, parent_dir), exist_ok=True)
                    except OSError as os_error:
                        self.emit_error(
                            (os_error, traceback.format_exc(),
                             f'error creating directory {os.path.join(self.dst, parent_dir)}',
                             'Error backing up files. See error log for more information'))
                        return
                    self.dst = os.path.join(self.dst, parent_dir)

                # get contents of input directory
                names = os.listdir(self.src)
                for name in names:
                    if self.is_killed:
                        raise WorkerKilledException

                    ignore_this = False
                    src_name = Path(os.path.join(self.src, str(name)))
                    dst_name = Path(os.path.join(self.dst, str(name)))

                    if src_name in self.ignore_files:
                        # ignore the file or directory
                        self.emit_progress(1)
                        self.emit_status(src_name.name)
                        continue
                    if os.path.isdir(src_name):
                        # recursion
                        worker = BackupSelection(source=src_name,
                                                 destination=dst_name,
                                                 thread_pool=self.thread_pool,
                                                 ignore_files=self.ignore_files,
                                                 ignore_extensions=self.ignore_extensions,
                                                 root_input=False)

                        self.worker_signals.new_thread.emit(worker)
                    elif os.path.isfile(src_name):
                        for extension in self.ignore_extensions:
                            if name.endswith(extension):
                                # ignore file if in the extension type ignore list
                                ignore_this = True
                                continue
                        if ignore_this:
                            self.emit_progress(1)
                            self.emit_status(f'ignoring extension: {src_name.name}...')
                            continue
                        file_size = os.path.getsize(src_name)
                        if os.path.isfile(dst_name):
                            # file exists in backup directory
                            if check_existing_file(src_name, dst_name):
                                self.emit_status(f'{src_name.name}...')
                                # input file is newer than last backup, overwrite
                                try:
                                    shutil.copy2(src_name, dst_name)
                                except OSError as os_error:
                                    self.emit_error(
                                        (os_error, traceback.format_exc(),
                                         f'error overwriting file {src_name}',
                                         'Error backing up files. See error log for more information'))
                                else:
                                    self.emit_memory_count(file_size)
                            self.emit_progress(1)
                        else:
                            self.emit_status(f'{src_name.name}...')
                            # file does not exist in backup directory, write
                            try:
                                shutil.copy2(src_name, dst_name)
                            except OSError as os_error:
                                self.emit_error(
                                    (os_error, traceback.format_exc(),
                                     f'error copying new file {src_name}',
                                     'Error backing up files. See error log for more information'))
                            else:
                                self.emit_progress(1)
                                self.emit_memory_count(file_size)

            elif os.path.isfile(self.src):
                for extension in self.ignore_extensions:
                    if self.src.name.endswith(extension):
                        # ignore file if in the extension type ignore list
                        self.emit_status(f'{self.src.name}...')
                        self.emit_progress(1)
                        return
                file_size = os.path.getsize(self.src)
                if os.path.isfile(os.path.join(self.dst, self.src.name)):
                    # file exists in backup directory
                    if check_existing_file(self.src, Path(os.path.join(self.dst, self.src.name))):
                        self.emit_status(f'{self.src.name}...')
                        # input file is newer than last backup, overwrite
                        try:
                            shutil.copy2(self.src, self.dst)
                        except OSError as os_error:
                            self.emit_error((os_error, traceback.format_exc(),
                                             f'error overwriting file {self.src}',
                                             'Error backing up files. See error log for more information'))
                        else:
                            self.emit_memory_count(file_size)
                    self.emit_progress(1)
                else:
                    self.emit_status(f'{self.src.name}...')
                    # file does not exist in backup directory, write
                    try:
                        shutil.copy2(self.src, self.dst)
                    except OSError as os_error:
                        self.emit_error((os_error, traceback.format_exc(),
                                         f'error copying new file {self.src}',
                                         'Error backing up files. See error log for more information'))
                    else:
                        self.emit_progress(1)
                        self.emit_memory_count(file_size)

        except WorkerKilledException:
            self.emit_status('worker killed')
        except Exception as error:
            self.emit_error((error, traceback.format_exc(),
                             f'error running backup for {self.src}',
                            'Error backing up files. See error log for more information.'))
        finally:
            self.worker_signals.finished.emit()

    def emit_progress(self, count):
        self.worker_signals.progress.emit(count)

    def emit_memory_count(self, memory_value):
        self.worker_signals.memory_count.emit(memory_value)

    def emit_status(self, message):
        self.worker_signals.status.emit(message)

    def emit_error(self, details):
        self.worker_signals.error.emit(details)

    def kill(self):
        self.is_killed = True
