"""Reputation lookups for submitted public URLs. No target URL is fetched here."""
import ipaddress
import os
from urllib.parse import urlparse

import requests
from database.models.routes.services.integrations.utils.validators import validate_http_url

from config import Config


def _public_host(hostname):
    try:
        return ipaddress.ip_address(hostname).is_global
    except ValueError:
        hostname = hostname.rstrip(".").lower()
        return "." in hostname and hostname not in {"localhost", "localhost.localdomain"} and not hostname.endswith((".local", ".internal", ".localhost", ".test", ".invalid"))


def check_url_reputation(url):
    if not isinstance(url, str) or not url.strip():
        return {"source": "unavailable", "domain": None, "providers": [], "risk_points": 0,
                "checked": False, "message": "No URL supplied for reputation lookup."}
    parsed = urlparse(url)
    valid, validation_message = validate_http_url(url, required=True)
    if not valid:
        return {"source": "blocked", "domain": parsed.hostname, "providers": [], "risk_points": 0, "checked": False, "message": validation_message}
    if not parsed.hostname or not _public_host(parsed.hostname):
        return {"source": "blocked", "domain": parsed.hostname, "providers": [], "risk_points": 0,
                "message": "Private and local addresses cannot be sent to reputation providers."}

    vt_key = os.getenv("VIRUSTOTAL_API_KEY", "").strip() or Config.VIRUSTOTAL_API_KEY.strip()
    safe_key = os.getenv("SAFE_BROWSING_API_KEY", "").strip() or Config.SAFE_BROWSING_API_KEY.strip()
    providers = []
    if not vt_key:
        providers.append({"provider": "VirusTotal", "status": "not_configured", "risk_points": 0})
    if not safe_key:
        providers.append({"provider": "Google Safe Browsing", "status": "not_configured", "risk_points": 0})

    if vt_key:
        try:
            submitted = requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers={"x-apikey": vt_key}, data={"url": url}, timeout=(4, 12),
            )
            submitted.raise_for_status()
            analysis_id = submitted.json().get("data", {}).get("id")
            if not analysis_id:
                raise ValueError("VirusTotal did not return an analysis reference")
            report = requests.get(
                f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                headers={"x-apikey": vt_key}, timeout=(4, 12),
            )
            report.raise_for_status()
            attributes = report.json().get("data", {}).get("attributes", {})
            stats = attributes.get("stats", {})
            if attributes.get("status") == "completed":
                malicious = int(stats.get("malicious", 0))
                suspicious = int(stats.get("suspicious", 0))
                points = 85 if malicious else 55 if suspicious else 0
                providers.append({"provider": "VirusTotal", "status": "complete", "malicious": malicious,
                                  "suspicious": suspicious, "harmless": int(stats.get("harmless", 0)),
                                  "risk_points": points})
            else:
                providers.append({"provider": "VirusTotal", "status": "pending", "risk_points": 0,
                                  "message": "The provider accepted the URL; analysis is still processing."})
        except (requests.RequestException, ValueError, TypeError, KeyError):
            providers.append({"provider": "VirusTotal", "status": "unavailable", "risk_points": 0,
                              "message": "The lookup failed or was rate limited."})

    if safe_key:
        try:
            response = requests.post(
                "https://safebrowsing.googleapis.com/v4/threatMatches:find",
                params={"key": safe_key},
                json={"client": {"clientId": "digitalsentinel", "clientVersion": "1.0"},
                      "threatInfo": {"threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                                     "platformTypes": ["ANY_PLATFORM"], "threatEntryTypes": ["URL"],
                                     "threatEntries": [{"url": url}]}},
                timeout=(4, 12),
            )
            response.raise_for_status()
            matches = response.json().get("matches", [])
            providers.append({"provider": "Google Safe Browsing", "status": "complete",
                              "threats_found": len(matches),
                              "matches": [{"threat_type": m.get("threatType"), "platform": m.get("platformType")} for m in matches],
                              "risk_points": 90 if matches else 0})
        except (requests.RequestException, ValueError, TypeError, KeyError):
            providers.append({"provider": "Google Safe Browsing", "status": "unavailable", "risk_points": 0,
                              "message": "The lookup failed or was rate limited."})

    complete = [provider for provider in providers if provider["status"] == "complete"]
    return {
        "domain": parsed.hostname,
        "source": "live" if complete else "pending" if any(p["status"] == "pending" for p in providers) else "unavailable",
        "providers": providers,
        "risk_points": max((provider["risk_points"] for provider in complete), default=0),
        "checked": bool(complete),
        "message": "URL checked by at least one configured provider. No match means no known listing in those provider results, not a guarantee of safety." if complete else "No provider check completed; URL reputation did not affect the score.",
    }
