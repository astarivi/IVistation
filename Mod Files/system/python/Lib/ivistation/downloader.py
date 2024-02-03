import time
import urllib2

from contextlib import closing


def download_file(url, local_path, timeout=20, chunk_size=8192, progress_every=32):
    """
    Download a file from the provided URL, and saves it to the local_path.

    Args:
        url: Remote URL to download from, string
        local_path: Local path to save the file to. Only full paths allowed.
        timeout: Time to wait for the connection to succeed, in seconds
        chunk_size: Size of the chunks to download at a time, in bytes
        progress_every: Every how many downloaded chunks to yield progress
    Returns:
        Yields progress from 0 to 100 as an int, and human-readable download
        speed as a string
    """
    repetitions = 0
    start_time = time.time()

    with closing(urllib2.urlopen(url, timeout=timeout)) as response, open(local_path, 'wb') as output_file:
        total_size = float(response.headers['Content-Length'])
        downloaded = 0

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            output_file.write(chunk)

            downloaded += len(chunk)
            repetitions += 1

            if repetitions >= progress_every:
                repetitions = 0
                # Calculate speed
                elapsed_time = time.time() - start_time
                speed = downloaded / (elapsed_time * 1024)

                if speed >= 1024:
                    speed = "{:.2f} MB/s".format(speed / 1024)
                else:
                    speed = "{:.2f} KB/s".format(speed)

                yield int((downloaded / total_size) * 100), speed

        yield 100, "0 KB/s"


def turbo_download(url, save_to, timeout=8, chunk_size=8192):
    """
    Downloads a file as fast as possible, disregarding progress.
    Used to download small files, or many sequential files.
    """

    with closing(urllib2.urlopen(url, timeout=timeout)) as response, open(save_to, 'wb') as output_file:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            output_file.write(chunk)


def memory_download(url, timeout=8):
    """
    Downloads a file asap, and returns the obtained contents.
    Used to download very small text files for further parsing,
    such as JSON files.
    """
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0'
    }

    request = urllib2.Request(url, headers=headers)

    with closing(urllib2.urlopen(request, timeout=timeout)) as response:
        return response.read()
