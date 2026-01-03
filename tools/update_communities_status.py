import json
import re
import datetime
from pathlib import Path
from dateutil.parser import parse
from datetime import timezone

def load_events(history_path, current_path):
    events = []

    # Load History
    if history_path.exists():
        with open(history_path, 'r') as f:
            try:
                events.extend(json.load(f))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {history_path}")

    # Load Current (Generated)
    if current_path.exists():
        with open(current_path, 'r') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    events.extend(data)
                elif isinstance(data, dict) and 'events' in data:
                     events.extend(data['events'])
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {current_path}")

    return events

def get_processed_events(events):
    processed_events = []

    for e in events:
        start_str = e.get('dtstart')
        if not start_str:
            continue

        try:
            dt = parse(start_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                 dt = dt.astimezone(timezone.utc)

            # Extract state - prefer normalized state name
            state = e.get("state")
            if not state:
                # Fallback to city or 'Online' if applicable
                loc = e.get("location", "")
                if loc == "Online" or "online" in loc.lower():
                    state = "Online"
                else:
                     state = e.get("city", "")

            processed_events.append({
                "organizer": e.get("organizer", "").strip(),
                "url": e.get("url", ""),
                "source": e.get("source", ""),
                "dtstart": dt,
                "state": state.strip() if state else ""
            })
        except Exception:
            pass

    return processed_events

def get_status_emoji(last_date):
    if not last_date:
        return "🔴" # Inactive

    now = datetime.datetime.now(timezone.utc)

    # Active if future event exists
    if last_date > now:
        return "🟢"

    delta = now - last_date
    months = delta.days / 30.0

    if months < 12:
        return "🟢"
    elif months < 18:
        return "⏸️"
    else:
        return "🔴"

def get_community_stats(name, link, processed_events):
    max_date = None
    states = set()

    # Normalize name for comparison
    target_name = name.lower().strip()

    # Clean link for comparison
    link_clean = link.lower().strip().rstrip('/')
    link_clean_noprotocol = re.sub(r'^https?://(www\.)?', '', link_clean)

    for e in processed_events:
        is_match = False

        # 1. Match by Organizer Name
        if e['organizer'] and e['organizer'].lower() == target_name:
            is_match = True

        # 2. Match by URL/Source containment
        if not is_match:
            event_url = e['url'].lower() if e['url'] else ""
            source_url = e['source'].lower() if e['source'] else ""

            if link_clean_noprotocol and (link_clean_noprotocol in event_url or link_clean_noprotocol in source_url):
                is_match = True

        if is_match:
            if max_date is None or e['dtstart'] > max_date:
                max_date = e['dtstart']

            if e['state']:
                # Clean up specific cases
                s = e['state']
                if s == "MX-CMX": s = "Ciudad de México"
                if s == "MX-NLE": s = "Nuevo León"
                if s == "MX-JAL": s = "Jalisco"
                if s == "MX-YUC": s = "Yucatán"
                if s == "MX-PUE": s = "Puebla"
                if s == "MX-QUE": s = "Querétaro"
                if s == "MX-QRO": s = "Querétaro"
                if s == "MX-AGS": s = "Aguascalientes"
                if s == "MX-MEX": s = "Estado de México"
                if s == "MX-MÉX": s = "Estado de México"
                if s == "MX-TLA": s = "Tlaxcala"

                # Exclude internal codes if any remain or generic empty
                if len(s) > 2:
                    states.add(s)
            elif name in ["Claude Users Group", "Mexico Tech Week"] or e.get("location") == "Online": # Specific fallback logic
                 states.add("Online")

    return max_date, states

def update_markdown(md_path, processed_events):
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        return

    with open(md_path, 'r') as f:
        lines = f.readlines()

    # Extract existing communities
    communities = []
    seen = set()

    for line in lines:
        if not line.strip().startswith('|'):
            continue
        if "Comunidad" in line and "Descripción" in line:
            continue
        if ":---" in line:
            continue

        # Split by pipe
        parts = [p.strip() for p in line.strip().split('|') if p.strip()]
        if len(parts) >= 2:
            col_name = parts[0]
            col_desc = parts[1] # Take description as second column

            # Extract Link and Name from col_name
            # Matches: 🟢 [**Name**](Link) or [**Name**](Link)
            match = re.search(r'\[\*\*(.*?)\*\*\]\((.*?)\)', col_name)
            if match:
                name = match.group(1)
                link = match.group(2)

                key = (name, link)
                if key not in seen:
                    communities.append({
                        "name": name,
                        "link": link,
                        "description": col_desc
                    })
                    seen.add(key)

    # Calculate stats for each community
    enriched_communities = []
    for c in communities:
        last_date, states = get_community_stats(c['name'], c['link'], processed_events)
        status = get_status_emoji(last_date)

        # Sort states list
        states_list = sorted(list(states))
        states_str = ", ".join(states_list) if states_list else "Online" # Default if no state found

        enriched_communities.append({
            "name": c['name'],
            "link": c['link'],
            "description": c['description'],
            "status": status,
            "states": states_str,
            "sort_key": c['name'].lower()
        })

    # Sort
    enriched_communities.sort(key=lambda x: x['sort_key'])

    # Regenerate File
    with open(md_path, 'w') as f:
        f.write("# Comunidades Tech en México\n\n")
        f.write("Esta es la lista completa de comunidades integradas en el agregador de **Cron-Quiles**, organizadas alfabéticamente. Estas comunidades organizan regularmente eventos técnicos, workshops y espacios de networking.\n\n")
        f.write("> [!NOTE]\n")
        f.write("> Las comunidades están clasificadas según su actividad reciente:\n")
        f.write("> * 🟢 **Activo**: Eventos en los últimos 12 meses.\n")
        f.write("> * ⏸️ **En Pausa**: Eventos entre 12 y 18 meses.\n")
        f.write("> * 🔴 **Inactivo**: Más de 18 meses sin eventos.\n\n")

        f.write("| Comunidad | Descripción | Estados |\n")
        f.write("| :--- | :--- | :--- |\n")

        for c in enriched_communities:
            row = f"| {c['status']} [**{c['name']}**]({c['link']}) | {c['description']} | {c['states']} |\n"
            f.write(row)

    print(f"Updated {md_path} with flattened table")

def main():
    root = Path(__file__).parent.parent
    history_file = root / "data/history.json"
    current_file = root / "gh-pages/data/cronquiles-mexico.json"
    md_file = root / "docs/COMMUNITIES.md"

    print("Loading events...")
    events = load_events(history_file, current_file)
    print(f"Loaded {len(events)} events")

    processed_events = get_processed_events(events)

    print("Updating markdown...")
    update_markdown(md_file, processed_events)

if __name__ == "__main__":
    main()
