from parse_manual import SYSTEMS, parse_roms


def parse_auto(progress_dialog):
    """
    Iterates all the systems, and imports what it can find.
    """
    total = 0

    for system, sys_parser in SYSTEMS.items():
        total += parse_roms(system, progress_dialog)

    return total
