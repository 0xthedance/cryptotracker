from typing import Dict, Any

ETHEREUM_RPC = "ethereum:mainnet:alchemy"

WALLET_TYPES = {
    "HOT": "HOT",
    "COLD": "COLD",
    "SMART": "SMART",
}

POOL_TYPES = {
    "STAKING": "staking",
    "LENDING": "lending",
    "STABILITY_POOL": "stability pool",
    "BORROWING": "borrowing",
    "AMM": "AMM pool",
}

NETWORKS = {
    "ETHEREUM": {
        "name": "Ethereum",
        "url_rpc": "ethereum:mainnet:alchemy",
        "image": "cryptotracker/logos/ethereum.png",
    },
    "ARBITRUM": {
        "name": "Arbitrum",
        "url_rpc": "arbitrum:mainnet:alchemy",
        "image": "cryptotracker/logos/arbitrum.png",
    },
    "AVALANCHE": {
        "name": "Avalanche",
        "url_rpc": "avalanche:mainnet:alchemy",
        "image": "cryptotracker/logos/avalanche.png",
    },
    "GNOSIS": {
        "name": "Gnosis Chain",
        "url_rpc": "gnosis:mainnet:alchemy",
        "image": "cryptotracker/logos/gnosis.png",
    },
    "BASE": {
        "name": "Base",
        "url_rpc": "base:mainnet:alchemy",
        "image": "cryptotracker/logos/base.png",
    },
}

PROTOCOLS_DATA: Dict[str, Any] = {
    "LQTY_V1": {
        "name": "Liquity v1",
        "image": "cryptotracker/logos/liquity_v1.png",
        NETWORKS["ETHEREUM"]["name"]: [
            {
                "type": POOL_TYPES["STAKING"],
                "contract_address": "0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d",
                "image": "cryptotracker/logos/liquity_staking.png",
            },
            {
                "type": POOL_TYPES["STABILITY_POOL"],
                "contract_address": "0x66017D22b0f8556afDd19FC67041899Eb65a21bb",
                "image": "cryptotracker/logos/liquity_stability_pool.png",
            },
            {
                "type": POOL_TYPES["BORROWING"],
                "contract_address": None,
                "image": "cryptotracker/logos/liquity_borrow.png",
            },
        ],
    },
    "LQTY_V2": {
        "name": "Liquity v2",
        "image": "cryptotracker/logos/liquity_v2.png",
        NETWORKS["ETHEREUM"]["name"]: [
            {
                "type": POOL_TYPES["BORROWING"],
                "contract_address": None,
                "image": "cryptotracker/logos/liquity_borrow_v2.png",
            },
            {
                "type": POOL_TYPES["STAKING"],
                "contract_address": "0x807def5e7d057df05c796f4bc75c3fe82bd6eee1",
                "image": "cryptotracker/logos/liquity_staking_v2.png",
            },
            {
                "type": POOL_TYPES["STABILITY_POOL"],
                "contract_address": "0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf",
                "image": "cryptotracker/logos/liquity_stability_pool_weth.png",
                "description": "WETH",
            },
            {
                "type": POOL_TYPES["STABILITY_POOL"],
                "contract_address": "0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b",
                "image": "cryptotracker/logos/liquity_stability_pool_lido.png",
                "description": "wstETH",
            },
            {
                "type": POOL_TYPES["STABILITY_POOL"],
                "contract_address": "0xd442e41019b7f5c4dd78f50dc03726c446148695",
                "image": "cryptotracker/logos/liquity_stability_pool_reth.png",
                "description": "rETH",
            },
        ],
    },
    "AAVE_V3": {
        "name": "Aave v3",
        "image": "cryptotracker/logos/aave.png",
        NETWORKS["ETHEREUM"]["name"]: [
            {
                "type": POOL_TYPES["LENDING"],
                "contract_address": "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e",
            },
        ],
        NETWORKS["ARBITRUM"]["name"]: [
            {
                "type": POOL_TYPES["LENDING"],
                "contract_address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
            },
        ],
        NETWORKS["AVALANCHE"]["name"]: [
            {
                "type": POOL_TYPES["LENDING"],
                "contract_address": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
            },
        ],
        NETWORKS["GNOSIS"]["name"]: [
            {
                "type": POOL_TYPES["LENDING"],
                "contract_address": "0x36616cf17557639614c1cdDb356b1B83fc0B2132",
            },
        ],
        NETWORKS["BASE"]["name"]: [
            {
                "type": POOL_TYPES["LENDING"],
                "contract_address": "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D",
            },
        ],
    },
    "UNI_V3": {
        "name": "Uniswap v3",
        "image": "cryptotracker/logos/uniswap.png",
        NETWORKS["ETHEREUM"]["name"]: [
            {
                "type": POOL_TYPES["AMM"],
                "contract_address": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
            },
        ],
    },
}

TOKENS: Dict[str, Any] = {
    "ETH": {
        "name": "ethereum",
        "symbol": "ETH",
        "image": "cryptotracker/logos/ethereum.png",
        "token_address": {
            "Ethereum": "NativeToken",
            "Arbitrum": "NativeToken",
            "Base": "NativeToken",
        },
    },
    "GNO": {
        "name": "gnosis",
        "symbol": "GNO",
        "image": "cryptotracker/logos/gnosis.png",
        "token_address": {
            "Gnosis Chain": "NativeToken",
        },
    },
    "AVAX": {
        "name": "avalanche-2",
        "symbol": "AVAX",
        "image": "cryptotracker/logos/avalanche.png",
        "token_address": {
            "Avalanche": "NativeToken",
        },
    },
    "LQTY": {
        "name": "liquity",
        "symbol": "LQTY",
        "image": "cryptotracker/logos/liquity.png",
        "token_address": {
            "Ethereum": "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D",
            "Avalanche": None,
            "Arbitrum": "0xfb9e5d956d889d91a82737b9bfcdac1dce3e1449",
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "SSV": {
        "name": "ssv-network",
        "symbol": "SSV",
        "image": "cryptotracker/logos/ssv.png",
        "token_address": {
            "Ethereum": "0x9D65fF81a3c488d585bBfb0Bfe3c7707c7917f54",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "BAL": {
        "name": "balancer",
        "symbol": "BAL",
        "image": "cryptotracker/logos/bal.png",
        "token_address": {
            "Ethereum": "0xba100000625a3754423978a60c9317c58a424e3d",
            "Avalanche": "0xe15bcb9e0ea69e6ab9fa080c4c4a5632896298c3",
            "Arbitrum": "0x040d1edc9569d4bab2d15287dc5a4f10f56a56b8",
            "Gnosis Chain": "0x7ef541e2a22058048904fe5744f9c7e4c57af717",
            "Base": "0x4158734d47fc9692176b5085e0f52ee0da5d47f1",
        },
    },
    "LUSD": {
        "name": "liquity-usd",
        "symbol": "LUSD",
        "image": "cryptotracker/logos/lusd.png",
        "token_address": {
            "Ethereum": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
            "Avalanche": None,
            "Arbitrum": "0x93b346b6bc2548da6a1e7d98e9a421b42541425b",
            "Gnosis Chain": None,
            "Base": "0x368181499736d0c0cc614dbb145e2ec1ac86b8c6",
        },
    },
    "SAFE": {
        "name": "safe",
        "symbol": "SAFE",
        "image": "cryptotracker/logos/safe.png",
        "token_address": {
            "Ethereum": "0x5afe3855358e112b5647b952709e6165e1c1eeee",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": "0x4d18815d14fe5c3304e87b3fa18318baa5c23820",
            "Base": None,
        },
    },
    "ARB": {
        "name": "arbitrum",
        "symbol": "ARB",
        "image": "cryptotracker/logos/arbitrum.png",
        "token_address": {
            "Ethereum": "0xb50721bcf8d664c30412cfbc6cf7a15145234ad1",
            "Avalanche": None,
            "Arbitrum": "0x912ce59144191c1204e64559fe8253a0e49e6548",
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "BOLD": {
        "name": "liquity-bold-2",
        "symbol": "BOLD",
        "image": "cryptotracker/logos/bold.png",
        "token_address": {
            "Ethereum": "0x6440f144b7e50D6a8439336510312d2F54beB01D",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "WETH": {
        "name": "weth",
        "symbol": "WETH",
        "image": "cryptotracker/logos/WETH.png",
        "token_address": {
            "Ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "Avalanche": None,
            "Arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "wstETH": {
        "name": "wrapped-steth",
        "symbol": "wstETH",
        "image": "cryptotracker/logos/wstETH.png",
        "token_address": {
            "Ethereum": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "rETH": {
        "name": "rocket-pool-eth",
        "symbol": "rETH",
        "image": "cryptotracker/logos/rETH.png",
        "token_address": {
            "Ethereum": "0xae78736cd615f374d3085123a210448e74fc6393",
            "Avalanche": None,
            "Arbitrum": None,
            "Gnosis Chain": None,
            "Base": None,
        },
    },
    "USDC": {
        "name": "usd-coin",
        "symbol": "USDC",
        "image": "cryptotracker/logos/USDC.png",
        "token_address": {
            "Ethereum": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "Avalanche": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
            "Arbitrum": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
            "Gnosis Chain": None,
            "Base": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        },
    },
}
