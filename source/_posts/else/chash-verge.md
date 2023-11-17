---
title: clash-verge
date: 2023-11-17 10:09:31
tags:
---

clash-verge规则配置。

参考链接：

- [clash-tutorials/教程合集/分享篇/分享自己使用 Clash Verge 搭配 rule-set 方案的一套配置.md at main · DustinWin/clash-tutorials (github.com)](https://github.com/DustinWin/clash-tutorials/blob/main/教程合集/分享篇/分享自己使用 Clash Verge 搭配 rule-set 方案的一套配置.md)



profile中新建merge类型的配置，将以下内容粘贴到其中。之后开启tun mode和service mode即可。

```yaml
proxy-providers:
  🛫 我的机场:
    type: http
    # 修改为你的 Clash 订阅链接
    url: "https://example.com/xxx/xxx&flag=clash"
    path: ./proxies/airport.yaml
    interval: 43200
    filter: "香港|台湾|日本|韩国|新加坡|美国"
    health-check:
      enable: true
      url: "https://www.gstatic.com/generate_204"
      interval: 600

mode: rule
ipv6: true
log-level: silent
allow-lan: true
mixed-port: 19925
unified-delay: false
tcp-concurrent: true
external-controller-tls: 127.0.0.1:9090
find-process-mode: strict
global-client-fingerprint: chrome
profile: {store-selected: true, store-fake-ip: true}

tun:
  enable: true
  stack: system
  dns-hijack: ['any:53']
  auto-route: true
  auto-detect-interface: true
  strict-route: true

proxy-groups:
  - {name: 🚀 节点选择, type: select, proxies: [🇭🇰 香港节点, 🇹🇼 台湾节点, 🇯🇵 日本节点, 🇰🇷 韩国节点, 🇸🇬 新加坡节点, 🇺🇸 美国节点]}

  - {name: 📈 网络测试, type: select, proxies: [🎯 全球直连, 🇭🇰 香港节点, 🇹🇼 台湾节点, 🇯🇵 日本节点, 🇰🇷 韩国节点, 🇸🇬 新加坡节点, 🇺🇸 美国节点]}

  - {name: 🐟 漏网之鱼, type: select, proxies: [🚀 节点选择, 🎯 全球直连], disable-udp: true}

  - {name: ⚡ 直连域名, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: 🪜 代理域名, type: select, proxies: [🚀 节点选择, 🎯 全球直连], disable-udp: true}

  - {name: 🎮 国区游戏, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: Ⓜ️ Microsoft 中国, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: 🗽 Google 中国, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: 🍎 Apple 中国, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: 🇨🇳 国内 IP, type: select, proxies: [🎯 全球直连, 🚀 节点选择]}

  - {name: ✈️ Telegram, type: select, proxies: [🚀 节点选择]}

  - {name: 🖥️ 直连软件, type: select, proxies: [🎯 全球直连]}

  - {name: 🏠 私有网络, type: select, proxies: [🎯 全球直连]}

  - {name: ⛔️ 广告域名, type: select, proxies: [🛑 全球拦截]}

  - {name: 🎯 全球直连, type: select, proxies: [DIRECT]}

  - {name: 🛑 全球拦截, type: select, proxies: [REJECT]}

  # 采用节点负载均衡策略，优点是更稳定，速度可能有提升；推荐在节点复用比较多的情况下使用
  - {name: 🇭🇰 香港节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "香港"}

  - {name: 🇹🇼 台湾节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "台湾"}

  - {name: 🇯🇵 日本节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "日本"}

  - {name: 🇰🇷 韩国节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "韩国"}

  - {name: 🇸🇬 新加坡节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "新加坡"}

  - {name: 🇺🇸 美国节点, type: load-balance, strategy: consistent-hashing, lazy: true, use: [🛫 我的机场], filter: "美国"}

rule-providers:
  ads:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/ads.yaml"
    path: ./ruleset/ads.yaml
    interval: 86400

  private:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/private.yaml"
    path: ./ruleset/private.yaml
    interval: 86400

  microsoft-cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/microsoft-cn.yaml"
    path: ./ruleset/microsoft-cn.yaml
    interval: 86400

  apple-cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/apple-cn.yaml"
    path: ./ruleset/apple-cn.yaml
    interval: 86400

  google-cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/google-cn.yaml"
    path: ./ruleset/google-cn.yaml
    interval: 86400

  games-cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/games-cn.yaml"
    path: ./ruleset/games-cn.yaml
    interval: 86400

  networktest:
    type: http
    behavior: classical
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/networktest.yaml"
    path: ./ruleset/networktest.yaml
    interval: 86400

  applications:
    type: http
    behavior: classical
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/applications.yaml"
    path: ./ruleset/applications.yaml
    interval: 86400

  proxy:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/proxy.yaml"
    path: ./ruleset/proxy.yaml
    interval: 86400

  cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/cn.yaml"
    path: ./ruleset/cn.yaml
    interval: 86400

  telegramip:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/telegramip.yaml"
    path: ./ruleset/telegramip.yaml
    interval: 86400

  privateip:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/privateip.yaml"
    path: ./ruleset/privateip.yaml
    interval: 86400

  cnip:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/DustinWin/clash-ruleset@release/cnip.yaml"
    path: ./ruleset/cnip.yaml
    interval: 86400

rules:
  - RULE-SET,ads,⛔️ 广告域名
  - RULE-SET,private,🏠 私有网络
  - RULE-SET,microsoft-cn,Ⓜ️ Microsoft 中国
  - RULE-SET,apple-cn,🍎 Apple 中国
  - RULE-SET,google-cn,🗽 Google 中国
  - RULE-SET,games-cn,🎮 国区游戏
  - RULE-SET,networktest,📈 网络测试
  - RULE-SET,applications,🖥️ 直连软件
  - RULE-SET,proxy,🪜 代理域名
  - RULE-SET,cn,⚡ 直连域名
  - RULE-SET,telegramip,✈️ Telegram
  - RULE-SET,privateip,🏠 私有网络,no-resolve
  - RULE-SET,cnip,🇨🇳 国内 IP
  - MATCH,🐟 漏网之鱼
```

