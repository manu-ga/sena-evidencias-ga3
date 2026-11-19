import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, H, W, sideColor } from "./theme";
import {
  AdIcon, BookmarkIcon, Candles, CheckIcon, Chip, FunnelIcon, WarnIcon, XIcon, fadeIn, outlined, pop, prog,
} from "./ui";

export type ShotP = { props: Record<string, any>; dur: number };

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const center: React.CSSProperties = { alignItems: "center", justifyContent: "center", fontFamily: FONT };
/** Escenario con el centro a y≈710: todo el contenido queda sobre los subtítulos (y≈1150-1350). */
const STAGE: React.CSSProperties = { ...center, display: "flex", background: C.bg, paddingBottom: 500, boxSizing: "border-box" };

/** Gran texto de impacto con pop de entrada. */
const Big: React.FC<{ text: string; size: number; color?: string; delay?: number; style?: React.CSSProperties }> = ({
  text, size, color = C.white, delay = 0, style,
}) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.0, color, textAlign: "center", letterSpacing: "-0.02em",
        transform: `scale(${pop(f, delay)})`, opacity: fadeIn(f, delay, 3), ...outlined(size * 0.07), ...style,
      }}
    >
      {text}
    </div>
  );
};

const Glow: React.FC<{ color: string; x?: number; y?: number; r?: number; o?: number }> = ({ color, x = W / 2, y = H / 2 - 100, r = 900, o = 0.35 }) => (
  <div style={{ position: "absolute", left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: "50%", background: `radial-gradient(${color}${Math.round(o * 255).toString(16).padStart(2, "0")}, transparent 62%)` }} />
);

// ------------------------------------------------------------------ 1. pantalla partida con choque
export const Slam: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const t = prog(f, 0, 7);
  const hit = f >= 7 ? Math.max(0, 1 - (f - 7) / 12) : 0;
  const sx = Math.sin(f * 2.3) * 20 * hit;
  const sy = Math.cos(f * 3.1) * 14 * hit;
  const half = (side: "ads" | "trading") => {
    const left = side === "ads";
    const col = left ? C.ads : C.trading;
    const x = interpolate(t, [0, 1], [left ? -W / 2 - 40 : W / 2 + 40, 0]);
    return (
      <div style={{ position: "absolute", top: 0, [left ? "left" : "right"]: 0, width: W / 2, height: H, transform: `translateX(${x}px)`,
        background: `linear-gradient(${left ? 160 : 200}deg, ${col}EE, ${col}55 60%, #0B0F17 100%)`, display: "flex", flexDirection: "column", ...center, justifyContent: "flex-start", paddingTop: 290 }}>
        {left ? <AdIcon size={220} color={C.white} /> : <Candles width={280} height={200} seed={11} n={9} shown={f / 3} />}
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: left ? 140 : 100, color: C.white, marginTop: 16, ...outlined(12) }}>{left ? props.left : props.right}</div>
        {left && <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 48, color: C.white, letterSpacing: "0.12em", marginTop: 6 }}>{props.leftSub}</div>}
      </div>
    );
  };
  return (
    <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px)` }}>
      {half("ads")}
      {half("trading")}
      <div style={{ position: "absolute", left: W / 2 - 6, top: 0, width: 12, height: H, background: C.white, opacity: 0.2 + hit * 0.8 }} />
      <AbsoluteFill style={{ background: C.white, opacity: f >= 7 && f < 10 ? 0.55 * (1 - (f - 7) / 3) : 0 }} />
      <AbsoluteFill style={{ ...center, display: "flex", justifyContent: "flex-start", paddingTop: 790 }}>
        <div style={{ background: `${C.bg}E6`, border: `6px solid ${C.white}`, borderRadius: 40, padding: "26px 50px", transform: `scale(${pop(f, 9)})`, opacity: fadeIn(f, 9, 3) }}>
          <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 112, lineHeight: 1.02, color: C.white, textAlign: "center" }}>
            {String(props.title).split(" TU ").length > 1 ? (<>¿DÓNDE VA<br />TU PLATA?</>) : props.title}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 2. zoom rápido a un lado
export const ZoomSide: React.FC<ShotP> = ({ props, dur }) => {
  const f = useCurrentFrame();
  const col = sideColor(props.side);
  const z = interpolate(f, [0, dur], [1.22, 1.0], { ...clampOpts });
  return (
    <AbsoluteFill style={{ ...STAGE, background: `linear-gradient(170deg, ${col}CC, ${C.bg} 78%)`, transform: `scale(${z})` }}>
      <div style={{ transform: `scale(${pop(f, 0)})` }}>
        {props.side === "trading" ? <Candles width={560} height={300} seed={5} n={14} shown={f / 1.4} /> : <FunnelIcon size={360} color={C.white} />}
      </div>
      <Big text={props.label} size={150} delay={3} style={{ marginTop: 36 }} />
      <Chip text={props.sub} color={C.white} size={46} solid style={{ marginTop: 26, color: C.bg, opacity: fadeIn(f, 6) }} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 3. palabra clave gigante
export const Keyword: React.FC<ShotP> = ({ props, dur }) => {
  const f = useCurrentFrame();
  const col = sideColor(props.side);
  const text = String(props.text);
  const size = text.length > 17 ? 118 : text.length > 11 ? 142 : 176;
  const bar = prog(f, 3, 14);
  const words = text.split(" ");
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={col} o={0.4} r={760} y={720} />
      <div style={{ position: "absolute", top: 330, opacity: fadeIn(f, 2) }}>
        <Chip text={props.tag} color={col} size={42} />
      </div>
      <div style={{ transform: `translateY(${interpolate(prog(f, 0, 7), [0, 1], [90, 0])}px) scale(${interpolate(f, [0, dur], [1, 1.06], clampOpts)})`, textAlign: "center" }}>
        {words.length > 2 ? (
          <>
            <Big text={words.slice(0, Math.ceil(words.length / 2)).join(" ")} size={size} color={C.white} />
            <Big text={words.slice(Math.ceil(words.length / 2)).join(" ")} size={size} color={col} delay={2} />
          </>
        ) : (
          <Big text={text} size={size} color={C.white} />
        )}
        <div style={{ height: 18, width: 760 * bar, background: col, borderRadius: 9, margin: "30px auto 0", boxShadow: `0 0 40px ${col}` }} />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 4. reloj 0:30 + dos columnas
export const ClockCols: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const sec = Math.max(0, Math.round(interpolate(f, [0, 28], [props.seconds ?? 30, 0], clampOpts)));
  const shrink = prog(f, 26, 34);
  const colsIn = (i: number) => prog(f, 30 + i * 4, 36 + i * 4);
  const rows = {
    ads: ["CREATIVO", "ÁNGULO", "CONVERSIÓN"],
    trading: ["LECTURA", "RIESGO", "DISCIPLINA"],
  };
  const col = (side: "ads" | "trading", idx: number) => {
    const c = sideColor(side);
    const x = interpolate(colsIn(idx), [0, 1], [side === "ads" ? -520 : 520, 0]);
    return (
      <div style={{ width: 460, transform: `translateX(${x}px)`, opacity: colsIn(idx) }}>
        <div style={{ background: c, color: C.bg, fontFamily: FONT, fontWeight: 900, fontSize: 56, textAlign: "center", padding: "20px 0", borderRadius: "28px 28px 0 0", letterSpacing: "0.04em" }}>
          {side === "ads" ? "ADS" : "TRADING"}
        </div>
        {rows[side].map((r, i) => (
          <div key={r} style={{ background: C.panel, border: `4px solid ${c}`, borderTop: i === 0 ? `4px solid ${c}` : "none", color: C.white, fontFamily: FONT, fontWeight: 800, fontSize: 46, padding: "34px 0", textAlign: "center",
            borderRadius: i === 2 ? "0 0 28px 28px" : 0, opacity: prog(f, 36 + idx * 3 + i * 4, 42 + idx * 3 + i * 4), transform: `translateY(${(1 - prog(f, 36 + idx * 3 + i * 4, 44 + idx * 3 + i * 4)) * 24}px)` }}>
            {r}
          </div>
        ))}
      </div>
    );
  };
  const clockScale = interpolate(shrink, [0, 1], [1.8, 0.8]);
  const clockY = interpolate(shrink, [0, 1], [560, 360]);
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: FONT }}>
      <Glow color={C.ads} x={120} y={900} r={640} o={0.25} />
      <Glow color={C.trading} x={W - 120} y={900} r={640} o={0.25} />
      <div style={{ position: "absolute", left: 0, right: 0, top: clockY, display: "flex", justifyContent: "center", transform: `scale(${clockScale})` }}>
        <div style={{ position: "relative", width: 360, height: 360 }}>
          <svg width={360} height={360} style={{ position: "absolute" }}>
            <circle cx={180} cy={180} r={160} fill="none" stroke="#ffffff1c" strokeWidth={22} />
            <circle cx={180} cy={180} r={160} fill="none" stroke={C.white} strokeWidth={22} strokeLinecap="round" strokeDasharray={1005} strokeDashoffset={1005 * (1 - sec / (props.seconds ?? 30))} transform="rotate(-90 180 180)" />
          </svg>
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 130, color: C.white, ...outlined(8) }}>
            0:{String(sec).padStart(2, "0")}
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 590, display: "flex", justifyContent: "center", gap: 40 }}>
        {col("ads", 0)}
        {col("trading", 1)}
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 5. embudo de anuncios
const FunnelScene: React.FC<{ label: string; tags?: string[]; leak?: boolean; text?: string }> = ({ label, tags = [], leak = false, text }) => {
  const f = useCurrentFrame();
  const S = 520 / 640;
  const dots = Array.from({ length: 16 }, (_, i) => i);
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={leak ? C.red : C.ads} o={0.35} r={760} y={650} />
      <div style={{ position: "absolute", top: 300, opacity: fadeIn(f, 2) }}><Chip text={label} color={C.ads} size={42} /></div>
      <div style={{ position: "absolute", top: 390, left: (W - 520) / 2, width: 520, height: 520, transform: `scale(${pop(f, 0)})` }}>
        <FunnelIcon size={520} color={leak ? C.red : C.ads} stroke={12} />
        {dots.map((i) => {
          const phase = ((f * 0.045 + i * 0.37) % 1);
          const gone = leak && phase > 0.5;
          const x = (gone ? 320 + (i % 2 ? 1 : -1) * (phase - 0.5) * 760 : 320 + Math.sin(i * 2.1) * 120 * (1 - phase * 0.8)) * S;
          const y = (80 + phase * 520 + (gone ? (phase - 0.5) * 260 : 0)) * S;
          return <div key={i} style={{ position: "absolute", left: x - 10, top: y, width: 20, height: 20, borderRadius: 10, background: gone ? C.red : C.ads, opacity: gone ? Math.max(0, 1 - (phase - 0.5) * 1.8) : 1, boxShadow: `0 0 18px ${gone ? C.red : C.ads}` }} />;
        })}
      </div>
      {tags[0] && <div style={{ position: "absolute", left: 60, top: 500, transform: `translateX(${(1 - prog(f, 4, 12)) * -400}px)` }}><Chip text={tags[0]} color={C.ads} size={48} solid /></div>}
      {tags[1] && <div style={{ position: "absolute", right: 60, top: 760, transform: `translateX(${(1 - prog(f, 8, 16)) * 400}px)` }}><Chip text={tags[1]} color={C.ads} size={48} solid /></div>}
      {text && <div style={{ position: "absolute", top: 950, left: 90, right: 90 }}><Big text={text} size={74} color={C.red} delay={4} /></div>}
    </AbsoluteFill>
  );
};
export const Funnel: React.FC<ShotP> = ({ props }) => <FunnelScene label={props.label} tags={props.tags} />;
export const Leak: React.FC<ShotP> = ({ props }) => <FunnelScene label="TRÁFICO" leak text={props.text} />;

// ------------------------------------------------------------------ 6. dos palabras que alternan
export const Duo: React.FC<ShotP> = ({ props, dur }) => {
  const f = useCurrentFrame();
  const second = f > dur / 2;
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={second ? C.red : C.ads} o={0.4} r={760} />
      <div style={{ opacity: second ? 0.35 : 1, transform: `scale(${second ? 0.8 : 1})` }}><Big text={props.a} size={170} color={C.ads} /></div>
      <div style={{ fontFamily: FONT, fontSize: 70, fontWeight: 900, color: C.dim, margin: "10px 0" }}>o</div>
      <div style={{ opacity: second ? 1 : 0.35 }}><Big text={props.b} size={170} color={C.red} delay={second ? Math.round(dur / 2) : 0} /></div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 7. lista de palabras que aparecen una a una
export const Triple: React.FC<ShotP> = ({ props, dur }) => {
  const f = useCurrentFrame();
  const words: string[] = props.words;
  const col = sideColor(props.side);
  const n = words.length;
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={col} o={0.35} r={800} />
      <div style={{ position: "absolute", top: 330 }}><Chip text={props.tag} color={col} size={42} /></div>
      {words.map((w, i) => {
        const at = Math.round((dur * i) / n);
        const active = f >= at && (i === n - 1 || f < Math.round((dur * (i + 1)) / n));
        if (f < at) return <div key={w} style={{ height: 200 }} />;
        return (
          <div key={w} style={{ opacity: active ? 1 : 0.4, height: 200, display: "flex", alignItems: "center", gap: 22 }}>
            <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 52, color: col, opacity: 0.9, width: 40 }}>{i + 1}</div>
            <Big text={w} size={w.length > 12 ? 86 : 132} color={active ? C.white : col} delay={at} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 8. anuncio que no conecta
export const NoConnect: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const shake = f > 8 ? Math.sin(f * 2.5) * 10 * Math.max(0, 1 - (f - 8) / 14) : 0;
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={C.red} o={0.3} r={700} />
      <div style={{ transform: `translateX(${shake}px) scale(${pop(f, 0)})`, position: "relative", marginTop: 20 }}>
        <AdIcon size={440} color={C.ads} stroke={11} />
        <div style={{ position: "absolute", right: -40, bottom: -10, opacity: fadeIn(f, 8, 2), transform: `scale(${pop(f, 8)})` }}><XIcon size={180} /></div>
      </div>
      <div style={{ marginTop: 30 }}><Big text={props.text} size={116} color={C.red} delay={6} /></div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 9. velas / trading
export const CandlesShot: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const tags: string[] = props.tags ?? [];
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={C.trading} o={0.33} r={780} y={760} />
      <div style={{ position: "absolute", top: 300, opacity: fadeIn(f, 2) }}><Chip text={props.label} color={C.trading} size={42} /></div>
      <div style={{ position: "absolute", top: 410, left: 90, transform: `scale(${pop(f, 0)})` }}>
        <Candles width={900} height={440} seed={21} n={22} shown={f / 1.6} />
      </div>
      {tags[0] && <div style={{ position: "absolute", left: 60, top: 880, transform: `translateX(${(1 - prog(f, 6, 14)) * -500}px)` }}><Chip text={tags[0]} color={C.trading} size={52} solid /></div>}
      {tags[1] && <div style={{ position: "absolute", right: 60, top: 970, transform: `translateX(${(1 - prog(f, 11, 19)) * 600}px)` }}><Chip text={tags[1]} color={C.trading} size={46} solid /></div>}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 10. mal lote → cuenta a cero
export const Crash: React.FC<ShotP> = ({ props, dur }) => {
  const f = useCurrentFrame();
  const mid = Math.round(dur * 0.45);
  const crash = prog(f, 6, 22);
  const bal = Math.round(interpolate(f, [mid, mid + 22], [1000, 0], { ...clampOpts }));
  const phase2 = f >= mid;
  const shake = f > mid && f < mid + 14 ? Math.sin(f * 3) * 14 : 0;
  return (
    <AbsoluteFill style={{ ...STAGE, justifyContent: "flex-start", paddingBottom: 0, transform: `translateX(${shake}px)` }}>
      <Glow color={C.red} o={phase2 ? 0.45 : 0.28} r={780} y={700} />
      <div style={{ marginTop: 400 }}><Candles width={880} height={400} seed={33} n={20} shown={20} crash={crash} /></div>
      <div style={{ marginTop: 40 }}>
        {!phase2 ? <Big text={props.text} size={128} color={C.white} delay={6} /> : <Big text={props.text2} size={118} color={C.red} delay={mid} />}
      </div>
      {phase2 && (
        <div style={{ marginTop: 18, display: "flex", alignItems: "center", gap: 24, opacity: fadeIn(f, mid + 2) }}>
          <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 84, color: bal === 0 ? C.red : C.white, ...outlined(7) }}>${bal.toLocaleString("en-US")}</div>
          <Chip text={props.sub} color={C.red} size={34} solid />
        </div>
      )}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 11. comparación con checks
export const Check: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const stage = props.stage as number;
  const card = (side: "ads" | "trading", text: string, checked: boolean, delay: number) => {
    const c = sideColor(side);
    const x = interpolate(prog(f, delay, delay + 8), [0, 1], [side === "ads" ? -300 : 300, 0]);
    const lit = checked ? 1 : 0.55;
    return (
      <div style={{ width: 900, background: checked ? `${c}2A` : C.panel, border: `6px solid ${c}`, borderRadius: 36, padding: "36px 44px", display: "flex", alignItems: "center", justifyContent: "space-between",
        opacity: prog(f, delay, delay + 6) * lit, transform: `translateX(${x}px) scale(${checked ? 1.03 : 1})`, boxShadow: checked ? `0 0 60px ${c}88` : "none" }}>
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 62, color: C.white, lineHeight: 1.05 }}>
          <div style={{ fontSize: 34, color: c, letterSpacing: "0.1em", marginBottom: 8 }}>{side === "ads" ? "ADS" : "TRADING"}</div>
          {text}
        </div>
        <div style={{ transform: `scale(${checked ? pop(f, 2) : 0.0})`, width: 150, display: "flex", justifyContent: "center" }}>
          {checked && <CheckIcon size={150} color={c} />}
        </div>
      </div>
    );
  };
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={C.ads} x={100} y={640} r={600} o={0.25} />
      <Glow color={C.trading} x={W - 100} y={920} r={600} o={0.25} />
      <div style={{ position: "absolute", top: 300, opacity: fadeIn(f, 1) }}><Chip text={props.label} color={C.white} size={42} /></div>
      <div style={{ display: "flex", flexDirection: "column", gap: 28, alignItems: "center", marginTop: 40 }}>
        {card("ads", props.left, stage >= 1, 0)}
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 64, color: C.dim }}>VS</div>
        {card("trading", props.right, stage >= 2, 3)}
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 12. alerta roja parpadeante
export const Alert: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const blink = 0.55 + 0.45 * Math.sin(f * 1.1) ** 2;
  return (
    <AbsoluteFill style={STAGE}>
      <AbsoluteFill style={{ background: `radial-gradient(transparent 38%, ${C.red}${Math.round(blink * 150).toString(16).padStart(2, "0")})` }} />
      <div style={{ border: `${14 * blink}px solid ${C.red}`, position: "absolute", inset: 30, borderRadius: 40, opacity: blink }} />
      <div style={{ transform: `scale(${pop(f, 0) * (0.96 + 0.06 * blink)})`, marginTop: 0 }}><WarnIcon size={380} color={C.red} /></div>
      <div style={{ opacity: 0.5 + 0.5 * blink, marginTop: 40 }}><Big text={props.text} size={104} color={C.white} delay={3} /></div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 13. tachón sobre "Entrar sin plan de pérdida"
export const Strike: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const blink = 0.6 + 0.4 * Math.sin(f * 1.0) ** 2;
  const line = prog(f, 10, 20);
  return (
    <AbsoluteFill style={STAGE}>
      <AbsoluteFill style={{ background: `radial-gradient(transparent 45%, ${C.red}${Math.round(blink * 110).toString(16).padStart(2, "0")})` }} />
      <div style={{ opacity: blink, marginTop: -40 }}><Chip text="⚠ ALERTA" color={C.red} size={50} solid /></div>
      <div style={{ position: "relative", marginTop: 40, transform: `scale(${pop(f, 0)})`, textAlign: "center", width: 940 }}>
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 104, color: C.white, lineHeight: 1.08, ...outlined(8) }}>{props.text}</div>
        <div style={{ position: "absolute", left: -10, top: "50%", height: 22, width: `${line * 104}%`, background: C.red, borderRadius: 11, boxShadow: `0 0 40px ${C.red}`, transform: "rotate(-4deg)" }} />
      </div>
      <div style={{ marginTop: 36, opacity: fadeIn(f, 16, 4), transform: `scale(${pop(f, 16)})` }}><XIcon size={160} /></div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 14. cierre / CTA
export const Cta: React.FC<ShotP> = ({ props }) => {
  const f = useCurrentFrame();
  const stage = props.stage as string;
  if (stage === "guardar") {
    const press = f > 18 && f < 26 ? 0.93 : 1;
    return (
      <AbsoluteFill style={STAGE}>
        <Glow color={C.ads} x={200} o={0.3} r={700} />
        <Glow color={C.trading} x={W - 200} y={H / 2 + 100} o={0.3} r={700} />
        <div style={{ transform: `scale(${pop(f, 0) * press})`, display: "flex", alignItems: "center", gap: 30, background: C.white, borderRadius: 120, padding: "36px 70px", marginTop: 0, boxShadow: `0 0 90px ${C.white}55` }}>
          <BookmarkIcon size={130} color={C.bg} />
          <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 104, color: C.bg, letterSpacing: "0.02em" }}>GUARDAR</div>
        </div>
        <div style={{ marginTop: 36, opacity: fadeIn(f, 6) }}><Chip text="ESTE VIDEO" color={C.white} size={52} /></div>
      </AbsoluteFill>
    );
  }
  if (stage === "comenta") {
    return (
      <AbsoluteFill style={STAGE}>
        <Glow color={C.ads} o={0.4} r={800} />
        <div style={{ marginTop: 0, transform: `scale(${pop(f, 0)})`, background: C.panel, border: `6px solid ${C.white}`, borderRadius: "70px 70px 70px 16px", padding: "50px 70px", textAlign: "center", position: "relative" }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 56, color: C.dim, letterSpacing: "0.1em" }}>COMENTA</div>
          <div style={{ marginTop: 12, background: C.ads, color: C.bg, fontFamily: FONT, fontWeight: 900, fontSize: 112, padding: "10px 40px", borderRadius: 40, transform: `scale(${pop(f, 5)})`, boxShadow: `0 0 80px ${C.ads}AA` }}>DIFERENCIA</div>
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={STAGE}>
      <Glow color={C.ads} x={160} y={800} o={0.35} r={620} />
      <Glow color={C.trading} x={W - 160} y={800} o={0.35} r={620} />
      <div style={{ display: "flex", gap: 24, marginTop: -60, alignItems: "center" }}>
        <div style={{ transform: `translateX(${(1 - prog(f, 0, 8)) * -300}px)` }}><Chip text="ADS" color={C.ads} size={62} solid /></div>
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 56, color: C.dim }}>VS</div>
        <div style={{ transform: `translateX(${(1 - prog(f, 2, 10)) * 300}px)` }}><Chip text="TRADING" color={C.trading} size={62} solid /></div>
      </div>
      <div style={{ marginTop: 44 }}><Big text="¿CUÁL ENCAJA CONTIGO?" size={96} color={C.white} delay={6} style={{ maxWidth: 900 }} /></div>
      <div style={{ position: "absolute", top: 1040, left: 90, right: 90, textAlign: "center", fontFamily: FONT, fontWeight: 600, fontSize: 27, color: C.dim, opacity: fadeIn(f, 12) }}>
        Contenido educativo. No es asesoría financiera: el trading y la publicidad pagada implican riesgo de pérdida.
      </div>
    </AbsoluteFill>
  );
};

export const SHOTS: Record<string, React.FC<ShotP>> = {
  slam: Slam, zoomside: ZoomSide, keyword: Keyword, clockcols: ClockCols, funnel: Funnel, leak: Leak, duo: Duo, triple: Triple,
  noconnect: NoConnect, candles: CandlesShot, crash: Crash, check: Check, alert: Alert, strike: Strike, cta: Cta,
};
