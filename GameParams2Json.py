import struct
import zlib
import pickle
import json
import os
import threading

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

entities_dir = os.path.join(__location__, 'entities')
if not os.path.exists(entities_dir):
    os.mkdir(os.path.join(__location__, 'entities'))


class GPEncode(json.JSONEncoder):
    def default(self, o):
        _hasattr = hasattr(o, '__dict__')
        if _hasattr:
            t = o.__dict__
            for key in t:
                if isinstance(t[key], str):
                    try:
                        t[key].decode('utf8')
                    except AttributeError:
                        try:
                            t[key] = t[key].decode('MacCyrillic')
                        except AttributeError:
                            try:
                                t[key] = t[key].encode('hex')
                            except LookupError:
                                pass
            return o.__dict__


def get_entity_types(game_params):
    entity_types = []
    for key in game_params:
        entity_type = game_params[key]['typeinfo']['type']
        if entity_type not in entity_types:
            entity_types.append(entity_type)
    return entity_types


def entity_writer(entity_type, game_params):
    entities = []
    for key in game_params:
        entity = game_params[key]
        if entity_type == entity['typeinfo']['type']:
            entities.append(entity)
    write_to = os.path.join(entities_dir, entity_type + '.json')
    with open(write_to, 'w') as f:
        json.dump(entities, f, indent=4)
        f.close()
    print('Done writing: %s.json' % entity_type, end='\n')


def write_entities(entity_types, game_params):
    entity_threads = []
    for entity_type in entity_types:
        th = threading.Thread(target=entity_writer, args=(entity_type, game_params))
        th.start()
        entity_threads.append(th)

    for th in entity_threads:
        th.join()
    print("All writers done.")


if __name__ == "__main__":
    with open('GameParams.data', 'rb') as f:
        data = bytearray(f.read())
        f.close()
        data = struct.pack('B' * len(data), *data[::-1])
        data = zlib.decompress(data)
        data = pickle.loads(data, encoding='MacCyrillic')
        data = json.dumps(data, cls=GPEncode, sort_keys=True)
        data = json.loads(data)
        write_entities(get_entity_types(data), data)
