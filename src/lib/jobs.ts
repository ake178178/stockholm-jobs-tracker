import fs from "fs";
import path from "path";
import type { DailyData } from "./types";

const DATA_DIR = path.join(process.cwd(), "data");

export function getAllDates(): string[] {
  if (!fs.existsSync(DATA_DIR)) return [];
  return fs
    .readdirSync(DATA_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(".json", ""))
    .sort()
    .reverse();
}

export function getDataForDate(date: string): DailyData | null {
  const filePath = path.join(DATA_DIR, `${date}.json`);
  if (!fs.existsSync(filePath)) return null;
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8")) as DailyData;
  } catch {
    return null;
  }
}

export function getLatestData(): DailyData | null {
  const dates = getAllDates();
  if (dates.length === 0) return null;
  return getDataForDate(dates[0]);
}

export const COMPANY_META: Record<
  string,
  { label: string; color: string; logo: string; url: string }
> = {
  amazon: {
    label: "Amazon / AWS",
    color: "#FF9900",
    logo: "☁️",
    url: "https://www.amazon.jobs/en/location/stockholm-sweden",
  },
  google: {
    label: "Google",
    color: "#4285F4",
    logo: "🔍",
    url: "https://careers.google.com/locations/stockholm/",
  },
  microsoft: {
    label: "Microsoft",
    color: "#00A4EF",
    logo: "🪟",
    url: "https://careers.microsoft.com/",
  },
  spotify: {
    label: "Spotify",
    color: "#1DB954",
    logo: "🎵",
    url: "https://www.lifeatspotify.com/jobs?l=stockholm",
  },
  klarna: {
    label: "Klarna",
    color: "#FFB3C7",
    logo: "💳",
    url: "https://www.klarna.com/careers/",
  },
  ericsson: {
    label: "Ericsson",
    color: "#0082F0",
    logo: "📡",
    url: "https://www.ericsson.com/en/careers/global-locations/sweden",
  },
  nokia: {
    label: "Nokia",
    color: "#124191",
    logo: "🌐",
    url: "https://jobs.nokia.com/",
  },
  sinch: {
    label: "Sinch",
    color: "#5A2D82",
    logo: "📱",
    url: "https://www.sinch.com/careers/",
  },
};

export function scoreLabel(score: number): { label: string; color: string } {
  if (score >= 70) return { label: "S", color: "#065F46" };
  if (score >= 50) return { label: "A", color: "#1E40AF" };
  if (score >= 30) return { label: "B", color: "#78350F" };
  return { label: "C", color: "#991B1B" };
}
