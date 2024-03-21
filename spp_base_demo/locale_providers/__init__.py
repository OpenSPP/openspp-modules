from faker import Faker
from faker.config import AVAILABLE_LOCALES
from .en_KE import Provider as EnKeProvider
from .lo_LA import Provider as LoLaProvider
from .si_LK import Provider as SiLkProvider
from .sw_KE import Provider as SwKeProvider
from .ta_LK import Provider as TaLkProvider


def get_faker_provider(lang):
    """
    The function `get_faker_provider` returns a provider based on the language code provided.

    :param lang: The `get_faker_provider` function takes a language code as input and returns the
    corresponding provider class based on the language. The language codes and their corresponding
    provider classes are as follows:
    :return: The function `get_faker_provider` returns a provider class based on the language code
    provided as an argument. If the language code matches one of the supported languages ("en_KE",
    "lo_LA", "si_LK", "sw_KE", "ta_LK"), it returns the corresponding provider class. Otherwise, it
    returns `None`.
    """
    if lang == "en_KE":
        return EnKeProvider
    if lang == "lo_LA":
        return LoLaProvider
    if lang == "si_LK":
        return SiLkProvider
    if lang == "sw_KE":
        return SwKeProvider
    if lang == "ta_LK":
        return TaLkProvider
    return None


def create_faker(lang):
    """
    The function `create_faker` creates a Faker object with a specified language locale and adds a
    custom provider if available.

    :param lang: The `lang` parameter is used to specify the language/locale for which you want to
    create a Faker instance. The function checks if the specified language is in the list of available
    locales (`AVAILABLE_LOCALES`). If it is, it creates a Faker instance with that locale. If the
    specified language is
    :return: An instance of the Faker class with the specified locale and additional provider if
    available.
    """
    locale = lang if lang in AVAILABLE_LOCALES else None
    fake = Faker(locale=locale)

    if lang and lang not in AVAILABLE_LOCALES:
        provider = get_faker_provider(lang)
        if provider:
            fake.add_provider(provider)

    return fake
