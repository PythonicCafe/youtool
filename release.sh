#!/bin/bash

rm -rf build dist
python setup.py sdist bdist_wheel
twine check dist/*

if [[ $1 = "--test" ]]; then
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
	twine upload dist/*
fi
