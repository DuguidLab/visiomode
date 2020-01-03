#!/usr/bin/env python3

"""Main application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis as rds
import visiomode.config as cfg


def main():
    config = cfg.Config()
    redis = rds.Redis(host=config.redis_host, port=config.redis_port)


if __name__ == '__main__':
    main()
