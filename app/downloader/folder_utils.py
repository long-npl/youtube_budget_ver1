import os
import logging
from time import sleep
import shutil

logger = logging.getLogger(__name__)


def get_tmp_files(folder):
    return [f for f in os.listdir(folder) if f.endswith(".crdownload") or f.endswith(".tmp")]


class DownloadTimeOut(Exception):
    pass


class InvalidNumberOfDownloadedFile(Exception):
    pass


class DownloadedFileNameNotMatch(Exception):
    pass


def download_and_move(dl_folder, output_folder, file_name, file_check=None, ext='.csv', wait_time=180):
    sleep(1)
    download_seconds = 0
    got_flag = False
    while True:
        tmp_files = get_tmp_files(dl_folder)
        got_flag = got_flag or len([f for f in os.listdir(dl_folder)]) > 0
        sleep(1)
        download_seconds += 1
        if (len(tmp_files) == 0 and got_flag) or download_seconds > wait_time:
            break

    if len(tmp_files) > 0:
        raise DownloadTimeOut(f"download timeout, found {len(tmp_files)} tmp files")

    if ext is None:
        src_file = [f for f in os.listdir(dl_folder) if not f.endswith(".tmp") and os.path.isfile(os.path.join(dl_folder, f))]
    else:
        src_file = [f for f in os.listdir(dl_folder) if f.endswith(ext)]

    if len(src_file) != 1:
        raise InvalidNumberOfDownloadedFile(f"expected 1 file, but got: {len(src_file)}")

    src_file = src_file[0]
    if file_check:
        if "*" in file_check:
            if file_check.replace("*", "") not in src_file:
                raise DownloadedFileNameNotMatch(f"expected: {file_check}, but got: {src_file}")
        else:
            if src_file != file_check:
                raise DownloadedFileNameNotMatch(f"expected: {file_check}, but got: {src_file}")

    # move to vnd folder
    os.makedirs(output_folder, exist_ok=True)
    shutil.move(os.path.join(dl_folder, src_file), os.path.join(output_folder, file_name))

    return True
