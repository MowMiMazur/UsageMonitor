import webview

from core.api import Api
from core.utils import resource_path
from core.constants import APP_NAME, get_full_version, WINDOW_WIDTH, WINDOW_HEIGHT


def main():
    api = Api()

    window = webview.create_window(
        title=f"{APP_NAME} {get_full_version()}",
        url=resource_path("web/index.html"),
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(WINDOW_WIDTH, WINDOW_HEIGHT),  # can't shrink below the initial size
        background_color="#0b0d11",
        text_select=False,
    )
    api.set_window(window)

    webview.start(gui="edgechromium")


if __name__ == "__main__":
    main()
