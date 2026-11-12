#!/usr/bin/env python3

# Copyright (c) 2026 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Matt Hart <matthart@qti.qualcomm.com>

"""Run one quick method or named command on a board through `pytactl service`.

    tac-api.py --serial <ID_SERIAL_SHORT> --command bootToEDL
    tac-api.py --serial <ID_SERIAL_SHORT> --pin reset --pin-value 1

It exits non-zero with the service's error when the request fails, so a
caller such as a LAVA power command stops instead of carrying on as if the
board had been powered or put in EDL mode.
"""

import sys
from argparse import ArgumentParser

import requests

parser = ArgumentParser()
parser.add_argument(
    "--url",
    default="http://localhost:5000",
    help="pytactl service URL (default: http://localhost:5000)",
)
parser.add_argument("--serial", required=True, help="Debug board serial number")
parser.add_argument("--command", help="Quick method, such as bootToEDL")
parser.add_argument("--pin", help="Named pin command")
parser.add_argument("--pin-value", choices=["0", "1"], help="Named pin value")
parser.add_argument(
    "--timeout", type=float, default=60, help="Request timeout in seconds"
)
args = parser.parse_args()

if not args.command and not args.pin:
    parser.error("give --command or --pin")
if args.pin and args.pin_value is None:
    parser.error("--pin needs --pin-value")

try:
    if args.pin:
        r = requests.put(
            f"{args.url}/{args.serial}/command/{args.pin}",
            json={"value": int(args.pin_value)},
            timeout=args.timeout,
        )
    else:
        r = requests.put(
            f"{args.url}/{args.serial}/quick/{args.command}", timeout=args.timeout
        )
except requests.RequestException as error:
    sys.exit(f"tac-api: {error}")

# Don't test the response itself for truth: a requests.Response is false for
# any 4xx or 5xx status.
if r.status_code != 200:
    sys.exit(f"tac-api: {args.serial}: HTTP {r.status_code}: {r.text.strip()}")
