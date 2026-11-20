import React from "react";
import { Easing, interpolate } from "remotion";
import { C, FONT } from "./theme";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);

/** 0→1 con desaceleración (ease-out) entre los fotogramas a y b. */
export const prog = (f: number, a: number, b: number): number =>
  interpolate(f, [a, b], [0, 1], { ...clampOpts, easing: easeOut });

/** Pop de escala 85% → 105% → 100% que empieza en `delay`. */
export const pop = (f: number, delay = 0): number =>
  interpolate(f - delay, [0, 5, 9], [0.85, 1.05, 1], { ...clampOpts, easing: Easing.out(Easing.quad) });

export const fadeIn = (f: number, delay = 0, len = 3): number => interpolate(f - delay, [0, len], [0, 1], clampOpts);

/** Texto con contorno oscuro para que se lea sobre cualquier fondo. */
export const outlined = (stroke = 10): React.CSSProperties => ({
  WebkitTextStroke: `${stroke}px ${C.bg}`,
  paintOrder: "stroke fill",
  textShadow: "0 8px 24px rgba(0,0,0,.45)",
});

export const Chip: React.FC<{ text: string; color: string; size?: number; solid?: boolean; style?: React.CSSProperties }> = ({
  text, color, size = 40, solid = false, style,
}) => (
  <div
    style={{
      fontFamily: FONT, fontWeight: 800, fontSize: size, letterSpacing: "0.06em", color: solid ? C.bg : color,
      background: solid ? color : `${color}22`, border: `4px solid ${color}`, borderRadius: size, padding: `${size * 0.22}px ${size * 0.7}px`,
      whiteSpace: "nowrap", ...style,
    }}
  >
    {text}
  </div>
);

// ------------------------------------------------------------------ íconos vectoriales
type IconProps = { size?: number; color?: string; stroke?: number };

export const FunnelIcon: React.FC<IconProps> = ({ size = 300, color = C.ads, stroke = 10 }) => (
  <svg width={size} height={size} viewBox="0 0 200 200" fill="none" stroke={color} strokeWidth={stroke / 2.2} strokeLinejoin="round" strokeLinecap="round">
    <path d="M14 26h172l-66 76v58l-40 22v-80z" fill={`${color}33`} />
    <path d="M40 54h120M62 80h76" opacity=".7" />
  </svg>
);

export const AdIcon: React.FC<IconProps> = ({ size = 300, color = C.ads, stroke = 10 }) => (
  <svg width={size} height={size} viewBox="0 0 200 200" fill="none" stroke={color} strokeWidth={stroke / 2.2} strokeLinejoin="round" strokeLinecap="round">
    <rect x="22" y="34" width="156" height="118" rx="18" fill={`${color}22`} />
    <path d="M84 70l44 24-44 24z" fill={color} />
    <path d="M22 172h156" opacity=".6" />
    <text x="30" y="58" fontSize="18" fontWeight="800" fill={color} stroke="none" fontFamily={FONT}>AD</text>
  </svg>
);

export const CheckIcon: React.FC<IconProps> = ({ size = 160, color = C.white, stroke = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={stroke / 2} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="50" cy="50" r="44" fill={`${color}22`} />
    <path d="M28 52l16 16 30-34" />
  </svg>
);

export const WarnIcon: React.FC<IconProps> = ({ size = 300, color = C.red, stroke = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={stroke / 2.4} strokeLinecap="round" strokeLinejoin="round">
    <path d="M50 10L94 88H6z" fill={`${color}33`} />
    <path d="M50 38v26" />
    <circle cx="50" cy="76" r="1.5" fill={color} />
  </svg>
);

export const BookmarkIcon: React.FC<IconProps> = ({ size = 160, color = C.white, stroke = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={stroke / 2.4} strokeLinecap="round" strokeLinejoin="round">
    <path d="M26 10h48v82L50 70 26 92z" fill={color} fillOpacity=".15" />
  </svg>
);

export const XIcon: React.FC<IconProps> = ({ size = 140, color = C.red, stroke = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={stroke / 2.2} strokeLinecap="round">
    <circle cx="50" cy="50" r="44" fill={`${color}22`} />
    <path d="M32 32l36 36M68 32L32 68" />
  </svg>
);

// ------------------------------------------------------------------ velas japonesas (determinista)
export const makeCandles = (seed: number, n: number, start = 100): { o: number; c: number; h: number; l: number }[] => {
  let s = seed;
  const rnd = () => ((s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296);
  let p = start;
  const out = [];
  for (let i = 0; i < n; i++) {
    const o = p;
    const c = o + (rnd() - 0.46) * 16;
    const h = Math.max(o, c) + rnd() * 7;
    const l = Math.min(o, c) - rnd() * 7;
    out.push({ o, c, h, l });
    p = c;
  }
  return out;
};

export const Candles: React.FC<{ width: number; height: number; seed?: number; n?: number; shown: number; crash?: number }> = ({
  width, height, seed = 7, n = 22, shown, crash = 0,
}) => {
  const data = makeCandles(seed, n);
  const lo = Math.min(...data.map((d) => d.l)) - 25;
  const hi = Math.max(...data.map((d) => d.h)) + 6;
  const y = (v: number) => height - ((v - lo) / (hi - lo)) * height;
  const step = width / n;
  return (
    <svg width={width} height={height} style={{ overflow: "visible" }}>
      {[0.25, 0.5, 0.75].map((g) => (
        <line key={g} x1={0} x2={width} y1={height * g} y2={height * g} stroke="#ffffff14" strokeWidth={2} />
      ))}
      {data.map((d, i) => {
        const vis = Math.max(0, Math.min(1, shown - i));
        if (vis <= 0) return null;
        const up = d.c >= d.o;
        const col = up ? "#22C55E" : C.red;
        const x = i * step + step / 2;
        return (
          <g key={i} opacity={vis} transform={`translate(0 ${(1 - vis) * 30})`}>
            <line x1={x} x2={x} y1={y(d.h)} y2={y(d.l)} stroke={col} strokeWidth={4} />
            <rect x={x - step * 0.3} width={step * 0.6} y={y(Math.max(d.o, d.c))} height={Math.max(5, Math.abs(y(d.o) - y(d.c)))} fill={col} rx={3} />
          </g>
        );
      })}
      {crash > 0 && (
        <g opacity={Math.min(1, crash * 2)}>
          <rect x={width - step * 1.9} width={step * 1.1} y={y(hi - 4) + 10} height={(height - y(hi - 4)) * 0.85 * crash} fill={C.red} rx={4} />
          <line x1={width - step * 1.35} x2={width - step * 1.35} y1={y(hi - 4) - 18} y2={height + 20} stroke={C.red} strokeWidth={5} />
        </g>
      )}
    </svg>
  );
};
