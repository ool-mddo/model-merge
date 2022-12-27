import json
import sys
from jinja2 import Environment, FileSystemLoader
from os import path


def patch(original_asis, emulated_asis, emulated_tobe):
    def _list_worker(oa_item, ea, et):
        ea_item = None
        et_item = None
        # TODO: check other ids
        for k in ["network-id", "node-id", "tp-id", "router-id"]:
            if k in oa_item:
                for e in ea:
                    if e[k] == oa_item[k]:
                        ea_item = e
                for e in et:
                    if e[k] == oa_item[k]:
                        et_item = e
        if ea_item is None or et_item is None:
            return oa_item
        else:
            return _worker(oa_item, ea_item, et_item)

    def _worker(oa, ea, et):
        if isinstance(oa, dict):
            new_var = {}
            for k in oa.keys():
                new_var[k] = _worker(oa[k], ea[k], et[k])
        elif isinstance(oa, list):
            new_var = [_list_worker(oa_item, ea, et) for oa_item in oa]
        else:
            if ea == et:
                new_var = oa
            else:
                new_var = et
        return new_var

    return _worker(original_asis, emulated_asis, emulated_tobe)


def get_diff(original_asis, patched_original_asis):
    def _list_worker(oa_item, poa):
        poa_item = None
        poa_key = None
        # TODO: check other ids
        for k in ["network-id", "node-id", "tp-id", "router-id"]:
            if k in oa_item:
                for p in poa:
                    if p[k] == oa_item[k]:
                        poa_item = p
                        poa_key = k
        if poa_item is None:
            return (None, False), None, None
        else:
            return _worker(oa_item, poa_item), poa_key, oa_item[poa_key]

    def _worker(oa, poa):
        if isinstance(oa, dict):
            new_var = {}
            for k in oa.keys():
                new_var[k], res = _worker(oa[k], poa[k])
                if not (res):
                    new_var.pop(k)
            if len(new_var) != 0:
                return new_var, True
        elif isinstance(oa, list):
            new_var = list(
                map(
                    lambda x: x[0][0] | {x[1]: x[2]},
                    filter(
                        lambda x: x[0][1],
                        [_list_worker(oa_item, poa) for oa_item in oa],
                    ),
                )
            )
            if len(new_var) != 0:
                return new_var, True
        else:
            if oa != poa:
                new_var = poa
                return new_var, True
        return None, False

    return _worker(original_asis, patched_original_asis)[0]


def calc_reversed_diffs(diff, original_asis):
    def _list_worker(diff_item, oa, parent):
        oa_item = None
        oa_key = None
        # TODO: check other ids
        for k in ["network-id", "node-id", "tp-id", "router-id"]:
            if k in diff_item:
                for o in oa:
                    if o[k] == diff_item[k]:
                        oa_item = o
                        oa_key = k
        if oa_item is None:
            raise Exception("diff is not subset of original")
        else:
            return _worker(diff_item, oa_item, parent)

    def _worker(diff, oa, parent):
        prod = []
        if isinstance(diff, dict):
            for k, v in diff.items():
                if k in ["network-id", "node-id", "tp-id", "router-id"]:
                    # skip "key" value
                    return prod, None
                sub_prod, value = _worker(
                    v, oa[k], diff | {"__original": oa[k], "__parent": parent}
                )
                prod.extend(sub_prod)
                if value is not None:
                    prod.append({k: value, "__original": oa[k], "__parent": parent})
            return prod, None
            # return list(map(lambda kv: {kv[0]: kv[1], "__original": oa, "__parent": parent}, diff.items()))
            return list(
                map(
                    lambda kv: {
                        kv[0]: _worker(kv[1], oa[kv[0]], diff),
                        "__original": "oa",
                        "__parent": parent,
                    },
                    diff.items(),
                )
            )
        elif isinstance(diff, list):
            for item in diff:
                sub_prod, value = _list_worker(item, oa, parent)
                prod.extend(sub_prod)
                # res2 must be None, because of "item" must be hash
            return prod, None
        else:
            return prod, diff

    return _worker(diff, original_asis, None)[0]


def get_node_and_template_name(reversed_diff_item, original_asis):
    def _get_node_id(rdiff):
        # python cannot do lazy-eval, so cannot write this
        # return rdiff.get("node-id", _get_node_id(rdiff["__parent"]))
        if "node-id" in rdiff:
            return rdiff["node-id"]
        else:
            return _get_node_id(rdiff["__parent"])

    def _get_os_type(original_asis, nodename):
        L1topo = next(
            filter(
                lambda x: x["network-id"] == "layer1",
                original_asis["ietf-network:networks"]["network"],
            )
        )
        return next(filter(lambda x: x["node-id"] == nodename, L1topo["node"]))[
            "mddo-topology:l1-node-attributes"
        ]["os-type"]

    def _get_key_names(rdiff, child={}):
        STOP_KEYS = ["mddo-topology:ospf-area-termination-point-attributes"]
        if not child:
            # top-level (most detailed) diff
            # must be 1 key
            key = list(rdiff.keys() - ["__original", "__parent"])[0]
            return _get_key_names(rdiff["__parent"], rdiff) + [key]
        else:
            contains = child.keys() - ["__original", "__parent"]
            key = next(
                filter(
                    lambda k: isinstance(rdiff[k], dict) and rdiff[k].keys() & contains,
                    rdiff.keys(),
                )
            )
            if key in STOP_KEYS:
                return [key]
            else:
                return _get_key_names(rdiff["__parent"], rdiff) + [key]

    node_id = _get_node_id(reversed_diff_item)
    template_name = []
    template_name += map(lambda x: x.split(":")[-1], _get_key_names(reversed_diff_item))
    template_name += [_get_os_type(original_asis, node_id)]
    template_name += ["j2"]

    return node_id, ".".join(template_name)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "usage: merge.py COMMAND original_asis.json emulated_asis.json emulated_tobe.json"
        )
        print("COMMAND: patch, config")
        exit(1)
    _, command, original_asis_file, emulated_asis_file, emulated_tobe_file = sys.argv
    original_asis, emulated_asis, emulated_tobe = map(
        lambda filename: json.load(open(filename)),
        [original_asis_file, emulated_asis_file, emulated_tobe_file],
    )

    patched_original_asis = patch(original_asis, emulated_asis, emulated_tobe)

    if command == "patch":
        print(json.dumps(patched_original_asis, indent=2))
        exit(0)
    if command == "config":
        prod = []
        j2env = Environment(
            loader=FileSystemLoader(path.join(path.dirname(__file__), "../templates")),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        diff = get_diff(original_asis, patched_original_asis)
        rdiffs = calc_reversed_diffs(diff, original_asis)
        for rdiff in rdiffs:
            node_id, template_name = get_node_and_template_name(rdiff, original_asis)
            prod.append(
                {
                    "node-id": node_id,
                    "config": j2env.get_template(template_name).render(rdiff=rdiff),
                }
            )
        print(json.dumps(prod, indent=2))
        exit(0)
