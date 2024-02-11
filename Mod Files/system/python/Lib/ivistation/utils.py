import re
import xbmc

THUMBNAIL_PATTERN = re.compile(r'\([^)]*\)')


# noinspection PyClassHasNoInit
class ArtworkType:
    BOXART = "boxart"
    BOXART3D = "boxart3d"
    LOGO = "logo"
    MIX = "mix"
    SCREENSHOTS = "screenshots"

    @staticmethod
    def get_from_value(value):
        return getattr(ArtworkType, value.upper())


def clean_rom_name(name):
    """
    Removes region tags from a ROM name, those such as (USA) (Europe),
    and anything contained withing "()" in general. Useful for
    searching in databases following the no-intro standard.
    """

    return re.sub(THUMBNAIL_PATTERN, '', name).strip()


def get_artwork_type(d_system):
    # If it's not defined
    if not xbmc.getCondVisibility('Skin.String({}_artworkfolder)'.format(d_system)):
        xbmc.executebuiltin('Skin.SetString({}_artworkfolder,boxart)'.format(d_system))

    try:
        return ArtworkType.get_from_value(
            xbmc.getInfoLabel("Skin.String({}_artworkfolder)".format(d_system))
        )
    except AttributeError:
        xbmc.executebuiltin('Skin.SetString({}_artworkfolder,boxart)'.format(d_system))

    return ArtworkType.BOXART
