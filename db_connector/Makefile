
#.SILENT:
SHELL = /bin/bash


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"db_connector_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

pack: make_build
	$(SET_VERSION)
	$(SET_BRANCH)
	rm -f db_connector-*.tar.gz
	echo Create archive \"db_connector-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../db_connector-$(VERSION)-$(BRANCH).tar.gz db_connector

clean_pack:
	rm -f db_connector-*.tar.gz


db_connector.tar.gz: build
	cd make_build; tar czf ../db_connector.tar.gz db_connector && rm -rf ../make_build

build: make_build

make_build: venv venv.tar.gz
	# required section
	echo make_build
	mkdir make_build

	cp -R ./db_connector make_build
	rm make_build/db_connector/db_connector.conf
	mv make_build/db_connector/db_connector.conf.example make_build/db_connector/db_connector.conf
	cp *.md make_build/db_connector/
	cp *.py make_build/db_connector/
	if [ -s requirements.txt ]; then \
		mkdir make_build/db_connector/venv;\
		tar -xzf ./venv.tar.gz -C make_build/db_connector/venv; \
	fi

clean_build:
	rm -rf make_build

venv:
	if [ -s requirements.txt ]; then \
		echo Create venv; \
		conda create --copy -p ./venv -y; \
		conda install -p ./venv python==3.8.5 -y; \
		./venv/bin/pip install --no-input  -r requirements.txt; \
	fi

venv.tar.gz: venv
	if [ -s requirements.txt ]; then \
		conda pack -p ./venv -o ./venv.tar.gz; \
	fi

clean_venv:
	rm -rf venv
	rm -f ./venv.tar.gz


clean: clean_build clean_venv clean_pack clean_test

test: venv
	@echo "Testing..."


clean_test:
	@echo "Clean tests"






