import sys
import os
import pathlib
import time
import datetime as dt

sys.path.insert(0, f"{pathlib.Path(__file__).parent.resolve()}")

# NOTE: We have removed the top-level import from crushe to avoid circular import errors.

class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

def progress_bar_str(done, total):
    percent = round(done / total * 100, 2)
    strin = "░░░░░░░░░░"
    strin = list(strin)
    for i in range(round(percent) // 10):
        strin[i] = "█"
    strin = "".join(strin)
    final = f"Percent: {percent}%\n{human_readable_size(done)}/{human_readable_size(total)}\n{strin}"
    return final

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

async def fast_download(client, msg, reply=None, download_folder=None, progress_bar_function=progress_bar_str):
    # Import download_file here to break the circular dependency.
    from crushe import download_file

    timer = Timer()
    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"Downloading...\n{data}")
    file = msg.document
    filename = msg.file.name
    dir = "downloads/"
    try:
        os.mkdir("downloads/")
    except Exception:
        pass
    if not filename:
        filename = "video.mp4"
    if download_folder is None:
        download_location = dir + filename
    else:
        download_location = download_folder + filename
    with open(download_location, "wb") as f:
        if reply is not None:
            await download_file(
                client=client,
                location=file,
                out=f,
                progress_callback=progress_bar
            )
        else:
            await download_file(
                client=client,
                location=file,
                out=f,
            )
    return download_location

async def fast_upload(client, file_location, reply=None, name=None, progress_bar_function=progress_bar_str):
    # Import upload_file here to break the circular dependency.
    from crushe import upload_file

    timer = Timer()
    if name is None:
        name = file_location.split("/")[-1]
    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"{data}")
    if reply is not None:
        with open(file_location, "rb") as f:
            the_file = await upload_file(
                client=client,
                file=f,
                name=name,
                progress_callback=progress_bar
            )
    else:
        with open(file_location, "rb") as f:
            the_file = await upload_file(
                client=client,
                file=f,
                name=name,
            )
        return the_file

