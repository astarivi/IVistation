import xbmc
import random


def main():
    container_ids = ("9000", "50",)

    for container_id in container_ids:
        try:
            item_count = int(xbmc.getInfoLabel(
                'Container({}).NumItems'.format(container_id))
            )
            randr = str(random.randrange(0, item_count, 1))
            if xbmc.getCondVisibility('Window.IsVisible(10000)') or item_count >= 10:
                xbmc.executebuiltin('SetFocus({},{})'.format(item_count, randr))
        except Exception:
            pass


if __name__ == '__main__':
    print("Random sort in progress.")
    main()
