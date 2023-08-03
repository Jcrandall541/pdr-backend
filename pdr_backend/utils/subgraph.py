"""
From this ref...
https://github.com/oceanprotocol/ocean-subgraph/pull/678 "Predictoor support")
... here's an example query:

query {
  predictContracts{
    id	
    token{
      name
    }
    blocksPerEpoch
    blocksPerSubscription
    truevalSubmitTimeoutBlock
    block
    eventIndex
    slots{
      id
      predictions{
        id
        user {
          id
        }
        stake
        payout {
          id
          predictedValue
          trueValue
          payout
        }
      }
      trueValues{
        trueValue
        floatValue
        txId
      }
      revenue
      revenues{
        
        amount
        txId
      }
      
      
    }
    subscriptions{
      
      user {
        id
      }
      expireTime
      txId
    }
    }
    
 }
"""


import os
import requests
from typing import Optional, Dict

from enforce_typing import enforce_types
from web3 import Web3

@enforce_types
def query_subgraph(subgraph_url:str, query:str) -> Dict[str, dict]:
    """
    @arguments
      subgraph_url -- e.g. http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph/graphql
      query -- e.g. in docstring above
    
    @return
      result -- e.g. {"data" : {"predictContracts": ..}}
    """
    request = requests.post(subgraph_url, "", json={"query": query}, timeout=1.5)
    if request.status_code != 200:
        # pylint: disable=broad-exception-raised
        raise Exception(
            f"Query failed. Url: {subgraph_url}. Return code is {request.status_code}\n{query}"
        )
    result = request.json()
    return result

@enforce_types
def get_all_interesting_prediction_contracts(
        subgraph_url:str,
        pairs=Optional[str],
        timeframes=Optional[str],
        sources=Optional[str],
        owners=Optional[str],
) -> Dict[str, dict]:
    """
    @description
      Query the chain for prediction contracts, then filter down 
      according to pairs, timeframes, sources, or owners.
    
    @arguments
      subgraph_url -- e.g.
      pairs -- E.g. filter to "BTC/USDT,ETH/USDT". If None, allow all
      timeframes -- E.g. filter to "5m,15m". If None, allow all
      sources -- E.g. filter to "binance,kraken". If None, allow all
      owners -- E.g. filter to "0x123,0x124". If None, allow all

    @return
      contracts -- dict of [contract_id] : contract_info
        where contract_info is a dict with fields name, address, symbol, ..
    """
    chunk_size = 1000  # max for subgraph = 1000
    offset = 0
    contracts = {}
    
    # prepare keys
    owners_filter = []
    pairs_filter = []
    timeframes_filter = []
    sources_filter = []
    if owners:
        owners_filter = [owner.lower() for owner in owners.split(",")]
    if pairs:
        pairs_filter = [pair for pair in pairs.split(",") if pairs]
    if timeframes:
        timeframes_filter = [
            timeframe for timeframe in timeframes.split(",") if timeframes
        ]
    if sources:
        sources_filter = [source for source in sources.split(",") if sources]

    while True:
        query = """
        {
            predictContracts(skip:%s, first:%s){
                id
                token {
                    id
                    name
                    symbol
                    nft {
                        owner {
                            id
                        }
                        nftData {
                            key
                            value
                        }
                    }
                }
                blocksPerEpoch
                blocksPerSubscription
                truevalSubmitTimeoutBlock
            }
        }
        """ % (
            offset,
            chunk_size,
        )
        offset += chunk_size
        try:
            result = query_subgraph(subgraph_url, query)
            if result["data"]["predictContracts"] == []:
                break
            for contract in result["data"]["predictContracts"]:
                # loop 725 values and get what we need
                info = {
                    "pair": None,
                    "base": None,
                    "quote": None,
                    "source": None,
                    "timeframe": None,
                }
                for nftData in contract["token"]["nft"]["nftData"]:
                    for info_key, info_values in info.items():
                        if (
                            nftData["key"]
                            == Web3.keccak(info_key.encode("utf-8")).hex()
                        ):
                            info[info_key] = Web3.to_text(hexstr=nftData["value"])
                # now do filtering
                if (
                    (
                        len(owners_filter) > 0
                        and contract["token"]["nft"]["owner"]["id"] not in owners_filter
                    )
                    or (
                        len(pairs_filter) > 0
                        and info["pair"]
                        and info["pair"] not in pairs_filter
                    )
                    or (
                        len(timeframes_filter) > 0
                        and info["timeframe"]
                        and info["timeframe"] not in timeframes_filter
                    )
                    or (
                        len(sources_filter) > 0
                        and info["source"]
                        and info["source"] not in sources_filter
                    )
                ):
                    continue

                contracts[contract["id"]] = {
                    "name": contract["token"]["name"],
                    "address": contract["id"],
                    "symbol": contract["token"]["symbol"],
                    "blocks_per_epoch": contract["blocksPerEpoch"],
                    "blocks_per_subscription": contract["blocksPerSubscription"],
                    "last_submited_epoch": 0,
                }
                contracts[contract["id"]].update(info)
        except Exception as e:
            print(e)
            return {}
    return contracts
