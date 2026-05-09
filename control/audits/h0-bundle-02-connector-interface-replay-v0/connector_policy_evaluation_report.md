# Connector Policy Evaluation Report

The policy evaluator is offline and fail-closed. It allows committed fixture
replay, can represent future operations as dry-run only, and blocks forbidden
operations such as downloads, arbitrary URL fetches, broad crawling, public
index mutation, master index mutation, and truth acceptance.
