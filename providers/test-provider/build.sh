#!/bin/sh

pyinstaller -F provider.py --distpath=bin --collect-all=kubespider_source_provider --clean