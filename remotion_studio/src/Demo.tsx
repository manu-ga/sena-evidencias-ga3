import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

type Props = { titulo: string; subtitulo: string };

export const Demo: React.FC<Props> = ({ titulo, subtitulo }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entrada = spring({ frame, fps, config: { damping: 12 } });
  const opacidad = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(160deg, #ff7a3d, #6a1b9a)",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "sans-serif",
        color: "white",
      }}
    >
      <div style={{ fontSize: 150, fontWeight: 800, transform: `scale(${entrada})`, textAlign: "center" }}>
        {titulo}
      </div>
      <div style={{ fontSize: 70, marginTop: 40, opacity: opacidad }}>{subtitulo}</div>
    </AbsoluteFill>
  );
};
