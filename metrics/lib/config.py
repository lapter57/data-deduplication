from ruamel.yaml import YAML

yaml = YAML(typ='safe')


def load_config(doc):
    config_dict = dict()
    if hasattr(doc, "items"):
        for key, val in doc.items():
            config_dict[key] = val
    return config_dict


class Dotdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=None):
        super().__init__()
        dct = dct if dct else dict()
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = Dotdict(value)
            self[key] = value


class Config(Dotdict):
    def __init__(self, file_path):
        super().__init__()
        with open(file_path, "r") as config_file:
            data = yaml.load(config_file)
        config_dict = load_config(data)
        dotdict = Dotdict(config_dict)
        for key, value in dotdict.items():
            setattr(self, key, value)

    __getattr__ = Dotdict.__getitem__
    __setattr__ = Dotdict.__setitem__
    __delattr__ = Dotdict.__delitem__
