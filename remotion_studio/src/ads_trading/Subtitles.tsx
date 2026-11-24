import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, SUB_Y, sideColor } from "./theme";
import { fadeIn, outlined, pop } from "./ui";

/** Subtítulo de alto impacto: 2-4 palabras por golpe, color según el lado del que se habla. */
export const SubtitleChunk: React.FC<{ text: string; side: string; emph?: boolean }> = ({ text, side, emph }) => {
  const f = useCurrentFrame();
  const col = sideColor(side);
  const up = text.toUpperCase();
  const size = up.length > 24 ? 74 : up.length > 17 ? 84 : 96;
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top: SUB_Y - 150, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.04, textAlign: "center", color: emph ? C.bg : col,
          background: emph ? C.ads : "transparent", borderRadius: 34, padding: emph ? "10px 36px" : 0,
          transform: `scale(${pop(f, 0)})`, opacity: fadeIn(f, 0, 2), ...(emph ? {} : outlined(size * 0.12)),
        }}
      >
        {up}
      </div>
    </div>
  );
};
