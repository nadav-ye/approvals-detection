from web3 import Web3
import argparse
import asyncio

import web3_utils


approval_event_signature = "0x" + Web3.keccak(text="Approval(address,address,uint256)").hex() # 8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925

def get_padded_address_from_arg() -> hex:
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", required=True)
    args = parser.parse_args()
    address:hex = args.address
    return web3_utils.encode_address_to_32bytes(address)

async def main():
    padded_address = get_padded_address_from_arg()

    filtered_logs = await web3_utils.get_all_logs_of_an_event_signature_of_address(approval_event_signature, padded_address)

    contracts_addresses_set = set(log["address"] for log in filtered_logs)

    contract_name_map = await web3_utils.fetch_contract_names(contracts_addresses_set)

    for log in filtered_logs:
        # print(log)
        try:
            value = int(log["data"].hex(), 16)
            # TODO: check what happens if it's an empty hex - "0x" - seems like; check what's 0xffffff means - unlimited?
        except Exception as e:
            print("invalid data: ", log["data"], "error: ", e)
            value = log["data"]
        
        # print(f"Block: {log['blockNumber']}, Owner: {owner}, Spender: {spender}, Token: {contract_name}, Value: {value} \n")
        print(f"approval on {contract_name_map[log['address']]} on amount of {value}")
    

if __name__ == "__main__":
    asyncio.run(main())