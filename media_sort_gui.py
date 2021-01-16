# -*- coding: utf-8 -*-
'''
Created on Sat Jan  2 13:11:58 2021

@author: prah_ch
'''
import sys
import os
import media_sort
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, \
    QLabel, QLineEdit, QFileDialog, QCheckBox, QProgressBar, QTextBrowser, \
    QMainWindow
from PyQt5.QtCore import QUrl, QSettings, QThread, pyqtSlot

Sorter = media_sort.Sorter()
SCRIPT_FOLDER = os.path.dirname(__file__)


# %% Define the Main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)
        self._settings = QSettings('media_sorter', 'last-setings')
        print(f'Using config file {self._settings.fileName()}')

        # %% Source and destination
        self._src_dir = QLineEdit()
        self._dst_dir = QLineEdit()
        layout.addWidget(QLabel('Source Directory:'), 0, 0)
        layout.addWidget(QLabel('Destination'), 1, 0)
        layout.addWidget(self._src_dir, 0, 1)
        layout.addWidget(self._dst_dir, 1, 1)

        # %% Browse path buttons
        self._src_browse = QPushButton('Browse')
        self._src_browse.clicked.connect(
            lambda: self._get_dir(lambda x: self._src_dir.setText(x)))
        self._dst_browse = QPushButton('Browse')
        self._dst_browse.clicked.connect(
            lambda: self._get_dir(lambda x: self._dst_dir.setText(x)))
        layout.addWidget(self._src_browse, 0, 2)
        layout.addWidget(self._dst_browse, 1, 2)

        # %% Folder output format
        layout.addWidget(QLabel('Output folder format'), 2, 0)
        self._fld_fmt = QLineEdit()
        HLink = 'https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes'
        help_btn = QLabel(f'<a href="{HLink}">Help</a>')
        help_btn.linkActivated.connect(self._open_link)
        layout.addWidget(self._fld_fmt, 2, 1)
        layout.addWidget(help_btn, 2, 2)

        # %% Options
        self._overwrite = QCheckBox('Overwrite')
        self._only_copy = QCheckBox('Only copy images')
        layout.addWidget(self._overwrite, 3, 0)
        layout.addWidget(self._only_copy, 3, 1)

        # %% The start button
        self._start = QPushButton('Start')
        self._start.clicked.connect(self._start_sort)
        layout.addWidget(self._start, 3, 2)

        # %% The progress bar
        self._progress = QProgressBar()
        self._progress.setValue(0)
        layout.addWidget(self._progress, 4, 0, 1, 3)

        # %% status, reports
        self._status = QLabel('Doing Nothing...')
        self._reports = QPushButton('Reports')
        self._reports.setEnabled(False)
        self._reports.clicked.connect(self._open_reports)
        layout.addWidget(self._status, 5, 0, 1, 2)
        layout.addWidget(self._reports, 5, 2)


        # %% Set window Title
        self.setWindowTitle('Media sorter')

        # %% Set the icon
        self.setWindowIcon(QIcon(os.path.join(SCRIPT_FOLDER, 'icon.svg')))
        # %% Restore last used values
        self._overwrite.setChecked(self._settings.value('overwrite',
                                                        False, type=bool))
        self._only_copy.setChecked(self._settings.value('onlyCopy',
                                                        True, type=bool))
        self._fld_fmt.setText(self._settings.value('fldFmt', '%Y_%m'))

    def _get_dir(self, set_fn):
        directory = str(QFileDialog.getExistingDirectory())
        set_fn(directory)

    @pyqtSlot()
    def _start_sort(self):
        self._start.setEnabled(False)
        self._reports.setEnabled(False)
        self._progress.setValue(0)
        Sorter.overwrite = self._overwrite.isChecked()
        Sorter.only_copy = self._only_copy.isChecked()
        Sorter.fld_fmt = self._fld_fmt.text()
        Sorter.setPercentage = lambda x: self._progress.setValue(int(x))
        Sorter.setStatus = lambda x: self._status.setText(str(x))
        Sorter.src = self._src_dir.text()
        Sorter.dst = self._dst_dir.text()
        thread = SortThread(self)
        thread.finished.connect(self._after_sort)
        thread.start()

    @pyqtSlot()
    def _after_sort(self):
        self._settings.setValue('overwrite', Sorter.overwrite)
        self._settings.setValue('onlyCopy', Sorter.only_copy)
        self._settings.setValue('fldFmt', Sorter.fld_fmt)
        self._start.setEnabled(True)
        self._reports.setEnabled(True)

    def _open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))

    def _open_reports(self):
        window = QMainWindow(self)
        reps = Reports()
        window.setCentralWidget(reps)
        window.show()


class SortThread(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)

    def run(self):
        Sorter.sort(Sorter.src, Sorter.dst)


class Reports(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('Failed Media'), 0, 0)
        text = QTextBrowser()
        layout.addWidget(text, 1, 0)
        report_failed = '\n'.join(Sorter.failed)
        text.setText(report_failed)



# %% Run this if program is executed directly
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
