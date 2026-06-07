#!/usr/bin/env python3
"""
Daily job scraper for Stockholm tech companies.
Fetches AI/Telecom/Cloud roles relevant to Kobe Wang's profile.
"""

import json
import re
import os
import time
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup
from typing import Optional

# ── Profile keywords ──────────────────────────────────────────────────────────
KEYWORD_SCORES = {
    "solutions architect":      30,
    "ai architect":             28,
    "cloud architect":          25,
    "technical product manager": 22,
    "forward deployed":         22,
    "engagement manager":       18,
    "o-ran":                    25,
    "telecom":                  20,
    "5g":                       18,
    "generative ai":            18,
    "agentic ai":               20,
    "llm":                      18,
    "rag":                      18,
    "machine learning":         15,
    "ai":                       12,
    "cloud":                    10,
    "aws":                      10,
    "azure":                    10,
    "gcp":                      10,
    "network":                   8,
    "wireless":                  8,
    "python":                    6,
    "react":                     5,
    "api":                       4,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def score_job(title: str, description: str = "") -> tuple[int, list[str]]:
    text = (title + " " + description).lower()
    score = 0
    reasons: list[str] = []
    for kw, pts in KEYWORD_SCORES.items():
        if kw in text:
            score += pts
            reasons.append(kw)
    return min(score, 100), reasons


def job_id(company: str, title: str, url: str) -> str:
    raw = f"{company}|{title}|{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def safe_get(url: str, params: Optional[dict] = None, timeout: int = 15) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  [WARN] {url}: {e}")
        return None


# ── Company scrapers ──────────────────────────────────────────────────────────

def fetch_amazon() -> list[dict]:
    print("→ Amazon.jobs")
    jobs = []
    queries = ["AI architect", "solutions architect", "machine learning", "telecom"]
    seen: set[str] = set()

    for q in queries:
        r = safe_get("https://www.amazon.jobs/en/search.json", params={
            "base_query": q,
            "loc_query": "Sweden",
            "country": "SWE",
            "result_limit": 20,
            "normalized_location[]": "Stockholm, Sweden",
        })
        if not r:
            continue
        try:
            data = r.json()
            for item in data.get("jobs", []):
                loc = item.get("normalized_location", "") or item.get("location", "")
                if "Sweden" not in loc and "Stockholm" not in loc:
                    continue
                title = item.get("title", "")
                url = "https://www.amazon.jobs" + item.get("job_path", "")
                uid = job_id("Amazon", title, url)
                if uid in seen:
                    continue
                seen.add(uid)
                sc, reasons = score_job(title, item.get("description", ""))
                if sc < 10:
                    continue
                jobs.append({
                    "id": uid,
                    "title": title,
                    "company": "Amazon / AWS",
                    "company_key": "amazon",
                    "location": loc,
                    "url": url,
                    "posted": item.get("posted_date", ""),
                    "job_type": "Full-time",
                    "match_score": sc,
                    "match_reasons": reasons,
                    "team": item.get("team", ""),
                })
        except Exception as e:
            print(f"  [ERROR] Amazon parse: {e}")
        time.sleep(1)

    print(f"  Amazon: {len(jobs)} jobs")
    return jobs


def fetch_google() -> list[dict]:
    print("→ Google Careers")
    jobs = []
    seen: set[str] = set()
    queries = ["AI architect", "solutions architect telecom", "machine learning engineer", "technical program manager"]

    for q in queries:
        r = safe_get(
            "https://careers.google.com/api/jobs/jobs-v1/search/",
            params={"q": q, "location": "Stockholm, Sweden", "hl": "en", "pageSize": 20},
        )
        if not r:
            continue
        try:
            data = r.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                locs = [a.get("display", "") for a in item.get("applyUrls", [])] or item.get("locations", [])
                loc_str = ", ".join(locs) if isinstance(locs, list) else str(locs)
                if "Stockholm" not in str(item) and "Sweden" not in str(item):
                    continue
                url = f"https://careers.google.com/jobs/results/{item.get('requisitionId', '')}/"
                uid = job_id("Google", title, url)
                if uid in seen:
                    continue
                seen.add(uid)
                sc, reasons = score_job(title, item.get("description", ""))
                if sc < 10:
                    continue
                jobs.append({
                    "id": uid,
                    "title": title,
                    "company": "Google",
                    "company_key": "google",
                    "location": loc_str or "Stockholm, Sweden",
                    "url": url,
                    "posted": "",
                    "job_type": "Full-time",
                    "match_score": sc,
                    "match_reasons": reasons,
                    "team": item.get("businessUnitDisplay", ""),
                })
        except Exception as e:
            print(f"  [ERROR] Google parse: {e}")
        time.sleep(1.5)

    print(f"  Google: {len(jobs)} jobs")
    return jobs


def fetch_microsoft() -> list[dict]:
    print("→ Microsoft Careers")
    jobs = []
    seen: set[str] = set()
    queries = ["AI architect", "cloud solution architect", "technical specialist AI", "telecom"]

    for q in queries:
        r = safe_get(
            "https://gcsservices.careers.microsoft.com/search/api/v1/search",
            params={
                "q": q,
                "lc": "Sweden",
                "exp": "Experienced professionals",
                "pgSz": 20,
                "o": "Relevance",
                "flt": "true",
            },
        )
        if not r:
            continue
        try:
            data = r.json()
            for item in data.get("operationResult", {}).get("result", {}).get("jobs", []):
                title = item.get("title", "")
                loc = item.get("properties", {}).get("primaryAddressCity", "")
                if "Stockholm" not in loc and "Sweden" not in str(item):
                    continue
                url = "https://careers.microsoft.com/us/en/job/" + str(item.get("jobId", ""))
                uid = job_id("Microsoft", title, url)
                if uid in seen:
                    continue
                seen.add(uid)
                sc, reasons = score_job(title, item.get("description", ""))
                if sc < 10:
                    continue
                jobs.append({
                    "id": uid,
                    "title": title,
                    "company": "Microsoft",
                    "company_key": "microsoft",
                    "location": f"{loc}, Sweden",
                    "url": url,
                    "posted": item.get("postingDate", ""),
                    "job_type": "Full-time",
                    "match_score": sc,
                    "match_reasons": reasons,
                    "team": item.get("properties", {}).get("discipline", ""),
                })
        except Exception as e:
            print(f"  [ERROR] Microsoft parse: {e}")
        time.sleep(1)

    print(f"  Microsoft: {len(jobs)} jobs")
    return jobs


def fetch_lever(company_slug: str, company_name: str, company_key: str) -> list[dict]:
    """Generic Lever.co API scraper."""
    print(f"→ {company_name} (Lever)")
    r = safe_get(f"https://api.lever.co/v0/postings/{company_slug}?mode=json")
    if not r:
        return []

    jobs = []
    seen: set[str] = set()
    try:
        postings = r.json()
        for item in postings:
            loc = item.get("categories", {}).get("location", "")
            if loc and "Stockholm" not in loc and "Sweden" not in loc and "Remote" not in loc:
                continue
            title = item.get("text", "")
            url = item.get("hostedUrl", "")
            desc = BeautifulSoup(item.get("descriptionBody", ""), "lxml").get_text(" ")
            uid = job_id(company_name, title, url)
            if uid in seen:
                continue
            seen.add(uid)
            sc, reasons = score_job(title, desc)
            if sc < 10:
                continue
            jobs.append({
                "id": uid,
                "title": title,
                "company": company_name,
                "company_key": company_key,
                "location": loc or "Stockholm, Sweden",
                "url": url,
                "posted": datetime.datetime.fromtimestamp(
                    item.get("createdAt", 0) / 1000
                ).strftime("%Y-%m-%d") if item.get("createdAt") else "",
                "job_type": item.get("categories", {}).get("commitment", "Full-time"),
                "match_score": sc,
                "match_reasons": reasons,
                "team": item.get("categories", {}).get("team", ""),
            })
    except Exception as e:
        print(f"  [ERROR] {company_name} parse: {e}")

    print(f"  {company_name}: {len(jobs)} jobs")
    return jobs


def fetch_greenhouse(company_slug: str, company_name: str, company_key: str) -> list[dict]:
    """Generic Greenhouse API scraper."""
    print(f"→ {company_name} (Greenhouse)")
    r = safe_get(f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true")
    if not r:
        return []

    jobs = []
    seen: set[str] = set()
    try:
        data = r.json()
        for item in data.get("jobs", []):
            loc = item.get("location", {}).get("name", "")
            if loc and "Stockholm" not in loc and "Sweden" not in loc and "Remote" not in loc:
                continue
            title = item.get("title", "")
            url = item.get("absolute_url", "")
            desc = BeautifulSoup(item.get("content", ""), "lxml").get_text(" ")
            uid = job_id(company_name, title, url)
            if uid in seen:
                continue
            seen.add(uid)
            sc, reasons = score_job(title, desc)
            if sc < 10:
                continue
            jobs.append({
                "id": uid,
                "title": title,
                "company": company_name,
                "company_key": company_key,
                "location": loc or "Stockholm, Sweden",
                "url": url,
                "posted": item.get("updated_at", "")[:10],
                "job_type": "Full-time",
                "match_score": sc,
                "match_reasons": reasons,
                "team": "",
            })
    except Exception as e:
        print(f"  [ERROR] {company_name} parse: {e}")

    print(f"  {company_name}: {len(jobs)} jobs")
    return jobs


def fetch_ericsson() -> list[dict]:
    print("→ Ericsson")
    jobs = []
    seen: set[str] = set()
    queries = ["AI architect", "solutions architect", "O-RAN", "machine learning"]

    for q in queries:
        r = safe_get("https://jobs.ericsson.com/careers/searchjobs", params={
            "query": q,
            "location": "Stockholm",
            "orgIds": "1",
            "alp": "6252001",
        })
        if not r:
            continue
        try:
            soup = BeautifulSoup(r.text, "lxml")
            for article in soup.select("article.article--result, li.job-result"):
                a_tag = article.find("a")
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                url = href if href.startswith("http") else "https://jobs.ericsson.com" + href
                uid = job_id("Ericsson", title, url)
                if uid in seen:
                    continue
                seen.add(uid)
                sc, reasons = score_job(title)
                if sc < 8:
                    continue
                loc_el = article.select_one(".location, .job-location")
                jobs.append({
                    "id": uid,
                    "title": title,
                    "company": "Ericsson",
                    "company_key": "ericsson",
                    "location": loc_el.get_text(strip=True) if loc_el else "Stockholm, Sweden",
                    "url": url,
                    "posted": "",
                    "job_type": "Full-time",
                    "match_score": sc,
                    "match_reasons": reasons,
                    "team": "",
                })
        except Exception as e:
            print(f"  [ERROR] Ericsson parse: {e}")
        time.sleep(1.5)

    print(f"  Ericsson: {len(jobs)} jobs")
    return jobs


def fetch_nokia() -> list[dict]:
    print("→ Nokia")
    jobs = []
    seen: set[str] = set()

    r = safe_get("https://jobs.nokia.com/en/sites/CX_1/jobs/search-results", params={
        "keyword": "AI architect solutions",
        "location": "Stockholm",
        "radius": "50km",
    })
    if not r:
        return []

    try:
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.select("li.job-list-item, .job-card"):
            a_tag = item.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            url = href if href.startswith("http") else "https://jobs.nokia.com" + href
            uid = job_id("Nokia", title, url)
            if uid in seen:
                continue
            seen.add(uid)
            sc, reasons = score_job(title)
            if sc < 8:
                continue
            jobs.append({
                "id": uid,
                "title": title,
                "company": "Nokia",
                "company_key": "nokia",
                "location": "Stockholm, Sweden",
                "url": url,
                "posted": "",
                "job_type": "Full-time",
                "match_score": sc,
                "match_reasons": reasons,
                "team": "",
            })
    except Exception as e:
        print(f"  [ERROR] Nokia parse: {e}")

    print(f"  Nokia: {len(jobs)} jobs")
    return jobs


def fetch_sinch() -> list[dict]:
    print("→ Sinch")
    jobs = []
    seen: set[str] = set()

    r = safe_get("https://www.sinch.com/careers/")
    if not r:
        return []

    try:
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/careers/" not in href or href == "/careers/":
                continue
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            url = href if href.startswith("http") else "https://www.sinch.com" + href
            uid = job_id("Sinch", title, url)
            if uid in seen:
                continue
            seen.add(uid)
            sc, reasons = score_job(title)
            if sc < 8:
                continue
            jobs.append({
                "id": uid,
                "title": title,
                "company": "Sinch",
                "company_key": "sinch",
                "location": "Stockholm, Sweden",
                "url": url,
                "posted": "",
                "job_type": "Full-time",
                "match_score": sc,
                "match_reasons": reasons,
                "team": "",
            })
    except Exception as e:
        print(f"  [ERROR] Sinch parse: {e}")

    # Also try Greenhouse (Sinch sometimes uses it)
    gh = fetch_greenhouse("sinch", "Sinch", "sinch")
    seen_ids = {j["id"] for j in jobs}
    for j in gh:
        if j["id"] not in seen_ids:
            jobs.append(j)

    print(f"  Sinch: {len(jobs)} jobs")
    return jobs


# ── Load previous data for "new" detection ────────────────────────────────────

def load_previous_ids(data_dir: str) -> set[str]:
    files = sorted([f for f in os.listdir(data_dir) if f.endswith(".json")])
    if not files:
        return set()
    latest_file = os.path.join(data_dir, files[-1])
    try:
        with open(latest_file) as f:
            data = json.load(f)
        return {j["id"] for j in data.get("jobs", [])}
    except Exception:
        return set()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today().isoformat()
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    previous_ids = load_previous_ids(data_dir)
    print(f"Previous job IDs loaded: {len(previous_ids)}")

    all_jobs: list[dict] = []

    # Run all scrapers
    all_jobs += fetch_amazon()
    all_jobs += fetch_google()
    all_jobs += fetch_microsoft()
    all_jobs += fetch_lever("spotify", "Spotify", "spotify")
    all_jobs += fetch_lever("klarna-2", "Klarna", "klarna")
    all_jobs += fetch_ericsson()
    all_jobs += fetch_nokia()
    all_jobs += fetch_sinch()

    # De-duplicate across companies
    seen: set[str] = set()
    unique_jobs: list[dict] = []
    for j in all_jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            j["is_new"] = j["id"] not in previous_ids
            unique_jobs.append(j)

    # Sort: new first, then by score desc
    unique_jobs.sort(key=lambda j: (-int(j["is_new"]), -j["match_score"]))

    # Stats
    by_company: dict[str, int] = {}
    for j in unique_jobs:
        by_company[j["company"]] = by_company.get(j["company"], 0) + 1

    payload = {
        "date": today,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "jobs": unique_jobs,
        "stats": {
            "total": len(unique_jobs),
            "new_count": sum(1 for j in unique_jobs if j["is_new"]),
            "by_company": by_company,
        },
    }

    out_path = os.path.join(data_dir, f"{today}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(unique_jobs)} jobs to {out_path}")
    print(f"   New today: {payload['stats']['new_count']}")
    for co, cnt in sorted(by_company.items()):
        print(f"   {co}: {cnt}")


if __name__ == "__main__":
    main()
