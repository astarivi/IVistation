# Credits to LoveMHz and Rocky5

import struct


class XBE_HEADER():
    def __init__(self, data):
        XOR_EP_DEBUG = 0x94859D4B  # Entry Point (Debug)
        XOR_EP_RETAIL = 0xA8FC57AB  # Entry Point (Retail)
        XOR_KT_DEBUG = 0xEFB1F152  # Kernel Thunk (Debug)
        XOR_KT_RETAIL = 0x5B6D40B6  # Kernel Thunk (Retail)

        self.dwMagic = struct.unpack('4s', data[0:4])[0]  # Magic number [should be "XBEH"]
        self.pbDigitalSignature = struct.unpack('256B', data[4:260])  # Digital signature
        self.dwBaseAddr = struct.unpack('I', data[260:264])[0]  # Base address
        self.dwSizeofHeaders = struct.unpack('I', data[264:268])[0]  # Size of headers
        self.dwSizeofImage = struct.unpack('I', data[268:272])[0]  # Size of image
        self.dwSizeofImageHeader = struct.unpack('I', data[272:276])[0]  # Size of image header
        self.dwTimeDate = struct.unpack('I', data[276:280])[0]  # Timedate stamp
        self.dwCertificateAddr = struct.unpack('I', data[280:284])[0]  # Certificate address
        self.dwSections = struct.unpack('I', data[284:288])[0]  # Number of sections
        self.dwSectionHeadersAddr = struct.unpack('I', data[288:292])[0]  # Section headers address

        # Struct init_flags
        self.dwInitFlags = struct.unpack('I', data[292:296])[0]  # Mount utility drive flag
        self.init_flags_mount_utility_drive = None  # Mount utility drive flag
        self.init_flags_format_utility_drive = None  # Format utility drive flag
        self.init_flags_limit_64mb = None  # Limit development kit run time memory to 64mb flag
        self.init_flags_dont_setup_harddisk = None  # Don't setup hard disk flag
        self.init_flags_unused = None  # Unused (or unknown)
        self.init_flags_unused_b1 = None  # Unused (or unknown)
        self.init_flags_unused_b2 = None  # Unused (or unknown)
        self.init_flags_unused_b3 = None  # Unused (or unknown)

        self.dwEntryAddr = struct.unpack('I', data[296:300])[0]  # Entry point address
        self.dwTLSAddr = struct.unpack('I', data[300:304])[0]  # TLS directory address
        self.dwPeStackCommit = struct.unpack('I', data[304:308])[0]  # Size of stack commit
        self.dwPeHeapReserve = struct.unpack('I', data[308:312])[0]  # Size of heap reserve
        self.dwPeHeapCommit = struct.unpack('I', data[312:316])[0]  # Size of heap commit
        self.dwPeBaseAddr = struct.unpack('I', data[316:320])[0]  # Original base address
        self.dwPeSizeofImage = struct.unpack('I', data[320:324])[0]  # Size of original image
        self.dwPeChecksum = struct.unpack('I', data[324:328])[0]  # Original checksum
        self.dwPeTimeDate = struct.unpack('I', data[328:332])[0]  # Original timedate stamp
        self.dwDebugPathnameAddr = struct.unpack('I', data[332:336])[0]  # Debug pathname address
        self.dwDebugFilenameAddr = struct.unpack('I', data[336:340])[0]  # Debug filename address
        self.dwDebugUnicodeFilenameAddr = struct.unpack('I', data[340:344])[0]  # Debug unicode filename address
        self.dwKernelImageThunkAddr = struct.unpack('I', data[344:348])[0]  # Kernel image thunk address
        self.dwNonKernelImportDirAddr = struct.unpack('I', data[348:352])[0]  # Non kernel import directory address
        self.dwLibraryVersions = struct.unpack('I', data[352:356])[0]  # Number of library versions
        self.dwLibraryVersionsAddr = struct.unpack('I', data[356:360])[0]  # Library versions address
        self.dwKernelLibraryVersionAddr = struct.unpack('I', data[360:364])[0]  # Kernel library version address
        self.dwXAPILibraryVersionAddr = struct.unpack('I', data[364:368])[0]  # XAPI library version address
        self.dwLogoBitmapAddr = struct.unpack('I', data[368:372])[0]  # Logo bitmap address
        self.dwSizeofLogoBitmap = struct.unpack('I', data[372:376])[0]  # Logo bitmap size

        self.dwEntryAddr_f = self.dwEntryAddr ^ XOR_EP_RETAIL  # Entry point address


class XBE_CERT():
    def __init__(self, data):
        self.dwSize = self._unpack(data, 'I', 0x0004, 0x0000)[0]
        self.dwTimeDate = self._unpack(data, 'I', 0x0004, 0x0004)[0]
        # Title ID
        intermediate_title_id = self._unpack(data, 'L', 0x0004, 0x0008)[0]
        self.dwTitleId = str(hex(intermediate_title_id)[2:10]).upper().zfill(8)

        self.wszTitleName = self._unpack(data, "80s", 0x0050, 0x000C)[0]

        self.dwAlternateTitleId = self._unpack(data, "64B", 0x0040, 0x005C)
        self.dwAllowedMedia = self._unpack(data, "I", 0x0004, 0x009C)[0]
        self.dwGameRegion = self._unpack(data, "I", 0x0004, 0x00A0)[0]
        self.dwGameRatings = self._unpack(data, "I", 0x0004, 0x00A4)[0]
        self.dwDiskNumber = self._unpack(data, "I", 0x0004, 0x00A8)[0]
        self.dwVersion = self._unpack(data, "I", 0x0004, 0x00AC)[0]
        self.bzLanKey = self._unpack(data, "16B", 0x0010, 0x00B0)
        self.bzSignatureKey = self._unpack(data, "16B", 0x0010, 0x00C0)

        self.bzTitleAlternateSignatureKey = []

        alt_sig_root = 0x00D0
        for i in range(16):
            self.bzTitleAlternateSignatureKey.append(
                self._unpack(data, "16B", 0x0010, alt_sig_root)
            )
            alt_sig_root += 0x0010

        # Title name cleanup
        self.cleanTitleName = self.wszTitleName.decode('utf-16').rstrip(chr(0))

    @staticmethod
    def _unpack(data, s_format, size, offset):
        return struct.unpack("<" + s_format, data[offset:offset+size])

class XBE_SECTION(object):
    def __init__(self, data):
        self.name = None
        self.data = None

        # Flags
        flags_byte = struct.unpack('B', data[0:1])[0]

        self.flag_writable = (flags_byte >> 0) % 2
        self.flag_preload = (flags_byte >> 1) % 2
        self.flag_executable = (flags_byte >> 2) % 2
        self.flag_inserted_file = (flags_byte >> 3) % 2
        self.flag_head_page_ro = (flags_byte >> 4) % 2
        self.flag_tail_page_ro = (flags_byte >> 5) % 2
        self.flag_unused_a1 = (flags_byte >> 6) % 2
        self.flag_unused_a2 = (flags_byte >> 7) % 2

        self.dwVirtualAddr = struct.unpack('I', data[4:8])[0]  # Virtual address
        self.dwVirtualSize = struct.unpack('I', data[8:12])[0]  # Virtual size
        self.dwRawAddr = struct.unpack('I', data[12:16])[0]  # File offset to raw data
        self.dwSizeofRaw = struct.unpack('I', data[16:20])[0]  # Size of raw data
        self.dwSectionNameAddr = struct.unpack('I', data[20:24])[0]  # Section name addr
        self.dwSectionRefCount = struct.unpack('I', data[24:28])[0]  # Section reference count
        self.dwHeadSharedRefCountAddr = struct.unpack('I', data[28:32])[0]  # Head shared page reference count address
        self.dwTailSharedRefCountAddr = struct.unpack('I', data[32:36])[0]  # Tail shared page reference count address
        self.bzSectionDigest = struct.unpack('20B', data[36:56])  # Section digest


class XBE(object):
    def __init__(self, xbe_path, keep_raw_cert=False):
        self.path = xbe_path
        self.raw_cert = None

        with open(xbe_path, "rb") as xbe_file:
            # Read the first 376 bytes to populate the header
            self.header = XBE_HEADER(xbe_file.read(376))
            self.cert_address = self.header.dwCertificateAddr - self.header.dwBaseAddr
            xbe_file.seek(self.cert_address)
            # Read the required certificate bytes (388)
            self.cert = XBE_CERT(xbe_file.read(464))
            # We're not reading anything more as we don't need to.

            if keep_raw_cert:
                xbe_file.seek(self.cert_address)
                self.raw_cert = xbe_file.read(464)

    def get_xbx_sector(self):
        with open(self.path, "rb") as xbe_file:
            sections_addr_start = self.header.dwSectionHeadersAddr - self.header.dwBaseAddr

            for x in range(0, self.header.dwSections):
                xbe_file.seek(sections_addr_start + (56 * x))
                sector = XBE_SECTION(xbe_file.read(56))

                # If there's no file flag, continue
                if not sector.flag_inserted_file:
                    continue

                xbe_file.seek(sector.dwSectionNameAddr - self.header.dwBaseAddr)

                section_name = ""
                val = struct.unpack('20s', xbe_file.read(20))[0]

                for i in range(0, 20):
                    if val[i] == "\x00":
                        break
                    section_name += val[i]

                # If the sector doesn't contain an image
                if section_name != '$$XTIMAGE':
                    continue

                xbe_file.seek(sector.dwRawAddr)

                image_magic = struct.unpack('4s', xbe_file.read(4))[0][:3]

                # Not the right format
                if image_magic != "XPR":
                    continue

                return sector

        raise ValueError

    def extract_xbx_title_image(self, save_to):
        try:
            sector = self.get_xbx_sector()
        except ValueError:
            return False

        with open(self.path, "rb") as xbe_file, open(save_to, 'wb') as output_file:
            # Seek to the start of the sector once again
            xbe_file.seek(sector.dwRawAddr)
            remaining_bytes = sector.dwSizeofRaw

            # Be extra careful with memory management
            while remaining_bytes > 0:
                chunk_size = min(4096, remaining_bytes)

                chunk = xbe_file.read(chunk_size)

                if not chunk:
                    break

                output_file.write(chunk)

                remaining_bytes -= chunk_size

            return True
