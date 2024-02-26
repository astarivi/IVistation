"""
Credits to:
frehov (Fredr1kh#3002)
Rocky5 - XBMC4Gamers
"""

import os
import shutil
import traceback

from io import BytesIO
from struct import unpack
from binascii import unhexlify
from os.path import basename, getsize, join
from xbmc import log, LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, translatePath
from ivistation.xbe import XBE

ATTACH_XBE_PATH = translatePath("Special://root/ivistation/data/attach.xbe")


def get_xiso_info(xiso_file):
    iso_info = {}

    with open(xiso_file, 'rb') as iso:
        # check for validity
        iso.seek(0x10000)
        if iso.read(0x14).decode("ascii", "ignore") == 'MICROSOFT*XBOX*MEDIA':  # read tailend of header
            iso_info['sector_size'] = 0x800

            # read the directory table
            iso_info['root_dir_sector'] = unpack('I', iso.read(4))[0]  # dtable
            iso_info['root_dir_size'] = unpack('I', iso.read(4))[0]
        else:
            print("header tail mismatch -- possible corruption?")
            print("this doesn't appear to be an xbox iso image")

    return iso_info


def extract_files(iso_files, iso_info, game_iso_folder, xbe_partitions=8, files=None):
    if files is None:
        files = {"default.xbe", "game.xbe"}

    iso_size = getsize(iso_files[0])
    isos = [open(x, 'rb') for x in iso_files]

    try:
        iso = isos[0]
        with BytesIO() as root_sector_buffer:
            # seek to root sector
            iso.seek(iso_info['root_dir_sector'] * iso_info['sector_size'])

            # read the root sector into a bytes object
            root_sector_buffer.write(iso.read(iso_info['root_dir_size']))
            root_sector_buffer.seek(0)

            # case-insensitive search of root sector for default.xbe
            for i in range(0, iso_info['root_dir_size']):
                root_sector_buffer.seek(i)
                # No idea why we're reading 1 byte here
                # astarivi: I tested, and it's the same as i + 1
                root_sector_buffer.read(1)

                try:
                    filename_length = unpack('<' + 'B' * 1,  root_sector_buffer.read(1))[0]  # filename length in directory table
                except:
                    continue

                for filename in files:
                    if filename_length != len(filename) or root_sector_buffer.read(len(filename)).decode("ascii", "ignore").lower() != filename:
                        continue

                    root_sector_buffer.seek(i - 8)
                    file_sector = unpack('I', root_sector_buffer.read(4))[0]
                    file_size = unpack('I', root_sector_buffer.read(4))[0]
                    file_offset = file_sector * iso_info['sector_size']

                    # dump the xbe in parts for huge xbe files.
                    # adding dangling size if xbe is not cleanly divisble by xbe_partitions
                    dangling_partition_size = file_size % xbe_partitions
                    file_partition_size = file_size / xbe_partitions

                    # File could be located in part 2 of the iso.
                    if file_offset > iso_size:
                        log(str.format("{} is not located in '{}', skipping to '{}', file_sector {}, file_offset {}", filename, basename(iso.name), basename(iso_files[1]), file_sector, file_offset), LOGDEBUG)
                        file_offset = file_offset - iso_size  # Set the correct offset for second iso(?).
                        iso = isos[1]  # switch file handle

                    iso.seek(file_offset)  # Move to the correct file

                    log(str.format("{} size is {} bytes, partition size is {} bytes, dangling size is {} bytes", filename, file_size, file_partition_size, dangling_partition_size), LOGDEBUG)
                    # write binary, truncating file before writing.
                    with open(join(game_iso_folder, filename), "wb") as xbe:
                        for partition in range(0, xbe_partitions):
                            xbe.write(iso.read(file_partition_size))

                        # write the remainder of the xbe
                        if dangling_partition_size > 0:
                            xbe.write(iso.read(dangling_partition_size))

                    log(str.format("Done extracting '{}' from '{}', size is {} bytes", filename, basename(iso.name), getsize(join(game_iso_folder, filename))), LOGDEBUG)
                iso = isos[0]  # Reset filehandle back to file number 1.
    finally:
        for iso in isos:
            iso.close()


# 0000 2800 > 0028 0000 how we want it
def swap_order(data, wsz=16, gsz=2):
    return "".join(["".join([m[i:i+gsz] for i in range(wsz-gsz, -gsz, -gsz)]) for m in [data[i:i+wsz] for i in range(0, len(data), wsz)]])
    # https://stackoverflow.com/posts/36744477/revisions


def create_attach_xbe(game_iso_folder):
    original_xbe = XBE(join(game_iso_folder, 'default.xbe'), keep_raw_cert=True)
    # Copy attach.xbe from data to the iso folder
    shutil.copy(ATTACH_XBE_PATH, join(game_iso_folder, 'attach.xbe'))

    # ATTACH XBE FILE
    with open(join(game_iso_folder, 'attach.xbe'), 'r+b') as attach_xbe:
        attach_xbe.seek(260, 0)  # move to base address
        base = attach_xbe.read(4)

        attach_xbe.seek(280, 0)  # move to cert address
        cert = attach_xbe.read(4)

        # get the location of the cert
        certAddress = unpack("i", cert)[0]  # init32 values
        baseAddress = unpack("i", base)[0]  # init32 values

        attach_xbe.seek((certAddress - baseAddress), 0)  # move to the titleid
        attach_xbe.write(original_xbe.raw_cert)

        attach_xbe.seek((certAddress - baseAddress + 172), 0)  # move to the version
        attach_xbe.write(unhexlify('01000080'))

        # Transfer TitleImage, if found
        try:
            image_sector = original_xbe.get_xbx_sector()
        except ValueError:
            image_sector = None

        if image_sector is not None:
            with open(original_xbe.path, 'rb') as og_xbe:
                # Move attach.xbe to xpr0 virtual address
                attach_xbe.seek(1060)
                image_address = unpack("i", attach_xbe.read(4))[0]

                base_size = (image_sector.dwSizeofRaw + image_address)  # <-- is the data size before the XPR0 required
                base_sizehex = hex(base_size)[2:-1].zfill(8)

                # Write size values to attach.xbe
                attach_xbe.seek(268, 0)  # move to base file size
                # Write the size of the base image
                attach_xbe.write(unhexlify(swap_order(base_sizehex)))

                xbx_sizehex = hex(image_sector.dwSizeofRaw)[2:-1].zfill(8)

                attach_xbe.seek(1056, 0)  # move to xpr0 virtual size address
                attach_xbe.write(unhexlify(swap_order(xbx_sizehex)))

                attach_xbe.seek(1064, 0)  # move to xpr0 raw size address
                attach_xbe.write(unhexlify(swap_order(xbx_sizehex)))

                # Move default.xbe to title image raw address
                og_xbe.seek(image_sector.dwRawAddr)
                # Move attach.xbe to the title image address xpr0
                attach_xbe.seek(image_address)

                remaining_bytes = image_sector.dwSizeofRaw

                # Be extra careful with memory management
                while remaining_bytes > 0:
                    chunk_size = min(4096, remaining_bytes)

                    chunk = og_xbe.read(chunk_size)

                    if not chunk:
                        break

                    attach_xbe.write(chunk)

                    remaining_bytes -= chunk_size

    default_xbe = join(game_iso_folder, "default.xbe")
    os.remove(default_xbe)
    os.rename(join(game_iso_folder, "attach.xbe"), default_xbe)


def process_iso_name(file_name):
    iso_full_name = file_name[:-4].replace('_1', '').replace('_2', '').replace('.1', '').replace('.2', '')
    iso_name = iso_full_name.split('(', 1)[0]
    # truncate the name to 42 characters, reason is the .iso
    iso_folder_name = iso_name[:36] if len(iso_name) > 36 else iso_name

    return iso_full_name


def process_iso(iso_files, game_iso_folder):
    file_name = basename(iso_files[0])

    iso_info = get_xiso_info(iso_files[0])  # check that iso is an xbox game and extract some details
    if not iso_info:  # doesn't work, if no xbe files is found inside the xiso. (yeah I was testing and forgot the xbe lol)
        log(str.format("ISO info could not be obtained, skipping '{}'", file_name), LOGDEBUG)
        return None

    if not os.path.isdir(game_iso_folder):
        os.mkdir(game_iso_folder)  # make a new folder for the current game

    extract_files(iso_files, iso_info, game_iso_folder)  # find and extract default.xbe/game.xbe from the iso

    # If we found a game.xbe, use that instead
    default_xbe = join(game_iso_folder, 'default.xbe')
    game_xbe = join(game_iso_folder, 'game.xbe')

    if os.path.isfile(game_xbe):
        os.remove(default_xbe)
        os.rename(game_xbe, default_xbe)

    print(str.format("Extracting TitleImage.xbx for '{}'", game_iso_folder))
    try:
        # Patch the title+id into attach.xbe...
        create_attach_xbe(game_iso_folder)
        return join(game_iso_folder, "default.xbe")
    except:
        try:
            os.remove(join(game_iso_folder, "default.xbe"))
            os.remove(join(game_iso_folder, "attach.xbe"))
        except:
            pass
        log("Not a valid XISO?", LOGERROR)
        log("Could not prepare the attach.xbe with extracted values from default.xbe", LOGERROR)
        traceback.print_exc()
        return None
