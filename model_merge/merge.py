import json
import sys

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


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("usage: merge.py COMMAND original_asis.json emulated_asis.json emulated_tobe.json")
        print("COMMAND: patch, config")
        exit(1)
    _, command, original_asis_file, emulated_asis_file, emulated_tobe_file = sys.argv
    original_asis, emulated_asis, emulated_tobe = map(
        lambda filename: json.load(open(filename)),
        [original_asis_file, emulated_asis_file, emulated_tobe_file])

    patched_original_asis = patch(original_asis, emulated_asis, emulated_tobe)

    if command == "patch":
        print(json.dumps(patched_original_asis, indent=2))
        exit(0)
