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
