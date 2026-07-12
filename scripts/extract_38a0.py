def extract(file_path, out_path, target=0x38A0):
    with open(file_path) as f:
        for line in f:
            if line.startswith('>'): continue
            parts = line.split()
            if not parts or not parts[0].startswith('38'):
                continue
            try:
                addr = int(parts[0].rstrip(':'), 16)
            except ValueError:
                continue
            if addr == (target // 8) * 8:
                # print line and the next line (to cover 16 words)
                print(f"{file_path}: {line.strip()}")
                # Inconclusive, but this script just prints the line.
