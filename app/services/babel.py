from fastapi_babel import Babel, BabelConfigs

from app.config import ROOT_DIR, TRANSLATION_DIRECTORY, DEFAULT_LOCALE

configs = BabelConfigs(
    ROOT_DIR=ROOT_DIR,
    BABEL_DEFAULT_LOCALE=DEFAULT_LOCALE,
    BABEL_TRANSLATION_DIRECTORY=TRANSLATION_DIRECTORY,
    BABEL_CONFIG_FILE=f"{ROOT_DIR}/babel.cfg"
)
babel = Babel(configs=configs)

