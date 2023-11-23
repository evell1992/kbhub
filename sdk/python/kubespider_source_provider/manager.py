import argparse
import os
import subprocess
from functools import wraps
import yaml


class ProviderConf:
    def __init__(self, path):
        self.name, self.type, self.instance_params = self.load_conf(path)

    @staticmethod
    def load_conf(path):
        with open(os.path.join(path, 'provider.yaml')) as f:
            conf = f.read()
            data = yaml.safe_load(conf)
            return data['provider_name'], data['provider_type'], data['instance_params']

    def params(self, **conf) -> dict:
        return self.instance_params


class Manager:
    TYPE = {
        "string": str,
        "list": list,
        "int": int,
        "bool": bool,
        "dict": dict
    }

    def __init__(self):
        self.provider = None
        self.search_method = None
        self.schedule_method = None

    def run(self):
        conf = self.parse_parameters("/Users/evell/Desktop/github/sphub/providers/nexus-source-provider")
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=f"Kubespider [{conf.type} : {conf.name}] ",
            prog='kubespider'
        )
        for param in conf.params():
            parser.add_argument(
                f"--{param.get('name')}",
                type=self.TYPE.get(param.get('value_type')),
                help=param.get('desc'),
                nargs='?'
            )
        parser.add_argument(
            "--call_mode",
            type=str,
            help="search or schedule")
        namespace = parser.parse_args()
        args = vars(namespace)
        if self.provider:
            call_mode = args.get("call_mode")
            if call_mode == 'search':
                provider = self.provider(**args)
                self.report('', getattr(provider, 'search'))
            elif call_mode == 'schedule':
                provider = self.provider(**args)
                self.report('', getattr(provider, 'schedule'))
            else:
                raise Exception(f'Unsupported call_mode: {call_mode}')
        else:
            raise Exception('this manager have no provider')

    @staticmethod
    def parse_parameters(conf_path):
        return ProviderConf(conf_path)

    @classmethod
    def compile_and_package(cls, provider_dir):
        conf = cls.parse_parameters(provider_dir)
        cache_dir = os.path.join(provider_dir, 'cache_dir')
        file_dir = os.path.join(provider_dir, 'provider.py')
        cmd = f"cd {provider_dir} && pyinstaller -F {file_dir} --hidden-import pyyaml"
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        build_path = os.path.join(provider_dir, 'build')
        dist_path = os.path.join(provider_dir, 'dist')
        bin_path = os.path.join(provider_dir, 'bin')
        move_bin = f'mkdir -p {bin_path} && mv {os.path.join(dist_path, "provider")} {bin_path}'
        clean_cmd = f'rm -rf {build_path} {dist_path}'
        subprocess.run(move_bin, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        subprocess.run(clean_cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    def search(self, func):
        if self.search_method is None:
            self.search_method = func
        else:
            print(self.search_method)
            raise Exception('search method has been bound')
        return func

    def schedule(self, func):
        if self.schedule_method is None:
            self.schedule_method = func
        else:
            print(self.schedule_method)
            raise Exception('schedule method has been bound')
        return func

    def report(self, host, function):
        print(function())

    def __call__(self, provider_class):
        if not self.provider:
            self.provider = provider_class
        else:
            raise Exception('this kubespider manager has been bound')

        return provider_class
