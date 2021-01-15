# -*- coding: utf-8 -*-
'''
Created on Fri Jan  1 17:31:40 2021

@author: prah_ch
'''
import datetime
import shutil
import os
import re
from PIL import Image, ExifTags

DATE_FMT = '%Y:%m:%d %H:%M:%S'
IMG_REGEX = r'.*\.(jpe?g|png|raw)$'
MEDIA_REGEX = r'.*\.(mp4|mov|mkv|jpe?g|png|raw)$'


# %% Sorter Class
class Sorter:
    def __init__(self):
        self.only_copy = True
        self.overwrite = True
        self.fld_fmt = '%Y_%m'
        self.progress = {}
        self.ignore_paths = []

    def setStatus(self, status):
        print('\nSTATUS: ' + status)

    def setPercentage(self, percentage):
        print(f'\rPERCENTAGE: {percentage}', end='')

    # %% Function to get date from an image
    def _get_date(self, path):
        '''
        Get the date of an image or video

        Parameters
        ----------
        path : str
            Path of the image or video.

        Returns
        -------
        date : datetime.datetime
            The creation time of the media file.

        '''
        assert os.path.exists(path), f'{path} does not exists'
        date = None
        try:
            if re.match(IMG_REGEX, path, re.I):
                img = Image.open(path)
                exif = {ExifTags.TAGS[t]: v for t,
                        v in img._getexif().items() if t in ExifTags.TAGS}
                date = datetime.datetime.strptime(exif['DateTime'], DATE_FMT)

        finally:
            if not re.match(MEDIA_REGEX, path, re.I):
                print(f'{path} is not supported')
            elif not date:
                ctime = os.stat(path).st_ctime
                date = datetime.datetime.fromtimestamp(ctime)

            return date

    # %% Function to get all images in all subfolders of a directory

    def get_all_files(self, path):
        '''
        Search path recursively for videos and images

        Parameters
        ----------
        path : str
            Path to search for media.
        ignore_dirs : list, optional
            List of directories to ignore. The default is [].

        Returns
        -------
        images : list
            List of absolute media paths.

        '''
        dir_content = os.listdir(path)
        images = []
        for file in dir_content:
            abs_file = os.path.abspath(os.path.join(path, file))
            if os.path.isdir(abs_file) and abs_file not in self.ignore_paths:
                images.extend(self.get_all_files(abs_file))
                # TBD: Set recursion limit
            elif re.match(MEDIA_REGEX, abs_file, re.I):
                images.append(abs_file)
        return images

    # %% Function to sort a list from get_all_media to a dictionary

    def sort_media_list(self, media_list):
        '''
        Sort media list created using get_all_media

        Parameters
        ----------
        media_list : list
            List of absolute media paths.
        folder_format : str, optional
            datetime.datetime.strftime format strig for
            the folder names. The default is '%Y_%m'.

        Returns
        -------
        out : dict
            Sorted dictionary.

        '''
        out = {}
        for image in media_list:
            date = self._get_date(image)
            if not date:
                continue
            date_str = date.strftime(self.fld_fmt)
            if date_str not in out.keys():
                out[date_str] = []
            out[date_str].append(image)
        return out

    # %% Function to prevent duplicate names

    def un_duplicate(self, name, used_names):
        '''
        Un-Duplicate a filename

        Parameters
        ----------
        name : str
            Absolute path of the file.
        used_names : list
            List of files with same base-name.

        Returns
        -------
        str
            New absolute path with un-duplicated name.

        '''
        base_name = os.path.basename(name)
        cnt = 0
        for used in used_names:
            if re.match(r'.*_?' + base_name, os.path.basename(used)):
                cnt += 1
        un_dup_name = f'{cnt}_{base_name}'
        return os.path.join(os.path.dirname(name), un_dup_name)

    # %% Function to copy/move sorted images

    def sort(self, src, dst):
        '''
        Sort a directory

        Parameters
        ----------
        src : str
            Source directory to sort.
        dst : str
            Destination directory for sorted media.

        Returns
        -------
        None.

        '''

        assert src != dst, f'{src} and {dst} are the same'
        if src in dst:  # Check if dst is a subdir of src
            self.ignore_paths.append(os.path.abspath(dst))

        # %% Get media list
        self.setStatus('Getting media list')
        im_list = self.get_all_files(src)

        # %% Sort media list
        self.setStatus('Sorting media by date')
        sorted_dict = self.sort_media_list(im_list)

        im_count = len(im_list)
        im_processed = 0
        self.failed = []
        self.setStatus('Writing changes to disc')
        # %% Create folders if they don't exist
        for folder in sorted_dict:
            abs_path = os.path.join(dst, folder)
            moved = []
            if not os.path.exists(abs_path):
                os.mkdir(abs_path)
            # %% Move/copy images to folder
            for old_path in sorted_dict[folder]:
                new_path = os.path.join(
                    dst, folder, os.path.basename(old_path))
                if new_path in moved:
                    new_path = self.un_duplicate(new_path, moved)
                moved.append(new_path)
                try:
                    if not self.overwrite and os.path.exists(new_path):
                        pass  # Count up and do nothing
                    elif self.only_copy:
                        shutil.copy2(old_path, new_path)
                        # Use copy2 in attempt to copy metadata
                    else:
                        os.rename(old_path, new_path)
                except OSError:
                    self.failed.append(old_path)
                im_processed += 1

                self.setPercentage(im_processed / im_count * 100)

        if self.failed:
            print(f'Failed to copy {len(self.failed)} images')
        self.setStatus('Done')


# %% Run this if programm is called directly
if __name__ == '__main__':
    srt = Sorter()
    srt.sort('/home/maxi/Pictures/', '/home/maxi/Pictures/sorted')
