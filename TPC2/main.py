import sys

def parse_csv(content):
    field = ""
    rows = []
    current = []
    quote = False
    
    for char in content:
        if char == '\n' and not quote:
            current.append(field)
            rows.append(current)
            field = ""
            current = []
        elif char == ';' and not quote:
            current.append(field)
            field = ""
        elif char == '"':
            quote = not quote
        else:
            field += char
    
    if field:
        current.append(field)
    if current:
        rows.append(current)
    
    return rows[1:]

def sort_composers(data):
    return sorted(set(row[4] for row in data))

def organize_by_period(data):
    org = {}
    
    for row in data:
        period = row[3]
        org[period] = org.get(period, 0) + 1
    
    return org

def titles_by_period(data):
    titles_by_period = {}
    
    for row in data:
        period = row[3]
        title = row[0]
        titles_by_period.setdefault(period, []).append(title)
    
    for period in titles_by_period:
        titles_by_period[period].sort()
    
    return titles_by_period

def main():
    if len(sys.argv) == 2:
        file = sys.argv[1]
    else:
        file = "obras.csv"

    with open(file, encoding="utf-8") as f:
        content = f.read()

    data = parse_csv(content)

    composers = sort_composers(data)
    org = organize_by_period(data)
    titles = titles_by_period(data)
    
    print("RESULTADOS\n")
    print("=== Compositores Ordenados Alfabeticamente ===\n")
    for composer in composers:
        print(composer)

    print("\n")

    print("=== Distribuição por Período ===\n")
    for period, count in org.items():
        print(f"{period}: {count}")

    print("\n")

    print("=== Títulos por Período ===")
    for period, titles in titles.items():
        print("\n")
        print(f"{period}:")
        for title in titles:
            print(f"  {title}")

if __name__ == "__main__":
    main()