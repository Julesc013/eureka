# Test Isolation Report

`tests/scripts/test_static_site_generator.py::StaticSiteGeneratorScriptTest.test_build_json_parses` now passes `--output` with a temporary directory. The test no longer writes to `site/dist` during ordinary unittest discovery.

The generated artifact policy and site/dist isolation policy define the rule for future tests: committed generated roots are not test scratch space.
