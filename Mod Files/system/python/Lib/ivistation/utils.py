import re

THUMBNAIL_PATTERN = re.compile(r'\([^)]*\)')


def clean_rom_name(name):
    """
    Removes region tags from a ROM name, those such as (USA) (Europe),
    and anything contained withing "()" in general. Useful for
    searching in databases following the no-intro standard.
    """

    return re.sub(THUMBNAIL_PATTERN, '', name).strip()
