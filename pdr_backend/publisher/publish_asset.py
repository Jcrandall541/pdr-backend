from typing import Union

from enforce_typing import enforce_types

from pdr_backend.contract.data_nft import DataNft
from pdr_backend.contract.erc721_factory import Erc721Factory
from pdr_backend.ppss.web3_pp import Web3PP
from pdr_backend.util.contract import get_address
from pdr_backend.util.mathutil import to_wei

MAX_UINT256 = 2**256 - 1


@enforce_types
def publish_asset(
    s_per_epoch: int,
    s_per_subscription: int,
    base: str,
    quote: str,
    source: str,
    timeframe: str,
    trueval_submitter_addr: str,
    feeCollector_addr: str,
    rate: Union[int, float],
    cut: Union[int, float],
    web3_pp: Web3PP,
):
    """Publish one specific asset to chain."""
    web3_config = web3_pp.web3_config
    pair = base + "/" + quote
    trueval_timeout = 60 * 60 * 24 * 3
    owner = web3_config.owner
    ocean_address = get_address(web3_pp, "Ocean")
    fre_address = get_address(web3_pp, "FixedPrice")
    factory = Erc721Factory(web3_pp)

    feeCollector = web3_config.w3.to_checksum_address(feeCollector_addr)
    trueval_submiter = web3_config.w3.to_checksum_address(trueval_submitter_addr)

    rate_wei = to_wei(rate)
    cut_wei = to_wei(cut)

    nft_name: str = base + "-" + quote + "-" + source + "-" + timeframe
    nft_symbol: str = pair
    erc20_name: str = nft_symbol
    erc20_symbol: str = nft_symbol

    nft_data: tuple = (nft_name, nft_symbol, 1, "", True, owner)
    erc_data: tuple = (
        3,
        [erc20_name, erc20_symbol],
        [
            owner,
            owner,
            feeCollector,
            ocean_address,
            ocean_address,
        ],
        [MAX_UINT256, 0, s_per_epoch, s_per_subscription, trueval_timeout],
        [],
    )
    fre_data: tuple = (
        fre_address,
        [ocean_address, owner, feeCollector, owner],
        [18, 18, rate_wei, cut_wei, 1],
    )

    logs_nft, logs_erc = factory.createNftWithErc20WithFixedRate(
        nft_data, erc_data, fre_data
    )
    data_nft_address: str = logs_nft["newTokenAddress"]
    print(f"Deployed NFT: {data_nft_address}")

    data_nft = DataNft(web3_pp, data_nft_address)
    tx = data_nft.set_data("pair", pair)
    print(f"Pair set to {pair} in {tx.hex()}")

    tx = data_nft.set_data("base", base)
    print(f"base set to {base} in {tx.hex()}")

    tx = data_nft.set_data("quote", quote)
    print(f"quote set to {quote} in {tx.hex()}")

    tx = data_nft.set_data("source", source)
    print(f"source set to {source} in {tx.hex()}")

    tx = data_nft.set_data("timeframe", timeframe)
    print(f"timeframe set to {timeframe} in {tx.hex()}")

    tx = data_nft.add_erc20_deployer(trueval_submiter)
    print(f"Erc20Deployer set to {trueval_submiter} in {tx.hex()}")

    return (nft_data, erc_data, fre_data, logs_nft, logs_erc)