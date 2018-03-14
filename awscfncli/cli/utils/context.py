# -*- encoding: utf-8 -*-

import fnmatch
import copy
import boto3


class ContextObject(object):
    """Click context object """

    def __init__(self, config,
                 profile,
                 region,
                 verbosity):
        self.config = config
        self.profile = profile
        self.region = region
        self.verbosity = verbosity

    def find_stack_config(self, env_pattern, stack_pattern):
        """ Find matching stack configurations

        Assuming config is a dict of dict of namedtuples:
            config[env][stack] = stack_config
        """
        for env_name in self.config.list_environments():
            if fnmatch.fnmatchcase(env_name, env_pattern):
                for stack_name in self.config.list_stacks(env_name):
                    if fnmatch.fnmatchcase(stack_name, stack_pattern):
                        stack_config = \
                            self.config.get_stack(env_name, stack_name)._asdict()

                        # override parameters
                        if self.profile is not None:
                            stack_config['Metadata']['Profile'] = self.profile
                        if self.region is not None:
                            stack_config['Metadata']['Region'] = self.region

                        yield stack_config

    def find_one_stack_config(self, env_pattern, stack_pattern):
        for r in self.find_stack_config(env_pattern, stack_pattern):
            return r
        else:
            raise RuntimeError('Stack not found.')

    def get_boto3_session(self, stack_config):

        session = boto3.session.Session(
            profile_name=stack_config['Metadata']['Profile'],
            region_name=stack_config['Metadata']['Region'],
        )

        return session
