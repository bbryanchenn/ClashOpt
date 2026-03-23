"use client";

import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Swords, BarChart3, RefreshCcw } from "lucide-react";

const roles = ["Top", "Jg", "Mid", "ADC", "Sup"];

const sample = {
  blue: ["Aatrox", "Vi", "Syndra", "Kai'Sa", "Nautilus"],
  red: ["K'Sante", "Sejuani", "Taliyah", "Xayah", "Rakan"],
};

type CompareResponse = {
  score: number;
  blue: {
    wincon: string[];
    synergy: number;
    comfort: number;
    counter: number;
    summary: string;
  };
  red: {
    wincon: string[];
    synergy: number;
    comfort: number;
    counter: number;
    summary: string;
  };
};

const fallbackResult: CompareResponse = {
  score: 49.04,
  blue: {
    wincon: ["front_to_back"],
    synergy: 5.6,
    comfort: 0,
    counter: 0.15,
    summary: "Wincon: front_to_back. Synergy 5.60. Counter risk 0.15.",
  },
  red: {
    wincon: ["front_to_back"],
    synergy: 5.61,
    comfort: 0,
    counter: 0.06,
    summary: "Wincon: front_to_back. Synergy 5.61. Counter risk 0.06.",
  },
};

function normalizeTeam(team: string[]) {
  return team.map((x) => x.trim()).filter(Boolean);
}

function Panel({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-[#C89B3C]/20 bg-[#091428]/75 shadow-[0_12px_40px_rgba(0,0,0,0.45)] backdrop-blur-xl">
      {title && (
        <div className="border-b border-[#C89B3C]/20 px-5 py-4 text-lg font-semibold text-[#F0E6D2]">
          {title}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-[#C89B3C]/40 bg-[#0A323C]/60 px-3 py-1 text-sm text-[#F0E6D2]">
      {children}
    </span>
  );
}

function StatCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-[#C89B3C]/20 bg-gradient-to-b from-[#0A223D]/75 to-[#091428]/75 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
      <div className="text-sm text-[#A09B8C]">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-[#F0E6D2]">{value}</div>
    </div>
  );
}

function TeamEditor({
  title,
  team,
  setTeam,
}: {
  title: string;
  team: string[];
  setTeam: React.Dispatch<React.SetStateAction<string[]>>;
}) {
  return (
    <Panel title={title}>
      <div className="space-y-3">
        {team.map((value, i) => (
          <div key={i} className="grid grid-cols-[72px_1fr] items-center gap-3">
            <div className="text-sm text-[#A09B8C]">{roles[i]}</div>
            <input
              value={value}
              placeholder={`Enter ${roles[i]} champ`}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                const next = [...team];
                next[i] = e.target.value;
                setTeam(next);
              }}
              className="h-11 rounded-xl border border-[#C89B3C]/25 bg-[#0A1428]/80 px-3 text-[#F0E6D2] outline-none ring-0 placeholder:text-[#5B5A56] focus:border-[#C89B3C] focus:shadow-[0_0_0_3px_rgba(200,155,60,0.2)]"
            />
          </div>
        ))}
      </div>
    </Panel>
  );
}

function SideBreakdown({
  label,
  data,
}: {
  label: string;
  data: CompareResponse["blue"];
}) {
  return (
    <Panel title={label}>
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {data.wincon.map((w) => (
            <Pill key={w}>{w}</Pill>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <StatCard title="Synergy" value={data.synergy} />
          <StatCard title="Comfort" value={data.comfort} />
          <StatCard title="Counter" value={data.counter} />
        </div>

        <div className="text-sm leading-6 text-[#C8C3B5]">{data.summary}</div>
      </div>
    </Panel>
  );
}

export default function Page() {
  const [blue, setBlue] = useState<string[]>(sample.blue);
  const [red, setRed] = useState<string[]>(sample.red);
  const [result, setResult] = useState<CompareResponse | null>(fallbackResult);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const ready = useMemo(
    () => normalizeTeam(blue).length === 5 && normalizeTeam(red).length === 5,
    [blue, red]
  );

  async function compare() {
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          blue: normalizeTeam(blue),
          red: normalizeTeam(red),
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new  Error(err.detail || "Unknown error");
      }

      const data: CompareResponse = await res.json();
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "An error occurred while comparing drafts.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#010A13] text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 top-0 h-80 w-80 rounded-full bg-[#005A82]/35 blur-3xl" />
        <div className="absolute right-0 top-24 h-96 w-96 rounded-full bg-[#C89B3C]/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-[#0AC8B9]/10 blur-3xl" />
      </div>
      <div className="relative mx-auto max-w-7xl px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between"
        >
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#C89B3C]/30 bg-[#0A223D]/70 px-3 py-1 text-sm text-[#F0E6D2]">
              <Swords className="h-4 w-4" />
              ClashOpt · Draft Intelligence
            </div>
            <h1 className="bg-gradient-to-r from-[#F0E6D2] via-[#C8AA6E] to-[#F0E6D2] bg-clip-text text-4xl font-semibold tracking-tight text-transparent md:text-5xl">
              Build Winning Drafts with Pro-Level Clarity
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-[#C8C3B5]">
              Compare both sides instantly, surface win conditions, and spot
              counter pressure with a premium League-inspired experience.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setBlue(sample.blue);
                setRed(sample.red);
              }}
              className="inline-flex h-11 items-center gap-2 rounded-2xl border border-[#C89B3C]/30 bg-[#0A223D]/70 px-4 text-sm text-[#F0E6D2] hover:bg-[#0E3052]"
            >
              <RefreshCcw className="h-4 w-4" />
              Load Sample
            </button>

            <button
              disabled={!ready || loading}
              onClick={compare}
              className="inline-flex h-11 items-center rounded-2xl bg-gradient-to-r from-[#C89B3C] to-[#E0C27A] px-4 text-sm font-semibold text-[#091428] shadow-[0_10px_20px_rgba(200,155,60,0.25)] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Comparing..." : "Compare Drafts"}
            </button>
          </div>
        </motion.div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <TeamEditor title="Blue Side" team={blue} setTeam={setBlue} />
          <TeamEditor title="Red Side" team={red} setTeam={setRed} />
        </div>

        {error && (
          <div className="mt-6 rounded-2xl border border-amber-300/40 bg-amber-500/10 p-4 text-sm text-amber-100">
            {error}
          </div>
        )}

        {result && (
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-6"
          >
            <div className="grid gap-4 md:grid-cols-4">
              <StatCard title="Blue Win Score" value={`${result.score}%`} />
              <StatCard
                title="Recommended Side"
                value={result.score >= 50 ? "Blue" : "Red"}
              />
              <StatCard
                title="Confidence"
                value={Math.abs(result.score - 50).toFixed(2)}
              />
              <StatCard title="Mode" value="Compare" />
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <SideBreakdown label="Blue Breakdown" data={result.blue} />
              <SideBreakdown label="Red Breakdown" data={result.red} />
            </div>

            <Panel title="Backend Status">
              <div className="flex items-center gap-2 text-sm text-[#C8C3B5]">
                <BarChart3 className="h-4 w-4" />
                Live endpoint: http://127.0.0.1:8000/compare
              </div>
            </Panel>
          </motion.div>
        )}
      </div>
    </div>
  );
}
