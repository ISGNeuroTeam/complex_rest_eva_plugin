# complex_rest_eva_plugin

Plugin for [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop)

### Installing

* Make symlink for ./complex_rest_eva_plugin/complex_rest_eva_plugin in plugins directory
* Run complex rest server

## Running the tests
Run all tests:
```bash
python ./complex_rest/manage.py test ./plugin_dev/complex_rest_eva_plugin/tests --settings=core.settings.test
```

## Deployment

* Make plugin archive:
```bash
make pack
```
* Unpack archive into complex_rest plugins directory

## Built With

* [Django](https://docs.djangoproject.com/en/3.2/) - The web framework used


## Contributing

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors


## License

[OT.PLATFORM. License agreement.](LICENSE.md)

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc