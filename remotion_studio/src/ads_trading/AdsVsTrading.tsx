import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate } from "remotion";
import timeline from "./timeline.json";
import { SHOTS } from "./shots";
import { SubtitleChunk } from "./Subtitles";
import { C, FONT, H, SUB_Y, W } from "./theme";

type Shot = { kind: string; start: number; end: number; props: Record<string, any> };
type Sub = { text: string; start: number; end: number; side: string; emph?: boolean };

const fps = timeline.fps;
const fr = (s: number) => Math.round(s * fps);

export const durationInFrames = Math.ceil(timeline.duration * fps);

/** Fondo permanente: color #0B0F17, cuadrícula sutil y dos halos (naranja a la izquierda, cian a la derecha). */
const Backdrop: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(#ffffff0d 2px, transparent 2px), linear-gradient(90deg, #ffffff0d 2px, transparent 2px)", backgroundSize: "90px 90px", backgroundPosition: `0px ${f * 0.8}px`, opacity: 0.5 }} />
      <div style={{ position: "absolute", left: -500, top: 500, width: 1100, height: 1100, borderRadius: "50%", background: `radial-gradient(${C.ads}30, transparent 65%)` }} />
      <div style={{ position: "absolute", right: -500, top: 700, width: 1100, height: 1100, borderRadius: "50%", background: `radial-gradient(${C.trading}30, transparent 65%)` }} />
    </AbsoluteFill>
  );
};

/** Cada plano entra con un "kick" de zoom rápido (corte dinámico). */
const ShotWrap: React.FC<{ shot: Shot; dur: number }> = ({ shot, dur }) => {
  const f = useCurrentFrame();
  const Comp = SHOTS[shot.kind];
  const kick = interpolate(f, [0, 6], [1.045, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ transform: `scale(${kick})` }}>
      <Comp props={shot.props} dur={dur} />
    </AbsoluteFill>
  );
};

const SafeGuides: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 270, background: "#ff000022", borderBottom: "3px dashed red" }} />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 480, background: "#ff000022", borderTop: "3px dashed red" }} />
    <div style={{ position: "absolute", left: 0, width: 60, top: 0, bottom: 0, background: "#ff000022" }} />
    <div style={{ position: "absolute", right: 0, width: 130, top: 0, bottom: 0, background: "#ff000022" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: SUB_Y, borderTop: "2px dashed yellow", fontFamily: FONT, color: "yellow", fontSize: 24 }}>centro de subtítulos</div>
  </AbsoluteFill>
);

export const AdsVsTrading: React.FC<{ safeGuides?: boolean }> = ({ safeGuides = false }) => {
  const shots = timeline.shots as Shot[];
  const subs = timeline.subs as Sub[];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, width: W, height: H }}>
      <Audio src={staticFile("ads_trading_audio.wav")} />
      <Backdrop />
      {shots.map((s, i) => {
        const from = fr(s.start);
        const dur = Math.max(1, (i + 1 < shots.length ? fr(shots[i + 1].start) : durationInFrames) - from);
        return (
          <Sequence key={`shot${i}`} from={from} durationInFrames={dur}>
            <ShotWrap shot={s} dur={dur} />
          </Sequence>
        );
      })}
      {subs.map((s, i) => (
        <Sequence key={`sub${i}`} from={fr(s.start)} durationInFrames={Math.max(1, fr(s.end) - fr(s.start))}>
          <SubtitleChunk text={s.text} side={s.side} emph={s.emph} />
        </Sequence>
      ))}
      {safeGuides && <SafeGuides />}
    </AbsoluteFill>
  );
};
