import glob

trace_files = glob.glob(r'C:/Users/vrock/Documents/Swords and Serpents/traces/**/*.txt', recursive=True)

keywords = ['door', 'connect', 'adjacent', 'next_room', 'room_num', 'level_map', 'dungeon_map']
for f in trace_files:
    try:
        with open(f, 'r', encoding='utf-8', errors='replace') as fp:
            content = fp.read()
        for kw in keywords:
            if kw.lower() in content.lower():
                print(f + ': contains "' + kw + '"')
                break
    except:
        pass