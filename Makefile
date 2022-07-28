
#.SILENT:
SHELL = /bin/bash

.PHONY: clean clean_build clean_pack clean_test clean_docker_test clean_venv test docker_test

all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"eva_plugin_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

VERSION := $(shell cat setup.py | grep version | head -n 1 | sed -re "s/[^\"']+//" | sed -re "s/[\"',]//g")
BRANCH := $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')


define clean_docker_containers
	@echo "Stopping and removing docker containers"
	docker-compose -f docker-compose-test.yml stop
	if [[ $$(docker ps -aq -f name=eva_plugin) ]]; then docker rm $$(docker ps -aq -f name=eva_plugin);  fi;
endef

pack: make_build
	rm -f eva_plugin-*.tar.gz
	echo Create archive \"eva_plugin-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../eva_plugin-$(VERSION)-$(BRANCH).tar.gz dashboards themes quizs db_connector


clean_pack:
	rm -f eva_plugin-*.tar.gz

eva_plugin.tar.gz: build
	cd make_build; tar czf ../eva_plugin.tar.gz eva_plugin && rm -rf ../make_build

build: make_build

make_build: make_build/dashboards make_build/quizs make_build/db_connector make_build/themes

make_build/dashboards: venv_dashboards venv_dashboards.tar.gz
	mkdir -p make_build
	cp -R ./dashboards make_build
	mv make_build/dashboards/dashboards.conf.example make_build/dashboards/dashboards.conf
	mkdir make_build/dashboards/venv
	tar -xzf ./venv_dashboards.tar.gz -C make_build/dashboards/venv

make_build/themes:
	mkdir -p make_build
	cp -R ./themes make_build
	mv make_build/themes/themes.conf.example make_build/themes/themes.conf

make_build/db_connector: venv_db_connector.tar.gz
	mkdir -p make_build
	cp -R ./db_connector make_build
	mv make_build/db_connector/db_connector.conf.example make_build/db_connector/db_connector.conf
	mkdir make_build/db_connector/venv
	tar -xzf ./venv_db_connector.tar.gz -C make_build/db_connector/venv

make_build/quizs: venv_quizs.tar.gz
	mkdir -p make_build
	cp -R ./quizs make_build
	mv make_build/quizs/quizs.conf.example make_build/quizs/quizs.conf
	mkdir make_build/quizs/venv
	tar -xzf ./venv_quizs.tar.gz -C make_build/quizs/venv


venv_db_connector:
	echo Create venv_db_connector
	conda create --copy -p ./venv_db_connector -y
	conda install -p ./venv_db_connector python==3.9.7 -y
	./venv_db_connector/bin/pip install --no-input  -r requirements_db_connector.txt

venv_quizs:
	echo Create venv_quizs
	conda create --copy -p ./venv_quizs -y
	conda install -p ./venv_quizs python==3.9.7 -y
	./venv_quizs/bin/pip install --no-input  -r requirements_quizs.txt

venv_dashboards:
	echo Create venv_dashboards
	conda create --copy -p ./venv_dashboards -y
	conda install -p ./venv_dashboards python==3.9.7 -y
	./venv_dashboards/bin/pip install --no-input  -r requirements_dashboards.txt

venv_dashboards.tar.gz: venv_dashboards
	conda pack -p ./venv_dashboards -o ./venv_dashboards.tar.gz

venv_quizs.tar.gz: venv_quizs
	conda pack -p ./venv_quizs -o ./venv_quizs.tar.gz

venv_db_connector.tar.gz: venv_db_connector
	conda pack -p ./venv_db_connector -o ./venv_db_connector.tar.gz

make_build: make_build/dashboards make_build/themes make_build db_connector make_build/quizs

clean_build:
	rm -rf make_build

clean_venv:
	rm -rf venv*

clean: clean_build clean_venv clean_pack clean_test

test: docker_test

logs:
	mkdir -p ./logs

docker_test: logs
	$(call clean_docker_containers)
	@echo "Testing..."
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-test.yml run --rm  complex_rest python ./complex_rest/manage.py test ./tests --settings=core.settings.test --no-input
	$(call clean_docker_containers)

clean_docker_test:
	$(call clean_docker_containers)

clean_test: clean_docker_test







