import argparse
import asyncio

import web3_utils
import address_approvals

from typing import Dict, List, Any

def get_address_from_arg() -> hex:
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", required=True)
    args = parser.parse_args()
    address:hex = args.address
    return address


def print_latest_approvals(latest_approvals:List[Dict[str, Any]]) -> None:
    for log in latest_approvals:
        amount = int(log["data"].hex(), 16)
        print(f"approval on {web3_utils.contract_name_map[log['address']]} on amount of {amount}")


def main():
    arg_address = get_address_from_arg()
    latest_approvals = asyncio.run(address_approvals.get_address_approvals(arg_address))
    print_latest_approvals(latest_approvals)


if __name__ == "__main__":
    main()