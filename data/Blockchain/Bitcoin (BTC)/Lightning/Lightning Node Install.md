---
title: Lightning Node Install
updated: 2024-07-10 17:29:07Z
created: 2024-07-10 16:19:09Z
latitude: 32.96595660
longitude: -97.68363840
altitude: 0.0000
tags:
  - lnd
  - todo
---

# Start in the directory with lnd installed (E:\Bitcoin Node\Lightning Network)

### open cmd
`lnd --configfile="E:\Bitcoin Node\Lightning Network\lnd-data\lnd.conf`

### open another cmd window
`lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\data\chain\bitcoin\mainnet\admin.macaroon" unlock`

Input your wallet unlock password and that’s it you should be up and running
* * *

## other useful commands

#### node info
In the second cmd window, type:
`lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\chain\bitcoin\mainnet\admin.macaroon" getinfo`

#### generate new address to receive BTC:
`lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\data\chain\bitcoin\mainnet\admin.macaroon" newaddress p2wkh`

Addresses Used:
1. Bc1q2kcsn2e2tv53zj504jac90knhhppjaxxn8kam4

#### Check balance:
lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\chain\bitcoin\mainnet\admin.macaroon" walletbalance

#### Pending channels:
lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\chain\bitcoin\mainnet\admin.macaroon" pendingchannels

#### Connect to peer: 
`lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\chain\bitcoin\mainnet\admin.macaroon" connect somealphanumericalvalue@ip:host`

#### open channels:
lncli --macaroonpath="E:\Bitcoin Node\Lightning Network\lnd-data\chain\bitcoin\mainnet\admin.macaroon" openchannel somealphanumericalvalue@ip:host [satoshis]

* hard to find nodes to connect with, most require anywhere between 20,000 - 100,0000 sats
* * *
### TODO: 
- [ ] send more BTC to open more channels
- [ ] open a channel with Kraken
- [ ] 02f1a8c87607f415c8f22c00593002775941dea48869ce23096af27b0cfdcc0b69@52.13.118.208:9735

