# ============================================================
# DIGITAL FOOTPRINT ANALYZER
# COMPLETE FLASK BACKEND
# ============================================================

from flask import Flask, render_template, request, jsonify
import requests
import socket
import ipaddress
import os
import re
import time
from datetime import datetime


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

APP_NAME = "Digital Footprint Analyzer"

REQUEST_TIMEOUT = 8

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "Chrome/151.0 Safari/537.36"
)


# ============================================================
# SOCIAL / PUBLIC PLATFORM DATABASE
# ============================================================

PLATFORMS = [
    {
        "name": "GitHub",
        "url": "https://github.com/{}"
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}"
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}"
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}/"
    },
    {
        "name": "Twitch",
        "url": "https://www.twitch.tv/{}"
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{}"
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{}"
    },
    {
        "name": "CodePen",
        "url": "https://codepen.io/{}"
    },
    {
        "name": "HackerNews",
        "url": "https://news.ycombinator.com/user?id={}"
    },
    {
        "name": "Keybase",
        "url": "https://keybase.io/{}"
    }
]


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# HEALTH / STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def api_status():

    return jsonify({
        "success": True,
        "status": "ONLINE",
        "service": APP_NAME,
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": "Backend is connected successfully."
    })


# ============================================================
# USERNAME / DIGITAL FOOTPRINT SCANNER
# ============================================================

@app.route("/api/scan", methods=["POST"])
def scan():

    try:

        data = request.get_json(silent=True) or {}

        username = str(
            data.get("username", "")
        ).strip()

        # ------------------------------
        # INPUT VALIDATION
        # ------------------------------

        if not username:

            return jsonify({
                "success": False,
                "message": "Username is required."
            }), 400

        if len(username) > 50:

            return jsonify({
                "success": False,
                "message": "Username must be 50 characters or less."
            }), 400

        # Basic username validation
        if not re.match(
            r"^[A-Za-z0-9_.-]+$",
            username
        ):

            return jsonify({
                "success": False,
                "message": (
                    "Username contains unsupported characters."
                )
            }), 400


        # ------------------------------
        # START SCAN
        # ------------------------------

        print()
        print("=" * 55)
        print("USERNAME SCAN STARTED")
        print("Target:", username)
        print("=" * 55)

        results = []

        for platform in PLATFORMS:

            platform_name = platform["name"]
            profile_url = platform["url"].format(username)

            print(
                f"[SCAN] {platform_name} -> {profile_url}"
            )

            try:

                response = requests.get(
                    profile_url,
                    timeout=REQUEST_TIMEOUT,
                    headers={
                        "User-Agent": USER_AGENT
                    },
                    allow_redirects=True
                )

                code = response.status_code

                # ------------------------------
                # RESPONSE CLASSIFICATION
                # ------------------------------

                if code == 200:

                    status = "FOUND"

                elif code in [401, 403, 429]:

                    status = "BLOCKED"

                elif code == 404:

                    status = "NOT FOUND"

                else:

                    status = "UNABLE"

            except requests.RequestException as error:

                print(
                    f"[ERROR] {platform_name}: {error}"
                )

                code = 0
                status = "UNABLE"


            results.append({
                "platform": platform_name,
                "status": status,
                "code": code,
                "url": profile_url
            })


        # ====================================================
        # CALCULATE SCAN STATISTICS
        # ====================================================

        total = len(results)

        found = sum(
            1
            for result in results
            if result["status"] == "FOUND"
        )

        blocked = sum(
            1
            for result in results
            if result["status"] == "BLOCKED"
        )

        not_found = sum(
            1
            for result in results
            if result["status"] == "NOT FOUND"
        )

        unable = sum(
            1
            for result in results
            if result["status"] == "UNABLE"
        )


        # ====================================================
        # FOOTPRINT SCORE
        # ====================================================

        score = min(
            100,
            found * 12
        )


        # ====================================================
        # RISK LEVEL
        # ====================================================

        if score >= 70:

            risk = "HIGH"

        elif score >= 40:

            risk = "MEDIUM"

        elif score > 0:

            risk = "LOW"

        else:

            risk = "MINIMAL"


        now = datetime.now()


        print()
        print("SCAN FINISHED")
        print("Total:", total)
        print("Found:", found)
        print("Blocked:", blocked)
        print("Not Found:", not_found)
        print("Unable:", unable)
        print("=" * 55)


        # ====================================================
        # RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "username": username,

            "total": total,

            "found": found,

            "blocked": blocked,

            "not_found": not_found,

            "unable": unable,

            "score": score,

            "risk": risk,

            "date": now.strftime("%d %b %Y"),

            "time": now.strftime("%H:%M:%S"),

            "results": results
        })


    except Exception as error:

        print(
            "[SCAN INTERNAL ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message": "Internal scan error."

        }), 500


# ============================================================
# IP LOOKUP
# ============================================================

@app.route("/api/ip", methods=["POST"])
def ip_lookup():

    try:

        data = request.get_json(silent=True) or {}

        ip = str(
            data.get("ip", "")
        ).strip()


        if not ip:

            return jsonify({
                "success": False,
                "message": "IP address is required."
            }), 400


        # Validate IP
        try:

            ipaddress.ip_address(ip)

        except ValueError:

            return jsonify({
                "success": False,
                "message": "Invalid IP address."
            }), 400


        print(
            "[IP LOOKUP]",
            ip
        )


        response = requests.get(

            f"https://ipapi.co/{ip}/json/",

            timeout=REQUEST_TIMEOUT,

            headers={
                "User-Agent":
                    "DigitalFootprintAnalyzer/1.0"
            }
        )


        if response.status_code != 200:

            return jsonify({

                "success": False,

                "message":
                    "Unable to lookup this IP."

            }), 400


        info = response.json()


        return jsonify({

            "success": True,

            "ip":
                info.get("ip", ip),

            "isp":
                info.get(
                    "org",
                    "Unknown"
                ),

            "region":
                info.get(
                    "region",
                    "Unknown"
                ),

            "city":
                info.get(
                    "city",
                    "Unknown"
                ),

            "country":
                info.get(
                    "country_name",
                    "Unknown"
                ),

            "asn":
                info.get(
                    "asn",
                    "Unknown"
                ),

            "timezone":
                info.get(
                    "timezone",
                    "Unknown"
                )
        })


    except Exception as error:

        print(
            "[IP LOOKUP ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "IP lookup failed."

        }), 500


# ============================================================
# IP LOCATION
#
# Some versions of your JS call /api/ip-location
# instead of /api/ip.
#
# This route keeps BOTH working.
# ============================================================

@app.route("/api/ip-location", methods=["POST"])
def ip_location():

    return ip_lookup()


# ============================================================
# IP ANALYZER
# ============================================================

@app.route("/api/ip-analyze", methods=["POST"])
def ip_analyze():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        ip = str(
            data.get("ip", "")
        ).strip()


        if not ip:

            return jsonify({

                "success": False,

                "message":
                    "IP address is required."

            }), 400


        try:

            ip_obj = ipaddress.ip_address(ip)

        except ValueError:

            return jsonify({

                "success": False,

                "message":
                    "Invalid IP address."

            }), 400


        # ------------------------------
        # BASIC IP INFORMATION
        # ------------------------------

        version = (
            "IPv4"
            if ip_obj.version == 4
            else "IPv6"
        )

        private = ip_obj.is_private

        loopback = ip_obj.is_loopback

        global_ip = ip_obj.is_global

        reserved = ip_obj.is_reserved

        multicast = ip_obj.is_multicast


        # ------------------------------
        # DNS REVERSE LOOKUP
        # ------------------------------

        hostname = "Unavailable"

        try:

            hostname = socket.gethostbyaddr(ip)[0]

        except Exception:

            pass


        return jsonify({

            "success": True,

            "ip": ip,

            "version": version,

            "private": private,

            "loopback": loopback,

            "global": global_ip,

            "reserved": reserved,

            "multicast": multicast,

            "hostname": hostname

        })


    except Exception as error:

        print(
            "[IP ANALYZER ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "IP analyzer failed."

        }), 500


# ============================================================
# AUTHORIZED PRIVATE / LOCAL PORT SCANNER
#
# IMPORTANT:
# Only localhost / private-network targets are allowed.
# ============================================================

@app.route("/api/port-scan", methods=["POST"])
def port_scan():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        target = str(
            data.get("target", "")
        ).strip()


        if not target:

            return jsonify({

                "success": False,

                "message":
                    "Target IP or hostname is required."

            }), 400


        # ====================================================
        # RESOLVE TARGET
        # ====================================================

        try:

            target_ip = socket.gethostbyname(
                target
            )

        except socket.gaierror:

            return jsonify({

                "success": False,

                "message":
                    "Unable to resolve target."

            }), 400


        # ====================================================
        # SECURITY CHECK
        # ====================================================

        try:

            target_obj = ipaddress.ip_address(
                target_ip
            )

        except ValueError:

            return jsonify({

                "success": False,

                "message":
                    "Invalid target."

            }), 400


        if not (
            target_obj.is_private
            or target_obj.is_loopback
        ):

            return jsonify({

                "success": False,

                "message": (
                    "Port scanning is limited to "
                    "localhost and private-network "
                    "targets."
                )

            }), 403


        # ====================================================
        # PORT LIST
        # ====================================================

        requested_ports = data.get(
            "ports",
            [21, 22, 23, 25, 53, 80,
             110, 135, 139, 143,
             443, 445, 3306,
             3389, 8080]
        )


        # Keep it controlled
        if not isinstance(
            requested_ports,
            list
        ):

            requested_ports = [
                21, 22, 23, 25,
                53, 80, 110,
                135, 139, 143,
                443, 445, 3306,
                3389, 8080
            ]


        ports = []

        for port in requested_ports:

            try:

                port = int(port)

                if 1 <= port <= 65535:

                    ports.append(port)

            except (
                ValueError,
                TypeError
            ):

                continue


        # Limit number of ports
        ports = ports[:30]


        results = []

        print()
        print(
            "[PORT SCAN]",
            target_ip
        )


        for port in ports:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            sock.settimeout(0.5)

            start = time.time()

            try:

                connection = sock.connect_ex(
                    (target_ip, port)
                )

                elapsed = round(
                    (time.time() - start) * 1000,
                    2
                )


                if connection == 0:

                    status = "OPEN"

                else:

                    status = "CLOSED"


            except Exception:

                elapsed = 0

                status = "ERROR"


            finally:

                sock.close()


            results.append({

                "port": port,

                "status": status,

                "response_time":
                    elapsed

            })


        open_ports = sum(
            1
            for item in results
            if item["status"] == "OPEN"
        )

        closed_ports = sum(
            1
            for item in results
            if item["status"] == "CLOSED"
        )


        return jsonify({

            "success": True,

            "target":
                target_ip,

            "total":
                len(results),

            "open":
                open_ports,

            "closed":
                closed_ports,

            "results":
                results

        })


    except Exception as error:

        print(
            "[PORT SCAN ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "Port scan failed."

        }), 500


# ============================================================
# LOG ANALYZER
# ============================================================

@app.route("/api/log-analyze", methods=["POST"])
def log_analyze():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        log_text = str(
            data.get(
                "log",
                data.get(
                    "content",
                    ""
                )
            )
        )


        if not log_text.strip():

            return jsonify({

                "success": False,

                "message":
                    "Log content is required."

            }), 400


        # ====================================================
        # BASIC LOG ANALYSIS
        # ====================================================

        lines = log_text.splitlines()

        total_lines = len(lines)

        failed = 0
        warnings = 0
        errors = 0
        suspicious = 0


        suspicious_keywords = [
            "failed password",
            "authentication failure",
            "unauthorized",
            "forbidden",
            "sql injection",
            "command injection",
            "brute force",
            "malware",
            "ransomware",
            "port scan",
            "scan detected"
        ]


        for line in lines:

            lower = line.lower()


            if (
                "failed" in lower
                or "failure" in lower
            ):

                failed += 1


            if (
                "warning" in lower
                or "warn" in lower
            ):

                warnings += 1


            if (
                "error" in lower
                or "exception" in lower
            ):

                errors += 1


            for keyword in suspicious_keywords:

                if keyword in lower:

                    suspicious += 1

                    break


        # ====================================================
        # RISK
        # ====================================================

        if suspicious >= 5:

            risk = "HIGH"

        elif suspicious >= 2:

            risk = "MEDIUM"

        elif failed >= 5 or errors >= 5:

            risk = "LOW"

        else:

            risk = "MINIMAL"


        return jsonify({

            "success": True,

            "total_lines":
                total_lines,

            "failed":
                failed,

            "warnings":
                warnings,

            "errors":
                errors,

            "suspicious":
                suspicious,

            "risk":
                risk

        })


    except Exception as error:

        print(
            "[LOG ANALYZER ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "Log analysis failed."

        }), 500


# ============================================================
# WEB SEARCH / WEBSITE CHECK
# ============================================================

@app.route("/api/web-search", methods=["POST"])
def web_search():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        url = str(
            data.get(
                "url",
                ""
            )
        ).strip()


        if not url:

            return jsonify({

                "success": False,

                "message":
                    "URL is required."

            }), 400


        if not (
            url.startswith("http://")
            or
            url.startswith("https://")
        ):

            url = "https://" + url


        response = requests.get(

            url,

            timeout=REQUEST_TIMEOUT,

            headers={
                "User-Agent":
                    USER_AGENT
            },

            allow_redirects=True
        )


        return jsonify({

            "success": True,

            "url":
                response.url,

            "status_code":
                response.status_code,

            "status":
                "ONLINE"
                if response.ok
                else "UNAVAILABLE",

            "content_type":
                response.headers.get(
                    "Content-Type",
                    "Unknown"
                )

        })


    except requests.RequestException as error:

        print(
            "[WEB SEARCH ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to connect to website."

        }), 400


    except Exception as error:

        print(
            "[WEB SEARCH INTERNAL ERROR]",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "Web check failed."

        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "message":
            "API endpoint not found."

    }), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "message":
            "Internal server error."

    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("        DIGITAL FOOTPRINT ANALYZER")
    print("=" * 60)
    print()
    print("Backend: http://127.0.0.1:5000")
    print()
    print("Available API services:")
    print("  [OK] /api/status")
    print("  [OK] /api/scan")
    print("  [OK] /api/ip")
    print("  [OK] /api/ip-location")
    print("  [OK] /api/ip-analyze")
    print("  [OK] /api/port-scan")
    print("  [OK] /api/log-analyze")
    print("  [OK] /api/web-search")
    print()
    print("=" * 60)
    print()

    app.run(
    host="0.0.0.0",
    port=5000,
    debug=False
)