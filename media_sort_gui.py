# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 13:11:58 2021

@author: prah_ch
"""
import sys
import media_sort
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, \
    QLabel, QLineEdit, QFileDialog, QCheckBox, QProgressBar
from PyQt5.QtCore import QUrl, QSettings


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
        # %% Set window Title
        self.setWindowTitle('Media sorter')
        # %% Restore last used values
        self._src_dir.setText(self._settings.value('src', ''))
        self._dst_dir.setText(self._settings.value('dst', ''))
        self._overwrite.setChecked(self._settings.value('overwrite', False, type=bool))
        self._only_copy.setChecked(self._settings.value('onlyCopy', True, type=bool))
        self._fld_fmt.setText(self._settings.value('fldFmt', '%Y_%m'))

    def _get_dir(self, set_fn):
        directory = str(QFileDialog.getExistingDirectory())
        set_fn(directory)

    def _start_sort(self):
        self._progress.setValue(0)
        src = self._src_dir.text()
        dst = self._dst_dir.text()
        overwrite = self._overwrite.isChecked()
        only_copy = self._only_copy.isChecked()
        fld_fmt = self._fld_fmt.text()
        media_sort.sort_dir(src, dst,
                            overwrite=overwrite,
                            only_copy=only_copy,
                            set_prc=lambda x: self._progress.setValue(int(x)),
                            fld_fmt=fld_fmt)
        # %% Write values to configuration
        self._settings.setValue('src', src)
        self._settings.setValue('dst', dst)
        self._settings.setValue('overwrite', overwrite)
        self._settings.setValue('onlyCopy', only_copy)
        self._settings.setValue('fldFmt', fld_fmt)

    def _open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))


# %% Run this if programm is executed directly
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
