from .en_KE import Provider as EnKeProvider
from .lo_LA import Provider as LoLaProvider
from .si_LK import Provider as SiLkProvider
from .sw_KE import Provider as SwKeProvider
from .ta_LK import Provider as TaLkProvider


def get_faker_provider(lang):
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
