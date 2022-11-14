# model-merge

## patch

apply diffs between emultated_{asis,tobe} to original_asis

usage and example:

```
model_merge$ python merge.py patch ../tests/testdata/mddo-ospf/original_asis.json ../tests/testdata/mddo-ospf/emulated_asis.json ../tests/testdata/mddo-ospf/emulated_tobe.json > ../tests/testdata/mddo-ospf/patched_original_asis.json
model_merge$ diff -du ../tests/testdata/mddo-ospf/{,patched_}original_asis.json
@@ -196,11 +187,11 @@
                 "mddo-topology:ospf-area-termination-point-attributes": {
                   "network-type": "BROADCAST",
                   "priority": 10,
-                  "metric": 1,
+                  "metric": 4,
                   "passive": false,
                   "timer": {
                     "hello-interval": 10,
-                    "dead-interval": 40,
+                    "dead-interval": 45,
                     "retransmission-interval": 5
                   },
                   "neighbor": [
```


## config

generate candidate config to apply avobe diffs

usage and example:
```
model_merge$ python merge.py config ../tests/testdata/mddo-ospf/original_asis.json ../tests/testdata/mddo-ospf/emulated_asis.json ../tests/testdata/mddo-ospf/emulated_tobe.json
[
  {
    "node-id": "rt2",
    "config": "set protocol ospf area 0.0.0.0 interface eth1.0 metric 4"
  },
  {
    "node-id": "rt2",
    "config": "set protocol ospf area 0.0.0.0 interface eth1.0 dead-interval 45"
  }
]
```


# how to dev

topology.json follows this scheme:

```
{
  "ietf-network:networks": {
    "network": [
      {
        "network-id": "bra",
        "node": [
          {
            "node-id": "brabra",
            "ietf-network-topology:termination-point": [
              {
                "tp-id": "brabrabra",
                "mddo-topology:ospf-area-termination-point-attributes": {
                  "some-attribute-key": "some-attribute-value"
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

patch function scans all leafs of original_asis and replaces those value when the value of emulated_tobe is different from emulated_asis.

config function generates raw config to apply avobe diff by following three steps.

1. calculate diff object
2. reverse step.1 diff object to traverse from each diff
3. apply template at each diff

each steps intermidiate object sample is ...

1. diff object

```
{
  "ietf-network:networks": {
    "network": [
      {
        "node": [
          {
            "ietf-network-topology:termination-point": [
              {
                "mddo-topology:ospf-area-termination-point-attributes": {
                  "metric": 4,
                  "timer": {
                    "dead-interval": 45
                  }
                },
                "tp-id": "eth1.0"
              }
            ],
            "node-id": "rt2"
          }
        ],
        "network-id": "ospf_area0"
      }
    ]
  }
}
```

2. reversed diff object

```
[
  {
    "metric": 4,
    "__original": 1,
    "__parent": {
      "mddo-topology:ospf-area-termination-point-attributes": {
        "metric": 4,
        "timer": {
          "dead-interval": 45
        }
      },
      "tp-id": "eth1.0",
      "__original": {
        "network-type": "BROADCAST",
        "priority": 10,
        "metric": 1,
        "passive": false,
        "timer": {
          "hello-interval": 10,
          "dead-interval": 40,
          "retransmission-interval": 5
        },
        "neighbor": [
          {
            "router-id": "172.16.0.1",
            "ip-address": "10.0.0.1/30"
          }
        ]
      },
      "__parent": {
        "ietf-network-topology:termination-point": [
          {
            "mddo-topology:ospf-area-termination-point-attributes": {
              "metric": 4,
              "timer": {
                "dead-interval": 45
              }
            },
            "tp-id": "eth1.0"
          }
        ],
        "node-id": "rt2",
        "__original": [ ... ],
        "__parent": { ... }
      }
    }
  },
  {
    "dead-interval": 45,
    "__original": 40,
    "__parent": {
      "metric": 4,
      "timer": {
        "dead-interval": 45
      },
      "__original": {
        "hello-interval": 10,
        "dead-interval": 40,
        "retransmission-interval": 5
      },
      "__parent": {
        "mddo-topology:ospf-area-termination-point-attributes": {
          "metric": 4,
          "timer": {
            "dead-interval": 45
          }
        },
        "tp-id": "eth1.0",
        "__original": [ ... ],
        "__parent": { ... }
      }
    }
  }
]
```
