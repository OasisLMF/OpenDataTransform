import yaml


def write_yaml(path, content):
    with open(path, "w") as f:
        yaml.dump(content, f)


def read_yaml(path):
    with open(path) as f:
        return yaml.load(f, yaml.SafeLoader)
