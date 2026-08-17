#!/usr/bin/env python3

import re
import json
import time
import base64
import socket
from pathlib import Path
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]

OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

SOURCES = ROOT / "sources_sg.txt"

USER_AGENT = "FreeForYoung-SG-ULTRA-V3"

URI_RE = re.compile(
    r"(?:vless|vmess|trojan|ss)://[^\s]+",
    re.I
)


def download(url):
    try:
        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT
            }
        )

        with urlopen(req, timeout=15) as r:
            return r.read().decode(
                "utf-8",
                "ignore"
            )

    except Exception:
        return ""


def decode_b64(data):

    try:
        clean = data.strip()

        clean += "=" * (
            -len(clean) % 4
        )

        return base64.b64decode(
            clean
        ).decode(
            "utf-8",
            "ignore"
        )

    except Exception:
        return ""


def extract(text):

    result = []

    decoded = decode_b64(text)

    if "://" in decoded:
        text += "\n" + decoded


    for x in URI_RE.findall(text):

        x = x.strip()

        if x not in result:
            result.append(x)


    return result



def get_host(uri):

    try:
        part = uri.split("@")[1]

        host = part.split(":")[0]

        host = host.replace(
            "/",
            ""
        )

        return host

    except Exception:
        return None



def resolve(host):

    try:

        return socket.gethostbyname(
            host
        )

    except Exception:

        return None



def geo(ip):

    try:

        url = (
            "http://ip-api.com/json/"
            + ip
            +
            "?fields=status,country,countryCode,city"
        )

        data = json.loads(
            urlopen(
                url,
                timeout=5
            )
            .read()
            .decode()
        )

        return data

    except Exception:

        return {}



def main():

    print(
        "=== FreeForYoung SG ULTRA V3 ==="
    )

    nodes = []


    for line in SOURCES.read_text(
        encoding="utf-8"
    ).splitlines():

        if not line:
            continue

        if line.startswith("#"):
            continue


        print(
            "SOURCE:",
            line
        )


        data = download(line)

        found = extract(data)

        print(
            "FOUND:",
            len(found)
        )

        nodes.extend(found)



    nodes = list(
        dict.fromkeys(nodes)
    )


    print(
        "TOTAL:",
        len(nodes)
    )



    singapore = []

    checked = set()


    for node in nodes:


        host = get_host(node)


        if not host:
            continue


        ip = resolve(host)


        if not ip:
            continue



        if ip in checked:
            continue


        checked.add(ip)


        info = geo(ip)


        if (
            info.get("countryCode")
            ==
            "SG"
        ):


            singapore.append(
                {
                    "uri": node,
                    "ip": ip,
                    "city": info.get(
                        "city"
                    )
                }
            )


    print(
        "SINGAPORE:",
        len(singapore)
    )



    urls = [
        x["uri"]
        for x in singapore
    ]


    header = (
        "#profile-title: FreeForYoung SG ULTRA V3\n"
        "#announce: Singapore only\n"
        "#subscription-auto-update-enable: 1\n"
        "#subscriptions-sort-type: ping\n"
    )


    (
        OUT /
        "singapore.txt"
    ).write_text(
        header
        +
        "\n".join(urls),
        encoding="utf-8"
    )



    (
        OUT /
        "singapore-top10.txt"
    ).write_text(
        header
        +
        "\n".join(
            urls[:10]
        ),
        encoding="utf-8"
    )



    encoded = base64.b64encode(
        "\n".join(urls)
        .encode()
    ).decode()



    (
        OUT /
        "singapore-base64.txt"
    ).write_text(
        encoded,
        encoding="utf-8"
    )



    stats = {

        "version":
            "SG Ultra V3",

        "generated":
            int(time.time()),

        "raw_nodes":
            len(nodes),

        "singapore_nodes":
            len(singapore),

        "published":
            len(urls)

    }



    (
        OUT /
        "singapore-stats.json"
    ).write_text(
        json.dumps(
            stats,
            indent=2
        ),
        encoding="utf-8"
    )


    print(stats)



if __name__ == "__main__":
    main()
