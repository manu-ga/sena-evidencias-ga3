import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing } from "remotion";
import timeline from "./timeline.json";

const NAVY = "#0E3A8A";
const SKY = "#1CA9E0";
const WHITE = "#FFFFFF";
const FONT = "Inter, 'Helvetica Neue', Arial, sans-serif";
const W = 1080;
const H = 1920;
const K = 1080 / 1086;            // el afiche mide 1086x1448: se ajusta al ancho del lienzo
const BASE_H = 1448 * K;
const fps = timeline.fps;
const fr = (s: number) => Math.round(s * fps);
export const nawhiFrames = Math.ceil(timeline.duration * fps);

const clampO = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (f: number, d = 0) => interpolate(f - d, [0, 5, 9], [0.85, 1.05, 1], { ...clampO, easing: Easing.out(Easing.quad) });
const fade = (f: number, d = 0, n = 3) => interpolate(f - d, [0, n], [0, 1], clampO);

type Cam = [number, number, number];
type ShotT = { kind: string; start: number; end: number; props: { a: Cam; b: Cam; target: [number, number]; chip?: string } };
type SubT = { text: string; start: number; end: number };

/** Coloca el afiche para que el punto (cx, cy) de la imagen caiga en `target` con zoom z, sin salirse del lienzo. */
const place = (cx: number, cy: number, z: number, tx: number, ty: number) => {
  let X = tx - z * cx * K;
  let Y = ty - z * cy * K;
  X = Math.min(0, Math.max(W - z * W, X));
  const h = z * BASE_H;
  // con zoom, el borde inferior del afiche puede subir hasta 400 px (se ve el fondo rayado) para que lo importante quede sobre los subtítulos
  Y = h >= H ? Math.min(0, Math.max(H - h - 400, Y)) : Math.min(H - h, Math.max(0, Y));
  return { X, Y };
};

const Backdrop: React.FC = () => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, #EAF6FD, #FFFFFF 40%, #D6EEFA)` }}>
    <AbsoluteFill style={{ background: `repeating-linear-gradient(115deg, ${SKY}22 0 90px, transparent 90px 180px)` }} />
  </AbsoluteFill>
);

const Chip: React.FC<{ text: string; f: number }> = ({ text, f }) => (
  <div style={{ position: "absolute", top: 290, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: fade(f, 2), transform: `scale(${pop(f, 2)})` }}>
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: text.length > 22 ? 40 : 52, color: WHITE, background: NAVY, borderRadius: 60, padding: "16px 44px", boxShadow: "0 10px 40px rgba(14,58,138,.35)", border: `4px solid ${WHITE}`, letterSpacing: "0.01em" }}>
      {text}
    </div>
  </div>
);

const CamShot: React.FC<{ shot: ShotT; dur: number; end?: boolean }> = ({ shot, dur, end }) => {
  const f = useCurrentFrame();
  const { a, b, target } = shot.props;
  const u = interpolate(f, [0, dur], [0, 1], { ...clampO, easing: Easing.inOut(Easing.quad) });
  const cx = a[0] + (b[0] - a[0]) * u;
  const cy = a[1] + (b[1] - a[1]) * u;
  const z = a[2] + (b[2] - a[2]) * u;
  const { X, Y } = place(cx, cy, z, target[0], target[1]);
  const kick = interpolate(f, [0, 6], [1.035, 1], clampO);
  return (
    <AbsoluteFill style={{ transform: `scale(${kick})` }}>
      <Backdrop />
      <div style={{ position: "absolute", left: 0, top: 0, width: W, height: BASE_H, transform: `translate(${X}px, ${Y}px) scale(${z})`, transformOrigin: "0 0" }}>
        <Img src={staticFile("nawhi.jpg")} style={{ width: W, height: BASE_H, display: "block" }} />
      </div>
      {shot.props.chip && <Chip text={shot.props.chip} f={f} />}
      {end && <EndCard f={f} />}
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill>
    <div style={{ position: "absolute", left: 0, right: 0, top: 700, bottom: 0, background: `linear-gradient(180deg, transparent, ${NAVY}EE 30%, ${NAVY})` }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 800, textAlign: "center", fontFamily: FONT, color: WHITE, transform: `scale(${pop(f, 4)})`, opacity: fade(f, 4) }}>
      <div style={{ fontWeight: 900, fontSize: 190, letterSpacing: "0.02em", lineHeight: 1 }}>NAWHI</div>
      <div style={{ display: "inline-block", marginTop: 18, background: SKY, color: NAVY, fontWeight: 900, fontSize: 56, padding: "8px 38px", borderRadius: 50, letterSpacing: "0.06em" }}>ASHWAGANDHA</div>
    </div>
    <div style={{ position: "absolute", left: 90, right: 90, top: 1130, textAlign: "center", fontFamily: FONT, fontWeight: 600, fontSize: 28, lineHeight: 1.3, color: "#DCE8FA", opacity: fade(f, 14, 6) }}>
      Producto homeopático de venta libre. Lee las indicaciones. Si tienes una condición de salud o tomas medicamentos, consulta a tu médico.
    </div>
  </AbsoluteFill>
);

const Sub: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  const up = text.toUpperCase();
  const size = up.length > 28 ? 62 : up.length > 20 ? 70 : 80;
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 1250, height: 240, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.06, textAlign: "center", color: WHITE, background: `${NAVY}F0`, borderRadius: 36, padding: "16px 36px", border: `4px solid ${WHITE}`, boxShadow: "0 10px 36px rgba(0,0,0,.3)", transform: `scale(${pop(f, 0)})`, opacity: fade(f, 0, 2) }}>
        {up}
      </div>
    </div>
  );
};

export const NawhiReel: React.FC<{ safeGuides?: boolean }> = ({ safeGuides = false }) => {
  const shots = timeline.shots as unknown as ShotT[];
  const subs = timeline.subs as unknown as SubT[];
  return (
    <AbsoluteFill style={{ background: "#fff" }}>
      <Audio src={staticFile("nawhi_audio.wav")} />
      {shots.map((s, i) => {
        const from = fr(s.start);
        const dur = Math.max(1, (i + 1 < shots.length ? fr(shots[i + 1].start) : nawhiFrames) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <CamShot shot={s} dur={dur} end={s.kind === "end"} />
          </Sequence>
        );
      })}
      {subs.map((s, i) => (
        <Sequence key={`s${i}`} from={fr(s.start)} durationInFrames={Math.max(1, fr(s.end) - fr(s.start))}>
          <Sub text={s.text} />
        </Sequence>
      ))}
      {safeGuides && (
        <AbsoluteFill style={{ pointerEvents: "none" }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 250, background: "#ff000022" }} />
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 420, background: "#ff000022" }} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
