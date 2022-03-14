import os.path

from converter.config import Config
from tests.config.fakes import config_file


def test_filename_provided___original_file_is_left_intact():
    with config_file({}) as p:
        new_conf_path = os.path.join(os.path.dirname(p), "new-conf.yml")
        orig_config = Config(config_path=p)

        updated_config = Config(config_path=p)
        updated_config.set("foo", "bar")

        updated_config.save(new_filename=new_conf_path)

        reloaded = Config(config_path=p)

        assert reloaded == orig_config
        assert updated_config == Config(config_path=new_conf_path)


def test_filename__not_provided___original_file_updated():
    with config_file({}) as p:
        updated_config = Config(config_path=p)
        updated_config.set("foo", "bar")

        updated_config.save()

        reloaded = Config(config_path=p)

        assert updated_config == reloaded
