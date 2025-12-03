import h5py
import glob
import json
import sys

def inspect_file(path):
    info = {'file': path}
    try:
        f = h5py.File(path, 'r')
    except Exception as e:
        info['error'] = str(e)
        return info

    # Common attrs
    for attr in ['keras_version', 'backend']:
        if attr in f.attrs:
            info[attr] = f.attrs[attr].decode() if isinstance(f.attrs[attr], bytes) else f.attrs[attr]

    # Try to get model_config if present
    try:
        if 'model_config' in f.attrs:
            mc = f.attrs['model_config']
            info['model_config'] = mc.decode() if isinstance(mc, bytes) else str(mc)
    except Exception:
        pass

    # Inspect top-level groups for layer names / input shape hints
    try:
        groups = list(f.keys())
        info['top_groups'] = groups
    except Exception:
        info['top_groups'] = []

    # Look for layer configs under 'model_weights' or 'model'
    try:
        if 'model_weights' in f:
            lw = list(f['model_weights'].keys())
            info['model_weights_layers'] = lw[:20]
    except Exception:
        pass

    f.close()
    return info

def main():
    files = glob.glob('*.h5')
    if not files:
        print('NO_H5_FOUND')
        return
    results = []
    for p in files:
        results.append(inspect_file(p))
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
