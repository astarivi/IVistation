import zlib


def calculate_crc32(file_path):
    with open(file_path, 'rb') as rom_file:
        # Read the entire ROM
        rom_data = rom_file.read()

        # Exclude the header (first 16 bytes)
        rom_data_without_header = rom_data[16:]

        # Calculate CRC32
        crc32_value = zlib.crc32(rom_data_without_header) & 0xFFFFFFFF

        if rom_data[:3] == b'NES':
            print("Header found")

        return crc32_value


rom_path = 'rom.nes'

crc32_result = calculate_crc32(rom_path)
print("{:08x}".format(crc32_result).lower())
