#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
import json
import sys


def _parse_cmdline():
    parser = ArgumentParser(description='Gera o arquivo de links')

    parser.add_argument('--data-file', type=FileType('r'), default='data.json',
                        help='Arquivo com os dados dos links')

    parser.add_argument('--output', type=FileType('w'), default='links.html',
                        help='Arquivo HTML com a lista de links')

    return parser.parse_args()


def out(*args):
    print(*args, file=output)


def _valid_services(all_services):
    for nome, params in all_services.items():
        if params.get('url_template'):
            yield nome, params


_ENV_SERVICE_KEYS = {'env', 'env_alt'}


def _is_env_service(params):
    return _ENV_SERVICE_KEYS.intersection(params.get('required_keys', {}))


def _non_env_services(services):
    for nome, params in _valid_services(services):
        if not _is_env_service(params):
            yield nome, params


def _env_services(services):
    for nome, params in _valid_services(services):
        if _is_env_service(params):
            yield nome, params


def _headers(services, environments):
    out('<html>')
    out('<body>')
    out('  <table border=1>')
    out('    <thead>')

    out('      <tr>')
    out('        <th rowspan=2 style="text-align:left">API</th>')
    for nome, params in _non_env_services(services):
        out(f'        <th rowspan=2>{nome}</th>')

    env_services_len = sum(1 for _ in _env_services(services))
    for name in environments.keys():
        out(f'        <th colspan={env_services_len}>{name}</th>')

    out('      </tr>')

    out('      <tr>')

    for environment in environments:
        for service, params in _env_services(services):
            out(f'        <th>{service}</th>')
    out('      </tr>')

    out('    </thead>')


def _has_missing_params(service_params, available_params):
    if 'required_keys' not in service_params:
        return False

    for key in service_params['required_keys']:
        if key not in available_params:
            return True

        if available_params[key] is None:
            return True

    return False


def _non_env_services_cells(api, api_params, services):
    url_params = {
            'api': api
            }
    url_params.update(**api_params)

    for service, service_params in _non_env_services(services):
        print(f'  {service}')

        if _has_missing_params(service_params, url_params):
            out('        <td></td>')
        else:
            url_template = service_params['url_template']
            url = url_template.format(**url_params)
            out(f'        <td><a href="{url}">{service}</a></td>')


def _env_services_cells(api, api_params, environments, services):
    for environment, env_params in environments.items():
        for service, service_params in _env_services(services):
            print(f'  {service} ({environment})')
            url_params = {
                    'api': api,
                    'env': environment,
                    'env_alt': env_params['alt'],
                    }
            url_params.update(**api_params)

            if _has_missing_params(service_params, url_params):
                out('        <td></td>')
            else:
                url_template = service_params['url_template']
                url = url_template.format(**url_params)
                out(f'        <td><a href="{url}">{service}</a></td>')


def _body(apis, services, environments):
    out('    <tbody>')

    for api, api_params in apis:
        print(f'Gerando links para {api}')
        out('      <tr>')
        out(f'        <th style="text-align:left">{api}</th>')

        _non_env_services_cells(api, api_params, services)

        _env_services_cells(api, api_params, environments, services)

        out('      </tr>')
    out('    </tbody>')


def _footers():
    out('  </table>')
    out('</html>')


def _generate_links(data_file):
    data = json.load(data_file)

    _headers(data['services'], data['environments'])

    _body(data['apis'].items(), data['services'], data['environments'])

    _footers()


def main():
    args = _parse_cmdline()

    global output
    output = args.output

    _generate_links(args.data_file)


if __name__ == '__main__':
    sys.exit(main())
