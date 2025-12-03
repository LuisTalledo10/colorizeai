import h5py, os, json
files = ['best_model_UNet_RMSprop.h5','best_model_UNet_Mejorada.h5','best_model_UNet_Basica.h5']
for f in files:
    print('---', f, '---')
    if not os.path.exists(f):
        print('MISSING')
        continue
    try:
        with h5py.File(f,'r') as h:
            for k in ['keras_version','backend','model_config']:
                if k in h.attrs:
                    print(k, ':', h.attrs[k])
            print('Top keys:', list(h.keys())[:20])
            if 'model_config' in h.attrs:
                try:
                    mc_raw = h.attrs['model_config']
                    mc = json.loads(mc_raw.decode('utf-8')) if isinstance(mc_raw, (bytes,bytearray)) else json.loads(mc_raw)
                    def find_input(cfg):
                        if isinstance(cfg, dict):
                            if cfg.get('class_name')=='InputLayer' or cfg.get('config',{}).get('name','').lower().startswith('input'):
                                return cfg
                            for v in cfg.values():
                                r = find_input(v)
                                if r: return r
                        elif isinstance(cfg, list):
                            for item in cfg:
                                r = find_input(item)
                                if r: return r
                        return None
                    inp = find_input(mc)
                    print('Found input in model_config:', bool(inp))
                    if inp:
                        snippet = json.dumps(inp, indent=2)
                        print('Input snippet (first 800 chars):')
                        print(snippet[:800])
                except Exception as e:
                    print('Could not parse model_config:', e)
    except Exception as e:
        print('h5 read error:', e)
print('done')
