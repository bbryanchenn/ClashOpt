"use client";

import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Swords, Shield, BarChart3, RefreshCcw } from "lucide-react";

const emptyTeam = ["", "", "", "", ""];
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
    <div className="rounded-2xl border border-white/10 bg-white/5 shadow-sm backdrop-blur">
      {title && (
        <div className="border-b border-white/10 px-5 py-4 text-lg font-semibold">
          {title}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-sm">
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
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-sm">
      <div className="text-sm text-white/60">{title}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
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
            <div className="text-sm text-white/60">{roles[i]}</div>
            <input
              value={value}
              placeholder={`Enter ${roles[i]} champ`}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                const next = [...team];
                next[i] = e.target.value;
                setTeam(next);
              }}
              className="h-11 rounded-xl border border-white/10 bg-black/20 px-3 outline-none ring-0 placeholder:text-white/30 focus:border-white/30"
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

        <div className="text-sm leading-6 text-white/70">{data.summary}</div>
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
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between"
        >
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-white/70">
              <Swords className="h-4 w-4" />
              ClashOpt Web MVP
            </div>
            <h1 className="text-4xl font-semibold tracking-tight">
              Clash Opt. Now on da web. SUGOI!
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-white/60">
              Enter both comps and compare win condition, synergy, and counter
              pressure using your live ClashOpt backend.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setBlue(sample.blue);
                setRed(sample.red);
              }}
              className="inline-flex h-11 items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 text-sm hover:bg-white/10"
            >
              <RefreshCcw className="h-4 w-4" />
              Load Sample
            </button>

            <button
              disabled={!ready || loading}
              onClick={compare}
              className="inline-flex h-11 items-center rounded-2xl bg-white px-4 text-sm font-medium text-black disabled:cursor-not-allowed disabled:opacity-50"
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
          <div className="mt-6 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-200">
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
              <div className="flex items-center gap-2 text-sm text-white/70">
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