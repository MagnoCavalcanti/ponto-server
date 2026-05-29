from datetime import datetime


class RepRegistroAdapter:
    """Adapta um dict de registro vindo do relógio para atributos usados pelo sistema."""

    def __init__(self, raw: dict):
        self._raw = raw
        data, hora = raw["data"].split(" ")
        if hora.count(":") == 1:
            hora = f"{hora}:00"
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        self._data = data_obj.strftime("%Y-%m-%d")
        self._hora = hora
        cpf = str(raw["cpf"])
        self._cpf = cpf.zfill(11) if len(cpf) < 11 else cpf
        self._nsr = raw["nsr"]

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def data(self) -> str:
        return self._data

    @property
    def hora(self) -> str:
        return self._hora

    @property
    def nsr(self) -> int:
        return self._nsr

    @property
    def cache_key(self) -> str:
        return f"{self._cpf}_{self._data}"
