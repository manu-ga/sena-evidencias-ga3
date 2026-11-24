import React from "react";
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline.json";
import { Flag, TEAM_COLOR, TEAM_NAME, Team } from "./flags";

const GOLD = "#F2C14E";
const RED = "#E63946";
const INK = "#05070D";
const WHITE = "#FFFFFF";
const DIM = "#9AA6BD";
const FONT = "Inter, 'Helvetica Neue', Arial, sans-serif";
const W = 1080;
const H = 1920;
const fps = timeline.fps;
const fr = (s: number) => Math.round(s * fps);
export const giganteFrames = Math.ceil(timeline.duration * fps);

const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const prog = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], { ...cl, easing: ease });
const pop = (f: number, d = 0) => interpolate(f - d, [0, 5, 9], [0.85, 1.05, 1], { ...cl, easing: Easing.out(Easing.quad) });
const fade = (f: number, d = 0, n = 4) => interpolate(f - d, [0, n], [0, 1], cl);
const shadowText = "0 6px 30px rgba(0,0,0,.65)";

type Shot = { kind: string; start: number; end: number; hit: boolean; props: Record<string, any> };
type Sub = { text: string; start: number; end: number };
type ScoreRow = { team: Team; p_copas: number; p_mundial: number; p_part: number; p_rank: number; total: number; copas: number; mundiales: number; ranking: number };

// ---------------------------------------------------------------------------- fondo de estadio
const Stadium: React.FC = () => {
  const f = useCurrentFrame();
  const beams = [-28, -10, 10, 28];
  const dots = Array.from({ length: 46 }, (_, i) => i);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(120% 70% at 50% 18%, #18284A 0%, #0A1222 45%, ${INK} 100%)`, overflow: "hidden" }}>
      {beams.map((a, i) => (
        <div key={i} style={{ position: "absolute", left: W / 2 - 110 + (i - 1.5) * 260, top: -200, width: 220, height: 1700, transformOrigin: "50% 0%",
          transform: `rotate(${a + Math.sin(f / 70 + i) * 4}deg)`, background: "linear-gradient(180deg, rgba(220,235,255,.22), rgba(220,235,255,0) 80%)", filter: "blur(18px)" }} />
      ))}
      {dots.map((i) => {
        const x = (i * 197) % W;
        const y = 1250 + ((i * 89) % 520);
        const tw = Math.max(0, Math.sin(f * 0.11 + i * 1.7)) ** 8;
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 6, height: 6, borderRadius: 3, background: WHITE, opacity: 0.12 + tw * 0.8, boxShadow: `0 0 ${10 + tw * 20}px ${WHITE}` }} />;
      })}
      <div style={{ position: "absolute", left: -200, right: -200, bottom: -380, height: 760, borderRadius: "50%", background: "radial-gradient(rgba(34,139,84,.35), transparent 70%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(5,7,13,.0) 40%, rgba(5,7,13,.75) 100%)" }} />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.11, mixBlendMode: "overlay" }}>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={f % 30} /></filter>
        <rect width={W} height={H} filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------- piezas comunes
const Kicker: React.FC<{ text: string; f: number; color?: string; top?: number }> = ({ text, f, color = GOLD, top = 360 }) => (
  <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: fade(f, 1), transform: `translateY(${(1 - prog(f, 0, 8)) * -30}px)` }}>
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 36, letterSpacing: "0.28em", color, borderTop: `3px solid ${color}`, borderBottom: `3px solid ${color}`, padding: "8px 22px" }}>{text}</div>
  </div>
);

const Big: React.FC<{ text: string; size: number; f: number; d?: number; color?: string; style?: React.CSSProperties }> = ({ text, size, f, d = 0, color = WHITE, style }) => (
  <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.02, color, textAlign: "center", letterSpacing: "-0.01em", textShadow: shadowText,
    transform: `scale(${pop(f, d)})`, opacity: fade(f, d, 3), ...style }}>{text}</div>
);

const Source: React.FC<{ text: string; f: number }> = ({ text, f }) => (
  <div style={{ position: "absolute", top: 1052, left: 80, right: 80, textAlign: "center", fontFamily: FONT, fontWeight: 600, fontSize: 22, color: DIM, opacity: fade(f, 10, 6) }}>{text}</div>
);

const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "flex-start", flexDirection: "column", paddingTop: 440, fontFamily: FONT }}>{children}</AbsoluteFill>
);

const Ball: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="46" fill="#F5F5F5" stroke="#111" strokeWidth="3" />
    <polygon points="50,30 66,42 60,61 40,61 34,42" fill="#111" />
    {[[50, 30, 50, 6], [66, 42, 88, 34], [60, 61, 74, 82], [40, 61, 26, 82], [34, 42, 12, 34]].map(([a, b, c, d], i) => (
      <line key={i} x1={a} y1={b} x2={c} y2={d} stroke="#111" strokeWidth="3" />
    ))}
  </svg>
);

// ---------------------------------------------------------------------------- planos
const Giants: React.FC<{ f: number }> = ({ f }) => (
  <Stage>
    <Kicker text="SUDAMÉRICA" f={f} />
    <Big text="LOS 3 GIGANTES" size={104} f={f} d={2} style={{ marginTop: 20 }} />
    <Big text="HISTÓRICOS" size={64} f={f} d={5} color={GOLD} />
    <div style={{ display: "flex", gap: 28, marginTop: 70 }}>
      {(["ARG", "BRA", "URU"] as Team[]).map((t, i) => (
        <div key={t} style={{ textAlign: "center", opacity: fade(f, 8 + i * 6), transform: `translateY(${(1 - prog(f, 8 + i * 6, 20 + i * 6)) * 120}px)` }}>
          <Flag team={t} width={290} frame={f} glow />
          <div style={{ marginTop: 18, fontWeight: 900, fontSize: 40, color: WHITE, textShadow: shadowText }}>{TEAM_NAME[t]}</div>
        </div>
      ))}
    </div>
  </Stage>
);

const Question: React.FC<{ f: number }> = ({ f }) => (
  <Stage>
    <Kicker text="EL GRAN DEBATE" f={f} color={WHITE} />
    <Big text="UNA PREGUNTA" size={92} f={f} d={2} style={{ marginTop: 60 }} />
    <Big text="QUE DIVIDE" size={92} f={f} d={5} />
    <Big text="A TODO EL CONTINENTE" size={72} f={f} d={8} color={GOLD} style={{ marginTop: 10 }} />
    <div style={{ marginTop: 50, height: 8, width: 700 * prog(f, 10, 30), background: `linear-gradient(90deg, ${TEAM_COLOR.CHI}, ${TEAM_COLOR.COL}, ${TEAM_COLOR.PAR}, ${TEAM_COLOR.PER})`, borderRadius: 4 }} />
  </Stage>
);

const Four: React.FC<{ f: number }> = ({ f }) => (
  <Stage>
    <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
      <Big text="¿EL CUARTO GRANDE" size={76} f={f} />
      <div style={{ width: 110, height: 110, borderRadius: 55, background: GOLD, color: INK, fontWeight: 900, fontSize: 86, display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: `0 0 60px ${GOLD}`, transform: `scale(${pop(f, 14) * (1 + 0.06 * Math.sin(f / 4))})`, opacity: fade(f, 14) }}>?</div>
    </div>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 26, marginTop: 40 }}>
      {(["CHI", "COL", "PAR", "PER"] as Team[]).map((t, i) => (
        <div key={t} style={{ textAlign: "center", transform: `scale(${pop(f, 3 + i * 3)})`, opacity: fade(f, 3 + i * 3) }}>
          <Flag team={t} width={290} frame={f} glow />
          <div style={{ marginTop: 10, fontWeight: 900, fontSize: 36, color: WHITE }}>{TEAM_NAME[t]}</div>
        </div>
      ))}
    </div>
  </Stage>
);

const TeamCard: React.FC<{ f: number; dur: number; p: Record<string, any> }> = ({ f, dur, p }) => {
  const t = p.team as Team;
  const players: string[] = p.players;
  const gap = Math.max(5, Math.floor((dur - 18) / players.length));
  return (
    <Stage>
      <div style={{ transform: `scale(${pop(f, 0)}) rotate(${-2 + Math.sin(f / 18) * 1}deg)` }}><Flag team={t} width={420} frame={f} glow /></div>
      <Big text={TEAM_NAME[t]} size={120} f={f} d={3} style={{ marginTop: 22 }} />
      <div style={{ marginTop: 10, background: GOLD, color: INK, fontWeight: 900, fontSize: 36, letterSpacing: "0.06em", padding: "8px 26px", borderRadius: 10, transform: `scale(${pop(f, 6)})`, opacity: fade(f, 6) }}>{p.badge}</div>
      <div style={{ marginTop: 26, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 14, width: 960 }}>
        {players.map((n, i) => {
          const d = 10 + i * gap;
          return (
            <div key={n} style={{ display: "flex", alignItems: "center", gap: 12, background: "rgba(10,16,30,.85)", borderLeft: `8px solid ${TEAM_COLOR[t]}`, padding: "10px 20px 10px 16px", borderRadius: 8,
              opacity: fade(f, d), transform: `translateX(${(1 - prog(f, d, d + 8)) * -60}px)` }}>
              <span style={{ fontWeight: 800, fontSize: 38, color: WHITE }}>{n}</span>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

const Chapter: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => (
  <Stage>
    <div style={{ transform: `rotate(${f * 4}deg) scale(${pop(f, 0)})`, marginTop: -20 }}><Ball size={220} /></div>
    <div style={{ marginTop: 40, fontWeight: 800, fontSize: 36, letterSpacing: "0.28em", color: GOLD, borderTop: `3px solid ${GOLD}`, borderBottom: `3px solid ${GOLD}`, padding: "8px 22px", opacity: fade(f, 2) }}>{p.kicker}</div>
    <div style={{ height: 30 }} />
    <Big text="LA BATALLA" size={110} f={f} d={4} />
    <Big text="MUNDIALISTA" size={110} f={f} d={7} color={GOLD} />
  </Stage>
);

const Podium: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => {
  const steps = [{ n: "2", h: 210 }, { n: "1", h: 290 }, { n: "3", h: 160 }];
  return (
    <Stage>
      <Big text={`${p.place} ${p.label}`} size={124} f={f} color={GOLD} />
      <Big text={p.event} size={60} f={f} d={4} />
      <div style={{ display: "flex", alignItems: "flex-end", gap: 12, marginTop: 50, height: 470 }}>
        {steps.map((s, i) => {
          const isThird = s.n === "3";
          const g = prog(f, 4 + i * 3, 16 + i * 3);
          return (
            <div key={s.n} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              {isThird && <div style={{ marginBottom: 14, transform: `scale(${pop(f, 14)})`, opacity: fade(f, 14) }}><Flag team="CHI" width={220} frame={f} glow /></div>}
              <div style={{ width: 230, height: s.h * g, background: isThird ? `linear-gradient(180deg, ${GOLD}, #9C7A22)` : "rgba(255,255,255,.12)", borderRadius: "12px 12px 0 0",
                display: "flex", alignItems: "flex-start", justifyContent: "center", fontWeight: 900, fontSize: 80, color: isThird ? INK : "rgba(255,255,255,.35)", paddingTop: 12 }}>{s.n}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

const Quarters: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => {
  const rows: [Team, string][] = p.rows;
  const isNew = (i: number) => (rows.length === 3 ? i === 2 : true);
  return (
    <Stage>
      <Kicker text="MEJOR RESULTADO MUNDIALISTA" f={f} top={360} />
      <Big text="CUARTOS DE FINAL" size={96} f={f} d={2} style={{ marginTop: 70 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 22, marginTop: 50 }}>
        {rows.map(([t, y], i) => {
          const d = isNew(i) ? 6 + i * 5 : 0;
          return (
            <div key={t} style={{ display: "flex", alignItems: "center", gap: 28, background: "rgba(10,16,30,.85)", border: `3px solid ${TEAM_COLOR[t]}`, borderRadius: 18, padding: "16px 30px", width: 880,
              opacity: fade(f, d), transform: `translateX(${(1 - prog(f, d, d + 9)) * 120}px)` }}>
              <Flag team={t} width={150} frame={f} radius={8} />
              <div style={{ flex: 1, fontWeight: 900, fontSize: 52, color: WHITE }}>{TEAM_NAME[t]}</div>
              <div style={{ background: GOLD, color: INK, fontWeight: 900, fontSize: 44, padding: "6px 20px", borderRadius: 10 }}>{y}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

const Bars: React.FC<{ f: number; dur: number }> = ({ f, dur }) => {
  const data: [Team, number, string][] = [["CHI", 2, "2015 · 2016"], ["PAR", 2, "1953 · 1979"], ["PER", 2, "1939 · 1975"], ["COL", 1, "2001"]];
  const at = [0.02, 0.3, 0.55, 0.72];
  return (
    <Stage>
      <Kicker text="TÍTULOS CONTINENTALES" f={f} />
      <Big text="COPAS AMÉRICA" size={104} f={f} d={2} style={{ marginTop: 60 }} />
      <div style={{ display: "flex", alignItems: "flex-end", gap: 34, marginTop: 40, height: 440 }}>
        {data.map(([t, v, years], i) => {
          const d = Math.round(at[i] * dur);
          const g = prog(f, d, d + 14);
          return (
            <div key={t} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 200, opacity: fade(f, d, 2) }}>
              <div style={{ fontWeight: 900, fontSize: 64, color: GOLD, textShadow: shadowText }}>{Math.round(v * g)}</div>
              <div style={{ width: 150, height: 110 * v * g, background: `linear-gradient(180deg, ${TEAM_COLOR[t]}, ${TEAM_COLOR[t]}55)`, borderRadius: "14px 14px 0 0", boxShadow: `0 0 40px ${TEAM_COLOR[t]}66` }} />
              <div style={{ marginTop: 14 }}><Flag team={t} width={120} frame={f} radius={6} /></div>
              <div style={{ marginTop: 8, fontWeight: 700, fontSize: 24, color: DIM }}>{years}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

const Words: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => (
  <Stage>
    <div style={{ height: 90 }} />
    {(p.lines as string[]).map((l, i) => (
      <Big key={l} text={l} size={l.length > 11 ? 100 : 118} f={f} d={i * 6} color={p.gold && i % 2 === 1 ? GOLD : i === 2 && !p.gold ? GOLD : WHITE} style={{ marginTop: 18 }} />
    ))}
  </Stage>
);

const Alert: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => {
  const blink = 0.55 + 0.45 * Math.sin(f / 3) ** 2;
  return (
    <Stage>
      <div style={{ marginTop: 80, background: RED, color: WHITE, fontWeight: 900, fontSize: 96, padding: "14px 50px", borderRadius: 16, transform: `scale(${pop(f, 0)})`, boxShadow: `0 0 ${60 * blink}px ${RED}` }}>ATENCIÓN</div>
      <Big text={p.text} size={84} f={f} d={5} style={{ marginTop: 60, maxWidth: 940 }} />
    </Stage>
  );
};

const Ranking: React.FC<{ f: number }> = ({ f }) => {
  const rows: [number, string, string, string?][] = [[8, "Bélgica", "", ""], [9, "Países Bajos", "", ""], [10, "COLOMBIA", "COL", "▲1"], [11, "Alemania", "", ""], [12, "Suiza", "", ""]];
  return (
    <Stage>
      <Kicker text="RANKING FIFA · 18/11/2026" f={f} />
      <Big text="COLOMBIA, TOP 10" size={84} f={f} d={2} style={{ marginTop: 50 }} />
      <div style={{ marginTop: 28, width: 860, display: "flex", flexDirection: "column", gap: 8 }}>
        {rows.map(([pos, name, code, mv], i) => {
          const me = code === "COL";
          return (
            <div key={pos} style={{ display: "flex", alignItems: "center", gap: 24, padding: "10px 26px", borderRadius: 12,
              background: me ? `linear-gradient(90deg, ${TEAM_COLOR.COL}, #F59E0B)` : "rgba(10,16,30,.8)", color: me ? INK : WHITE,
              transform: `scale(${me ? 1.06 * pop(f, 14) : 1}) translateX(${(1 - prog(f, 4 + i * 3, 14 + i * 3)) * 80}px)`, opacity: fade(f, 4 + i * 3) }}>
              <div style={{ width: 70, fontWeight: 900, fontSize: 48 }}>{pos}</div>
              {me ? <Flag team="COL" width={90} frame={f} radius={6} /> : <div style={{ width: 90 }} />}
              <div style={{ flex: 1, fontWeight: me ? 900 : 700, fontSize: me ? 50 : 40 }}>{name}</div>
              <div style={{ fontWeight: 900, fontSize: 36, color: me ? "#065F46" : DIM }}>{mv}</div>
            </div>
          );
        })}
      </div>
      <Source text="Fuente: FIFA/Coca-Cola Men's World Ranking, 18 de noviembre de 2026" f={f} />
    </Stage>
  );
};

const History: React.FC<{ f: number }> = ({ f }) => (
  <Stage>
    <Kicker text="MEJOR PUESTO HISTÓRICO FIFA" f={f} />
    <div style={{ display: "flex", gap: 40, marginTop: 70 }}>
      {(["CHI", "COL"] as Team[]).map((t, i) => (
        <div key={t} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, background: "rgba(10,16,30,.85)", border: `4px solid ${GOLD}`, borderRadius: 26, padding: "36px 40px",
          transform: `scale(${pop(f, 3 + i * 5)})`, opacity: fade(f, 3 + i * 5) }}>
          <Flag team={t} width={260} frame={f} />
          <div style={{ fontWeight: 900, fontSize: 150, color: GOLD, lineHeight: 1 }}>3.º</div>
          <div style={{ fontWeight: 900, fontSize: 44, color: WHITE }}>{TEAM_NAME[t]}</div>
        </div>
      ))}
    </div>
    <Source text="Fuente: FIFA (mejor posición histórica de cada selección)" f={f} />
  </Stage>
);

const Balance: React.FC<{ f: number }> = ({ f }) => {
  const tilt = Math.sin(f / 9) * 6 * Math.exp(-f / 70);
  return (
    <Stage>
      <svg width={620} height={380} viewBox="0 0 620 380" style={{ marginTop: 20, transform: `scale(${pop(f, 0)})` }}>
        <rect x="300" y="80" width="20" height="260" fill={GOLD} rx="6" />
        <rect x="200" y="330" width="220" height="26" fill={GOLD} rx="8" />
        <g transform={`rotate(${tilt} 310 90)`}>
          <rect x="60" y="80" width="500" height="16" fill={GOLD} rx="8" />
          <line x1="90" y1="96" x2="90" y2="200" stroke={GOLD} strokeWidth="5" />
          <line x1="530" y1="96" x2="530" y2="200" stroke={GOLD} strokeWidth="5" />
          <path d="M20,200 Q90,270 160,200 Z" fill={GOLD} />
          <path d="M460,200 Q530,270 600,200 Z" fill={GOLD} />
        </g>
        <circle cx="310" cy="80" r="22" fill={WHITE} />
      </svg>
      <Big text="MÁS PAREJA" size={112} f={f} d={4} style={{ marginTop: 40 }} />
      <Big text="DE LO QUE PARECE" size={76} f={f} d={7} color={GOLD} />
    </Stage>
  );
};

const Score: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => {
  const rows = timeline.score as ScoreRow[];
  const hl = p.stage === 1;
  const cell = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(1));
  return (
    <Stage>
      <Kicker text="CLASIFICACIÓN PROPIA · NO OFICIAL" f={f} color={GOLD} top={350} />
      <div style={{ marginTop: 20, width: 940, borderRadius: 18, overflow: "hidden", background: "rgba(10,16,30,.9)", border: "2px solid rgba(255,255,255,.15)", transform: `scale(${pop(f, 0)})` }}>
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr 1.3fr 1fr 1fr 110px", background: "rgba(255,255,255,.08)", padding: "12px 18px", fontWeight: 800, fontSize: 19, color: DIM, letterSpacing: "0.03em" }}>
          <div>SELECCIÓN</div><div>COPAS<br />×3</div><div>MUNDIAL<br />3.º=5 · 4tos=3</div><div>MUNDIALES<br />×0,5</div><div>RANKING<br />HOY</div><div style={{ textAlign: "right" }}>TOTAL</div>
        </div>
        {rows.map((r, i) => {
          const me = hl && i === 0;
          return (
            <div key={r.team} style={{ display: "grid", gridTemplateColumns: "300px 1fr 1.3fr 1fr 1fr 110px", alignItems: "center", padding: "14px 18px", fontWeight: 800, fontSize: 34,
              color: me ? INK : WHITE, background: me ? GOLD : "transparent", borderTop: "1px solid rgba(255,255,255,.08)", opacity: fade(f, 4 + i * 3), }}>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}><Flag team={r.team} width={62} frame={f} radius={5} /><span style={{ fontSize: 29 }}>{TEAM_NAME[r.team]}</span></div>
              <div>{cell(r.p_copas)}</div><div>{cell(r.p_mundial)}</div><div>{cell(r.p_part)}</div><div>{cell(r.p_rank)}</div>
              <div style={{ textAlign: "right", fontWeight: 900, fontSize: 42 }}>{cell(r.total)}</div>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 18, fontWeight: 600, fontSize: 23, color: DIM, width: 930, textAlign: "center", lineHeight: 1.35, opacity: fade(f, 12) }}>
        Ranking hoy: top 10 = 3 · 11-30 = 2 · 31-50 = 1 · 51+ = 0. Mundiales incluye 2026.<br />Fuentes: FIFA (ranking 18/11/2026) y Wikipedia (consulta 24/11/2026).
      </div>
      {hl && (
        <div style={{ marginTop: 22, background: GOLD, color: INK, fontWeight: 900, fontSize: 44, padding: "10px 30px", borderRadius: 14, transform: `scale(${pop(f, 3)})`, opacity: fade(f, 3) }}>
          CHILE · 4.º GRANDE EN ESTA CLASIFICACIÓN
        </div>
      )}
    </Stage>
  );
};

const Debate: React.FC<{ f: number; p: Record<string, any> }> = ({ f, p }) => {
  if (p.stage === 0) {
    return (
      <Stage>
        <Kicker text="EL VEREDICTO NO ES FINAL" f={f} color={WHITE} />
        <Big text="LA DISCUSIÓN" size={116} f={f} d={2} style={{ marginTop: 110 }} />
        <Big text="SIGUE ABIERTA" size={116} f={f} d={5} color={GOLD} />
      </Stage>
    );
  }
  const items: [Team, string][] = [["COL", "ARGUMENTOS"], ["PAR", "HISTORIA"], ["PER", "LEYENDAS"]];
  return (
    <Stage>
      <div style={{ display: "flex", flexDirection: "column", gap: 26, marginTop: 40 }}>
        {items.map(([t, w], i) => {
          const d = Math.round(i * 22);
          return (
            <div key={t} style={{ display: "flex", alignItems: "center", gap: 26, background: "rgba(10,16,30,.88)", borderLeft: `14px solid ${TEAM_COLOR[t]}`, borderRadius: 16, padding: "20px 30px", width: 900,
              opacity: fade(f, d), transform: `translateX(${(1 - prog(f, d, d + 9)) * -120}px)` }}>
              <Flag team={t} width={170} frame={f} radius={8} />
              <div>
                <div style={{ fontWeight: 800, fontSize: 36, color: DIM }}>{TEAM_NAME[t]} TIENE</div>
                <div style={{ fontWeight: 900, fontSize: 66, color: WHITE }}>{w}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

const Final: React.FC<{ f: number; dur: number }> = ({ f, dur }) => {
  const list: [string, Team][] = [["01", "ARG"], ["02", "BRA"], ["03", "URU"], ["04", "CHI"]];
  const swap = Math.round(dur * 0.42);           // el título cede su lugar a la pregunta
  const a = 1 - prog(f, swap, swap + 8);
  const b = prog(f, swap + 2, swap + 10);
  return (
    <Stage>
      <div style={{ position: "relative", height: 200, width: 1000 }}>
        <div style={{ position: "absolute", inset: 0, opacity: a, transform: `translateY(${(1 - a) * -30}px)` }}>
          <Big text="LOS 4 GRANDES" size={84} f={f} />
          <Big text="DE SUDAMÉRICA" size={52} f={f} d={3} color={GOLD} />
          <div style={{ marginTop: 10, textAlign: "center", fontWeight: 800, fontSize: 30, letterSpacing: "0.2em", color: DIM, opacity: fade(f, 6) }}>EL DEBATE ESTÁ ABIERTO</div>
        </div>
        <div style={{ position: "absolute", inset: 0, opacity: b, transform: `scale(${0.9 + 0.1 * b})`, textAlign: "center" }}>
          <div style={{ fontWeight: 900, fontSize: 80, color: WHITE, textShadow: shadowText, marginTop: 6 }}>¿ESTÁS DE ACUERDO?</div>
          <div style={{ marginTop: 16, display: "inline-block", background: RED, color: WHITE, fontWeight: 900, fontSize: 36, padding: "10px 26px", borderRadius: 12 }}>COMENTA Y DEFIENDE A TU SELECCIÓN</div>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 10 }}>
        {list.map(([n, t], i) => {
          const me = n === "04";
          const d = 10 + i * 8;
          return (
            <div key={n} style={{ display: "flex", alignItems: "center", gap: 24, width: 780, padding: "8px 24px", borderRadius: 14,
              background: me ? `linear-gradient(90deg, ${GOLD}, #B8892B)` : "rgba(10,16,30,.85)", color: me ? INK : WHITE,
              opacity: fade(f, d), transform: `translateY(${(1 - prog(f, d, d + 9)) * 40}px) scale(${me ? pop(f, d) * (1 + 0.02 * Math.sin(f / 6)) : 1})` }}>
              <div style={{ fontWeight: 900, fontSize: 46, width: 70 }}>{n}</div>
              <Flag team={t} width={100} frame={f} radius={6} />
              <div style={{ flex: 1, fontWeight: 900, fontSize: 46 }}>{TEAM_NAME[t]}</div>
              {me && <div style={{ fontWeight: 900, fontSize: 46 }}>?</div>}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 12, fontWeight: 600, fontSize: 22, color: DIM, opacity: fade(f, 20) }}>Clasificación propia, no oficial</div>
    </Stage>
  );
};

// ---------------------------------------------------------------------------- montaje
const ShotView: React.FC<{ shot: Shot; dur: number }> = ({ shot, dur }) => {
  const f = useCurrentFrame();
  const p = shot.props;
  const cam = interpolate(f, [0, dur], [1.0, 1.05], cl) * interpolate(f, [0, 6], [1.05, 1], cl);
  const flash = shot.hit ? interpolate(f, [0, 1, 5], [0.0, 0.55, 0], cl) : 0;
  const streak = shot.hit ? interpolate(f, [0, 10], [-400, 1500], cl) : -9999;
  let body: React.ReactNode = null;
  switch (shot.kind) {
    case "giants": body = <Giants f={f} />; break;
    case "question": body = <Question f={f} />; break;
    case "four": body = <Four f={f} />; break;
    case "team": body = <TeamCard f={f} dur={dur} p={p} />; break;
    case "chapter": body = <Chapter f={f} p={p} />; break;
    case "podium": body = <Podium f={f} p={p} />; break;
    case "quarters": body = <Quarters f={f} p={p} />; break;
    case "bars": body = <Bars f={f} dur={dur} />; break;
    case "words": body = <Words f={f} p={p} />; break;
    case "alert": body = <Alert f={f} p={p} />; break;
    case "ranking": body = <Ranking f={f} />; break;
    case "history": body = <History f={f} />; break;
    case "balance": body = <Balance f={f} />; break;
    case "score": body = <Score f={f} p={p} />; break;
    case "debate": body = <Debate f={f} p={p} />; break;
    case "final": body = <Final f={f} dur={dur} />; break;
  }
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: `scale(${cam})` }}>{body}</AbsoluteFill>
      <div style={{ position: "absolute", top: -200, left: streak, width: 160, height: 2400, transform: "rotate(18deg)", background: "linear-gradient(90deg, transparent, rgba(255,255,255,.35), transparent)" }} />
      <AbsoluteFill style={{ background: WHITE, opacity: flash }} />
    </AbsoluteFill>
  );
};

const SubView: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  const up = text.toUpperCase();
  const size = up.length > 26 ? 58 : up.length > 18 ? 66 : 74;
  return (
    <div style={{ position: "absolute", left: 70, right: 150, top: 1090, height: 210, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.06, textAlign: "center", color: WHITE, background: "rgba(5,7,13,.82)", borderRadius: 18, padding: "14px 30px",
        borderBottom: `6px solid ${GOLD}`, transform: `scale(${pop(f, 0)})`, opacity: fade(f, 0, 2) }}>{up}</div>
    </div>
  );
};

export const CuartoGigante: React.FC<{ safeGuides?: boolean; hideSubs?: boolean }> = ({ safeGuides = false, hideSubs = false }) => {
  const shots = timeline.shots as Shot[];
  const subs = timeline.subs as Sub[];
  return (
    <AbsoluteFill style={{ background: INK }}>
      <Audio src={staticFile("gigante_audio.wav")} />
      <Stadium />
      {shots.map((s, i) => {
        const from = fr(s.start);
        const dur = Math.max(1, (i + 1 < shots.length ? fr(shots[i + 1].start) : giganteFrames) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <ShotView shot={s} dur={dur} />
          </Sequence>
        );
      })}
      {!hideSubs && subs.map((s, i) => (
        <Sequence key={`s${i}`} from={fr(s.start)} durationInFrames={Math.max(1, fr(s.end) - fr(s.start))}>
          <SubView text={s.text} />
        </Sequence>
      ))}
      <Sequence from={giganteFrames - fr(1.2)}>
        <FadeOut />
      </Sequence>
      {safeGuides && (
        <AbsoluteFill style={{ pointerEvents: "none" }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 340, background: "#ff000033" }} />
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 610, background: "#ff000033" }} />
          <div style={{ position: "absolute", right: 0, top: 900, bottom: 0, width: 130, background: "#ff000033" }} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

const FadeOut: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: INK, opacity: interpolate(f, [0, fr(1.2)], [0, 1], cl) }} />;
};
