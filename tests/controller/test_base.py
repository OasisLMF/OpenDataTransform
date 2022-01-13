from unittest.mock import Mock, patch

from converter.config import Config
from converter.connector import BaseConnector
from converter.controller.base import Controller
from converter.mapping import BaseMapping
from converter.runner.base import BaseRunner


class FakeRunner(BaseRunner):
    pass


class FakeExtractor(BaseConnector):
    pass


class FakeLoader(BaseConnector):
    pass


class FakeMapping(BaseMapping):
    pass


def test_component_class_paths_are_set___specific_component_classes_are_used():
    runner = Mock()
    extractor = Mock()
    loader = Mock()
    mapping = Mock()

    with patch(
        "tests.controller.test_base.FakeRunner",
        return_value=runner,
    ) as runner_ctor_mock, patch(
        "tests.controller.test_base.FakeExtractor",
        return_value=extractor,
    ) as extractor_ctor_mock, patch(
        "tests.controller.test_base.FakeLoader",
        return_value=loader,
    ) as loader_ctor_mock, patch(
        "tests.controller.test_base.FakeMapping",
        return_value=mapping,
    ) as mapping_ctor_mock:
        config = Config(
            overrides={
                "transformations": {
                    "ACC": {
                        "input_format": {
                            "name": "A",
                            "version": "1",
                        },
                        "output_format": {
                            "name": "B",
                            "version": "1",
                        },
                        "runner": {
                            "path": "tests.controller.test_base.FakeRunner",
                            "options": {"first": "Some Runner Param"},
                        },
                        "extractor": {
                            "path": "tests.controller.test_base.FakeExtractor",
                            "options": {"first": "Some Extractor Param"},
                        },
                        "loader": {
                            "path": "tests.controller.test_base.FakeLoader",
                            "options": {"first": "Some Loader Param"},
                        },
                        "mapping": {
                            "path": "tests.controller.test_base.FakeMapping",
                            "options": {"first": "Some Mapping Param"},
                        },
                    }
                }
            }
        )

        controller = Controller(config)

        controller.run(threaded=False)

        transformer_config = config.get_transformation_configs()[0]
        extractor_ctor_mock.assert_called_once_with(
            transformer_config,
            first="Some Extractor Param",
        )
        loader_ctor_mock.assert_called_once_with(
            transformer_config, first="Some Loader Param"
        )
        mapping_ctor_mock.assert_called_once_with(
            transformer_config, first="Some Mapping Param"
        )
        runner_ctor_mock.assert_called_once_with(
            transformer_config, first="Some Runner Param"
        )
        runner.run.assert_called_once_with(extractor, mapping, loader)


def test_component_class_paths_default___default_component_classes_are_used():
    runner = Mock()
    extractor = Mock()
    loader = Mock()
    mapping = Mock()

    with patch(
        "converter.runner.PandasRunner",
        return_value=runner,
    ) as runner_ctor_mock, patch(
        "converter.connector.CsvConnector",
        side_effect=[extractor, loader],
    ) as connector_ctor_mock, patch(
        "converter.mapping.FileMapping",
        return_value=mapping,
    ) as mapping_ctor_mock:
        config = Config(
            overrides={
                "transformations": {
                    "ACC": {
                        "input_format": {
                            "name": "A",
                            "version": "1",
                        },
                        "output_format": {
                            "name": "B",
                            "version": "1",
                        },
                        "runner": {"options": {"first": "Some Runner Param"}},
                        "extractor": {"options": {"first": "Some Extractor Param"}},
                        "loader": {"options": {"first": "Some Loader Param"}},
                        "mapping": {"options": {"first": "Some Mapping Param"}},
                    }
                }
            }
        )

        controller = Controller(config)

        controller.run(threaded=False)

        transformer_config = config.get_transformation_configs()[0]
        connector_ctor_mock.assert_any_call(
            transformer_config, first="Some Extractor Param"
        )
        connector_ctor_mock.assert_any_call(transformer_config, first="Some Loader Param")
        mapping_ctor_mock.assert_called_once_with(
            transformer_config, first="Some Mapping Param"
        )
        runner_ctor_mock.assert_called_once_with(
            transformer_config, first="Some Runner Param"
        )
        runner.run.assert_called_once_with(extractor, mapping, loader)
